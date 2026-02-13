#!/usr/bin/env python3
"""
Visual comparison tool for pixel-perfect UI validation.
Compares implementation screenshots with Figma designs.
"""

import argparse
import asyncio
import base64
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
import numpy as np
from io import BytesIO

def compare_images(img1_path, img2_path, output_path=None, viewport=None):
    """
    Compare two images and highlight differences.
    Returns similarity percentage and saves diff image if output_path provided.
    Validates responsive implementation if viewport specified.
    """
    # Open images
    img1 = Image.open(img1_path).convert('RGB')
    img2 = Image.open(img2_path).convert('RGB')
    
    # Check for viewport-specific issues
    if viewport:
        width, height = viewport
        if img1.width > width:
            raise ValueError(f"❌ CRITICAL: Horizontal overflow detected! Image width {img1.width}px exceeds viewport {width}px")
    
    # Resize if needed (to smaller dimensions)
    if img1.size != img2.size:
        min_width = min(img1.width, img2.width)
        min_height = min(img1.height, img2.height)
        img1 = img1.resize((min_width, min_height), Image.LANCZOS)
        img2 = img2.resize((min_width, min_height), Image.LANCZOS)
    
    # Calculate difference
    diff = ImageChops.difference(img1, img2)
    
    # Convert to numpy for analysis
    diff_array = np.array(diff)
    
    # Calculate similarity percentage
    max_diff = 255 * 3 * diff_array.shape[0] * diff_array.shape[1]
    actual_diff = np.sum(diff_array)
    similarity = (1 - actual_diff / max_diff) * 100
    
    # Create visualization if output path provided
    if output_path:
        # Create a red overlay for differences
        diff_mask = diff.convert('L')
        diff_mask = diff_mask.point(lambda p: 255 if p > 10 else 0)
        
        # Create output image with highlighted differences
        result = img1.copy()
        overlay = Image.new('RGB', img1.size, (255, 0, 0))
        result.paste(overlay, (0, 0), diff_mask)
        result.save(output_path)
    
    return similarity, diff

def analyze_differences(diff_image):
    """
    Analyze the difference image to categorize issues.
    """
    diff_array = np.array(diff_image)
    issues = {
        'color_differences': [],
        'spacing_issues': [],
        'typography_variations': [],
        'missing_elements': []
    }
    
    # Analyze color differences
    color_threshold = 10
    color_diffs = np.where(np.any(diff_array > color_threshold, axis=2))
    if len(color_diffs[0]) > 0:
        issues['color_differences'].append({
            'pixel_count': len(color_diffs[0]),
            'percentage': len(color_diffs[0]) / (diff_array.shape[0] * diff_array.shape[1]) * 100
        })
    
    # Edge detection for spacing/alignment issues
    gray_diff = diff_image.convert('L')
    edges = np.array(gray_diff)
    
    # Find horizontal and vertical lines (potential spacing issues)
    horizontal_lines = np.where(np.mean(edges, axis=1) > 5)[0]
    vertical_lines = np.where(np.mean(edges, axis=0) > 5)[0]
    
    if len(horizontal_lines) > 0:
        issues['spacing_issues'].append({
            'horizontal_positions': horizontal_lines.tolist()[:10]  # Limit to first 10
        })
    
    if len(vertical_lines) > 0:
        issues['spacing_issues'].append({
            'vertical_positions': vertical_lines.tolist()[:10]  # Limit to first 10
        })
    
    return issues

def generate_report(similarity, issues):
    """
    Generate a detailed comparison report.
    """
    report = []
    report.append(f"Visual Similarity: {similarity:.2f}%")
    report.append("-" * 50)
    
    if similarity >= 99:
        report.append("✅ Implementation is pixel-perfect!")
    elif similarity >= 95:
        report.append("⚠️ Minor differences detected - review required")
    else:
        report.append("❌ Significant differences - fixes needed")
    
    report.append("\nDetailed Analysis:")
    
    if issues['color_differences']:
        report.append(f"\nColor Differences:")
        for diff in issues['color_differences']:
            report.append(f"  - {diff['pixel_count']} pixels ({diff['percentage']:.2f}%) have color variations")
    
    if issues['spacing_issues']:
        report.append(f"\nSpacing/Alignment Issues:")
        for issue in issues['spacing_issues']:
            if 'horizontal_positions' in issue:
                report.append(f"  - Horizontal misalignments at Y positions: {issue['horizontal_positions'][:5]}")
            if 'vertical_positions' in issue:
                report.append(f"  - Vertical misalignments at X positions: {issue['vertical_positions'][:5]}")
    
    report.append("\nRecommendations:")
    if similarity < 99:
        if issues['color_differences']:
            report.append("  • Check color token mappings and opacity values")
        if issues['spacing_issues']:
            report.append("  • Verify padding, margin, and gap values")
        report.append("  • Ensure font loading and rendering matches design")
        report.append("  • Check border radius and shadow properties")
    
    return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description='Compare UI implementation with Figma design')
    parser.add_argument('--implementation', required=True, help='Path to implementation screenshot')
    parser.add_argument('--figma', required=True, help='Path to Figma screenshot')
    parser.add_argument('--output', help='Path to save difference visualization')
    parser.add_argument('--report', help='Path to save comparison report')
    parser.add_argument('--viewport', help='Viewport size (e.g., 375x667 for mobile)')
    parser.add_argument('--strict', action='store_true', help='Fail if not production-ready')
    
    args = parser.parse_args()
    
    # Parse viewport if provided
    viewport = None
    if args.viewport:
        w, h = args.viewport.split('x')
        viewport = (int(w), int(h))
    
    # Perform comparison
    try:
        similarity, diff = compare_images(args.implementation, args.figma, args.output, viewport)
    except ValueError as e:
        print(str(e))
        print("\n⚠️ Implementation is NOT production-ready!")
        print("Fix: Remove hardcoded widths and use responsive units")
        exit(1)
    
    # Analyze differences
    issues = analyze_differences(diff)
    
    # Generate report
    report = generate_report(similarity, issues)
    print(report)
    
    # Save report if requested
    if args.report:
        with open(args.report, 'w') as f:
            f.write(report)
    
    # Strict mode checks
    if args.strict:
        if similarity < 99:
            print("\n❌ Strict mode: Not pixel-perfect")
            exit(1)
        if viewport and viewport[0] <= 768:  # Mobile/tablet
            print("✅ Mobile viewport validated")
    
    # Exit with appropriate code
    exit(0 if similarity >= 99 else 1)

if __name__ == "__main__":
    main()
