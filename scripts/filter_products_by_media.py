"""Filter products fixture entries to those with existing media files.

This script overwrites `products/fixtures/products.json` after:
- backing it up with a timestamp
- removing entries whose `image` field is missing from `media/`
- renumbering primary keys consecutively (important for fixture integrity)

Note: If other fixtures reference these PKs, those fixtures will need updating.
"""

import json
from pathlib import Path
from datetime import datetime

workspace = Path(__file__).resolve().parents[1]
json_path = workspace / 'products' / 'fixtures' / 'products.json'
media_dir = workspace / 'media'
backup_path = json_path.with_suffix('.json.bak')
removed_out = workspace / 'scripts' / 'removed_products.json'

# Read fixture data
with json_path.open(encoding='utf-8') as f:
    products = json.load(f)

# Backup the original fixture so changes are reversible
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
backup_version = json_path.with_name(f"products.json.bak.{timestamp}")
backup_path.write_text(json.dumps(products, indent=3), encoding='utf-8')
print(f"Backup written to {backup_version}")

media_files = set(p.name for p in media_dir.iterdir() if p.is_file()) if media_dir.exists() else set()

keep_entries = []
removed_entries = []
for p in products:
    img = p.get('fields', {}).get('image')
    if img and isinstance(img, str) and img in media_files:
        keep_entries.append(p)
    else:
        removed_entries.append(p)

# Renumber PKs consecutively starting at 1 (Django fixtures often expect this)
for i, p in enumerate(keep_entries, start=1):
    p['pk'] = i

# Write filtered file (overwrites original)
with json_path.open('w', encoding='utf-8') as f:
    json.dump(keep_entries, f, indent=3)

# Write removed entries for review
with removed_out.open('w', encoding='utf-8') as f:
    json.dump({'removed_count': len(removed_entries), 'removed': removed_entries}, f, indent=2)

print(f"Total original products: {len(products)}")
print(f"Kept products: {len(keep_entries)}")
print(f"Removed products: {len(removed_entries)} (details in {removed_out})")
print("Note: PKs have been renumbered consecutively starting at 1. If other fixtures reference these PKs, they may need updating.")
