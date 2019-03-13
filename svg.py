import fiona
import matplotlib.pyplot as plt

shapes = fiona.open("continent_ln.shp")
#  "bounds": [
#              -179.99999999990004,
#                  -85.47029087362489,
#                      180.00000000010002,
#                          83.6235991262987
#                            ],
#
lines = []

print(shapes[0])

#for shape in shapes:
#    xs = []
#    ys = []
#    for point in shape['geometry']['coordinates']:
#        xs.append(point[0])
#        ys.append(point[1])
#
#
#    plt.plot(xs, ys, 'k')
#
#plt.savefig('testfig')
#
for shape in shapes:
    points = shape['geometry']['coordinates']
    first_point = points[0]
    for point in points[1:-1]:
        #if first_point[0] < -124 or first_point[0] > -67 or point[0] < -124 or point[0] > -67 or first_point[1] < 25 or first_point[1] > 50 or point[1] < 25 or point[1] > 50:
        #    first_point = point
        #    continue
        #if int(point[0]) == int(first_point[0]) and int(point[1]) == int(first_point[1]):
        #    continue
        lines += '<line style="stroke:rgb(0,0,0);stroke-width:1"  x1="'+str((first_point[0]+180))+'" y1="'+str(180-(first_point[1]+90))+'" x2="'+str((point[0]+180))+'" y2="'+str(180-(point[1]+90))+'"/>'
        first_point = point

content = []
content += "<html>"
content += "<head>"
content += "</head>"
content += "<body>"
content += "<h1>test</h1>"
content += '<svg height="600" width="600">'
for line in lines:
    content += line
content += "</svg>"
content += "</body>"
content += "</html>"

content = "".join(content)



with open("output.html", 'w') as f:
    f.write(content)
