import pylab as pl
import glob
import time
import tkFileDialog
import string
import os
from Tkinter import *
import sys
import csv
# from scipy import *
from numpy import *
from spreadsheet import *

update_step = 300 ## numnber of seconds between frames
hold_ms = 10    ## number of ms to hold each frame

exit = False
file_opt = {}

def getAssignment(cellstr, name_ck=None, typ=int):
    '''
    return the name and value assigned in specified cell
    check that name is same if name_ck is provided

    "n_row = 16" --> 16
    '''
    if '=' not in cellstr:
        raise ValueError('No "=" in cellstr "%d"' % cellstr)
    name, value = cellstr.split('=')
    name = name.strip()
    value = value.strip()
    if typ:
        value = typ(value)
    if name_ck:
        assert name_ck == name, '%s != %s' % (name_ck, name)
    return value

def get_bitmap(ss, start_row, start_col, n_row, n_col):
    dat = [l[start_col:start_col + n_col] for l in 
           ss.lines[start_row:start_row + n_row]]
    bitmap = zeros((n_row, n_col), bool)

    for i, l in enumerate(dat):
        for j, w in enumerate(l):
            if w.strip():
                bitmap[i, j] = 1
    return bitmap

class Wordmap:
    def __init__(self, ss, start_row, start_col, n_row):
        cellstr = ss.lines[start_row][start_col]
        n_word = getAssignment(cellstr)
        stop_col = start_col + 1 + n_word

        self.words = ss.lines[start_row][start_col + 1:stop_col]
        rows = ss.lines[start_row + 1][start_col + 1:stop_col]
        cols = ss.lines[start_row + 2][start_col + 1:stop_col]
        lens = ss.lines[start_row + 3][start_col + 1:stop_col]
        self.rows = map(int, rows)
        self.cols = map(int, cols)
        self.lens = map(int, lens)
        self.bitmap = get_bitmap(ss, start_row + 5, start_col + 1, n_row, n_word)

    def get_word(idx):
        return self.words[idx], self.rows[idx], self.cols[idx]

    def get_line(self, idx):
        return ' '.join(w for j, w in enumerate(self.words) if
                       self.bitmap[idx][j])
    def cconvert(self, cname, outfile=None, hex=False):
        if outfile is None:
            outfile = sys.stdout

        l = len(self.words)
        xs = self.cols
        ys = self.rows
        lens = self.lens
        if l % 8 == 0:
            n_word = l
        else:
            n_word = (l // 8 + 1) * 8
        if hex:
            outfile.write(struct.pack('B', n_word))
        else:
            print >> outfile, 'static prog_char %s_WORDS[] PROGMEM = {' % cname
            print >> outfile,  '    %3d, // # words' % n_word ## #words on faceplate

        ## define words
        for i in range(n_word):
            if i < l:
                x = xs[i]
                y = ys[i]
                ln = lens[i]
                if hex:
                    outfile.write('BBB', (x, y, l))
                else:
                    print >> outfile,  '    %3d,%3d,%3d,' % (x, y, ln),
            else:
                if hex:
                    outfile.write('BBB', (0, 0, 0))
                else:
                    print >> outfile,  '      0,  0,  0,',
            if i % 4 == 3:
                if not hex:
                    print >> outfile,  "    // words"
        if hex:
            outfile.write()
            outfile.write('B', n_word // 8)
        else:
            print >> outfile,  '};'
            print >> outfile,  ''
            print >> outfile,  'static prog_char %s_SEQ[] PROGMEM = {' % cname
            print >> outfile,  '   %s, // number of bytes per state' % (n_word // 8)
        mlen = max(lens)
        words = [w for w in self.words]
        if  len(self.words) % 8 != 0:
            words.extend(['' for i in range(8 - len(self.words) % 8)])
        ## print words in columns, right most col is first word
        padded_words = [w.rjust(mlen) for w in words]
        assert len(padded_words) % 8 == 0
        ### VOODOO HERE
        tmp_pw = ['' for w in padded_words]
        for j in range(n_word):
            # padded_words.insert(k + j, list(' ' * mlen))
            byte_num = j // 8
            bit_num = j % 8
            tmp_pw[byte_num * 8 + 8 - bit_num - 1] = padded_words[j]
        padded_words = tmp_pw
        i = n_word  - n_word % 8
        while i > 0:
            padded_words.insert(i, ' ')
            padded_words.insert(i, ' ')
            padded_words.insert(i, ' ')
            padded_words.insert(i, ' ')
            i -= 8
        padded_words = [list(w.rjust(mlen)) for w in padded_words]

        ws = transpose(padded_words)
        word_strings = []
        for l in ws:
            word_strings.append('//    ' + ''.join(l))
        ## flip bytes then print (TODO)
        for l in word_strings:
            if hex:
                pass
            else:
                print >> outfile, l
        print >> outfile,  '   ',
        for i, bits in enumerate(self.bitmap):
            bytes = bits2bytes(bits)
            for val in bytes:
                if hex:
                    outfile.write('B', val)
                else:
                    print >> outfile,  '%s,' % uint8_2_bits(val),
            if not hex:
                print >> outfile,  "\n   ",
        if not hex:
            print >> outfile,  '};'
        
def readwtf(csvfile):
    f = csv.reader(open(csvfile))
    lines = list(f)
    ss = Spreadsheet(lines)
    ## check WTF
    assert ss.getRegion('C2')[0][0] == '0'
    
    ## check version is hms
    assert getAssignment(ss.getCell("A2"), typ=None) == "hms", "Incorrect format in cell 'A2' '%s', expected 'version=hms'" % ss.getCell('A2')

    n_row = getAssignment(ss.getCell('A4'), name_ck='n_row')
    n_col = getAssignment(ss.getCell('A5'), name_ck='n_col')
    # n_hour_word = getAssignment(ss.getCell('A6'), name_ck='n_hour_word')
    # n_min_word = getAssignment(ss.getCell('A7'), name_ck='n_min_word')
    # n_sec_word = getAssignment(ss.getCell('A8'), name_ck='n_sec_word')

    print 'n_row', n_row
    print 'n_col', n_col
    # print 'n_min_word', n_min_word
    # print 'n_sec_word', n_sec_word
    start_row, start_col = ss.parsecell('C3')
    letters = [l[:n_col] for l in ss.getRegion('C3:**')[:n_row]]
    
    hour_wordmap = Wordmap(ss, 25, 0, 24)
    min_wordmap = Wordmap(ss, 56, 0, 60)
    if ss.getCell('A124') is not None:
        sec_wordmap = Wordmap(ss, 123, 0)
    else:
        sec_wordmap = None
                              
    for hour in range(24):
        # print hour_wordmap.get_line(hour)
        for min in range(60):
            # print '    ', min_wordmap.get_line(min)
            pass
            
    author = ss.getCell('B20')
    email = ss.getCell('B21')
    licence = ss.getCell('B22')
    desc = ss.getCell('B23')
    return {'letters': letters,
            'n_row':n_row,
            'n_col':n_col,
            'hour_wordmap':hour_wordmap,
            'min_wordmap':min_wordmap,
            'sec_wordmap':sec_wordmap,
            'author':author,
            'email':email,
            'licence':licence,
            'desc':desc
            }

def readcsv(csvfile, n_row=8):
    f = csv.reader(open(csvfile))
    letters = [f.next() for i in range(n_row)]
    rows = f.next()
    cols = f.next()
    lens = f.next()
    words = f.next()[1:]
    n_word = len(words)
    bitmap = zeros((288, n_word), int)
    for i in range(288):
        l = f.next()
        for j, c in enumerate(l[1:]):
            if c:
                bitmap[i, j] = 1
    minutes_hack = list(f)
    if len(minutes_hack):
        min_rows = map(int, minutes_hack[0][1:])
        min_cols = map(int, minutes_hack[1][1:])
        n_min_led = min([len(min_rows),len(min_cols)])
        n_min_state = len(minutes_hack) - 2
        min_bitmap = zeros((n_min_state, n_min_led), int)
        for i, l in enumerate(minutes_hack[2:]):
            for j, v in enumerate(l[1:]):
                if v.strip() != '':
                    min_bitmap[i, j] = 1
        
    else:
        min_rows = []
        min_cols = []
        n_min_led = 0
        n_min_state = 0
        min_bitmap = None
    return {'letters': letters,
            'data':bitmap, 
            'rows':map(int, rows[1:]),
            'cols':map(int, cols[1:]),
            'lens':map(int, lens[1:]),
            'words':words[1:],
            'min_rows':min_rows,
            'min_cols':min_cols,
            'n_min_led': n_min_led,
            'n_min_state': n_min_state,
            'min_bitmap': min_bitmap,
            }

def bitmap(csvfile):
    data = readwtf(csvfile)
    import pylab as pl
    pl.pcolormesh(data['data'][::-1], cmap='binary_r')
    words = data['words']
    words = [unicode(w, 'utf-8') for w in words]
    locs, tics = pl.xticks(arange(len(words)) + .5, words, rotation=90)
    pl.yticks(arange(0, 288, 12), ['%d:00' % i for i in range(24)[::-1]])
    pl.ylim(0, 288)
    pl.xlim(0, len(words))
    pl.show()

class ScreenJr:
    def __init__(self, n_col=16):
        self.buffer = zeros(n_col, 'uint8')

    def __getitem__(self, idx):
        return self.buffer[idx]

    def setPixel(self, row, col, val):
        if color:
            self.buffer[col] &= (1 << row)
        else:
            self.buffer[col] |= (1 << row)

    def getPixel(self, row, col):
        out = self.buffer[col] & (1 << col)
        return out
    def clearall(self):
        self.buffer *= 0


OFF = '#202020'
ON = '#FFFFFF'
my_inch = 40.
XOFF = 2.5 * my_inch
YOFF = 1.85 * my_inch
dx = .4 * my_inch
dy = .7 * my_inch


def nop():
    pass

font = ('Neucha', 20)

class ClockTHREEjr:
    def __init__(self, wtf, font=font, save_images=False, dt=300):
        # def simulate(csvfile, font=('Kranky', 20)):
        self.font=font
        tk = Tk()
        tk.tk_setPalette('#000000')
        tk.title('ClockTHREEjr')
        tk.bind("<Key>", self.key_press)
        self.tk = tk

        self.display_second = 86400 - 300 * 4
        self.update_step = dt
        self.wtf = wtf
        self.readwtf(wtf)
        self.last_update = 0
        self.minimum_update_time = .25
        self.save_images = save_images
        self.img_num = 0
        if self.save_images:
            self.movie_dir = wtf[:-4]
            print 'saving images in', self.movie_dir
            if not os.path.exists(self.movie_dir):
                os.mkdir(self.movie_dir)
            else:
                for png in glob.glob("%s/*.png" % self.movie_dir):
                    os.unlink(png)
        labels = []

        self.r = Frame(tk, background='#000000')
        margin = 2.5 * my_inch
        width = 2 * margin + self.N_COL * dx
        self.can = Canvas(self.r, width=width, height=9*my_inch)
        self.can.bind("<Button-3>", self.time_forward)
        self.can.bind("<Button-1>", self.time_backward)
        self.r.pack()
        self.makemenu()
        size = int(my_inch / 25. * 10.)
        self.did = self.can.create_text(XOFF + 9 * dx, YOFF -1 * dy, text="00:00:00", font=('Digital-7 Mono', size), fill=ON)
        filename = os.path.split(self.wtf)[1][:-4]
        self.can.create_text(XOFF + 7 * dx, 
                             YOFF + 9 * dy, text=filename, font=('Times', 10), fill=ON)
        all_labels_off = {}
        for row in range(self.N_ROW):
            for col in range(self.N_COL):
                all_labels_off[row, col] = self.can.create_text(XOFF + dx * col, YOFF + dy * row, text=self.letters[row][col], font=self.font, fill=OFF)
        all_labels_on = {}
        self.labels_on = {}
        print 'font', self.font
        for i in range(self.N_ROW):
            for j in range(self.N_COL):
                all_labels_on[i, j] = self.can.create_text(XOFF + dx * j, YOFF + dy * i, text=self.letters[i][j], font=self.font, fill=ON)
                self.can.itemconfigure(all_labels_on[i, j], state='hidden')
        self.can.pack()
        # display = Label(r, text='00:00', font=('DS-Digital', 20))
        self.display = Label(self.r, text='00:00:00', font=('Digital-7 Mono', 15))
        self.all_labels_on = all_labels_on
        self.all_labels_off = all_labels_off
        self.after_id = self.r.after(1, self.next_time)
        self.tk.protocol("WM_DELETE_WINDOW", self.destroy)
        # self.pause()
        self.tk.mainloop()
    
    def redraw_letters(self):
        for i in range(self.N_ROW):
            for j in range(self.N_COL):
                self.can.itemconfigure(self.all_labels_off[i, j], text=self.letters[i][j])
                self.can.itemconfigure(self.all_labels_on[i, j], state='hidden', text=self.letters[i][j], font=self.font)
        self.labels_on = {}
        self.next_time()
                
    def readwtf(self, wtf):
        try:
            self.data = readwtf(wtf)
        except AssertionError:
            raise
            # self.askopenfilename()
        self.letters = self.data['letters']
        # self.n_word = len(self.data['words'])
        self.N_ROW = self.data['n_row']
        self.N_COL = self.data['n_col']

        print 'author:', self.data['author']
        print 'email:', self.data['email']
        print 'licence:', self.data['licence']
        print 'description:\n', self.data['desc']
    def askopenfont(self, *args, **kw):   
        """Returns an opened file in read mode.
        This time the dialog just returns a filename and the file is opened by your own code.
        Credit: http://tkinter.unpythonic.net/wiki/tkFileDialog
        """

        self.tk.tk_setPalette('#888888')
        save_update_step = self.update_step
        self.update_step = 0

        filename = tkFileDialog.askopenfilename(parent=self.tk)
        if filename:
            self.readwtf(filename)
            self.redraw_letters()
        self.update_step = save_update_step
        self.tk.tk_setPalette('#000000')
    def askopenfilename(self, *args, **kw):   
        """Returns an opened file in read mode.
        This time the dialog just returns a filename and the file is opened by your own code.
        Credit: http://tkinter.unpythonic.net/wiki/tkFileDialog
        """

        self.tk.tk_setPalette('#888888')
        save_update_step = self.update_step
        self.update_step = 0

        filename = tkFileDialog.askopenfilename(parent=self.tk)
        if filename:
            self.readwtf(filename)
            self.redraw_letters()
        self.update_step = save_update_step
        self.tk.tk_setPalette('#000000')
    def cconvert(self):
        self.tk.tk_setPalette('#888888')
        save_update_step = self.update_step
        self.update_step = 0
        outfn = None
        while outfn is None:
            outfn = tkFileDialog.asksaveasfilename(
                filetypes=[('h files', '.h')],
                title='Save H-file')
            
            if outfn:
                cconvert(self.wtf, 8, outfn)
        self.update_step = save_update_step
        self.tk.tk_setPalette('#000000')

    def makemenu(self):
    ##  Make menu
        # create a toplevel menu
        menubar = Menu(self.tk)
        # menubar.add_command(label="Hello!", command=none)
        # menubar.add_command(label="Quit!", command=tk.quit)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.askopenfilename)
        filemenu.add_command(label="C-Convert", command=self.cconvert)

        menubar.add_cascade(label="File", menu=filemenu)

        fontmenu = Menu(menubar, tearoff=0)
        fontmenu.add_command(label='SelectFont', command=self.askopenfont)
        menubar.add_cascade(label="TBD", menu=fontmenu)

        langmenu = Menu(menubar, tearoff=0)
        langmenu.add_command(label="TBD", command=nop)
        menubar.add_cascade(label="Lang", menu=langmenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=nop)
        menubar.add_cascade(label="Help", menu=helpmenu)
        # display the menu
        self.tk.config(menu=menubar)
        self.menu=menubar

    def time_forward(self, event):
        self.pause()
        self.display_second += 300

    def time_backward(self, *args, **kw):
        self.pause()
        self.display_second -= 300

    def do_uppercase(self):
        for i, j in self.all_labels_off:
            self.can.itemconfigure(self.all_labels_on[i, j], text=self.letters[i][j].upper())        
            self.can.itemconfigure(self.all_labels_off[i, j], text=self.letters[i][j].upper())

    def do_lowercase(self):
        for i, j in self.all_labels_off:
            self.can.itemconfigure(self.all_labels_on[i, j], text=self.letters[i][j].lower())        
            self.can.itemconfigure(self.all_labels_off[i, j], text=self.letters[i][j].lower())

    def key_press(self, event):
        if event.char == ' ':
            self.toggle_pause()
        elif event.char == 'H':
            self.pause()
            self.display_second += 3600
        elif event.char == 'h':
            self.pause()
            self.display_second -= 3600
        elif event.char == 'F':
            self.pause()
            self.display_second += 60 * 5
        elif event.char == 'f':
            self.pause()
            self.display_second -= 60 * 5
        elif event.char == 'M':
            self.pause()
            self.display_second += 60
        elif event.char == 'm':
            self.pause()
            self.display_second -= 60
        elif event.char == 'S':
            self.pause()
            self.display_second += 15
        elif event.char == 's':
            self.pause()
            self.display_second -= 15
        elif event.char == '.':
            self.pause()
            self.display_second += 1
        
        elif event.char == 'U':
            self.do_uppercase()
        elif event.char == 'l':
            self.do_lowercase()

        
    def toggle_pause(self):
        if self.update_step == 0: ## unpause
            self.unpause()
        else: ## pause
            self.pause()
    def pause(self):
        self.save_update_step = self.update_step
        self.update_step = 0
    def unpause(self):
        self.update_step = self.save_update_step

    def next_time(self): # every minute
        now = time.time()
        if now - self.last_update > self.minimum_update_time:
            self.last_update = now
            self.display_second += self.update_step
            self.display_second %= 86400
            minute = self.display_second / 60
            time5 = minute / 5

            tm = '%02d:%02d:%02d' % (minute / 60, minute % 60, self.display_second % 60)
            self.can.itemconfig(self.did, text=tm)
            # display.config(text=tm)
            self.sequence_leds(self.display_second)
            if True:
                if self.save_images:
                    if self.update_step == 300:
                        self.img_num = time5
                    else:
                        self.img_num += 1

                    fn = '%s/%04d.png' % (self.movie_dir, self.img_num)
                    if not os.path.exists(fn) and sys.platform.startswith('win'): # windows
                        import ImageGrab
                        
                        geom =self.tk.geometry()
                        size, x, y = geom.split('+')
                        w, h = size.split('x')
                        ImageGrab.grab((int(x), int(y), 
                                        int(x) + int(w) + 10, int(y) + int(h) + 30)).save(fn)
                    elif not os.path.exists(fn): ## linux
                        print fn
                        os.system('import -window ClockTHREEjr %s' % fn)
                    if time5 == 288:
                        self.save_images = False
                    ## use convert to create animated gifs I.E.
                    ## > convert -delay 50 Hungarian_v1/*.png Hungarian_v1.gif
                    

        if exit:
            self.tk.destroy()
        else:
            self.after_id = self.r.after(hold_ms, self.next_time)
        
    def turn_on(self, i, j):
        if (i, j) in self.labels_on:
            pass
        else:
            self.labels_on[i, j] = self.all_labels_on[i, j]
            self.can.itemconfigure(self.all_labels_on[i, j], state='normal')
    def turn_off(self, i, j):
        if (i, j) in self.labels_on:
            self.can.itemconfigure(self.all_labels_on[i, j], state='hidden')
            del self.labels_on[i, j]
    def set_pixel(self, i, j, state):
        if state:
            self.turn_on(i, j)
        else:
            self.turn_off(i, j)
        for l in self.labels_on:
            self.can.delete(l)
    def sequence_leds(self, seconds):
        '''
        Display time sentence for time at seconds past midnight
        '''
        h = seconds // 3600
        m = (seconds // 60) % 60
        s = seconds % 60

        h_word_state = self.data['hour_wordmap'].bitmap[h]
        m_word_state = self.data['min_wordmap'].bitmap[m]

        for i in where(1 - h_word_state)[0]:
            bit = False
            row = self.data['hour_wordmap'].rows[i]
            col = self.data['hour_wordmap'].cols[i]
            length = self.data['hour_wordmap'].lens[i]
            for x in range(length):
                self.set_pixel(row, col + x, bit)
        for i in where(h_word_state)[0]:
            bit = True
            row = self.data['hour_wordmap'].rows[i]
            col = self.data['hour_wordmap'].cols[i]
            length = self.data['hour_wordmap'].lens[i]
            for x in range(length):
                self.set_pixel(row, col + x, bit)
        for i in where(1 - m_word_state)[0]:
            bit = False
            row = self.data['min_wordmap'].rows[i]
            col = self.data['min_wordmap'].cols[i]
            length = self.data['min_wordmap'].lens[i]
            for x in range(length):
                self.set_pixel(row, col + x, bit)
        for i in where(m_word_state)[0]:
            bit = True
            row = self.data['min_wordmap'].rows[i]
            col = self.data['min_wordmap'].cols[i]
            length = self.data['min_wordmap'].lens[i]
            for x in range(length):
                self.set_pixel(row, col + x, bit)

    def destroy(self, *args, **kw):
        self.r.after_cancel(self.after_id)
        self.tk.destroy()

def uint8_2_bits(uint):
    s = '0b'
    for i in range(7, -1, -1):
        if uint >> i & 1:
            s += '1'
        else:
            s += '0'
    return s

def bits2int(bits):
    return int(sum([b * 2 ** i for i, b in enumerate(bits)]))

def bits2bytes(bits):
    n = len(bits) // 8
    if len(bits) % 8:    
        n += 1

    out = []
    for i in range(n):
        out.append(bits2int(bits[i * 8:(i + 1) * 8]))
    return out

def cconvert(filename, n_row=8, outfilename=None):
    data = readwtf(filename)
    if outfilename is None:
        outfile = sys.stdout
    else:
        outfile = open(outfilename, 'w')
    data['hour_wordmap'].cconvert('HOUR', outfile)
    data['min_wordmap'].cconvert('MINUTE', outfile)
    
def timelist(fn):
    data = readwtf(fn)
    words = data['words']
    for i, l in enumerate(data['data']):
        print '%02d:%02d' % divmod(i * 5, 60),
        for j, bit in enumerate(l):
            if bit:
                print words[j],
        print
                                                    
usage = '>Simulate.py wtf font save dt'
if __name__ == '__main__':
    print usage
    n_row = 8
    if len(sys.argv) > 1:
        fn = sys.argv[1]
    else:
        n = len(glob.glob('/home/justin/Downloads/ClockTHREEjr faceplate layouts - English2_v1*.csv'))
        if n == 1:
            fn = '/home/justin/Downloads/ClockTHREEjr faceplate layouts - English2_v1.csv'
        else:
            fn = '/home/justin/Downloads/ClockTHREEjr faceplate layouts - English2_v1 (%d).csv' % (n - 1)
    if len(sys.argv) > 2:
        fontname = sys.argv[2]
    else:
        fontname = 'David'
        fontname = 'Times'
        fontname = 'Neucha'
    if len(sys.argv) > 3:
        save_images = sys.argv[3] == 'True'
    else:
        save_images = False
    if len(sys.argv) > 4:
        dt = float(sys.argv[4])
    else:
        dt = 300
    fontsize = int(my_inch / 25. * 10)
    ClockTHREEjr(fn, (fontname, fontsize), save_images=save_images, dt=dt)
    
