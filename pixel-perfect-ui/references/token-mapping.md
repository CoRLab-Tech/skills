# Token Mapping Guide

## Figma to Tailwind Mapping

### Colors

```javascript
// Figma color to Tailwind
const colorMap = {
  // Primary colors
  '#3B82F6': 'blue-500',
  '#2563EB': 'blue-600',
  '#1D4ED8': 'blue-700',
  
  // Neutral colors
  '#F9FAFB': 'gray-50',
  '#F3F4F6': 'gray-100',
  '#E5E7EB': 'gray-200',
  '#D1D5DB': 'gray-300',
  '#9CA3AF': 'gray-400',
  '#6B7280': 'gray-500',
  '#4B5563': 'gray-600',
  '#374151': 'gray-700',
  '#1F2937': 'gray-800',
  '#111827': 'gray-900'
}
```

### Typography Scale

```javascript
// Figma font size to Tailwind
const fontSizeMap = {
  '12px': 'text-xs',    // 0.75rem
  '14px': 'text-sm',    // 0.875rem
  '16px': 'text-base',  // 1rem
  '18px': 'text-lg',    // 1.125rem
  '20px': 'text-xl',    // 1.25rem
  '24px': 'text-2xl',   // 1.5rem
  '30px': 'text-3xl',   // 1.875rem
  '36px': 'text-4xl',   // 2.25rem
  '48px': 'text-5xl',   // 3rem
  '60px': 'text-6xl',   // 3.75rem
  '72px': 'text-7xl',   // 4.5rem
  '96px': 'text-8xl',   // 6rem
  '128px': 'text-9xl'   // 8rem
}

// Font weight mapping
const fontWeightMap = {
  '100': 'font-thin',
  '200': 'font-extralight',
  '300': 'font-light',
  '400': 'font-normal',
  '500': 'font-medium',
  '600': 'font-semibold',
  '700': 'font-bold',
  '800': 'font-extrabold',
  '900': 'font-black'
}
```

### Spacing System

```javascript
// Figma spacing to Tailwind (4px base)
const spacingMap = {
  '0px': '0',
  '1px': 'px',
  '2px': '0.5',     // 0.125rem
  '4px': '1',       // 0.25rem
  '6px': '1.5',     // 0.375rem
  '8px': '2',       // 0.5rem
  '10px': '2.5',    // 0.625rem
  '12px': '3',      // 0.75rem
  '14px': '3.5',    // 0.875rem
  '16px': '4',      // 1rem
  '20px': '5',      // 1.25rem
  '24px': '6',      // 1.5rem
  '28px': '7',      // 1.75rem
  '32px': '8',      // 2rem
  '36px': '9',      // 2.25rem
  '40px': '10',     // 2.5rem
  '44px': '11',     // 2.75rem
  '48px': '12',     // 3rem
  '56px': '14',     // 3.5rem
  '64px': '16',     // 4rem
  '80px': '20',     // 5rem
  '96px': '24',     // 6rem
  '112px': '28',    // 7rem
  '128px': '32',    // 8rem
  '144px': '36',    // 9rem
  '160px': '40',    // 10rem
  '176px': '44',    // 11rem
  '192px': '48',    // 12rem
  '208px': '52',    // 13rem
  '224px': '56',    // 14rem
  '240px': '60',    // 15rem
  '256px': '64',    // 16rem
  '288px': '72',    // 18rem
  '320px': '80',    // 20rem
  '384px': '96'     // 24rem
}
```

### Border Radius

```javascript
// Figma radius to Tailwind
const radiusMap = {
  '0px': 'rounded-none',
  '2px': 'rounded-sm',     // 0.125rem
  '4px': 'rounded',        // 0.25rem
  '6px': 'rounded-md',     // 0.375rem
  '8px': 'rounded-lg',     // 0.5rem
  '12px': 'rounded-xl',    // 0.75rem
  '16px': 'rounded-2xl',   // 1rem
  '24px': 'rounded-3xl',   // 1.5rem
  '9999px': 'rounded-full'
}
```

## Figma to CSS Variables

### Setup CSS Variables

```css
:root {
  /* Colors */
  --color-primary: #3B82F6;
  --color-primary-hover: #2563EB;
  --color-secondary: #8B5CF6;
  --color-text: #1F2937;
  --color-text-muted: #6B7280;
  --color-background: #FFFFFF;
  --color-surface: #F9FAFB;
  
  /* Typography */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'Fira Code', monospace;
  
  /* Spacing */
  --space-1: 0.25rem;  /* 4px */
  --space-2: 0.5rem;   /* 8px */
  --space-3: 0.75rem;  /* 12px */
  --space-4: 1rem;     /* 16px */
  --space-5: 1.25rem;  /* 20px */
  --space-6: 1.5rem;   /* 24px */
  --space-8: 2rem;     /* 32px */
  --space-10: 2.5rem;  /* 40px */
  --space-12: 3rem;    /* 48px */
  --space-16: 4rem;    /* 64px */
  
  /* Border radius */
  --radius-sm: 0.125rem;  /* 2px */
  --radius-md: 0.375rem;  /* 6px */
  --radius-lg: 0.5rem;    /* 8px */
  --radius-xl: 0.75rem;   /* 12px */
  --radius-2xl: 1rem;     /* 16px */
  --radius-full: 9999px;
}
```

## Shadow Conversion

### Figma Shadow to CSS

```javascript
function convertFigmaShadow(figmaShadow) {
  // Figma format: { x, y, blur, spread, color, opacity }
  const { x, y, blur, spread, color, opacity } = figmaShadow;
  
  // Convert color to rgba
  const rgba = hexToRgba(color, opacity);
  
  // CSS format: x y blur spread color
  return `${x}px ${y}px ${blur}px ${spread}px ${rgba}`;
}

// Common shadow mappings
const shadowMap = {
  'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  'base': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
}
```

## Gradient Conversion

### Figma Gradient to CSS

```javascript
function convertFigmaGradient(gradient) {
  const { type, stops, angle } = gradient;
  
  if (type === 'LINEAR') {
    const cssStops = stops.map(stop => 
      `${hexToRgba(stop.color, stop.opacity)} ${stop.position * 100}%`
    ).join(', ');
    
    return `linear-gradient(${angle}deg, ${cssStops})`;
  }
  
  if (type === 'RADIAL') {
    const cssStops = stops.map(stop => 
      `${hexToRgba(stop.color, stop.opacity)} ${stop.position * 100}%`
    ).join(', ');
    
    return `radial-gradient(circle, ${cssStops})`;
  }
}
```

## Line Height Mapping

```javascript
// Figma line height to CSS
const lineHeightMap = {
  'AUTO': 'normal',
  '100%': '1',
  '110%': '1.1',
  '120%': '1.2',
  '130%': '1.3',
  '140%': '1.4',
  '150%': '1.5',
  '160%': '1.6',
  '170%': '1.7',
  '175%': '1.75',
  '180%': '1.8',
  '200%': '2'
}

// Tailwind line height classes
const tailwindLineHeight = {
  '1': 'leading-none',
  '1.25': 'leading-tight',
  '1.375': 'leading-snug',
  '1.5': 'leading-normal',
  '1.625': 'leading-relaxed',
  '2': 'leading-loose'
}
```

## Letter Spacing Mapping

```javascript
// Figma letter spacing to Tailwind
const letterSpacingMap = {
  '-0.05em': 'tracking-tighter',
  '-0.025em': 'tracking-tight',
  '0': 'tracking-normal',
  '0.025em': 'tracking-wide',
  '0.05em': 'tracking-wider',
  '0.1em': 'tracking-widest'
}
```
