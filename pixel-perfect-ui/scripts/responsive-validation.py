#!/usr/bin/env python3
"""
Responsive validation tool to ensure production-ready mobile-first implementations.
Detects common responsive issues like hardcoded widths, horizontal scroll, and missing images.
"""

import argparse
import asyncio
import re
import json
from pathlib import Path

class ResponsiveValidator:
    def __init__(self):
        self.issues = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        # Viewport configurations
        self.viewports = [
            {'name': 'Mobile', 'width': 375, 'height': 667},
            {'name': 'Tablet', 'width': 768, 'height': 1024},
            {'name': 'Desktop', 'width': 1440, 'height': 900}
        ]
    
    def check_hardcoded_widths(self, code_content):
        """Check for hardcoded pixel widths that break responsiveness."""
        issues = []
        
        # Patterns to detect hardcoded widths
        patterns = [
            (r'w-\[\d+px\]', 'Tailwind hardcoded width'),
            (r'width:\s*\d+px', 'CSS hardcoded width'),
            (r'maxWidth:\s*\d+px', 'Inline style hardcoded max-width'),
            (r'minWidth:\s*\d+px', 'Inline style hardcoded min-width'),
            (r'style={{.*width:\s*\d+.*}}', 'Inline style object hardcoded width')
        ]
        
        lines = code_content.split('\n')
        for i, line in enumerate(lines, 1):
            for pattern, description in patterns:
                if re.search(pattern, line):
                    # Exception for small values (icons, buttons)
                    match = re.search(r'\d+', line)
                    if match and int(match.group()) > 100:
                        issues.append({
                            'line': i,
                            'type': description,
                            'content': line.strip(),
                            'fix': 'Use responsive units like max-w-7xl, percentages, or breakpoints'
                        })
        
        return issues
    
    def check_responsive_containers(self, code_content):
        """Check if containers use proper responsive patterns."""
        has_responsive_container = False
        recommended_patterns = [
            'max-w-7xl mx-auto',
            'max-w-6xl mx-auto',
            'max-w-5xl mx-auto',
            'container mx-auto',
            'max-w-screen-xl',
            'max-w-screen-lg'
        ]
        
        for pattern in recommended_patterns:
            if pattern in code_content:
                has_responsive_container = True
                break
        
        if not has_responsive_container and 'className=' in code_content:
            return [{
                'type': 'Missing responsive container',
                'fix': 'Add responsive container classes like "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"'
            }]
        
        return []
    
    def check_image_handling(self, code_content):
        """Check for proper image handling and missing images."""
        issues = []
        
        # Find all image references
        img_patterns = [
            (r'<img\s+src="([^"]+)"', 'HTML img tag'),
            (r'<Image\s+src="([^"]+)"', 'Next.js Image component'),
            (r"src='([^']+)'", 'Single quote src'),
            (r'backgroundImage:\s*[\'"]url\(([^)]+)\)', 'Background image')
        ]
        
        for pattern, description in img_patterns:
            matches = re.findall(pattern, code_content)
            for match in matches:
                # Check for placeholder images
                if any(placeholder in match.lower() for placeholder in ['placeholder', 'temp', 'dummy', 'example']):
                    issues.append({
                        'type': 'Placeholder image',
                        'path': match,
                        'fix': 'Export actual image from Figma and save to public/assets/'
                    })
                
                # Check for external URLs (should be local for production)
                if match.startswith('http') and 'localhost' not in match:
                    issues.append({
                        'type': 'External image URL',
                        'path': match,
                        'fix': 'Download and serve locally or configure Next.js for remote images'
                    })
        
        # Check for missing Next.js Image imports
        if '<img ' in code_content and 'next/image' not in code_content:
            issues.append({
                'type': 'Using HTML img instead of Next.js Image',
                'fix': 'Import and use Next.js Image component for optimization'
            })
        
        return issues
    
    def check_mobile_breakpoints(self, code_content):
        """Check if mobile breakpoints are properly implemented."""
        has_mobile_breakpoints = any(bp in code_content for bp in ['sm:', 'md:', 'lg:', 'xl:', '@media'])
        
        if not has_mobile_breakpoints and 'className=' in code_content:
            return [{
                'type': 'Missing responsive breakpoints',
                'fix': 'Add mobile-first breakpoints using sm:, md:, lg:, xl: prefixes'
            }]
        
        return []
    
    def check_overflow_issues(self, code_content):
        """Check for potential horizontal overflow issues."""
        issues = []
        
        # Check for fixed positioning that might break mobile
        if 'fixed' in code_content and 'inset-0' not in code_content:
            lines = code_content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'fixed' in line and not any(safe in line for safe in ['top-0', 'bottom-0', 'inset-']):
                    issues.append({
                        'line': i,
                        'type': 'Potentially problematic fixed positioning',
                        'content': line.strip(),
                        'fix': 'Ensure fixed elements work on all viewports'
                    })
        
        # Check for missing overflow handling
        if not any(overflow in code_content for overflow in ['overflow-x-hidden', 'overflow-x-auto', 'overflow-hidden']):
            if any(risk in code_content for risk in ['w-full', 'width: 100%', 'min-w-']):
                issues.append({
                    'type': 'Missing overflow handling',
                    'fix': 'Consider adding overflow-x-hidden to prevent horizontal scroll'
                })
        
        return issues
    
    def check_touch_targets(self, code_content):
        """Check if touch targets are appropriate for mobile."""
        issues = []
        
        # Find all interactive elements
        button_patterns = [
            r'<button[^>]*>(.*?)</button>',
            r'<a[^>]*>(.*?)</a>',
            r'<Button[^>]*/>',
            r'onClick=\{[^}]+\}'
        ]
        
        # Check for small touch targets
        small_size_patterns = ['p-1', 'py-1', 'px-1', 'p-2', 'h-6', 'h-8']
        
        for pattern in button_patterns:
            matches = re.findall(pattern, code_content, re.IGNORECASE)
            if matches:
                for size_pattern in small_size_patterns:
                    if size_pattern in code_content:
                        issues.append({
                            'type': 'Small touch target',
                            'pattern': size_pattern,
                            'fix': 'Ensure touch targets are at least 44x44px (use min-h-[44px] min-w-[44px])'
                        })
                        break
        
        return issues
    
    def generate_report(self, file_path, issues_found):
        """Generate a comprehensive validation report."""
        report = []
        report.append(f"📱 Responsive Validation Report")
        report.append("=" * 60)
        report.append(f"File: {file_path}")
        report.append("")
        
        total_issues = sum(len(v) for v in issues_found.values())
        
        if total_issues == 0:
            report.append("✅ No responsive issues found!")
        else:
            report.append(f"⚠️ Found {total_issues} responsive issues:")
            report.append("")
            
            # Report by severity
            if issues_found['hardcoded_widths']:
                report.append("🔴 CRITICAL: Hardcoded Widths")
                for issue in issues_found['hardcoded_widths']:
                    report.append(f"  Line {issue['line']}: {issue['type']}")
                    report.append(f"    Code: {issue['content'][:80]}...")
                    report.append(f"    Fix: {issue['fix']}")
                report.append("")
            
            if issues_found['missing_responsive']:
                report.append("🟡 HIGH: Missing Responsive Patterns")
                for issue in issues_found['missing_responsive']:
                    report.append(f"  - {issue['type']}")
                    report.append(f"    Fix: {issue['fix']}")
                report.append("")
            
            if issues_found['image_issues']:
                report.append("🟠 MEDIUM: Image Issues")
                for issue in issues_found['image_issues']:
                    report.append(f"  - {issue['type']}: {issue.get('path', '')}")
                    report.append(f"    Fix: {issue['fix']}")
                report.append("")
            
            if issues_found['overflow_risks']:
                report.append("🟡 MEDIUM: Overflow Risks")
                for issue in issues_found['overflow_risks']:
                    report.append(f"  - {issue['type']}")
                    if 'content' in issue:
                        report.append(f"    Code: {issue['content'][:80]}...")
                    report.append(f"    Fix: {issue['fix']}")
                report.append("")
            
            if issues_found['touch_targets']:
                report.append("🔵 LOW: Touch Target Issues")
                for issue in issues_found['touch_targets']:
                    report.append(f"  - {issue['type']}: {issue.get('pattern', '')}")
                    report.append(f"    Fix: {issue['fix']}")
        
        report.append("")
        report.append("📋 Production Checklist:")
        report.append("  [ ] Test on 375px viewport (Mobile)")
        report.append("  [ ] Test on 768px viewport (Tablet)")
        report.append("  [ ] Test on 1440px viewport (Desktop)")
        report.append("  [ ] No horizontal scroll on any device")
        report.append("  [ ] All images exported from Figma")
        report.append("  [ ] Touch targets ≥ 44x44px")
        report.append("  [ ] Text readable without zooming")
        
        return "\n".join(report)
    
    def validate_file(self, file_path):
        """Validate a single file for responsive issues."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        issues = {
            'hardcoded_widths': self.check_hardcoded_widths(content),
            'missing_responsive': self.check_responsive_containers(content) + self.check_mobile_breakpoints(content),
            'image_issues': self.check_image_handling(content),
            'overflow_risks': self.check_overflow_issues(content),
            'touch_targets': self.check_touch_targets(content)
        }
        
        return issues

def main():
    parser = argparse.ArgumentParser(description='Validate responsive implementation')
    parser.add_argument('--file', help='File path to validate')
    parser.add_argument('--url', help='URL to validate (requires Playwright)')
    parser.add_argument('--report', help='Output report file path')
    parser.add_argument('--strict', action='store_true', help='Fail on any issue')
    
    args = parser.parse_args()
    
    validator = ResponsiveValidator()
    
    if args.file:
        # Validate file
        issues = validator.validate_file(args.file)
        report = validator.generate_report(args.file, issues)
        print(report)
        
        if args.report:
            with open(args.report, 'w') as f:
                f.write(report)
        
        # Exit code based on issues
        total_issues = sum(len(v) for v in issues.values())
        if args.strict and total_issues > 0:
            exit(1)
        elif issues['hardcoded_widths']:
            exit(1)  # Critical issues always fail
    
    elif args.url:
        print("URL validation requires Playwright MCP integration")
        print("Use: mcp1_browser_navigate --url <url>")
        print("Then: mcp1_browser_resize --width 375 --height 667")
        print("Check for horizontal scroll and layout issues")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
