import sys
import argparse
import spacy
from PIL import Image, ImageDraw, ImageFont
import os
import ginza
import platform

def create_gif(text, interval, output_file, start_delay=2000, font_path=None, no_highlight=False, text_color='black', bg_color='white', span_type='bunsetu', pause_on_break=False, break_delay=500, delimiter='。'):
    # Initialize GiNZA
    try:
        nlp = spacy.load("ja_ginza")
    except Exception as e:
        print(f"Error initializing GiNZA: {e}")
        print("Ensure 'ginza' and 'ja_ginza' are installed: pip install -U ginza ja_ginza")
        sys.exit(1)

    # Tokenize the text
    doc = nlp(text)
    if span_type == 'token':
        words_raw = [token.text for token in doc]
    else:
        words_raw = [span.text for span in ginza.bunsetu_spans(doc)]
    
    # Clean words: remove newlines and return carriage chars
    words = []
    for w in words_raw:
        clean_w = w.replace('\n', '').replace('\r', '')
        if clean_w:
            words.append(clean_w)

    if not words:
        print("No words found in the input text.")
        return

    print(f"Tokenized components: {words}")

    # Settings for image
    width, height = 400, 400
    # Use provided colors (PIL handles color strings like 'white', 'black', 'red')
    
    # Dummy image for text measurement
    dummy_img = Image.new('RGB', (1, 1))
    draw_dummy = ImageDraw.Draw(dummy_img)
    
    frames = []

    try:
        # Determine font path if not provided
        if not font_path:
            system = platform.system()
            if system == "Windows":
                # Try common Japanese fonts on Windows
                candidates = ["C:/Windows/Fonts/msgothic.ttc", "C:/Windows/Fonts/msmincho.ttc", "C:/Windows/Fonts/meiryo.ttc"]
            elif system == "Darwin": # macOS
                candidates = ["/System/Library/Fonts/Hiragino Sans GB.ttc", "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc"]
            elif system == "Linux":
                candidates = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"]
            else:
                candidates = []
                
            for path in candidates:
                if os.path.exists(path):
                    font_path = path
                    break
        
        if font_path:
             print(f"Using font: {font_path}")
             font_size = 50
             font = ImageFont.truetype(font_path, font_size)
        else:
             print("Warning: No suitable Japanese font found. Using default font (Japanese characters may not render correctly).")
             font = ImageFont.load_default()

    except IOError:
        print(f"Warning: Could not load font at {font_path}. Using default font.")
        font = ImageFont.load_default()

    # Calculate required dimensions
    max_left_dist = 0
    max_right_dist = 0
    
    # Pre-calculate measurements to determine width
    for word in words:
        pivot_idx = len(word) // 2
        prefix = word[:pivot_idx]
        pivot_char = word[pivot_idx]
        suffix = word[pivot_idx+1:]
        
        try:
             # Get bounding box for the full text to get height (check just for font validity)
            _, top, _, bottom = draw_dummy.textbbox((0, 0), word, font=font)
            
            left_p, _, right_p, _ = draw_dummy.textbbox((0, 0), prefix, font=font)
            prefix_width = right_p - left_p
            
            left_c, _, right_c, _ = draw_dummy.textbbox((0, 0), pivot_char, font=font)
            pivot_width = right_c - left_c
            
            left_s, _, right_s, _ = draw_dummy.textbbox((0, 0), suffix, font=font)
            suffix_width = right_s - left_s

        except AttributeError:
             # Fallback for older Pillow versions
            prefix_width, _ = draw_dummy.textsize(prefix, font=font)
            pivot_width, _ = draw_dummy.textsize(pivot_char, font=font)
            suffix_width, _ = draw_dummy.textsize(suffix, font=font)

        left_dist = prefix_width + (pivot_width / 2)
        right_dist = suffix_width + (pivot_width / 2)
        
        max_left_dist = max(max_left_dist, left_dist)
        max_right_dist = max(max_right_dist, right_dist)

    # Calculate width with some padding
    required_width = int(2 * max(max_left_dist, max_right_dist) + 100) # 50px padding on each side
    width = max(width, required_width)
    
    # Calculate center of the image
    cx = width / 2
    cy = height / 2

    for word in words:
        # Create a new image for each frame
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # Identify the anchor character (middle of the string)
        pivot_idx = len(word) // 2
        
        # Split text into part before pivot, pivot itself, and suffix
        prefix = word[:pivot_idx]
        pivot_char = word[pivot_idx]
        suffix = word[pivot_idx+1:]
        
        if no_highlight:
            pivot_color = text_color
        else:
            pivot_color = (255, 0, 0)

        # Calculate dimensions
        try:
            # Get bounding box for the full text to get height
            _, top, _, bottom = draw.textbbox((0, 0), word, font=font)
            text_height = bottom - top
            
            # Get width of the prefix
            left_p, _, right_p, _ = draw.textbbox((0, 0), prefix, font=font)
            prefix_width = right_p - left_p
            
            # Get width of the pivot character
            left_c, _, right_c, _ = draw.textbbox((0, 0), pivot_char, font=font)
            pivot_width = right_c - left_c
            
        except AttributeError:
             # Fallback for older Pillow versions
            text_width, text_height = draw.textsize(word, font=font)
            prefix_width, _ = draw.textsize(prefix, font=font)
            pivot_width, _ = draw.textsize(pivot_char, font=font)

        # Calculate x position
        # The center of the pivot character should be at cx
        # x_start + prefix_width + pivot_width/2 = cx
        # x_start = cx - prefix_width - pivot_width/2
        
        x = cx - prefix_width - (pivot_width / 2)
        y = (height - text_height) / 2 # Vertically centered

        # Draw prefix
        if prefix:
            draw.text((x, y), prefix, font=font, fill=text_color)
        
        # Draw pivot
        # X position for pivot is x + prefix_width
        draw.text((x + prefix_width, y), pivot_char, font=font, fill=pivot_color)
        
        # Draw suffix
        if suffix:
            # X position for suffix is x + prefix_width + pivot_width
            draw.text((x + prefix_width + pivot_width, y), suffix, font=font, fill=text_color)
            
        frames.append(img)

    if frames:
        # Calculate durations: first frame gets start_delay, others get interval
        # Calculate durations: first frame gets start_delay, others get interval
        durations = []
        for i, word in enumerate(words):
            if pause_on_break and delimiter in word:
                durations.append(break_delay)
            else:
                durations.append(interval)
        
        if durations:
            durations[0] = start_delay
        if durations:
            durations[0] = start_delay

        # Save as GIF
        frames[0].save(
            output_file,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0
        )
        print(f"GIF saved to {output_file}")
    else:
        print("No frames generated.")

def main():
    parser = argparse.ArgumentParser(description='Generate a GIF from Japanese text tokens using GiNZA with anchor alignment.')
    parser.add_argument('text', type=str, help='The Japanese text to process')
    parser.add_argument('--interval', type=int, default=500, help='Interval between frames in milliseconds')
    parser.add_argument('--output', type=str, default='output_anchor.gif', help='Output GIF filename')
    parser.add_argument('--start_delay', type=int, default=2000, help='Delay for the first frame in milliseconds')
    parser.add_argument('--font_path', type=str, help='Path to a TrueType or OpenType font file')

    parser.add_argument('--no_highlight', action='store_true', help='Disable red highlight for anchor character')
    parser.add_argument('--text_color', type=str, default='black', help='Text color (e.g., "white", "#FFFFFF")')
    parser.add_argument('--bg_color', type=str, default='white', help='Background color (e.g., "black", "#000000")')
    parser.add_argument('--span_type', type=str, choices=['bunsetu', 'token'], default='bunsetu', help='Span type for tokenization (bunsetu or token)')
    parser.add_argument('--pause_on_break', action='store_true', help='Enable pause on sentence break')
    parser.add_argument('--break_delay', type=int, default=500, help='Delay for sentence break in milliseconds (default: 500)')
    parser.add_argument('--delimiter', type=str, default='。', help='Delimiter character for break (default: "。")')

    args = parser.parse_args()

    create_gif(args.text, args.interval, args.output, args.start_delay, font_path=args.font_path,
               no_highlight=args.no_highlight, text_color=args.text_color, bg_color=args.bg_color, span_type=args.span_type,
               pause_on_break=args.pause_on_break, break_delay=args.break_delay, delimiter=args.delimiter)

if __name__ == "__main__":
    main()
