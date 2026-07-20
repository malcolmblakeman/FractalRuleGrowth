import streamlit as st
import random
import colorsys
import math
from PIL import Image, ImageDraw, ImageSequence
import io
import base64
import tempfile
import os

# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

DEFAULT_COLORS = {
    1: (230, 0, 140),
    2: (0, 180, 255),
    3: (180, 255, 0),
    4: (128, 0, 255),
    5: (128, 128, 128),
}

CELL = 12
MARGIN = 4

SHAPE_ICONS = {
    "Triangle": "🔺",
    "Octagon": "🛑",
    "Square": "⬜",
    "Hexagon": "⬣",
}

# ══════════════════════════════════════════════════════════════════════════════
#  CORE LOGIC
# ══════════════════════════════════════════════════════════════════════════════

def parse_rule(rule_string):
    n = int(len(rule_string) ** 0.5)
    if n * n != len(rule_string):
        raise ValueError("Rule string length must be a perfect square.")
    rules = {}
    index = 0
    for a in range(1, n + 1):
        for b in range(1, n + 1):
            rules[(a, b)] = int(rule_string[index])
            index += 1
    return rules, n


def random_rule(num_colors):
    length = num_colors * num_colors
    return "".join(str(random.randint(1, num_colors)) for _ in range(length))


def apply_rule(rules, a, b, sym=False):
    if sym and b > a:
        a, b = b, a
    return rules[(a, b)]


# ══════════════════════════════════════════════════════════════════════════════
#  GENERATE FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def generate_triangle(rule_string, num_lines, boundary=1, random_scale=0, wait_until=0, sym=False):
    rules, n = parse_rule(rule_string)
    rows = [[1]]
    while len(rows) < num_lines:
        prev = rows[-1]
        if boundary == -1:
            edge = random.randint(1, n)
        elif boundary == 0:
            edge = ((len(rows) - 1) % n) + 1
        else:
            edge = boundary
        new_row = [edge]
        for i in range(len(prev) - 1):
            if random_scale != 0:
                if random.random() < random_scale and len(rows) > wait_until:
                    new_row.append(random.randint(1, n))
                else:
                    new_row.append(apply_rule(rules, prev[i], prev[i + 1], sym))
            else:
                new_row.append(apply_rule(rules, prev[i], prev[i + 1], sym))
        new_row.append(edge)
        rows.append(new_row)
    return rows


def generate_square(rule_string, generations, boundary=1, random_scale=0, wait_until=0, sym=False):
    rules, n = parse_rule(rule_string)

    def add_cross(board, radius, gen):
        if boundary == -1:
            edge = random.randint(1, n)
        elif boundary == 0:
            edge = ((gen - 1) % n) + 1
        else:
            edge = boundary
        board[(0, -radius)] = edge
        board[(0, radius)] = edge
        board[(-radius, 0)] = edge
        board[(radius, 0)] = edge

    def fill_ring(board, radius, gen):
        changed = True
        while changed:
            changed = False
            for y in range(-radius, radius + 1):
                for x in range(-radius, radius + 1):
                    if (x, y) in board:
                        continue
                    neighbors = []
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        p = (x + dx, y + dy)
                        if p in board:
                            neighbors.append(board[p])
                    if len(neighbors) == 2:
                        if random_scale != 0:
                            if random.random() < random_scale and gen > wait_until:
                                board[(x, y)] = random.randint(1, n)
                            else:
                                board[(x, y)] = apply_rule(rules, neighbors[0], neighbors[1], sym)
                        else:
                            board[(x, y)] = apply_rule(rules, neighbors[0], neighbors[1], sym)
                        changed = True

    if boundary == -1:
        center = random.randint(1, n)
    elif boundary == 0:
        center = 1
    else:
        center = boundary
    board = {(0, 0): center}
    radius = 0
    for gen in range(generations):
        radius += 1
        add_cross(board, radius, gen)
        fill_ring(board, radius, gen)

    rows = [
        [board[(x, y)] for x in range(-radius, radius + 1)]
        for y in range(-radius, radius + 1)
    ]
    return rows


def generate_square_history(rule_string, generations, boundary=1, random_scale=0, wait_until=0, sym=False):
    rules, n = parse_rule(rule_string)
    history = []

    def add_cross(board, radius, gen):
        if boundary == -1:
            edge = random.randint(1, n)
        elif boundary == 0:
            edge = ((gen - 1) % n) + 1
        else:
            edge = boundary
        board[(0, -radius)] = edge
        board[(0, radius)] = edge
        board[(-radius, 0)] = edge
        board[(radius, 0)] = edge

    def fill_ring(board, radius, gen):
        changed = True
        while changed:
            changed = False
            for y in range(-radius, radius + 1):
                for x in range(-radius, radius + 1):
                    if (x, y) in board:
                        continue
                    neighbors = []
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        p = (x + dx, y + dy)
                        if p in board:
                            neighbors.append(board[p])
                    if len(neighbors) == 2:
                        if random_scale != 0:
                            if random.random() < random_scale and gen > wait_until:
                                board[(x, y)] = random.randint(1, n)
                            else:
                                board[(x, y)] = apply_rule(rules, neighbors[0], neighbors[1], sym)
                        else:
                            board[(x, y)] = apply_rule(rules, neighbors[0], neighbors[1], sym)
                        changed = True

    if boundary == -1:
        center = random.randint(1, n)
    elif boundary == 0:
        center = 1
    else:
        center = boundary
    board = {(0, 0): center}
    radius = 0
    for gen in range(generations):
        radius += 1
        add_cross(board, radius, gen)
        fill_ring(board, radius, gen)
        rows = [
            [board[(x, y)] for x in range(-radius, radius + 1)]
            for y in range(-radius, radius + 1)
        ]
        history.append(rows)
    return history


def generate_hex(rule_string, generations, boundary=1, order=0, random_scale=0, wait_until=0, sym=False):
    def hex_ring(radius):
        if radius == 0:
            return [(0, 0)]
        results = []
        q, r = 0, -radius
        directions = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
        for dq, dr in directions:
            for _ in range(radius):
                results.append((q, r))
                q += dq
                r += dr
        return results

    def add_outer_points(board, radius, n, boundary=1, order=1):
        ring = hex_ring(radius)
        if order == -1:
            points = ring[::2] if random.randint(0, 1) == 0 else ring[1::2]
        elif order == 0:
            points = ring[::2] if radius % 2 == 0 else ring[1::2]
        elif order == 1:
            points = ring[::2]
        elif order == 2:
            points = ring[1::2]
        else:
            points = ring[::2]
        for p in points:
            if boundary == -1:
                edge = random.randint(1, n)
            elif boundary == 0:
                edge = ((radius - 1) % n) + 1
            else:
                edge = boundary
            board[p] = edge

    def hex_distance(q, r):
        return max(abs(q), abs(r), abs(q + r))

    def hex_neighbors(q, r):
        return [(q+1, r), (q-1, r), (q, r+1), (q, r-1), (q+1, r-1), (q-1, r+1)]

    def fill_ring(board, radius, rules, n, sym=True, random_scale=0, wait_until=0):
        changed = True
        while changed:
            changed = False
            for q in range(-radius, radius + 1):
                for r in range(-radius, radius + 1):
                    if (q, r) in board:
                        continue
                    if hex_distance(q, r) > radius:
                        continue
                    touching = []
                    for nb in hex_neighbors(q, r):
                        if nb in board:
                            touching.append((hex_distance(*nb), board[nb]))
                    touching.sort(key=lambda x: x[0], reverse=False)
                    touching = [color for _, color in touching]
                    if len(touching) >= 2:
                        if random_scale != 0:
                            if random.random() < random_scale and radius > wait_until:
                                board[(q, r)] = random.randint(1, n)
                            else:
                                board[(q, r)] = apply_rule(rules, touching[0], touching[1], sym)
                        else:
                            board[(q, r)] = apply_rule(rules, touching[0], touching[1], sym)
                        changed = True

    rules, n = parse_rule(rule_string)
    if boundary == -1:
        center = random.randint(1, n)
    elif boundary == 0:
        center = 1
    else:
        center = boundary
    board = {(0, 0): center}

    for gen in range(generations):
        radius = gen + 1
        add_outer_points(board, radius, n, boundary, order)
        fill_ring(board, radius, rules, n, sym, random_scale, wait_until)

    return board


# ══════════════════════════════════════════════════════════════════════════════
#  DRAW FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def draw_triangle(rows, colors=None, rainbow=False, cell=CELL, margin=MARGIN):
    if colors is None:
        colors = DEFAULT_COLORS
    max_width = len(rows[-1])
    width = max_width * cell + 2 * margin
    height = len(rows) * cell + 2 * margin
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for y, row in enumerate(rows):
        x0 = ((max_width - len(row)) * cell) // 2 + margin
        for x, value in enumerate(row):
            left = x0 + x * cell
            top = y * cell + margin
            fill = colors.get(value, (200, 200, 200))
            if rainbow:
                r, g, b = fill
                r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
                h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)
                new_h = (h + (180.0 * (50 - y % 100 + 50) / 100.0 / 360.0)) % 1.0
                nr, ng, nb = colorsys.hls_to_rgb(new_h, l, s)
                fill = (int(nr * 255), int(ng * 255), int(nb * 255))
            draw.rectangle([left, top, left + cell - 1, top + cell - 1], fill=fill)
    return img


def make_pattern_octagon(rows, colors=None, rainbow=False):
    tri = draw_triangle(rows, colors=colors, rainbow=rainbow)
    S = tri.width
    canvas = Image.new("RGBA", (2 * S - 1, 2 * S - 1), (0, 0, 0, 0))

    tb = Image.new("RGBA", (S, 2 * S - 1), (0, 0, 0, 0))
    tb.paste(tri.rotate(180), (0, 0))
    tb.paste(tri, (0, S - 1))

    lr = Image.new("RGBA", (2 * S - 1, S), (0, 0, 0, 0))
    lr.paste(tri.rotate(270), (0, 0))
    lr.paste(tri.rotate(90), (S - 1, 0))

    canvas.alpha_composite(tb, ((canvas.width - S) // 2, 0))
    canvas.alpha_composite(lr, (0, (canvas.height - S) // 2))

    cross = canvas.copy()
    scale = 1.07
    cross = cross.resize(
        (int(cross.width * scale), int(cross.height * scale)),
        Image.Resampling.LANCZOS,
    )
    overlay = cross.rotate(45, expand=True)

    pixels_base = canvas.load()
    pixels_overlay = overlay.load()
    dx = (canvas.width - overlay.width) // 2
    dy = (canvas.height - overlay.height) // 2

    for oy in range(overlay.height):
        by = oy + dy
        if not (0 <= by < canvas.height):
            continue
        for ox in range(overlay.width):
            bx = ox + dx
            if not (0 <= bx < canvas.width):
                continue
            if pixels_base[bx, by][3] == 0 and pixels_overlay[ox, oy][3] != 0:
                pixels_base[bx, by] = pixels_overlay[ox, oy]

    return canvas


def draw_square(rows, colors=None, rainbow=False, cell=CELL, margin=MARGIN):
    if colors is None:
        colors = DEFAULT_COLORS
    height_cells = len(rows)
    width_cells = len(rows[0])
    width = width_cells * cell + 2 * margin
    height = height_cells * cell + 2 * margin
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for y, row in enumerate(rows):
        for x, value in enumerate(row):
            left = x * cell + margin
            top = y * cell + margin
            fill = colors.get(value, (200, 200, 200))
            if rainbow:
                r, g, b = fill
                r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
                h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)
                cx = (width_cells - 1) / 2
                cy = (height_cells - 1) / 2
                rad = math.hypot(x - cx, y - cy)
                new_h = (h + (180.0 * (0 - abs(rad) % 80 + 0) / 40.0 / 360.0)) % 1.0
                nr, ng, nb = colorsys.hls_to_rgb(new_h, l, s)
                fill = (int(nr * 255), int(ng * 255), int(nb * 255))
            draw.rectangle([left, top, left + cell - 1, top + cell - 1], fill=fill)
    return img


def draw_hex(board, colors=None, size=25, rainbow=False):
    if colors is None:
        colors = DEFAULT_COLORS

    def hex_distance(q, r):
        return max(abs(q), abs(r), abs(q + r))

    def hex_to_pixel(q, r, sz):
        x = sz * math.sqrt(3) * (q + r / 2)
        y = sz * 1.5 * r
        return x, y

    coords = [hex_to_pixel(q, r, size) for q, r in board]
    minx = min(x for x, y in coords)
    maxx = max(x for x, y in coords)
    miny = min(y for x, y in coords)
    maxy = max(y for x, y in coords)

    img = Image.new("RGBA", (int(maxx - minx + 120), int(maxy - miny + 120)), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    for (q, r), value in board.items():
        x, y = hex_to_pixel(q, r, size)
        x -= minx - 60
        y -= miny - 60
        fill = colors.get(value, (200, 200, 200))
        if rainbow:
            dis = hex_distance(q, r)
            rc, gc, bc = fill
            r_n, g_n, b_n = rc / 255.0, gc / 255.0, bc / 255.0
            h, l, s = colorsys.rgb_to_hls(r_n, g_n, b_n)
            new_h = (h + (180.0 * (40 - abs(dis) % 80 + 40) / 40 / 360.0)) % 1.0
            nr, ng, nb = colorsys.hls_to_rgb(new_h, l, s)
            fill = (int(nr * 255), int(ng * 255), int(nb * 255))

        pts = []
        for i in range(6):
            angle = math.radians(60 * i + 30)
            pts.append((x + size * math.cos(angle), y + size * math.sin(angle)))
        draw.polygon(pts, fill=fill, outline=(20, 20, 20))

    return img


# ══════════════════════════════════════════════════════════════════════════════
#  ANIMATE FUNCTIONS (return temp file path)
# ══════════════════════════════════════════════════════════════════════════════

def animate_gif_tri(rule, colors=None, boundary=1, random_scale=0, wait_until=0, sym=False, rainbow=False,
                    filename="triangle.gif", start_rows=10, end_rows=100, duration=50, loop=0, zoomout=False):
    if colors is None:
        colors = DEFAULT_COLORS
    rows = generate_triangle(rule, num_lines=end_rows, boundary=boundary, random_scale=random_scale, wait_until=wait_until, sym=sym)
    final_img = draw_triangle(rows[:end_rows], colors=colors)
    final_w, final_h = final_img.size
    frames = []
    for n in range(start_rows, end_rows + 1):
        img = draw_triangle(rows[:n], colors=colors, rainbow=rainbow)
        canvas = Image.new("RGBA", (final_w, final_h), (0, 0, 0, 0))
        canvas.alpha_composite(img, ((final_w - img.width) // 2, 0))
        if zoomout:
            img = img.resize((final_w, final_h), Image.Resampling.NEAREST)
            canvas = img
        frames.append(canvas.convert("P", palette=Image.ADAPTIVE))
    durations = [duration] * len(frames)
    durations[-1] = 500
    frames[0].save(filename, save_all=True, append_images=frames[1:], duration=durations, loop=loop, optimize=False, disposal=2)
    return filename


def animate_gif_oct(rule, colors=None, boundary=1, random_scale=0, wait_until=0, sym=False, rainbow=False,
                    filename="octagon.gif", start_rows=1, end_rows=50, duration=50, loop=0, zoomout=False, angdur=0):
    if colors is None:
        colors = DEFAULT_COLORS
    rows = generate_triangle(rule, num_lines=end_rows, boundary=boundary, random_scale=random_scale, wait_until=wait_until, sym=sym)
    final_img = make_pattern_octagon(rows[:end_rows], colors=colors, rainbow=rainbow)
    final_w, final_h = final_img.size
    frames = []
    for n in range(start_rows, end_rows + 1):
        img = make_pattern_octagon(rows[:n], colors=colors, rainbow=rainbow)
        canvas = Image.new("RGBA", (final_w, final_h), (0, 0, 0, 0))
        canvas.alpha_composite(img, ((final_w - img.width) // 2, (final_h - img.height) // 2))
        if zoomout:
            img = img.resize((final_w, final_h), Image.Resampling.NEAREST)
            canvas = img
        if angdur > 0:
            frame_idx = n - start_rows
            canvas = canvas.rotate((180.0 / angdur) * frame_idx, expand=False)
        frames.append(canvas.convert("P", palette=Image.ADAPTIVE))
    durations = [duration] * len(frames)
    durations[-1] = 500
    frames[0].save(filename, save_all=True, append_images=frames[1:], duration=durations, loop=loop, optimize=False, disposal=2)
    return filename


def animate_gif_sq(rule, colors=None, boundary=1, random_scale=0, wait_until=0, sym=False, rainbow=False,
                   filename="square.gif", start_rows=10, end_rows=100, duration=50, loop=0, zoomout=False):
    if colors is None:
        colors = DEFAULT_COLORS
    his = generate_square_history(rule, generations=end_rows, boundary=boundary, random_scale=random_scale, wait_until=wait_until, sym=sym)
    final_img = draw_square(his[-1], colors=colors, rainbow=rainbow)
    final_w, final_h = final_img.size
    frames = []
    for n in range(start_rows, end_rows + 1):
        img = draw_square(his[n - 1], colors=colors, rainbow=rainbow)
        if zoomout:
            img = img.resize((final_w, final_h), Image.Resampling.NEAREST)
            canvas = img
        else:
            canvas = Image.new("RGBA", (final_w, final_h), (0, 0, 0, 0))
            canvas.alpha_composite(img, ((final_w - img.width) // 2, (final_h - img.height) // 2))
        frames.append(canvas.convert("P", palette=Image.ADAPTIVE))
    durations = [duration] * len(frames)
    durations[-1] = 500
    frames[0].save(filename, save_all=True, append_images=frames[1:], duration=durations, loop=loop, optimize=False, disposal=2)
    return filename


def animate_gif_hex(rule, colors=None, boundary=0, order=-1, random_scale=0, wait_until=0, sym=False, rainbow=False,
                    filename="hexagon.gif", start_gen=1, end_gen=10, duration=50, loop=0, zoomout=False):
    if colors is None:
        colors = DEFAULT_COLORS
    board = generate_hex(rule, generations=end_gen, boundary=boundary, order=order, random_scale=random_scale, wait_until=wait_until, sym=sym)
    items = list(board.items())
    final_img = draw_hex(board, colors=colors, rainbow=rainbow)
    final_w, final_h = final_img.size
    frames = []
    for gen in range(start_gen, end_gen + 1):
        count = 1 + 3 * gen * (gen + 1)
        partial = dict(items[:count])
        img = draw_hex(partial, colors=colors, rainbow=rainbow)
        if zoomout:
            img = img.resize((final_w, final_h), Image.Resampling.NEAREST)
            canvas = img
        else:
            canvas = Image.new("RGBA", (final_w, final_h), (0, 0, 0, 0))
            canvas.alpha_composite(img, ((final_w - img.width) // 2, (final_h - img.height) // 2))
        frames.append(canvas.convert("P", palette=Image.ADAPTIVE))
    durations = [duration] * len(frames)
    durations[-1] = 500
    frames[0].save(filename, save_all=True, append_images=frames[1:], duration=durations, loop=loop, optimize=False, disposal=2)
    return filename


# ══════════════════════════════════════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def color_svg(hex_color, size=24):
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
        <rect x="1" y="1" width="{size-2}" height="{size-2}" rx="3" fill="{hex_color}" stroke="#555" stroke-width="2"/>
    </svg>
    """


def draw_rule_table(rules, n, colors, cell=48):
    width = n * cell + 2 * cell
    height = (n + 1) * cell + 2 * cell
    img = Image.new("RGB", (width, height), (30, 30, 30))
    draw = ImageDraw.Draw(img)
    for i in range(1, n + 1):
        cx = cell + (i - 1) * cell + cell // 2
        cy = cell // 2
        draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=colors[i])
        cx2 = cell // 2
        cy2 = cell + (i - 1) * cell + cell // 2
        draw.ellipse([cx2 - 14, cy2 - 14, cx2 + 14, cy2 + 14], fill=colors[i])
    for a in range(1, n + 1):
        for b in range(1, n + 1):
            val = rules[(a, b)]
            left = cell + (b - 1) * cell
            top = cell + (a - 1) * cell
            draw.rectangle([left, top, left + cell - 1, top + cell - 1], fill=colors[val])
            draw.rectangle([left, top, left + cell - 1, top + cell - 1], outline=(60, 60, 60))
    return img


def get_download_link(img, filename, label, format="PNG"):
    buf = io.BytesIO()
    if format.upper() == "PNG":
        img.save(buf, format="PNG")
        mime = "image/png"
    else:
        img.save(buf, format="GIF")
        mime = "image/gif"
    b64 = base64.b64encode(buf.getvalue()).decode()
    href = f'<a href="data:{mime};base64,{b64}" download="{filename}" style="display:inline-block;padding:0.5em 1em;background:#4CAF50;color:white;text-decoration:none;border-radius:6px;font-weight:500;">{label}</a>'
    return href


def get_file_download_link(file_path, filename, label):
    with open(file_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    href = f'<a href="data:image/gif;base64,{b64}" download="{filename}" style="display:inline-block;padding:0.5em 1em;background:#2196F3;color:white;text-decoration:none;border-radius:6px;font-weight:500;">{label}</a>'
    return href


# ══════════════════════════════════════════════════════════════════════════════
#  VISUAL RULE EDITOR
# ══════════════════════════════════════════════════════════════════════════════

def visual_rule_editor(num_colors):

    st.subheader("🎨 Visual Rule Editor")

    # CSS for unified group border
    st.markdown(
        """
        <style>
        .rule-input-box {
            border: 1.5px dashed #777;
            border-radius: 8px;
            padding: 8px 4px;
            margin-bottom: 4px;
            background: rgba(240, 240, 255, 0.5);
        }
        .rule-output-box {
            border: 1.5px dashed #777;
            border-radius: 8px;
            padding: 6px 4px;
            background: rgba(240, 255, 240, 0.5);
        }
        .rule-arrow {
            text-align: center;
            color: #888;
            font-size: 12px;
            margin: 2px 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    colors = {
        i: st.session_state.colors[i]
        for i in range(1, num_colors + 1)
    }

    rule = list(st.session_state.rule_string)

    idx = 0

    for a in range(1, num_colors + 1):

        cols = st.columns([1]*num_colors, gap="small")

        for b in range(1, num_colors + 1):

            current = int(rule[idx])

            with cols[b-1]:

                # Input pair with dashed border
                st.markdown(
                    f"""
                    <div class="rule-input-box">
                        <div style="display:flex; justify-content:center; gap:2px;">
                            {color_svg(colors[a])}
                            {color_svg(colors[b])}
                    """,
                    unsafe_allow_html=True
                )

                # Arrow separator
                st.markdown('<div class="rule-arrow">↓</div>', unsafe_allow_html=True)

                

                choice_cols = st.columns([1]*num_colors, gap="small")

                for c in range(1, num_colors + 1):

                    with choice_cols[c-1]:

                        st.markdown(
                            color_svg(colors[c], 32),
                            unsafe_allow_html=True
                        )

                        if c == current:
                            label = "⬤"
                        else:
                            label = "○"

                        if st.button(
                            label,
                            key=f"rule_{idx}_{c}",
                            help=f"Set result to color {c}",
                        ):
                            rule[idx] = str(c)
                            st.session_state.rule_string = "".join(rule)
                            st.rerun()

            idx += 1

    st.code(st.session_state.rule_string)


# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════

def init_state():
    defaults = {
        "mode": "Triangle",
        "num_colors": 3,
        "rule_string": "213132321",
        "rule_source": "Random",
        "boundary_mode": "Fixed (1)",
        "rainbow": False,
        "sym": False,
        "random_scale": 0.0,
        "wait_until": 0,
        # Pattern size
        "tri_lines": 40,
        "sq_generations": 15,
        "hex_generations": 8,
        "hex_order": 0,
        # Animation
        "anim_start": 1,
        "anim_end": 50,
        "anim_duration": 50,
        "anim_zoomout": False,
        "oct_angdur": 0,
        # Colors
        "colors": {k: rgb_to_hex(v) for k, v in DEFAULT_COLORS.items()},
        # Cached images
        "last_image": None,
        "last_gif_path": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

def sidebar():
    st.sidebar.title("⚙️ Controls")

    modes = ["Triangle", "Octagon", "Square", "Hexagon"]

    selected_mode = st.sidebar.selectbox(
        "Shape",
        modes,
        index=modes.index(st.session_state.mode),
        format_func=lambda x: f"{SHAPE_ICONS[x]} {x}",
    )

    # Update session state only when selection changes
    if selected_mode != st.session_state.mode:
        st.session_state.mode = selected_mode
        st.session_state.last_image = None
        st.session_state.last_gif_path = None
        st.rerun()

    st.sidebar.markdown("---")

    # Colors
    nc = st.sidebar.selectbox("Number of Colors", [2, 3, 4, 5], index=1,
                              on_change=lambda: _on_colors_changed())
    st.session_state.num_colors = nc

    # Rule source
    rule_src = st.sidebar.radio("Rule Source", ["Random", "Custom"], horizontal=True,
                                on_change=lambda: _on_rule_source_changed())
    st.session_state.rule_source = rule_src

    if rule_src == "Custom":
        length = nc * nc
        rule = st.sidebar.text_input(
            f"Rule string ({length} digits)",
            value=st.session_state.rule_string[:length],
            max_chars=length,
            key="rule_input"
        )
        if len(rule) == length and st.session_state.rule_string != rule:
            st.session_state.rule_string = rule
            st.session_state.last_image = None
    else:
        if st.sidebar.button("🎲 New Random Rule", use_container_width=True):
            st.session_state.rule_string = random_rule(nc)
            st.session_state.last_image = None
            request_generate()
            #st.rerun()

    st.sidebar.markdown("---")

    # Pattern settings
    st.sidebar.subheader("📐 Pattern Settings")
    bnd = st.sidebar.selectbox("Boundary", ["Fixed (1)", "Cyclic", "Random"], index=0, on_change=request_generate)
    st.session_state.boundary_mode = bnd
    st.session_state.rainbow = st.sidebar.checkbox("🌈 Rainbow Mode")
    st.session_state.sym = st.sidebar.checkbox("🔄 Symmetric Rule")

    mode = st.session_state.mode
    if mode in ["Triangle", "Octagon"]:
        st.session_state.tri_lines = st.sidebar.slider("Lines", 5, 150, st.session_state.tri_lines, on_change=request_generate)
    elif mode == "Square":
        st.session_state.sq_generations = st.sidebar.slider("Generations", 3, 40, st.session_state.sq_generations, on_change=request_generate)
    elif mode == "Hexagon":
        st.session_state.hex_generations = st.sidebar.slider("Generations", 2, 25, st.session_state.hex_generations, on_change=request_generate)
        order_labels = {"-1": "Random", "0": "Alternate", "1": "Pattern A", "2": "Pattern B"}
        order_val = st.sidebar.selectbox("Hex Order", ["-1", "0", "1", "2"], index=1,
                                         format_func=lambda x: order_labels[x], on_change=request_generate)
        st.session_state.hex_order = int(order_val)

    # Advanced
    st.sidebar.markdown("---")
    with st.sidebar.expander("⚙️ Advanced"):
        st.session_state.random_scale = st.slider("Random Scale", 0.0, 1.0,st.session_state.random_scale, step=0.05)
        st.session_state.wait_until = st.slider("Wait Until", 0, 50, st.session_state.wait_until)

    st.sidebar.markdown("---")

    # Animation settings
    with st.sidebar.expander("🎬 Animation Settings"):
        if mode in ["Triangle", "Octagon"]:
            st.session_state.anim_start = st.slider("Start Row", 1, 100, min(st.session_state.anim_start, 100), key="anim_start_sl")
            st.session_state.anim_end = st.slider("End Row", 5, 150, max(st.session_state.anim_end, 5), key="anim_end_sl")
        elif mode == "Square":
            st.session_state.anim_start = st.slider("Start Gen", 1, 30, min(st.session_state.anim_start, 30), key="anim_start_sq")
            st.session_state.anim_end = st.slider("End Gen", 3, 40, max(st.session_state.anim_end, 3), key="anim_end_sq")
        elif mode == "Hexagon":
            st.session_state.anim_start = st.slider("Start Gen", 1, 20, min(st.session_state.anim_start, 20), key="anim_start_hex")
            st.session_state.anim_end = st.slider("End Gen", 2, 25, max(st.session_state.anim_end, 2), key="anim_end_hex")


        st.session_state.anim_duration = st.slider("Frame Duration (ms)", 10, 200, st.session_state.anim_duration, key="anim_dur")
        st.session_state.anim_zoomout = st.checkbox("🔍 Zoom Out", value=st.session_state.anim_zoomout, key="anim_zoom")

        if mode == "Octagon":
            st.session_state.oct_angdur = st.slider("Rotation Speed", 0, 100, st.session_state.oct_angdur, key="oct_ang")

    st.sidebar.markdown("---")

    # Color palette
    with st.sidebar.expander("🎨 Color Palette"):
        def random_hex_color():
            return "#{:06x}".format(random.randint(0, 0xFFFFFF))
        def randomize_colors():
            for i in range(1, nc + 1):
                color = random_hex_color()
                st.session_state.colors[i] = color
                st.session_state[f"color_{i}"] = color
            request_generate()

        for i in range(1, nc + 1):
            st.session_state.colors[i] = st.color_picker(
                f"Color {i}",
                value=st.session_state.colors.get(i, rgb_to_hex(DEFAULT_COLORS.get(i, (200, 200, 200)))),
                key=f"color_{i}"
            )
        st.button("🎰 Random Colors", on_click=randomize_colors, use_container_width=True )

        


def _on_colors_changed():
    st.session_state.rule_string = random_rule(st.session_state.num_colors)
    st.session_state.last_image = None
    st.session_state.last_gif_path = None


def _on_rule_source_changed():
    if st.session_state.rule_source == "Random":
        st.session_state.rule_string = random_rule(st.session_state.num_colors)
        st.session_state.last_image = None


# ══════════════════════════════════════════════════════════════════════════════
#  GENERATE IMAGE
# ══════════════════════════════════════════════════════════════════════════════

def generate_image():
    mode = st.session_state.mode
    nc = st.session_state.num_colors
    rule_str = st.session_state.rule_string
    bnd_map = {"Fixed (1)": 1, "Cyclic": 0, "Random": -1}
    bnd = bnd_map[st.session_state.boundary_mode]
    colors_rgb = {k: hex_to_rgb(v) for k, v in st.session_state.colors.items()}
    rainbow = st.session_state.rainbow
    sym = st.session_state.sym
    rs = st.session_state.random_scale
    wu = st.session_state.wait_until

    if mode == "Triangle":
        rows = generate_triangle(rule_str, st.session_state.tri_lines, bnd, rs, wu, sym)
        img = draw_triangle(rows, colors=colors_rgb, rainbow=rainbow)
    elif mode == "Octagon":
        rows = generate_triangle(rule_str, st.session_state.tri_lines, bnd, rs, wu, sym)
        img = make_pattern_octagon(rows, colors=colors_rgb, rainbow=rainbow)
    elif mode == "Square":
        rows = generate_square(rule_str, st.session_state.sq_generations, bnd, rs, wu, sym)
        img = draw_square(rows, colors=colors_rgb, rainbow=rainbow)
    elif mode == "Hexagon":
        board = generate_hex(rule_str, st.session_state.hex_generations, bnd, st.session_state.hex_order, rs, wu, sym)
        img = draw_hex(board, colors=colors_rgb, rainbow=rainbow)
    else:
        img = None

    st.session_state.last_image = img
    return img


# ══════════════════════════════════════════════════════════════════════════════
#  GENERATE GIF
# ══════════════════════════════════════════════════════════════════════════════

def generate_gif():
    mode = st.session_state.mode
    nc = st.session_state.num_colors
    rule_str = st.session_state.rule_string
    bnd_map = {"Fixed (1)": 1, "Cyclic": 0, "Random": -1}
    bnd = bnd_map[st.session_state.boundary_mode]
    colors_rgb = {k: hex_to_rgb(v) for k, v in st.session_state.colors.items()}
    rainbow = st.session_state.rainbow
    sym = st.session_state.sym
    rs = st.session_state.random_scale
    wu = st.session_state.wait_until
    start = st.session_state.anim_start
    end = st.session_state.anim_end
    dur = st.session_state.anim_duration
    zoom = st.session_state.anim_zoomout

    # Clean up old gif
    if st.session_state.last_gif_path and os.path.exists(st.session_state.last_gif_path):
        try:
            os.unlink(st.session_state.last_gif_path)
        except:
            pass

    with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as f:
        temp_path = f.name

    try:
        if mode == "Triangle":
            animate_gif_tri(rule_str, colors=colors_rgb, boundary=bnd, random_scale=rs, wait_until=wu,
                           sym=sym, rainbow=rainbow, filename=temp_path, start_rows=start, end_rows=end,
                           duration=dur, loop=0, zoomout=zoom)
        elif mode == "Octagon":
            animate_gif_oct(rule_str, colors=colors_rgb, boundary=bnd, random_scale=rs, wait_until=wu,
                           sym=sym, rainbow=rainbow, filename=temp_path, start_rows=start, end_rows=end,
                           duration=dur, loop=0, zoomout=zoom, angdur=st.session_state.oct_angdur)
        elif mode == "Square":
            animate_gif_sq(rule_str, colors=colors_rgb, boundary=bnd, random_scale=rs, wait_until=wu,
                          sym=sym, rainbow=rainbow, filename=temp_path, start_rows=start, end_rows=end,
                          duration=dur, loop=0, zoomout=zoom)
        elif mode == "Hexagon":
            animate_gif_hex(rule_str, colors=colors_rgb, boundary=bnd, order=st.session_state.hex_order,
                           random_scale=rs, wait_until=wu, sym=sym, rainbow=rainbow, filename=temp_path,
                           start_gen=start, end_gen=end, duration=dur, loop=0, zoomout=zoom)

        st.session_state.last_gif_path = temp_path
        return temp_path
    except Exception as e:
        st.error(f"Error generating GIF: {e}")
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        return None


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN PAGE
# ══════════════════════════════════════════════════════════════════════════════
if "needs_generate" not in st.session_state:
    st.session_state.needs_generate = False
def request_generate():
    st.session_state.needs_generate = True
def main_page():
    mode = st.session_state.mode
    icon = SHAPE_ICONS[mode]

    st.title(f"{icon} {mode} Pattern Generator")
    st.caption("Create beautiful geometric patterns from color substitution rules")

    # Validate rule
    nc = st.session_state.num_colors
    rule_str = st.session_state.rule_string
    expected_len = nc * nc

    if len(rule_str) != expected_len or not rule_str.isdigit():
        st.error(f"Rule string must be {expected_len} digits (1-{nc}). Current: '{rule_str}'")
        return

    # Check all digits are valid
    if any(int(d) < 1 or int(d) > nc for d in rule_str):
        st.error(f"All digits must be between 1 and {nc}.")
        return

    # Visual rule editor
    with st.expander("🎨 Visual Rule Editor", expanded=False):
        visual_rule_editor(nc)
        rule_str = st.session_state.rule_string
        rules, n = parse_rule(rule_str)

    # Rule table preview
    rules, n = parse_rule(rule_str)
    colors_rgb = {k: hex_to_rgb(v) for k, v in st.session_state.colors.items()}

    with st.expander("📋 Rule Table"):
        rule_img = draw_rule_table(rules, n, colors_rgb, cell=56)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(rule_img)
        with col2:
            st.code(f'Rule: "{rule_str}"')
            st.markdown(f"**Colors:** {nc}")
            st.markdown(f"**Boundary:** {st.session_state.boundary_mode}")
            st.markdown(f"**Rainbow:** {'Yes' if st.session_state.rainbow else 'No'}")
            st.markdown(f"**Symmetric:** {'Yes' if st.session_state.sym else 'No'}")

    st.markdown("---")

    # Generate button
    col_gen, col_info = st.columns([1, 3])
    with col_gen:
        if st.button("🔄 Generate", type="primary", use_container_width=True):
            with st.spinner("Generating pattern..."):
                st.session_state.needs_generate = True
    if st.session_state.needs_generate:
        with st.spinner("Generating pattern..."):
            generate_image()
            #st.rerun()
        st.session_state.needs_generate = False

    # Display image
    if st.session_state.last_image is not None:
        img = st.session_state.last_image

        # Dark background for transparent images
        st.markdown("""
        <style>
        .image-container {
            background: #1a1a2e;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)

        #st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.image(img, use_container_width=True)
        #st.markdown('</div>', unsafe_allow_html=True)

        # Download PNG
        st.markdown(get_download_link(img, f"{mode.lower()}_pattern.png", "⬇ Download PNG"), unsafe_allow_html=True)

        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Size", f"{img.width} × {img.height}")
        with col2:
            st.metric("Colors", nc)
        with col3:
            if mode in ["Triangle", "Octagon"]:
                st.metric("Lines", st.session_state.tri_lines)
            elif mode == "Square":
                st.metric("Generations", st.session_state.sq_generations)
            else:
                st.metric("Generations", st.session_state.hex_generations)

    else:
        st.info("Click **Generate** to create a pattern")

    st.markdown("---")

    # GIF Section
    st.subheader("🎬 Animation")

    gif_cols = st.columns([1, 1])
    with gif_cols[0]:
        if st.button("🎞️ Generate GIF", use_container_width=True):
            with st.spinner("Generating animation (this may take a moment)..."):
                gif_path = generate_gif()
                if gif_path:
                    st.rerun()

    with gif_cols[1]:
        if st.session_state.last_gif_path and os.path.exists(st.session_state.last_gif_path):
            st.markdown(get_file_download_link(
                st.session_state.last_gif_path,
                f"{mode.lower()}_animation.gif",
                "⬇ Download GIF"
            ), unsafe_allow_html=True)
        else:
            st.markdown("&nbsp;")  # placeholder

    if st.session_state.last_gif_path and os.path.exists(st.session_state.last_gif_path):
        st.markdown("""
        <style>
        .gif-container {
            background: #1a1a2e;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)
        #st.markdown('<div class="gif-container">', unsafe_allow_html=True)
        st.image(st.session_state.last_gif_path, use_container_width=True)
        #st.markdown('</div>', unsafe_allow_html=True)

        st.subheader("Smooth Viewer (No Lag)")
        frames = []
        gif = Image.open(st.session_state.last_gif_path)

        # Extract all frames
        frames = [
            frame.copy().convert("RGBA")
            for frame in ImageSequence.Iterator(gif)
        ]

        # Get GIF FPS from frame duration
        duration = gif.info.get("duration", 50)  # milliseconds per frame
        fps = 1000 / duration if duration > 0 else 50

        # encode frames as base64 PNG list
        encoded_frames = []
        for f in frames:
            buf = io.BytesIO()
            f.save(buf, format="WEBP", lossless=True)
            encoded_frames.append(
                base64.b64encode(buf.getvalue()).decode()
            )

        html = f"""
        <div style="text-align:center;">
            <img id="frame" style="width:100%; max-width:500px;">

            <br><br>

            <input type="range" min="0" max="{len(encoded_frames)-1}"
                value="0" id="slider" style="width:500px;"/>

            <button onclick="playing = !playing;">Play/Pause</button>
        </div>

        <script>
            let frames = {encoded_frames};
            let i = 0;
            let playing = false;

            const img = document.getElementById("frame");
            const slider = document.getElementById("slider");

            function render(idx) {{
                img.src = "data:image/webp;base64," + frames[idx];
            }}

            slider.oninput = (e) => {{
                i = parseInt(e.target.value);
                render(i);
            }}

            function loop() {{
                if (playing) {{
                    i = (i + 1) % frames.length;
                    slider.value = i;
                    render(i);
                }}
            }}

            setInterval(loop, {50});
            render(0);
        </script>
        """

        st.components.v1.html(html, height=650)

    elif st.session_state.last_gif_path is None:
        st.info("Generate a pattern first, then create an animation")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    st.set_page_config(
        page_title="Geometric Pattern Generator",
        layout="wide",
        page_icon="🎨",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    
    # st.markdown("""
    # <style>
    # /* Main background */
    # .main .block-container {
    #     background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%);
    #     color: #e0e0e0;
    #     padding-top: 2rem;
    # }
    
    # /* Sidebar */
    # [data-testid="stSidebar"] {
    #     background: linear-gradient(180deg, #1e1e3a 0%, #15152a 100%);
    # }
    
    # /* Headers */
    # h1, h2, h3 {
    #     color: #ffffff !important;
    # }
    
    # /* Buttons */
    # .stButton > button {
    #     font-weight: 500;
    # }
    
    # /* Expander */
    # .streamlit-expanderHeader {
    #     color: #b0b0d0 !important;
    # }
    
    # /* Metrics */
    # [data-testid="stMetric"] {
    #     background: rgba(255, 255, 255, 0.05);
    #     border-radius: 8px;
    #     padding: 10px;
    # }
    
    # /* Selectbox */
    # .stSelectbox label, .stSlider label, .stCheckbox label {
    #     color: #c0c0e0 !important;
    # }
    
    # /* Code block */
    # .stCode {
    #     background: rgba(0, 0, 0, 0.3) !important;
    # }
    # </style>
    # """, unsafe_allow_html=True)

    init_state()
    sidebar()
    main_page()


if __name__ == "__main__":
    main()