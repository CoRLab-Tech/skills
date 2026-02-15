# Chart Patterns Reference

Full implementations for common chart types in React using D3.js. All examples use Approach A (useRef + useEffect) with TypeScript.

## Table of Contents

- [Bar Chart](#bar-chart)
- [Grouped Bar Chart](#grouped-bar-chart)
- [Line Chart](#line-chart)
- [Multi-Line Chart](#multi-line-chart)
- [Area Chart](#area-chart)
- [Scatter Plot](#scatter-plot)
- [Pie / Donut Chart](#pie--donut-chart)
- [Heatmap](#heatmap)
- [Chord Diagram](#chord-diagram)
- [Force-Directed Network](#force-directed-network)
- [Treemap](#treemap)
- [Scales Quick Reference](#scales-quick-reference)

---

## Bar Chart

```tsx
import { useRef, useEffect } from 'react';
import * as d3 from 'd3';

interface BarDatum {
  category: string;
  value: number;
}

interface BarChartProps {
  data: BarDatum[];
  width?: number;
  height?: number;
  color?: string;
}

export function BarChart({ data, width = 800, height = 400, color = 'steelblue' }: BarChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const innerW = width - margin.left - margin.right;
    const innerH = height - margin.top - margin.bottom;

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleBand().domain(data.map((d) => d.category)).range([0, innerW]).padding(0.1);
    const y = d3.scaleLinear().domain([0, d3.max(data, (d) => d.value) ?? 0]).range([innerH, 0]).nice();

    g.append('g').attr('transform', `translate(0,${innerH})`).call(d3.axisBottom(x));
    g.append('g').call(d3.axisLeft(y));

    g.selectAll('rect')
      .data(data)
      .join('rect')
      .attr('x', (d) => x(d.category)!)
      .attr('y', (d) => y(d.value))
      .attr('width', x.bandwidth())
      .attr('height', (d) => innerH - y(d.value))
      .attr('fill', color);

    return () => { svg.selectAll('*').remove(); };
  }, [data, width, height, color]);

  return <svg ref={svgRef} width={width} height={height} role="img" aria-label="Bar chart" />;
}
```

## Grouped Bar Chart

```tsx
interface GroupedDatum {
  category: string;
  [key: string]: string | number;
}

function drawGroupedBarChart(
  svgEl: SVGSVGElement,
  data: GroupedDatum[],
  keys: string[],
  width: number,
  height: number
) {
  const svg = d3.select(svgEl);
  svg.selectAll('*').remove();

  const margin = { top: 20, right: 30, bottom: 40, left: 50 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const x0 = d3.scaleBand().domain(data.map((d) => d.category)).range([0, innerW]).padding(0.2);
  const x1 = d3.scaleBand().domain(keys).range([0, x0.bandwidth()]).padding(0.05);
  const y = d3.scaleLinear()
    .domain([0, d3.max(data, (d) => d3.max(keys, (k) => d[k] as number)) ?? 0])
    .range([innerH, 0]).nice();
  const color = d3.scaleOrdinal(d3.schemeCategory10).domain(keys);

  g.append('g').attr('transform', `translate(0,${innerH})`).call(d3.axisBottom(x0));
  g.append('g').call(d3.axisLeft(y));

  const groups = g.selectAll('g.group').data(data).join('g')
    .attr('class', 'group')
    .attr('transform', (d) => `translate(${x0(d.category)},0)`);

  groups.selectAll('rect')
    .data((d) => keys.map((k) => ({ key: k, value: d[k] as number })))
    .join('rect')
    .attr('x', (d) => x1(d.key)!)
    .attr('y', (d) => y(d.value))
    .attr('width', x1.bandwidth())
    .attr('height', (d) => innerH - y(d.value))
    .attr('fill', (d) => color(d.key));
}
```

## Line Chart

```tsx
interface LineDatum {
  date: Date;
  value: number;
}

function drawLineChart(svgEl: SVGSVGElement, data: LineDatum[], width: number, height: number) {
  const svg = d3.select(svgEl);
  svg.selectAll('*').remove();

  const margin = { top: 20, right: 30, bottom: 40, left: 50 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3.scaleTime()
    .domain(d3.extent(data, (d) => d.date) as [Date, Date])
    .range([0, innerW]);

  const y = d3.scaleLinear()
    .domain([0, d3.max(data, (d) => d.value) ?? 0])
    .range([innerH, 0]).nice();

  g.append('g').attr('transform', `translate(0,${innerH})`).call(d3.axisBottom(x));
  g.append('g').call(d3.axisLeft(y));

  const line = d3.line<LineDatum>()
    .x((d) => x(d.date))
    .y((d) => y(d.value))
    .curve(d3.curveMonotoneX);

  g.append('path')
    .datum(data)
    .attr('fill', 'none')
    .attr('stroke', 'steelblue')
    .attr('stroke-width', 2)
    .attr('d', line);
}
```

## Multi-Line Chart

```tsx
interface Series {
  name: string;
  values: { date: Date; value: number }[];
}

function drawMultiLineChart(svgEl: SVGSVGElement, series: Series[], width: number, height: number) {
  const svg = d3.select(svgEl);
  svg.selectAll('*').remove();

  const margin = { top: 20, right: 80, bottom: 40, left: 50 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const allDates = series.flatMap((s) => s.values.map((v) => v.date));
  const allValues = series.flatMap((s) => s.values.map((v) => v.value));

  const x = d3.scaleTime().domain(d3.extent(allDates) as [Date, Date]).range([0, innerW]);
  const y = d3.scaleLinear().domain([0, d3.max(allValues) ?? 0]).range([innerH, 0]).nice();
  const color = d3.scaleOrdinal(d3.schemeCategory10).domain(series.map((s) => s.name));

  g.append('g').attr('transform', `translate(0,${innerH})`).call(d3.axisBottom(x));
  g.append('g').call(d3.axisLeft(y));

  const line = d3.line<{ date: Date; value: number }>()
    .x((d) => x(d.date))
    .y((d) => y(d.value))
    .curve(d3.curveMonotoneX);

  series.forEach((s) => {
    g.append('path')
      .datum(s.values)
      .attr('fill', 'none')
      .attr('stroke', color(s.name))
      .attr('stroke-width', 2)
      .attr('d', line);

    // Label at end of line
    const last = s.values[s.values.length - 1];
    g.append('text')
      .attr('x', x(last.date) + 5)
      .attr('y', y(last.value))
      .attr('dy', '0.35em')
      .attr('fill', color(s.name))
      .style('font-size', '12px')
      .text(s.name);
  });
}
```

## Area Chart

```tsx
function drawAreaChart(svgEl: SVGSVGElement, data: LineDatum[], width: number, height: number) {
  const svg = d3.select(svgEl);
  svg.selectAll('*').remove();

  const margin = { top: 20, right: 30, bottom: 40, left: 50 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3.scaleTime()
    .domain(d3.extent(data, (d) => d.date) as [Date, Date])
    .range([0, innerW]);
  const y = d3.scaleLinear()
    .domain([0, d3.max(data, (d) => d.value) ?? 0])
    .range([innerH, 0]).nice();

  g.append('g').attr('transform', `translate(0,${innerH})`).call(d3.axisBottom(x));
  g.append('g').call(d3.axisLeft(y));

  const area = d3.area<LineDatum>()
    .x((d) => x(d.date))
    .y0(innerH)
    .y1((d) => y(d.value))
    .curve(d3.curveMonotoneX);

  g.append('path')
    .datum(data)
    .attr('fill', 'steelblue')
    .attr('fill-opacity', 0.3)
    .attr('stroke', 'steelblue')
    .attr('stroke-width', 2)
    .attr('d', area);
}
```

## Scatter Plot

```tsx
interface ScatterDatum {
  x: number;
  y: number;
  size?: number;
  category?: string;
  label?: string;
}

function drawScatterPlot(svgEl: SVGSVGElement, data: ScatterDatum[], width: number, height: number) {
  const svg = d3.select(svgEl);
  svg.selectAll('*').remove();

  const margin = { top: 20, right: 30, bottom: 40, left: 50 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const xScale = d3.scaleLinear()
    .domain(d3.extent(data, (d) => d.x) as [number, number])
    .range([0, innerW]).nice();
  const yScale = d3.scaleLinear()
    .domain(d3.extent(data, (d) => d.y) as [number, number])
    .range([innerH, 0]).nice();
  const sizeScale = d3.scaleSqrt()
    .domain([0, d3.max(data, (d) => d.size ?? 1) ?? 1])
    .range([3, 15]);
  const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

  g.append('g').attr('transform', `translate(0,${innerH})`).call(d3.axisBottom(xScale));
  g.append('g').call(d3.axisLeft(yScale));

  g.selectAll('circle')
    .data(data)
    .join('circle')
    .attr('cx', (d) => xScale(d.x))
    .attr('cy', (d) => yScale(d.y))
    .attr('r', (d) => sizeScale(d.size ?? 1))
    .attr('fill', (d) => colorScale(d.category ?? 'default'))
    .attr('opacity', 0.7);
}
```

## Pie / Donut Chart

```tsx
interface PieDatum {
  label: string;
  value: number;
}

function drawPieChart(
  svgEl: SVGSVGElement,
  data: PieDatum[],
  width: number,
  height: number,
  donut = false
) {
  const svg = d3.select(svgEl);
  svg.selectAll('*').remove();

  const radius = Math.min(width, height) / 2 - 20;
  const g = svg.append('g').attr('transform', `translate(${width / 2},${height / 2})`);

  const pie = d3.pie<PieDatum>().value((d) => d.value).sort(null);
  const arc = d3.arc<d3.PieArcDatum<PieDatum>>()
    .innerRadius(donut ? radius * 0.5 : 0)
    .outerRadius(radius);
  const color = d3.scaleOrdinal(d3.schemeCategory10);

  g.selectAll('path')
    .data(pie(data))
    .join('path')
    .attr('d', arc)
    .attr('fill', (_, i) => color(String(i)))
    .attr('stroke', 'white')
    .attr('stroke-width', 2);

  // Labels
  const labelArc = d3.arc<d3.PieArcDatum<PieDatum>>()
    .innerRadius(radius * 0.7)
    .outerRadius(radius * 0.7);

  g.selectAll('text')
    .data(pie(data))
    .join('text')
    .attr('transform', (d) => `translate(${labelArc.centroid(d)})`)
    .attr('text-anchor', 'middle')
    .attr('dy', '0.35em')
    .style('font-size', '12px')
    .text((d) => d.data.label);
}
```

## Heatmap

```tsx
interface HeatmapDatum {
  row: string;
  column: string;
  value: number;
}

function drawHeatmap(svgEl: SVGSVGElement, data: HeatmapDatum[], width: number, height: number) {
  const svg = d3.select(svgEl);
  svg.selectAll('*').remove();

  const margin = { top: 60, right: 30, bottom: 30, left: 80 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  const rows = Array.from(new Set(data.map((d) => d.row)));
  const columns = Array.from(new Set(data.map((d) => d.column)));

  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3.scaleBand().domain(columns).range([0, innerW]).padding(0.01);
  const y = d3.scaleBand().domain(rows).range([0, innerH]).padding(0.01);
  const color = d3.scaleSequential(d3.interpolateYlOrRd)
    .domain([0, d3.max(data, (d) => d.value) ?? 1]);

  g.selectAll('rect')
    .data(data)
    .join('rect')
    .attr('x', (d) => x(d.column)!)
    .attr('y', (d) => y(d.row)!)
    .attr('width', x.bandwidth())
    .attr('height', y.bandwidth())
    .attr('fill', (d) => color(d.value));

  // Column labels
  g.selectAll('.col-label')
    .data(columns)
    .join('text')
    .attr('class', 'col-label')
    .attr('x', (d) => x(d)! + x.bandwidth() / 2)
    .attr('y', -10)
    .attr('text-anchor', 'middle')
    .style('font-size', '12px')
    .text((d) => d);

  // Row labels
  g.selectAll('.row-label')
    .data(rows)
    .join('text')
    .attr('class', 'row-label')
    .attr('x', -10)
    .attr('y', (d) => y(d)! + y.bandwidth() / 2)
    .attr('dy', '0.35em')
    .attr('text-anchor', 'end')
    .style('font-size', '12px')
    .text((d) => d);
}
```

## Chord Diagram

```tsx
interface ChordDatum {
  source: string;
  target: string;
  value: number;
}

function drawChordDiagram(svgEl: SVGSVGElement, data: ChordDatum[], width: number, height: number) {
  const svg = d3.select(svgEl);
  svg.selectAll('*').remove();

  const innerRadius = Math.min(width, height) * 0.3;
  const outerRadius = innerRadius + 30;

  const nodes = Array.from(new Set(data.flatMap((d) => [d.source, d.target])));
  const matrix = Array.from({ length: nodes.length }, () => Array(nodes.length).fill(0));

  data.forEach((d) => {
    const i = nodes.indexOf(d.source);
    const j = nodes.indexOf(d.target);
    matrix[i][j] += d.value;
    matrix[j][i] += d.value;
  });

  const chord = d3.chord().padAngle(0.05).sortSubgroups(d3.descending);
  const arc = d3.arc<d3.ChordGroup>().innerRadius(innerRadius).outerRadius(outerRadius);
  const ribbon = d3.ribbon().radius(innerRadius);
  const color = d3.scaleOrdinal(d3.schemeCategory10).domain(nodes);

  const g = svg.append('g').attr('transform', `translate(${width / 2},${height / 2})`);
  const chords = chord(matrix);

  g.append('g')
    .attr('fill-opacity', 0.67)
    .selectAll('path')
    .data(chords)
    .join('path')
    .attr('d', ribbon as any)
    .attr('fill', (d) => color(nodes[d.source.index]))
    .attr('stroke', (d) => d3.rgb(color(nodes[d.source.index])).darker().toString());

  const group = g.append('g').selectAll('g').data(chords.groups).join('g');

  group.append('path')
    .attr('d', arc as any)
    .attr('fill', (d) => color(nodes[d.index]))
    .attr('stroke', (d) => d3.rgb(color(nodes[d.index])).darker().toString());

  group.append('text')
    .each((d: any) => { d.angle = (d.startAngle + d.endAngle) / 2; })
    .attr('dy', '0.31em')
    .attr('transform', (d: any) =>
      `rotate(${(d.angle * 180 / Math.PI) - 90})translate(${outerRadius + 10})${d.angle > Math.PI ? 'rotate(180)' : ''}`
    )
    .attr('text-anchor', (d: any) => (d.angle > Math.PI ? 'end' : null))
    .style('font-size', '12px')
    .text((_, i) => nodes[i]);
}
```

## Force-Directed Network

```tsx
interface Node extends d3.SimulationNodeDatum {
  id: string;
  group?: string;
}

interface Link extends d3.SimulationLinkDatum<Node> {
  source: string;
  target: string;
  value?: number;
}

function drawForceGraph(
  svgEl: SVGSVGElement,
  nodes: Node[],
  links: Link[],
  width: number,
  height: number
) {
  const svg = d3.select(svgEl);
  svg.selectAll('*').remove();

  const color = d3.scaleOrdinal(d3.schemeCategory10);

  const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink<Node, Link>(links).id((d) => d.id).distance(100))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2));

  const link = svg.append('g')
    .selectAll('line')
    .data(links)
    .join('line')
    .attr('stroke', '#999')
    .attr('stroke-opacity', 0.6)
    .attr('stroke-width', (d) => Math.sqrt(d.value ?? 1));

  const node = svg.append('g')
    .selectAll('circle')
    .data(nodes)
    .join('circle')
    .attr('r', 8)
    .attr('fill', (d) => color(d.group ?? 'default'))
    .call(
      d3.drag<SVGCircleElement, Node>()
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
        })
    );

  // Labels
  const label = svg.append('g')
    .selectAll('text')
    .data(nodes)
    .join('text')
    .text((d) => d.id)
    .attr('font-size', '10px')
    .attr('dx', 12)
    .attr('dy', '0.35em');

  simulation.on('tick', () => {
    link
      .attr('x1', (d: any) => d.source.x)
      .attr('y1', (d: any) => d.source.y)
      .attr('x2', (d: any) => d.target.x)
      .attr('y2', (d: any) => d.target.y);
    node.attr('cx', (d) => d.x!).attr('cy', (d) => d.y!);
    label.attr('x', (d) => d.x!).attr('y', (d) => d.y!);
  });

  // Cleanup: stop simulation on unmount
  return () => simulation.stop();
}
```

## Treemap

```tsx
interface TreeNode {
  name: string;
  value?: number;
  children?: TreeNode[];
}

function drawTreemap(svgEl: SVGSVGElement, data: TreeNode, width: number, height: number) {
  const svg = d3.select(svgEl);
  svg.selectAll('*').remove();

  const root = d3.hierarchy(data)
    .sum((d) => d.value ?? 0)
    .sort((a, b) => (b.value ?? 0) - (a.value ?? 0));

  d3.treemap<TreeNode>().size([width, height]).padding(2)(root);

  const color = d3.scaleOrdinal(d3.schemeCategory10);

  const cell = svg.selectAll('g')
    .data(root.leaves())
    .join('g')
    .attr('transform', (d: any) => `translate(${d.x0},${d.y0})`);

  cell.append('rect')
    .attr('width', (d: any) => d.x1 - d.x0)
    .attr('height', (d: any) => d.y1 - d.y0)
    .attr('fill', (d) => color(d.parent?.data.name ?? ''))
    .attr('fill-opacity', 0.8);

  cell.append('text')
    .attr('x', 4)
    .attr('y', 14)
    .style('font-size', '11px')
    .text((d) => d.data.name);
}
```

---

## Scales Quick Reference

### Quantitative
```tsx
d3.scaleLinear().domain([0, 100]).range([0, 500]);
d3.scaleLog().domain([1, 1000]).range([0, 500]);
d3.scaleSqrt().domain([0, 100]).range([0, 30]);       // Good for bubble sizes
d3.scaleTime().domain([new Date(2020, 0), new Date(2025, 0)]).range([0, 500]);
```

### Ordinal
```tsx
d3.scaleBand().domain(['A', 'B', 'C']).range([0, 400]).padding(0.1);  // Bar charts
d3.scalePoint().domain(['A', 'B', 'C']).range([0, 400]);              // Dot plots
d3.scaleOrdinal(d3.schemeCategory10);                                   // Color categories
```

### Sequential (color)
```tsx
d3.scaleSequential(d3.interpolateBlues).domain([0, 100]);
d3.scaleSequential(d3.interpolateYlOrRd).domain([0, 100]);
d3.scaleDiverging(d3.interpolateRdBu).domain([-10, 0, 10]);
```
