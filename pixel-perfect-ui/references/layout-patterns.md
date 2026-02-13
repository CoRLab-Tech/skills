# Layout Patterns

## Flexbox Layouts

### Centered Content

```css
/* Perfect centering */
.center-content {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}

/* Tailwind */
<div className="flex items-center justify-center min-h-screen">
```

### Holy Grail Layout

```typescript
const HolyGrailLayout = ({ header, sidebar, content, aside, footer }) => (
  <div className="flex flex-col min-h-screen">
    {/* Header */}
    <header className="bg-white border-b">
      {header}
    </header>
    
    {/* Main content area */}
    <div className="flex-1 flex">
      {/* Left sidebar */}
      <aside className="w-64 bg-gray-50 border-r">
        {sidebar}
      </aside>
      
      {/* Main content */}
      <main className="flex-1 p-6">
        {content}
      </main>
      
      {/* Right sidebar */}
      <aside className="w-64 bg-gray-50 border-l">
        {aside}
      </aside>
    </div>
    
    {/* Footer */}
    <footer className="bg-white border-t">
      {footer}
    </footer>
  </div>
);
```

### Split Screen

```typescript
const SplitScreen = ({ left, right, ratio = "50/50" }) => {
  const getRatio = () => {
    switch(ratio) {
      case "30/70": return ["w-[30%]", "w-[70%]"];
      case "40/60": return ["w-[40%]", "w-[60%]"];
      case "60/40": return ["w-[60%]", "w-[40%]"];
      case "70/30": return ["w-[70%]", "w-[30%]"];
      default: return ["w-1/2", "w-1/2"];
    }
  };
  
  const [leftWidth, rightWidth] = getRatio();
  
  return (
    <div className="flex h-screen">
      <div className={`${leftWidth} overflow-y-auto`}>
        {left}
      </div>
      <div className={`${rightWidth} overflow-y-auto`}>
        {right}
      </div>
    </div>
  );
};
```

## Grid Layouts

### Dashboard Grid

```typescript
const DashboardGrid = ({ widgets }) => (
  <div className="grid grid-cols-12 gap-6 p-6">
    {widgets.map((widget) => (
      <div
        key={widget.id}
        className={`
          col-span-12
          ${widget.size === 'small' ? 'md:col-span-3' : ''}
          ${widget.size === 'medium' ? 'md:col-span-6' : ''}
          ${widget.size === 'large' ? 'md:col-span-9' : ''}
          ${widget.size === 'full' ? 'md:col-span-12' : ''}
        `}
      >
        {widget.content}
      </div>
    ))}
  </div>
);
```

### Feature Grid

```typescript
const FeatureGrid = ({ features }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
    {features.map((feature, index) => (
      <div 
        key={index}
        className="flex flex-col items-center text-center p-6"
      >
        <div className="w-16 h-16 mb-4 flex items-center justify-center bg-blue-100 rounded-full">
          {feature.icon}
        </div>
        <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
        <p className="text-gray-600">{feature.description}</p>
      </div>
    ))}
  </div>
);
```

## Container Patterns

### Max Width Container

```typescript
const Container = ({ children, size = 'default' }) => {
  const sizes = {
    'sm': 'max-w-3xl',
    'default': 'max-w-5xl',
    'lg': 'max-w-7xl',
    'full': 'max-w-full'
  };
  
  return (
    <div className={`${sizes[size]} mx-auto px-4 sm:px-6 lg:px-8`}>
      {children}
    </div>
  );
};
```

### Responsive Padding Container

```typescript
const ResponsiveContainer = ({ children }) => (
  <div className="px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16">
    {children}
  </div>
);
```

## Hero Sections

### Centered Hero

```typescript
const CenteredHero = ({ title, subtitle, cta }) => (
  <section className="relative bg-white">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-32">
      <div className="text-center">
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
          {title}
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
          {subtitle}
        </p>
        <div className="flex gap-4 justify-center">
          {cta}
        </div>
      </div>
    </div>
  </section>
);
```

### Split Hero

```typescript
const SplitHero = ({ title, subtitle, cta, image }) => (
  <section className="relative bg-white">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center py-24">
        <div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            {title}
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            {subtitle}
          </p>
          <div className="flex gap-4">
            {cta}
          </div>
        </div>
        <div className="relative">
          <img 
            src={image} 
            alt="Hero" 
            className="w-full h-auto rounded-lg shadow-xl"
          />
        </div>
      </div>
    </div>
  </section>
);
```

## Sticky Layouts

### Sticky Header

```typescript
const StickyHeader = ({ children }) => (
  <header className="sticky top-0 z-50 bg-white border-b backdrop-blur-sm bg-white/95">
    {children}
  </header>
);
```

### Sticky Sidebar

```typescript
const StickySidebar = ({ sidebar, content }) => (
  <div className="flex gap-8">
    <aside className="w-64 flex-shrink-0">
      <div className="sticky top-20">
        {sidebar}
      </div>
    </aside>
    <main className="flex-1 min-w-0">
      {content}
    </main>
  </div>
);
```

## Responsive Patterns

### Mobile-First Stack

```typescript
const MobileFirstLayout = ({ items }) => (
  <div className="flex flex-col md:flex-row gap-6">
    {items.map((item, index) => (
      <div key={index} className="flex-1">
        {item}
      </div>
    ))}
  </div>
);
```

### Hide/Show by Breakpoint

```typescript
const ResponsiveLayout = ({ mobile, tablet, desktop }) => (
  <>
    {/* Mobile only */}
    <div className="block md:hidden">
      {mobile}
    </div>
    
    {/* Tablet only */}
    <div className="hidden md:block lg:hidden">
      {tablet}
    </div>
    
    {/* Desktop only */}
    <div className="hidden lg:block">
      {desktop}
    </div>
  </>
);
```

## Spacing Patterns

### Consistent Vertical Rhythm

```typescript
const VerticalRhythm = ({ children }) => (
  <div className="space-y-8">
    {React.Children.map(children, (child) => (
      <div>{child}</div>
    ))}
  </div>
);
```

### Section Spacing

```typescript
const Section = ({ children, spacing = 'default' }) => {
  const spacingMap = {
    'none': 'py-0',
    'small': 'py-8 md:py-12',
    'default': 'py-12 md:py-16 lg:py-20',
    'large': 'py-16 md:py-24 lg:py-32'
  };
  
  return (
    <section className={spacingMap[spacing]}>
      {children}
    </section>
  );
};
```

## Alignment Patterns

### Baseline Grid Alignment

```css
/* Establish baseline grid */
.baseline-grid {
  line-height: 1.5rem; /* 24px baseline */
}

.baseline-grid > * {
  margin-bottom: 1.5rem; /* Maintain baseline */
}

/* Headings maintain baseline */
.baseline-grid h1 { line-height: 3rem; margin-bottom: 1.5rem; }
.baseline-grid h2 { line-height: 2.25rem; margin-bottom: 1.5rem; }
.baseline-grid h3 { line-height: 1.5rem; margin-bottom: 1.5rem; }
```

### Optical Alignment

```typescript
// Adjust for visual weight
const OpticallyAlignedIcon = ({ icon, size = 24 }) => (
  <div 
    className="flex items-center justify-center"
    style={{
      width: size,
      height: size,
      // Optical adjustment for visual centering
      marginTop: -2,
      marginLeft: -2
    }}
  >
    {icon}
  </div>
);
```

## Z-Index Management

```css
/* Z-index scale */
:root {
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-fixed: 300;
  --z-modal-backdrop: 400;
  --z-modal: 500;
  --z-popover: 600;
  --z-tooltip: 700;
  --z-notification: 800;
}

/* Usage */
.dropdown { z-index: var(--z-dropdown); }
.sticky-header { z-index: var(--z-sticky); }
.modal-backdrop { z-index: var(--z-modal-backdrop); }
.modal { z-index: var(--z-modal); }
```
