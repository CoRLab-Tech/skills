#!/usr/bin/env python3
"""
Extract a specific component from Figma and generate React code.
Focused on individual component extraction.
"""

import argparse
import json
import re
from pathlib import Path

def parse_node_id(node_input):
    """Parse node ID from various input formats."""
    # Remove any colon or dash formatting
    return node_input.replace('-', ':')

def extract_component_properties(design_data):
    """Extract component-specific properties from design data."""
    props = {
        'dimensions': {},
        'typography': {},
        'colors': {},
        'spacing': {},
        'borders': {},
        'effects': []
    }
    
    # Parse dimensions
    if 'width' in design_data:
        props['dimensions']['width'] = design_data['width']
    if 'height' in design_data:
        props['dimensions']['height'] = design_data['height']
    
    # Parse typography
    if 'fontSize' in design_data:
        props['typography']['fontSize'] = design_data['fontSize']
    if 'fontFamily' in design_data:
        props['typography']['fontFamily'] = design_data['fontFamily']
    if 'fontWeight' in design_data:
        props['typography']['fontWeight'] = design_data['fontWeight']
    if 'lineHeight' in design_data:
        props['typography']['lineHeight'] = design_data['lineHeight']
    if 'letterSpacing' in design_data:
        props['typography']['letterSpacing'] = design_data['letterSpacing']
    
    # Parse colors
    if 'color' in design_data:
        props['colors']['text'] = design_data['color']
    if 'backgroundColor' in design_data:
        props['colors']['background'] = design_data['backgroundColor']
    
    # Parse spacing
    if 'padding' in design_data:
        props['spacing']['padding'] = design_data['padding']
    if 'margin' in design_data:
        props['spacing']['margin'] = design_data['margin']
    if 'gap' in design_data:
        props['spacing']['gap'] = design_data['gap']
    
    # Parse borders
    if 'borderRadius' in design_data:
        props['borders']['radius'] = design_data['borderRadius']
    if 'borderWidth' in design_data:
        props['borders']['width'] = design_data['borderWidth']
    if 'borderColor' in design_data:
        props['borders']['color'] = design_data['borderColor']
    
    # Parse effects (shadows, etc.)
    if 'boxShadow' in design_data:
        props['effects'].append({
            'type': 'shadow',
            'value': design_data['boxShadow']
        })
    
    return props

def generate_component_interface(name, props):
    """Generate TypeScript interface for component props."""
    interface_lines = [f"interface {name}Props {{"]
    
    # Add common props
    interface_lines.append("  className?: string;")
    interface_lines.append("  children?: React.ReactNode;")
    
    # Add component-specific props based on extracted data
    if props.get('dimensions'):
        if 'width' in props['dimensions']:
            interface_lines.append("  width?: string | number;")
        if 'height' in props['dimensions']:
            interface_lines.append("  height?: string | number;")
    
    interface_lines.append("}")
    
    return '\n'.join(interface_lines)

def generate_react_component(name, props, use_typescript=True):
    """Generate React component code."""
    
    # Convert name to PascalCase
    component_name = ''.join(word.capitalize() for word in name.split('-'))
    
    # Generate styles object
    styles = {}
    
    if props['dimensions']:
        if 'width' in props['dimensions']:
            styles['width'] = props['dimensions']['width']
        if 'height' in props['dimensions']:
            styles['height'] = props['dimensions']['height']
    
    if props['typography']:
        for key, value in props['typography'].items():
            styles[key] = value
    
    if props['colors']:
        if 'text' in props['colors']:
            styles['color'] = props['colors']['text']
        if 'background' in props['colors']:
            styles['backgroundColor'] = props['colors']['background']
    
    if props['spacing']:
        for key, value in props['spacing'].items():
            styles[key] = value
    
    if props['borders']:
        if 'radius' in props['borders']:
            styles['borderRadius'] = props['borders']['radius']
        if 'width' in props['borders']:
            styles['borderWidth'] = props['borders']['width']
        if 'color' in props['borders']:
            styles['borderColor'] = props['borders']['color']
    
    if props['effects']:
        for effect in props['effects']:
            if effect['type'] == 'shadow':
                styles['boxShadow'] = effect['value']
    
    # Format styles as JavaScript object
    style_lines = []
    for key, value in styles.items():
        if isinstance(value, str):
            style_lines.append(f"    {key}: '{value}',")
        else:
            style_lines.append(f"    {key}: {value},")
    
    style_string = '\n'.join(style_lines)
    
    # Generate component
    if use_typescript:
        interface = generate_component_interface(component_name, props)
        
        component = f'''import React from 'react';

{interface}

export const {component_name}: React.FC<{component_name}Props> = ({{
  className,
  children,
  ...props
}}) => {{
  const baseStyles = {{
{style_string}
  }};

  return (
    <div 
      className={{className}}
      style={{baseStyles}}
      {{...props}}
    >
      {{children}}
    </div>
  );
}};

export default {component_name};'''
    else:
        component = f'''import React from 'react';

export const {component_name} = ({{
  className,
  children,
  ...props
}}) => {{
  const baseStyles = {{
{style_string}
  }};

  return (
    <div 
      className={{className}}
      style={{baseStyles}}
      {{...props}}
    >
      {{children}}
    </div>
  );
}};

export default {component_name};'''
    
    return component

def main():
    parser = argparse.ArgumentParser(description='Extract component from Figma')
    parser.add_argument('--node-id', required=True, help='Figma node ID')
    parser.add_argument('--component-name', required=True, help='Component name')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--typescript', action='store_true', help='Generate TypeScript component')
    
    args = parser.parse_args()
    
    # Parse node ID
    node_id = parse_node_id(args.node_id)
    print(f"Extracting component from node: {node_id}")
    
    # Here you would call Figma MCP to get design data
    # For now, using placeholder data
    design_data = {
        'width': '320px',
        'height': 'auto',
        'padding': '16px',
        'backgroundColor': '#ffffff',
        'borderRadius': '8px',
        'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
        'fontSize': '14px',
        'fontFamily': 'Inter, sans-serif',
        'fontWeight': '500',
        'color': '#1a1a1a'
    }
    
    # Extract component properties
    props = extract_component_properties(design_data)
    
    # Generate component code
    component_code = generate_react_component(
        args.component_name,
        props,
        args.typescript
    )
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        extension = '.tsx' if args.typescript else '.jsx'
        output_path = Path(f"{args.component_name}{extension}")
    
    # Write component file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(component_code)
    
    print(f"✅ Component created: {output_path}")
    print("\nExtracted properties:")
    print(json.dumps(props, indent=2))
    
    print("\nNext steps:")
    print("1. Import and use the component in your application")
    print("2. Customize props and styling as needed")
    print("3. Add any additional functionality")

if __name__ == "__main__":
    main()
