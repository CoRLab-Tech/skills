#!/usr/bin/env python3
"""
Extract design from Figma and implement as React/Next.js component.
Automates the full workflow from design to code.
"""

import argparse
import json
import re
import os
from pathlib import Path

def parse_figma_url(url):
    """Extract node ID from Figma URL."""
    # Pattern: https://figma.com/design/FILE_KEY/FILE_NAME?node-id=NODE_ID
    match = re.search(r'node-id=([0-9-:]+)', url)
    if match:
        return match.group(1).replace('-', ':')
    return None

def detect_project_type(project_root):
    """Detect if project uses Next.js App Router or Pages Router."""
    app_dir = Path(project_root) / 'app'
    pages_dir = Path(project_root) / 'pages'
    
    if app_dir.exists():
        return 'app-router'
    elif pages_dir.exists():
        return 'pages-router'
    else:
        return 'react'

def detect_styling_system(project_root):
    """Detect the styling system used in the project."""
    package_json_path = Path(project_root) / 'package.json'
    
    if not package_json_path.exists():
        return 'css'
    
    with open(package_json_path) as f:
        package_data = json.load(f)
        deps = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
    
    if 'tailwindcss' in deps:
        return 'tailwind'
    elif 'styled-components' in deps:
        return 'styled-components'
    elif '@emotion/react' in deps or '@emotion/styled' in deps:
        return 'emotion'
    else:
        return 'css-modules'

def generate_component_template(name, styles, layout, project_type='react', styling='tailwind'):
    """Generate component code based on extracted design data."""
    
    # Convert to PascalCase
    component_name = ''.join(word.capitalize() for word in name.split('-'))
    
    if styling == 'tailwind':
        return generate_tailwind_component(component_name, styles, layout, project_type)
    elif styling == 'styled-components':
        return generate_styled_component(component_name, styles, layout, project_type)
    else:
        return generate_css_module_component(component_name, styles, layout, project_type)

def generate_tailwind_component(name, styles, layout, project_type):
    """Generate RESPONSIVE Tailwind-based component."""
    
    # CRITICAL: Use responsive container pattern
    container_classes = 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'
    
    # Map design tokens to RESPONSIVE Tailwind classes
    classes = []
    
    # Layout classes with responsive modifiers
    if layout.get('display') == 'flex':
        classes.append('flex')
        if layout.get('flexDirection') == 'column':
            # Stack on mobile, row on desktop
            classes.append('flex-col lg:flex-row')
        if layout.get('alignItems'):
            align_map = {
                'center': 'items-center',
                'flex-start': 'items-start',
                'flex-end': 'items-end'
            }
            classes.append(align_map.get(layout['alignItems'], ''))
        if layout.get('justifyContent'):
            justify_map = {
                'center': 'justify-center',
                'space-between': 'justify-between',
                'flex-start': 'justify-start'
            }
            classes.append(justify_map.get(layout['justifyContent'], ''))
    
    # RESPONSIVE Spacing classes
    if styles.get('padding'):
        # Convert to responsive padding
        padding_value = styles['padding'].replace('px', '')
        if int(padding_value) > 20:
            classes.append('p-4 sm:p-6 lg:p-8')
        else:
            classes.append(f"p-{int(int(padding_value)/4)}")
    if styles.get('margin'):
        # Use auto margins for centering
        classes.append('mx-auto')
    if styles.get('gap'):
        # Responsive gap
        gap_value = styles['gap'].replace('px', '')
        classes.append(f"gap-{int(int(gap_value)/4)} lg:gap-{int(int(gap_value)/2)}")
    
    # RESPONSIVE Typography classes
    if styles.get('fontSize'):
        # Mobile-first font sizing
        font_size = styles['fontSize'].replace('px', '')
        if int(font_size) > 24:
            classes.append('text-2xl sm:text-3xl lg:text-4xl')
        elif int(font_size) > 18:
            classes.append('text-lg sm:text-xl lg:text-2xl')
        else:
            classes.append('text-base sm:text-lg')
    if styles.get('fontWeight'):
        weight_map = {
            '400': 'font-normal',
            '500': 'font-medium',
            '600': 'font-semibold',
            '700': 'font-bold'
        }
        classes.append(weight_map.get(styles['fontWeight'], ''))
    
    # Color classes
    if styles.get('color'):
        classes.append(f"text-[{styles['color']}]")
    if styles.get('backgroundColor'):
        classes.append(f"bg-[{styles['backgroundColor']}]")
    
    # Border and radius
    if styles.get('borderRadius'):
        classes.append(f"rounded-[{styles['borderRadius']}]")
    if styles.get('borderWidth'):
        classes.append(f"border-[{styles['borderWidth']}]")
    
    class_string = ' '.join(filter(None, classes))
    
    if project_type == 'app-router':
        return f'''
"use client";

import Image from 'next/image';

export default function {name}() {{
  return (
    <section className="min-h-screen bg-white">
      <div className="{container_classes}">
        <div className="{class_string}">
          {{/* CRITICAL: Export all images from Figma first! */}}
          {{/* Use: mcp0_get_screenshot --nodeId <id> --filename "image.png" */}}
          {{/* Then save to public/assets/ */}}
          
          {{/* Example responsive image: */}}
          {{/* <Image 
            src="/assets/exported-image.png" 
            alt="Description"
            width={{800}}
            height={{600}}
            className="w-full h-auto"
            priority
          /> */}}
          
          {{/* Content from Figma - ensure mobile-first */}}
        </div>
      </div>
    </section>
  )
}}
'''
    else:
        return f'''
import React from 'react';
import Image from 'next/image';

export function {name}() {{
  return (
    <section className="min-h-screen bg-white">
      <div className="{container_classes}">
        <div className="{class_string}">
          {{/* CRITICAL: Export all images from Figma first! */}}
          {{/* Mobile-first responsive implementation required */}}
        </div>
      </div>
    </section>
  )
}}
'''

def generate_styled_component(name, styles, layout, project_type):
    """Generate styled-components based component."""
    
    css_props = []
    
    # Layout
    if layout.get('display'):
        css_props.append(f"display: {layout['display']};")
    if layout.get('flexDirection'):
        css_props.append(f"flex-direction: {layout['flexDirection']};")
    if layout.get('alignItems'):
        css_props.append(f"align-items: {layout['alignItems']};")
    if layout.get('justifyContent'):
        css_props.append(f"justify-content: {layout['justifyContent']};")
    
    # Spacing
    if styles.get('padding'):
        css_props.append(f"padding: {styles['padding']};")
    if styles.get('margin'):
        css_props.append(f"margin: {styles['margin']};")
    if styles.get('gap'):
        css_props.append(f"gap: {styles['gap']};")
    
    # Typography
    if styles.get('fontSize'):
        css_props.append(f"font-size: {styles['fontSize']};")
    if styles.get('fontWeight'):
        css_props.append(f"font-weight: {styles['fontWeight']};")
    if styles.get('lineHeight'):
        css_props.append(f"line-height: {styles['lineHeight']};")
    
    # Colors
    if styles.get('color'):
        css_props.append(f"color: {styles['color']};")
    if styles.get('backgroundColor'):
        css_props.append(f"background-color: {styles['backgroundColor']};")
    
    css_string = '\n  '.join(css_props)
    
    return f'''
import styled from 'styled-components'

const Container = styled.div\`
  {css_string}
\`

export {'default ' if project_type == 'app-router' else ''}function {name}() {{
  return (
    <Container>
      {{/* TODO: Add content based on Figma design */}}
    </Container>
  )
}}
'''

def generate_css_module_component(name, styles, layout, project_type):
    """Generate CSS Modules based component."""
    
    css_content = f'''.container {{
  {generate_css_properties(styles, layout)}
}}'''
    
    component_content = f'''
import styles from './{name}.module.css'

export {'default ' if project_type == 'app-router' else ''}function {name}() {{
  return (
    <div className={{styles.container}}>
      {{/* TODO: Add content based on Figma design */}}
    </div>
  )
}}
'''
    
    return {
        'component': component_content,
        'css': css_content
    }

def generate_css_properties(styles, layout):
    """Generate CSS properties from design data."""
    props = []
    
    # Layout
    if layout.get('display'):
        props.append(f"display: {layout['display']};")
    if layout.get('flexDirection'):
        props.append(f"flex-direction: {layout['flexDirection']};")
    if layout.get('alignItems'):
        props.append(f"align-items: {layout['alignItems']};")
    if layout.get('justifyContent'):
        props.append(f"justify-content: {layout['justifyContent']};")
    
    # Spacing
    if styles.get('padding'):
        props.append(f"padding: {styles['padding']};")
    if styles.get('margin'):
        props.append(f"margin: {styles['margin']};")
    if styles.get('gap'):
        props.append(f"gap: {styles['gap']};")
    
    # Typography
    if styles.get('fontSize'):
        props.append(f"font-size: {styles['fontSize']};")
    if styles.get('fontWeight'):
        props.append(f"font-weight: {styles['fontWeight']};")
    if styles.get('lineHeight'):
        props.append(f"line-height: {styles['lineHeight']};")
    
    # Colors
    if styles.get('color'):
        props.append(f"color: {styles['color']};")
    if styles.get('backgroundColor'):
        props.append(f"background-color: {styles['backgroundColor']};")
    
    # Borders
    if styles.get('borderRadius'):
        props.append(f"border-radius: {styles['borderRadius']};")
    if styles.get('borderWidth'):
        props.append(f"border-width: {styles['borderWidth']};")
    
    return '\n  '.join(props)

def main():
    parser = argparse.ArgumentParser(description='Extract Figma design and implement as component')
    parser.add_argument('--figma-url', required=True, help='Figma URL with node selection')
    parser.add_argument('--output-path', required=True, help='Output path for component')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    parser.add_argument('--component-name', help='Component name (auto-detected from path if not provided)')
    
    args = parser.parse_args()
    
    # Extract node ID from URL
    node_id = parse_figma_url(args.figma_url)
    if not node_id:
        print("Error: Could not extract node ID from Figma URL")
        print("Make sure to use 'Copy link to selection' in Figma")
        exit(1)
    
    print(f"Extracting design from node: {node_id}")
    
    # Detect project configuration
    project_type = detect_project_type(args.project_root)
    styling_system = detect_styling_system(args.project_root)
    
    print(f"Project type: {project_type}")
    print(f"Styling system: {styling_system}")
    
    # Here you would call Figma MCP tools to extract design data
    # For now, using placeholder data
    design_data = {
        'styles': {
            'padding': '16px',
            'fontSize': '14px',
            'fontWeight': '500',
            'color': '#1a1a1a',
            'backgroundColor': '#ffffff',
            'borderRadius': '8px'
        },
        'layout': {
            'display': 'flex',
            'flexDirection': 'column',
            'alignItems': 'center',
            'gap': '12px'
        }
    }
    
    # Generate component name
    component_name = args.component_name or Path(args.output_path).stem
    
    # Generate component code
    component_code = generate_component_template(
        component_name,
        design_data['styles'],
        design_data['layout'],
        project_type,
        styling_system
    )
    
    # Write component file(s)
    output_path = Path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if isinstance(component_code, dict):
        # CSS Modules - write both files
        with open(output_path, 'w') as f:
            f.write(component_code['component'])
        
        css_path = output_path.with_suffix('.module.css')
        with open(css_path, 'w') as f:
            f.write(component_code['css'])
        
        print(f"✅ Created component: {output_path}")
        print(f"✅ Created styles: {css_path}")
    else:
        # Single file component
        with open(output_path, 'w') as f:
            f.write(component_code)
        
        print(f"✅ Created component: {output_path}")
    
    print("\nNext steps:")
    print("1. Review and customize the generated component")
    print("2. Add content based on Figma design")
    print("3. Run visual-compare.py to validate pixel-perfect accuracy")

if __name__ == "__main__":
    main()
