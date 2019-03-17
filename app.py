from flask import Flask, render_template
from collections import namedtuple
import fiona


app= Flask(__name__)
Line = namedtuple('Line', ['start', 'end'], verbose=True)

@app.route('/')
def index():
    shapes = fiona.open("continent_ln.shp")
    lines = []
    for shape in shapes:
        points = shape['geometry']['coordinates']
        first_point = points[0]
        for point in points[1:-1]:
            if int(point[0]) == int(first_point[0]) and int(point[1]) == int(first_point[1]):
                continue
            lines.append(Line(
                start=(
                    first_point[0]+180, 
                    180-(first_point[1]+90)
                ), 
                end=(
                    point[0]+180, 
                    180-(point[1]+90)
                )
            ))
            first_point = point

    return render_template('index.html', lines=lines)
