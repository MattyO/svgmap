from collections import namedtuple
from functools import reduce
from itertools import tee

Line = namedtuple('Line', ['start', 'end'], verbose=True)
Point = namedtuple('Point', ['x', 'y'], verbose=True)
Tick = namedtuple('Tick', ['line', 'text'], verbose=True)

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def Struct(**kwargs):
    return namedtuple('Struct', ' '.join(kwargs.keys()))(**kwargs)

class Viewport(object):
    def __init__(self, *axis, padding=0):
        self.axis=axis
        self.padding=padding

    @property
    def drawable(self):
        return Struct(**reduce(lambda d1, d2: {**d1, **d2}, [a.cls.drawable_info(a.size, self.padding) for a in self.axis ]))

class AxisBase(object):
    def __repr__(self):
        return self.__class__.__name__
    def __init__(self, name):
        self.name = name
    def set(self, minimum=None, maximum=None, step=None, collection=None):
        self.min = minimum
        self.max = maximum
        self.step = step
        self.collection=collection

    @classmethod
    def size(cls, num, inverse=False):
        return Struct(cls=cls, size=num)

class X(AxisBase):
    @classmethod
    def drawable_info(self, size, padding):
        return {
                'width' : size - (padding*2),
                'left' : padding,
                'right': size - padding,
                }

    def scale(drawable_info, num):
        #return lambda mi, ma: scale(num, [mi, ma], [drawable_info.left, drawable_info.right])
        return [drawable_info.left, drawable_info.right]

class Y(AxisBase):
    @classmethod
    def drawable_info(self, size, padding):
        return {
                'height': size - (padding*2),
                'top'   : padding,
                'bottom': size - padding,
                }

    def scale(drawable_info):
        return [drawable_info.top, drawable_info.bottom]

class Property(object):
    def __init__(self, name, key_or_index, parse=lambda d: d, convert=lambda d: int(d)):
        self.name = name
        self.key_or_index = key_or_index
        self.parse = parse
        self.convert = convert

    def value(self, item):
        return self.parse(item[self.key_or_index])

    def graphable(self, item):
        return self.convert(parse(item[key_or_index]))

class MetaInfo(object):
    def __init__(self, data, prop):
        self.min = min([prop.value(d) for d in data])
        self.max = max([prop.value(d) for d in data])
        self.difference = self.max - self.min
        self.type = next(iter(set(type(prop.value(d)) for d in data)), None)

class MetaProxy(object):
    def __init__(self, data_collection):
        self.data_collection = data_collection

    def __getattr__(self, attr):
        prop = next(filter(lambda p: p.name == attr, self.data_collection.properties), None)
        return MetaInfo(self.data_collection.data, prop)

class DataCollection(object):
    def __init__(self, data, *properties):
        self.data = data
        self.properties = properties

    @property
    def meta(self):
        return MetaProxy(self)

    def to_dict(self):
        return [ { p.name: p.value(d) for p in self.properties } for d in self.data  ]

    def get_property(self, name):
        return next(filter(lambda p: p.name == name, self.properties), None)

class Graph(object):
    def __init__(self, viewport):
        self.viewport = viewport
        self.plot_objects = {}
        self.axis = {}
        self.data_collections = {}

    @property
    def create(self):
        return CreateFactory(self)


class CreateFactory(object):
    def __init__(self, graph):
        self.graph = graph

    def axis(self, axis, name=None):
        pass

    def line(self, data_collection, name, *axis):

        self.graph.plot_objects[name] = [
                Line(
                    start=Struct(**{ str(a): data_collection.get_property(a.name).value(d1) for a in axis}),
                    end=Struct(**{ str(a): data_collection.get_property(a.name).value(d2) for a in axis })
                ) for (d1, d2) in pairwise(data_collection.data)  ]
