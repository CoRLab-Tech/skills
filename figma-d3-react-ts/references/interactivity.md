# Interactivity & Animation Reference

Patterns for adding tooltips, zoom/pan, drag, brush, transitions, and animations to D3 charts in React.

## Table of Contents

- [Tooltips](#tooltips)
- [Zoom and Pan](#zoom-and-pan)
- [Drag Behavior](#drag-behavior)
- [Brush Selection](#brush-selection)
- [Transitions and Animations](#transitions-and-animations)
- [Click and Hover Interactions](#click-and-hover-interactions)
- [Crosshair / Bisector Tooltip](#crosshair--bisector-tooltip)

---

## Tooltips

### HTML tooltip (positioned over SVG)

```tsx
import { useRef, useEffect } from 'react';
import * as d3 from 'd3';

export function ChartWithTooltip({ data }: { data: any[] }) {
  const svgRef = useRef<SVGSVGElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!svgRef.current || !tooltipRef.current) return;

    const svg = d3.select(svgRef.current);
    const tooltip = d3.select(tooltipRef.current);

    // ... draw chart elements ...

    svg.selectAll('circle')
      .on('mouseover', (event, d: any) => {
        tooltip
          .style('opacity', 1)
          .html(`<strong>${d.label}</strong><br/>Value: ${d.value}`);
      })
      .on('mousemove', (event) => {
        const [x, y] = d3.pointer(event, svgRef.current);
        tooltip
          .style('left', `${x + 15}px`)
          .style('top', `${y - 10}px`);
      })
      .on('mouseout', () => {
        tooltip.style('opacity', 0);
      });
  }, [data]);

  return (
    <div style={{ position: 'relative' }}>
      <svg ref={svgRef} width={800} height={400} />
      <div
        ref={tooltipRef}
        style={{
          position: 'absolute',
          opacity: 0,
          background: 'white',
          border: '1px solid #ddd',
          borderRadius: '4px',
          padding: '8px 12px',
          pointerEvents: 'none',
          fontSize: '12px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          transition: 'opacity 0.15s',
        }}
      />
    </div>
  );
}
```

### SVG-native tooltip (simpler, no HTML overlay)

```tsx
// Add a <title> element for browser-native tooltip
g.selectAll('rect')
  .data(data)
  .join('rect')
  // ... attrs ...
  .append('title')
  .text((d) => `${d.category}: ${d.value}`);
```

---

## Zoom and Pan

```tsx
useEffect(() => {
  const svg = d3.select(svgRef.current);
  svg.selectAll('*').remove();

  const g = svg.append('g');
  // ... draw chart inside g ...

  const zoom = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.5, 10])
    .on('zoom', (event) => {
      g.attr('transform', event.transform);
    });

  svg.call(zoom);

  // Optional: reset zoom button
  // d3.select('#reset-zoom').on('click', () => {
  //   svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
  // });

  return () => { svg.on('.zoom', null); };
}, [data]);
```

### Constrained zoom (only X axis)

```tsx
const zoom = d3.zoom<SVGSVGElement, unknown>()
  .scaleExtent([1, 8])
  .translateExtent([[0, 0], [width, height]])
  .on('zoom', (event) => {
    const newXScale = event.transform.rescaleX(xScale);
    xAxisGroup.call(d3.axisBottom(newXScale));
    bars.attr('x', (d: any) => newXScale(d.category))
        .attr('width', newXScale.bandwidth?.() ?? xScale.bandwidth());
  });
```

---

## Drag Behavior

Used primarily with force-directed graphs and custom interactions.

```tsx
const drag = d3.drag<SVGCircleElement, NodeType>()
  .on('start', (event, d) => {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  })
  .on('drag', (event, d) => {
    d.fx = event.x;
    d.fy = event.y;
  })
  .on('end', (event, d) => {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  });

nodes.call(drag);
```

---

## Brush Selection

### 1D brush (X axis range selection)

```tsx
useEffect(() => {
  // ... draw chart ...

  const brush = d3.brushX()
    .extent([[0, 0], [innerWidth, innerHeight]])
    .on('end', (event) => {
      if (!event.selection) return;
      const [x0, x1] = event.selection as [number, number];
      const selectedRange = [xScale.invert(x0), xScale.invert(x1)];
      console.log('Selected range:', selectedRange);
      // Call parent callback: onBrush?.(selectedRange)
    });

  g.append('g')
    .attr('class', 'brush')
    .call(brush);
}, [data]);
```

### 2D brush (area selection)

```tsx
const brush = d3.brush()
  .extent([[0, 0], [innerWidth, innerHeight]])
  .on('end', (event) => {
    if (!event.selection) return;
    const [[x0, y0], [x1, y1]] = event.selection;
    const selected = data.filter(
      (d) =>
        xScale(d.x) >= x0 && xScale(d.x) <= x1 &&
        yScale(d.y) >= y0 && yScale(d.y) <= y1
    );
    console.log('Selected points:', selected);
  });
```

---

## Transitions and Animations

### Enter transition (bars growing from bottom)

```tsx
g.selectAll('rect')
  .data(data)
  .join('rect')
  .attr('x', (d) => xScale(d.category)!)
  .attr('y', innerHeight)           // Start at bottom
  .attr('width', xScale.bandwidth())
  .attr('height', 0)                // Start with no height
  .attr('fill', 'steelblue')
  .transition()
  .duration(750)
  .delay((_, i) => i * 50)          // Stagger
  .attr('y', (d) => yScale(d.value))
  .attr('height', (d) => innerHeight - yScale(d.value));
```

### Update transition (smooth data changes)

```tsx
// Use .join() with enter/update/exit for smooth transitions
g.selectAll('rect')
  .data(data, (d: any) => d.category) // Key function for identity
  .join(
    (enter) =>
      enter
        .append('rect')
        .attr('x', (d) => xScale(d.category)!)
        .attr('y', innerHeight)
        .attr('width', xScale.bandwidth())
        .attr('height', 0)
        .attr('fill', 'steelblue')
        .call((enter) =>
          enter.transition().duration(750)
            .attr('y', (d) => yScale(d.value))
            .attr('height', (d) => innerHeight - yScale(d.value))
        ),
    (update) =>
      update.call((update) =>
        update.transition().duration(750)
          .attr('x', (d) => xScale(d.category)!)
          .attr('y', (d) => yScale(d.value))
          .attr('width', xScale.bandwidth())
          .attr('height', (d) => innerHeight - yScale(d.value))
      ),
    (exit) =>
      exit.call((exit) =>
        exit.transition().duration(300)
          .attr('y', innerHeight)
          .attr('height', 0)
          .remove()
      )
  );
```

### Chained transitions

```tsx
circles
  .transition()
  .duration(500)
  .attr('fill', 'orange')
  .transition()
  .duration(500)
  .attr('r', 15);
```

### Easing functions

```tsx
.transition()
  .duration(1000)
  .ease(d3.easeBounceOut)   // Bounce effect
  // Other options:
  // d3.easeLinear
  // d3.easeQuadInOut
  // d3.easeCubicInOut
  // d3.easeElasticOut
  // d3.easeBackOut
```

---

## Click and Hover Interactions

### Highlight on hover

```tsx
circles
  .on('mouseover', function () {
    d3.select(this)
      .transition().duration(200)
      .attr('r', 10)
      .attr('fill', 'orange');
  })
  .on('mouseout', function (_, d: any) {
    d3.select(this)
      .transition().duration(200)
      .attr('r', 5)
      .attr('fill', colorScale(d.category));
  });
```

### Click to select

```tsx
circles
  .on('click', function (event, d: any) {
    // Reset all
    d3.selectAll('circle').attr('stroke', 'none').attr('stroke-width', 0);
    // Highlight clicked
    d3.select(this).attr('stroke', 'black').attr('stroke-width', 2);
    // Callback to React
    // onSelect?.(d);
  });
```

### Dispatching events to React

```tsx
// Inside useEffect:
circles.on('click', (event, d: any) => {
  // Use a callback prop instead of custom events
  onPointClick?.(d);
});

// Component signature:
interface Props {
  data: DataPoint[];
  onPointClick?: (point: DataPoint) => void;
}
```

---

## Crosshair / Bisector Tooltip

For line charts — show tooltip at nearest data point as mouse moves.

```tsx
// After drawing the line chart...

const bisect = d3.bisector<LineDatum, Date>((d) => d.date).center;

const focus = g.append('g').style('display', 'none');
focus.append('circle').attr('r', 5).attr('fill', 'steelblue').attr('stroke', 'white').attr('stroke-width', 2);
focus.append('line').attr('class', 'x-hover').attr('stroke', '#999').attr('stroke-dasharray', '3,3');
focus.append('line').attr('class', 'y-hover').attr('stroke', '#999').attr('stroke-dasharray', '3,3');

const tooltip = d3.select(tooltipRef.current);

svg.append('rect')
  .attr('width', innerWidth)
  .attr('height', innerHeight)
  .attr('transform', `translate(${margin.left},${margin.top})`)
  .style('fill', 'none')
  .style('pointer-events', 'all')
  .on('mouseover', () => focus.style('display', null))
  .on('mouseout', () => {
    focus.style('display', 'none');
    tooltip.style('opacity', 0);
  })
  .on('mousemove', function (event) {
    const [mx] = d3.pointer(event, this);
    const date = xScale.invert(mx);
    const i = bisect(data, date);
    const d = data[i];

    focus.attr('transform', `translate(${xScale(d.date)},${yScale(d.value)})`);
    focus.select('.x-hover')
      .attr('x1', 0).attr('y1', 0)
      .attr('x2', 0).attr('y2', innerHeight - yScale(d.value));
    focus.select('.y-hover')
      .attr('x1', 0).attr('y1', 0)
      .attr('x2', -xScale(d.date)).attr('y2', 0);

    tooltip
      .style('opacity', 1)
      .style('left', `${xScale(d.date) + margin.left + 15}px`)
      .style('top', `${yScale(d.value) + margin.top - 10}px`)
      .html(`<strong>${d3.timeFormat('%b %d, %Y')(d.date)}</strong><br/>Value: ${d.value}`);
  });
```
