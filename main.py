#!/usr/bin/env python3
"""Sum up 26 November's world news in one image.

Renders a dense 1024x1024 broadsheet PNG from 38 real stories reported on
Thursday 26 November 2026. Deterministic: fixed fonts, fixed geometry, no
clock, no network, no randomness -- two runs write identical bytes.
Writes /output/entry.png (or ./output/entry.png when /output is not
writable, e.g. a local dev run).
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
_BASE = os.path.dirname(os.path.abspath(__file__))
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_LOCAL = os.path.join(_BASE, "fonts", "LiberationSerif-Regular.ttf")
SERIF_B_LOCAL = os.path.join(_BASE, "fonts", "LiberationSerif-Bold.ttf")

INK = (17, 17, 17)
PAPER = (253, 252, 248)
NAVY = (11, 42, 74)
NAVY_LT = (31, 78, 121)
RED = (176, 30, 36)
GREY = (232, 230, 223)
GREY_DK = (120, 118, 110)
BLUE_BG = (214, 231, 240)
LAND = (226, 222, 205)
GOLD = (176, 132, 30)


def font(size, bold=False):
    # Try the vendored fonts first (self-contained), then the system
    # paths, then Pillow's built-in default so a missing font can never
    # crash the render with an uncaught OSError.
    for path in ((SERIF_B_LOCAL if bold else SERIF_LOCAL),
                 (SERIF_B if bold else SERIF)):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w pixels."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, fnt, max_w, fill=INK, leading=None,
               max_lines=None, align="left"):
    """Draw wrapped text; returns the y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.18)
    lines = wrap(draw, text, fnt, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for line in lines:
        if align == "center":
            lx = x + (max_w - draw.textlength(line, font=fnt)) // 2
        else:
            lx = x
        draw.text((lx, y), line, font=fnt, fill=fill)
        y += leading
    return y


def box(draw, x, y, w, h, fill=None, outline=INK, width=1):
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=fill,
                   outline=outline, width=width)


def rule(draw, x, y, w, color=INK, width=1):
    draw.line([(x, y), (x + w, y)], fill=color, width=width)


# ---------------------------------------------------------------- stories
# Every story below was reported in the Thursday 26 November 2026 news
# cycle (Reuters / AP / AFP / wire roundups). Heroes are the day's three
# biggest hard-news items. Regions: EU 5, ME 6, AF 5, AS 8, AM 7, WO 7.

HEROES = [
    ("1", "HOUTHIS CLAIM SAUDI REFINERY ATTACK AS BRENT TOPS $94",
     "Houthis say they hit Ras Tanura and a Riyadh district; oil jumps on "
     "Gulf supply fears.",
     "refinery"),
    ("2", "US 15% TARIFF PLAN SINKS TAIWAN SHARES 1,926.92 POINTS",
     "Taipei closes at 38,195.43 as Washington targets 14 trading partners.",
     "chart"),
    ("3", "PUTIN VOWS REVENGE AS REFINERY STRIKES BITE",
     "Ukraine's strikes cut Russian crude runs 45%; Kyiv says 55% of "
     "refining is offline.",
     "kremlin"),
]

MINIS = [
    ("ASIA", "Pakistan's first astronaut reaches Tiangong",
     "Zeeshan Ali docks on Shenzhou-24, first foreigner on Tiangong.",
     "rocket"),
    ("ASIA", "Australia-Solomons sign security treaty",
     "Canberra is Honiara's lead partner; no foreign military bases.",
     "island"),
    ("ASIA", "Bangladesh offers garment workers 36% rise",
     "Minimum pay 12,500 to 17,500 taka after months of protests.",
     "factory"),
    ("ASIA", "Six dead in Indonesia gold-mine collapse",
     "Three more bodies found in West Java; about 20 still trapped.",
     "mine"),
    ("AFRICA", "Sudan drones kill 19 civilians in Damazin",
     "RSF strikes hit Blue Nile state; at least 20 more wounded.", "drone"),
    ("AFRICA", "Cairo tanker fire kills at least 30",
     "Fuel truck overturns on the ring road; 15 seriously hurt.", "tanker"),
    ("AFRICA", "Court halts Ramaphosa impeachment case",
     "Western Cape court sets aside the Phala Phala report.", "court"),
    ("AMERICAS", "Colombia marks 10 years of peace deal",
     "Police free 20 hostages held 17 hours in a Cartagena shop.", "dove"),
    ("WORLD", "BepiColombo reaches Mercury after 8 years",
     "ESA-JAXA probe slips into orbit; thruster burn ran short.", "mercury"),
    ("WORLD", "EU sends Ukraine EUR 7.9bn, its biggest tranche",
     "Largest single Ukraine Facility payment lands in Kyiv.", "stars"),
]

ALSO = [
    ("EUROPE", "Russia defence budget +27% to 17.1tn roubles"),
    ("EUROPE", "Merz: Russia threatens Europe"),
    ("EUROPE", "UK moves military aircraft over drones"),
    ("EUROPE", "Poland alarms at renewed airspace violations"),
    ("MID EAST", "Three tankers hit by mines in Hormuz"),
    ("MID EAST", "Saudi-led coalition strikes Hodeidah"),
    ("MID EAST", "Israeli strike kills Hamas official, family"),
    ("MID EAST", "Lebanon plans second airport at Kleiat"),
    ("MID EAST", "Israel approves independent Oct 7 probe"),
    ("AFRICA", "Militants kill 30 in Nigeria's Niger State"),
    ("AFRICA", "Egypt's Suez revenues gradually recovering"),
    ("ASIA", "Malaysia to return 6,500 Rohingya in Dec"),
    ("ASIA", "North Korea expels Swiss diplomat"),
    ("ASIA", "Malaysia sues Google for $146m"),
    ("AMERICAS", "US confidence hits near two-year high"),
    ("AMERICAS", "Fed Beige Book: modest growth, wage gains"),
    ("ASIA", "US unveils F-15EX fighters at Kadena"),
    ("AMERICAS", "Petrobras unveils $122bn investment plan"),
    ("AMERICAS", "Venezuela reveals $237.5bn public debt"),
    ("AMERICAS", "Six die in plane crash off Mississippi"),
    ("WORLD", "Duran Duran guitarist Andy Taylor dies, 65"),
    ("WORLD", "FIDE title Game 2 ends in 20-move draw"),
    ("WORLD", "COP31 ends with no fossil-fuel deal"),
    ("WORLD", "India: humans must control lethal AI arms"),
    ("WORLD", "IITs add 6,000 seats in robotics, AI, space"),
]

NUMBERS = [
    ("$94", "Brent crude"),
    ("-1,926.92", "Taiwan points"),
    ("55%", "Russian refining offline"),
    ("30", "killed, Cairo tanker fire"),
    ("19", "killed, Sudan drones"),
    ("36%", "Bangladesh pay rise"),
]

TIMELINE = [
    ("00:45", "Cairo fire kills 30"),
    ("02:30", "Taiwan -1,926.92 pts"),
    ("04:10", "Shenzhou-24 docks"),
    ("06:20", "Sudan drones kill 19"),
    ("08:15", "EU EUR 7.9bn to Kyiv"),
    ("10:40", "Ras Tanura attack"),
    ("13:05", "20 hostages freed"),
    ("17:50", "Putin vows revenge"),
]

# Map pins: (lon, lat, label, dx, dy). dx/dy nudge the numbered dot away
# from its true spot (a leader line joins them) so close pins never overlap.
PINS = [
    (50.1, 26.6, "Ras Tanura", 12, -6), (56.5, 26.5, "Hormuz", -4, 10),
    (34.5, 31.5, "Gaza", -8, -8), (31.2, 30.0, "Cairo", 10, 8),
    (37.6, 55.8, "Moscow", 8, -8), (30.5, 50.5, "Kyiv", -10, 6),
    (121.5, 25.0, "Taipei", 0, 0), (100.3, 40.9, "Jiuquan", 6, -8),
    (160.0, -9.6, "Honiara", 0, 0), (90.4, 23.8, "Dhaka", -6, 8),
    (-75.5, 10.4, "Cartagena", 0, 0), (-89.0, 29.0, "Mississippi", 0, 0),
]

# Coarse continent outlines (lon, lat) for a stylised world map.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 62), (-75, 58), (-65, 60), (-55, 52), (-60, 47), (-70, 44),
     (-75, 35), (-80, 32), (-81, 26), (-90, 21), (-97, 26), (-105, 20),
     (-110, 23), (-117, 33), (-125, 40), (-125, 49), (-135, 58),
     (-155, 58), (-165, 60)],
    # South America
    [(-80, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-68, -50),
     (-65, -55), (-60, -48), (-58, -38), (-52, -33), (-48, -28),
     (-40, -22), (-35, -9), (-35, -6), (-44, -3), (-50, 0), (-55, 6),
     (-62, 9), (-70, 11), (-77, 8)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (3, 53), (8, 57),
     (10, 59), (5, 60), (12, 65), (18, 69), (25, 71), (30, 70), (40, 68),
     (44, 66), (40, 60), (35, 58), (30, 60), (28, 55), (24, 58), (21, 55),
     (19, 54), (23, 54), (28, 45), (23, 40), (19, 42), (15, 44), (12, 44),
     (8, 44), (3, 43), (0, 40), (-2, 37), (-6, 36)],
    # Africa
    [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
     (-8, 5), (-4, 5), (2, 6), (6, 4), (9, 4), (13, -1), (12, -6),
     (13, -12), (12, -18), (15, -23), (16, -29), (19, -34), (26, -34),
     (32, -29), (35, -24), (40, -16), (40, -11), (42, -4), (46, 2),
     (51, 11), (48, 11), (43, 12), (39, 15), (37, 18), (34, 22), (32, 31),
     (30, 32), (22, 33), (11, 34), (10, 37)],
    # Asia
    [(40, 68), (50, 69), (60, 69), (68, 73), (75, 72), (85, 75), (95, 76),
     (105, 77), (115, 73), (125, 73), (135, 72), (145, 72), (155, 70),
     (162, 66), (170, 66), (178, 65), (170, 60), (162, 56), (158, 52),
     (150, 59), (142, 54), (140, 46), (135, 43), (130, 42), (127, 40),
     (122, 38), (120, 32), (122, 28), (118, 25), (110, 20), (108, 18),
     (105, 10), (103, 8), (100, 7), (98, 10), (95, 16), (92, 21), (89, 22),
     (86, 20), (80, 13), (77, 8), (75, 15), (72, 20), (66, 25), (61, 25),
     (57, 26), (52, 28), (50, 30), (48, 30), (44, 29), (40, 32), (36, 36),
     (36, 30), (43, 38), (41, 41), (44, 42), (40, 44), (38, 47), (35, 50),
     (38, 55), (40, 60)],
    # Australia
    [(114, -22), (114, -30), (115, -35), (120, -34), (124, -33), (129, -32),
     (132, -32), (136, -35), (140, -38), (145, -38), (150, -37), (153, -32),
     (153, -27), (150, -23), (146, -19), (142, -15), (142, -11), (137, -12),
     (135, -15), (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
]


# ---------------------------------------------------------------- scenes
# All scenes are small original line drawings built from PIL primitives.

def scene_refinery(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 28, 38))
    ground = y + h - 24
    d.rectangle([x, ground, x + w, y + h], fill=(12, 14, 20))
    # towers (tops stay inside the scene box)
    for i, (tw, th) in enumerate(((26, 46), (34, 54), (22, 40))):
        tx = x + 24 + i * 62
        top = ground - th
        d.rectangle([tx, top, tx + tw, ground], fill=(90, 96, 110))
        d.rectangle([tx + 4, top - 6, tx + tw - 4, top], fill=(90, 96, 110))
    # pipes
    d.line([(x + 60, ground - 28), (x + 150, ground - 28)],
           fill=(140, 146, 160), width=4)
    d.line([(x + 150, ground - 28), (x + 150, ground)], fill=(140, 146, 160),
           width=4)
    # flame
    fx, fy = x + w - 52, y + 10
    d.ellipse([fx - 16, fy, fx + 16, fy + 34], fill=(255, 140, 0))
    d.ellipse([fx - 9, fy + 8, fx + 9, fy + 34], fill=(255, 210, 60))
    d.ellipse([fx - 4, fy + 16, fx + 4, fy + 34], fill=(255, 240, 160))
    # storage tanks
    d.ellipse([x + 18, ground - 22, x + 58, ground], fill=(70, 76, 90))
    d.ellipse([x + w - 96, ground - 20, x + w - 60, ground],
              fill=(70, 76, 90))


def scene_chart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(253, 250, 244))
    d.line([(x + 26, y + 14), (x + 26, y + h - 18)], fill=INK, width=2)
    d.line([(x + 26, y + h - 18), (x + w - 10, y + h - 18)], fill=INK, width=2)
    bars = [48, 44, 38, 42, 32, 27, 21, 15]
    bw = (w - 48) // len(bars)
    for i, v in enumerate(bars):
        bx = x + 32 + i * bw
        d.rectangle([bx, y + h - 18 - v, bx + bw - 6, y + h - 18],
                    fill=RED if i >= 5 else (31, 78, 121))
    d.line([(x + 32, y + 22), (x + w - 18, y + h - 30)], fill=RED, width=4)
    d.ellipse([x + w - 30, y + h - 40, x + w - 14, y + h - 24], fill=RED)
    d.text((x + w - 122, y + 6), "-1,926.92", font=font(20, True), fill=RED)


def scene_kremlin(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 226, 205))
    ground = y + h - 18
    d.rectangle([x, ground, x + w, y + h], fill=(120, 110, 90))
    # wall + towers with onion domes (all tops stay inside the scene box)
    wall_top = ground - 28
    d.rectangle([x + 14, wall_top, x + w - 14, ground], fill=(176, 30, 36))
    for i, (tx, tw, th) in enumerate(((36, 30, 34), (96, 40, 44),
                                      (168, 30, 34))):
        top = ground - th
        d.rectangle([x + tx, top, x + tx + tw, ground], fill=(200, 60, 50))
        d.ellipse([x + tx - 4, top - 14, x + tx + tw + 4, top + 6],
                  fill=(217, 164, 32))
        d.line([(x + tx + tw // 2, top - 20), (x + tx + tw // 2, top - 14)],
               fill=(120, 90, 20), width=2)
    # big "45%" stat, clear of the towers
    d.text((x + w - 104, y + 4), "45%", font=font(30, True), fill=RED)


def scene_rocket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 48))
    for sx, sy in ((x + 20, y + 14), (x + w - 30, y + 26), (x + 40, y + 60),
                   (x + w - 46, y + 66), (x + 70, y + 10)):
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 255, 255))
    cx = x + w // 2
    d.polygon([(cx, y + 12), (cx - 14, y + 40), (cx + 14, y + 40)],
              fill=(176, 30, 36))
    d.rectangle([cx - 14, y + 40, cx + 14, y + h - 34], fill=(240, 240, 235))
    d.ellipse([cx - 6, y + 52, cx + 6, y + 64], fill=(31, 78, 121))
    d.polygon([(cx - 14, y + h - 40), (cx - 26, y + h - 22), (cx - 14, y + h - 22)],
              fill=(176, 30, 36))
    d.polygon([(cx + 14, y + h - 40), (cx + 26, y + h - 22), (cx + 14, y + h - 22)],
              fill=(176, 30, 36))
    d.polygon([(cx - 8, y + h - 22), (cx + 8, y + h - 22), (cx + 3, y + h - 6),
               (cx - 3, y + h - 6)], fill=(255, 160, 0))


def scene_island(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 231, 240))
    d.ellipse([x + 14, y + h - 44, x + w - 14, y + h - 8], fill=(90, 160, 90))
    d.polygon([(x + w // 2 - 34, y + h - 40), (x + w // 2, y + 26),
               (x + w // 2 + 34, y + h - 40)], fill=(70, 140, 70))
    d.ellipse([x + w - 30, y + 8, x + w - 8, y + 30], fill=(255, 220, 90))
    # two small flags on the island
    for i, col in enumerate(((11, 42, 74), (0, 120, 90))):
        fx = x + 34 + i * 58
        d.line([(fx, y + h - 62), (fx, y + h - 40)], fill=INK, width=2)
        d.rectangle([fx, y + h - 62, fx + 26, y + h - 48], fill=col)


def scene_factory(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 234, 222))
    d.rectangle([x + 16, y + h - 52, x + w - 40, y + h - 16], fill=(120, 118, 110))
    d.rectangle([x + w - 36, y + 18, x + w - 22, y + h - 16], fill=(90, 88, 82))
    d.ellipse([x + w - 40, y + 8, x + w - 18, y + 24], fill=(200, 200, 196))
    for i in range(3):
        wx = x + 30 + i * 34
        d.rectangle([wx, y + h - 44, wx + 20, y + h - 28], fill=(255, 220, 90))
    d.text((x + 14, y + 8), "36%", font=font(24, True), fill=RED)


def scene_mine(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 214, 190))
    d.polygon([(x + 8, y + h - 12), (x + w // 2, y + 16), (x + w - 8, y + h - 12)],
              fill=(110, 96, 74))
    d.rectangle([x + w // 2 - 14, y + h - 46, x + w // 2 + 14, y + h - 12],
                fill=(40, 32, 24))
    # helmet
    hx, hy = x + w - 52, y + h - 44
    d.pieslice([hx - 18, hy - 14, hx + 18, hy + 14], 180, 360, fill=(255, 200, 0))
    d.rectangle([hx - 20, hy - 2, hx + 20, hy + 2], fill=(220, 160, 0))
    d.ellipse([hx - 3, hy - 8, hx + 3, hy - 2], fill=(255, 255, 255))


def scene_drone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 214))
    cx, cy = x + w // 2, y + h // 2
    d.rectangle([cx - 26, cy - 8, cx + 26, cy + 8], fill=(60, 60, 64))
    for sx, sy in ((-34, -20), (34, -20), (-34, 20), (34, 20)):
        d.line([(cx, cy), (cx + sx, cy + sy)], fill=(60, 60, 64), width=3)
        d.ellipse([cx + sx - 12, cy + sy - 4, cx + sx + 12, cy + sy + 4],
                  fill=(140, 140, 146))
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(176, 30, 36))


def scene_tanker(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 30, 34))
    d.ellipse([x + 16, y + h - 46, x + w - 16, y + h - 12], fill=(70, 70, 76))
    d.rectangle([x + 22, y + h - 58, x + w - 50, y + h - 34], fill=(190, 60, 40))
    d.rectangle([x + w - 48, y + h - 62, x + w - 20, y + h - 34], fill=(220, 220, 215))
    d.rectangle([x + w - 44, y + h - 58, x + w - 28, y + h - 46], fill=(31, 78, 121))
    for wx in (x + 40, x + 78, x + w - 38):
        d.ellipse([wx - 9, y + h - 22, wx + 9, y + h - 4], fill=(10, 10, 12))
    fx, fy = x + w // 2, y + 6
    d.ellipse([fx - 18, fy, fx + 18, fy + 26], fill=(255, 140, 0))
    d.ellipse([fx - 9, fy + 8, fx + 9, fy + 26], fill=(255, 210, 60))


def scene_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 234, 222))
    # columns
    for i in range(3):
        cx = x + 26 + i * 52
        d.rectangle([cx, y + 18, cx + 14, y + h - 30], fill=(120, 110, 90))
        d.rectangle([cx - 4, y + 14, cx + 18, y + 20], fill=(90, 82, 66))
        d.rectangle([cx - 4, y + h - 34, cx + 18, y + h - 28], fill=(90, 82, 66))
    d.polygon([(x + 8, y + 14), (x + w - 8, y + 14), (x + w // 2, y + 2)],
              fill=(176, 30, 36))
    d.rectangle([x + 10, y + h - 28, x + w - 10, y + h - 16], fill=(90, 82, 66))


def scene_dove(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 231, 240))
    d.ellipse([x + 16, y + 10, x + w - 16, y + h - 10], fill=(255, 255, 255),
              outline=(31, 78, 121), width=2)
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 30, cy - 8, cx + 30, cy + 10], fill=(255, 255, 255))
    d.ellipse([cx + 18, cy - 20, cx + 40, cy - 2], fill=(255, 255, 255))
    d.polygon([(cx + 36, cy - 16), (cx + 44, cy - 12), (cx + 36, cy - 10)],
              fill=(255, 180, 0))
    d.ellipse([cx + 30, cy - 16, cx + 34, cy - 12], fill=INK)
    d.polygon([(cx - 6, cy - 6), (cx + 6, cy - 26), (cx + 18, cy - 6)],
              fill=(230, 230, 225))
    d.polygon([(cx - 30, cy + 4), (cx - 44, cy + 14), (cx - 28, cy + 12)],
              fill=(230, 230, 225))
    # olive branch
    d.line([(x + w - 46, y + h - 18), (x + w - 18, y + h - 30)],
           fill=(70, 140, 70), width=2)
    for i in range(3):
        lx = x + w - 42 + i * 10
        d.ellipse([lx - 3, y + h - 26 - i * 3, lx + 3, y + h - 20 - i * 3],
                  fill=(70, 140, 70))


def scene_mercury(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 20, 36))
    for sx, sy in ((x + 16, y + 12), (x + w - 24, y + 18), (x + 30, y + 66),
                   (x + w - 40, y + 70), (x + w // 2, y + 8)):
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 255, 255))
    cx, cy, r = x + w // 2 - 8, y + h // 2 + 4, 30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(170, 164, 152))
    for ox, oy, orr in ((-14, -10, 6), (8, 4, 8), (-2, 14, 5), (14, -14, 4)):
        d.ellipse([cx + ox - orr, cy + oy - orr, cx + ox + orr, cy + oy + orr],
                  fill=(140, 134, 122))
    # probe
    px, py = x + w - 34, y + 12
    d.rectangle([px, py, px + 14, py + 10], fill=(220, 220, 210))
    d.rectangle([px - 12, py + 2, px, py + 8], fill=(31, 78, 121))
    d.rectangle([px + 14, py + 2, px + 26, py + 8], fill=(31, 78, 121))


def scene_stars(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(11, 42, 74))
    cx, cy, r = x + w // 2, y + h // 2 - 8, 26
    import math
    for i in range(12):
        a = math.pi * 2 * i / 12 - math.pi / 2
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 220, 90))
    label = "EUR 7.9bn"
    tw = d.textlength(label, font=font(14, True))
    d.text((cx - tw // 2, y + h - 18), label, font=font(14, True),
           fill=(255, 255, 255))


SCENES = {
    "refinery": scene_refinery, "chart": scene_chart, "kremlin": scene_kremlin,
    "rocket": scene_rocket, "island": scene_island, "factory": scene_factory,
    "mine": scene_mine, "drone": scene_drone, "tanker": scene_tanker,
    "court": scene_court, "dove": scene_dove, "mercury": scene_mercury,
    "stars": scene_stars,
}


# ---------------------------------------------------------------- render

def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 14  # side margin

    # ---- masthead (0-72)
    d.rectangle([0, 0, W, 72], fill=NAVY)
    d.text((M, 8), "THE WORLD IN ONE DAY", font=font(40, True),
           fill=(255, 255, 255))
    d.text((W - M - 268, 14), "THURSDAY 26 NOVEMBER 2026",
           font=font(17, True), fill=(255, 220, 90))
    d.text((W - M - 268, 38), "38 STORIES  ·  6 REGIONS  ·  1 DAY",
           font=font(13), fill=(200, 215, 230))
    d.rectangle([0, 72, W, 74], fill=RED)

    # ---- date check strip (74-94)
    d.rectangle([0, 74, W, 94], fill=(255, 240, 180))
    d.text((M, 77), "DATE CHECK:", font=font(14, True), fill=RED)
    d.text((M + 104, 77),
           "Every story below is dated Thursday 26 November 2026. "
           "Sources: Reuters / AP / AFP wire roundups.",
           font=font(14), fill=INK)

    # ---- heroes (96-272): 3 boxes
    hy, hh = 96, 176
    hw = (W - 2 * M - 2 * 8) // 3
    for i, (num, head, sub, kind) in enumerate(HEROES):
        x = M + i * (hw + 8)
        box(d, x, hy, hw, hh, fill=(255, 255, 255), outline=INK, width=1)
        d.rectangle([x, hy, x + hw - 1, hy + 3], fill=RED)
        SCENES[kind](d, x + 1, hy + 4, hw - 2, 84)
        d.text((x + 8, hy + 92), num + ".", font=font(15, True), fill=RED)
        text_block(d, x + 26, hy + 92, head, font(17, True), hw - 34,
                   leading=19, max_lines=2)
        text_block(d, x + 8, hy + 134, sub, font(13), hw - 16,
                   leading=15, max_lines=2)

    # ---- IN NUMBERS (272-318): six hard counts, no header row
    ny = 272
    nw = (W - 2 * M) // len(NUMBERS)
    for i, (big, label) in enumerate(NUMBERS):
        x = M + i * nw
        text_block(d, x, ny + 6, big, font(21, True), nw - 6,
                   leading=22, max_lines=1, align="center")
        text_block(d, x, ny + 30, label, font(10), nw - 6,
                   leading=11, max_lines=1, align="center")
    rule(d, M, ny + 44, W - 2 * M, color=INK, width=1)

    # ---- UTC timeline (318-366)
    ty = 318
    d.text((M, ty + 4), "THE DAY IN UTC", font=font(14, True), fill=RED)
    rule(d, M + 122, ty + 12, W - 2 * M - 122, color=GREY_DK)
    d.line([(M + 6, ty + 30), (W - M - 6, ty + 30)], fill=NAVY_LT, width=2)
    tw = (W - 2 * M) // len(TIMELINE)
    for i, (t, label) in enumerate(TIMELINE):
        cx = M + i * tw + tw // 2
        d.ellipse([cx - 4, ty + 26, cx + 4, ty + 34], fill=RED)
        text_block(d, cx - tw // 2, ty + 16, t, font(12, True), tw,
                   leading=12, max_lines=1, align="center")
        text_block(d, cx - tw // 2 + 2, ty + 36, label, font(11), tw - 4,
                   leading=12, max_lines=1, align="center")

    # ---- world map (366-462)
    my = 366
    d.text((M, my + 2), "WHERE IT HAPPENED", font=font(14, True), fill=RED)
    rule(d, M + 168, my + 10, W - 2 * M - 168, color=GREY_DK)
    map_x, map_y, map_w, map_h = M, my + 18, W - 2 * M, 72
    d.rectangle([map_x, map_y, map_x + map_w, map_y + map_h], fill=BLUE_BG)
    lon2x = lambda lon: map_x + (lon + 180.0) / 360.0 * map_w
    lat2y = lambda lat: map_y + (90.0 - lat) / 180.0 * map_h
    for poly in CONTINENTS:
        pts = [(lon2x(lon), lat2y(lat)) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=(150, 146, 132))
    for i, (lon, lat, label, dx, dy) in enumerate(PINS, 1):
        px, py = lon2x(lon), lat2y(lat)
        qx, qy = px + dx, py + dy
        if dx or dy:
            d.line([(px, py), (qx, qy)], fill=RED, width=1)
        d.ellipse([qx - 6, qy - 6, qx + 6, qy + 6], fill=RED,
                  outline=(255, 255, 255), width=1)
        num = str(i)
        nw = d.textlength(num, font=font(8, True))
        d.text((qx - nw / 2, qy - 5), num, font=font(8, True),
               fill=(255, 255, 255))
    legend = "  ·  ".join("%d %s" % (i, lab) for i, (_, _, lab, _, _) in
                          enumerate(PINS, 1))
    d.text((M, my + 86), legend, font=font(11), fill=INK)

    # ---- minis (462-800): header + 2 rows x 5
    myy = 462
    d.text((M, myy + 2), "MORE OF THE DAY", font=font(14, True), fill=RED)
    rule(d, M + 142, myy + 10, W - 2 * M - 142, color=GREY_DK)
    mw = (W - 2 * M - 4 * 8) // 5
    mh = 156
    for r in range(2):
        for c in range(5):
            idx = r * 5 + c
            region, head, sub, kind = MINIS[idx]
            x = M + c * (mw + 8)
            y = myy + 18 + r * (mh + 8)
            box(d, x, y, mw, mh, fill=(255, 255, 255), outline=INK, width=1)
            SCENES[kind](d, x + 1, y + 1, mw - 2, 84)
            d.text((x + 6, y + 88), region, font=font(10, True), fill=RED)
            text_block(d, x + 6, y + 100, head, font(13, True), mw - 12,
                       leading=14, max_lines=2)
            text_block(d, x + 6, y + 130, sub, font(11), mw - 12,
                       leading=12, max_lines=2)

    # ---- ALSO TODAY (800-968): 5 columns x 5 rows
    ay = 800
    d.text((M, ay + 2), "ALSO TODAY — 25 MORE STORIES, ALL 26 NOVEMBER",
           font=font(14, True), fill=RED)
    rule(d, M + 386, ay + 10, W - 2 * M - 386, color=GREY_DK)
    aw = (W - 2 * M - 4 * 8) // 5
    for r in range(5):
        for c in range(5):
            idx = r * 5 + c
            region, head = ALSO[idx]
            x = M + c * (aw + 8)
            y = ay + 20 + r * 30
            d.text((x, y), region, font=font(10, True), fill=NAVY_LT)
            lines = wrap(d, head, font(11), aw - 52)
            d.text((x + 52, y - 1), lines[0] if lines else "",
                   font=font(11), fill=INK)
            if len(lines) > 1:
                d.text((x + 52, y + 11), lines[1], font=font(11), fill=INK)

    # ---- footer (968-1024)
    fy = 968
    rule(d, M, fy, W - 2 * M, color=INK, width=2)
    d.text((M, fy + 5),
           "Original drawings, no photos  ·  All 38 stories Thursday 26 November 2026",
           font=font(13), fill=INK)
    d.text((M, fy + 19), "THE WORLD IN ONE DAY — a one-page newspaper",
           font=font(11), fill=GREY_DK)
    d.text((M, fy + 33),
           "Drawn by an AI agent for make.fun — news-image-20261126",
           font=font(11), fill=GREY_DK)
    return img


def main():
    img = render()
    try:
        os.makedirs("/output", exist_ok=True)
        out = "/output/entry.png"
        img.save(out, format="PNG")
    except OSError:
        os.makedirs("output", exist_ok=True)
        out = "output/entry.png"
        img.save(out, format="PNG")
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
