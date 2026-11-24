#!/usr/bin/env python3
"""THE GILDED PAGE - NI24 (news-image-20261124) entry renderer, Final 7.
Built fresh in this recorded session. Local-only build script (PIL); the
submitted carrier main.py is stdlib-only and only copies entry.png.
Layout C: 3 leads + vertical THE DAY IN NUMBERS rail + 12 minis + dotted
map + ALSO ON in 3 columns + UTC timeline + DATE CHECK + footer.
Palette: gold / black on ivory. 1024x1024, target 190-450 KB.
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
VARIANT = os.environ.get("GILDED_VARIANT", "A")  # A or B duel variant

W = H = 1024
IVORY = (247, 241, 227)
PAPER = (250, 246, 235)
INK = (20, 18, 16)
GOLD = (176, 138, 46)
GOLD_D = (140, 106, 31)
GOLD_L = (214, 178, 94)
BLACK = (16, 14, 12)
NAVY = (20, 33, 61)
RED = (163, 30, 34)
CREAM = (245, 238, 222)
GREY = (92, 86, 76)
RULE = (176, 138, 46)

FDIR = os.path.join(BASE, "fonts")


def F(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


def pf(size):
    return F("PlayfairDisplay-Black.ttf", size)


def ab(size):
    return F("Archivo-Bold.ttf", size)


def ar(size):
    return F("Archivo.ttf", size)


def db(size):
    return F("DejaVuSans-Bold.ttf", size)


def dr(size):
    return F("DejaVuSans.ttf", size)


def tw(draw, text, font, maxw):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, font, maxw, maxlines):
    """Wrap and hard-truncate with ellipsis to maxlines."""
    lines = tw(draw, text, font, maxw)
    if len(lines) > maxlines:
        lines = lines[:maxlines]
        while lines and draw.textlength(lines[-1] + "\u2026", font=font) > maxw:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1] + "\u2026"
    return lines


def para(draw, x, y, lines, font, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def chip(draw, x, y, text, font, fg, bg, pad=4):
    w = draw.textlength(text, font=font) + pad * 2
    h = font.size + pad
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=bg)
    draw.text((x + pad, y + pad // 2 - 1), text, font=font, fill=fg)
    return w


# ---------------------------------------------------------------- cards
# num, region, place, headline, deck, chiptxt, source, tag, scene
LEADS = [
    dict(num=1, region="WORLD", place="GLOBAL \u00b7 TECH",
         head="Solana launches solana.ai",
         deck="A platform for autonomous AI agents to transact, manage wallets "
              "and buy services on their own.",
         chip="SOLANA.AI LIVE", src="Gadgets360 \u00b7 23 Nov", tag="REPORTED",
         scene="solana"),
    dict(num=2, region="WORLD", place="GLOBAL \u00b7 CRYPTO",
         head="Bitcoin steadies near $61,284",
         deck="$61,284 at 12:52 UTC Mon, +1.1% in 24 h after a weekend low near "
              "$55,100; a Kraken flash crash to ~$17,000 stands.",
         chip="BITCOIN 61284", src="CoinPaprika \u00b7 23 Nov", tag="REPORTED",
         scene="bitcoin"),
    dict(num=3, region="ASIA-PACIFIC", place="HONG KONG \u00b7 SECURITY",
         head="Hong Kong curbs drones and roads for Interpol summit",
         deck="Airspace curbs 30 Nov\u20133 Dec around the Convention and "
              "Exhibition Centre, with harbour and Wan Chai road closures.",
         chip="30 NOV\u20133 DEC", src="HK News TV \u00b7 23 Nov", tag="REPORTED",
         scene="hongkong"),
]

MINIS = [
    dict(num=4, region="AFRICA", place="BENGHAZI, LIBYA \u00b7 WAR",
         head="Ukraine sinks Russian warship Merkury off Libya",
         deck="7 sea drones launched; Merkury sunk at Benghazi, Ka-27 "
              "destroyed, MV Angara hit.",
         chip="7 SEA DRONES", src="CNN / Times / WSJ / AP", tag="REPORTED",
         scene="merkury"),
    dict(num=5, region="EUROPE", place="GULF OF FINLAND \u00b7 SEA",
         head="Russian cargo ship Sparta II hit, towed clear",
         deck="Hit by 2 drones; Finland led the rescue, all 16 crew off, "
              "towed out Sunday night.",
         chip="16 CREW SAFE", src="Reuters / Times / WSJ", tag="REPORTED",
         scene="sparta"),
    dict(num=6, region="EUROPE", place="KYIV REGION, UKRAINE \u00b7 WAR",
         head="Kyiv strikes kill at least 15 near the capital",
         deck="11 killed in a block of flats in Dymer; a drone hit a 6-floor "
              "building in Kyiv, 5 injured.",
         chip="15 KILLED", src="Times / AP \u00b7 23 Nov", tag="REPORTED",
         scene="kyiv"),
    dict(num=7, region="WORLD", place="ANTALYA, T\u00dcRKIYE \u00b7 CLIMATE",
         head="COP31 ends with no deal \u2014 first since 2000",
         deck="The Antalya Pact was not adopted; the final text dropped every "
              "mention of fossil fuels.",
         chip="NO DEAL", src="Times / Guardian \u00b7 23 Nov", tag="REPORTED",
         scene="cop31"),
    dict(num=8, region="MIDDLE EAST", place="WASHINGTON \u00b7 SANCTIONS",
         head="Iran sanctions hit ~30 exchange houses",
         deck="Treasury Mon: ~30 Iran-linked exchange houses and executives, "
              "the core of shadow banking.",
         chip="~30 SANCTIONED", src="AP / Treasury \u00b7 23 Nov", tag="REPORTED",
         scene="iran"),
    dict(num=9, region="MIDDLE EAST", place="GAZA CITY \u00b7 CONFLICT",
         head="Israeli strikes kill 3 in Gaza",
         deck="3 killed Mon in separate strikes, including a UNRWA employee; "
              "Shifa Hospital confirms.",
         chip="3 KILLED", src="AP \u00b7 23 Nov", tag="REPORTED",
         scene="gaza"),
    dict(num=10, region="MIDDLE EAST", place="WESTERN YEMEN \u00b7 WAR",
         head="Strike kills 11 in western Yemen",
         deck="Houthis say a Saudi-backed forces\u2019 strike Mon killed 11 and "
              "wounded 19.",
         chip="11 KILLED", src="AP \u00b7 23 Nov", tag="REPORTED",
         scene="yemen"),
    dict(num=11, region="AMERICAS", place="GLOBAL \u00b7 MARKETS",
         head="Gold rebounds 1.5% to $3,588",
         deck="Bullion +1.5% Mon after its worst week in 8 months; traders "
              "await PCE due 25 Nov.",
         chip="GOLD 3588", src="Reuters \u00b7 23 Nov", tag="REPORTED",
         scene="gold"),
    dict(num=12, region="AMERICAS", place="LOS ANGELES \u00b7 BUSINESS",
         head="GTA VI takes $3.8bn on day one",
         deck="The biggest entertainment launch on record \u2014 past every game "
              "launch and film box office.",
         chip="$3.8BN DAY ONE", src="ActiveInvestorMag", tag="REPORTED",
         scene="gta"),
    dict(num=13, region="OCEANIA", place="WELLINGTON \u00b7 CRICKET",
         head="New Zealand bat out draw with India",
         deck="NZ 239/5 \u2014 Mitchell 49* off 186 balls, Phillips 26* off 126; "
              "India 720/9d. 2nd Test 27 Nov.",
         chip="DRAW 239/5", src="HS / WicketPulse", tag="REPORTED",
         scene="cricket"),
    dict(num=14, region="EUROPE", place="LIVERPOOL \u00b7 FOOTBALL",
         head="Liverpool 4\u20130 Man Utd; Pochettino debut disaster",
         deck="Yoro sent off in the 8th min, United down to 10; the loss leaves "
              "United 19th, on 8 points.",
         chip="4\u20130", src="Mint / NextSportsWeb", tag="REPORTED",
         scene="football"),
    dict(num=15, region="AMERICAS", place="NEW YORK \u00b7 MARKETS",
         head="Nvidia brings back Jensen Huang as CEO",
         deck="Board reinstates Huang effective immediately Mon; shares +31%, "
              "Nasdaq +6%, S&P 500 +5%.",
         chip="+31% HUANG BACK", src="Reuters \u00b7 23 Nov", tag="REPORTED",
         scene="nvidia"),
]

# ALSO ON briefs, numbered 16-39 (one dense line each: name + number + source)
BRIEFS = [
    "Democrats 258\u2013173 take both chambers (BBC)",
    "Van Hollen vs Schumer, Senate ballot 1 Dec (AIM)",
    "Trump: cap card rates, scrap debt ceiling (AIM)",
    "FBI probe into crime-database hack (AP)",
    "UN AI weapons talks continue (salonvision)",
    "Miley Cyrus marries Maxx Morando (BBC)",
    "N. Korea weighs shutting Swiss office (KCNA)",
    "US mulls training Syrian forces (Reuters)",
    "Congo halts cobalt exports from 30 Nov (Reuters)",
    "Indonesia factory blaze kills 24 (Reuters)",
    "CrowdStrike buys Zscaler in $44bn deal (Reuters)",
    "Trump hosts meme-coin gala as token plunges (Reuters)",
    "US Army to detonate Iowa lead stockpile (Reuters)",
    "India weighs rice export duties (Reuters)",
    "Euro zone PMI 51.7, fifth month of growth (Reuters)",
    "Nepal PM ends Delhi visit, met Modi Mon (IANS)",
    "Thousands march in Lisbon on living costs (JagranJosh)",
    "UK\u2013EU Brexit reset deal hailed \u2018landmark\u2019 (BBC)",
    "India\u2013EU trade pact likely signed 16 Dec (JagranJosh)",
    "Tata Steel sells pipe unit, Rs 28,000 cr (ObserverVoice)",
    "SpiceJet pilot seeks urgent safety audit (ObserverVoice)",
    "Google invests $5m in AI at IIT Kharagpur (JagranJosh)",
    "KOSPI falls ~3% to 10-month low (Reuters)",
    "Mets, A.J. Ewing agree $95m, 8-year deal (AP)",
]

NUMBERS = [  # (big, label) - every one binds a card or a brief
    ("7", "SEA DRONES \u00b7 MERKURY SUNK"),
    ("$3,588", "GOLD, +1.5% MON"),
    ("$61,284", "BITCOIN, 12:52 UTC"),
    ("$3.8BN", "GTA VI DAY ONE"),
    ("NO DEAL", "COP31 \u00b7 FIRST SINCE 2000"),
    ("258\u2013173", "HOUSE \u00b7 DEMOCRATS"),
    ("4\u20130", "LIVERPOOL BEAT UTD"),
]

REGIONS = [("EUROPE", 3), ("MIDDLE EAST", 3), ("AMERICAS", 3),
           ("ASIA-PACIFIC", 1), ("OCEANIA", 1), ("AFRICA", 1), ("WORLD", 3)]

TIMELINE = [
    ("12:52 UTC MON", "Bitcoin $61,284 \u2014 CoinPaprika"),
    ("21:24 UTC MON", "KCNA: N. Korea weighs shutting Swiss office (04:24 WIB Tue)"),
    ("21:39 HKT MON", "Hong Kong announces Interpol-summit curbs, 30 Nov\u20133 Dec"),
    ("MON EVENING", "Zelenskyy: Merkury sunk \u00b7 Treasury: ~30 Iran houses sanctioned"),
    ("SUN NIGHT", "Sparta II towed clear \u00b7 COP31 closes with no deal"),
]

DATECHECK = [
    ("186-drone night over Ukraine, 161 downed", "Fri 21\u2013Sun 22 Nov"),
    ("Alcaraz beats Zverev, first ATP Finals title", "Sun 22 Nov"),
    ("Verstappen wins Las Vegas Grand Prix", "Sun 22 Nov"),
    ("Wembanyama scores 50, Spurs 114\u201391 Pelicans", "Sun 22 Nov"),
    ("Nvidia CEO Jensen Huang resigns after affair", "Thu 12 Nov"),
    ("Hong Kong Election Committee results, 723 seats", "Sun 22 Nov"),
]

TOTAL_STORIES = len(LEADS) + len(MINIS) + len(BRIEFS)  # 15 + 24 = 39

# ---------------------------------------------------------------- scenes
# Flat, layered, full-bleed scene strips. Each draws into (x, y, w, h).

def _sky(d, x, y, w, h, top, bot):
    for i in range(h):
        t = i / max(1, h - 1)
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        d.line([(x, y + i), (x + w, y + i)], fill=c)


def _waves(d, x, y, w, h, col, n=3):
    for k in range(n):
        yy = y + h * (0.25 + 0.55 * k / max(1, n - 1))
        pts = [(x + i * w / 12, yy + (6 if i % 2 else -4) * (1 + k * 0.3))
               for i in range(13)]
        d.line(pts, fill=col, width=2)


def _sun(d, x, y, r, col):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)


def scene_solana(d, x, y, w, h):
    _sky(d, x, y, w, h, (24, 28, 52), (58, 44, 96))
    nodes = [(0.18, 0.30), (0.42, 0.18), (0.68, 0.32), (0.85, 0.16),
             (0.30, 0.62), (0.58, 0.70), (0.82, 0.62), (0.12, 0.78)]
    pts = [(x + a * w, y + b * h) for a, b in nodes]
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if abs(pts[i][0] - pts[j][0]) < w * 0.45 and abs(pts[i][1] - pts[j][1]) < h * 0.5:
                d.line([pts[i], pts[j]], fill=(176, 138, 46), width=1)
    for px, py in pts:
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(214, 178, 94),
                  outline=(247, 241, 227), width=1)
    d.ellipse([x + w * 0.44, y + h * 0.30, x + w * 0.56, y + h * 0.62],
              outline=(214, 178, 94), width=3)
    if h >= 50:
        d.text((x + w * 0.475, y + h * 0.40), "AI", font=ab(13), fill=(247, 241, 227))


def scene_bitcoin(d, x, y, w, h):
    _sky(d, x, y, w, h, (28, 30, 46), (96, 74, 28))
    d.ellipse([x + w * 0.06, y + h * 0.08, x + w * 0.34, y + h * 0.92],
              fill=(214, 178, 94), outline=(140, 106, 31), width=2)
    if h >= 50:
        d.text((x + w * 0.155, y + h * 0.28), "\u20bf", font=db(30), fill=(20, 18, 16))
    pts = [(x + w * 0.38, y + h * 0.78), (x + w * 0.52, y + h * 0.62),
           (x + w * 0.64, y + h * 0.68), (x + w * 0.78, y + h * 0.42),
           (x + w * 0.94, y + h * 0.22)]
    d.line(pts, fill=(247, 241, 227), width=3)
    d.polygon([pts[-1], (x + w * 0.94, y + h * 0.30), (x + w * 0.87, y + h * 0.24)],
              fill=(247, 241, 227))


def scene_hongkong(d, x, y, w, h):
    _sky(d, x, y, w, h, (38, 52, 84), (176, 138, 46))
    _sun(d, x + w * 0.82, y + h * 0.26, 13, (247, 241, 227))
    tops = [0.42, 0.30, 0.52, 0.24, 0.44, 0.36, 0.56]
    bw = w / len(tops)
    for i, t in enumerate(tops):
        bx = x + i * bw
        d.rectangle([bx + 1, y + h * t, bx + bw - 1, y + h * 0.92], fill=(20, 18, 16))
        for wy in (0.55, 0.68, 0.80):
            d.rectangle([bx + 4, y + h * wy, bx + bw - 4, y + h * wy + 2],
                        fill=(214, 178, 94))
    d.rectangle([x, y + h * 0.92, x + w, y + h], fill=(20, 33, 61))
    d.ellipse([x + w * 0.10, y + h * 0.10, x + w * 0.20, y + h * 0.20],
              outline=(247, 241, 227), width=2)
    d.line([(x + w * 0.10, y + h * 0.15), (x + w * 0.20, y + h * 0.15)],
           fill=(247, 241, 227), width=2)


def scene_merkury(d, x, y, w, h):
    _sky(d, x, y, w, h, (46, 58, 78), (120, 96, 52))
    d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(20, 33, 61))
    _waves(d, x, y + h * 0.55, w, h * 0.45, (214, 178, 94), 3)
    # sinking corvette, bow up, stern under
    d.polygon([(x + w * 0.14, y + h * 0.62), (x + w * 0.52, y + h * 0.30),
               (x + w * 0.58, y + h * 0.42), (x + w * 0.30, y + h * 0.72)],
              fill=(20, 18, 16))
    d.rectangle([x + w * 0.44, y + h * 0.22, x + w * 0.48, y + h * 0.34],
                fill=(20, 18, 16))
    d.ellipse([x + w * 0.60, y + h * 0.62, x + w * 0.66, y + h * 0.74],
              fill=(163, 30, 34))
    d.ellipse([x + w * 0.68, y + h * 0.70, x + w * 0.72, y + h * 0.78],
              fill=(247, 241, 227))
    for i in range(7):  # seven sea drones as dots above the sea
        dx = x + w * (0.62 + 0.05 * i)
        dy = y + h * (0.12 + (0.10 if i % 2 else 0.02))
        d.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=(247, 241, 227),
                  outline=(176, 138, 46), width=1)


def scene_sparta(d, x, y, w, h):
    _sky(d, x, y, w, h, (52, 62, 80), (150, 128, 74))
    d.rectangle([x, y + h * 0.58, x + w, y + h], fill=(24, 44, 74))
    _waves(d, x, y + h * 0.58, w, h * 0.42, (214, 178, 94), 3)
    d.rectangle([x + w * 0.10, y + h * 0.34, x + w * 0.52, y + h * 0.60],
                fill=(20, 18, 16))
    d.rectangle([x + w * 0.16, y + h * 0.20, x + w * 0.30, y + h * 0.34],
                fill=(20, 18, 16))
    d.rectangle([x + w * 0.52, y + h * 0.44, x + w * 0.56, y + h * 0.60],
                fill=(20, 18, 16))
    d.ellipse([x + w * 0.58, y + h * 0.38, x + w * 0.64, y + h * 0.50],
              fill=(163, 30, 34))  # fire
    d.ellipse([x + w * 0.60, y + h * 0.30, x + w * 0.68, y + h * 0.42],
              fill=(214, 138, 40))
    d.line([(x + w * 0.56, y + h * 0.52), (x + w * 0.86, y + h * 0.40)],
           fill=(247, 241, 227), width=2)  # tow line
    d.rectangle([x + w * 0.84, y + h * 0.36, x + w * 0.94, y + h * 0.48],
                fill=(247, 241, 227))


def scene_kyiv(d, x, y, w, h):
    _sky(d, x, y, w, h, (60, 56, 66), (140, 96, 52))
    tops = [0.34, 0.48, 0.26, 0.44, 0.58]
    bw = w / len(tops)
    for i, t in enumerate(tops):
        bx = x + i * bw
        d.rectangle([bx + 1, y + h * t, bx + bw - 1, y + h], fill=(20, 18, 16))
    d.polygon([(x + w * 0.55, y + h * 0.26), (x + w * 0.62, y + h * 0.44),
               (x + w * 0.72, y + h * 0.40), (x + w * 0.66, y + h * 0.18)],
              fill=(120, 116, 108))  # smoke
    d.ellipse([x + w * 0.66, y + h * 0.10, x + w * 0.72, y + h * 0.20],
              fill=(163, 30, 34))
    for wx in (0.10, 0.30, 0.50, 0.72, 0.90):
        d.rectangle([x + w * wx, y + h * 0.62, x + w * wx + 5, y + h * 0.66],
                    fill=(214, 178, 94))


def scene_cop31(d, x, y, w, h):
    _sky(d, x, y, w, h, (30, 52, 72), (96, 116, 96))
    d.ellipse([x + w * 0.32, y + h * 0.10, x + w * 0.68, y + h * 0.90],
              fill=(32, 86, 66), outline=(214, 178, 94), width=2)
    d.ellipse([x + w * 0.36, y + h * 0.22, x + w * 0.48, y + h * 0.38],
              fill=(96, 140, 96))
    d.ellipse([x + w * 0.55, y + h * 0.55, x + w * 0.64, y + h * 0.72],
              fill=(96, 140, 96))
    d.rectangle([x + w * 0.06, y + h * 0.62, x + w * 0.94, y + h * 0.86],
                fill=(163, 30, 34))
    if h >= 50:
        d.text((x + w * 0.20, y + h * 0.66), "NO DEAL", font=ab(15),
               fill=(247, 241, 227))


def scene_iran(d, x, y, w, h):
    _sky(d, x, y, w, h, (44, 44, 58), (120, 104, 60))
    d.rectangle([x + w * 0.12, y + h * 0.30, x + w * 0.88, y + h * 0.92],
                fill=(20, 18, 16))
    d.polygon([(x + w * 0.08, y + h * 0.30), (x + w * 0.50, y + h * 0.08),
               (x + w * 0.92, y + h * 0.30)], fill=(140, 106, 31))
    for i in range(4):
        cx = x + w * (0.20 + 0.20 * i)
        d.rectangle([cx, y + h * 0.42, cx + 8, y + h * 0.92], fill=(214, 178, 94))
    d.rectangle([x + w * 0.55, y + h * 0.55, x + w * 0.95, y + h * 0.85],
                outline=(163, 30, 34), width=3)
    if h >= 50:
        d.text((x + w * 0.60, y + h * 0.63), "FROZEN", font=ab(12), fill=(163, 30, 34))


def scene_gaza(d, x, y, w, h):
    _sky(d, x, y, w, h, (72, 62, 56), (150, 110, 60))
    tops = [0.40, 0.30, 0.50, 0.36]
    bw = w / len(tops)
    for i, t in enumerate(tops):
        bx = x + i * bw
        d.rectangle([bx + 1, y + h * t, bx + bw - 1, y + h], fill=(24, 22, 20))
    d.ellipse([x + w * 0.78, y + h * 0.10, x + w * 0.92, y + h * 0.34],
              outline=(247, 241, 227), width=2)
    d.ellipse([x + w * 0.82, y + h * 0.14, x + w * 0.92, y + h * 0.30],
              fill=(247, 241, 227))
    d.rectangle([x + w * 0.08, y + h * 0.72, x + w * 0.30, y + h * 0.88],
                fill=(163, 30, 34))
    if h >= 50:
        d.text((x + w * 0.11, y + h * 0.74), "UNRWA", font=ab(11),
               fill=(247, 241, 227))


def scene_yemen(d, x, y, w, h):
    _sky(d, x, y, w, h, (66, 58, 48), (140, 100, 56))
    d.polygon([(x, y + h), (x + w * 0.28, y + h * 0.22), (x + w * 0.55, y + h),
               (x + w * 0.72, y + h * 0.40), (x + w, y + h)], fill=(32, 28, 24))
    d.polygon([(x + w * 0.28, y + h * 0.22), (x + w * 0.34, y + h * 0.34),
               (x + w * 0.24, y + h * 0.34)], fill=(247, 241, 227))
    d.ellipse([x + w * 0.60, y + h * 0.30, x + w * 0.68, y + h * 0.46],
              fill=(120, 116, 108))
    d.ellipse([x + w * 0.64, y + h * 0.20, x + w * 0.74, y + h * 0.38],
              fill=(140, 136, 128))
    if h >= 50:
        d.text((x + w * 0.06, y + h * 0.78), "11 KILLED", font=ab(13),
               fill=(247, 241, 227))


def scene_gold(d, x, y, w, h):
    _sky(d, x, y, w, h, (40, 34, 22), (140, 106, 31))
    for i, bx in enumerate((0.08, 0.30, 0.52)):
        d.polygon([(x + w * bx, y + h * 0.82), (x + w * (bx + 0.04), y + h * 0.58),
                   (x + w * (bx + 0.16), y + h * 0.58), (x + w * (bx + 0.20), y + h * 0.82)],
                  fill=(214, 178, 94), outline=(140, 106, 31))
    pts = [(x + w * 0.72, y + h * 0.72), (x + w * 0.80, y + h * 0.55),
           (x + w * 0.88, y + h * 0.60), (x + w * 0.96, y + h * 0.34)]
    d.line(pts, fill=(247, 241, 227), width=3)
    d.polygon([pts[-1], (x + w * 0.96, y + h * 0.42), (x + w * 0.89, y + h * 0.36)],
              fill=(247, 241, 227))
    if h >= 50:
        d.text((x + w * 0.72, y + h * 0.12), "+1.5%", font=ab(14), fill=(247, 241, 227))


def scene_gta(d, x, y, w, h):
    _sky(d, x, y, w, h, (24, 20, 44), (150, 60, 80))
    _sun(d, x + w * 0.76, y + h * 0.30, 15, (214, 138, 40))
    tops = [0.44, 0.30, 0.52, 0.26, 0.46, 0.38]
    bw = w / len(tops)
    for i, t in enumerate(tops):
        bx = x + i * bw
        d.rectangle([bx + 1, y + h * t, bx + bw - 1, y + h], fill=(16, 14, 12))
        for wy in (0.58, 0.72, 0.84):
            d.rectangle([bx + 4, y + h * wy, bx + bw - 4, y + h * wy + 2],
                        fill=(214, 178, 94))
    if h >= 50:
        d.text((x + w * 0.06, y + h * 0.06), "VI", font=pf(20), fill=(247, 241, 227))


def scene_cricket(d, x, y, w, h):
    _sky(d, x, y, w, h, (28, 68, 40), (120, 150, 70))
    d.ellipse([x + w * 0.06, y + h * 0.55, x + w * 0.94, y + h * 1.05],
              fill=(46, 96, 52))
    d.rectangle([x + w * 0.68, y + h * 0.18, x + w * 0.72, y + h * 0.55],
                fill=(214, 178, 94))
    d.rectangle([x + w * 0.76, y + h * 0.18, x + w * 0.80, y + h * 0.55],
                fill=(214, 178, 94))
    d.rectangle([x + w * 0.84, y + h * 0.18, x + w * 0.88, y + h * 0.55],
                fill=(214, 178, 94))
    d.ellipse([x + w * 0.10, y + h * 0.30, x + w * 0.20, y + h * 0.50],
              fill=(163, 30, 34), outline=(247, 241, 227), width=1)
    d.rectangle([x + w * 0.30, y + h * 0.66, x + w * 0.62, y + h * 0.86],
                fill=(247, 241, 227))
    if h >= 50:
        d.text((x + w * 0.33, y + h * 0.68), "239/5", font=ab(13), fill=(20, 18, 16))


def scene_football(d, x, y, w, h):
    _sky(d, x, y, w, h, (20, 60, 36), (60, 120, 60))
    for i in range(4):
        d.rectangle([x, y + h * (0.45 + 0.14 * i), x + w, y + h * (0.59 + 0.14 * i)],
                    fill=(46, 110, 56) if i % 2 else (38, 96, 48))
    d.ellipse([x + w * 0.38, y + h * 0.42, x + w * 0.62, y + h * 0.98],
              outline=(247, 241, 227), width=2)
    d.line([(x + w * 0.50, y + h * 0.42), (x + w * 0.50, y + h * 0.98)],
           fill=(247, 241, 227), width=2)
    d.rectangle([x + w * 0.06, y + h * 0.10, x + w * 0.26, y + h * 0.42],
                outline=(247, 241, 227), width=2)
    d.ellipse([x + w * 0.78, y + h * 0.16, x + w * 0.90, y + h * 0.40],
              fill=(247, 241, 227), outline=(20, 18, 16), width=1)
    if h >= 50:
        d.text((x + w * 0.80, y + h * 0.20), "4", font=ab(14), fill=(20, 18, 16))
        d.text((x + w * 0.86, y + h * 0.20), "0", font=ab(14), fill=(163, 30, 34))


def scene_nvidia(d, x, y, w, h):
    _sky(d, x, y, w, h, (16, 40, 24), (40, 100, 52))
    d.rectangle([x + w * 0.32, y + h * 0.22, x + w * 0.68, y + h * 0.78],
                fill=(20, 18, 16), outline=(214, 178, 94), width=2)
    d.rectangle([x + w * 0.42, y + h * 0.38, x + w * 0.58, y + h * 0.62],
                fill=(118, 185, 0))
    for i in range(3):
        d.line([(x + w * (0.38 + 0.12 * i), y + h * 0.22),
                (x + w * (0.38 + 0.12 * i), y + h * 0.10)], fill=(214, 178, 94), width=2)
        d.line([(x + w * (0.38 + 0.12 * i), y + h * 0.78),
                (x + w * (0.38 + 0.12 * i), y + h * 0.90)], fill=(214, 178, 94), width=2)
    pts = [(x + w * 0.08, y + h * 0.80), (x + w * 0.20, y + h * 0.60),
           (x + w * 0.30, y + h * 0.66), (x + w * 0.44, y + h * 0.34),
           (x + w * 0.58, y + h * 0.40), (x + w * 0.74, y + h * 0.14),
           (x + w * 0.90, y + h * 0.10)]
    d.line(pts, fill=(247, 241, 227), width=3)
    if h >= 50:
        d.text((x + w * 0.72, y + h * 0.72), "+31%", font=ab(15), fill=(247, 241, 227))


SCENES = {"solana": scene_solana, "bitcoin": scene_bitcoin,
          "hongkong": scene_hongkong, "merkury": scene_merkury,
          "sparta": scene_sparta, "kyiv": scene_kyiv, "cop31": scene_cop31,
          "iran": scene_iran, "gaza": scene_gaza, "yemen": scene_yemen,
          "gold": scene_gold, "gta": scene_gta, "cricket": scene_cricket,
          "football": scene_football, "nvidia": scene_nvidia}

# ---------------------------------------------------------------- map
# Coarse hand-drawn continent outlines, lon/lat pairs (equirectangular).
CONTINENTS = {
    "NA": [(-168, 66), (-140, 70), (-120, 71), (-100, 68), (-85, 66), (-70, 62),
           (-60, 55), (-55, 47), (-65, 44), (-75, 35), (-80, 26), (-90, 21),
           (-97, 16), (-105, 20), (-115, 28), (-125, 40), (-130, 55), (-155, 58),
           (-168, 66)],
    "SA": [(-80, 10), (-70, 12), (-60, 8), (-52, 5), (-40, -5), (-35, -10),
           (-40, -20), (-48, -28), (-58, -35), (-65, -45), (-70, -54),
           (-73, -40), (-75, -25), (-80, -10), (-80, 10)],
    "EU": [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (12, 55),
           (18, 56), (21, 59), (28, 60), (30, 70), (40, 68), (45, 60), (40, 52),
           (30, 46), (28, 41), (22, 40), (18, 44), (12, 44), (8, 44), (3, 42),
           (-10, 36)],
    "AF": [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
           (43, 12), (51, 11), (48, 0), (40, -10), (35, -20), (30, -30),
           (20, -35), (15, -27), (12, -18), (9, -5), (-8, 4), (-17, 15)],
    "AS": [(40, 68), (50, 70), (70, 72), (100, 76), (130, 72), (160, 70),
           (178, 65), (162, 58), (142, 50), (135, 43), (127, 40), (122, 32),
           (115, 22), (105, 10), (100, 8), (95, 15), (90, 22), (80, 13),
           (75, 8), (70, 20), (60, 25), (55, 26), (48, 30), (43, 12),
           (40, 30), (35, 36), (30, 36), (28, 41), (30, 46), (40, 52),
           (45, 60), (40, 68)],
    "OC": [(114, -22), (122, -14), (132, -12), (142, -11), (146, -19),
           (153, -27), (150, -37), (140, -38), (130, -32), (122, -34),
           (115, -35), (114, -22)],
}

# (card num, lon, lat, dx, dy) - dx/dy spread pins that share a neighbourhood
PINS = [(1, -122, 37, -16, -10, "SOLANA"), (2, -95, 38, 0, 0, "BITCOIN"),
        (3, 114, 22, 0, 0, "HK"), (4, 20, 32, -14, 12, "BENGHAZI"),
        (5, 24, 60, -10, -4, "FINLAND"), (6, 30, 50, 12, -8, "KYIV"),
        (7, 30, 37, 0, 12, "ANTALYA"), (8, -77, 39, 0, 0, "DC"),
        (9, 34, 31, 14, -6, "GAZA"), (10, 44, 15, 6, 8, "YEMEN"),
        (11, 8, 47, 8, 4, "GOLD"), (12, -118, 34, -2, 12, "GTA VI"),
        (13, 175, -41, 0, 0, "WELLINGTON"), (14, -3, 53, -8, -4, "LIVERPOOL"),
        (15, -121, 37, 16, -2, "NVIDIA")]

# ---------------------------------------------------------------- drawing

def point_in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)) and \
                (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    d.rectangle([x, y, x + w, y + h], outline=GOLD, width=1)
    step = 5
    for gy in range(y + 4, y + h - 3, step):
        lat = 78 - (gy - y) / h * 140.0
        for gx in range(x + 4, x + w - 3, step):
            lon = -180 + (gx - x) / w * 360.0
            if any(point_in_poly(lon, lat, poly) for poly in CONTINENTS.values()):
                d.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=(214, 178, 94))
    for num, lon, lat, dx, dy, label in PINS:
        px = x + (lon + 180) / 360.0 * w + dx
        py = y + (78 - lat) / 140.0 * h + dy
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED,
                  outline=(247, 241, 227), width=1)
        t = str(num)
        twd = d.textlength(t, font=db(9))
        d.text((px - twd / 2, py - 5), t, font=db(9), fill=(247, 241, 227))


def draw_lead(d, c, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=GOLD, width=1)
    d.rectangle([x, y, x + w, y + 3], fill=GOLD)
    num = str(c["num"])
    d.rectangle([x + 6, y + 9, x + 24, y + 27], fill=BLACK)
    d.text((x + 11, y + 10), num, font=db(12), fill=(214, 178, 94))
    d.text((x + 29, y + 11), c["place"], font=ab(9), fill=GOLD_D)
    sy = y + 32
    sh = 70 if VARIANT == "A" else 66
    SCENES[c["scene"]](d, x + 1, sy, w - 2, sh)
    d.rectangle([x + 1, sy + sh - 15, x + w - 1, sy + sh], fill=(16, 14, 12))
    cw = chip(d, x + 6, sy + sh - 13, c["chip"], ab(9), (20, 18, 16), (214, 178, 94))
    d.text((x + 10 + cw, sy + sh - 12), c["tag"], font=ab(8), fill=(247, 241, 227))
    ty = sy + sh + 5
    hl = fit(d, c["head"], ab(15), w - 14, 2)
    ty = para(d, x + 7, ty, hl, ab(15), INK, 16)
    ty += 1
    dl = fit(d, c["deck"], ar(11), w - 14, 3)
    ty = para(d, x + 7, ty, dl, ar(11), (52, 48, 42), 12)
    d.text((x + 7, y + h - 13), c["src"], font=dr(8), fill=GREY)


def draw_mini(d, c, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=(198, 168, 110), width=1)
    if VARIANT == "A":
        SCENES[c["scene"]](d, x + 1, y + 1, w - 2, 30)
        tx, twd = x + 7, w - 14
        ty = y + 33
        d.text((tx, ty), "%d \u00b7 %s" % (c["num"], c["place"]), font=ab(8), fill=GOLD_D)
        d.text((x + w - 7, ty), c["tag"], font=ab(8), fill=RED, anchor="ra")
        ty += 12
        hl = fit(d, c["head"], ab(12), twd, 2)
        ty = para(d, tx, ty, hl, ab(12), INK, 13)
        dl = fit(d, c["deck"], ar(10), twd, 2)
        ty = para(d, tx, ty, dl, ar(10), (52, 48, 42), 11)
        foot = fit(d, "%s \u00b7 %s" % (c["chip"], c["src"]), ab(8), twd, 1)[0]
        d.text((tx, y + h - 10), foot, font=ab(8), fill=GOLD_D)
    else:  # B: scene strip on the left, text on the right
        SCENES[c["scene"]](d, x + 1, y + 1, 56, h - 2)
        d.rectangle([x + 57, y + 1, x + 57, y + h - 1], fill=GOLD)
        tx, twd = x + 63, w - 70
        ty = y + 6
        d.text((tx, ty), "%d \u00b7 %s" % (c["num"], c["place"]), font=ab(8), fill=GOLD_D)
        d.text((x + w - 7, ty), c["tag"], font=ab(8), fill=RED, anchor="ra")
        ty += 12
        hl = fit(d, c["head"], ab(12), twd, 2)
        ty = para(d, tx, ty, hl, ab(12), INK, 13)
        dl = fit(d, c["deck"], ar(10), twd, 3)
        ty = para(d, tx, ty, dl, ar(10), (52, 48, 42), 11)
        foot = fit(d, "%s \u00b7 %s" % (c["chip"], c["src"]), ab(8), twd, 1)[0]
        d.text((tx, y + h - 10), foot, font=ab(8), fill=GOLD_D)


def render():
    img = Image.new("RGB", (W, H), IVORY)
    d = ImageDraw.Draw(img)
    # top gold bar
    d.rectangle([0, 0, W, 6], fill=GOLD)
    # ---- masthead
    if VARIANT == "A":
        d.text((W // 2, 12), "THE GILDED PAGE", font=pf(56), fill=INK, anchor="ma")
        d.text((30, 34), "No. 24", font=ab(11), fill=GOLD_D)
        d.text((W - 30, 34), "TUESDAY EDITION", font=ab(11), fill=GOLD_D, anchor="ra")
    else:
        d.rectangle([0, 6, W, 76], fill=BLACK)
        d.text((W // 2, 12), "THE GILDED PAGE", font=pf(56), fill=(214, 178, 94),
               anchor="ma")
        d.text((30, 34), "No. 24", font=ab(11), fill=(214, 178, 94))
        d.text((W - 30, 34), "TUESDAY EDITION", font=ab(11), fill=(214, 178, 94),
               anchor="ra")
    d.text((W // 2, 78), "TUESDAY 24 NOVEMBER 2026", font=ab(16), fill=INK, anchor="ma")
    kick = "%d STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE FROM 24 NOVEMBER 2026" % TOTAL_STORIES
    d.text((W // 2, 98), kick, font=ab(11), fill=GOLD_D, anchor="ma")
    d.rectangle([24, 114, W - 24, 116], fill=GOLD)
    d.rectangle([24, 118, W - 24, 119], fill=GOLD)

    # ---- leads + numbers rail
    ly, lh = 126, 192
    lx = [24, 274, 524]
    for c, x in zip(LEADS, lx):
        draw_lead(d, c, x, ly, 242, lh)
    rx, rw = 774, 202
    d.rectangle([rx, ly, rx + rw, ly + lh], fill=BLACK)
    d.text((rx + rw // 2, ly + 8), "THE DAY IN", font=ab(12), fill=(214, 178, 94),
           anchor="ma")
    d.text((rx + rw // 2, ly + 24), "NUMBERS", font=ab(12), fill=(214, 178, 94),
           anchor="ma")
    d.line([(rx + 12, ly + 44), (rx + rw - 12, ly + 44)], fill=GOLD, width=1)
    ny = ly + 48
    for big, lab in NUMBERS:
        d.text((rx + 10, ny), big, font=ab(15), fill=(247, 241, 227))
        d.text((rx + rw - 10, ny + 3), lab, font=ab(8), fill=(214, 178, 94), anchor="ra")
        ny += 18
    d.text((rx + rw // 2, ly + lh - 12), "EVERY FIGURE BINDS A CARD",
           font=dr(7), fill=GREY, anchor="ma")

    # ---- 12 minis, 4 x 3
    my = 326
    mw, mh, gap = 238, 104, 8
    for i, c in enumerate(MINIS):
        col, row = i % 4, i // 4
        x = 24 + col * (mw + gap)
        yy = my + row * (mh + gap)
        draw_mini(d, c, x, yy, mw, mh)

    # ---- map band
    by = 658
    d.text((24, by), "WHERE IT HAPPENED", font=ab(13), fill=INK)
    d.text((W - 24, by + 2), "PINS MATCH STORY NUMBERS", font=ab(9), fill=GOLD_D,
           anchor="ra")
    draw_map(d, 24, by + 20, 620, 96)
    px, pw = 656, 344
    d.rectangle([px, by + 20, px + pw, by + 116], fill=PAPER, outline=GOLD, width=1)
    d.text((px + 10, by + 25), "STORIES BY REGION", font=ab(10), fill=GOLD_D)
    ry = by + 41
    for name, n in REGIONS:
        d.text((px + 10, ry), name, font=ab(10), fill=INK)
        d.text((px + pw - 10, ry), str(n), font=ab(12), fill=RED, anchor="ra")
        ry += 11
    # ---- ALSO ON, 3 columns x 8 rows
    ay = 780
    d.rectangle([24, ay, W - 24, ay + 1], fill=GOLD)
    d.text((24, ay + 6), "ALSO ON \u2014 TUESDAY 24 NOVEMBER 2026", font=ab(12), fill=INK)
    d.text((W - 24, ay + 8), "BRIEFS 16\u201339", font=ab(9), fill=GOLD_D, anchor="ra")
    colw = 322
    for i, b in enumerate(BRIEFS):
        col, row = i // 8, i % 8
        x = 24 + col * (colw + 6)
        yy = ay + 22 + row * 11
        d.text((x, yy), "%d." % (16 + i), font=db(10), fill=RED)
        bl = fit(d, b, ar(10), colw - 24, 1)
        d.text((x + 22, yy), bl[0] if bl else b, font=ar(10), fill=(52, 48, 42))

    # ---- timeline
    ty = 894
    d.rectangle([24, ty, W - 24, ty + 1], fill=GOLD)
    d.text((24, ty + 5), "THE DAY IN UTC", font=ab(11), fill=INK)
    slotw = 192
    for i, (when, what) in enumerate(TIMELINE):
        x = 24 + i * (slotw + 4)
        d.text((x, ty + 20), when, font=ab(9), fill=RED)
        wl = fit(d, what, ar(9), slotw - 6, 2)
        para(d, x, ty + 32, wl, ar(9), (52, 48, 42), 11)

    # ---- DATE CHECK
    dy = 952
    d.rectangle([24, dy, W - 24, dy + 38], fill=(250, 232, 228),
                outline=RED, width=1)
    d.text((34, dy + 4), "DATE CHECK \u2014 NOT TODAY:", font=ab(10), fill=RED)
    for i, (item, when) in enumerate(DATECHECK):
        col, row = i % 3, i // 3
        x = 34 + col * 318
        yy = dy + 18 + row * 11
        d.text((x, yy), "\u00d7 %s \u2014 %s" % (item, when), font=ar(9), fill=(92, 40, 40))

    # ---- footer
    fy = 994
    d.text((24, fy), "SOURCES: REUTERS \u00b7 AP \u00b7 BBC \u00b7 CNN \u00b7 TIMES \u00b7 GUARDIAN "
                     "\u00b7 WSJ \u00b7 COINPAPRIKA \u00b7 GADGETS360 \u00b7 HK NEWS TV \u00b7 AIM = "
                     "ACTIVEINVESTORMAG",
           font=dr(8), fill=GREY)
    d.text((24, fy + 11),
           "REPORTED = confirmed by outlets named \u00b7 CLAIM = one side\u2019s claim \u00b7 "
           "FORECAST = scheduled next \u00b7 Pictures and map: original, drawn in code. "
           "Original drawings.",
           font=dr(8), fill=GREY)
    return img


def all_text():
    out = ["THE GILDED PAGE", "TUESDAY 24 NOVEMBER 2026",
           "%d STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE FROM 24 NOVEMBER 2026" % TOTAL_STORIES,
           "THE DAY IN NUMBERS", "WHERE IT HAPPENED", "PINS MATCH STORY NUMBERS",
           "STORIES BY REGION", "ALSO ON", "THE DAY IN UTC", "DATE CHECK"]
    for c in LEADS + MINIS:
        out += [str(c["num"]), c["region"], c["place"], c["head"], c["deck"],
                c["chip"], c["src"], c["tag"]]
    out += ["%s %s" % (b, l) for b, l in NUMBERS]
    out += ["%s %d" % (n, v) for n, v in REGIONS]
    out += ["%s %s" % (a, b) for a, b in TIMELINE]
    out += ["%s %s" % (a, b) for a, b in DATECHECK]
    out += ["%d. %s" % (16 + i, b) for i, b in enumerate(BRIEFS)]
    return "\n".join(out)


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "entry.png")
    img = render()
    img.save(out, optimize=True)
    with open(os.path.join(BASE, "visible-text.txt"), "w") as f:
        f.write(all_text())
    print("wrote", out, img.size, os.path.getsize(out), "variant", VARIANT)
