#!/usr/bin/env python3
"""
Generate PWA icons for Lead Intelligence Platform with glassmorphism theme.
Creates maskable icons (192x192 and 512x512) with gradient background and glass effect.
"""

import os
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL/Pillow not available. Install with: pip install Pillow")

# Theme colors from theme.css
PRIMARY_GRADIENT_START = (102, 126, 234)  # #667eea
PRIMARY_GRADIENT_END = (118, 75, 162)     # #764ba2
GLASS_WHITE = (255, 255, 255, 100)        # Semi-transparent white for glass effect
ICON_TEXT = "LI"  # Lead Intelligence

def create_gradient_background(width, height, start_color, end_color):
    """Create a gradient background image."""
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # Draw gradient
    for y in range(height):
        # Calculate color interpolation
        ratio = y / height
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return image

def add_glass_effect(image, opacity=100):
    """Add glass effect overlay to image."""
    # Create a white overlay with transparency
    overlay = Image.new('RGBA', image.size, (255, 255, 255, opacity))
    
    # Apply blur filter for glass effect
    blurred = overlay.filter(ImageFilter.GaussianBlur(radius=10))
    
    # Composite overlay on image
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    result = Image.alpha_composite(image, blurred)
    
    return result

def create_icon(size, output_path):
    """Create a PWA icon with glassmorphism theme."""
    # Create gradient background
    bg = create_gradient_background(size, size, PRIMARY_GRADIENT_START, PRIMARY_GRADIENT_END)
    
    # Convert to RGBA for transparency effects
    icon = bg.convert('RGBA')
    
    # Create overlay for glass effect
    overlay = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Draw circular glass effect in center
    center = size // 2
    radius = int(size * 0.35)  # 35% of size
    
    # Outer circle with glass effect (semi-transparent white)
    draw.ellipse(
        [center - radius, center - radius, center + radius, center + radius],
        fill=(255, 255, 255, 60),  # Semi-transparent white
        outline=(255, 255, 255, 120)
    )
    
    # Inner circle for depth
    inner_radius = int(radius * 0.7)
    draw.ellipse(
        [center - inner_radius, center - inner_radius, center + inner_radius, center + inner_radius],
        fill=(255, 255, 255, 30)
    )
    
    # Apply blur to overlay for glass effect
    blurred_overlay = overlay.filter(ImageFilter.GaussianBlur(radius=max(2, size // 50)))
    
    # Composite overlay on icon
    icon = Image.alpha_composite(icon, blurred_overlay)
    
    # Add text/logo
    draw = ImageDraw.Draw(icon)
    
    # Try to load a font, fallback to default if not available
    font_size = int(size * 0.35)
    font = None
    
    # Try different fonts
    font_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "arial.ttf",
    ]
    
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except:
            continue
    
    if font is None:
        # Use default font
        font = ImageFont.load_default()
        font_size = int(size * 0.25)
    
    # Calculate text position (centered)
    try:
        bbox = draw.textbbox((0, 0), ICON_TEXT, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        # Fallback for older PIL versions
        text_width, text_height = draw.textsize(ICON_TEXT, font=font)
        bbox = (0, 0, text_width, text_height)
    
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 - bbox[1]
    
    # Draw text with white color and subtle shadow
    # Shadow
    draw.text((text_x + 2, text_y + 2), ICON_TEXT, font=font, fill=(0, 0, 0, 80))
    # Main text
    draw.text((text_x, text_y), ICON_TEXT, font=font, fill=(255, 255, 255, 255))
    
    # Convert to RGB for PNG save (no transparency needed for maskable icons)
    final_icon = Image.new('RGB', (size, size), (102, 126, 234))
    if icon.mode == 'RGBA':
        final_icon.paste(icon, mask=icon.split()[3])
    else:
        final_icon.paste(icon)
    
    # Save icon
    final_icon.save(output_path, 'PNG', optimize=True)
    print(f"Created icon: {output_path} ({size}x{size})")

def main():
    """Generate PWA icons."""
    if not PIL_AVAILABLE:
        print("Error: PIL/Pillow is required to generate icons.")
        print("Install with: pip install Pillow")
        return
    
    # Get script directory
    script_dir = Path(__file__).parent.parent
    public_dir = script_dir / "frontend" / "public"
    
    # Create public directory if it doesn't exist
    public_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate 192x192 icon
    icon_192_path = public_dir / "icon-192.png"
    create_icon(192, icon_192_path)
    
    # Generate 512x512 icon
    icon_512_path = public_dir / "icon-512.png"
    create_icon(512, icon_512_path)
    
    print("\nPWA icons generated successfully!")
    print(f"Icons saved to: {public_dir}")
    print("\nNext steps:")
    print("1. Verify icons are displayed correctly in the browser")
    print("2. Test PWA install prompt")
    print("3. Verify manifest.json references are correct")

if __name__ == "__main__":
    main()

