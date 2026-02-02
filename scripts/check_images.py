import json
import os
from pathlib import Path

workspace = Path(__file__).resolve().parents[1]
json_path = workspace / 'products' / 'fixtures' / 'products.json'
media_dir = workspace / 'media'

with json_path.open(encoding='utf-8') as f:
    products = json.load(f)

referenced = []
for p in products:
    img = p.get('fields', {}).get('image')
    if img and isinstance(img, str) and img.strip():
        referenced.append(img.strip())

referenced_set = set(referenced)
media_files = set([p.name for p in media_dir.iterdir() if p.is_file()]) if media_dir.exists() else set()

missing = sorted(referenced_set - media_files)
present = sorted(referenced_set & media_files)

orphan_media = sorted(media_files - referenced_set)

print(f"total_products_with_image_field={len(referenced)}")
print(f"unique_referenced_images={len(referenced_set)}")
print(f"media_files_count={len(media_files)}")
print(f"missing_count={len(missing)}")
print('missing_sample=' + str(missing[:50]))
print(f"orphan_media_count={len(orphan_media)}")
print('orphan_media_sample=' + str(orphan_media[:50]))

# Also save full lists to files for review
out = workspace / 'scripts' / 'image_check_results.json'
with out.open('w', encoding='utf-8') as f:
    json.dump({'missing': missing, 'present': present, 'orphan_media': orphan_media}, f, indent=2)

print(f"Wrote full results to {out}")
