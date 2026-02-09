"""Remove duplicate products based on repeated image filenames.

Keeps the first occurrence of each image filename and removes subsequent
duplicates, then renumbers PKs and writes the cleaned fixture back.
"""

import json
from pathlib import Path
from datetime import datetime

workspace = Path(__file__).resolve().parents[1]
json_path = workspace / 'products' / 'fixtures' / 'products.json'
backup_version = json_path.with_name(f"products.json.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}")
removed_out = workspace / 'scripts' / 'removed_duplicate_products.json'

action_image = 'DP1202201517023245M.jpg'

# Read fixture data
with json_path.open(encoding='utf-8') as f:
    products = json.load(f)

# Backup the original fixture so the operation is reversible
backup_version.write_text(json.dumps(products, indent=3), encoding='utf-8')
print(f"Backup written to {backup_version}")

seen = set()
keep = []
removed = []
for p in products:
    img = p.get('fields', {}).get('image')
    if img == action_image:
        if img in seen:
            removed.append(p)
            continue
    # Track seen for any image so we remove duplicates globally (keeps first occurrence)
    if img:
        if img in seen:
            removed.append(p)
            continue
        seen.add(img)
    keep.append(p)

# Renumber PKs
for i, p in enumerate(keep, start=1):
    p['pk'] = i

# Write back
with json_path.open('w', encoding='utf-8') as f:
    json.dump(keep, f, indent=3)

with removed_out.open('w', encoding='utf-8') as f:
    json.dump({'removed_count': len(removed), 'removed': removed}, f, indent=2)

print(f"Removed duplicates: {len(removed)} (details in {removed_out})")
print(f"Kept products now: {len(keep)}")
