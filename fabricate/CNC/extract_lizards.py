# import matplotlib; matplotlib.interactive(True)
import re
from pylab import *
from numpy import *
from .cnc import *
from . import constants

can = canvas.Canvas('lizards.pdf', pagesize=(20 * inch, 12 * inch))
scale = 2/ 6.652
can.scale(scale, scale)
can.translate(0 * inch / scale, 25 * inch / scale)

rg = re.compile('<g>(.*?)</g>', flags=re.MULTILINE)
rx1 = re.compile('x1="([^"]*)"')
ry1 = re.compile('y1="([^"]*)"')
rx2 = re.compile('x2="([^"]*)"')
ry2 = re.compile('y2="([^"]*)"')
f = open("/home/justin/Dropbox/WyoLumCode/CNC/MC_Escher_single_lizard_tile.svg")
dat = ''.join(f.read().split())

cx = 110.8
cy = 178.6
# cx = cy = 0
x1s = array([float(m.group(1)) for m in rx1.finditer(dat)]) - cx
y1s = array([float(m.group(1)) for m in ry1.finditer(dat)]) - cy
x2s = array([float(m.group(1)) for m in rx2.finditer(dat)]) - cx
y2s = array([float(m.group(1)) for m in ry2.finditer(dat)]) - cy

figure(1); axis('equal')
# figure(2); axis('equal')
theta = 2 * pi/3.
R = array([[cos(theta), -sin(theta)],
           [sin(theta), cos(theta)]])


def rotate(center, pt, degrees):
    DEG = pi / 180.
    ang = -degrees * DEG
    center = array(center)
    if center.ndim == 1:
        out = dot(array(pt) - center, [[cos(ang), -sin(ang)], 
                                       [sin(ang), cos(ang)]]) + center
    else:
        out = dot(array(pt) - center[:,newaxis], [[cos(ang), -sin(ang)], 
                                                  [sin(ang), cos(ang)]]) + center
    return out

def translate(vec, dat):
    return dat + vec

p0 = [0, 0]
p1 = array([333.526, -16.438])
p2 = dot(R, p1)
p3 = dot(R, p2)
# plot(p1[0], p1[1], 'bo')
# plot(p2[0], p2[1], 'bo')
# plot(p3[0], p3[1], 'bo')
pts = [p0, p1]
for i in range(5):
    pts.append(rotate(pts[-1], pts[-2], -120))
hex = array(pts)
# plot(hex[:,0], hex[:,1], 'k-', alpha=.2)

knee = rotate(p0, p1, 60)
foot = p0
head = p1
quad = array([p0, p1, knee, p2, p0])

for i in range(3):
    # plot(quad[:,0], quad[:,1], '-')
    quad = rotate(knee, quad, 120)

start = 40
mid = 50
stop = -47
figure(1)
if False:
    for i, (x, y) in enumerate(zip(x1s, y1s)):
        text(x, y, '%d' % i, fontsize=10)

for x1, y1, x2, y2 in zip(x1s, y1s, x2s, y2s):
    plot([x1, x2], [y1, y2], 'r-', alpha=.2)
    if True:
        x1, y1 = dot(R, [x1, y1])
        x2, y2 = dot(R, [x2, y2])
        plot([x1, x2], [y1, y2], 'r-', alpha=.2)
        x1, y1 = dot(R, [x1, y1])
        x2, y2 = dot(R, [x2, y2])
        plot([x1, x2], [y1, y2], 'r-', alpha=.2)


starts = list(zip(x1s, y1s))
stops = list(zip(x2s, y2s))
N = len(starts)
M = len(stops)
assert N == M

def find_next_segment(path, starts, stops):
    last = array(path[-1])
    mind = 1e6
    for i, start in enumerate(starts):
        d = linalg.norm(start - last)
        if d < mind:
            mind = d
        # print i, throw, d
        if d < 1:
            path.append(stops.pop(i))
            dups.append(starts.pop(i))
            break
    else:
        raise ValueError("no more points")
    return

# remove = [95]
remove = []
for i in remove:
    starts.pop(i)
    stops.pop(i)
start_i = 27
path = [array(starts.pop(start_i)), array(stops.pop(start_i))]
rest = []
dups = []
while starts:
    try:
        find_next_segment(path, starts, stops)
    except ValueError:
        try:
            find_next_segment(path, stops, starts)
        except ValueError:
            if linalg.norm(array(path[-1]) - path[0]) < 1:
                break
            rest.append(path.pop())
path = array(path)
rest.extend(stops)
rest = array(rest)
# plot(path[:,0], path[:,1], 'm-', linewidth=6, alpha=.2)

divs = [[2, 14],
        [14, 26],
        [38, 46]]

pth = MyPath()
for start, stop in divs:
    dat = path[start-1:stop]
    pth.moveTo(*dat[0])
    [pth.lineTo(*xy) for xy in dat[1:]]

print('HEIGHT (in)', (pth.getRight() - pth.getLeft()) / inch * scale)
print(' WIDTH (in)', (pth.getTop() - pth.getBottom()) / inch * scale)

## now find all segments that are in the middle (not on the edge).
starts = list(zip(x1s, y1s))
stops = list(zip(x2s, y2s))
path = array(path)
inside = MyPath()
figure(1)
for start, stop in zip(starts, stops):
    start = array(start)
    stop = array(stop)

    d1s = start[newaxis,:] - path
    d1 = min(sqrt(sum(d1s * d1s, axis=1)))

    d2s = stop[newaxis,:] - path
    d2 = min(sqrt(sum(d2s * d2s, axis=1)))
    
    if d1 + d2 > 2:
        inside.moveTo(*start)
        inside.lineTo(*stop)
        plot([start[0], stop[0]], [start[1], stop[1]], 'b-')

liz = [pth, inside]
print('len(liz[0].points)', len(liz[0].points))
liz_colors = [constants.red, constants.blue]
colors = 'bgrpk'

i = 0
vec = (knee - foot + knee - head)
rightv = (head - foot + head - knee) * 1
downv = (head - knee + foot - knee) * 1
for start, stop in divs:
    dat = path[start-1:stop]
    color = colors[i % len(colors)]
    i += 1
    figure(1)
    plot(dat[:,0], dat[:,1], '%s-' % color, linewidth=5)
    print(dat)
    # figure(2)
    # plot(dat[:,0], dat[:,1], '%s-' % color, linewidth=5, alpha=.5)
TOP, RIGHT = can._pagesize
TOP -= 25 * inch
BOTTOM = -25 * inch / scale
TOP = BOTTOM + can._pagesize[1] / scale
RIGHT = 4800
for ang in [0, 120, 240]:
    center = foot
    r = rotate(center, dat, ang)
    r_path = [x.rotate(ang, center, copy=True) for x in liz]
    for k in range(12):
        for j in range(12):
            vec = k * rightv + j * downv
            pth_copy = [x.translate(*vec, copy=True) for x in r_path]
            for x, c in zip(pth_copy, liz_colors):
                if 0 < x.getLeft() and x.getRight() < RIGHT:
                    if BOTTOM < x.getBottom() and x.getTop() < TOP:
                        x.drawOn(can, color=c, segmentate=False) 

can.showPage()
can.save()
print('wrote', can._filename)

show()
