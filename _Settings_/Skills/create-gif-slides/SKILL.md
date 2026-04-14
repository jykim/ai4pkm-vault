---
name: create-gif-slides
description: Create animated GIF slideshows from structured content. Use when the user asks to create a GIF summary, animated slide recap, GIF presentation, or visual summary GIF for events, meetups, presentations, or any multi-point content. Supports Korean text, dark/light themes, custom colors, progress indicators, and quote boxes. Ideal for social media sharing (Gobi Brain Updates, Slack, etc).
---

# Create GIF Slides

Generate looping animated GIF presentations from structured slide data. Each GIF contains a title frame, content slides with badges/points/quotes, and an optional closing CTA frame.

## Workflow

### Step 1: Prepare JSON Input

Create a temporary JSON file with this structure:

```json
{
  "title": "Main Title",
  "subtitle": "Optional subtitle (e.g. year)",
  "date": "2026-04-11",
  "meta": "5 Sessions / 80+ Attendees",
  "slides": [
    {
      "num": "01",
      "badge": "TOPIC",
      "badge_color": "#00C8DC",
      "title": "Slide Title Here",
      "speaker": "Speaker Name",
      "points": [
        "Key point one",
        "Key point two",
        "Key point three (max 4 recommended)"
      ],
      "quote": "A notable quote\\nSecond line optional"
    }
  ],
  "closing": {
    "headline": "Subtitle text",
    "title": "Big CTA Title",
    "features": [
      {"label": "Feature", "desc": "Description"}
    ],
    "cta_text": "example.com",
    "cta_sub": "Try it free"
  }
}
```

**Field notes:**
- `slides[].badge_color`: Hex color (`#RRGGBB`). Auto-assigned if omitted.
- `slides[].points`: Max 4 items fit well. Use `>>` marker style auto-applied.
- `slides[].quote`: Use `\\n` for line breaks in JSON.
- `closing`: Entire section is optional. Max 3 features fit well.

### Step 2: Generate GIF

```bash
python /path/to/create-gif-slides/scripts/create_gif_slides.py \
  --input /tmp/slides.json \
  --output /path/to/output.gif
```

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `--theme` | `dark` | `dark` or `light` |
| `--width` | `800` | Frame width in pixels |
| `--height` | `450` | Frame height in pixels |
| `--slide-hold` | `12` | Frames per slide (higher = longer display) |
| `--title-hold` | `12` | Frames for title |
| `--closing-hold` | `15` | Frames for closing |
| `--slide-duration` | `140` | Per-frame duration in ms |

**Typical output:** 80-100 frames, 200-400 KB, ~10s loop.

### Step 3: Clean Up

Delete the temporary JSON file after GIF creation.

## Design Constraints

- **Korean text**: Supported via AppleSDGothicNeo (macOS) or NotoSansCJK (Linux).
- **No emoji in points**: Use text markers like `>>` instead — emoji render as boxes in PIL.
- **Max 4 points per slide**: More will overflow the quote box area.
- **Quote max 2 lines**: Use `\\n` for line break.
- **Badge text**: Keep short (1-2 words). Width auto-calculated.

## Preset Badge Colors

Colors auto-cycle if `badge_color` omitted: cyan, purple, pink, teal, gold, blue, orange, green.

## Dependencies

- Python 3.8+
- Pillow (`pip install Pillow`)
- Korean font (AppleSDGothicNeo on macOS, NotoSansCJK on Linux)
