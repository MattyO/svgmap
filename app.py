from flask import Flask, render_template, request
from collections import namedtuple
import fiona
import sys
import copy
import math
import time
from pprint import pprint
from datetime import datetime, timedelta

from graph import DataCollection, Graph, Viewport, Property, X, Y
import graph


app= Flask(__name__)
#Line = namedtuple('Line', ['start', 'end'], verbose=True)

Point = namedtuple('Point', ['lat', 'lon'], verbose=True)
Bounds = namedtuple('Bounds', ['topleft', 'bottomright'], verbose=True)

class Line:
    def __init__(self, start, end, attributes={}):
        self.start = start
        self.end = end
        self.attributes = attributes


def is_in_bounds(bounds, point):
    return point.lat < bounds.topleft.lat and point.lat > bounds.bottomright.lat and point.lon > bounds.topleft.lon and point.lon < bounds.bottomright.lon

def map_point(totalbounds, bounds, point, debug=False):
    width  = totalbounds.bottomright.lon - totalbounds.topleft.lon
    #print(width  )
    height = totalbounds.topleft.lat- totalbounds.bottomright.lat
    #print(height )
    bounds_width = bounds.bottomright.lon - bounds.topleft.lon
    #print(bounds_width  )
    bounds_height = bounds.topleft.lat- bounds.bottomright.lat
    #print(bounds_height   )
    #print(point.lon)
    #print(bounds.topleft.lon  )
    #print(bounds_width)

    percentx = (point.lon - bounds.topleft.lon) / bounds_width
    #print(percentx)
    percenty = (point.lat - bounds.bottomright.lat) / bounds_height
    if debug == True:
        print(percentx)
        print(percenty)
        print(is_in_bounds(bounds, point))
        print(bounds)
        print(point)
        print(width)
        print(height)
        print(bounds_width)
        print(bounds_height)
        print(percentx)
        print(percenty)
    #print(percenty)

    #print(totalbounds.topleft.lon)
    #print((width * percentx))
    newx = totalbounds.topleft.lon+ (width * percentx)
    #print(newx)
    newy = totalbounds.bottomright.lat+ (height * percenty)
    #print(newy)
    return [newx, newy]

#lat 81.6235991262987
#lon -178.00000000010002
#lat 0.6235991262987
#lon 7.999999999899984

totalbounds  = Bounds(topleft=Point(lat=81, lon=-178), bottomright=Point(lat=-80, lon=180))
bounds = Bounds(topleft=Point(lat=81, lon=-178), bottomright=Point(lat=0, lon=0))

print('find me')
#print(map_point(totalbounds, bounds, Point(lat=80, lon=-177)))
#print(map_point(totalbounds, bounds, Point(lat=40, lon=-89)))
#print(map_point(totalbounds, bounds, Point(lat=1, lon=-1)))
#raise Exception("test")

def time_datas():
    return [
["01-01-2018",266.0],
["01-02-2018",145.9],
["01-03-2018",183.1],
["01-04-2018",119.3],
["01-05-2018",180.3],
["01-06-2018",168.5],
["01-07-2018",231.8],
["01-08-2018",224.5],
["01-09-2018",192.8],
["01-10-2018",122.9],
["01-11-2018",336.5],
["01-12-2018",185.9],
["02-01-2019",194.3],
["02-02-2019",149.5],
["02-03-2019",210.1],
["02-04-2019",273.3],
["02-05-2019",191.4],
["02-06-2019",287.0],
["02-07-2019",226.0],
["02-08-2019",303.6],
["02-09-2019",289.9],
["02-10-2019",421.6],
["02-11-2019",264.5],
["02-12-2019",342.3],
["03-01-2020",339.7],
["03-02-2020",440.4],
["03-03-2020",315.9],
["03-04-2020",439.3],
["03-05-2020",401.3],
["03-06-2020",437.4],
["03-07-2020",575.5],
["03-08-2020",407.6],
["03-09-2020",682.0],
["03-10-2020",475.3],
["03-11-2020",581.3],
["03-12-2020",646.9]]

def to_timestamp(time_data, i):
    temp_data = []

    for d in time_data:
        new_datum = datetime.strptime(d[i], "%d-%m-%Y").timestamp()
        temp_data.append(d[0:i] + [new_datum] + d[(i+1):len(d)])
    return temp_data

#def find_meta_data(time_data):
#    array_len = len(time_data[0])
#    r_dict= {
#        'data_type': type(time_data)
#    }
#    for i in range(0,i):
#        column_data = [ foo[i] for foo in time_data ]
#        r_dict[i] = {
#            'min': min(column_data),
#            'max': max(column_data),
#            'type': type(next(column_data))
#        }
#    return r_dict

def scale(data_array, i, start_range, end_range):
    start_min = start_range[0]
    start_max = start_range[1]
    end_min = end_range[0]
    end_max = end_range[1]

    end_max - end_min
    return [ d[0:i] + [((d[i] - start_min)  / (start_max - start_min) *  (end_max - end_min)) + end_min] + d[(i+1):len(d)] for d in data_array]


def date_list(min_date, max_date):
    fill = []
    full_fill = []
    for year in range(min_date.year, max_date.year + 1):
      if year == min_date.year:
        t_months = [min_date.month, 13]
      elif year == max_date.year:
            t_months = [1,max_date.month + 1]
      else:
        t_months = [1,13]
      fill.append((year, t_months))

    for year, months in fill:
        for m in range(*months):
            full_fill.append([year, m])

    return [ datetime(y,m, 1, 0, 0) for [y, m] in full_fill ] 



#g.create.axis(Y(dc.properties.month), min=0, max=700, step=100)
#g.create.axis(X, collection=date_list(dc.meta.y.min, dc.meta.y.max))

#dc.meta.property_name.min
#dc.meta.property_name.max
#dc.meta.property_name.difference
#dc.meta.property_name.count
#dc.meta.x.min
#dc.meta.x.max
#dc.meta.x.difference


#graph.plot.svg()
#graph.plot.img()
#graph.plot.jpeg()

def inc_date(d, td):
    return (datetime.fromtimestamp(d).replace(day=1, hour=0, minute=0, second=0) + td).replace(day=1)

@app.route('/graph')
def graph():
    time_data = time_datas()

#g.create.line(DataCollection(data, properties=[Property(name, callable), Property(name, int), 'property_name']), x='property_name', y='property_name')
    dc = DataCollection(time_data,
        Property('month', 0, parse=lambda t: datetime.strptime(t, "%d-%m-%Y"), convert=lambda t: t.timestamp()), 
        Property('count', 1),
    )
    dl = date_list(
            inc_date(dc.meta.month.min, -timedelta(days=1)), 
            inc_date(dc.meta.month.max, timedelta(days=1)))

    x, y = X(dc.properties.month), Y(dc.properties.count)

    g = Graph(Viewport(Y.size(300, inverse=True), X.size(800), padding=30, attributes={'height':Y, 'width':X}))
    g.create.line(dc, 'counts', x, y )
    g.create.axis(x, collection=dl, tick_size=5, tick_additional_offset=5, tick_text=lambda d: d.strftime("%Y") if d.month == 1 else "", tick_text_properties = {'text-anchor':"middle",  "dominant-baseline": 'hanging'})
    g.create.axis(y, collection=[0, 100, 200, 300, 400, 500, 600, 700], tick_text_properties = {'text-anchor':"end"})

    #mdata = find_meta_data(time_data)
    time_data = to_timestamp(time_data, 0)

    padding = 30
    height=300
    width=800
    datamin=0
    datamax = 700
    tic_length = 5
    datemin = min([ d[0] for d in time_data])
    datemax = max([ d[0] for d in time_data])

    datemin_date = (datetime.fromtimestamp(datemin).replace(day=1, hour=0, minute=0, second=0) - timedelta(days=1)).replace(day=1)
    datemax_date  = (datetime.fromtimestamp(datemax).replace(day=1, hour=0, minute=0, second=0) + timedelta(days=1)).replace(day=1)
    datemin = datemin_date.timestamp()
    datemax = datemax_date.timestamp()

    scale_time = date_list(datemin_date, datemax_date)
    scale_timestamps = [ st.timestamp() for st in scale_time ]
    scale_text =[ str(d.year) if d.month == 1 else "" for d in scale_time ]

    scale_data_num = [0, 100, 200, 300, 400, 500, 600, 700]

    scale_data = [ list(t) for t in zip([padding] *len(scale_data_num), scale_data_num)]
    scale_data_start = scale(scale_data, 1, [datamin, datamax], [height - padding, padding])
    scale_data_end = [ [sde[0]-tic_length, sde[1]]  for sde in copy.copy(scale_data_start)]
    scale_data_text = zip([ str(sdn) for sdn in scale_data_num], scale_data_end)
    scale_data_points = zip(scale_data_start, scale_data_end)
    scale_data_lines = [Line(start=s,end=e) for (s,e) in scale_data_points ]


    scale_date_data = [ list(t) for t in zip(scale_timestamps , [height - padding] * len(scale_timestamps))]
    scale_date_data_start = scale(scale_date_data, 0, [datemin, datemax], [padding, width - (padding*2)])
    scale_date_data_end = [ [sde[0], sde[1]+tic_length]  for sde in copy.copy(scale_date_data_start )]
    scale_date_points = zip(scale_date_data_start, scale_date_data_end)
    scale_date_lines = [Line(start=s,end=e) for (s,e) in scale_date_points]
    scale_date_text =zip(scale_text, [[x,y+ 10] for (x, y) in scale_date_data_end])

    time_data = scale(time_data, 0, [datemin, datemax], [padding, width - (padding*2)])
    time_data = scale(time_data, 1, [datamin, datamax], [height - padding, padding])

    time_lines = []
    for tdi in range(0, len(time_data)-1):
        time_lines.append(Line(
            start=(time_data[tdi][0], time_data[tdi][1]),
            end=(time_data[tdi+1][0], time_data[tdi+1][1])
        ))

    yaxis = Line(
        start=(padding, padding),
        end=(padding, height-padding))
    xaxis  = Line(
            start=(padding, height-padding),
            end=(width-padding, height-padding))

    return render_template('graph.html', 
            height=height, 
            width=width, 
            xaxis=xaxis, 
            yaxis=yaxis, 
            time_data=time_data, 
            time_lines=time_lines, 
            scale_data_lines=scale_data_lines, 
            scale_data_text=scale_data_text, 
            scale_date_lines=scale_date_lines, 
            scale_date_text=scale_date_text, 
            new_graph=g)


@app.route('/')
def index():
    startx = request.args.get('startx', default=None, type=int)
    starty = request.args.get('starty', default=None, type=int)
    endx = request.args.get('endx', default=None, type=int)
    endy  = request.args.get('endy', default=None, type=int)
    bounds = None

    shapes = fiona.open("continent_ln.shp")
    western, southern, eastern, northern = shapes.bounds
    width  = math.fabs(eastern - western)
    height = math.fabs(northern - southern)

    totalbounds= Bounds(topleft=Point(lat=northern, lon=western), bottomright=Point(lat=southern, lon=eastern))

    if startx != None:
        startlat = (height-starty) - math.fabs(southern) 
        startlon = startx - math.fabs(eastern)
        endlat =  (height - endy) - math.fabs(southern)
        endlon = endx - math.fabs(eastern)
        #print('start bounding', file=sys.stderr)
        #print(startlat, file=sys.stderr)
        #print(startlon, file=sys.stderr)
        #print(endlat, file=sys.stderr)
        #print(endlon, file=sys.stderr)

        bounds = Bounds(topleft=Point(lat=startlat, lon=startlon), bottomright=Point(lat=endlat, lon=endlon))


    lines = []
    print('interesting')
    print(shapes[190]['geometry']['coordinates'][460:470])
    print('interesting')
    for si, shape in enumerate(shapes):
        points = shape['geometry']['coordinates']
        first_point = points[0]
        numskipped = 0
        fpi = 0
        for pi, point in enumerate(points[1:-1]):
            if bounds == None and int(point[0]) == int(first_point[0]) and int(point[1]) == int(first_point[1]):
                continue


            if bounds != None and (not is_in_bounds(bounds, Point(lat=point[1], lon=point[0])) or not is_in_bounds(bounds, Point(lat=first_point[1], lon=first_point[0]))):
                first_point = point
                fpi = pi
                continue

            if bounds != None:
                #print('first point', file=sys.stderr)
                #print(first_point, file=sys.stderr)
                #print(point, file=sys.stderr)
                a = first_point
                b = point
                mfirst_point = map_point(totalbounds, bounds, Point(lat=first_point[1], lon=first_point[0]))
                mpoint = map_point(totalbounds, bounds, Point(lat=point[1], lon=point[0]))

                if math.sqrt(math.pow(first_point[0] - point[0], 2) + math.pow(first_point[1] - point[1], 2)) > 200:
                    print(si)
                    print(fpi)
                    print(pi)
                    print(a)
                    print(b)
                    print(first_point)
                    print(point)
                    print('debug a')
                    print(map_point(totalbounds, bounds, Point(lat=a[1], lon=a[0]), debug=True))
                    print('debug b')
                    print(map_point(totalbounds, bounds, Point(lat=b[1], lon=b[0]), debug=True))
                    raise Exception('should be this long')
                #print(first_point, file=sys.stderr)
                #print(point, file=sys.stderr)
                #raise Exception('first point')
            else:
                mfirst_point = first_point
                mpoint = point

            lines.append(Line(
                start=(
                    mfirst_point[0] + math.fabs(western), 
                    height-(mfirst_point[1]+math.fabs(southern))
                ), 
                end=(
                    mpoint[0] + math.fabs(western), 
                    height-(mpoint[1]+math.fabs(southern))
                )
            ))
            first_point = point
            fpi = pi

    return render_template('index.html', lines=lines, height=height, width=width)
