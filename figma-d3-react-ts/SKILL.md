---
name: figma-d3-react-ts
description: >
  D3.js data visualization in React/Next.js components with PIXEL-PERFECT Figma matching.
  Use when building interactive charts, graphs, network diagrams, geographic maps, or any
  custom data visualization with D3.js inside React components. Covers pixel-perfect Figma
  extraction workflow, iterative visual validation via Playwright, two integration approaches
  (useRef+useEffect imperative vs declarative React rendering), responsive sizing, TypeScript
  typing, SSR/Next.js compatibility, accessibility, and performance.
  Triggers on: 'create a chart', 'add a D3 visualization', 'build a graph component',
  'data visualization', 'interactive chart', 'force-directed graph', 'bar chart', 'line chart',
  'heatmap', 'scatter plot', 'pie chart', 'chord diagram'.
---

# D3.js for React — Pixel-Perfect from Figma

Every chart MUST match its Figma design 100%. Follow the steps below **in order**.

---

## Step 1: Extract from Figma

```bash
mcp0_get_screenshot --nodeId <chart-node-id>
mcp0_get_design_context --nodeId <chart-node-id>
mcp0_get_variable_defs --nodeId <chart-node-id>
```

---

## Step 2: Analyze Chart Properties

Study the Figma screenshot and answer these before writing any code:

**Chart type** — line / multi-line / area / bar / grouped bar / scatter / pie / heatmap / other?
**Area fills?** — yes (area chart) or no (line chart only)?
**Series count** — how many lines/bars? Count precisely.
**Line behavior** — converging, diverging, parallel, spread from one point?

**Lines/shapes** — color (hex), thickness (px), opacity, style (solid/dashed/dotted), dash pattern, curve type (curveLinear / curveMonotoneX)
**Special lines** — average/median/threshold? Style (e.g., white dashed)?
**Fills/gradients** — direction, stops, opacity, or none?

**Axes** — Y labels (values, font, color, size), Y title (text, rotation), X labels, axis line color/thickness
**Grid** — horizontal lines (color, style), vertical lines (present? color, style)

**Colors on dark bg** — grid `#232b3e`, axis `#8596bb`, labels `#7184af`, title `#ebeef4` (see AGENTS.md dark context rules)

**Legend** — position, items, symbols

---

## Step 2b: Extract Shape Fill Patterns (MANDATORY for ALL chart types)

**⛔ DO NOT guess fill patterns for ANY shape. Always extract from Figma first.**

Figma DataViz shapes (bars, area fills, pie slices, scatter dots, line strokes, heatmap cells) often use **multi-layer composites** — not simple solid colors. Every shape type can have gradients, masks, textures, and blend modes. You MUST extract the exact layer structure before writing any fill/stroke code.

### Which shapes to extract

| Chart type | Shape atoms to find |
|---|---|
| Bar / Grouped bar / Histogram | `.Atom / Bar / V` or `.Atom / Bar / H` |
| Area chart | Area fill path — look for `<path>` with `fill` + gradient/mask |
| Line chart | Line stroke — look for stroke gradients, glow effects, or dashed patterns |
| Pie / Donut | Slice segments — look for radial gradients, stroke separators |
| Scatter / Bubble | Dot/circle atoms — look for radial gradients, opacity, blur/glow |
| Heatmap / Matrix | Cell rectangles — look for color scales, opacity mapping |
| Treemap | Nested rectangles — look for fill patterns, border styles |
| Sankey / Chord | Flow paths — look for gradient fills along path direction |

### Extraction workflow

1. **Find the shape atom node** — In the chart's design context, locate the individual shape element. Look for names like `.Atom / Bar / V`, `Bar / V`, `Slice`, `Dot`, `Area`, `Line`, or similar. Note its node ID.

2. **Screenshot the shape atom at full zoom:**
   ```bash
   mcp0_get_screenshot --nodeId <shape-atom-node-id>
   ```

3. **Get the shape atom's design context:**
   ```bash
   mcp0_get_design_context --nodeId <shape-atom-node-id>
   ```

4. **Identify the layer structure** — Read the design context and map each layer:

   | Layer | What to look for in Figma | SVG equivalent |
   |-------|--------------------------|----------------|
   | **Base fill/stroke** | `bg-[var(--data-viz/...)]` — solid color | `fill={color}` or `stroke={color}` |
   | **Gradient** | `bg-gradient-to-*` or `linear-gradient(...)` | `<linearGradient>` or `<radialGradient>` in `<defs>` |
   | **Opacity mask** | `bg-gradient-*` inside a `mask` or `overflow-clip` div | SVG `<mask>` with gradient fill |
   | **Tiling texture** | `bg-size-[Wpx_Hpx]` + `backgroundImage: url(...)` + `opacity-*` | SVG `<pattern>` with repeating elements |
   | **Blend overlay** | `mix-blend-plus-lighter`, `mix-blend-overlay`, etc. | SVG `style={{ mixBlendMode }}` or skip if subtle |
   | **Blur / glow** | `blur(...)`, `drop-shadow(...)` | SVG `<filter>` with `<feGaussianBlur>` |
   | **Stroke style** | `border-dashed`, `strokeDasharray` | `strokeDasharray="X Y"` |
   | **Opacity** | `opacity-40`, `opacity-0.5` | `opacity={0.4}` |

5. **Download and inspect any mask/texture images** (if present):
   ```bash
   mcp1_browser_navigate --url "<image-url>"
   mcp1_browser_take_screenshot  # see the tile/mask pattern
   ```

### Key rules (apply to ALL shape types)

- **Never assume solid fills** — Always check. Even a simple-looking bar or area fill may have gradient + texture layers.
- **Mask ≠ overlay** — A Figma mask controls the **visibility** of the layer below. It does NOT paint color on top. In SVG, use `<mask>` (white = visible, black = hidden). Never use `fill="black"` as a painted overlay.
- **Gradient direction matters** — `from-black to-rgba(0,0,0,0.08)` in a Figma mask = opacity mask where one end is fully visible and the other fades out. Map the direction (`to-b` = top→bottom, `to-r` = left→right, `to-br` = diagonal) to SVG gradient `x1/y1/x2/y2`.
- **Textures inside masks fade together** — If a tiling pattern and a gradient share the same mask container, apply the same SVG `<mask>` to both layers.
- **Check line/texture direction visually** — Download the tile image. Horizontal lines = pattern repeats vertically. Vertical lines = pattern repeats horizontally. Diagonal = both. **Never assume — always inspect.**
- **Tile size** — The Figma `bg-size` value (e.g., `14.08px × 14.08px`) is the SVG `<pattern>` width/height.
- **Area chart gradients** — Often fade from the line color at the top to transparent at the bottom. Use `<linearGradient>` with `stopOpacity`.
- **Line stroke gradients** — Some lines change color along their length. Use `<linearGradient>` applied to `stroke`.
- **Radial gradients** — Used in pie slices, scatter dots, and radial charts. Use `<radialGradient>` with `cx/cy/r`.

### SVG template: shape with gradient opacity mask + line texture

```tsx
<defs>
  {/* Opacity mask: adjust direction (x1,y1→x2,y2) per Figma gradient */}
  <linearGradient id="shape-mask-grad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stopColor="white" stopOpacity="1" />
    <stop offset="100%" stopColor="white" stopOpacity="0.08" />
  </linearGradient>
  <mask id="shape-mask" maskContentUnits="objectBoundingBox">
    <rect width="1" height="1" fill="url(#shape-mask-grad)" />
  </mask>
  {/* Tiling line pattern — adjust width/height per Figma bg-size */}
  <pattern id="shape-lines" patternUnits="userSpaceOnUse" width="100" height="3.5">
    <rect width="100" height="3.5" fill="white" />
    <rect width="100" height="1" fill="black" opacity="0.30" />
  </pattern>
</defs>

{/* Layer 1: solid color with gradient opacity mask */}
<path d={shapePath} fill={shapeColor} mask="url(#shape-mask)" />
{/* Layer 2: line texture, also masked (omit if no texture in Figma) */}
<path d={shapePath} fill="url(#shape-lines)" mask="url(#shape-mask)" opacity="0.15" />
```

### SVG template: area chart with gradient fill

```tsx
<defs>
  <linearGradient id="area-grad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stopColor={lineColor} stopOpacity="0.4" />
    <stop offset="100%" stopColor={lineColor} stopOpacity="0" />
  </linearGradient>
</defs>
<path d={areaPath} fill="url(#area-grad)" />
<path d={linePath} fill="none" stroke={lineColor} strokeWidth={2} />
```

---

## Step 3: Research D3 Example via Playwright

Look up the matching example from `references/d3-examples-catalog.md` (167 examples):

| Chart Type | Example to Open |
|---|---|
| Line | `https://observablehq.com/@d3/line-chart` |
| Multi-line | `https://observablehq.com/@d3/multi-line-chart` |
| Area | `https://observablehq.com/@d3/area-chart` |
| Bar | `https://observablehq.com/@d3/bar-chart` |
| Grouped bar | `https://observablehq.com/@d3/grouped-bar-chart` |
| Stacked bar | `https://observablehq.com/@d3/stacked-bar-chart` |
| Scatter | `https://observablehq.com/@d3/scatterplot` |
| Pie | `https://observablehq.com/@d3/pie-chart` |
| Force graph | `https://observablehq.com/@d3/force-directed-graph` |
| Treemap | `https://observablehq.com/@d3/treemap` |
| Sankey | `https://observablehq.com/@d3/sankey` |

**Open it in Playwright MCP:**

```bash
mcp1_browser_navigate --url "<example-url>"
mcp1_browser_take_screenshot --type png --filename "d3-example-ref.png"
mcp1_browser_snapshot   # read the D3 code cells
```

**Extract from the example:** scale types, shape generator, curve type, axis config, data structure, margin convention, interaction patterns.

**Key rule:**
- D3 example → **correct API patterns** (scales, generators, bindings)
- Figma → **exact visual styling** (colors, fonts, spacing, opacity)
- Never copy example colors. Always copy example D3 patterns.

---

## Step 4: Implement

Combine D3 patterns (Step 3) + Figma styling (Step 2).

**SVG attributes must use exact Figma values:**
```tsx
// ❌ WRONG
stroke="steelblue" strokeWidth={2}

// ✅ RIGHT
stroke="#7b8ec8" strokeWidth={1} opacity={0.45}
```

**SVG text must use inline attributes, not Tailwind:**
```tsx
// ❌ WRONG
className="fill-gray-600 font-body"

// ✅ RIGHT
fill="#7184af" fontFamily="Titillium Web, sans-serif" fontSize={12}
```

**Choose approach** (see `references/chart-patterns.md` for full examples):
- **Approach B (Declarative JSX)** — D3 for math only, React renders SVG. Use for simple charts.
- **Approach A (Imperative useRef+useEffect)** — D3 owns the DOM. Use when you need zoom/drag/force/brush/transitions.

**Approach A requires:** `'use client'` + `dynamic(() => import(...), { ssr: false })` for Next.js.

---

## Step 5: Validate (Iterative Loop)

```
1. 📸 mcp0_get_screenshot --nodeId <chart-node-id>     (Figma)
2. 🏗️ npx nx build web-app                              (verify no errors)
3. 📸 npx playwright screenshot <url> <file>             (implementation)
4. 👁️ Compare: chart type, line count, colors, styles, grid, legend, density
5. 🔄 If mismatch → fix → go to step 2
   ✅ If match → done
```

---

## Step 6: Common Pitfalls

| Figma Shows | Mistake | Fix |
|---|---|---|
| Lines without area fills | Using `d3.area()` | Use `d3.line()` only |
| ~25 thin transparent lines | 5-8 thick opaque lines | 25+ lines, `opacity: 0.4` |
| White dashed average line | Hardcoded average | Make it a prop |
| Vertical grid lines | Only horizontal grids | Add vertical `<line>` elements |
| Lines with bumps | Smooth monotonic lines | Add realistic data variation |
| Dense clustered band | Evenly spread lines | Cluster most lines in the dense range |
| Dark background | Light-mode CSS fallbacks | Use dark-context tokens |
| Shape with gradient+texture | Guessing solid fill | Run Step 2b: extract shape atom from Figma first |
| Figma mask layer | Painting black/white overlay on top | Use SVG `<mask>` (white=visible, black=hidden) |
| Tiling line/dot texture | Wrong direction or spacing | Download tile image, inspect visually, read `bg-size` |
| Gradient on shape | Adding separate color overlay | Gradient controls shape opacity via `<mask>`, not a painted layer |
| Area fill gradient | Solid color or wrong direction | Extract gradient stops + direction from Figma area path |
| Line stroke with glow | Plain solid stroke | Check for blur/shadow filters, add SVG `<filter>` if present |

---

## Storybook: Mandatory Dark + Light

Every chart story MUST export `Dark` (primary) and `Light`:

```tsx
export const Dark: Story = {
  parameters: { backgrounds: { default: 'dark', values: [{ name: 'dark', value: '#020712' }] } },
};
export const Light: Story = {
  parameters: { backgrounds: { default: 'light', values: [{ name: 'light', value: '#ffffff' }] } },
};
```

Dark is primary. Additional variants (e.g., `Empty`, `FewLines`) also use dark background.

---

## Quick Reference

| Topic | Where |
|---|---|
| Full chart code examples (bar, line, scatter, pie, heatmap, chord, force) | `references/chart-patterns.md` |
| Tooltips, zoom, drag, brush, transitions | `references/interactivity.md` |
| 167 official D3 Observable examples | `references/d3-examples-catalog.md` |
| Responsive sizing (ResizeObserver hook) | `references/chart-patterns.md` → Responsive section |
| TypeScript typing for D3 | `references/chart-patterns.md` → TypeScript section |
| SSR / Next.js compatibility | Approach A: `dynamic(import, {ssr:false})`. Approach B: works as-is. |
| React StrictMode | Always `svg.selectAll('*').remove()` at start of useEffect |
| Accessibility | `<svg role="img" aria-label="..."><title>...</title><desc>...</desc>` |
| Performance | >1000 elements → use `<canvas>`. Memoize scales with `useMemo`. |

---

## Install

```bash
npm install d3 && npm install -D @types/d3
```
