import unittest
import graph
from datetime import datetime
from graph import Struct

class ViewportTest(unittest.TestCase):
    def struct_to_dict(self,struct):
        return {**struct._asdict()}

    def test_drawable_info(self):
        vp = graph.Viewport(graph.Y.size(300, inverse=True), graph.X.size(800), padding=30)

        self.assertEqual(
                self.struct_to_dict(vp.drawable),
                self.struct_to_dict(Struct(top=30, left=30, height=240, width=740, right=770, bottom=270)))

class DataCollectionTest(unittest.TestCase):
    def test_get_property_max(self):
        dc = graph.DataCollection([(0,0), (0,1), (0,10)], graph.Property('first_property', 1) )
        self.assertEqual(dc.meta.first_property.max, 10)

    def test_get_property_min(self):
        dc = graph.DataCollection([(0,0), (0,1), (0,10)], graph.Property('first_property', 1) )
        self.assertEqual(dc.meta.first_property.min, 0)

    def test_property_hash(self):
        dc = graph.DataCollection([(0,0), (0,1), (0,10)], graph.Property('first_property', 0), graph.Property('second_property', 1) )

        self.assertEqual(
                dc.to_dict(),
                [{'first_property': 0, 'second_property': 0},
                 {'first_property': 0, 'second_property': 1},
                 {'first_property': 0, 'second_property': 10}])


class PropertyTest(unittest.TestCase):
    def test_simple(self):
        p = graph.Property('month', 0)
        self.assertTrue(p.value([100,2]), 100)

    def test_parse(self):
        p = graph.Property('month', 0, parse=lambda t: datetime.strptime(t, "%d-%m-%Y"))
        self.assertTrue(p.value(['01-01-2018',2]), datetime(2018, 1,1))

class GraphTest(unittest.TestCase):
    def setUp(self):
        self.g = graph.Graph(graph.Viewport(graph.Y.size(300, inverse=True), graph.X.size(800), padding=30))

    def test_create_line(self):
        data = [(0,0), (0,1), (0,10)]
        dc = graph.DataCollection(data, graph.Property('month', 1), graph.Property('count', 0) )
        self.g.create.line(dc,'counts', graph.X('count'), graph.Y('month'))

        self.assertEqual(self.g.plot_objects['counts'], [])

    def test_create_x_axis(self):
        self.g.create.axis(graph.X, name='counts')


        self.assertEqual(self.g.axis[graph.X], [Line, Tick])
