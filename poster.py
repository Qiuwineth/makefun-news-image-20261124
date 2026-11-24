#!/usr/bin/env python3
"""THE WORLD ON TUESDAY - a one-page newspaper of 24 November 2026.
Draws the poster with a 5x7 bitmap font and a tiny PNG writer; pure stdlib.
No network, no randomness: the same run always writes the same bytes."""
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (246, 241, 229)
INK = (24, 22, 18)
RED = (178, 32, 42)
BLUE = (29, 58, 95)
GREY = (112, 104, 90)
LIGHT = (226, 219, 203)

# 5x7 bitmap font: each glyph is 7 rows of 5 bits, top row first.
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x0E, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x01, 0x0E),
    '.': (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ',': (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ':': (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ';': (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    '?': (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '-': (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    '•': (0x00, 0x00, 0x0E, 0x0E, 0x0E, 0x00, 0x00),
    '%': (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '+': (0x00, 0x00, 0x04, 0x0E, 0x04, 0x00, 0x00),
    '/': (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
}


class Canvas:
    def __init__(self, w=W, h=H, bg=PAPER):
        self.w, self.h = w, h
        self.buf = bytearray(bg) * (w * h)

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c, fill=True):
        if fill:
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    self.px(xx, yy, c)
        else:
            for xx in range(x, x + w):
                self.px(xx, y, c)
                self.px(xx, y + h - 1, c)
            for yy in range(y, y + h):
                self.px(x, yy, c)
                self.px(x + w - 1, yy, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.rect(x0 - t // 2, y0 - t // 2, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=False):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.px(xx, yy, c)
                elif abs(d - r * r) <= r:
                    self.px(xx, yy, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            if ch == ' ':
                cx += 6 * scale
                continue
            g = FONT.get(ch)
            if g is None:
                cx += 6 * scale
                continue
            for row, bits in enumerate(g):
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + row * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def wrap(self, s, max_w, scale):
        lines, cur = [], ''
        for word in s.split(' '):
            trial = (cur + ' ' + word).strip()
            if self.text_w(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * cv.w * 3:(y + 1) * cv.w * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        return struct.pack('>I', len(data)) + typ + data + struct.pack('>I', zlib.crc32(typ + data) & 0xFFFFFFFF)

    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', comp)
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


# ---- small line icons, drawn from rectangles, lines and circles ----

def icon_tower(cv, x, y, s, c):
    # A tall tower with a pointed crown, struck: a burst at the top.
    w = 10 * s
    cv.rect(x + 3 * s, y + 4 * s, 4 * s, 6 * s, c)
    cv.line(x + 3 * s, y + 4 * s, x + 5 * s, y, c, s)
    cv.line(x + 7 * s, y + 4 * s, x + 5 * s, y, c, s)
    cv.rect(x + 4 * s, y + 6 * s, 2 * s, s, PAPER)
    cv.rect(x + 4 * s, y + 8 * s, 2 * s, s, PAPER)
    cv.line(x + 5 * s, y - s, x + 2 * s, y - 3 * s, RED, s // 2 + 1)
    cv.line(x + 5 * s, y - s, x + 8 * s, y - 3 * s, RED, s // 2 + 1)
    cv.line(x + 5 * s, y - s, x + 5 * s, y - 4 * s, RED, s // 2 + 1)


def icon_ship(cv, x, y, s, c):
    cv.rect(x + 4 * s, y, s, 5 * s, c)
    cv.rect(x + s, y + s, 8 * s, s, c)
    cv.rect(x, y + 5 * s, 10 * s, 2 * s, c)
    cv.line(x + 2 * s, y + 7 * s, x + 8 * s, y + 7 * s, c, s)
    cv.line(x, y + 9 * s, x + 10 * s, y + 9 * s, BLUE, s // 2 + 1)
    cv.line(x + 2 * s, y + 10 * s, x + 8 * s, y + 10 * s, BLUE, s // 2 + 1)


def icon_building(cv, x, y, s, c):
    cv.rect(x + s, y, 8 * s, 10 * s, c)
    for wy in (2, 5, 8):
        for wx in (2, 5):
            cv.rect(x + wx * s, y + wy * s, s, s, PAPER)
    cv.line(x, y + 9 * s, x + 10 * s, y + 9 * s, RED, s)


def icon_flag(cv, x, y, s, c):
    cv.rect(x, y, s, 10 * s, c)
    cv.rect(x + s, y, 7 * s, 4 * s, RED)
    cv.rect(x + 2 * s, y + s, 2 * s, 2 * s, PAPER)
    cv.rect(x + 5 * s, y + s, 2 * s, 2 * s, PAPER)


def icon_satellite(cv, x, y, s, c):
    cv.rect(x + 3 * s, y + 4 * s, 4 * s, 3 * s, c)
    cv.rect(x, y + 3 * s, 2 * s, 5 * s, BLUE)
    cv.rect(x + 8 * s, y + 3 * s, 2 * s, 5 * s, BLUE)
    cv.line(x + 5 * s, y + 4 * s, x + 8 * s, y, c, s // 2 + 1)
    cv.circle(x + 8 * s, y, s, RED, fill=True)


def icon_trophy(cv, x, y, s, c):
    cv.rect(x + 2 * s, y, 6 * s, 4 * s, c)
    cv.rect(x + s, y + s, s, 2 * s, c)
    cv.rect(x + 8 * s, y + s, s, 2 * s, c)
    cv.rect(x + 4 * s, y + 4 * s, 2 * s, 3 * s, c)
    cv.rect(x + 2 * s, y + 7 * s, 6 * s, 2 * s, c)
    cv.rect(x + 3 * s, y + s, 4 * s, 2 * s, PAPER)


def icon_chart(cv, x, y, s, c):
    cv.vline(x, y, 10 * s, c, s)
    cv.hline(x, y + 9 * s, 10 * s, c, s)
    cv.line(x + s, y + 7 * s, x + 3 * s, y + 4 * s, RED, s)
    cv.line(x + 3 * s, y + 4 * s, x + 5 * s, y + 6 * s, RED, s)
    cv.line(x + 5 * s, y + 6 * s, x + 9 * s, y + 2 * s, RED, s)


# ---- layout ----

def render():
    cv = Canvas()
    MX = 40
    # masthead
    title = 'THE WORLD ON TUESDAY'
    cv.text((W - cv.text_w(title, 4)) // 2, 26, title, 4, INK)
    cv.hline(MX, 72, W - 2 * MX, RED, 4)
    date = '24 NOVEMBER 2026'
    cv.text((W - cv.text_w(date, 9)) // 2, 92, date, 9, INK)
    cv.hline(MX, 172, W - 2 * MX, INK, 2)

    # lead story
    y = 196
    icon_tower(cv, MX + 18, y + 30, 6, INK)
    lx = 250
    cv.text(lx, y, 'MIDDLE EAST - RIYADH', 3, RED)
    lead = ['HOUTHIS STRIKE', "RIYADH'S TALLEST", 'TOWER AGAIN']
    ly = y + 26
    for ln in lead:
        cv.text(lx, ly, ln, 6, INK)
        ly += 50
    sub = cv.wrap('SECOND HIT IN FIVE DAYS INJURES 11; FIGHTERS CLOSE ON ADEN', 700, 3)
    sy = ly + 4
    for ln in sub:
        cv.text(lx, sy, ln, 3, GREY)
        sy += 24
    cv.hline(MX, 428, W - 2 * MX, INK, 2)

    # second story
    y = 448
    icon_ship(cv, MX + 18, y + 22, 6, INK)
    cv.text(lx, y, 'LIBYA - BENGHAZI PORT', 3, RED)
    second = ['UKRAINE DRONES SINK', 'RUSSIAN CORVETTE IN LIBYA']
    ly = y + 26
    for ln in second:
        cv.text(lx, ly, ln, 5, INK)
        ly += 42
    sub = cv.wrap('UN SEEKS PROBE; ITALY RAISES CONCERN', 700, 3)
    sy = ly + 4
    for ln in sub:
        cv.text(lx, sy, ln, 3, GREY)
        sy += 24
    cv.hline(MX, 592, W - 2 * MX, INK, 2)

    # six-box grid
    boxes = [
        ('ZAPORIZHZHIA', 'STRIKE KILLS 2,', 'WOUNDS 40', 'FLAT BLOCK HIT, 4 CHILDREN HURT', icon_building),
        ('GAZA', 'AIRSTRIKE KILLS', 'HAMAS CHIEF', 'SIX MORE DEAD, TWO POLICE', icon_flag),
        ('ESTONIA', 'RUSSIA WARNS OF', "'OPEN WAR'", 'OVER BORDER CLOSURE PLANS', icon_flag),
        ('SPACE', 'NATO VOWS TO', 'DEFEND SPACE', 'AFTER NUCLEAR SATELLITE REPORTS', icon_satellite),
        ('SENEGAL', 'SENEGAL RESTORED', 'AS CHAMPIONS', 'AFRICA CUP TITLE RESTORED', icon_trophy),
        ('MARKETS', 'STOCKS SLIP', 'ON RATE FEARS', 'S&P 500 -0.95%; BRENT $87.51', icon_chart),
    ]
    bw, bh, gap = 464, 112, 10
    gx, gy = MX, 606
    for i, (kick, h1, h2, sub, icon) in enumerate(boxes):
        bx = gx + (i % 2) * (bw + gap)
        by = gy + (i // 2) * (bh + gap)
        cv.rect(bx, by, bw, bh, LIGHT, fill=False)
        icon(cv, bx + 14, by + 36, 3, INK)
        tx = bx + 66
        cv.text(tx, by + 10, kick, 2, RED)
        cv.text(tx, by + 28, h1, 4, INK)
        cv.text(tx, by + 60, h2, 4, INK)
        cv.text(tx, by + 94, sub, 2, GREY)

    # bottom strip
    y = 606 + 3 * bh + 2 * gap + 8
    cv.hline(MX, y, W - 2 * MX, RED, 3)
    strip = ('ALSO: RUSSIAN JETS ENTER KOREA AIR ZONE • EBOLA RESPONDERS TRAPPED '
             'IN CONGO FIGHTING • CHINA PROBES POLITBURO MEMBER • SPAIN AMNESTIES PUIGDEMONT')
    lines = cv.wrap(strip, W - 2 * MX, 2)
    sy = y + 12
    for ln in lines:
        cv.text(MX, sy, ln, 2, INK)
        sy += 18
    return cv


def main():
    outdir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(outdir, exist_ok=True)
    cv = render()
    n = write_png(cv, os.path.join(outdir, 'entry.png'))
    print('wrote entry.png', n, 'bytes')


if __name__ == '__main__':
    main()
