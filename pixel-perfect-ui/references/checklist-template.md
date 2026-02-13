# Implementation Checklist Template

Use this template when implementing any Figma design (page, block, or component).

> ⚠️ **CRITICAL WORKFLOW**: For each section, ALWAYS extract fresh Figma data FIRST, then implement. Never rely on cached/old data!

---

# Implementation Checklist: [Component/Page Name]

**Created**: [Date]
**Figma Source**: [URL or Node ID]
**Target Path**: [e.g., src/app/page.tsx or src/components/MyComponent.tsx]
**Type**: [Page | Block/Section | Component]
**Status**: 🟡 Pending Approval

---

## 📋 Sections to Implement

[List each section identified from Figma with their node IDs]

1. **Section Name 1** (node-id: xxx)
2. **Section Name 2** (node-id: xxx)
3. **Section Name 3** (node-id: xxx)
...

---

## 🔄 SECTION-BY-SECTION IMPLEMENTATION

> ⚠️ **CRITICAL RULE**: For EACH section below:
> 1. First EXTRACT fresh Figma data for that specific section
> 2. Then IMPLEMENT based on that fresh extraction
> 3. Mark section complete
> 4. Move to next section
> 
> **NEVER rely on old/cached Figma data. Always re-extract before implementing!**

---

### Section 1: [Section Name]
**Node ID**: [figma-node-id]
**Status**: ⬜ Not Started

#### 1.1 Extract from Figma
- [ ] mcp0_get_design_context for this section
- [ ] mcp0_get_screenshot for visual reference
- [ ] Export any images/assets needed
- [ ] Note typography, colors, spacing

#### 1.2 Implement
- [ ] Create/update component structure
- [ ] Implement desktop layout (1440px)
- [ ] Implement tablet layout (768px)
- [ ] Implement mobile layout (375px)
- [ ] Add images with Next.js Image
- [ ] Apply styles (typography, colors, spacing)
- [ ] Add hover/focus states

#### 1.3 Validate
- [ ] Visual check matches Figma
- [ ] Responsive on all viewports
- [ ] No horizontal scroll

✅ **Section 1 Complete**: [ ]

---

### Section 2: [Section Name]
**Node ID**: [figma-node-id]
**Status**: ⬜ Not Started

#### 2.1 Extract from Figma
- [ ] mcp0_get_design_context for this section
- [ ] mcp0_get_screenshot for visual reference
- [ ] Export any images/assets needed
- [ ] Note typography, colors, spacing

#### 2.2 Implement
- [ ] Create/update component structure
- [ ] Implement desktop layout (1440px)
- [ ] Implement tablet layout (768px)
- [ ] Implement mobile layout (375px)
- [ ] Add images with Next.js Image
- [ ] Apply styles (typography, colors, spacing)
- [ ] Add hover/focus states

#### 2.3 Validate
- [ ] Visual check matches Figma
- [ ] Responsive on all viewports
- [ ] No horizontal scroll

✅ **Section 2 Complete**: [ ]

---

[Copy and repeat for each additional section...]

---

## 🏁 Final Validation

- [ ] All sections implemented
- [ ] Full page visual comparison with Figma
- [ ] No horizontal scroll on any viewport (375px, 768px, 1024px, 1440px)
- [ ] All images loading correctly
- [ ] Touch targets ≥ 44x44px on mobile
- [ ] Text readable without zooming (min 14px mobile)
- [ ] Resource validation passed (no broken links/images)
- [ ] No hardcoded pixel widths
- [ ] Production checklist complete

---

## 📝 Notes

### Design Specifications
- **Primary Colors**: 
- **Typography**: 
- **Key Spacing**: 

### Dependencies
- Components needed: 
- Images to export: 
- External resources: 

### Known Issues/Blockers
- 

---

## ✅ Completion Summary

**Completed**: [Date when finished]
**Final Status**: [Pending/Complete]
**Sections Completed**: X of Y

### What was implemented:
- 

### Deviations from design (if any):
- 

---

## Status Legend

- 🟡 **Pending Approval** - Plan created, waiting for user confirmation
- ⬜ **Not Started** - Section not yet begun
- 🔵 **In Progress** - Currently being implemented
- ✅ **Complete** - Section/task finished
- 🟢 **All Complete** - All sections finished and validated
- 🔴 **Blocked** - Cannot proceed (include reason)
- ⏸️ **Paused** - Temporarily stopped (include reason)
