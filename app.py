from flask import Flask, render_template, request
from collections import namedtuple
import fiona
import sys
import math


app= Flask(__name__)
Line = namedtuple('Line', ['start', 'end'], verbose=True)

Point = namedtuple('Point', ['lat', 'lon'], verbose=True)
Bounds = namedtuple('Bounds', ['topleft', 'bottomright'], verbose=True)


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
