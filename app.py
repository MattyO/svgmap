from flask import Flask, render_template, request
from collections import namedtuple
import fiona
import sys
import math


app= Flask(__name__)
Line = namedtuple('Line', ['start', 'end'], verbose=True)

Point = namedtuple('Bounds', ['lat', 'lon'], verbose=True)
Bounds = namedtuple('Bounds', ['topleft', 'bottomright'], verbose=True)


def is_in_bounds(bounds, point):
    return point.lat < bounds.topleft.lat and point.lat > bounds.bottomright.lat and point.lon > bounds.topleft.lon and point.lon < bounds.bottomright.lon

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

    if startx != None:
        startlat = (height-starty) - math.fabs(southern) 
        startlon = startx - math.fabs(eastern)
        endlat =  (height - endy) - math.fabs(southern)
        endlon = endx - math.fabs(eastern)

        bounds = Bounds(topleft=Point(lat=startlat, lon=startlon), bottomright=Point(lat=endlat, lon=endlon))

        print(startlat, file=sys.stderr)
        print(startlon, file=sys.stderr)
        print(endlat, file=sys.stderr)
        print(endlon, file=sys.stderr)


    lines = []
    for shape in shapes:
        points = shape['geometry']['coordinates']
        first_point = points[0]
        for point in points[1:-1]:
            if int(point[0]) == int(first_point[0]) and int(point[1]) == int(first_point[1]):
                continue

            if bounds != None and is_in_bounds(bounds, Point(lat=point[1], lon=point[0])):
                first_point = point
                continue

            lines.append(Line(
                start=(
                    first_point[0] + math.fabs(western), 
                    height-(first_point[1]+math.fabs(southern))
                ), 
                end=(
                    point[0] + math.fabs(western), 
                    height-(point[1]+math.fabs(southern))
                )
            ))
            first_point = point

    return render_template('index.html', lines=lines, height=height, width=width)
