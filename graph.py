from collections import namedtuple

Line = namedtuple('Line', ['start', 'end'], verbose=True)
Point = namedtuple('Point', ['x', 'y'], verbose=True)

def Struct(**kwargs):
    return namedtuple('Struct', ' '.join(kwargs.keys()))(**kwargs)

class Viewport(object):
    def __init__(self, height, width, padding=0):
        self.height=height
        self.width=width
        self.padding=padding

    @property
    def drawable
        return Struct(
                    width   = self.width-(self.padding*2), 
                    height  = self.height - (self.padding*2)
                    left    = self.padding
                    right   = self.width - padding
                    top     = height-padding
                    bottom  = padding
                )

def AxisBase(object):
    def set(self, minimum=None, maximum=None, step=None, collection)
        self.min = minimum
        self.max = maximum
        self.step = step

def X(AxisBase):
    pass
def Y(AxisBase):
    pass

def Property(object):
    def __init__(name, parse=lambda d: d, covert=lambda d: d):
        self.name = name
        self.parse = parse
        self.convert = convert

    def value(item):
        return parse(item)

    def graphable(item)
        return convert(parse(item))

def MetaInfo(object):
    def __init__(self, data, prop):
        self.min = min([prop.value(d) for d in data])
        self.max = max([prop.value(d) for d in data])
        self.difference = max - min
        self.type = next(set([type(prop.get(d)) for d in data]), None)

class MetaProxy(object):
    def __init__(self, data_collection)
        self.data_collection = data_collection

    def __getattr__(self, attr):
        prop = next(filter(lambda p: p.name == attr, self.data_collection.properties), None)
        return MetaInfo(self.DataCollection.data, prop)

class DataCollection(object):
    def __init__(self, data, properties=None):kj:W
        self.data = data
        self.properties = properties

    @property
    def meta(self):
        return MetaProxy(self)

class Graph(object):
    def __init__(self, viewport):
        self.viewport = viewport
        self.plot_objects
        self.axis = []

    @property
    def create(self)
        return CreateFactory(self)


class CreateFactory(object):
    def __inti__(self, graph):
        self.graph = graph

    def axis(self):
        self.ax
        pass

    def line(self)
        self.graph.line_objects.append(
        pass
