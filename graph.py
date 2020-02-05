from collections import namedtuple
from functools import reduce
from itertools import tee

import geometry

#Line = namedtuple('Line', ['start', 'end'])
Point = namedtuple('Point', ['x', 'y'])
Tick = namedtuple('Tick', ['line', 'text'])
Label = namedtuple('Label', ['point', 'text', 'attributes'])

class PlotLine(object):
    def __init__(self, data_collection, name, *axis):
        self.dc = data_collection
        self.name = name
        self.axis = axis

    def create_geometries(self):
        return {self.name: [geometry.Line(start=d1, end=d2) for (d1, d2) in pairwise(self.dc.to_dc_items())]}

class Line:
    def __init__(self, start, end, attributes={'shape-rendering':"geometricPrecision"}, styles={"stroke":"rgb(0,0,0)", 'stroke-width':'0.5'}):

        self.start = start
        self.end = end
        self.attributes = attributes
        self.styles = styles

def noop_scale(num):
    return lambda mi, ma: num

def single_scale(num, start_range, end_range):
    start_min = start_range[0]
    start_max = start_range[1]
    end_min = end_range[0]
    end_max = end_range[1]

    end_max - end_min
    return int(((num - start_min)  / (start_max - start_min) *  (end_max - end_min)) + end_min)

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def Struct(**kwargs):
    return namedtuple('Struct', ' '.join(kwargs.keys()))(**kwargs)

class Viewport(object):
    def __init__(self, *axis, padding=0, attributes={}):
        self.axis=axis
        self.padding=padding
        self.attributes = attributes

    def find_axis(self, axis_class):
        return next(filter(lambda a: a.cls == axis_class, self.axis))

    @property
    def drawable(self):
        return Struct(**reduce(lambda d1, d2: {**d1, **d2}, [a.cls.drawable_info(a, self.padding) for a in self.axis ]))

class AxisBase(object):
    def __repr__(self):
        return self.__class__.__name__

    def __init__(self, prop):
        self.prop = prop

    def set(self, minimum=None, maximum=None, step=None, collection=None):
        self.min = minimum
        self.max = maximum
        self.step = step
        self.collection=collection

    @classmethod
    def size(cls, num, inverse=False):
        return type("AxisSize", (object,), {'cls':cls, 'size':num, 'inverse':inverse})

class X(AxisBase):
    @classmethod
    def drawable_info(self, a, padding):
        #size, min, max
        return {
                'width' : a.size - (padding*2),
                'left' : padding,
                'right': a.size - padding,
                }

    @classmethod
    def scale(self, drawable_info, num):
        return lambda mi, ma: single_scale(num, [mi, ma], [drawable_info.left, drawable_info.right])
        #return [drawable_info.left, drawable_info.right]

class Y(AxisBase):
    @classmethod
    def drawable_info(self, a, padding):
        return {
                'height': a.size - (padding*2),
                'top'   : padding,
                'bottom': a.size - padding,
                }

    @classmethod
    def scale(self, drawable_info, num):

        return lambda mi, ma: single_scale(num, [mi, ma], [drawable_info.bottom, drawable_info.top])
        #return [drawable_info.top, drawable_info.bottom]

class Property(object):
    def __init__(self, name, key_or_index, parse=lambda d: d, convert=lambda d: int(d)):
        self.name = name
        self.key_or_index = key_or_index
        self.parse = parse
        self.convert = convert

    def value(self, item):
        return self.parse(item[self.key_or_index])

    def cp(self, num):
        return self.convert(num)

    def graphable(self, item):
        return self.convert(self.parse(item[self.key_or_index]))

class MetaInfo(object):
    def __init__(self, data, prop):
        #TODO chagne min and max from graphable to value
        self.min = min([prop.graphable(d) for d in data])
        self.max = max([prop.graphable(d) for d in data])
        self.difference = self.max - self.min
        self.type = next(iter(set(type(prop.value(d)) for d in data)), None)

class MetaProxy(object):
    def __init__(self, data_collection):
        self.data_collection = data_collection

    def __getattr__(self, attr):
        prop = next(filter(lambda p: p.name == attr, self.data_collection.properties), None)
        return MetaInfo(self.data_collection.data, prop)

class DCItem(object):
    def __init__(self, dc, datum):
        self.dc = dc
        self.datum = datum

class DataCollection(object):
    def __init__(self, data, *properties):
        self.data = data
        self.properties = Struct(**{ p.name: p for p in properties})

    @property
    def meta(self):
        return MetaProxy(self)


    def to_dict(self):

        return [ { p.name: p.value(d) for p_name, p in self.properties._asdict().items()} for d in self.data  ]

    def to_dc_items(self):
        return [DCItem(self, d) for d in self.data]

    def get_property(self, name):
        return next(filter(lambda p: p.name == name, self._properties), None)

    def bounds(self, a):
        td = [ a.prop.graphable(d) for d in self.data  ]
        return [min(td), max(td)]


def update_struct(struct, key, value):
    struct_attributes = {k: v for k, v in struct._asdict().items() }
    struct_attributes.update(**{key: value})
    return Struct(**struct_attributes)

class Graph(object):
    def __init__(self, viewport):
        self.viewport = viewport
        self.data_info = {}
        self.axis_info = {}
        self.data_collections = {}
        self.info = {'plot': [], 'axis': []}
        self.plots = []

    @property
    def create(self):
        return CreateFactory(self)

    def _complete_with_bounds(self):
        ##bound[x] = (a,b)
        ##bounds[y] = (a,b)
        #for plot objects in all plot objcts
        #    for axis in all bounds
        #        update plot_object[axis](bound)

        def update_bounds(thing, axis_name, bounds):
            if(isinstance(thing, Label)):
                return Label(
                        update_struct(thing.point, axis_name, getattr(thing.point, axis_name)(*bounds)), thing.text, thing.attributes)
            if(isinstance(thing, Line)):
                return Line(
                        start= update_struct(thing.start, axis_name, getattr(thing.start, axis_name)(*bounds)),
                        end= update_struct(thing.end, axis_name, getattr(thing.end, axis_name)(*bounds)), attributes=thing.attributes, styles=thing.styles)


        bounds_map = {}
        for name, di in  self.data_info.items():
            axis_names = [ str(a) for a in di.axis ]
            for axis in di.axis:
                axis_name = str(axis)
                axis_collection = self.axis_info[axis].collection if axis in self.axis_info else []
                axis_graphable = [axis.prop.convert(ac) for ac in axis_collection]
                dc_bounds = di.data_collection.bounds(axis)
                combined_bounds = dc_bounds + axis_graphable
                total_bounds = [min(combined_bounds), max(combined_bounds)]
                bounds_map[axis] = total_bounds

        for name, di in  self.data_info.items():
            for axis, bounds in bounds_map.items():
                axis_name = str(axis)
                di = update_struct(di,'plot_objects',[
                    Line(
                        start= update_struct(line.start, axis_name, getattr(line.start, axis_name)(*bounds)),
                        end= update_struct(line.end, axis_name, getattr(line.end, axis_name)(*bounds)))
                    for line in di.plot_objects ])
                self.data_info[name]=di

        for axis_info_axis, ai in  self.axis_info.items():
            for axis, bounds in bounds_map.items():
                axis_name = str(axis)
                ai = update_struct(ai,'plot_objects',[ update_bounds(po , axis_name, bounds) for po in ai.plot_objects ])

                self.axis_info[axis_info_axis]=ai



    def svg2(self, **callbacks):
        #axis_geomitries = axis.create_geomitries(self.viewport, self.info.axis)
        #add create gemoetries for axis class.  plotable? axis have default.  jj
        #geometry

        plot_geometries = []
        if len(self.plots) > 0:
            plot_geometries = reduce(lambda d1,d2: {**d1, **d2}, [plot.create_geometries() for plot in self.plots])

        after_create_geometry = callbacks.get('after_create_geometry', None)
        if callable(after_create_geometry):
            plot_geometry_callback_results = after_create_geometry(plot_geometries)
            if plot_geometry_callback_results  is not None:
                plot_geometries = plot_geometry_callback_results 


        #plot_geometries = [axis.apply_coordinate(pg, viewport) for axis in pg.axis for pg in plot_geometries ]
        #if plot_coordinate_callback_results  is not None:
        #    plot_geometries = plot_coordinate_callback_results


        #plot_geomitries = SvgType.apply_aethetics(pg) for pg in plot_geomitries) 
        #svg_objects  = "\n".join(SvgType.svg_object(pg) for pg in plot_geomitries) 
        svg_objects = ""

        svg_attributes = [ '{}="{}"'.format(attribute_name, self.viewport.find_axis(axis_class).size) 
                for attribute_name, axis_class in self.viewport.attributes.items()]
        svg_attributes_text = " ".join(svg_attributes)

        svg = '<svg ' + svg_attributes_text + '>'
        svg += "\n".join(svg_objects)
        svg += '</svg>'

        return svg


    def svg(self):
        self._complete_with_bounds()
        axs = Struct(**{ a.cls.__name__: a.size for a in self.viewport.axis})

        def line(l):
            attributes = " ".join([ "{}=\"{}\"".format(key, value) for key, value in l.attributes.items() ])
            styles  = ";".join([ "{}:{}".format(key, value) for key, value in l.styles.items() ])
            return  ('<line ' + attributes + ' style="' + styles +'" x1="{}" y1="{}" x2="{}" y2="{}"/>') \
                .format(l.start.X, l.start.Y, l.end.X, l.end.Y)

        def text(l):
            attributes = " ".join([ "{}=\"{}\"".format(key, value) for key, value in l.attributes.items() ])
            return  ('<text style="font-size: 12px"  x="{}" y="{}" '+attributes+'>{}</text>').format(l.point.X, l.point.Y, l.text)

        def draw(thing):
            if isinstance(thing, Line):
                return line(thing)
            if isinstance(thing, Label):
                return text(thing)

            return ""


        svg = '<svg height="{}" width="{}">'.format(axs.Y, axs.X)
        for name, pos in self.data_info.items():
            svg += "\n".join([line(po) for po in pos.plot_objects ])

        for a, aos in self.axis_info.items():
            svg += "\n".join([draw(ao) for ao in aos.plot_objects])

        svg += '</svg>'
        return svg



class CreateFactory(object):
    def __init__(self, graph):
        self.graph = graph

    def axis(self, axis, collection=None, tick_size = 5, tick_additional_offset=0, tick_text_properties={}, tick_line_properties={'shape-rendering':"crispEdges"}, tick_line_styles={'stroke':'rgb(0,0,0)'}, tick_text=lambda t: str(t), **args):
        import operator

        axis_size = next( a for a in self.graph.viewport.axis if a.cls == type(axis))
        drawable_info = axis_size.cls.drawable_info(axis_size, self.graph.viewport.padding)
        #TODO put axis size, min, andmax on the axis class.  use that to make this method more repeatable
        left, right, top, bottom =  drawable_info.get('left', None), \
                                    drawable_info.get('right', None),\
                                    drawable_info.get('top', None),\
                                    drawable_info.get('bottom', None),
        tick_operator = operator.add
        if left == None or right == None:
            viewport_left  = self.graph.viewport.drawable.left
            left, right= viewport_left, viewport_left
            tick_operator = operator.sub

        if top == None or bottom == None:
            viewport_bottom = self.graph.viewport.drawable.bottom
            top, bottom = viewport_bottom, viewport_bottom


        ticks = [
                Line(
                    start=update_struct(Struct(X=noop_scale(left), Y=noop_scale(top)), str(axis), axis.scale(self.graph.viewport.drawable, axis.prop.cp(t))), 
                    end=update_struct(Struct(X=noop_scale(tick_operator(right,tick_size)), Y=noop_scale(tick_operator(bottom,tick_size))), str(axis), axis.scale(self.graph.viewport.drawable, axis.prop.cp(t))), attributes=tick_line_properties, styles=tick_line_styles)
            for t in collection 
        ]

        labels = [
            Label(update_struct(Struct(
                        X=noop_scale(tick_operator(right,tick_size)), 
                        Y=noop_scale(tick_operator(bottom,tick_size))), 
                    str(axis), 
                    axis.scale(self.graph.viewport.drawable, axis.prop.cp(t))),
                tick_text(t), tick_text_properties)
            for t in collection 

        ]

        #TODO error scale thes
        self.graph.axis_info[axis] = Struct(
                collection=collection,
                plot_objects= [Line(start=Struct(X=noop_scale(left), Y=noop_scale(top)), end=Struct(X=noop_scale(right), Y=noop_scale(bottom)), attributes=tick_line_properties, styles=tick_line_styles)]+ticks + labels)

    def line(self, data_collection, name, *axis):
        self.graph.plots.append(PlotLine(data_collection, name, *axis))
        def find_axis(a_name):
            return next( a for a in axis if str(a) == a_name  )

        d_info = self.graph.viewport.drawable

        self.graph.data_info[name] = Struct(
                data_collection = data_collection,
                axis = axis,
                plot_objects = [
                    Line(
                        start=Struct(**{ str(a): a.scale(d_info, a.prop.graphable(d1)) for a in axis}),
                        end=Struct(**{ str(a): a.scale(d_info, a.prop.graphable(d2)) for a in axis })
                    ) for (d1, d2) in pairwise(data_collection.data)  ])

        #self.graph.plot_objects[name] = [
        #    Line(
        #        start=Struct(**{key: value(*data_collection.bounds(find_axis(key))) for key, value in line.start._asdict().items() }),
        #        end=Struct(**{key : value(*data_collection.bounds(find_axis(key))) for key, value in line.end._asdict().items()}))
        #    for line in self.graph.plot_objects[name]]
