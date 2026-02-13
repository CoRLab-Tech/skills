# Playwright MCP Commands Reference

## Essential Commands for Component Verification

### Navigation
```typescript
// Navigate to Storybook story
mcp1_browser_navigate("http://localhost:6008/iframe.html?id=organisms-componentname--default&viewMode=story")

// Navigate to main Storybook
mcp1_browser_navigate("http://localhost:6008")
```

### Screenshots
```typescript
// Full page screenshot
mcp1_browser_take_screenshot({
  filename: "component-desktop.png",
  type: "png",
  fullPage: true
})

// Viewport only screenshot
mcp1_browser_take_screenshot({
  filename: "component-viewport.png",
  type: "png",
  fullPage: false
})

// Element screenshot
mcp1_browser_take_screenshot({
  element: "Component container",
  ref: "e10", // from snapshot
  filename: "component-element.png",
  type: "png"
})
```

### Viewport Resizing
```typescript
// Mobile (iPhone 6)
mcp1_browser_resize(375, 667)

// Tablet (iPad)
mcp1_browser_resize(768, 1024)

// Desktop (common)
mcp1_browser_resize(1440, 900)

// Custom size
mcp1_browser_resize(width, height)
```

### Browser Control
```typescript
// Close browser (when stuck)
mcp1_browser_close()

// Get current snapshot
mcp1_browser_snapshot()

// Wait for element/time
mcp1_browser_wait_for({
  text: "Component loaded",
  time: 3 // seconds
})
```

## URL Patterns for Storybook

### Organism Components
```
http://localhost:6008/iframe.html?id=organisms-herosection--default
http://localhost:6008/iframe.html?id=organisms-statssection--default
http://localhost:6008/iframe.html?id=organisms-perimetersection--default
http://localhost:6008/iframe.html?id=organisms-showcasesection--default
http://localhost:6008/iframe.html?id=organisms-enterprisesection--default
http://localhost:6008/iframe.html?id=organisms-newslettersection--default
http://localhost:6008/iframe.html?id=organisms-businesssection--default
http://localhost:6008/iframe.html?id=organisms-footer--default
```

### Molecule Components
```
http://localhost:6008/iframe.html?id=molecules-statcard--default
http://localhost:6008/iframe.html?id=molecules-perimetercard--default
http://localhost:6008/iframe.html?id=molecules-enterprisecard--default
http://localhost:6008/iframe.html?id=molecules-featurecard--default
```

### Story Variants
```
// Mobile view
?id=organisms-componentname--mobile-view

// Tablet view
?id=organisms-componentname--tablet-view

// Desktop view
?id=organisms-componentname--desktop-view

// Custom story
?id=organisms-componentname--story-name
```

## Common Viewport Sizes

| Device | Width | Height | Use Case |
|--------|-------|--------|----------|
| iPhone SE | 375 | 667 | Small mobile |
| iPhone 12 | 390 | 844 | Standard mobile |
| iPad | 768 | 1024 | Tablet portrait |
| iPad Pro | 1024 | 1366 | Large tablet |
| Laptop | 1366 | 768 | Small laptop |
| Desktop | 1440 | 900 | Standard desktop |
| Large Desktop | 1920 | 1080 | Large screen |

## Troubleshooting

### Timeout Issues
```typescript
// If timeout occurs, restart browser
mcp1_browser_close()
// Then navigate again
mcp1_browser_navigate("http://localhost:6008")
```

### Snapshot Not Loading
```typescript
// Wait before taking snapshot
mcp1_browser_wait_for({ time: 2 })
// Then take screenshot
mcp1_browser_take_screenshot(...)
```

### Element Not Found
```typescript
// Get current snapshot first
mcp1_browser_snapshot()
// Find the ref in the output
// Use the ref in your command
mcp1_browser_click({ ref: "e123", element: "Button" })
```

## Verification Workflow

1. **Desktop First**
   ```typescript
   mcp1_browser_navigate(storyUrl)
   mcp1_browser_take_screenshot({ filename: "desktop.png", fullPage: true })
   ```

2. **Mobile Check**
   ```typescript
   mcp1_browser_resize(375, 667)
   mcp1_browser_take_screenshot({ filename: "mobile.png", fullPage: true })
   ```

3. **Tablet Check**
   ```typescript
   mcp1_browser_resize(768, 1024)
   mcp1_browser_take_screenshot({ filename: "tablet.png", fullPage: true })
   ```

4. **Return to Desktop**
   ```typescript
   mcp1_browser_resize(1440, 900)
   ```
