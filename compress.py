"""Compress all images in nanqiang-balai to ~1MB target"""
from PIL import Image
import os, sys, tempfile

BASE = r"C:\Users\73662\Desktop\nanqiang-balai\img"

def compress(path, target_mb=1.0):
    sz = os.path.getsize(path)
    if sz <= target_mb * 1024 * 1024 * 1.1:
        print(f"  SKIP {os.path.basename(path)} ({sz/1024/1024:.2f}MB)")
        return
    
    img = Image.open(path)
    ext = os.path.splitext(path)[1].lower()
    
    # Resize if huge dimensions
    max_dim = 2400
    if max(img.size) > max_dim:
        ratio = max_dim / max(img.size)
        img = img.resize((int(img.width*ratio), int(img.height*ratio)), Image.LANCZOS)
    
    name = os.path.basename(path)
    quality = 85 if ext in ('.jpg', '.jpeg') else None
    
    if ext in ('.jpg', '.jpeg'):
        # Binary search for quality
        for q in [85, 75, 65, 55, 45, 35, 25]:
            buf = os.path.gettempdir() + "\\_compress_tmp.jpg"
            img.convert("RGB").save(buf, "JPEG", quality=q, optimize=True)
            nsz = os.path.getsize(buf)
            if nsz <= target_mb * 1024 * 1024:
                os.replace(buf, path)
                print(f"  OK   {name} {sz/1024/1024:.2f}MB -> {nsz/1024/1024:.2f}MB (q={q})")
                return
        # fallback: save whatever we got
        os.replace(buf, path)
        print(f"  FALL {name} -> {os.path.getsize(path)/1024/1024:.2f}MB")
    elif ext == '.png':
        # Convert to RGB, save as jpg-like: resize + save PNG with optimize
        img_rgb = img.convert("RGBA") if img.mode == 'RGBA' else img.convert("RGBA")
        bg = Image.new("RGBA", img_rgb.size, (0,0,0,0))
        # Try saving as PNG with optimized
        for max_px in [2400, 1600, 1200, 800]:
            tmp = img_rgb.copy()
            if max(tmp.size) > max_px:
                ratio = max_px / max(tmp.size)
                tmp = tmp.resize((int(tmp.width*ratio), int(tmp.height*ratio)), Image.LANCZOS)
            buf = os.path.gettempdir() + "\\_compress_tmp.png"
            tmp.save(buf, "PNG", optimize=True)
            nsz = os.path.getsize(buf)
            if nsz <= target_mb * 1024 * 1024:
                os.replace(buf, path)
                print(f"  OK   {name} {sz/1024/1024:.2f}MB -> {nsz/1024/1024:.2f}MB (max_px={max_px})")
                return
        # If still too big, convert PNG to JPEG
        img_rgb.convert("RGB").save(path.replace('.png','.jpg'), "JPEG", quality=80, optimize=True)
        os.remove(path)
        print(f"  CNVT {name} -> .jpg")
    else:
        print(f"  SKIP unsupported {name}")

for subdir in ["cast", "gallery", "posters"]:
    folder = os.path.join(BASE, subdir)
    if not os.path.isdir(folder):
        continue
    print(f"\n=== {subdir} ===")
    for f in os.listdir(folder):
        fp = os.path.join(folder, f)
        if os.path.isfile(fp):
            compress(fp)

# hero-cover
hero = os.path.join(BASE, "hero-cover.jpg")
if os.path.exists(hero):
    print(f"\n=== hero-cover ===")
    compress(hero, 1.5)
