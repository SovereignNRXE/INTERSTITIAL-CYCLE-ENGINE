"""
INTERSTITIAL CYCLE ENGINE — Brand Render Engine
Ground-up rebuild to brand spec v1.0

Palette:
  BG      #0A0A0A
  WHITE   #FFFFFF  — headings, scores, primary values
  GREY70  #4D4D4D  — body text, secondary content
  GREY50  #808080  — metadata, rules, cycle ref
  GREY15  #D9D9D9  — node names, labels

Typography:
  Liberation Sans Bold   — Display / Heading / Bold labels
  Liberation Sans Regular — Body / Meta / Strapline

Layout:
  W = 1600px, PAD = 84px each side, content width = 1488px
  Header: spiral icon (72px) + wordmark text, white 1px rule underneath
  No footer. No left stripe. No coloured badges.
  Page ref: micro grey top-right.
  Score bars: full content width, solid fill, brightness-scaled by score
  Scenario bars: label | bar | % outcome — single row
"""

import os, textwrap
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.image import imread as mpl_imread
from PIL import Image, ImageDraw, ImageFont

# ── Paths ──────────────────────────────────────────────────────────────────────
_DIR = Path(__file__).parent

SPIRAL_PATH   = _DIR / "spiral_symbol.png"
WORDMARK_PATH = _DIR / "logo_dark_wordmark.png"

FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

# ── Palette ────────────────────────────────────────────────────────────────────
BG     = (10,  10,  10)
WHITE  = (255, 255, 255)
G70    = (77,  77,  77)
G50    = (128, 128, 128)
G15    = (217, 217, 217)
TRACK  = (28,  28,  28)

# ── Font cache ─────────────────────────────────────────────────────────────────
_FC = {}
def F(size, bold=False):
    k = (size, bold)
    if k not in _FC:
        p = FONT_BOLD if bold else FONT_REG
        try:
            _FC[k] = ImageFont.truetype(p, size)
        except Exception:
            _FC[k] = ImageFont.load_default()
    return _FC[k]

# ── Score → grey ───────────────────────────────────────────────────────────────
def sg(pct):
    """Score → RGB grey tuple, 0%=dim, 100%=white"""
    v = int(55 + min(pct, 100) / 100 * 200)
    return (v, v, v)

def sg_f(pct):
    v = (55 + min(pct, 100) / 100 * 200) / 255
    return (v, v, v)

# ── Layout constants ───────────────────────────────────────────────────────────
W   = 2400
PAD = 84
CW  = W - PAD * 2   # 2232
HH  = 160           # header height

# ── Header ─────────────────────────────────────────────────────────────────────
def draw_header(img, draw, page_ref=""):
    """Spiral icon + Interstitial wordmark + rule. No grey box, no badge."""
    icon_sz = 108
    icon_y  = (HH - icon_sz) // 2

    # Spiral symbol
    if SPIRAL_PATH.exists():
        sp = Image.open(str(SPIRAL_PATH)).convert("RGB").resize(
            (icon_sz, icon_sz), Image.LANCZOS)
        img.paste(sp, (PAD, icon_y))
    else:
        draw.rectangle([PAD, icon_y, PAD+icon_sz, icon_y+icon_sz], outline=WHITE)

    tx = PAD + icon_sz + 28

    # "Interstitial" — bold 34pt
    draw.text((tx, icon_y + 4), "Interstitial",
              font=F(50, bold=True), fill=WHITE)

    # "MEASURING THE FUTURE" — regular 11pt, tracked feel via spacing
    draw.text((tx, icon_y + 68), "MEASURING THE FUTURE",
              font=F(16), fill=G50)

    # Page ref — micro grey, top right
    if page_ref:
        rw = draw.textlength(page_ref, font=F(11))
        draw.text((W - PAD - rw, 24), page_ref, font=F(16), fill=G50)

    # White rule under header — 1px
    draw.line([(PAD, HH - 1), (W - PAD, HH - 1)], fill=WHITE, width=1)

# ── Score bar ──────────────────────────────────────────────────────────────────
def draw_bar(draw, x, y, w, pct, h=24):
    """Full-width track, solid fill scaled to pct, % label right of fill."""
    draw.rectangle([x, y, x + w, y + h], fill=TRACK)
    fw = int(w * pct / 100)
    if fw > 0:
        draw.rectangle([x, y, x + fw, y + h], fill=sg(pct))
    # % label
    lbl = f"{pct}%"
    lx  = x + fw + 10 if fw < w - 60 else x + fw - 50
    ly  = y + h // 2 - 8
    draw.text((lx, ly), lbl, font=F(21, bold=True), fill=WHITE)

# ── Thin rule ──────────────────────────────────────────────────────────────────
def rule(draw, y, col=G70, weight=1):
    draw.line([(PAD, y), (W - PAD, y)], fill=col, width=weight)

# ── Text wrap ─────────────────────────────────────────────────────────────────
def wrap(text, chars=108):
    return textwrap.wrap(str(text), width=chars)

# ── Pre-calculate page height ──────────────────────────────────────────────────
def calc_height(blocks):
    h = HH + 40
    for b in blocks:
        t = b[0]
        if   t == 'space':   h += b[1]
        elif t == 'rule':    h += 30
        elif t == 'h1':      h += 68
        elif t == 'h2':      h += 48
        elif t == 'meta':    h += 34
        elif t == 'kv':      h += 44
        elif t == 'body':    h += len(wrap(b[1])) * 34 + 12
        elif t == 'node':
            nd = b[1]
            h += 42                                    # id + name row
            h += 40                                    # bar
            h += len(wrap(nd.get('assessment',''))) * 34 + 12
            h += len(wrap('GAP  ' + nd.get('gap',''))) * 34 + 32
        elif t == 'summary':
            h += len(b[1]) * 58 + 54                  # per-node 2 rows
        elif t == 'scenarios':
            h += len(b[1]) * 76 + 24
        elif t == 'synthesis':
            h += len(wrap(b[1], 100)) * 40 + 48
    return max(h + 60, 1000)

# ── Page render ────────────────────────────────────────────────────────────────
def render_page(blocks, page_num, total, out_path):
    H   = calc_height(blocks)
    img = Image.new('RGB', (W, H), BG)
    drw = ImageDraw.Draw(img)

    draw_header(img, drw, page_ref=f"{page_num} / {total}")

    y = HH + 54

    for b in blocks:
        t = b[0]

        # ── space ─────────────────────────────────────────────────────────────
        if t == 'space':
            y += b[1]

        # ── rule ──────────────────────────────────────────────────────────────
        elif t == 'rule':
            col, wt = (b[1], b[2]) if len(b) > 2 else (G70, 1)
            rule(drw, y + 12, col, wt)
            y += 30

        # ── h1: section heading — white bold 18pt ─────────────────────────────
        elif t == 'h1':
            drw.text((PAD, y), b[1].upper(), font=F(27, bold=True), fill=WHITE)
            y += 68

        # ── h2: sub-heading — grey15 bold 14pt ───────────────────────────────
        elif t == 'h2':
            drw.text((PAD, y), b[1].upper(), font=F(21, bold=True), fill=G15)
            y += 48

        # ── meta: small grey line ─────────────────────────────────────────────
        elif t == 'meta':
            drw.text((PAD, y), b[1], font=F(17), fill=G50)
            y += 34

        # ── kv: key  value pair ───────────────────────────────────────────────
        elif t == 'kv':
            key, val = b[1], b[2]
            kw = drw.textlength(key.upper() + "  ", font=F(19, bold=True))
            drw.text((PAD, y), key.upper() + "  ", font=F(19, bold=True), fill=G50)
            drw.text((PAD + kw, y), val.upper(), font=F(19, bold=False), fill=WHITE)
            y += 44

        # ── body: grey70 regular 13pt wrapped ────────────────────────────────
        elif t == 'body':
            for ln in wrap(b[1]):
                drw.text((PAD, y), ln, font=F(20), fill=G70)
                y += 34
            y += 12

        # ── node: full node block ─────────────────────────────────────────────
        elif t == 'node':
            nd     = b[1]
            nid    = nd['id']
            nname  = nd['name']
            status = nd.get('status', '').upper()
            score  = nd.get('score', 0)
            assess = nd.get('assessment', '')
            gap    = nd.get('gap', '')

            # Row 1: N-01  NODE NAME                            STATUS
            id_str = nid + "  "
            iw     = drw.textlength(id_str, font=F(22, bold=True))
            drw.text((PAD, y), id_str, font=F(22, bold=True), fill=WHITE)
            drw.text((PAD + iw, y), nname.upper(), font=F(22), fill=G15)
            sw = drw.textlength(status, font=F(16))
            drw.text((W - PAD - sw, y + 4), status, font=F(16), fill=G50)
            y += 42

            # Row 2: score bar — full CW
            draw_bar(drw, PAD, y, CW, score, h=24)
            y += 40

            # Assessment
            for ln in wrap(assess):
                drw.text((PAD, y), ln, font=F(20), fill=G70)
                y += 34
            y += 12

            # GAP
            gap_label = "GAP  "
            glw = drw.textlength(gap_label, font=F(18, bold=True))
            gap_lines = wrap(gap, chars=100)
            for i, ln in enumerate(gap_lines):
                if i == 0:
                    drw.text((PAD, y), gap_label, font=F(18, bold=True), fill=G50)
                    drw.text((PAD + glw, y), ln, font=F(18), fill=G50)
                else:
                    drw.text((PAD + glw, y), ln, font=F(18), fill=G50)
                y += 34
            y += 32

        # ── summary: node strength table ──────────────────────────────────────
        elif t == 'summary':
            nodes, composite = b[1], b[2]
            for nd in nodes:
                nid   = nd['id'] + "  "
                nname = nd['name'].upper()
                score = nd.get('score', 0)
                stat  = nd.get('status', '').upper()

                iw = drw.textlength(nid, font=F(19, bold=True))
                drw.text((PAD, y), nid, font=F(19, bold=True), fill=WHITE)
                drw.text((PAD + iw, y), nname, font=F(19), fill=G15)
                sw = drw.textlength(stat, font=F(15))
                drw.text((W - PAD - sw, y + 2), stat, font=F(15), fill=G50)
                y += 30

                draw_bar(drw, PAD, y, CW, score, h=18)
                y += 28

            # Composite
            rule(drw, y + 6, G70)
            y += 20
            comp_label = "COMPOSITE SCORE  "
            clw = drw.textlength(comp_label, font=F(24, bold=True))
            drw.text((PAD, y), comp_label, font=F(24, bold=True), fill=G50)
            drw.text((PAD + clw, y), f"{composite}%", font=F(24, bold=True), fill=WHITE)
            y += 54

        # ── scenarios: probability bar matrix ────────────────────────────────
        elif t == 'scenarios':
            for sc in b[1]:
                sid     = f"[{sc['id']}]"
                label   = sc.get('label', '').upper()
                prob    = sc.get('probability', 0)
                outcome = sc.get('outcome', '').upper()

                # Label row
                prefix = sid + "  "
                pw = drw.textlength(prefix, font=F(21, bold=True))
                drw.text((PAD, y), prefix, font=F(21, bold=True), fill=WHITE)
                drw.text((PAD + pw, y), label, font=F(21), fill=G15)
                ow = drw.textlength(outcome, font=F(16))
                drw.text((W - PAD - ow, y + 3), outcome, font=F(16), fill=G50)
                y += 36

                # Probability bar
                draw_bar(drw, PAD, y, CW, prob, h=22)
                y += 38

        # ── synthesis: grey15 regular 14pt ───────────────────────────────────
        elif t == 'synthesis':
            for ln in wrap(b[1], 100):
                drw.text((PAD, y), ln, font=F(21), fill=G15)
                y += 40
            y += 24

    img.save(str(out_path), "JPEG", quality=98, subsampling=0)


# ── Build page block lists ─────────────────────────────────────────────────────
def build_pages(data):
    subj      = data['subject']
    scope     = data['scope']
    ref       = data['ref']
    ts        = data['timestamp'][:10]
    nodes     = data['nodes']
    scenarios = data['scenarios']
    composite = data['composite_score']
    synthesis = data['synthesis']
    master    = data['master_node']
    n         = data.get('cycle_number', 0)
    cyc       = f"INTER//CYCLE {str(n).zfill(6)}"

    meta = f"{ts}    {ref}    {cyc}"

    def header_block(pg):
        return [
            ('meta',  meta),
            ('space', 10),
            ('kv',    'Subject', subj),
            ('kv',    'Scope',   scope),
            ('space', 12),
            ('rule',  WHITE, 1),
        ]

    # Page 1 — nodes N-01/02/03
    p1 = header_block(1) + [
        ('h1',   'Node Assessments'),
        ('rule', G70, 1),
        ('space', 10),
    ]
    for nd in nodes[:3]:
        p1 += [('node', nd), ('rule', G70, 1), ('space', 6)]

    # Page 2 — nodes N-04/05/06
    p2 = header_block(2) + [
        ('h1',   'Node Assessments  —  continued'),
        ('rule', G70, 1),
        ('space', 10),
    ]
    for nd in nodes[3:]:
        p2 += [('node', nd), ('rule', G70, 1), ('space', 6)]

    # Page 3 — summary / scenarios / synthesis
    p3 = header_block(3) + [
        ('h1',   'Node Strength Summary'),
        ('rule', G70, 1),
        ('space', 10),
        ('summary',   nodes, composite),
        ('space', 10),
        ('rule',  WHITE, 1),
        ('h1',   'Scenario Matrix  —  36-Month Horizon'),
        ('rule', G70, 1),
        ('space', 10),
        ('scenarios', scenarios),
        ('space', 10),
        ('rule',  WHITE, 1),
        ('h1',   'Synthesis'),
        ('rule', G70, 1),
        ('space', 12),
        ('synthesis', synthesis),
        ('meta', f"Master node: {master}    {ref}"),
    ]

    return [p1, p2, p3]


# ── Entry point ────────────────────────────────────────────────────────────────
def render_report_images(data, run_dir):
    run_dir = Path(run_dir)
    pages   = build_pages(data)
    paths   = []
    for i, pg in enumerate(pages, 1):
        out = run_dir / f"page_{i}.jpg"
        render_page(pg, i, 3, out)
        paths.append(out)
    return paths


# ── Markov graph ───────────────────────────────────────────────────────────────
def render_markov_graph(data, run_dir):
    """
    Brand-compliant node graph.
    - Pure #0A0A0A background
    - Liberation Sans throughout (no monospace)
    - Spiral + wordmark header
    - White solid bars on nodes, brightness-scaled borders
    - Double border on COMPOSITE
    - White arrows node→composite, dark-grey dashed inter-node
    - No footer
    """
    run_dir = Path(run_dir)

    nodes     = data['nodes']
    subject   = data['subject']
    ref       = data['ref']
    ts        = data['timestamp'][:10]
    composite = data['composite_score']
    n_val     = data.get('cycle_number', 0)
    cyc       = f"INTER//CYCLE {str(n_val).zfill(6)}"

    plt.rcParams.update({
        'font.family':   'Liberation Sans',
        'text.color':    'white',
        'figure.facecolor': '#0A0A0A',
    })

    FIG_W, FIG_H = 24, 19
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    fig.patch.set_facecolor('#0A0A0A')

    # ── Header bar: spiral + wordmark ─────────────────────────────────────────
    HEADER_FRAC = 0.072
    SUB_FRAC    = 0.044
    GRAPH_BOT   = 0.055
    GRAPH_TOP   = 1.0 - HEADER_FRAC - SUB_FRAC

    if SPIRAL_PATH.exists():
        sp_ax = fig.add_axes([0.025, 1.0 - HEADER_FRAC + 0.005,
                              0.046, HEADER_FRAC - 0.010])
        sp_ax.imshow(np.array(Image.open(str(SPIRAL_PATH)).convert('RGB')),
                     aspect='auto', interpolation='lanczos')
        sp_ax.axis('off')

    fig.text(0.083, 1.0 - HEADER_FRAC * 0.36, "Interstitial",
             fontsize=19, fontweight='bold', color='white',
             fontfamily='Liberation Sans', va='center')
    fig.text(0.083, 1.0 - HEADER_FRAC * 0.76, "MEASURING THE FUTURE",
             fontsize=7.5, color='#808080',
             fontfamily='Liberation Sans', va='center')

    # White rule under header
    rule_y = 1.0 - HEADER_FRAC
    fig.add_artist(plt.Line2D(
        [0.025, 0.975], [rule_y, rule_y],
        transform=fig.transFigure,
        color='white', linewidth=0.7, zorder=10))

    # Subject + cycle metadata — strip directly below rule
    sub_mid  = rule_y - SUB_FRAC * 0.32
    meta_mid = rule_y - SUB_FRAC * 0.72
    fig.text(0.50, sub_mid, subject.upper(),
             fontsize=12, fontweight='bold', color='white',
             ha='center', fontfamily='Liberation Sans')
    fig.text(0.50, meta_mid, f"{ref}    {ts}    {cyc}",
             fontsize=7.5, color='#808080',
             ha='center', fontfamily='Liberation Sans')

    # Dim rule separating header from graph
    fig.add_artist(plt.Line2D(
        [0.025, 0.975], [GRAPH_TOP, GRAPH_TOP],
        transform=fig.transFigure,
        color='#2A2A2A', linewidth=0.5, zorder=10))

    # ── Graph axes ─────────────────────────────────────────────────────────────
    ax = fig.add_axes([0.025, GRAPH_BOT, 0.95, GRAPH_TOP - GRAPH_BOT])
    ax.set_facecolor('#0A0A0A')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Node ring layout
    cx, cy   = 5.0, 5.3
    radius   = 3.15
    angles   = [90, 30, 330, 270, 210, 150]
    NODE_W   = 1.80
    NODE_H   = 1.20

    positions = {}
    for i, nd in enumerate(nodes):
        a = np.radians(angles[i])
        positions[nd['id']] = (cx + radius * np.cos(a),
                               cy + radius * np.sin(a))
    positions['COMPOSITE'] = (cx, cy)

    # ── Draw node box ──────────────────────────────────────────────────────────
    def draw_node(key, nd_data, is_comp=False):
        x, y   = positions[key]
        pct    = nd_data.get('score', composite)
        name   = nd_data.get('name', key)
        gc     = sg_f(pct)
        lw     = 2.0 if is_comp else 1.2

        if is_comp:
            # Outer border (double border effect)
            ax.add_patch(mpatches.FancyBboxPatch(
                (x - NODE_W/2 - 0.14, y - NODE_H/2 - 0.14),
                NODE_W + 0.28, NODE_H + 0.28,
                boxstyle="square,pad=0", linewidth=0.9,
                edgecolor=(0.40, 0.40, 0.40), facecolor='#0A0A0A'))

        ax.add_patch(mpatches.FancyBboxPatch(
            (x - NODE_W/2, y - NODE_H/2), NODE_W, NODE_H,
            boxstyle="square,pad=0", linewidth=lw,
            edgecolor=gc, facecolor='#0A0A0A'))

        if is_comp:
            ax.text(x, y + 0.17, "COMPOSITE",
                    ha='center', va='center',
                    fontsize=11, fontweight='bold', color='white',
                    fontfamily='Liberation Sans')
            ax.text(x, y - 0.12, f"{composite}%",
                    ha='center', va='center',
                    fontsize=18, fontweight='bold', color='white',
                    fontfamily='Liberation Sans')
        else:
            # Node ID bold, name regular
            ax.text(x, y + 0.34, key,
                    ha='center', va='center',
                    fontsize=9, fontweight='bold', color='white',
                    fontfamily='Liberation Sans')
            short = name[:18] if len(name) > 18 else name
            ax.text(x, y + 0.14, short,
                    ha='center', va='center',
                    fontsize=7.5, color=gc,
                    fontfamily='Liberation Sans')

            # Score bar — solid fill, brightness-scaled
            bx      = x - NODE_W/2 + 0.08
            by      = y - NODE_H/2 + 0.09
            bw_full = NODE_W - 0.16
            bw_fill = bw_full * (pct / 100)
            ax.add_patch(mpatches.Rectangle(
                (bx, by), bw_full, 0.13, color=(0.11, 0.11, 0.11)))
            ax.add_patch(mpatches.Rectangle(
                (bx, by), bw_fill, 0.13, color=gc))
            ax.text(x, by + 0.065, f"{pct}%",
                    ha='center', va='center',
                    fontsize=7, color='white',
                    fontfamily='Liberation Sans')

    # Inter-node edges — dashed dark grey
    edge_pairs = [
        (nodes[0]['id'], nodes[1]['id']),
        (nodes[1]['id'], nodes[2]['id']),
        (nodes[2]['id'], nodes[3]['id']),
        (nodes[3]['id'], nodes[4]['id']),
        (nodes[4]['id'], nodes[5]['id']),
        (nodes[5]['id'], nodes[0]['id']),
        (nodes[0]['id'], nodes[3]['id']),
        (nodes[1]['id'], nodes[4]['id']),
    ]
    for f_id, t_id in edge_pairs:
        x0, y0 = positions[f_id]
        x1, y1 = positions[t_id]
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(
                        arrowstyle='->', color='#303030',
                        lw=0.8, linestyle='--',
                        connectionstyle='arc3,rad=0.13',
                        shrinkA=46, shrinkB=46))

    # Node → Composite edges — solid white
    weights = data.get('nodes_edge_weights', {})
    for nd in nodes:
        x0, y0 = positions[nd['id']]
        x1, y1 = positions['COMPOSITE']
        w = weights.get(nd['id'], 0.17)
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(
                        arrowstyle='->', color='white',
                        lw=1.1,
                        connectionstyle='arc3,rad=0.05',
                        shrinkA=46, shrinkB=52))
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        ax.text(mx, my, f"{w:.2f}",
                ha='center', va='center',
                fontsize=5.5, color='#4D4D4D',
                fontfamily='Liberation Sans',
                bbox=dict(boxstyle='square,pad=0.1',
                          fc='#0A0A0A', ec='none'))

    # Draw all nodes
    for nd in nodes:
        draw_node(nd['id'], nd)
    draw_node('COMPOSITE', {'score': composite, 'name': 'COMPOSITE'}, is_comp=True)

    # ── Legend ─────────────────────────────────────────────────────────────────
    lx, ly = 0.30, 0.50
    ax.plot([lx, lx + 0.30], [ly + 0.20, ly + 0.20],
            color='white', lw=0.9)
    ax.annotate('', xy=(lx + 0.30, ly + 0.20), xytext=(lx, ly + 0.20),
                arrowprops=dict(arrowstyle='->', color='white', lw=0.9))
    ax.text(lx + 0.38, ly + 0.20, 'Node  →  Composite  (weighted)',
            fontsize=6.5, color='#808080', va='center',
            fontfamily='Liberation Sans')
    ax.plot([lx, lx + 0.30], [ly + 0.04, ly + 0.04],
            color='#303030', lw=0.8, linestyle='--')
    ax.text(lx + 0.38, ly + 0.04, 'Inter-node dependency',
            fontsize=6.5, color='#4D4D4D', va='center',
            fontfamily='Liberation Sans')

    out = run_dir / "markov_graph.jpg"
    plt.savefig(str(out), dpi=200, bbox_inches='tight',
                facecolor='#0A0A0A', edgecolor='none')
    plt.close()
    return out
