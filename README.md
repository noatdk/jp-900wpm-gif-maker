# Japanese Anchor GIF Generator (`generator.py`)

A Python script to generate animated GIFs from Japanese text using an **Anchor-based RSVP (Rapid Serial Visual Presentation)** method. It centers the text based on the middle character (the "pivot") of each segment, keeping the reader's eye focused on a fixed point. This is a toy script which was inspired by this tweet https://x.com/UltraLinx/status/2011434505253650868

## Requirements

Install the required Python packages:

```bash
pip install -U spacy ginza ja_ginza Pillow
```

## Preview
![Output](output_anchor.gif)

> Note: The text in the preview is from the prologue of [魔女と傭兵](https://ncode.syosetu.com/n2819ha/).

## Basic Usage

```bash
python generator.py "日本語のテキストを入力してください"
```

This will generate `output_anchor.gif` in the current directory.

## Reading from File (PowerShell)

You can pass file content as an argument. Ensure correct encoding (UTF-8).

```powershell
python generator.py "$(Get-Content input.txt -Raw -Encoding utf8)" --interval 200
```

## Command Line Arguments

| Argument | Description | Default |
| :--- | :--- | :--- |
| `text` | The Japanese text to process (Required). | - |
| `--interval` | Duration of each frame in milliseconds. | `500` |
| `--start_delay` | Duration of the very first frame (ms). | `2000` |
| `--output` | Filename of the generated GIF. | `output_anchor.gif` |
| `--font_path` | Path to a custom TrueType/OpenType font file. Auto-detects system font if omitted. | Auto-detect |
| `--text_color` | Color of the text (name or hex). | `black` |
| `--bg_color` | Color of the background. | `white` |
| `--no_highlight` | Disable the red color highlight for the anchor character. | `False` |
| `--span_type` | Tokenization mode: `bunsetu` (phrases) or `token` (words). | `bunsetu` |
| `--pause_on_break` | Enable longer pause when a delimiter is found. | `False` |
| `--break_delay` | Duration of the frame containing the delimiter (ms). | `500` |
| `--delimiter` | The character that triggers the break pause. | `。` |

## Examples

### 1. Custom Colors and Speed
Green text on black background, faster speed (200ms):
```bash
python generator.py "マトリックスのような配色" --text_color "#00FF00" --bg_color "black" --interval 200
```

### 2. Disable Highlight and Use Custom Font
All black text, using a specific font file:
```bash
python generator.py "明朝体で表示" --no_highlight --font_path "C:/Windows/Fonts/msmincho.ttc"
```

### 3. Sentence Break Pause
Pause for 1.5 seconds (1500ms) at every period (`。`):
```bash
python generator.py "文の終わりで止まります。読みやすいですか？" --pause_on_break --break_delay 1500
```
