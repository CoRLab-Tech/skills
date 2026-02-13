---
name: figma-illustration-import
description: Import vector illustrations from Figma as reusable React atom components. Use when a component or page needs a custom illustration (NOT a standard Carbon icon). Triggers on requests like 'implement this illustration from Figma', 'add this Figma illustration', 'create illustration component', or when a Figma node contains a multi-layer vector illustration (lock, envelope, microscope, etc.). BEFORE creating a new illustration, always check if it already exists in `apps/web-app/src/components/atoms/Illustration*.tsx` and `apps/web-app/public/assets/illustrations/`.
---

# Figma Illustration Import

Import multi-layer vector illustrations from Figma into reusable React atom components with local SVG/PNG assets, Storybook stories, and light/dark theme support.

## Pre-Flight: Check Existing Illustrations

Before creating any illustration, check if it already exists:

```bash
# List all existing illustration components
find apps/web-app/src/components/atoms -name "Illustration*" -type f | sort

# List all existing illustration asset folders
ls apps/web-app/public/assets/illustrations/
```

If the illustration already exists, import and use it directly:

```tsx
import { IllustrationPassword } from '../atoms/IllustrationPassword';
<IllustrationPassword size={160} />
```

If it does NOT exist, proceed with the workflow below.

## Workflow

### Step 1: Extract from Figma

Require a Figma node ID. Use the Figma MCP tools to extract the design:

```
mcp0_get_screenshot(nodeId: "<node-id>")
mcp0_get_design_context(nodeId: "<node-id>", artifactType: "REUSABLE_COMPONENT", forceCode: true)
```

The `get_design_context` response returns:
- **Asset URLs** — `http://localhost:3845/assets/<hash>.svg|png` constants
- **React+Tailwind code** — with `absolute` positioning using `inset-[top right bottom left]` percentages
- **Layer names** — via `data-name` attributes (use these for descriptive file names)

### Step 2: Download Assets

Create a folder and download all assets with descriptive names derived from layer names:

```bash
mkdir -p apps/web-app/public/assets/illustrations/<illustration-name>/

# Download each asset — name files descriptively based on layer purpose
curl -L -o <descriptive-name>.svg "http://localhost:3845/assets/<hash>.svg"
curl -L -o <descriptive-name>.png "http://localhost:3845/assets/<hash>.png"
```

Naming conventions:
- Use kebab-case: `shield-border.svg`, `check-circle.png`
- Name by visual purpose, not Figma layer ID: `envelope-front.svg` not `vector-3.svg`
- Keep `.svg` for vectors, `.png` for rasters/gradients

### Step 3: Create the Component

Create `apps/web-app/src/components/atoms/Illustration<Name>.tsx`:

```tsx
'use client';

import { forwardRef } from 'react';
import { cn } from '../../lib/utils';

export interface Illustration<Name>Props
  extends React.HTMLAttributes<HTMLDivElement> {
  size?: number;
}

const Illustration<Name> = forwardRef<HTMLDivElement, Illustration<Name>Props>(
  ({ className, size = 160, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('relative shrink-0', className)}
        style={{ width: size, height: size }}
        role="img"
        aria-label="<descriptive label>"
        {...props}
      >
        {/* Layer comment */}
        <div
          className="absolute"
          style={{
            top: '<top>%',
            right: '<right>%',
            bottom: '<bottom>%',
            left: '<left>%',
          }}
        >
          <img
            alt=""
            className="block size-full"
            src="/assets/illustrations/<name>/<asset>.svg"
            style={{ maxWidth: 'none' }}
          />
        </div>
        {/* ... repeat for each layer ... */}
      </div>
    );
  }
);

Illustration<Name>.displayName = 'Illustration<Name>';

export { Illustration<Name> };
```

Key patterns:
- **`'use client'`** directive — required (uses `forwardRef`)
- **`cn()` utility** — from `../../lib/utils` for className merging
- **`size` prop** — default 160, controls width and height
- **Percentage-based positioning** — from Figma's `inset-[top right bottom left]` values, split into individual `top/right/bottom/left` style properties
- **`role="img"` + `aria-label`** — accessibility
- **`mix-blend-multiply`** class — preserve from Figma when present on shadow layers
- **Rotated elements** — wrap in flex container with `items-center justify-center`, inner div with `flex-none` and explicit `width/height/transform`
- **`<img>` tags** — use `alt=""` (decorative), `className="block size-full"`, `style={{ maxWidth: 'none' }}`

### Step 4: Create Storybook Stories

Create `apps/web-app/src/components/atoms/Illustration<Name>.stories.tsx`:

```tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Illustration<Name> } from './Illustration<Name>';

const meta: Meta<typeof Illustration<Name>> = {
  title: 'Atoms/Illustration<Name>',
  component: Illustration<Name>,
  tags: ['autodocs'],
  argTypes: {
    size: {
      control: { type: 'range', min: 40, max: 320, step: 8 },
    },
  },
};

export default meta;
type Story = StoryObj<typeof Illustration<Name>>;

export const Default: Story = { args: { size: 160 } };
export const Small: Story = { args: { size: 80 } };
export const Large: Story = { args: { size: 240 } };

export const OnLightBackground: Story = {
  args: { size: 160 },
  decorators: [
    (Story) => (
      <div style={{ padding: '2rem', background: '#ffffff', borderRadius: '8px' }}>
        <Story />
      </div>
    ),
  ],
};

export const OnDarkBackground: Story = {
  args: { size: 160 },
  decorators: [
    (Story) => (
      <div style={{ padding: '2rem', background: '#020712', borderRadius: '8px' }}>
        <Story />
      </div>
    ),
  ],
};

export const LightAndDarkComparison: Story = {
  args: { size: 160 },
  render: (args) => (
    <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
      <div style={{ padding: '2rem', background: '#ffffff', borderRadius: '8px', border: '1px solid #d7dde9' }}>
        <p style={{ marginBottom: '1rem', fontSize: '12px', color: '#7184af', fontFamily: 'Titillium Web, sans-serif' }}>Light</p>
        <Illustration<Name> {...args} />
      </div>
      <div style={{ padding: '2rem', background: '#020712', borderRadius: '8px', border: '1px solid #2f3953' }}>
        <p style={{ marginBottom: '1rem', fontSize: '12px', color: '#99a8c6', fontFamily: 'Titillium Web, sans-serif' }}>Dark</p>
        <Illustration<Name> {...args} />
      </div>
    </div>
  ),
};
```

### Step 5: Verify

1. Run TypeScript check: `npx tsc --noEmit --project apps/web-app/tsconfig.json`
2. Open Storybook and navigate to the `LightAndDarkComparison` story
3. Take a screenshot and compare with the Figma original
4. Iterate if needed

## Storybook Config Prerequisite

Ensure `apps/web-app/.storybook/main.ts` includes `staticDirs`:

```typescript
const config: StorybookConfig = {
  stories: ['../**/*.@(mdx|stories.@(js|jsx|ts|tsx))'],
  addons: [],
  staticDirs: ['../public'],
  // ...
};
```

Without this, illustration assets will 404 in Storybook.

## Theme Handling

Illustrations use the **same assets** for both light and dark themes. The SVGs use `var(--fill-0, <fallback>)` where the fallback is the light-theme color. Theme differentiation comes from the **parent background color**, not from swapping assets. A single component works on both light and dark backgrounds.
