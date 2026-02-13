# Figma to Storybook Implementation Checklist

## Pre-Implementation
- [ ] Storybook running on correct port (check with `npm run storybook`)
- [ ] Figma desktop app open with correct file
- [ ] Playwright MCP available
- [ ] Existing components identified in codebase

## For Each Component

### 1. Analysis Phase
- [ ] Component exists in `src/components/organisms/` or `molecules/`
- [ ] Component imported in main page file
- [ ] Dependencies (atoms/molecules) identified
- [ ] Figma node ID obtained (if needed)

### 2. Figma Design Extraction
- [ ] Used `mcp0_get_design_context()` with node ID
- [ ] Captured screenshot with `mcp0_get_screenshot()`
- [ ] Noted design specifications:
  - [ ] Colors and backgrounds
  - [ ] Spacing and gaps
  - [ ] Typography variants
  - [ ] Responsive behavior
  - [ ] Special effects (blur, gradients)

### 3. Storybook Story Creation
- [ ] Delegated to `skill("storybook")` for story creation
- [ ] Verified story appears in Storybook UI
- [ ] All required viewport variants created (Mobile, Tablet, Desktop)

### 4. Playwright Verification
- [ ] Navigated to story URL
- [ ] Captured desktop screenshot
- [ ] Resized to mobile (375px) and captured
- [ ] Resized to tablet (768px) and captured
- [ ] Compared with Figma design

### 5. Responsive Design Check
- [ ] Delegated to `skill("next-best-practices")` for responsive implementation
- [ ] No horizontal scroll at any viewport
- [ ] All viewports tested (375px, 768px, 1024px, 1440px)

### 6. Image Verification
- [ ] All images exist in `public/assets/` (checked with `list_dir`)
- [ ] Missing images downloaded from Figma localhost
- [ ] No console errors about missing images

### 7. Final Quality Check
- [ ] Component matches Figma design
- [ ] Responsive breakpoints work correctly
- [ ] Typography follows design system
- [ ] Colors match design tokens
- [ ] Spacing is consistent
- [ ] Interactive elements work

## Common Issues to Check

### Design Matching
- [ ] Spacing matches Figma design
- [ ] Colors match design tokens
- [ ] Typography matches design system
- [ ] Layout matches Figma structure

**Note:** For code-level fixes, delegate to:
- `skill("next-best-practices")` for component issues
- `skill("storybook")` for story issues

## Completion
- [ ] All viewport screenshots captured
- [ ] No console errors
- [ ] Component documented in Storybook
- [ ] TODO list updated
- [ ] Summary provided to user
