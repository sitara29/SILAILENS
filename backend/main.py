from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from supabase import create_client
import os, uuid, numpy as np
from datetime import datetime, timezone
from PIL import Image
import io
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

load_dotenv()
app = FastAPI(title="SilaiLens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

# ── LOAD BOTH MODELS ─────────────────────────────────────
dynasty_model  = None
ornament_model = None

try:
    dynasty_model = tf.keras.models.load_model("silailens_model.keras")
    print("✓ Dynasty model loaded")
except Exception as e:
    print(f"Dynasty model missing: {e}")

try:
    ornament_model = tf.keras.models.load_model("ornament_model.keras")
    print("✓ Ornament model loaded")
except Exception as e:
    print(f"Ornament model missing: {e}")

ORNAMENT_NAMES = ["headwear", "weapons", "waistbands", "leg_ornaments"]

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((224, 224))
    arr = np.array(img, dtype=np.float32)
    arr = preprocess_input(arr)
    return np.expand_dims(arr, axis=0)

def predict_dynasty(img_array):
    """Model 1 — predicts Chola or Pallava"""
    prob = float(dynasty_model.predict(img_array, verbose=0)[0][0])
    dynasty    = "Pallava" if prob >= 0.5 else "Chola"
    confidence = prob if dynasty == "Pallava" else (1.0 - prob)
    return dynasty, round(confidence, 2)

def predict_ornaments(img_array):
    """Model 2 — predicts which ornaments are present"""
    if ornament_model is None:
        return None
    probs = ornament_model.predict(img_array, verbose=0)[0]
    return {
        name: {
            "present":    bool(probs[i] >= 0.5),
            "confidence": round(float(probs[i]), 2)
        }
        for i, name in enumerate(ORNAMENT_NAMES)
    }

HISTORICAL_CONTEXT = {
    "Chola": (
        "Chola Dynasty (9th-13th century CE) was one of the longest-ruling dynasties "
        "of Tamil Nadu. Sculptures are renowned for intricate bronze casting and stone "
        "carvings featuring elaborate headwear, weapons, ornate waistbands, and leg ornaments."
    ),
    "Pallava": (
        "Pallava Dynasty (3rd-9th century CE) pioneered rock-cut architecture and refined "
        "sculptural traditions. Their sculptures feature tall crowns, flowing drapery, and "
        "simpler ornamentation compared to later Chola work."
    ),
    "Unknown": (
        "Dynasty could not be identified with sufficient confidence. Please try with a clearer image."
    )
}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "dynasty_model": "loaded" if dynasty_model else "missing",
        "ornament_model": "loaded" if ornament_model else "missing",
        "pipeline": "dynasty → ornaments"
    }

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(400, "Invalid file type. Accepted: JPEG, PNG, WEBP")

    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(400, "File too large. Max 10MB")

    # Preprocess once
    arr = preprocess_image(image_bytes)

    # Model 1 → Dynasty
    dynasty, confidence = predict_dynasty(arr)

    ornaments = predict_ornaments(arr)
    if ornaments is None:
        ornaments = {"headwear": {"present": False, "confidence": 0.0},
                     "weapons": {"present": False, "confidence": 0.0},
                     "waistbands": {"present": False, "confidence": 0.0},
                     "leg_ornaments": {"present": False, "confidence": 0.0}}

    historical_context = HISTORICAL_CONTEXT.get(dynasty, "")

    sculpture_id  = str(uuid.uuid4())
    timestamp     = datetime.now(timezone.utc).isoformat()
    safe_filename = f"{sculpture_id}_{file.filename or 'sculpture.jpg'}"

    try:
        supabase.storage.from_("sculpture-images").upload(
            f"sculptures/{safe_filename}",
            image_bytes,
            {"content-type": file.content_type or "image/jpeg", "upsert": "true"},
        )
        image_url = supabase.storage.from_("sculpture-images").get_public_url(
            f"sculptures/{safe_filename}"
        )
    except Exception as e:
        print(f"Storage upload failed: {e}")
        image_url = ""

    metadata = {
        "sculpture_id":       sculpture_id,
        "timestamp":          timestamp,
        "dynasty":            dynasty,
        "dynasty_confidence": confidence,
        "ornaments":          ornaments,
        "image_filename":     file.filename,
        "historical_context": historical_context,
        "pipeline":           "dynasty_model → ornament_model"
    }

    try:
        result = supabase.table("analyses").insert({
            "id":                       sculpture_id,
            "user_id":                  None,
            "image_url":                image_url,
            "dynasty":                  dynasty,
            "dynasty_confidence":       confidence,
            "headwear_present":         ornaments["headwear"]["present"],
            "headwear_confidence":      ornaments["headwear"]["confidence"],
            "weapons_present":          ornaments["weapons"]["present"],
            "weapons_confidence":       ornaments["weapons"]["confidence"],
            "waistbands_present":       ornaments["waistbands"]["present"],
            "waistbands_confidence":    ornaments["waistbands"]["confidence"],
            "leg_ornaments_present":    ornaments["leg_ornaments"]["present"],
            "leg_ornaments_confidence": ornaments["leg_ornaments"]["confidence"],
            "historical_context":       historical_context,
            "metadata_json":            metadata,
        }).execute()
        analysis_id = result.data[0]["id"]
    except Exception as e:
        print(f"DB insert failed: {e}")
        analysis_id = sculpture_id

    return {
        "analysis_id":        analysis_id,
        "dynasty":            dynasty,
        "dynasty_confidence": confidence,
        "ornaments":          ornaments,
        "historical_context": historical_context,
        "image_url":          image_url,
        "metadata":           metadata,
    }