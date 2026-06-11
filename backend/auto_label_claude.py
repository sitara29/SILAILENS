import anthropic, base64, csv, os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# ── CONFIG ────────────────────────────────────────────────
API_KEY      = os.getenv("ANTHROPIC_API_KEY")
FOLDERS      = {
    "chola":   "./training_data/chola",
    "pallava": "./training_data/pallava",
}
OUTPUT_CSV   = "labels_claude.csv"
IMAGE_EXTS   = {".jpg", ".jpeg", ".jfif", ".png", ".webp", ".jpeg"}
# ─────────────────────────────────────────────────────────

if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file!")

client = anthropic.Anthropic(api_key=API_KEY)

PROMPT = """Look at this temple sculpture image carefully.

Identify whether each of these 4 ornamental features is PRESENT or ABSENT on the main sculpture figure:

1. HEADWEAR — any crown, tall headpiece, jata (matted hair), mukuta, turban, or elaborate hair ornament on the head
2. WEAPONS — any weapon held or displayed: trident, sword, chakra disc, bow, axe, mace, spear
3. WAISTBANDS — any ornate belt, girdle, beaded waistband, or hip ornament around the waist area
4. LEG_ORNAMENTS — any anklets, rings around ankles, leg bands, or ornaments on the legs/feet

IMPORTANT RULES:
- If the image shows a temple building or architectural panel with NO clear human/deity figure, return all 0s
- If an ornament is partially visible or unclear, mark it 0
- Focus only on the MAIN central figure

Reply with ONLY this exact format, nothing else:
headwear=1 or 0
weapons=1 or 0
waistbands=1 or 0
leg_ornaments=1 or 0"""

def encode_image(path: str) -> tuple:
    ext = Path(path).suffix.lower()
    mime = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".jfif": "image/jpeg", ".png": "image/png",
        ".webp": "image/webp"
    }.get(ext, "image/jpeg")
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8"), mime

def parse_response(text: str) -> dict:
    result = {"headwear": 0, "weapons": 0, "waistbands": 0, "leg_ornaments": 0}
    for line in text.strip().lower().splitlines():
        for key in result:
            if key in line:
                result[key] = 1 if "=1" in line.replace(" ", "") else 0
    return result

def label_image(img_path: str) -> dict:
    try:
        b64, mime = encode_image(img_path)
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": mime, "data": b64}},
                    {"type": "text", "text": PROMPT}
                ]
            }]
        )
        return parse_response(response.content[0].text)
    except Exception as e:
        print(f"    ERROR: {e}")
        return {"headwear": 0, "weapons": 0, "waistbands": 0, "leg_ornaments": 0}

# ── MAIN ──────────────────────────────────────────────────
rows = []
total = 0

print(f"API Key loaded: {API_KEY[:20]}...")

for dynasty, folder in FOLDERS.items():
    files = [f for f in sorted(os.listdir(folder))
             if Path(f).suffix.lower() in IMAGE_EXTS]
    print(f"\n{dynasty.upper()} — {len(files)} images")

    for i, fname in enumerate(files, 1):
        img_path = os.path.join(folder, fname)
        print(f"  [{i}/{len(files)}] {fname[:50]}...", end=" ", flush=True)

        labels = label_image(img_path)
        row = {
            "filename": fname,
            "dynasty": dynasty,
            **labels
        }
        rows.append(row)
        total += 1

        print(f"H={labels['headwear']} W={labels['weapons']} "
              f"WB={labels['waistbands']} LO={labels['leg_ornaments']}")

# ── SAVE CSV ──────────────────────────────────────────────
with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["filename","dynasty","headwear","weapons","waistbands","leg_ornaments"])
    writer.writeheader()
    writer.writerows(rows)

print(f"\n✓ Saved {total} rows to {OUTPUT_CSV}")
print(f"✓ Estimated cost: ~${total * 0.003:.2f}")