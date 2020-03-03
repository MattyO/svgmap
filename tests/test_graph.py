import unittest
from collections import namedtuple
from datetime import datetime

from graph import Struct, Line, Graph, Viewport, X, Y, DataCollection, Property, DCItem, SvgType
import graph
import geometry


def r_struct_to_dict(struct):

    if(isinstance(struct, list)):
        return [ r_struct_to_dict(t) for t in struct ]

    return {key: r_struct_to_dict(value) if getattr(value, '_fields', None) != None else value  for key, value in struct._asdict().items()}

class SVG2Test(unittest.TestCase):
    def test_returns_a_svg(self):
        g = Graph(Viewport(Y.size(300, inverse=True), X.size(800), padding=30, attributes={'height':Y, 'width':X}))
        svg_text = g.svg2()
        self.assertEqual(svg_text, '<svg height="300" width="800"></svg>')

    def test_creates_plot_geometry(self):
        def geometry_callback(plot_geometries):
            self.assertEqual(list(plot_geometries.keys()), ['test'])
            line_geometries = plot_geometries['test']
            #TODO: update line geometries to always use the gemomety class and not switch
            self.assertIsInstance(line_geometries[0], geometry.Line)
            self.assertEqual(line_geometries[0].start.datum, [0,0])
            self.assertEqual(line_geometries[0].end.datum, [1,2])

        dc = DataCollection([[0, 0],[1, 2]], Property('first', 0), Property('second', 0))
        g = Graph(Viewport(Y.size(300, inverse=True), X.size(800), padding=30, attributes={'height':Y, 'width':X}))
        g.create.line(dc, 'test', X(dc.properties.first), Y(dc.properties.second))

        g.svg2(after_create_geometry=geometry_callback)

    def test_creates_coordinates(self):
        def coordinate_callback(plot_geometries):
            line_geometries = plot_geometries['test']
            self.assertEqual(line_geometries[0].start.coordinates[X], 0)
            self.assertEqual(line_geometries[0].start.coordinates[Y], 300)
            self.assertEqual(line_geometries[0].end.coordinates[X], 400)
            self.assertEqual(line_geometries[0].end.coordinates[Y], 150)

            self.assertEqual(line_geometries[1].start.coordinates[X], 400)
            self.assertEqual(line_geometries[1].start.coordinates[Y], 150)
            self.assertEqual(line_geometries[1].end.coordinates[X], 800)
            self.assertEqual(line_geometries[1].end.coordinates[Y], 0)

        dc = DataCollection([[0, 0],[2, 1], [4, 3]], Property('first', 0), Property('second', 0))
        g = Graph(Viewport(Y.size(300, inverse=True), X.size(800), padding=0, attributes={'height':Y, 'width':X}))
        g.create.line(dc, 'test', X(dc.properties.first), Y(dc.properties.second))

        g.svg2(after_create_coordinates=coordinate_callback)

    def test_create_coordinates_with_padding(self):
        def coordinate_callback(plot_geometries):
            line_geometries = plot_geometries['test']
            self.assertEqual(line_geometries[0].start.coordinates[X], 50)
            self.assertEqual(line_geometries[0].start.coordinates[Y], 250)
            self.assertEqual(line_geometries[0].end.coordinates[X], 400)
            self.assertEqual(line_geometries[0].end.coordinates[Y], 150)

            self.assertEqual(line_geometries[1].start.coordinates[X], 400)
            self.assertEqual(line_geometries[1].start.coordinates[Y], 150)
            self.assertEqual(line_geometries[1].end.coordinates[X], 750)
            self.assertEqual(line_geometries[1].end.coordinates[Y], 50)

        dc = DataCollection([[0, 0],[2, 1], [4, 3]], Property('first', 0), Property('second', 1))
        g = Graph(Viewport(Y.size(300, inverse=True), X.size(800), padding=50, attributes={'height':Y, 'width':X}))
        g.create.line(dc, 'test', X(dc.properties.first), Y(dc.properties.second))

        g.svg2(after_create_coordinates=coordinate_callback)

    def test_create_axis_geometries(self):
        def coordinate_callback(plot_geometries):
            line_geometries = plot_geometries['axis_Y']

            self.assertIsInstance(line_geometries[0], graph.Line)

            self.assertEqual(line_geometries[0].start.datum, [0, "{{left}}" ])
            self.assertEqual(line_geometries[0].end.datum,   [6, "{{left}}" ])

            self.assertEqual(line_geometries[1].start.datum, [0, "{{left}}" ])
            self.assertEqual(line_geometries[1].end.datum,   [0, "{{left}} + 5" ])

            self.assertIsInstance(line_geometries[2], graph.Text)
            self.assertEqual(line_geometries[2].point.datum, [0, "{{left}} + 5" ])
            self.assertEqual(line_geometries[2].text, '')

            self.assertEqual(line_geometries[13].start.datum, [6, "{{left}}" ])
            self.assertEqual(line_geometries[13].end.datum,   [6, "{{left}} + 5" ])

            self.assertIsInstance(line_geometries[14], graph.Text)
            self.assertEqual(line_geometries[14].point.datum, [6, "{{left}} + 5" ])
            self.assertEqual(line_geometries[14].text, '')


        dc = DataCollection([[0, 0],[2, 1], [4, 3]], Property('first', 0), Property('second', 0))
        g = Graph(Viewport(Y.size(300, inverse=True), X.size(800), padding=50, attributes={'height':Y, 'width':X}))
        #g.create.line(dc, 'test', X(dc.properties.first), Y(dc.properties.second))

        g.create.axis(Y(dc.properties.second), collection=[0,1,2,3,4,5,6], options={'position': {X: 'left'}})

        g.svg2(after_create_geometry=coordinate_callback)

    def test_create_axis_coordinates(self):
        def coordinate_callback(plot_geometries):
            line_geometries = plot_geometries['axis_Y']

            self.assertIsInstance(line_geometries[0], graph.Line)

            self.assertEqual(line_geometries[0].start.coordinates[Y], 250)
            self.assertEqual(line_geometries[0].start.coordinates[X], 50)
            self.assertEqual(line_geometries[0].end.coordinates[Y], 50)
            self.assertEqual(line_geometries[0].end.coordinates[X], 50)

            self.assertEqual(line_geometries[1].start.coordinates[Y], 250)
            self.assertEqual(line_geometries[1].start.coordinates[X], 50)
            self.assertEqual(line_geometries[1].end.coordinates[Y], 250)
            self.assertEqual(line_geometries[1].end.coordinates[X], 55)

            self.assertEqual(line_geometries[2].point.coordinates[Y], 250)
            self.assertEqual(line_geometries[2].point.coordinates[X], 55)

            self.assertEqual(line_geometries[13].start.coordinates[Y], 50)
            self.assertEqual(line_geometries[13].start.coordinates[X], 50)
            self.assertEqual(line_geometries[13].end.coordinates[Y], 50)
            self.assertEqual(line_geometries[13].end.coordinates[X], 55)

            self.assertEqual(line_geometries[14].point.coordinates[Y], 50)
            self.assertEqual(line_geometries[14].point.coordinates[X], 55)


        dc = DataCollection([[0, 0],[2, 1], [4, 3]], Property('first', 0), Property('second', 0))
        g = Graph(Viewport(Y.size(300, inverse=True), X.size(800), padding=50, attributes={'height':Y, 'width':X}))
        #g.create.line(dc, 'test', X(dc.properties.first), Y(dc.properties.second))

        g.create.axis(Y(dc.properties.second), collection=[0,1,2,3,4,5,6], options={'position': {X: 'left'}})

        g.svg2(after_create_coordinates=coordinate_callback)

    def test_create_datatime_axis(self):
        def geometry_callback(plot_geometries):
            for g in plot_geometries['axis_X']:
                if isinstance(g, graph.Line):
                    print("Line")
                    print(g.start.datum)
                    print(g.end.datum)
                if isinstance(g, graph.Text):
                    print("Text")
                    print(g.point.datum)

        def coordinate_callback(plot_geometries):
            line_geometries = plot_geometries['axis_X']

            self.assertIsInstance(line_geometries[0], graph.Line)

            self.assertEqual(line_geometries[0].start.coordinates[Y], 250)
            self.assertEqual(line_geometries[0].start.coordinates[X], 50)
            self.assertEqual(line_geometries[0].end.coordinates[Y], 50)
            self.assertEqual(line_geometries[0].end.coordinates[X], 50)

            self.assertEqual(line_geometries[1].start.coordinates[Y], 250)
            self.assertEqual(line_geometries[1].start.coordinates[X], 50)
            self.assertEqual(line_geometries[1].end.coordinates[Y], 250)
            self.assertEqual(line_geometries[1].end.coordinates[X], 55)

            self.assertEqual(line_geometries[2].point.coordinates[Y], 250)
            self.assertEqual(line_geometries[2].point.coordinates[X], 55)

            self.assertEqual(line_geometries[13].start.coordinates[Y], 50)
            self.assertEqual(line_geometries[13].start.coordinates[X], 50)
            self.assertEqual(line_geometries[13].end.coordinates[Y], 50)
            self.assertEqual(line_geometries[13].end.coordinates[X], 55)

            self.assertEqual(line_geometries[14].point.coordinates[Y], 50)
            self.assertEqual(line_geometries[14].point.coordinates[X], 55)

        g = Graph(Viewport(Y.size(300, inverse=True), X.size(800), padding=50, attributes={'height':Y, 'width':X}))

        datetime_list = [ [datetime(2020, 1, day)] for day in range( 15,20 ) ]
        datetime_collection = DataCollection(datetime_list , Property('default', 0, convert=lambda t: t.timestamp()))

        g.create.axis(X(datetime_collection.properties.default), collection=datetime_collection, options={'position': {Y: 'bottom'}})

        g.svg2(after_create_geometry=geometry_callback, after_create_coordinates=coordinate_callback)



    def test_create_lines(self):
        dc = DataCollection([[0, 0],[2, 1], [4, 3]], Property('first', 0), Property('second', 0))
        g = Graph(Viewport(Y.size(300, inverse=True), X.size(800), padding=0, attributes={'height':Y, 'width':X}))
        g.create.line(dc, 'test', X(dc.properties.first), Y(dc.properties.second))

        svg_text = g.svg2()

        self.assertTrue('<line x1="0" y1="300" x2="400" y2="150"' in svg_text)
        self.assertTrue('<line x1="400" y1="150" x2="800" y2="0"' in svg_text)

    def test_svg_type(self):
        l = Line(DCItem(None, None, None), DCItem(None, None, None))
        l.start.coordinates[X] = 0
        l.start.coordinates[Y] = 1
        l.end.coordinates[X] = 200
        l.end.coordinates[Y] = 300

        svg_type = SvgType(
            Line="<line x1={{start.X}}, y1={{start.Y}}, x2={{end.X}}, y2={{end.Y}} /> ",
        )
        self.assertEqual(svg_type.tag(l), "<line x1=0, y1=1, x2=200, y2=300 /> ")

    def test_dc_item_can_get_coordinate(self):
        i = DCItem('test', None, None)
        i.coordinates[X] = 1
        self.assertEqual(i.X, 1)
        self.assertEqual(i.dc, 'test')
        


class ViewportTest(unittest.TestCase):
    def struct_to_dict(self,struct):
        return {**struct._asdict()}

    def test_find_axis(self):
        vp = graph.Viewport(graph.Y.size(300, inverse=True), graph.X.size(800), padding=30)
        self.assertEqual(vp.find_axis(Y).size, 300)

    def test_drawable_info(self):
        vp = graph.Viewport(graph.Y.size(300, inverse=True), graph.X.size(800), padding=30)

        self.assertEqual(
                self.struct_to_dict(vp.drawable),
                self.struct_to_dict(Struct(top=30, left=30, height=240, width=740, right=770, bottom=270)))


class DataCollectionTest(unittest.TestCase):
    
    def test_data_collection_with_one_item_list_and_no_properties(self):
        dc = graph.DataCollection([0,1,2,3,4])
        p = dc.get_property('default')

        self.assertEqual(dc.properties.default, p)
        self.assertEqual(dc.meta.default.min, 0)
        self.assertEqual(dc.meta.default.max, 4)

    def test_geometry_items(self):
        dc = graph.DataCollection([(0,0), (0,1), (0,10)], graph.Property('first_property', 1) )
        items = dc.to_dc_items(None)

        self.assertEqual(items[0].dc, dc)
        self.assertEqual(items[0].datum, (0,0))
        self.assertEqual(items[2].datum, (0,10))

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


    def test_properties_lookup(self):
        p = graph.Property('first_property', 1)
        dc = graph.DataCollection([(0,0), (0,1), (0,10)], p)
        self.assertEqual(dc.properties.first_property, p)



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
        data = [(0,0), (5,1), (10,10)]
        dc = graph.DataCollection(data, graph.Property('month', 1), graph.Property('count', 0) )
        self.g.create.line(dc,'counts', graph.X(dc.properties.count), graph.Y(dc.properties.month))

        self.assertEqual(r_struct_to_dict(
            self.g.plot_objects['counts']),
            r_struct_to_dict([
                Line(start=Struct(X=30,Y=270), end=Struct(X=400,Y=((240*.9)+30))),
                Line(start=Struct(X=400,Y=((240*.9)+30)), end=Struct(X=770,Y=30)),
            ]))

    def test_create_line_with_datetimes(self):
        data = [["01-01-2018",0],
                ["01-02-2018",5],
                ["01-03-2018",10]]

        month_prop = graph.Property('month', 0, parse=lambda t: datetime.strptime(t, "%d-%m-%Y"), convert=lambda t: t.timestamp())
        dc = graph.DataCollection(data, month_prop, graph.Property('count', 1) )

        self.g.create.line(dc,'counts', graph.X(dc.properties.month), graph.Y(dc.properties.count))

        self.assertEqual(self.g.plot_objects['counts'][0].start.X, 30)
        self.assertEqual(self.g.plot_objects['counts'][0].end.X, 418)
        self.assertEqual(self.g.plot_objects['counts'][1].start.X, 418)
        self.assertEqual(self.g.plot_objects['counts'][1].end.X, 770)


    def test_create_x_axis(self):
        pass
        #self.g.create.axis(graph.X, name='counts', collection=[])


        #self.assertEqual(self.g.axis[graph.X], [Line, Tick])

    def test_create_axis_effects_data_plotting(self):
        pass

    def test_create_stacked(self):
        pass
        #self.g.create.line(dc,'counts', graph.X('count'), graph.X('count2'), graph.Y('month'), stack=graph.X))
