#!/usr/bin/env python3
"""
Create animated GIF slideshows from structured JSON input.

Usage:
    python create_gif_slides.py --input slides.json --output output.gif [options]

Input JSON format: see SKILL.md for full specification.
"""
import argparse, json, math, sys
from pathlib import Path
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow required. pip install Pillow", file=sys.stderr); sys.exit(1)

THEMES = {
    "dark": {
        "bg_top": (18,18,32), "bg_bottom": (30,30,52),
        "text_primary": (255,255,255), "text_secondary": (160,160,180),
        "text_dim": (80,80,100), "card_bg": (35,35,55),
        "line_color": (50,50,70), "dot_color": (60,60,90), "accent": (0,200,220),
    },
    "light": {
        "bg_top": (245,245,250), "bg_bottom": (230,230,240),
        "text_primary": (30,30,40), "text_secondary": (100,100,120),
        "text_dim": (180,180,190), "card_bg": (255,255,255),
        "line_color": (210,210,220), "dot_color": (220,220,230), "accent": (0,140,180),
    },
}

DEFAULT_BADGE_COLORS = [
    (0,200,220),(140,80,220),(220,80,160),(0,180,160),
    (220,180,40),(60,120,255),(220,120,40),(100,200,80),
]

FONT_PATHS = [
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
]

def load_font(size, bold=False):
    for path in FONT_PATHS:
        try:
            idx = 8 if bold else 3
            return ImageFont.truetype(path, size, index=idx)
        except (OSError, IndexError):
            try: return ImageFont.truetype(path, size)
            except OSError: continue
    return ImageFont.load_default()

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0,2,4))

def draw_bg(draw, w, h, theme, fi=0):
    top, bot = theme["bg_top"], theme["bg_bottom"]
    for y in range(h):
        t = y/h
        draw.line([(0,y),(w,y)], fill=(int(top[0]+(bot[0]-top[0])*t), int(top[1]+(bot[1]-top[1])*t), int(top[2]+(bot[2]-top[2])*t)))
    for x in range(0,w,40):
        for y in range(0,h,40):
            o = int(math.sin((x+y+fi*5)*0.02)*2)
            draw.ellipse([x+o,y+o,x+2+o,y+2+o], fill=theme["dot_color"])

def draw_badge(draw, x, y, text, color, font, tc=(255,255,255)):
    tw = len(text)*10+20
    draw.rounded_rectangle((x,y,x+tw,y+28), radius=14, fill=color)
    draw.text((x+tw//2,y+14), text, fill=tc, font=font, anchor="mm")

def draw_progress(draw, cur, total, w, y, theme):
    bw = min(300, w-100); bx = (w-bw)//2
    draw.rounded_rectangle((bx,y,bx+bw,y+6), radius=3, fill=theme["line_color"])
    fw = int(bw*cur/total)
    if fw > 0: draw.rounded_rectangle((bx,y,bx+fw,y+6), radius=3, fill=theme["accent"])
    for i in range(total):
        dx = bx+int(bw*i/(total-1)) if total>1 else bx
        draw.ellipse([dx-4,y-4,dx+4,y+10], fill=theme["text_primary"] if i<=cur-1 else theme["text_dim"])

def make_title(data, w, h, theme, fonts):
    img = Image.new("RGB",(w,h)); draw = ImageDraw.Draw(img); draw_bg(draw,w,h,theme)
    a = theme["accent"]
    draw.line([(150,130),(w-150,130)], fill=a, width=1)
    draw.line([(150,310),(w-150,310)], fill=a, width=1)
    if data.get("date"): draw.text((w//2,145), data["date"], fill=theme["text_secondary"], font=fonts["sm"], anchor="mt")
    draw.text((w//2,175), data.get("title","Slides"), fill=theme["text_primary"], font=fonts["xl"], anchor="mt")
    if data.get("subtitle"): draw.text((w//2,230), data["subtitle"], fill=a, font=fonts["xl"], anchor="mt")
    if data.get("meta"): draw.text((w//2,280), data["meta"], fill=theme["text_secondary"], font=fonts["sm"], anchor="mt")
    draw_badge(draw, w//2-40, 340, "RECAP", (140,80,220), fonts["smb"])
    return img

def make_slide(s, idx, total, w, h, theme, fonts, fi=0):
    img = Image.new("RGB",(w,h)); draw = ImageDraw.Draw(img); draw_bg(draw,w,h,theme,fi)
    bc = DEFAULT_BADGE_COLORS[idx % len(DEFAULT_BADGE_COLORS)]
    if s.get("badge_color"):
        try: bc = hex_to_rgb(s["badge_color"])
        except: pass
    num = s.get("num", f"{idx+1:02d}")
    draw.text((30,15), num, fill=theme["line_color"], font=fonts["xl"])
    draw_badge(draw, 80, 28, s.get("badge",f"SLIDE {num}"), bc, fonts["smb"])
    if s.get("speaker"): draw.text((w-30,30), s["speaker"], fill=theme["text_secondary"], font=fonts["sm"], anchor="rt")
    draw.line([(30,65),(w-30,65)], fill=theme["line_color"], width=1)
    draw.text((30,78), s.get("title",""), fill=theme["text_primary"], font=fonts["lg"])
    pts = s.get("points",[])
    for i,p in enumerate(pts):
        y = 125+i*36
        draw.text((45,y), ">>", fill=bc, font=fonts["md"])
        draw.text((80,y), p, fill=(210,210,230), font=fonts["md"])
    q = s.get("quote","")
    if q:
        qy = 280 if len(pts)>3 else 260
        draw.rounded_rectangle((30,qy,w-30,qy+75), radius=8, fill=theme["card_bg"])
        draw.rounded_rectangle((30,qy,34,qy+75), radius=2, fill=bc)
        lines = q.split("\\n") if "\\n" in q else q.split("\n")
        for i,l in enumerate(lines):
            draw.text((50,qy+12+i*28), l, fill=theme["text_secondary"], font=fonts["md"])
    draw_progress(draw, idx+1, total, w, 410, theme)
    draw.text((w-30,410), f"{idx+1}/{total}", fill=theme["text_dim"], font=fonts["sm"], anchor="rt")
    return img

def make_closing(c, w, h, theme, fonts):
    img = Image.new("RGB",(w,h)); draw = ImageDraw.Draw(img); draw_bg(draw,w,h,theme,10)
    a = theme["accent"]
    draw.line([(150,100),(w-150,100)], fill=a, width=1)
    if c.get("headline"): draw.text((w//2,115), c["headline"], fill=theme["text_secondary"], font=fonts["mdb"], anchor="mt")
    if c.get("title"): draw.text((w//2,155), c["title"], fill=theme["text_primary"], font=fonts["xl"], anchor="mt")
    feats = c.get("features",[])
    if feats:
        n = len(feats); fw = min(190,(w-60)//n-20); tw = n*(fw+20)-20; sx = (w-tw)//2
        for i,f in enumerate(feats):
            x = sx+i*(fw+20)
            draw.rounded_rectangle((x,215,x+fw,280), radius=10, fill=theme["card_bg"])
            draw.text((x+fw//2,232), f.get("label",""), fill=a, font=fonts["smb"], anchor="mt")
            draw.text((x+fw//2,260), f.get("desc",""), fill=theme["text_secondary"], font=fonts["sm"], anchor="mt")
    if c.get("cta_text"):
        draw.rounded_rectangle((w//2-120,310,w//2+120,350), radius=20, fill=a)
        draw.text((w//2,330), c["cta_text"], fill=theme["text_primary"], font=fonts["mdb"], anchor="mm")
    if c.get("cta_sub"): draw.text((w//2,375), c["cta_sub"], fill=theme["text_secondary"], font=fonts["sm"], anchor="mt")
    draw.line([(150,410),(w-150,410)], fill=a, width=1)
    return img

def create_gif(data, output, theme_name="dark", width=800, height=450,
               title_hold=12, slide_hold=12, closing_hold=15,
               title_dur=130, slide_dur=140, closing_dur=160):
    theme = THEMES.get(theme_name, THEMES["dark"])
    fonts = {"xl":load_font(42,True),"lg":load_font(28,True),"mdb":load_font(22,True),
             "md":load_font(20,False),"sm":load_font(16,False),"smb":load_font(16,True)}
    frames, durs = [], []
    tf = make_title(data,width,height,theme,fonts)
    for _ in range(title_hold): frames.append(tf); durs.append(title_dur)
    slides = data.get("slides",[])
    for i,s in enumerate(slides):
        for f in range(slide_hold):
            frames.append(make_slide(s,i,len(slides),width,height,theme,fonts,f)); durs.append(slide_dur)
    cl = data.get("closing")
    if cl:
        cf = make_closing(cl,width,height,theme,fonts)
        for _ in range(closing_hold): frames.append(cf); durs.append(closing_dur)
    out = Path(output); out.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(str(out), save_all=True, append_images=frames[1:], duration=durs, loop=0, optimize=True)
    print(f"Created: {out}\nFrames: {len(frames)}, Size: {out.stat().st_size/1024:.0f} KB")

def main():
    p = argparse.ArgumentParser(description="Create animated GIF slideshows")
    p.add_argument("--input", required=True); p.add_argument("--output", required=True)
    p.add_argument("--theme", default="dark", choices=list(THEMES.keys()))
    p.add_argument("--width", type=int, default=800); p.add_argument("--height", type=int, default=450)
    p.add_argument("--title-hold", type=int, default=12); p.add_argument("--slide-hold", type=int, default=12)
    p.add_argument("--closing-hold", type=int, default=15)
    p.add_argument("--title-duration", type=int, default=130); p.add_argument("--slide-duration", type=int, default=140)
    p.add_argument("--closing-duration", type=int, default=160)
    a = p.parse_args()
    with open(a.input,"r",encoding="utf-8") as f: data = json.load(f)
    create_gif(data, a.output, a.theme, a.width, a.height, a.title_hold, a.slide_hold, a.closing_hold, a.title_duration, a.slide_duration, a.closing_duration)

if __name__ == "__main__": main()
