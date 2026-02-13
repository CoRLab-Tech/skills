# Responsive Patterns - PRODUCTION READY

## 🚨 CRITICAL: Never Use Hardcoded Widths

### ❌ FORBIDDEN Patterns
```jsx
// NEVER DO THIS
<div className="w-[1728px]">  // Breaks on mobile
<div style={{width: '1728px'}}>  // Causes horizontal scroll
<div className="min-w-[1200px]">  // Forces overflow
```

### ✅ REQUIRED Patterns
```jsx
// ALWAYS DO THIS
<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
<div className="w-full max-w-screen-xl">
<div className="container mx-auto">
```

## Mobile-First Container Pattern

### Standard Responsive Container
```jsx
// Use for all main content sections
const Container = ({ children }) => (
  <div className="w-full">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {children}
    </div>
  </div>
);

// Breakpoint-specific padding
// Mobile: px-4 (16px)
// Tablet: px-6 (24px)  
// Desktop: px-8 (32px)
```

### Full-Width with Constrained Content
```jsx
// Background full width, content constrained
<section className="bg-gray-50">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-20">
    {/* Content here */}
  </div>
</section>
```

## Responsive Typography

### Font Size Scaling
```jsx
// Mobile-first font sizing
<h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl">
  Responsive Heading
</h1>

<p className="text-sm sm:text-base lg:text-lg">
  Body text that scales appropriately
</p>

// Line height adjustments
<p className="text-base leading-relaxed sm:text-lg sm:leading-loose">
  Comfortable reading on all devices
</p>
```

### Readable Text Widths
```jsx
// Prevent text from spanning full width on large screens
<div className="max-w-prose mx-auto">
  <p>This text won't exceed ~65-75 characters for optimal readability</p>
</div>

// Alternative max-widths
// max-w-prose (~65ch)
// max-w-3xl (48rem)
// max-w-4xl (56rem)
```

## Responsive Grid Patterns

### Mobile-First Grid
```jsx
// Stack on mobile, grid on larger screens
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
  {items.map(item => (
    <div key={item.id}>{/* Card content */}</div>
  ))}
</div>

// Two-column with responsive gap
<div className="grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-12">
  <div>Left content</div>
  <div>Right content</div>
</div>
```

### Flexible Card Grid
```jsx
// Auto-fit grid that responds to content
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
  {cards.map(card => (
    <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
      {/* Card with responsive padding */}
    </div>
  ))}
</div>
```

## Responsive Flexbox

### Stack to Row Pattern
```jsx
// Vertical on mobile, horizontal on desktop
<div className="flex flex-col sm:flex-row gap-4 sm:gap-6 lg:gap-8">
  <div className="flex-1">First item</div>
  <div className="flex-1">Second item</div>
</div>

// Reverse order on mobile
<div className="flex flex-col-reverse sm:flex-row">
  <div className="sm:w-1/2">Content</div>
  <div className="sm:w-1/2">Image</div>
</div>
```

### Responsive Alignment
```jsx
// Center on mobile, space-between on desktop
<div className="flex flex-col sm:flex-row items-center sm:items-start justify-center sm:justify-between">
  <div>Logo</div>
  <nav>Menu items</nav>
</div>
```

## Image Handling

### Responsive Images with Next.js
```jsx
// CRITICAL: Always export images from Figma first!
import Image from 'next/image';

// Responsive image that maintains aspect ratio
<div className="relative w-full aspect-video">
  <Image
    src="/assets/hero-image.png"  // Exported from Figma
    alt="Descriptive alt text"
    fill
    className="object-cover"
    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
    priority
  />
</div>

// Image with responsive sizing
<Image
  src="/assets/feature.png"
  alt="Feature"
  width={800}
  height={600}
  className="w-full h-auto"
  placeholder="blur"
  blurDataURL="..."  // Optional blur placeholder
/>
```

### Background Images
```jsx
// Responsive background with overlay
<div className="relative min-h-[300px] sm:min-h-[400px] lg:min-h-[500px]">
  <Image
    src="/assets/bg-image.png"
    alt=""
    fill
    className="object-cover"
  />
  <div className="absolute inset-0 bg-black/50" />
  <div className="relative z-10 p-4 sm:p-6 lg:p-8">
    {/* Content over image */}
  </div>
</div>
```

## Navigation Patterns

### Mobile-First Navigation
```jsx
const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Logo />
          </div>
          
          {/* Desktop menu */}
          <div className="hidden sm:flex sm:items-center sm:space-x-8">
            {navItems.map(item => (
              <a key={item.id} href={item.href} className="text-gray-700 hover:text-gray-900">
                {item.label}
              </a>
            ))}
          </div>
          
          {/* Mobile menu button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="sm:hidden p-2"
            aria-label="Toggle menu"
          >
            <MenuIcon />
          </button>
        </div>
      </div>
      
      {/* Mobile menu */}
      {isOpen && (
        <div className="sm:hidden border-t">
          <div className="px-4 py-2 space-y-2">
            {navItems.map(item => (
              <a
                key={item.id}
                href={item.href}
                className="block py-2 text-gray-700"
              >
                {item.label}
              </a>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
};
```

## Touch-Friendly Interactions

### Minimum Touch Targets
```jsx
// Ensure 44x44px minimum touch targets
<button className="min-h-[44px] min-w-[44px] p-3 rounded-lg">
  Click Me
</button>

// Touch-friendly spacing between elements
<div className="space-y-4">
  <button className="w-full py-3 px-4">First Action</button>
  <button className="w-full py-3 px-4">Second Action</button>
</div>
```

### Hover and Focus States
```jsx
// Clear interactive states for all devices
<button className="
  bg-blue-600 text-white
  hover:bg-blue-700
  focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
  active:bg-blue-800
  transition-colors
">
  Interactive Button
</button>
```

## Responsive Spacing

### Breakpoint-Based Spacing
```jsx
// Spacing that adapts to screen size
<section className="py-8 sm:py-12 md:py-16 lg:py-20 xl:py-24">
  <div className="space-y-4 sm:space-y-6 lg:space-y-8">
    {/* Content with responsive vertical spacing */}
  </div>
</section>

// Responsive margins
<div className="mt-4 sm:mt-6 md:mt-8 lg:mt-10">
  {/* Content */}
</div>
```

## Overflow Prevention

### Horizontal Scroll Prevention
```jsx
// Root level overflow control
<body className="overflow-x-hidden">
  <div className="min-h-screen">
    {/* All content */}
  </div>
</body>

// Section-level overflow handling
<section className="w-full overflow-x-hidden">
  <div className="max-w-7xl mx-auto">
    {/* Safe content area */}
  </div>
</section>
```

### Text Overflow
```jsx
// Prevent long text from breaking layout
<p className="truncate">
  Very long text that could break the layout...
</p>

// Multi-line truncation
<p className="line-clamp-3">
  Long paragraph that will be truncated after three lines...
</p>
```

## Validation Checklist

Before considering any implementation production-ready:

```markdown
## Mobile (375px)
- [ ] No horizontal scroll
- [ ] All text readable (≥14px)
- [ ] Touch targets ≥44x44px
- [ ] Images loading correctly
- [ ] Content properly stacked

## Tablet (768px)
- [ ] Layout adjusts smoothly
- [ ] No content overflow
- [ ] Proper spacing maintained

## Desktop (1440px)
- [ ] Content not too wide
- [ ] Proper use of max-width
- [ ] No hardcoded widths

## Performance
- [ ] Images optimized
- [ ] Lazy loading implemented
- [ ] Proper loading states

## Accessibility
- [ ] Keyboard navigation works
- [ ] ARIA labels present
- [ ] Color contrast passes WCAG
```

## Common Mistakes to Avoid

### ❌ Never Do
```jsx
// Fixed widths that break responsiveness
width: 1728px
w-[1728px]
min-w-[1200px]

// Assuming desktop-first
@media (max-width: 768px)  // Should be min-width

// Ignoring mobile viewport
<meta name="viewport" content="width=1200">

// Fixed positioning without testing
position: fixed; left: 500px;
```

### ✅ Always Do
```jsx
// Flexible, responsive units
max-w-7xl
w-full max-w-screen-xl
width: 100%

// Mobile-first approach
@media (min-width: 768px)

// Proper viewport meta
<meta name="viewport" content="width=device-width, initial-scale=1">

// Test all viewports
375px, 768px, 1024px, 1440px
```
