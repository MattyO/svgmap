import unittest
import graph

class DataCollectionTest(unittest.TestCase):
    def test_get_property_max(self):
        dc = graph.DataCollection([(0,0), (0,1), (0,10)], graph.Property('first_property', 1) )
        self.assertEqual(dc.meta.first_property.max, 10)

    def test_get_property_min(self):
        dc = graph.DataCollection([(0,0), (0,1), (0,10)], graph.Property('first_property', 1) )
        self.assertEqual(dc.meta.first_property.min, 0)

class PropertyTest(unittest.TestCase):
    def test_simple(self):
        p = graph.Property('month', 0)
        self.assertTrue(p.value([100,2]), 100)

    def test_parse(self):
        p = graph.Property('month', 0, parse=lambda t: datetime.strptime(t, "%d-%m-%Y"))
        self.assertTrue(p.value(['01-01-2018',2]), datetime(2018, 1,1))

class GraphTest(unittest.TestCase):
    def setUp(self):
        self.g = graph.Graph(graph.Viewport(300, 800, padding=30))

    def test_create_line(self):
        data = [(0,0), (0,1), (0,10)]
        dc = graph.DataCollection(data, graph.Property('month', 1), graph.Property('counts', 0) )
        self.g.create.line(dc, name='counts', x='count', y='month')

        self.assertEqual(self.g.plot_objects['counts'], [Point, Point, Point, Line, Line ])

    def test_create_x_axis(self):
        self.g.create.axis(X, name='counts', x='count', y='month')


        self.assertEqual(self.g.axis[X], [Line, Tick])
