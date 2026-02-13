#!/usr/bin/env python3
"""
Resource validator to detect broken links, missing images, and invalid resources.
Ensures all assets are present and accessible before deployment.
"""

import argparse
import os
import re
import json
import requests
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image as PILImage

class ResourceValidator:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.public_dir = self.project_root / 'public'
        self.src_dir = self.project_root / 'src'
        
        self.issues = {
            'missing_images': [],
            'broken_links': [],
            'invalid_paths': [],
            'external_dependencies': [],
            'placeholder_content': []
        }
        
        self.checked_resources = set()
        self.valid_resources = set()
    
    def validate_file(self, file_path):
        """Validate all resources in a single file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            self.issues['invalid_paths'].append({
                'file': str(file_path),
                'error': 'File does not exist'
            })
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check different resource types
        self.check_images(content, file_path)
        self.check_links(content, file_path)
        self.check_fonts(content, file_path)
        self.check_icons(content, file_path)
        self.check_placeholders(content, file_path)
    
    def check_images(self, content, source_file):
        """Check all image references for existence and validity."""
        
        # Patterns for image references
        patterns = [
            # Next.js Image component
            (r'<Image[^>]*src=["\']([^"\']+)["\']', 'Next.js Image'),
            # HTML img tag
            (r'<img[^>]*src=["\']([^"\']+)["\']', 'HTML img'),
            # Background images in CSS/style
            (r'background(?:-image)?:\s*url\(["\']?([^"\')\s]+)["\']?\)', 'CSS background'),
            # Import statements
            (r'import\s+\w+\s+from\s+["\']([^"\']+\.(?:png|jpg|jpeg|gif|svg|webp))["\']', 'Import'),
            # Direct string references
            (r'["\']/(assets|images)/([^"\']+\.(?:png|jpg|jpeg|gif|svg|webp))["\']', 'Direct reference')
        ]
        
        for pattern, context in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                img_path = match.group(1) if len(match.groups()) == 1 else match.group(0)
                self.validate_image_resource(img_path, source_file, context)
    
    def validate_image_resource(self, img_path, source_file, context):
        """Validate a single image resource."""
        
        # Skip if already checked
        if img_path in self.checked_resources:
            return
        
        self.checked_resources.add(img_path)
        
        # Check for placeholder/dummy images
        if any(keyword in img_path.lower() for keyword in ['placeholder', 'dummy', 'temp', 'example', 'lorem']):
            self.issues['placeholder_content'].append({
                'file': str(source_file),
                'resource': img_path,
                'type': 'Placeholder image',
                'fix': 'Export actual image from Figma and replace placeholder'
            })
            return
        
        # Handle different path types
        if img_path.startswith('http'):
            # External URL
            self.validate_external_url(img_path, source_file, context)
        elif img_path.startswith('/'):
            # Absolute path from public directory
            self.validate_public_resource(img_path, source_file, context)
        else:
            # Relative import
            self.validate_relative_import(img_path, source_file, context)
    
    def validate_public_resource(self, resource_path, source_file, context):
        """Validate resource in public directory."""
        
        # Remove leading slash
        clean_path = resource_path.lstrip('/')
        full_path = self.public_dir / clean_path
        
        if not full_path.exists():
            self.issues['missing_images'].append({
                'file': str(source_file),
                'resource': resource_path,
                'expected_location': str(full_path),
                'context': context,
                'fix': f'Export from Figma and save to: {full_path}'
            })
        else:
            # Validate image file
            try:
                with PILImage.open(full_path) as img:
                    width, height = img.size
                    
                    # Check for suspicious dimensions
                    if width == 1 and height == 1:
                        self.issues['placeholder_content'].append({
                            'file': str(source_file),
                            'resource': resource_path,
                            'type': '1x1 placeholder image',
                            'fix': 'Replace with actual image from design'
                        })
                    
                    self.valid_resources.add(resource_path)
                    
            except Exception as e:
                self.issues['broken_links'].append({
                    'file': str(source_file),
                    'resource': resource_path,
                    'error': f'Invalid image file: {str(e)}',
                    'fix': 'Re-export image from Figma in correct format'
                })
    
    def validate_relative_import(self, import_path, source_file, context):
        """Validate relative import path."""
        
        source_dir = Path(source_file).parent
        resolved_path = (source_dir / import_path).resolve()
        
        if not resolved_path.exists():
            # Try common asset directories
            possible_locations = [
                self.src_dir / 'assets' / Path(import_path).name,
                self.public_dir / 'assets' / Path(import_path).name,
                self.src_dir / 'images' / Path(import_path).name,
                self.public_dir / 'images' / Path(import_path).name
            ]
            
            found = False
            for location in possible_locations:
                if location.exists():
                    self.valid_resources.add(str(location))
                    found = True
                    break
            
            if not found:
                self.issues['missing_images'].append({
                    'file': str(source_file),
                    'resource': import_path,
                    'context': context,
                    'tried_locations': [str(p) for p in possible_locations],
                    'fix': 'Export from Figma and save to project assets'
                })
    
    def validate_external_url(self, url, source_file, context):
        """Validate external URL resource."""
        
        # Check if URL is accessible
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code >= 400:
                self.issues['broken_links'].append({
                    'file': str(source_file),
                    'resource': url,
                    'status_code': response.status_code,
                    'context': context,
                    'fix': 'Download and serve locally or fix external URL'
                })
            else:
                # Warn about external dependencies
                self.issues['external_dependencies'].append({
                    'file': str(source_file),
                    'resource': url,
                    'context': context,
                    'warning': 'External dependency - consider serving locally',
                    'fix': 'Download and add to public/assets/ for better performance'
                })
        except Exception as e:
            self.issues['broken_links'].append({
                'file': str(source_file),
                'resource': url,
                'error': str(e),
                'context': context,
                'fix': 'Check URL or download resource locally'
            })
    
    def check_links(self, content, source_file):
        """Check all hyperlinks in the content."""
        
        # Find all href attributes
        href_pattern = r'href=["\']([^"\']+)["\']'
        matches = re.finditer(href_pattern, content)
        
        for match in matches:
            link = match.group(1)
            
            # Skip anchors and mailto
            if link.startswith('#') or link.startswith('mailto:'):
                continue
            
            # Check internal links
            if link.startswith('/'):
                # Check if route exists (for Next.js)
                route_path = self.src_dir / 'app' / link.lstrip('/') / 'page.tsx'
                route_path_jsx = self.src_dir / 'app' / link.lstrip('/') / 'page.jsx'
                pages_path = self.src_dir / 'pages' / f"{link.lstrip('/')}.tsx"
                
                if not any(p.exists() for p in [route_path, route_path_jsx, pages_path]):
                    self.issues['broken_links'].append({
                        'file': str(source_file),
                        'link': link,
                        'type': 'Internal route',
                        'fix': 'Create the missing page or fix the link'
                    })
    
    def check_fonts(self, content, source_file):
        """Check font file references."""
        
        font_pattern = r'@font-face[^}]*src:[^}]*url\(["\']?([^"\')\s]+)["\']?\)'
        matches = re.finditer(font_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            font_path = match.group(1)
            if font_path.startswith('/'):
                full_path = self.public_dir / font_path.lstrip('/')
                if not full_path.exists():
                    self.issues['missing_images'].append({
                        'file': str(source_file),
                        'resource': font_path,
                        'type': 'Font file',
                        'fix': 'Add font file to public directory'
                    })
    
    def check_icons(self, content, source_file):
        """Check icon references."""
        
        # Check for icon imports
        icon_patterns = [
            r'<Icon[^>]*name=["\']([^"\']+)["\']',
            r'icon:\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in icon_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                icon_name = match.group(1)
                
                # Check if icon file exists
                icon_locations = [
                    self.public_dir / 'assets' / f'{icon_name}.svg',
                    self.src_dir / 'assets' / 'icons' / f'{icon_name}.svg',
                    self.src_dir / 'components' / 'icons' / f'{icon_name}.tsx'
                ]
                
                if not any(p.exists() for p in icon_locations):
                    self.issues['missing_images'].append({
                        'file': str(source_file),
                        'resource': icon_name,
                        'type': 'Icon',
                        'fix': 'Export icon from Figma as SVG or add to icon library'
                    })
    
    def check_placeholders(self, content, source_file):
        """Check for placeholder content that shouldn't be in production."""
        
        placeholder_patterns = [
            (r'lorem\s+ipsum', 'Lorem ipsum text'),
            (r'https?://via\.placeholder\.com', 'Placeholder.com image'),
            (r'https?://placehold\.it', 'Placehold.it image'),
            (r'https?://lorempixel\.com', 'Lorem pixel image'),
            (r'https?://placekitten\.com', 'Placekitten image'),
            (r'TODO|FIXME|XXX|HACK', 'TODO comment'),
            (r'Coming\s+Soon', 'Coming Soon placeholder'),
        ]
        
        for pattern, description in placeholder_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.issues['placeholder_content'].append({
                    'file': str(source_file),
                    'type': description,
                    'fix': 'Replace with actual content from design/copy'
                })
    
    def validate_directory(self, directory):
        """Validate all files in a directory recursively."""
        
        directory = Path(directory)
        
        # File extensions to check
        extensions = ['.tsx', '.jsx', '.ts', '.js', '.css', '.scss']
        
        for ext in extensions:
            for file_path in directory.rglob(f'*{ext}'):
                # Skip node_modules and .next
                if 'node_modules' in str(file_path) or '.next' in str(file_path):
                    continue
                
                self.validate_file(file_path)
    
    def generate_report(self):
        """Generate comprehensive validation report."""
        
        report = []
        report.append("🔍 Resource Validation Report")
        report.append("=" * 60)
        
        total_issues = sum(len(v) for v in self.issues.values())
        
        if total_issues == 0:
            report.append("✅ All resources validated successfully!")
            report.append(f"   Checked {len(self.checked_resources)} resources")
            report.append(f"   Valid resources: {len(self.valid_resources)}")
        else:
            report.append(f"❌ Found {total_issues} resource issues\n")
            
            # Missing images (CRITICAL)
            if self.issues['missing_images']:
                report.append("🔴 CRITICAL: Missing Images/Resources")
                report.append(f"   Found {len(self.issues['missing_images'])} missing resources\n")
                
                for issue in self.issues['missing_images'][:10]:  # Show first 10
                    report.append(f"   File: {issue['file']}")
                    report.append(f"   Missing: {issue['resource']}")
                    report.append(f"   Type: {issue.get('type', 'Image')}")
                    report.append(f"   Fix: {issue['fix']}")
                    report.append("")
                
                if len(self.issues['missing_images']) > 10:
                    report.append(f"   ... and {len(self.issues['missing_images']) - 10} more\n")
            
            # Broken links (HIGH)
            if self.issues['broken_links']:
                report.append("🟡 HIGH: Broken Links")
                report.append(f"   Found {len(self.issues['broken_links'])} broken links\n")
                
                for issue in self.issues['broken_links'][:5]:
                    report.append(f"   File: {issue['file']}")
                    report.append(f"   Link: {issue.get('resource', issue.get('link'))}")
                    error_msg = issue.get('error', f"Status {issue.get('status_code')}")
                    report.append(f"   Error: {error_msg}")
                    report.append(f"   Fix: {issue['fix']}")
                    report.append("")
            
            # Placeholder content (MEDIUM)
            if self.issues['placeholder_content']:
                report.append("🟠 MEDIUM: Placeholder Content")
                report.append(f"   Found {len(self.issues['placeholder_content'])} placeholders\n")
                
                for issue in self.issues['placeholder_content'][:5]:
                    report.append(f"   File: {issue['file']}")
                    report.append(f"   Type: {issue['type']}")
                    report.append(f"   Fix: {issue['fix']}")
                    report.append("")
            
            # External dependencies (INFO)
            if self.issues['external_dependencies']:
                report.append("🔵 INFO: External Dependencies")
                report.append(f"   Found {len(self.issues['external_dependencies'])} external resources\n")
                
                for issue in self.issues['external_dependencies'][:3]:
                    report.append(f"   File: {issue['file']}")
                    report.append(f"   URL: {issue['resource']}")
                    report.append(f"   Recommendation: {issue['fix']}")
                    report.append("")
        
        report.append("\n📋 Resource Checklist:")
        report.append("  [ ] All images exported from Figma")
        report.append("  [ ] No placeholder content")
        report.append("  [ ] All links validated")
        report.append("  [ ] Icons and fonts present")
        report.append("  [ ] External resources minimized")
        
        return "\n".join(report)
    
    def export_json_report(self, output_path):
        """Export detailed JSON report."""
        
        report = {
            'summary': {
                'total_issues': sum(len(v) for v in self.issues.values()),
                'resources_checked': len(self.checked_resources),
                'valid_resources': len(self.valid_resources)
            },
            'issues': self.issues,
            'valid_resources': list(self.valid_resources)
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

def main():
    parser = argparse.ArgumentParser(description='Validate all resources and detect broken links')
    parser.add_argument('--file', help='Single file to validate')
    parser.add_argument('--directory', help='Directory to validate recursively')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    parser.add_argument('--report', help='Save report to file')
    parser.add_argument('--json', help='Export JSON report')
    parser.add_argument('--strict', action='store_true', help='Fail on any issues')
    
    args = parser.parse_args()
    
    validator = ResourceValidator(args.project_root)
    
    if args.file:
        validator.validate_file(args.file)
    elif args.directory:
        validator.validate_directory(args.directory)
    else:
        # Default: validate src directory
        validator.validate_directory(validator.src_dir)
    
    # Generate report
    report = validator.generate_report()
    print(report)
    
    # Save reports
    if args.report:
        with open(args.report, 'w') as f:
            f.write(report)
    
    if args.json:
        validator.export_json_report(args.json)
    
    # Exit code
    total_issues = sum(len(v) for v in validator.issues.values())
    if args.strict and total_issues > 0:
        exit(1)
    elif validator.issues['missing_images'] or validator.issues['broken_links']:
        exit(1)  # Critical issues
    else:
        exit(0)

if __name__ == "__main__":
    main()
