# Figma MCP Commands Reference

## Essential Commands for Design Extraction

### Get Design Context
Extracts the actual component code from Figma design.

```typescript
mcp0_get_design_context({
  nodeId: "2473:15690", // Node ID from Figma
  clientLanguages: "typescript,html,css",
  clientFrameworks: "react,nextjs,tailwindcss"
})
```

**Returns:** React component code with Tailwind classes that needs to be adapted to your project's design system.

### Get Screenshot
Captures a visual of the Figma design for comparison.

```typescript
mcp0_get_screenshot({
  nodeId: "2473:15690",
  clientLanguages: "typescript,html,css", 
  clientFrameworks: "react,nextjs,tailwindcss"
})
```

**Returns:** Screenshot image of the Figma design.

### Get Metadata
Explores Figma document structure when node IDs are unknown.

```typescript
mcp0_get_metadata({
  nodeId: "0:1", // Root node to explore from
  clientLanguages: "typescript,html,css",
  clientFrameworks: "react,nextjs,tailwindcss"
})
```

**Returns:** XML structure showing node IDs and hierarchy.

### Get Variable Definitions
Extracts design tokens and variables from Figma.

```typescript
mcp0_get_variable_defs({
  nodeId: "2473:15690",
  clientLanguages: "typescript,html,css",
  clientFrameworks: "react,nextjs,tailwindcss"
})
```

**Returns:** Variable definitions like colors, spacing, etc.

### Create Design System Rules
Generates design system documentation.

```typescript
mcp0_create_design_system_rules({
  clientLanguages: "typescript,html,css",
  clientFrameworks: "react,nextjs,tailwindcss"
})
```

## Node ID Formats

Figma node IDs can appear in different formats:
- Colon format: `2473:15690`
- Dash format: `2473-15690`
- Both are valid and interchangeable

## Finding Node IDs

### From Documentation
Check existing analysis files:
```typescript
grep_search({
  SearchPath: "/figma-analysis",
  Query: "Node ID.*15690",
  MatchPerLine: true
})
```

### From Figma URL
Extract from URL patterns:
- `https://figma.com/design/:fileKey/:fileName?node-id=1-2` → Node ID: `1:2`
- `https://figma.com/design/:fileKey/branch/:branchKey/:fileName` → Use branchKey as fileKey

### By Exploring Structure
Start from root and navigate:
```typescript
// Get page structure
mcp0_get_metadata({ nodeId: "0:1" })

// Then get specific section
mcp0_get_metadata({ nodeId: "2255:2600" })
```

## Common Node IDs from Project

Based on the reusable-sections.md file:

| Section | Node ID | Description |
|---------|---------|-------------|
| Homepage Hero | 2473:15647 | Main hero with gradient |
| Journey Hero | 2473:15668 | Inner page hero |
| Stats Section | 2473:15690 | 3 stat cards |
| Perimeter Section | 2473:15712 | 4 feature cards |
| Enterprise Section | 2473:15759 | 4-column with intro |
| Newsletter Section | 2473:15781 | Email signup |

## Workflow Pattern

1. **Always call get_design_context first**
   ```typescript
   mcp0_get_design_context({ nodeId: "2473:15690", ... })
   ```

2. **Immediately follow with screenshot**
   ```typescript
   mcp0_get_screenshot({ nodeId: "2473:15690", ... })
   ```

3. **Extract key specifications from response:**
   - Background colors
   - Spacing (gap, padding)
   - Typography (font sizes, weights)
   - Layout (flex, grid)
   - Special effects (blur, gradients)

## Adapting Figma Code

The MCP returns Tailwind code that needs adaptation:

### Original from Figma:
```jsx
<div className="bg-[var(--white,white)] gap-[48px] px-[96px] py-[160px]">
```

### Adapted for Project:
```jsx
<section className="bg-white px-4 py-16 sm:px-6 lg:px-24 lg:py-40">
```

### Key Adaptations:
1. Replace hardcoded values with responsive classes
2. Use design tokens from `@/lib/design-tokens`
3. Add responsive breakpoints (sm:, lg:, etc.)
4. Convert inline styles to className or styled objects
5. Use proper semantic HTML elements

## Error Handling

### Node Not Found
```
Error: No node could be found for the provided nodeId
```
**Solution:** Ensure Figma desktop app is open with the correct file as active tab.

### Timeout Issues
```
Error: TimeoutError
```
**Solution:** The Figma file might be too large. Try a more specific node ID.

### Invalid Framework
```
Error: Invalid clientFrameworks
```
**Solution:** Use supported frameworks: react, nextjs, tailwindcss, vue, etc.

## Best Practices

1. **Always verify node exists** before calling get_design_context
2. **Capture both code and screenshot** for complete context
3. **Document extracted specifications** in comments
4. **Adapt to existing design system** rather than using raw Figma output
5. **Check responsive behavior** in Figma before implementing

## Example Full Workflow

```typescript
// 1. Get design specifications
const designContext = await mcp0_get_design_context({
  nodeId: "2473:15690",
  clientLanguages: "typescript,html,css",
  clientFrameworks: "react,nextjs,tailwindcss"
})

// 2. Get visual reference
const screenshot = await mcp0_get_screenshot({
  nodeId: "2473:15690",
  clientLanguages: "typescript,html,css",
  clientFrameworks: "react,nextjs,tailwindcss"
})

// 3. Analyze returned code for:
// - Layout structure (flex/grid)
// - Spacing values (gap, padding)
// - Color values
// - Typography styles
// - Component hierarchy

// 4. Create/update component matching design
// 5. Add to Storybook
// 6. Verify with Playwright
```
