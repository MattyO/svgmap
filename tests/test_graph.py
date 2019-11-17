import unitest
import graph

class DataCollection(unittest.TestCase):
    def test_get_property(self):
        graph.DataCollection([(0,0), (0,1), (0,10)], graph.Property('first', 0) )
        self.assertEqual(

class GraphTest(unittest.TestCase):
    def setUp(self):
        self.g = graph.Graph(graph.ViewPort(300, 800))

    def test_bar(self):
        self.assertEqual(0,1)
