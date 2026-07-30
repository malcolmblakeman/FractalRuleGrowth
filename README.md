# 🔺✨ Pattern Forge

### Geometric Pattern Generator from Color Substitution Rules

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

<img src="README_ASSETS/banner.png" width="100%" alt="Pattern Forge Banner">

**Create mesmerizing geometric fractals by defining simple color rules.**
7 shapes • 2–5 colors • Rainbow mode • Animated growth • Infinite possibilities

[🚀 Try it Live](https://your-app.streamlit.app) · [📖 How It Works](#-how-it-works) · [🎨 Gallery](#-gallery)


---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔺 **7 Geometric Shapes** | Triangle, Octagon, Square, Hexagon, Quadagon, Pentagon, Trigon |
| 🎨 **2–5 Color Palettes** | Full color picker with randomize option |
| 📋 **Visual Rule Editor** | Click-to-edit rule table — no coding required |
| 🌈 **Rainbow Mode** | Cyclic hue shifting creates stunning gradients |
| 🎬 **GIF Animation** | Watch patterns grow with zoom-out and rotation effects |
| 🔄 **Symmetric Rules** | Mirror rules for perfectly balanced patterns |
| 🎲 **Random Noise** | Add controlled chaos with adjustable scale |
| ⬇️ **Export PNG/GIF** | Download high-resolution outputs instantly |

---

## 🧠 How It Works

The core idea is beautifully simple: **every cell's color is determined by its two neighbors and a lookup rule.**

### Step 1: Define a Rule Table

For *n* colors, you create an *n×n* table. Each cell says: *"When color A meets color B, produce color C."*

<img src="README_ASSETS/rule_diagram.png" width="400" alt="Rule Table">

### Step 2: Pick Adjacent Pair

As the pattern grows row by row, each new cell looks at its two parents:

<img src="README_ASSETS/how_step1.png" width="500" alt="Step 1 - Pick pair">

### Step 3: Look Up Result

The rule table maps the pair → result color. Repeat for every cell, every row:

<img src="README_ASSETS/how_step2.png" width="500" alt="Step 2 - Lookup">

### Step 4: Watch Complexity Emerge

From those simple rules, intricate fractal-like structures emerge:

<img src="README_ASSETS/anim_triangle.gif" width="500" alt="Triangle growth animation">

> 🤯 **That's it.** No complex algorithms — just color substitution applied recursively. The complexity is *emergent*.

# 🧬 Growth Modes

All growth logic lives in `comp.py`. Every mode shares the same rule engine (`parse_rule`, `apply_rule`) and boundary system — they differ only in **how they seed** and **how they find neighbors**.

---

## 🔺 Triangle — 1D Cellular Automaton

> **Source:** `generate_triangle()` · L52–81

The base engine. Everything else reuses or mimics it.

**How it grows:**

1. Start with a single seed cell: `rows = [[1]]`
2. Each new row is built from the row above by reading **adjacent pairs**:
   ```
   new_row = [edge] + [rule[a, b] for (a, b) in zip(prev, prev[1:])] + [edge]
   ```
3. Edge cells are injected (not computed) using the `boundary` parameter
4. Rows are centered visually to form the triangle shape

**Key parameters:**

| Param | Effect |
|---|---|
| `boundary` | `-1` = random edges · `0` = cycling 1→n · else = fixed value |
| `sym` | Sorts `(a,b)` to `(min,max)` before lookup — makes the rule table symmetric |
| `random_scale` + `wait_until` | After N rows, randomly injects noise colors with given probability |
| `rainbow` | Rendering only — shifts hue per row in `draw_triangle` |

**In one sentence:** *Two parents above produce one child below, row by row.*

---

## 🟦 Square — Expanding Diamond with Cross Seeding

> **Source:** `generate_square()` · L83–180 · `generate_square_his()` · L182–275

Square does **not** grow row-by-row. It grows outward by **radius** from a center point.

**How it grows:**

1. **Seed:** Place a single cell at the origin → `board = {(0,0): center}`
2. **Each generation** increments the radius by 1, then:
   - **`add_cross()`** — Injects 4 cardinal boundary points at the new radius:
     ```python
     board[(0, -r)] = edge   # top
     board[(0,  r)] = edge   # bottom
     board[(-r, 0)] = edge   # left
     board[( r, 0)] = edge   # right
     ```
   - **`fill_ring()`** — Iterative closure loop:
     ```python
     while changed:
         for each cell in the ring:
             neighbors = filled orthogonal neighbors  # up/down/left/right
             if len(neighbors) == 2:
                 board[cell] = apply_rule(neighbors[0], neighbors[1])
                 changed = True
     ```
     Keeps looping until no more cells can be filled.

**Why it looks like a diamond:** Only the cross is seeded. Corners fill only when they gain exactly 2 orthogonal neighbors (e.g., left + top), so growth propagates inward from the `+` shape into a filled square.

**In one sentence:** *Seed a cross, then flood-fill inward wherever exactly 2 neighbors exist.*

---

## ⬡ Hexagon — Alternating Crystal Rings

> **Source:** `generate_hex()` · L277–429

The most complex mode. Uses **axial hex coordinates** `(q, r)` and 6-directional neighbors.

**How it grows:**

1. **Coordinate system:** Axial hex grid — 6 neighbors per cell instead of 4
2. **`hex_ring(radius)`** — Walks the perimeter of the current ring in 6 directions:
   ```python
   directions = [(1,0), (0,1), (-1,1), (-1,0), (0,-1), (1,-1)]
   ```
3. **`add_outer_points()`** — The crystal seeding trick:
   - Generates the full ring, then selects **every other point**
   - The `order` parameter controls the alternation pattern:
     | `order` | Behavior |
     |---|---|
     | `-1` | Randomly picks even or odd indices |
     | `0` | Alternates by radius parity *(default, most natural)* |
     | `1` | Always even indices |
     | `2` | Always odd indices |
   - Result: only `3×R` points seeded per ring, not `6×R` — half the ring is empty
4. **`fill_ring()`** — Hex fill with distance-sorted neighbors:
   ```python
   touching = [color for nb in 6_neighbors if nb in board]
   touching.sort(key=hex_distance)  # closest parents first
   if len(touching) >= 2:           # note: >=2, not ==2
       board[cell] = apply_rule(touching[0], touching[1])
   ```

**The elegant trick:** By seeding only every other edge point, the interior is *forced* to be computed from 2 parents — just like triangle, but on a hex lattice. The alternating pattern creates the crystalline look.

**In one sentence:** *Half-seed each ring, then fill gaps from the 2 nearest filled hex neighbors.*

---

## 🔷 Octagon — Triangle in 8-Fold Symmetry

> **Source:** `animate_gif_oct()` · L915–963 · `make_pattern_same()` · L498–552

> [!IMPORTANT]
> **Octagon is NOT a new growth mode. It is a rendering mode.** The underlying data is identical to Triangle.

**How it works:**

1. **Grow exactly like triangle:**
   ```python
   rows = generate_triangle(rule, num_lines, ...)  # same function!
   ```
2. **`make_pattern_same()` composites 8 triangles onto one canvas:**
   - Draw the triangle → `tri`
   - **Cardinal layer (4 triangles):** Stack `tri` + `tri.rotate(180)` vertically, `tri.rotate(90)` + `tri.rotate(270)` horizontally → 4-way star
   - **Diagonal layer (4 triangles):** Scale the cross by `1.07×` (LANCZOS), rotate 45°, overlay onto the cardinal layer
   - **Composite rule:** Only fill pixels where the base is transparent — prevents overwriting
3. **Why `1.07×` scale?** The diagonal triangles need to be slightly larger to close seam gaps when rotated 45°

**This is why octagon parameters match triangle exactly:** `start_rows`, `end_rows`, `boundary`, `random_scale`, `sym` — because the growth *is* triangle. Only the drawing changes.

**In one sentence:** *Grow a triangle, then stamp it 8 times with rotation to form an octagon.*

---

## 🧩 Shared Core

Every mode uses the same rule engine from `comp.py`:

```python
def parse_rule(rule_string):
    n = int(sqrt(len(rule_string)))          # e.g. "213132321" → n=3
    rules[(a, b)] = int(rule_string[index])  # maps (1,1)..(n,n) → color

def apply_rule(rules, a, b, sym=False):
    if sym and b > a:
        a, b = b, a                          # symmetric lookup
    return rules[(a, b)]

# Boundary logic (identical across all modes):
if boundary == -1:  edge = random.randint(1, n)
elif boundary == 0: edge = ((gen - 1) % n) + 1   # cycling
else:               edge = boundary               # fixed
```

All modes also respect `random_scale` and `wait_until` for controlled noise injection after N generations.

---

## 📊 Comparison at a Glance

| | 🔺 Triangle | 🟦 Square | ⬡ Hexagon | 🔷 Octagon |
|---|---|---|---|---|
| **Data structure** | List of lists | Dict `(x,y)→color` | Dict `(q,r)→color` | List of lists |
| **Growth direction** | Row by row ↓ | Radius outward ◎ | Ring outward ⬡ | Row by row ↓ |
| **Seeding** | Edges per row | Cross per radius | Every-other ring point | Edges per row |
| **Neighbor rule** | 2 from prev row | Exactly 2 orthogonal | ≥2 of 6 hex dirs | 2 from prev row |
| **Symmetry** | 1× | 4× | 6× | 8× |
| **Grows its own data?** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ Reuses Triangle |
---

## 🎨 Gallery

### All 7 Shapes (same rule, different geometry)

<img src="README_ASSETS/shapes_overview.png" width="100%" alt="All shapes overview">

<details>
<summary>🔸 Individual Shape Showcases</summary>

| Octagon | Hexagon | Square | Pentagon |
|:-------:|:-------:|:------:|:--------:|
| <img src="README_ASSETS/octagon_showcase.png" width="200"> | <img src="README_ASSETS/hexagon_showcase.png" width="200"> | <img src="README_ASSETS/square_showcase.png" width="200"> | <img src="README_ASSETS/pentagon_showcase.png" width="200"> |

</details>

### 🌈 Rainbow Mode

Toggle rainbow mode to shift hues based on position — turns any pattern into a psychedelic masterpiece:

<img src="README_ASSETS/rainbow_comparison.png" width="100%" alt="Rainbow comparison">

### 🎬 Animated Growth

Watch patterns unfold in real-time with customizable speed, zoom, and rotation:

| Triangle Growth | Octagon Spin | Hexagon Bloom | Square Expand |
|:---------------:|:------------:|:-------------:|:-------------:|
| <img src="README_ASSETS/anim_triangle_rainbow.gif" width="180"> | <img src="README_ASSETS/anim_octagon_spin.gif" width="180"> | <img src="README_ASSETS/anim_hexagon.gif" width="180"> | <img src="README_ASSETS/anim_square.gif" width="180"> |

### 🎨 More Colors = More Complexity

| 3 Colors | 4 Colors | 5 Colors |
|:--------:|:--------:|:--------:|
| <img src="README_ASSETS/anim_triangle.gif" width="200"> | <img src="README_ASSETS/showcase_4color.png" width="200"> | <img src="README_ASSETS/showcase_5color.png" width="200"> |

---

## 🚀 Quick Start

### Play Online (No Install)

👉 **[Open in Streamlit](https://your-app.streamlit.app)** — zero setup, start creating immediately.

### Run Locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/pattern-forge.git
cd pattern-forge

# Install dependencies
pip install streamlit pillow

# Run!
streamlit run app.py


That's it. No complex build steps.

---

## ⚙️ Controls Guide

### Shape Selection
Choose from 7 geometric templates in the sidebar. Each applies the same rule logic to a different lattice structure.

### Rule Source
- **Random** — Click "New Random Rule" for instant inspiration
- **Custom** — Type a rule string directly (e.g., `"213132321"` for 3 colors)

### Visual Rule Editor
Expand the editor to click-to-change any rule cell. The colored circles show input pairs, and buttons select the output.

### Boundary Modes
| Mode | Behavior |
|------|----------|
| Fixed (1) | All edges are color 1 |
| Cyclic | Edge color cycles through palette |
| Random | Each edge gets a random color |

### Advanced Settings
| Setting | Effect |
|---------|--------|
| **Symmetric Rule** | Rule[A,B] = Rule[B,A] — creates balanced patterns |
| **Random Scale** | 0.0 = pure rule, 1.0 = pure noise |
| **Wait Until** | Apply noise only after N rows/generations |
| **Rainbow Mode** | Shift hue based on position |

### Animation Settings
| Setting | Effect |
|---------|--------|
| **Start/End** | Row or generation range to animate |
| **Frame Duration** | Milliseconds per frame (lower = faster) |
| **Zoom Out** | Each frame fills the canvas (growing zoom-out effect) |
| **Rotation Speed** | For octagon/pentagon/etc — spin while growing |

---

## 🔬 Technical Details

### Rule String Format

For *n* colors, the rule is a string of *n²* digits. The digit at index `(a-1)×n + (b-1)` gives the output for pair `(a, b)`.

```
Rule "213132321" for 3 colors:

       B=1  B=2  B=3
  A=1 [ 2    1    3 ]
  A=2 [ 1    3    2 ]
  A=3 [ 3    2    1 ]
```

### Growth Algorithms

| Shape | Lattice | Growth Direction |
|-------|---------|------------------|
| Triangle | Triangular grid | Top-down rows |
| Octagon | 4 rotated triangles + 45° fill | 8-fold symmetry |
| Square | Square grid | Concentric rings from center |
| Hexagon | Hex grid (axial coords) | Concentric hex rings |
| Quadagon | 4 rotated triangles | 4-fold symmetry |
| Pentagon | 5 rotated triangles | 5-fold symmetry |
| Trigon | 3 rotated triangles | 3-fold symmetry |

### Color Theory

Patterns use **additive color mixing** principles — the rule table acts as a discrete color algebra. Simple rules like `A+B→C` where C differs from both A and B create the most visual interest.

---

## 🛠️ Development

```bash
# Generate README demo assets (creates README_ASSETS/ folder)
python generate_readme_assets.py

# Run in dev mode with auto-reload
streamlit run app.py --server.runOnSave true
```

### Project Structure

```
pattern-forge/
├── app.py                      # Main Streamlit application
├── generate_readme_assets.py   # Asset generator for README
├── README.md                   # This file
├── README_ASSETS/              # Generated images & GIFs
│   ├── banner.png
│   ├── shapes_overview.png
│   ├── anim_triangle.gif
│   └── ...
└── requirements.txt            # Python dependencies
```

---

## 📜 License

MIT License — use it, fork it, make beautiful things.

---

## 🙏 Acknowledgments

Inspired by:
- **Cellular automata** (Wolfram's Rule 30, etc.)
- **Color substitution systems** in generative art
- **Islamic geometric patterns** and their mathematical foundations
- The **Sierpinski triangle** as the canonical example of emergent complexity from simple rules

---

<div align="center">

**Made with 💜 and recursive color substitution**

*"Simple rules, infinite beauty."*

</div>
```
