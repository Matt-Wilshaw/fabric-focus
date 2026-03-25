"""Print basic statistics about product images in fixtures vs the media folder.

This is a quick analysis script used during data clean-up.
"""

import json
from pathlib import Path
from collections import defaultdict

workspace = Path('.')
json_path = workspace / 'products' / 'fixtures' / 'products.json'
media_dir = workspace / 'media'

products = json.loads(json_path.read_text(encoding='utf-8'))
media_files = set(p.name for p in media_dir.iterdir() if p.is_file())

images_to_products = defaultdict(list)
for p in products:
    img = p.get('fields', {}).get('image')
    images_to_products[img].append(p['pk'])

total_products = len(products)
unique_images_referenced = len([img for img in images_to_products.keys() if img])
media_count = len(media_files)

# duplicates: images referenced by more than one product (and not empty)
dup_images = {img: pks for img, pks in images_to_products.items() if img and len(pks) > 1}

missing_images = [img for img in images_to_products.keys() if img and img not in media_files]

print(f"total_products={total_products}")
print(f"unique_images_referenced={unique_images_referenced}")
print(f"media_files_count={media_count}")
print(f"duplicate_images_count={len(dup_images)}")
if dup_images:
    print('\nDuplicate images used by multiple products (image: [pks])')
    for img, pks in list(dup_images.items())[:20]:
        print(f"  {img}: {pks}")

print('\nMissing images (referenced but not in media):')
print(missing_images)

# If there are no missing images, show which image(s) may explain 124 products vs 123 files
print('\nSummary:')
print('  Products:', total_products)
print('  Unique image filenames referenced:', unique_images_referenced)
print('  Files in media:', media_count)

# Check if unique_images_referenced > media_count explained by duplicates absent or not

# Show any empty image fields
empty_image_pks = [p['pk'] for p in products if not p.get('fields', {}).get('image')]
print('\nProducts with empty image field (pks):', empty_image_pks)
