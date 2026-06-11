import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras import layers, models
import numpy as np
from PIL import Image
import os, random, csv
from sklearn.metrics import classification_report

DATASET_PATH = './training_data/'
CSV_PATH     = './labels_claude.csv'
IMG_SIZE     = 224
BATCH_SIZE   = 8
SEED         = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

ORNAMENTS = ['headwear', 'weapons', 'waistbands', 'leg_ornaments']

# ── LOAD DATA FROM CSV ────────────────────────────────────
print("Loading images from CSV labels...")

X, y = [], []
skipped = 0

with open(CSV_PATH, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        dynasty  = row['dynasty']
        filename = row['filename']
        filepath = os.path.join(DATASET_PATH, dynasty, filename)

        if not os.path.exists(filepath):
            skipped += 1
            continue

        try:
            img = Image.open(filepath).convert('RGB').resize((IMG_SIZE, IMG_SIZE))
            X.append(np.array(img, dtype=np.float32))
            y.append([int(row[o]) for o in ORNAMENTS])
        except Exception as e:
            skipped += 1

print(f"Loaded: {len(X)} images | Skipped: {skipped}")

X = preprocess_input(np.array(X))
y = np.array(y, dtype=np.float32)

# Print label distribution
print("\nLabel distribution:")
for i, name in enumerate(ORNAMENTS):
    count = int(y[:, i].sum())
    print(f"  {name:15s}: {count}/{len(y)} ({count/len(y)*100:.0f}%)")

# ── TRAIN/VAL SPLIT ───────────────────────────────────────
idx = list(range(len(X)))
random.shuffle(idx)
split   = int(0.8 * len(idx))
tr_idx  = idx[:split]
val_idx = idx[split:]

X_train = X[tr_idx];  y_train = y[tr_idx]
X_val   = X[val_idx]; y_val   = y[val_idx]
print(f"\nTrain: {len(X_train)} | Val: {len(X_val)}\n")

# ── AUGMENTATION ──────────────────────────────────────────
def augment(img):
    if random.random() > 0.5:
        img = np.fliplr(img)
    img = img + random.uniform(-15, 15)
    img = np.clip(img, -128, 128)
    if random.random() > 0.7:
        img = img * random.uniform(0.85, 1.15)
        img = np.clip(img, -128, 128)
    return img

# ── MODEL: MobileNetV2 multi-label ───────────────────────
base = MobileNetV2(weights='imagenet', include_top=False,
                   input_shape=(IMG_SIZE, IMG_SIZE, 3))
base.trainable = False

model = models.Sequential([
    base,
    layers.GlobalAveragePooling2D(),
    layers.BatchNormalization(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.4),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(4, activation='sigmoid')  # 4 ornament outputs
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

model.summary()

# ── PHASE 1: Train head ───────────────────────────────────
print("\n" + "="*50)
print("PHASE 1: Training head (25 epochs max)...")
print("="*50)

best_loss = float('inf')
no_improv = 0

for epoch in range(25):
    idx_e = list(range(len(X_train)))
    random.shuffle(idx_e)
    losses = []

    for i in range(0, len(idx_e), BATCH_SIZE):
        b  = idx_e[i:i+BATCH_SIZE]
        Xb = np.array([augment(X_train[j]) for j in b])
        yb = y_train[b]
        loss = model.train_on_batch(Xb, yb)
        losses.append(loss[0])

    # Validation
    val_preds = model.predict(X_val, verbose=0)
    val_loss  = tf.keras.losses.binary_crossentropy(y_val, val_preds).numpy().mean()
    val_bin   = (val_preds >= 0.5).astype(int)
    val_acc   = np.mean(val_bin == y_val)

    print(f"Epoch {epoch+1:02d} — loss: {np.mean(losses):.4f} — "
          f"val_loss: {val_loss:.4f} — val_acc: {val_acc:.4f}")

    if val_loss < best_loss:
        best_loss = val_loss
        model.save_weights('best_ornament_p1.weights.h5')
        no_improv = 0
        print(f"  ✓ Best val_loss: {best_loss:.4f}")
    else:
        no_improv += 1
        if no_improv >= 8:
            print("  Early stop")
            break

model.load_weights('best_ornament_p1.weights.h5')

# ── PHASE 2: Fine-tune ────────────────────────────────────
print("\n" + "="*50)
print("PHASE 2: Fine-tuning (30 epochs max)...")
print("="*50)

base.trainable = True
for layer in base.layers[:-30]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(0.00005),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

best_loss2 = best_loss
no_improv2 = 0

for epoch in range(30):
    idx_e = list(range(len(X_train)))
    random.shuffle(idx_e)
    losses = []

    for i in range(0, len(idx_e), BATCH_SIZE):
        b  = idx_e[i:i+BATCH_SIZE]
        Xb = np.array([augment(X_train[j]) for j in b])
        yb = y_train[b]
        loss = model.train_on_batch(Xb, yb)
        losses.append(loss[0])

    val_preds = model.predict(X_val, verbose=0)
    val_loss  = tf.keras.losses.binary_crossentropy(y_val, val_preds).numpy().mean()
    val_bin   = (val_preds >= 0.5).astype(int)
    val_acc   = np.mean(val_bin == y_val)

    print(f"Epoch {epoch+1:02d} — loss: {np.mean(losses):.4f} — "
          f"val_loss: {val_loss:.4f} — val_acc: {val_acc:.4f}")

    if val_loss < best_loss2:
        best_loss2 = val_loss
        model.save_weights('best_ornament_p2.weights.h5')
        no_improv2 = 0
        print(f"  ✓ Best val_loss: {best_loss2:.4f}")
    else:
        no_improv2 += 1
        if no_improv2 >= 10:
            print("  Early stop")
            break

# Load best weights
if os.path.exists('best_ornament_p2.weights.h5'):
    model.load_weights('best_ornament_p2.weights.h5')
    print("Loaded Phase 2 best weights")
else:
    model.load_weights('best_ornament_p1.weights.h5')
    print("Using Phase 1 best weights")

# ── FINAL EVALUATION ──────────────────────────────────────
print("\n" + "="*50)
print("FINAL RESULTS PER ORNAMENT")
print("="*50)

val_preds = model.predict(X_val, verbose=0)
val_bin   = (val_preds >= 0.5).astype(int)

for i, name in enumerate(ORNAMENTS):
    report = classification_report(
        y_val[:, i], val_bin[:, i],
        target_names=['absent', 'present'],
        output_dict=True, zero_division=0
    )
    acc = np.mean(val_bin[:, i] == y_val[:, i])
    print(f"\n{name.upper()}:")
    print(f"  Accuracy : {acc*100:.1f}%")
    print(f"  Precision: {report['present']['precision']*100:.1f}%")
    print(f"  Recall   : {report['present']['recall']*100:.1f}%")
    print(f"  F1-score : {report['present']['f1-score']*100:.1f}%")

overall = np.mean(val_bin == y_val)
print(f"\nOVERALL ACCURACY: {overall*100:.1f}%")

# ── SAVE MODEL ────────────────────────────────────────────
model.save('ornament_model.keras')
print("\n✓ Saved: ornament_model.keras")