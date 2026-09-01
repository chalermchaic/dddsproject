"""รันครั้งเดียว: สร้างทุกไฟล์ + zip ให้พร้อมส่ง"""
import os, zipfile, textwrap

FILES = {
    "Dockerfile": r'''...''',            # ผมจะเติมเนื้อหาจริงให้ครบทุกคีย์
    "requirements.txt": r'''...''',
    "db/schema.sql": r'''...''',
    # ... ครบทุกไฟล์ในโครงสร้างด้านบน
}

ROOT = "smart-crm-analytics"
for path, content in FILES.items():
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(content).lstrip())

with zipfile.ZipFile(f"{ROOT}.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for r, _, fs in os.walk(ROOT):
        for fn in fs:
            p = os.path.join(r, fn)
            z.write(p, os.path.relpath(p, "."))
print(f"✅ เสร็จแล้ว → {ROOT}.zip")