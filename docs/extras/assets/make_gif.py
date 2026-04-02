from PIL import Image, ImageDraw, ImageFont
import math, os

# ═══════════════════════════════════════════════════════════════════
#  CANVAS
# ═══════════════════════════════════════════════════════════════════
W, H  = 1340, 570   # output (GIF) pixel dimensions
SCALE = 3           # supersampling: draw at SW×SH, downsample to W×H with LANCZOS
SW, SH = W * SCALE, H * SCALE

S = SCALE   # short alias used everywhere below

# ── Dark / neon palette ─────────────────────────────────────────
BG       = ( 13,  17,  23)
PANEL_BG = ( 22,  27,  34)
PLOT_BG  = ( 17,  21,  28)
ATOM_BG  = ( 18,  22,  32)   # dark purple-tinted atom region

GREEN      = (  0, 200, 120)
GREEN_DK   = (  0, 130,  80)
GREEN_ACC  = ( 10,  80,  55)
GFILL      = ( 22,  55,  38)
ATOM_FILL  = (160,  80, 255)   # neon purple atom body
ATOM_DK    = ( 90,  40, 180)   # purple atom outline

RED        = (255,  80,  80)
RED_ACC    = (110,  25,  25)

BLUE       = (160,  80, 255)
BLUE_DK    = ( 90,  40, 180)

ORANGE     = (255, 160,   0)
ORANGE_L   = (255, 200,  80)

GRAY       = (130, 145, 170)
LGRAY      = ( 70,  80, 100)
BORDER     = ( 40,  50,  70)
BLACK      = (220, 230, 240)   # near-white for general text
WHITE      = (255, 255, 255)   # pure white (atom/node labels)

FONT_PATH = "/usr/share/fonts/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/gnu-free/FreeSansBold.ttf"
OUTPUT    = "/home/vvitale/qoolqit/docs/extras/assets/qoolqit_demo.gif"

# ═══════════════════════════════════════════════════════════════════
#  FONTS  — loaded at SCALE× point size
# ═══════════════════════════════════════════════════════════════════
def load_fonts():
    def tf(p, sz):
        if p and os.path.exists(p):
            return ImageFont.truetype(p, sz * S)
        print(f"WARNING: font not found: {p!r} — falling back to bitmap font.")
        return ImageFont.load_default()
    return {
        "h1":    tf(FONT_BOLD, 26),
        "h2":    tf(FONT_BOLD, 18),
        "h3":    tf(FONT_BOLD, 15),
        "body":  tf(FONT_PATH, 16),
        "small": tf(FONT_PATH, 14),
        "tiny":  tf(FONT_PATH, 13),
    }
FONTS = load_fonts()

# ═══════════════════════════════════════════════════════════════════
#  MATH HELPERS
# ═══════════════════════════════════════════════════════════════════
def lerp(a, b, t): return a + (b - a) * t
def ease(t):       t = max(0., min(1., t)); return 3*t*t - 2*t*t*t
def clamp(v):      return max(0., min(1., v))
def ip(P, Q, t):   return [(lerp(px,qx,t), lerp(py,qy,t)) for (px,py),(qx,qy) in zip(P,Q)]

# ═══════════════════════════════════════════════════════════════════
#  TEXT HELPERS  — all pixel offsets inside helpers are pre-scaled
#                  because fonts are loaded at S× and bboxes return
#                  S× pixel metrics automatically.
# ═══════════════════════════════════════════════════════════════════
def txt(draw, xy, s, font="body", fill=BLACK, anchor=None):
    draw.text(xy, s, font=FONTS[font], fill=fill, anchor=anchor)

# ── Tokeniser for rich_txt ─────────────────────────────────────
def _tokenise(s):
    tokens = []
    i = 0
    while i < len(s):
        if s[i] == 'Ω' and i+1 < len(s) and s[i+1] == '~':
            tokens.append(('tilde', 'Ω')); i += 2
        elif s[i] == 'J' and i+1 < len(s) and s[i+1] == '~':
            tokens.append(('tilde', 'J')); i += 2
        elif s[i] == '≤':
            tokens.append(('leq', '≤')); i += 1
        elif s[i] == '≥':
            tokens.append(('geq', '≥')); i += 1
        elif s[i] == '_':
            # Subscript token: _word  (letters/digits until next non-alnum/non-underscore)
            j = i + 1
            while j < len(s) and (s[j].isalnum() or s[j] == '_'):
                j += 1
            tokens.append(('sub', s[i+1:j])); i = j
        else:
            j = i + 1
            while j < len(s):
                if (s[j] == 'Ω' and j+1 < len(s) and s[j+1] == '~'): break
                if (s[j] == 'J' and j+1 < len(s) and s[j+1] == '~'): break
                if s[j] in ('≤', '≥', '_'): break
                j += 1
            tokens.append(('plain', s[i:j])); i = j
    return tokens

def _token_width(tok_type, text, font_key):
    f = FONTS[font_key]
    ft = FONTS["tiny"]
    if tok_type in ('plain', 'tilde'):
        bx = f.getbbox(text); return bx[2] - bx[0]
    elif tok_type == 'sub':
        bx = ft.getbbox(text); return bx[2] - bx[0]
    elif tok_type in ('leq', 'geq'):
        try:    bx = f.getbbox(text); return bx[2] - bx[0]
        except: return int(f.getbbox('=')[2] - f.getbbox('=')[0])

def rich_txt(draw, xy, s, font="body", fill=BLACK, anchor=None):
    """Render *s* with Ω~, J~, ≤, ≥ tokens handled correctly."""
    tokens = _tokenise(s)
    if not tokens: return
    f  = FONTS[font]
    ft = FONTS["tiny"]
    total_w  = sum(_token_width(tt, tx, font) for tt, tx in tokens)
    sample   = f.getbbox("Ag")
    line_h   = sample[3] - sample[1]
    x, y = int(xy[0]), int(xy[1])
    if anchor == "mm":   x -= total_w // 2; y -= line_h // 2
    elif anchor == "lm": y -= line_h // 2
    elif anchor == "rm": x -= total_w;      y -= line_h // 2
    elif anchor == "mt": x -= total_w // 2
    cx = x
    for tok_type, text in tokens:
        w = _token_width(tok_type, text, font)
        if tok_type == 'plain':
            draw.text((cx, y), text, font=f, fill=fill)
        elif tok_type == 'tilde':
            draw.text((cx, y), text, font=f, fill=fill)
            tbox = ft.getbbox("~")
            tw = tbox[2] - tbox[0]; th = tbox[3] - tbox[1]
            draw.text((cx + w//2 - tw//2, y - th - 2*S), "~", font=ft, fill=fill)
        elif tok_type == 'sub':
            bh = f.getbbox("A")[3] - f.getbbox("A")[1]
            sub_y = y + int(bh * 0.55)
            draw.text((cx, sub_y), text, font=ft, fill=fill)
        elif tok_type in ('leq', 'geq'):
            draw.text((cx, y), text, font=f, fill=fill)
        cx += w

def txt_t(draw, xy, base_str, suffix="", font="body", fill=BLACK, anchor=None):
    """base_str with a tilde superscript, then optional suffix at normal size."""
    f  = FONTS[font]; ft = FONTS["tiny"]
    bx = f.getbbox(base_str); bw = bx[2]-bx[0]; bh = bx[3]-bx[1]
    tx_box = ft.getbbox("~"); tw = tx_box[2]-tx_box[0]; th = tx_box[3]-tx_box[1]
    total_str = base_str + suffix
    full_box  = f.getbbox(total_str) if suffix else bx
    fw = full_box[2] - full_box[0]; fh = bh
    x, y = int(xy[0]), int(xy[1])
    if anchor == "mm":   x -= fw//2; y -= fh//2
    elif anchor == "lm": y -= fh//2
    elif anchor == "rm": x -= fw;    y -= fh//2
    elif anchor == "mt": x -= fw//2
    draw.text((x, y), total_str, font=f, fill=fill)
    draw.text((x + bw//2 - tw//2, y - th - 2*S), "~", font=ft, fill=fill)

def txt_sub(draw, xy, base_str, sub_str, font="body", fill=BLACK, anchor=None):
    """base_str followed by sub_str rendered as a subscript."""
    f  = FONTS[font]; ft = FONTS["tiny"]
    bx = f.getbbox(base_str); bw = bx[2]-bx[0]; bh = bx[3]-bx[1]
    sx = ft.getbbox(sub_str); sw = sx[2]-sx[0]
    fw = bw + sw
    x, y = int(xy[0]), int(xy[1])
    if anchor == "mm":   x -= fw//2; y -= bh//2
    elif anchor == "lm": y -= bh//2
    elif anchor == "rm": x -= fw;    y -= bh//2
    elif anchor == "mt": x -= fw//2
    draw.text((x, y), base_str, font=f, fill=fill)
    sub_y = y + int(bh * 0.55)   # drop ~55% of cap-height
    draw.text((x + bw, sub_y), sub_str, font=ft, fill=fill)

# ═══════════════════════════════════════════════════════════════════
#  DRAWING PRIMITIVES  — width/radius/dash/gap args all in S× pixels
# ═══════════════════════════════════════════════════════════════════
def circ(draw, c, r, fill, outline=BLACK, width=2*S):
    x, y, r = int(c[0]), int(c[1]), max(1, int(r))
    draw.ellipse((x-r, y-r, x+r, y+r), fill=fill, outline=outline, width=width)

def seg(draw, a, b, fill=GRAY, width=2*S):
    draw.line((int(a[0]),int(a[1]),int(b[0]),int(b[1])), fill=fill, width=width)

def arr(draw, a, b, fill=GRAY, width=2*S, L=12*S):
    seg(draw, a, b, fill=fill, width=width)
    ang = math.atan2(b[1]-a[1], b[0]-a[0])
    p1 = (b[0]-L*math.cos(ang-math.pi/6), b[1]-L*math.sin(ang-math.pi/6))
    p2 = (b[0]-L*math.cos(ang+math.pi/6), b[1]-L*math.sin(ang+math.pi/6))
    draw.polygon([(int(b[0]),int(b[1])),(int(p1[0]),int(p1[1])),(int(p2[0]),int(p2[1]))], fill=fill)

def dash_h(draw, y, x0, x1, fill=GRAY, dash=5*S, gap=5*S):
    x = int(x0)
    while x < int(x1):
        draw.line((x,int(y),min(x+dash,int(x1)),int(y)), fill=fill, width=S)
        x += dash + gap

def dash_v(draw, x, y0, y1, fill=GRAY, dash=5*S, gap=5*S):
    y = int(y0)
    while y < int(y1):
        draw.line((int(x),y,int(x),min(y+dash,int(y1))), fill=fill, width=S)
        y += dash + gap

# ═══════════════════════════════════════════════════════════════════
#  PANEL
# ═══════════════════════════════════════════════════════════════════
HEADER_H = 62*S

def panel(draw, box, title, sub=None, accent=GREEN_ACC):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    draw.rounded_rectangle(box, radius=14*S, outline=BORDER, width=2*S, fill=PANEL_BG)
    hbox = (x0, y0, x1, y0 + HEADER_H)
    draw.rounded_rectangle(hbox, radius=14*S, fill=accent)
    draw.rectangle((x0, y0+HEADER_H-14*S, x1, y0+HEADER_H), fill=accent)
    if sub:
        txt(draw, (cx, y0+14*S), title, font="h2", fill=WHITE, anchor="mt")
        rich_txt(draw, (cx, y0+33*S), sub, font="tiny", fill=(160, 220, 190), anchor="mt")
    else:
        txt(draw, (cx, y0+HEADER_H//2), title, font="h2", fill=WHITE, anchor="mm")

def section_label(draw, x0, x1, y, label):
    rich_txt(draw, ((x0+x1)//2, y), label, font="h3", fill=GRAY, anchor="mm")

# ═══════════════════════════════════════════════════════════════════
#  LAYOUT  — all constants at S× resolution
# ═══════════════════════════════════════════════════════════════════
LEFT  = ( 14*S,  62*S, 614*S, 530*S)
RIGHT = (626*S,  62*S, 1326*S, 530*S)

GA = (30*S, 154*S, 600*S, 292*S)

GRAPH_PTS = [
    (162*S, 193*S), (272*S, 169*S), (392*S, 177*S),
    (476*S, 225*S), (255*S, 260*S), (388*S, 266*S),
]
EDGES = [(0,1),(1,2),(2,3),(0,4),(1,4),(1,5),(2,5),(4,5),(2,4),(3,5)]

def draw_graph(draw):
    for i, j in EDGES:
        d  = math.dist(GRAPH_PTS[i], GRAPH_PTS[j])
        ww = max(2*S, int((6 - min(d/(55*S), 3)) * S))
        seg(draw, GRAPH_PTS[i], GRAPH_PTS[j], fill=(100, 60, 200), width=ww)
    for k, p in enumerate(GRAPH_PTS):
        circ(draw, p, 17*S, BLUE, outline=BLUE_DK, width=2*S)
        txt(draw, p, str(k), font="tiny", fill=WHITE, anchor="mm")

# Parameter space — data area (where data is drawn)
# AX0/AY1 is the axis origin corner (tick base); data starts PX0/PY1 inset from there
_TICK_OUT = 6*S    # how far ticks protrude outward
_TICK_GAP = 4*S    # gap between tick tip and label
_YLAB_W   = 36*S   # pixel width reserved for y-axis tick labels left of AX0
_XLAB_H   = 20*S   # pixel height reserved for x-axis tick labels below AY1

# Outer box corners (where axis lines run)
AX0 = 147*S + _YLAB_W   # left edge of data, right of y-label space
AY1 = 522*S - _XLAB_H   # bottom edge of data, above x-label space
PX0 = AX0               # data left  = axis origin x
PY0 = 298*S             # data top
PX1 = 481*S             # data right
PY1 = AY1               # data bottom = axis origin y

J_MAX, O_MAX = 1.28, 0.58
P_INIT = (1.0, 0.4)
P_COMP = (0.5, 0.2)
O_LIM, J_LIM = 0.2, 1.0

def to_px(j, om):
    return (int(PX0 + (j/J_MAX)*(PX1-PX0)),
            int(PY1 - (om/O_MAX)*(PY1-PY0)))

# Hardware plane
LSR_X0      = 630*S
LSR_X1      = 718*S
MAX_BEAM_PX = 160*S
ATX0        = LSR_X1 + MAX_BEAM_PX
ATX1        = 1316*S
ATY0        = 124*S
ATY1        = 345*S

WY0, WY1 = ATY1 + 8*S,  ATY1 + 76*S
BY0, BY1 = WY1  + 5*S,  RIGHT[3] - 6*S

CX = (ATX0 + ATX1) // 2
CY = 239*S

SPREAD = 1.35   # atom cloud expansion factor from stage 1 → stage 3

# H0: same shape as GRAPH_PTS, mapped into the atom region with a margin
# Scale is chosen so H1 (= SPREAD × H0) also fits inside the region.
_AT_MARGIN = 70 * S
_gx_vals = [p[0] for p in GRAPH_PTS]
_gy_vals = [p[1] for p in GRAPH_PTS]
_gx_lo, _gx_hi = min(_gx_vals), max(_gx_vals)
_gy_lo, _gy_hi = min(_gy_vals), max(_gy_vals)
_gx_rng = max(_gx_hi - _gx_lo, 1)
_gy_rng = max(_gy_hi - _gy_lo, 1)
_at_w = ATX1 - ATX0 - 2 * _AT_MARGIN
_at_h = ATY1 - ATY0 - 2 * _AT_MARGIN
# Divide by SPREAD so the expanded cloud (H1) still fits inside
_scale_g = min(_at_w / _gx_rng, _at_h / _gy_rng) / SPREAD
# Centre of the graph cloud
_gcx = (_gx_lo + _gx_hi) / 2
_gcy = (_gy_lo + _gy_hi) / 2
H0 = [(int(CX + (_px - _gcx) * _scale_g),
       int(CY + (_py - _gcy) * _scale_g))
      for _px, _py in GRAPH_PTS]

H1  = [(int(CX+(x-CX)*SPREAD), int(CY+(y-CY)*SPREAD)) for x,y in H0]

def _verify():
    for tag, pts in [("H0",H0),("H1",H1)]:
        ok = all(ATX0<=int(x)<=ATX1 and ATY0<=int(y)<=ATY1 for x,y in pts)
        print(f"{tag} inside=[{ATX0}..{ATX1},{ATY0}..{ATY1}]: {ok}  "
              f"{[(int(x),int(y)) for x,y in pts]}")
_verify()

# ═══════════════════════════════════════════════════════════════════
#  PARAMETER SPACE PLOT
# ═══════════════════════════════════════════════════════════════════
_AXIS_COL = (150, 160, 180)
_GRID_COL = ( 35,  42,  55)
_DASH_COL = ( 80,  90, 110)

def draw_param_plot(draw, t_init=0.0, t_arrow=0.0, t_comp=0.0):

    # Outer background covers data area + tick+label margins
    outer = (PX0 - _YLAB_W - _TICK_OUT, PY0,
             PX1,                         PY1 + _XLAB_H + _TICK_OUT)
    draw.rectangle(outer, fill=PLOT_BG)
    draw.rectangle((PX0,PY0,PX1,PY1), outline=BORDER, width=S)

    # Allowed region fill
    ax0,ay0 = to_px(0, O_LIM)
    ax1,ay1 = to_px(J_LIM, 0)
    draw.rectangle((ax0,ay0,ax1,ay1), fill=GFILL)

    # Grid lines (clipped to data box)
    for jv in [0.2,0.4,0.6,0.8,1.0]:
        gx = to_px(jv,0)[0]
        seg(draw,(gx,PY0),(gx,PY1), fill=_GRID_COL, width=S)
    for ov in [0.1,0.2,0.3,0.4,0.5]:
        gy = to_px(0,ov)[1]
        seg(draw,(PX0,gy),(PX1,gy), fill=_GRID_COL, width=S)

    # Constraint dashes — clipped to data box
    jl_x = to_px(J_LIM, 0)[0]
    ol_y = to_px(0, O_LIM)[1]
    dash_v(draw, jl_x, PY0, PY1, fill=_DASH_COL)
    dash_h(draw, ol_y, PX0, PX1, fill=_DASH_COL)

    # Allowed region outline
    draw.rectangle((ax0,ay0,ax1,ay1), outline=GREEN, width=2*S)

    # Axis lines along data-box edges, with arrowheads at the far ends
    seg(draw,(PX0, PY1),(PX1, PY1),      fill=_AXIS_COL, width=2*S)   # x-axis
    seg(draw,(PX0, PY0),(PX0, PY1),      fill=_AXIS_COL, width=2*S)   # y-axis
    arr(draw,(PX1-14*S, PY1),(PX1, PY1), fill=_AXIS_COL, width=2*S, L=10*S)
    arr(draw,(PX0, PY1),(PX0, PY0),      fill=_AXIS_COL, width=2*S, L=10*S)

    # Axis labels at arrowhead ends
    txt_t(draw,(PX1+4*S, PY1),          "J", font="body", fill=_AXIS_COL, anchor="lm")
    txt_t(draw,(PX0+4*S, PY0+2*S),      "Ω", font="body", fill=_AXIS_COL)

    # X-axis ticks: protrude downward below PY1; labels below ticks
    for v in [0.2,0.4,0.6,0.8,1.0]:
        px = to_px(v,0)[0]
        draw.line((px, PY1, px, PY1+_TICK_OUT), fill=_AXIS_COL, width=S)
        txt(draw,(px, PY1+_TICK_OUT+_TICK_GAP), f"{v:.1f}",
            font="small", fill=_AXIS_COL, anchor="mt")
    # Y-axis ticks: protrude leftward of PX0; labels left of ticks
    for v in [0.1,0.2,0.3,0.4,0.5]:
        py = to_px(0,v)[1]
        draw.line((PX0-_TICK_OUT, py, PX0, py), fill=_AXIS_COL, width=S)
        txt(draw,(PX0-_TICK_OUT-_TICK_GAP, py), f"{v:.1f}",
            font="small", fill=_AXIS_COL, anchor="rm")

    # Ω~/J~ = 0.4 reference line
    seg(draw, to_px(0,0), to_px(J_LIM, J_LIM*0.4), fill=BLUE, width=2*S)
    lp = to_px(0.48, 0.48*0.4)
    rich_txt(draw,(lp[0]-4*S, lp[1]-18*S), "Ω~/J~ = 0.4", font="small", fill=BLUE, anchor="rm")

    # Legend — in the strip to the right of the plot
    lx, ly = PX1+8*S, PY0+10*S
    draw.rectangle((lx,ly,lx+120*S,ly+60*S), fill=PANEL_BG, outline=BORDER, width=S)
    draw.rectangle((lx+6*S,ly+9*S,lx+20*S,ly+21*S), fill=GFILL, outline=GREEN, width=S)
    txt(draw,(lx+26*S, ly+15*S), "Allowed", font="tiny", fill=BLACK, anchor="lm")
    txt(draw,(lx+26*S, ly+28*S), "region",  font="tiny", fill=BLACK, anchor="lm")
    seg(draw,(lx+6*S,ly+46*S),(lx+20*S,ly+46*S), fill=BLUE, width=2*S)
    rich_txt(draw,(lx+26*S,ly+46*S), "Ω~/J~ = 0.4", font="tiny", fill=BLACK, anchor="lm")

    _DOT_R = 9*S   # fixed dot radius for initial and compiled points

    # Travelling arrow — drawn first so dots render on top of the arrowhead
    if t_arrow > 0.0:
        pi    = to_px(*P_INIT)
        p_end = to_px(*P_COMP)
        cj    = lerp(P_INIT[0], P_COMP[0], ease(t_arrow))
        co    = lerp(P_INIT[1], P_COMP[1], ease(t_arrow))
        pc    = to_px(cj, co)
        dx_full = p_end[0] - pi[0]; dy_full = p_end[1] - pi[1]
        total_len = math.hypot(dx_full, dy_full)
        stop_dist = _DOT_R + 3*S          # stop tip just outside compiled dot
        min_draw  = 14*S                   # minimum arrow length before drawing

        dist_travelled = math.dist(pi, pc)
        if dist_travelled < min_draw:
            pass   # too short to draw cleanly — skip
        elif math.dist(pc, p_end) > stop_dist:
            # Arrow still travelling
            arr(draw, pi, pc, fill=BLACK, width=2*S)
            circ(draw, pc, 5*S, (255,215,50), outline=(200,160,0), width=S)
        else:
            # Arrow has reached the compiled dot — freeze tip just outside it
            if total_len > 0:
                px_tip = (int(p_end[0] - dx_full/total_len * stop_dist),
                          int(p_end[1] - dy_full/total_len * stop_dist))
                arr(draw, pi, px_tip, fill=BLACK, width=2*S)

    # Initial point (1, 0.4) — amber dot, fixed size, label to the left
    if t_init > 0.01:
        p = to_px(*P_INIT)
        r = _DOT_R
        circ(draw, p, r, ORANGE, outline=ORANGE_L, width=2*S)
        txt(draw,(p[0]-r-5*S, p[1]-14*S), "(1, 0.4)", font="tiny", fill=BLACK, anchor="rm")
        txt(draw,(p[0]-r-5*S, p[1]+1*S),  "initial",  font="tiny", fill=ORANGE, anchor="rm")

    # Compiled point (0.5, 0.2) — green dot, fixed size, labels BELOW
    if t_comp > 0.01:
        p = to_px(*P_COMP)
        r = _DOT_R
        circ(draw, p, r, GREEN, outline=GREEN_DK, width=2*S)
        txt(draw,(p[0], p[1]+r+3*S),  "compiled",   font="tiny", fill=GREEN, anchor="mt")
        txt(draw,(p[0], p[1]+r+16*S), "(0.5, 0.2)", font="tiny", fill=BLACK, anchor="mt")

# ═══════════════════════════════════════════════════════════════════
#  HARDWARE PLANE
# ═══════════════════════════════════════════════════════════════════
def _atom_glow(img, pts, frame_t=0.0, pulsing=False):
    """Neon purple glow halo composited onto the RGBA image layer."""
    gd = ImageDraw.Draw(img, "RGBA")
    for k, p in enumerate(pts):
        if pulsing:
            ph  = 0.5 + 0.5 * math.sin(2 * math.pi * (frame_t + k / 7))
            r   = (13 + 6*ph) * S
            col = (int(120+80*ph), int(40+30*ph), int(220+35*ph), int(90+80*ph))
        else:
            r   = 18 * S
            col = (140, 60, 220, 70)
        gd.ellipse((p[0]-r, p[1]-r, p[0]+r, p[1]+r), fill=col, outline=ATOM_DK, width=S)

def draw_hw(draw, pts, beam_amp=1.0, compiled=False, show_wave=False,
            wave_phase=0, img=None, frame_t=0.0, pulsing=False):
    laser_cy = (ATY0 + ATY1) // 2
    strip_cx = (LSR_X0 + LSR_X1) // 2

    # Atom region box
    draw.rounded_rectangle((ATX0,ATY0,ATX1,ATY1),
                            radius=12*S, outline=GREEN, width=2*S, fill=ATOM_BG)

    # Trap-array lattice grid — horizontal and vertical lines suggesting
    # the optical trap array of a neutral-atom platform
    _GRID_STEP = 44*S
    _GCOL      = (38, 30, 72)   # dim purple-grey, distinct from ATOM_BG=(18,22,32)
    _gx_start  = ATX0 + (_GRID_STEP - (ATX0 % _GRID_STEP if _GRID_STEP else 1)) % _GRID_STEP
    _gy_start  = ATY0 + (_GRID_STEP - (ATY0 % _GRID_STEP if _GRID_STEP else 1)) % _GRID_STEP
    for gx in range(ATX0 + 22*S, ATX1, _GRID_STEP):
        draw.line((gx, ATY0+2*S, gx, ATY1-2*S), fill=_GCOL, width=S)
    for gy in range(ATY0 + 22*S, ATY1, _GRID_STEP):
        draw.line((ATX0+2*S, gy, ATX1-2*S, gy), fill=_GCOL, width=S)

    # Laser source box
    sy0, sy1 = laser_cy-22*S, laser_cy+22*S
    draw.rounded_rectangle((LSR_X0,sy0,LSR_X1,sy1),
                            radius=8*S, fill=(20,20,40), outline=LGRAY, width=2*S)
    txt(draw,(strip_cx, laser_cy), "Laser", font="tiny", fill=BLACK, anchor="mm")

    # Status text
    if compiled:
        txt(draw,(strip_cx, laser_cy-42*S), "[OK] within", font="tiny", fill=GREEN, anchor="mm")
        txt(draw,(strip_cx, laser_cy-28*S), "limits",      font="tiny", fill=GREEN, anchor="mm")
    else:
        txt(draw,(strip_cx, laser_cy-42*S), "[!] over",    font="tiny", fill=RED,   anchor="mm")
        txt(draw,(strip_cx, laser_cy-28*S), "limit",       font="tiny", fill=RED,   anchor="mm")

    txt(draw,(strip_cx, laser_cy+36*S), "Allowed",     font="tiny", fill=GREEN, anchor="mm")
    txt(draw,(strip_cx, laser_cy+50*S), "atom region", font="tiny", fill=GREEN, anchor="mm")

    # Beam — multi-layer RGBA glow composited on the image for a neon laser look
    exceeds  = beam_amp > 1.0
    vis_len  = int(MAX_BEAM_PX * min(beam_amp, 1.85))
    if exceeds:
        c_core = (255, 240, 220, 255)   # near-white hot core
        c_mid  = (255,  80,  40, 140)   # red mid-glow
        c_out  = (200,  30,  10,  55)   # dim red outer halo
    else:
        c_core = (255, 250, 220, 255)   # near-white core
        c_mid  = (255, 180,  30, 130)   # amber mid-glow
        c_out  = (255, 120,   0,  50)   # dim orange outer halo
    hw_out  = max(8*S,  int((4 + 18*min(beam_amp/2.0, 1.0)) * S))
    hw_mid  = max(4*S,  int((2 + 10*min(beam_amp/2.0, 1.0)) * S))
    hw_core = max(1*S,  2*S)
    x0, x1 = LSR_X1, LSR_X1 + vis_len
    gd = ImageDraw.Draw(img, "RGBA")
    gd.rectangle((x0, laser_cy - hw_out,  x1, laser_cy + hw_out),  fill=c_out)
    gd.rectangle((x0, laser_cy - hw_mid,  x1, laser_cy + hw_mid),  fill=c_mid)
    gd.rectangle((x0, laser_cy - hw_core, x1, laser_cy + hw_core), fill=c_core)

    # Ω_max indicator: horizontal red bar above the laser beam,
    # spanning the gap between the laser box (LSR_X1) and the atom box (ATX0).
    # Placed above the beam at a fixed y clear of the widest possible beam.
    _max_half_w = max(4*S, int((5 + 22) * S)) // 2   # half-width when beam_amp=2.0
    bar_y = laser_cy - _max_half_w - 10*S             # fixed y above beam
    bar_cx = (LSR_X1 + ATX0) // 2
    seg(draw, (LSR_X1, bar_y), (ATX0, bar_y), fill=RED, width=2*S)
    # Vertical tick marks at each end of the bar
    seg(draw, (LSR_X1, bar_y - 5*S), (LSR_X1, bar_y + 5*S), fill=RED, width=2*S)
    seg(draw, (ATX0,   bar_y - 5*S), (ATX0,   bar_y + 5*S), fill=RED, width=2*S)
    # Label centred above the bar
    txt_sub(draw, (bar_cx, bar_y - 14*S), "Ω", "max", font="tiny", fill=RED, anchor="mm")

    # Atom glow (composited before bonds and atoms)
    if img is not None:
        _atom_glow(img, pts, frame_t=frame_t, pulsing=pulsing)

    # Atoms (no edges — hardware panel shows atom positions only)
    for k, p in enumerate(pts):
        circ(draw, p, 13*S, ATOM_FILL, outline=ATOM_DK, width=2*S)
        txt(draw, p, str(k), font="tiny", fill=WHITE, anchor="mm")

    if show_wave:
        _draw_wave(draw, (630*S, WY0, 1318*S, WY1), wave_phase)


def _draw_wave(draw, box, phase):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=8*S, outline=BORDER, width=S, fill=PANEL_BG)
    th = 20*S
    draw.rectangle((x0+2*S, y0+2*S, x1-2*S, y0+th), fill=(20,30,25))
    txt(draw,((x0+x1)//2, y0+11*S), "Laser pulse  -  atom evolution",
        font="small", fill=BLACK, anchor="mm")
    wt = y0 + th + 4*S
    wave_pts = []
    for x in range(x0+14*S, x1-14*S):
        u  = (x-(x0+14*S)) / max(1,(x1-x0-28*S))
        cy = (wt+y1)/2
        yy = cy - 13*S*math.sin(2*math.pi*(2.3*u+phase))*math.exp(-0.3*u)
        wave_pts.append((x, max(wt+2*S, min(y1-3*S, yy))))
    if len(wave_pts) > 1:
        draw.line(wave_pts, fill=ORANGE, width=2*S)


def draw_bits(draw, box, probs):
    """Draw 6 bitstrings in two columns of 3 inside *box*.
    probs must have 6 entries: indices 0-2 go in the left column,
    indices 3-5 go in the right column.
    """
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=8*S, outline=BORDER, width=S, fill=PANEL_BG)
    txt(draw,((x0+x1)//2, y0+13*S), "Bitstring distribution",
        font="small", fill=BLACK, anchor="mm")

    mid    = (x0 + x1) // 2
    bar_y0 = y0 + 28*S
    row_h  = max(1, (y1 - bar_y0 - 6*S) // 3)

    # Divider between columns
    draw.line((mid, y0+20*S, mid, y1-4*S), fill=BORDER, width=S)

    labels = ["000000", "011001", "110001", "101010", "100110", "001110"]
    col_defs = [
        (x0, mid),   # left column
        (mid, x1),   # right column
    ]
    _LBL_W = 88*S   # pixels reserved for the bitstring label on each column
    _PAD   = 10*S   # left padding inside each column

    for col, (cx0, cx1) in enumerate(col_defs):
        col_w = cx1 - cx0
        bmax  = col_w - _LBL_W - 40*S   # space available for the bar
        for row in range(3):
            i  = col * 3 + row
            yy = bar_y0 + row * row_h + row_h // 2
            lbl_x = cx0 + _PAD
            bar_x0 = cx0 + _LBL_W
            bar_w  = int(bmax * probs[i])
            bar_x1 = bar_x0 + max(4*S, bar_w)
            txt(draw, (lbl_x, yy), labels[i], font="small", anchor="lm")
            if bar_w > 0:
                draw.rounded_rectangle((bar_x0, yy-9*S, bar_x1, yy+9*S),
                                       radius=5*S, fill=BLUE, outline=BLUE_DK, width=S)
            val_x = bar_x0 + 8*S if bar_w == 0 else bar_x1 + 8*S
            txt(draw, (val_x, yy), f"{probs[i]:.2f}", font="small", anchor="lm")

# ═══════════════════════════════════════════════════════════════════
#  FRAME BUILDER
# ═══════════════════════════════════════════════════════════════════
DIV_X = 620*S

def build_frames(n=320):
    frames = []
    # Stage frame counts: stage 1 = 1 flash frame,
    # stages 2+3 share a unified compile animation (no pause at boundary),
    # stage 4 = longer evolution finale.
    N1       = 1
    N23      = 260   # frames for the unified compile span (stages 2+3 together)
    F1       = N1
    F3       = F1 + N23   # end of compile span
    # stage 4: [F3, n)
    for f in range(n):
        img  = Image.new("RGBA", (SW, SH), BG)
        draw = ImageDraw.Draw(img, "RGBA")

        # Canvas title
        txt(draw,(SW//2, 28*S),
            "QoolQit   -   Dimensionless Program → Compiled Physical Program",
            font="h1", fill=GREEN, anchor="mm")
        seg(draw,(12*S,50*S),(SW-12*S,50*S), fill=BORDER, width=S)



        # ── Stage logic ─────────────────────────────────────────
        if f < F1:
            # Stage 1: single frame — initial state, no animation
            panel(draw, LEFT,
                  "1  -  Dimensionless Program",
                  "Ω~/J~ = 0.4   -   laser power is 40 % of coupling strength",
                  accent=GREEN_ACC)
            draw_graph(draw)
            section_label(draw, GA[0], GA[2], 313*S, "Parameter space  Ω~ vs J~")
            draw_param_plot(draw, t_init=1.0)

            panel(draw, RIGHT,
                  "2  -  Initial Hardware Mapping",
                  "Atoms at minimum spacing   -   Ω~ = 0.4,  J~ = 1.0",
                  accent=GREEN_ACC)
            draw_hw(draw, H0, beam_amp=2.0, compiled=False, img=img, frame_t=0.0)

        elif f < F3:
            # Unified compile span: single continuous t across stages 2+3,
            # eased once so there is no deceleration/re-acceleration at the boundary.
            t_lin = (f - F1) / (N23 - 1)   # linear 0→1 across full compile span
            t     = ease(t_lin)             # eased once, monotonically 0→1

            # Panel labels switch at the midpoint
            if t_lin < 0.5:
                panel(draw, LEFT,
                      "2  -  Program Point (1, 0.4) Outside Allowed Region",
                      "Ω~ = 0.4  >  Ω~_max = 0.2   -   must compile to fit device",
                      accent=RED_ACC)
                panel(draw, RIGHT,
                      "2  -  Laser Power Exceeds Device Limit",
                      "Ω~ = 0.4  >  Ω~_max = 0.2   -   rescale Ω~ and J~ by 2",
                      accent=RED_ACC)
            else:
                panel(draw, LEFT,
                      "3  -  Compile:  (1, 0.4) → (0.5, 0.2)",
                      "Rescale Ω~ and J~ by 2   -   ratio Ω~/J~ = 0.4 preserved",
                      accent=GREEN_ACC)
                panel(draw, RIGHT,
                      "3  -  Spread Atoms  +  Reduce Laser Power",
                      "Atom spacing x 1.35   -   J~ and Ω~ both halve to reach (0.5, 0.2)",
                      accent=GREEN_ACC)

            draw_graph(draw)
            section_label(draw, GA[0], GA[2], 313*S, "Parameter space  Ω~ vs J~")
            draw_param_plot(draw, t_init=1.0, t_arrow=t, t_comp=clamp((t - 0.8) / 0.2))

            draw_hw(draw, ip(H0, H1, t),
                    beam_amp=lerp(2.0, 1.0, clamp(t / 0.8)),
                    compiled=(t > 0.8),
                    img=img, frame_t=t)

        else:
            N4_actual = n - F3
            t = ease((f - F3) / max(N4_actual - 1, 1))
            panel(draw, LEFT,
                  "4  -  Compiled Program  [OK]",
                  "Ω~ = J~ = 0.2   -   inside allowed region, ratio preserved",
                  accent=GREEN_ACC)
            draw_graph(draw)
            section_label(draw, GA[0], GA[2], 313*S, "Parameter space  Ω~ vs J~")
            draw_param_plot(draw, t_init=1.0, t_arrow=1.0, t_comp=1.0)

            panel(draw, RIGHT,
                  "4  -  Evolve on Hardware and Measure",
                  "Compiled Hamiltonian   -   bitstring outcomes sampled",
                  accent=GREEN_ACC)
            draw_hw(draw, H1, beam_amp=1.0, compiled=True,
                    show_wave=True, wave_phase=t,
                    img=img, frame_t=t, pulsing=True)

            p0 = [
                max(0.05, 0.20 + 0.42 * t),
                max(0.05, 0.50 - 0.24 * t),
                max(0.05, 0.16 + 0.06 * math.sin(2 * math.pi * t)),
                max(0.05, 0.30 - 0.18 * t),
                max(0.05, 0.10 + 0.22 * math.sin(math.pi * t)),
                max(0.05, 0.08 + 0.14 * t),
            ]
            s = sum(p0)
            p0 = [v / s for v in p0]
            blend = clamp(t / 0.35)   # transition from [1,0,0,0,0,0] over first 35% of stage 4
            start = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            probs = [lerp(start[i], p0[i], blend) for i in range(6)]
            draw_bits(draw, (630*S, BY0, 1318*S, BY1), probs)

        # Footer
        rich_txt(draw,(SW//2, 547*S),
            "Compilation preserves Ω~/J~ = 0.4 while rescaling by 2 "
            "to satisfy Ω~ ≤ 0.2  and  J~ ≤ 1.0.",
            font="small", fill=GRAY, anchor="mm")

        # Downsample to output resolution with high-quality quantisation
        out = img.resize((W, H), Image.LANCZOS).convert("RGB")
        frames.append(out.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=1))
    return frames

# ═══════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════
def main():
    frames = build_frames(n=379)
    frames[0].save(
        OUTPUT, save_all=True, append_images=frames[1:],
        duration=40, loop=0, optimize=False, disposal=2,
    )
    print(f"Saved: {OUTPUT}")

if __name__ == "__main__":
    main()
