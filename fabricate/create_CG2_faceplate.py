 # -*- coding: latin-1 -*-
import shutil
import string
import os.path
from random import choice
import string
from numpy import *
import PIL.Image
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing, Group, String, Circle, Rect
from reportlab.lib.units import inch, mm, cm
from reportlab.lib.colors import pink, black, red, blue, green, white
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
import reportlab.rl_config
import codecs
reportlab.rl_config.warnOnMissingFontGlyphs = 0
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import glob
import os.path
import sys
sys.path.append('/home/justin/Dropbox/WyoLumCode/CNC/')
from cnc import *
from baffles import *

sys.path.append('../')
from cnc import *

from numpy import arange
from copy import deepcopy
import Langs.Simulate2x
import Langs.Simulate1440

mount_r =  1.5 * mm
pcb_w = 6.4 * inch
pcb_h = 9 * inch

WIDTH = 19.675 * inch
PCB_OFF = .0 * inch
HEIGHT = 9 * inch + 2 * PCB_OFF
corner_holes = array([ ## mount posts ## with magnets
        (        6 * mm,          6 * mm, mount_r),
        (        6 * mm, HEIGHT - 6 * mm, mount_r),
        (WIDTH - 6 * mm,          6 * mm, mount_r),
        (WIDTH - 6 * mm, HEIGHT - 6 * mm, mount_r)])


MARGIN = 1 * inch
x0 = (WIDTH - 2 * pcb_w)/2 + .2 * inch
dx = 0.4 * inch
dy = 0.7 * inch

__version__ = 'cg2_v0.1alpha'

directory = './'
linewidth = 1.

fontnames = ['HELVETICA-BOLD', 'Helvetica-Bold',
             'HELVETICA', 'Helvetica',
             ]
fontpath = ['/home/justin/Dropbox/WyoLumCode/fonts/', '/home/justin/Documents/googlefontdirectory/']

BAFFLE_H = 20.00 * mm - 3.9 * mm
BAFFLE_T = .076 * inch

h_baffle = c3jr_h_baffle(BAFFLE_H,
                         BAFFLE_T,
                         n_notch=33,
                         delta=dx,
                         overhangs=(BAFFLE_T/2, BAFFLE_T/2),
                         overhang_heights=(None, None),
                         overhang_tapers=(False, False),
                         board_hooks=(5*mm, 5*mm),
                         board_hooks_up=False,
                         margin=0.016
                         )
v_baffle = c3jr_v_baffle(BAFFLE_H,
                         BAFFLE_T,
                         n_notch=9,
                         delta=dy,
                         overhangs=(.15 * inch, .15 * inch),
                         overhang_heights=(None, None),
                         overhang_tapers=(True, True),
                         margin=0.016
                         )
def button_hole(x, y, p):
    w = .3 * inch
    h = .3 * inch
    p.translate(-x + w/2, -y + w/2)
    p.moveTo(0, 0)
    p.lineTo(w, 0)
    p.lineTo(w, h)
    p.lineTo(0, h)
    p.lineTo(0, 0)
    p.translate(x - w/2, y - w/2)
    return p

def create_backplate(can):
    can.translate(MARGIN, MARGIN)
    can.drawCentredString(WIDTH / 2, -MARGIN / 2, "CHRONOGRAM Backplate %s" % __version__)
    
    extra = .25 * mm
    p = outline(extra)
    if True:
        for hole in corner_holes:
            p.drill(*hole)

    cord_r = .1 * inch
    p.moveTo(-extra, .5*inch + cord_r)
    p.lineTo(cord_r, .5*inch + cord_r)
    center = array((cord_r, .5*inch))
    for theta in arange(90, -90, -1) * DEG:
        p.lineTo(center + [cord_r * cos(theta), cord_r * sin(theta)])
    p.lineTo(-extra, .5*inch - cord_r)

    p.drawOn(can, linewidth=linewidth)
    
    ## Draw finger hole
    finger_r = 8 * mm
    p = MyPath()
    p.moveTo(-extra, HEIGHT/2 + finger_r)
    p.lineTo(p.getLast() + (finger_r, 0))
    center = p.getLast() - (0, finger_r)

    for theta in arange(90, -90, -1) * DEG:
        p.lineTo(center + [finger_r * cos(theta), finger_r * sin(theta)])
    p.lineTo(-extra, HEIGHT/2 - finger_r)
    p.drawOn(can)

    p.moveTo(WIDTH + extra, HEIGHT/2 + finger_r)
    p.lineTo(p.getLast() - (finger_r, 0))
    center = p.getLast() - (0, finger_r)
    for theta in arange(90, 270, 1) * DEG:
        p.lineTo(center + [finger_r * cos(theta), finger_r * sin(theta)])
    p.lineTo(WIDTH + extra, HEIGHT/2 - finger_r)
    p.drawOn(can)

    if True:
        keyhole = Keyhole([2 * inch, 8 * inch])
        keyhole.drawOn(can, linewidth=linewidth)
        keyhole = Keyhole([WIDTH - 2 * inch, 8 * inch])
        keyhole.drawOn(can, linewidth=linewidth)

    pcb = getPCB(outline=False, leds=False, buttons=False, button_holes=True)
    pcb.translate(x0 - dx/2, PCB_OFF)
    pcb.drawOn(can, linewidth=linewidth)

    mounts = [
        [.15 * inch, .15 * inch, mount_r],
        [.15 * inch, pcb_h - .15 * inch, mount_r],
        [pcb_w - .15 * inch, .15 * inch, mount_r],
        [pcb_w - .15 * inch, pcb_h - .15 * inch, mount_r],
                    ]
    pcb = getPCB(outline=False, leds=False, buttons=False, button_holes=True)
    # for hole in mounts:
    #     pcb.drill(*hole)
    pcb.translate(x0 - dx/2, PCB_OFF)
    pcb.translate(pcb_w,0)
    pcb.drawOn(can, linewidth=linewidth)

def drawline(p, x0, y0, x1, y1, linewidth=linewidth):
    p.moveTo(x0, y0)
    p.lineTo(x1, y1)

def add_font(fontname, path=None):
    FONTNAME = fontname.upper()
    if FONTNAME not in fontnames:
        if path is None:
            print path
            def addit(args, d, names):
                # if 'CustomerFonts' in d:
                #     return ## skip proprietary fonts
                for fn in names:
                    FN = fn.upper()
                    if FN[:-4] == FONTNAME and FN[-4:] == '.TTF':
                        pdfmetrics.registerFont(TTFont(FN[:-4], os.path.join(d, fn)))
                        fontnames.append(FONTNAME)
                        if not os.path.exists(os.path.join('/home/justin/Dropbox/WyoLumCode/fonts/', fn)):
                            shutil.copy(os.path.join(d, fn), os.path.join('/home/justin/Dropbox/WyoLumCode/fonts/', fn))
                        break
            for fontdir in fontpath:
                os.path.walk(fontdir, addit, ())
                if FONTNAME in fontnames:
                    break
        else:
            path = '%s/%s.ttf' % (path, fontname)
            pdfmetrics.registerFont(TTFont(FONTNAME, path))
            fontnames.append(FONTNAME)
    return FONTNAME in fontnames

def new_canvas(basename):
    can = canvas.Canvas('%s/%s_%s.pdf' % (directory, basename, __version__),
                        pagesize=(WIDTH + 2 * MARGIN, HEIGHT + 2 * MARGIN))
    return can
def outline(extra=0):
    '''
    draw CG2 outline with "extra" margin for backplate tightness
    '''
    p = MyPath()
    p.moveTo(-extra, -extra)
    p.lineTo(WIDTH + extra, -extra)
    p.lineTo(WIDTH + extra, HEIGHT + extra)
    p.lineTo(-extra, HEIGHT + extra)
    p.lineTo(-extra, -extra)
    
    return p

def getPCB(outline=False, leds=False, buttons=False, button_holes=True):
    ''' PCB from back side'''
    nx = 16

    x0 = dx / 2
    y0 = 2.05 * inch

    ny = 8

    led_xs = arange(nx) * dx + x0
    led_ys = (arange(ny) * dy + y0)[::-1]
    pcb = MyPath()
    if outline:
        pcb.rect([0, 0,
                  pcb_w, pcb_h,])

    
    pcb_mounts = [[.2 * inch, 1.5*inch, mount_r],
                  [.2 * inch, pcb_h - 1.5 * inch, mount_r],
                  [pcb_w - .2 * inch, 1.5*inch, mount_r],
                  [pcb_w - .2 * inch, pcb_h - 1.5 * inch, mount_r],

                  # [.15 * inch, .15 * inch, mount_r],
                  # [.15 * inch, pcb_h - .15 * inch, mount_r],
                  # [pcb_w - .15 * inch, .15 * inch, mount_r],
                  # [pcb_w - .15 * inch, pcb_h - .15 * inch, mount_r],
                    ]
    for hole in pcb_mounts:
        pcb.drill(*hole)

    if leds:
        for x in led_xs:
            for y in led_ys:
                pcb.drill(x, y, 2.5*mm)


    labels = 'RST MODE DEC INC ENT'.split()
    for i in range(5):
        x = pcb_w - .5*inch - i * .6 * inch
        y = pcb_h - .4 * inch
        if buttons:
            pcb.drill(x, y, 2.5 * mm) # BUTTON
        if button_holes:
            button_hole(x, y, pcb)
            pcb.addText(x, y + .25 * inch, labels[i], 'TERMINALDOSIS-MEDIUM', 12)    
    ## thumbwheel
    x = pcb_w - .5 * inch - 5 * .6 * inch
    y = pcb_h - .5 * inch
    pcb.drill(x, y, .25 * inch)
    pcb.addText(x, pcb_h - .4 * inch + .25 * inch, 'DIM', 'TERMINALDOSIS-MEDIUM', 12)
    pcb.rect([pcb_w - .44 * inch - .62 * inch, .44 * inch,
              .62 * inch, .12 * inch])
    x = pcb_w - .44 * inch - .62 * inch
    y = .28 * inch
    # can.drawCentredString(y - .04 * inch, -x,'GRN')
    pcb.addText(x, y, 'G', 'TERMINALDOSIS-MEDIUM', 12)
    # can.drawCentredString(y, -x - .75 * inch,'BLK')
    pcb.addText(x + .65 * inch, y, 'B', 'TERMINALDOSIS-MEDIUM', 12)
    pcb.addText(x + .6 * inch / 2, y + .35 * inch, '5V FTDI', 'TERMINALDOSIS-MEDIUM', 12)
    return pcb

def create_faceplate(basename, style, case, font, fontsize, reverse=True, color=None,
                     can=None, showtime=False, who=None, baffles=False, do_corner_holes=False,
                     top=None,
                     bottom=None, fpid='NA'):
    if font.title().startswith('Helvetica'):
        font = font.title()
    else:
        font = font.upper()

    if can is None:
        can = new_canvas(basename + '_W%s' % fpid)
        save_can = True
    else:
        save_can = False
    can.saveState()
    
    if save_can:
        pass ## text only
        # can.setFont('Courier', 18)
        # can.drawCentredString(WIDTH / 2 + MARGIN, HEIGHT+1.5*MARGIN, "%s %s" % (basename, __version__))
    if who:
        pass
        # can.drawCentredString(WIDTH / 2 + MARGIN, .5*MARGIN, who)
    can.setFont(font, fontsize)
    
    # can.drawString(MARGIN, MARGIN/4, "FPID: %s" % fpid)
        
    # can.drawString(MARGIN, HEIGHT + 3 * MARGIN / 2, font)
    if reverse:
        can.translate(WIDTH + 2 * MARGIN, 0)
        can.scale(-1, 1)
    else:
        can.drawCentredString(WIDTH / 2 + MARGIN, MARGIN/2, "SAMPLE ONLY, DO NOT PRINT")

    if top:
        # can.drawCentredString(WIDTH / 2 + MARGIN, HEIGHT - 1.3 * inch + MARGIN, top)
        pass 
    if bottom:
        # can.drawCentredString(WIDTH / 2 + MARGIN, .9 * inch + MARGIN, bottom)
        pass

    if color:
        can.setFillColor(color)
        can.rect(MARGIN, MARGIN, WIDTH, HEIGHT, fill=True)
        can.setFillColor(white)

    can.translate(MARGIN, MARGIN)
    # outline().drawOn(can)

    
    
    x0 = (WIDTH - 2 * pcb_w)/2 + .2 * inch
    dx = 0.4 * inch
    nx = 32

    pcb = getPCB(outline=True, leds=True, buttons=True, button_holes=True)
    pcb.translate(x0 - dx/2, PCB_OFF)
    # pcb.drawOn(can)

    pcb.translate(pcb_w, 0)
    # pcb.drawOn(can)

    y0 = 2.10 * inch
    dy = 0.7 * inch
    ny = 8

    baffle_xs = arange(nx + 1) * dx + x0 - dx/2
    baffle_ys = arange(ny + 1) * dy + y0 - dy/2

    led_xs = arange(nx) * dx + x0
    led_ys = (arange(ny) * dy + y0)[::-1]
    if type(style) == type(''):
        lines = style.strip().splitlines()
    else:
        lines = style

################################################################################
    encName = 'winansi'
    decoder = codecs.lookup(encName)[1]
    def decodeFunc(txt):
        if txt is None:
            return ' '
        else:
            return case(decoder(txt, errors='replace')[0])
    # lines = [[decodeFunc(case(char)) for char in line] for line in lines]
################################################################################

    can.setFont(font, fontsize)

    asc, dsc = pdfmetrics.getAscentDescent(font,fontsize)
    if case('here') == 'HERE':
        v_off = asc/2
    else:
        v_off = asc/3
        if 'thegirlnextdoor' in font.lower():
            v_off = asc/5
    if 'italic' in font.lower():
        h_off = pdfmetrics.stringWidth('W', font, fontsize) / 8.
    else:
        h_off = 0
    
    if showtime:
        can.setFillColor((.1, .1, .1))

    xmin = min(baffle_xs)
    xmax = max(baffle_xs)
    ymin = min(baffle_ys)
    ymax = max(baffle_ys)
    if baffles: ## DRAW_GRID???
        p = MyPath()
        for x in baffle_xs:
            drawline(p, x, ymin, x, ymax)
        for y in baffle_ys:
            drawline(p, xmin, y, xmax, y)
        p.drawOn(can, linewidth=linewidth)

    for i, y in enumerate(led_ys):
        for j, x in enumerate(led_xs):
            # can.circle(x, y, 2.5 * mm, fill=False)
            if len(lines[i]) > j:
                can.drawCentredString(x - h_off, y  - v_off, case(lines[i][j]))
    if showtime:
        can.setFillColor((1, 1, 1))
        timechars = [[0, 0], [0, 1],  # it 
                [0, 3], [0, 4],  # is
                [1, 0], [1, 1], [1, 2], [1, 3], # five
                [2, 3], [2, 4], # to
                [3, 0], [3, 1], [3, 2], [3, 3], [3, 4], # three
                [5, 10], [5, 11], [5, 13], [5, 14], [5, 15], # in the
                [6, 8], [6, 9], [6, 10], [6, 11], [6, 12], [6, 13], [6, 14], # morning
                ]
        for i, j in timechars:
            can.drawCentredString(led_xs[j], led_ys[i]  - v_off, case(lines[i][j]))
            
        
    ## reference point
    can.setStrokeColor(black)
    can.setFillColor(black)
    # can.circle(baffle_xs[-1] + .25 * inch, baffle_ys[-1] + .25 * inch, .025, fill=True)
    can.circle(WIDTH - 1 * inch, 9 * inch, .025, fill=True)
    if save_can:
        can.showPage()
        can.save()
        print 'wrote', can._filename
    try:
        can.restoreState()
    except:
        pass


    return can._filename

def my_upper(s):
    return unicode(s, 'utf-8').upper()
def my_lower(s):
    return s.lower()
lower = my_lower
upper = my_upper

english2_v1 = Langs.Simulate2x.readwtf("Langs/English2_v1.wtf")['letters']
german2_v1440 = Langs.Simulate1440.readwtf("Langs/German2_v1440.csv")['letters']
cases = {'lower':lower,
         'UPPER':upper}

def main():
    font = 'UbuntuMono-BoldItalic'
    font = 'AveriaSansLibre-Regular'
    font = 'TerminalDosis-Regular'
    font = 'TerminalDosis-Medium'
    font = 'david'
    font = "Helvetica-Bold"
    font = 'JosefinSans-Regular'

    add_font('TerminalDosis-Medium')
    add_font('TerminalDosis-Regular')
    add_font(font)
    case = 'UPPER'
    case = 'lower'
    fontsize=35 # normal
    fontsize=28
    fpid = 'NONE'
    create_faceplate('english2_v1_%s_%s_%s' % (font, case, fontsize), 
                     english2_v1, 
                     # 'german2_v1440_%s_%s_%s' % (font, case, fontsize), 
                     # german2_v1440, 
                     cases[case], 
                     font, fontsize, baffles=False, reverse=True, fpid=fpid)
    bp_can = new_canvas('Backplate')
    create_backplate(bp_can)
    t = MyText(15.2 * inch, .85*inch, "MASTER", centered=False)
    t.drawOn(bp_can)
    bp_can.save()
    print 'wrote', bp_can._filename
    baff_can = new_canvas("Baffles")

    localizer = MyPath()
    lw = .34 * inch
    localizer.drill(lw/2, lw/2, 1.5 * mm)
    localizer.drill(lw/2, lw/2, 4.5 * mm)
    localizer.translate(2 * inch, 8 * inch)
    localizer.drawOn(baff_can)
    t = MyText(2 * inch, 8.5 * inch, "Localizer, 8 per CHRONOGRAM2", centered=False)
    t.drawOn(baff_can)


    h_baffle.translate(MARGIN+ .25 * inch, HEIGHT / 2 - 2 * BAFFLE_H)
    h_baffle.drawOn(baff_can)
    t = MyText(MARGIN+ .25 * inch, HEIGHT / 2 - .75 * BAFFLE_H, "H BAFFLE, 10 per CHRONOGRAM2", centered=False)
    t.drawOn(baff_can)

    v_baffle.translate(MARGIN+ .25 * inch, HEIGHT / 2 + 2 * BAFFLE_H)
    v_baffle.drawOn(baff_can)
    t = MyText(MARGIN + .25 * inch, HEIGHT / 2 + 3.25 * BAFFLE_H, "V BAFFLE, 34 per CHRONOGRAM2", centered=False)
    t.drawOn(baff_can)

    baff_can.showPage()
    baff_can.save()

    print 'wrote', baff_can._filename
if __name__ == '__main__':
    main()
