import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras import layers, models
import numpy as np
from PIL import Image
import os, random
from sklearn.metrics import classification_report

DATASET_PATH = './training_data/'
IMG_SIZE     = 224
BATCH_SIZE   = 8
SEED         = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

# ── LOAD ──────────────────────────────────────────────────
def load_folder(folder, label):
    imgs, lbls = [], []
    for fname in os.listdir(folder):
        ext = os.path.splitext(fname)[1].lower()
        if ext not in {'.jpg','.jpeg','.jfif','.png','.webp'}:
            continue
        try:
            img = Image.open(os.path.join(folder, fname)).convert('RGB').resize((IMG_SIZE, IMG_SIZE))
            imgs.append(np.array(img, dtype=np.float32))
            lbls.append(label)
        except:
            pass
    print(f"  {os.path.basename(folder)}: {len(imgs)} images")
    return imgs, lbls

print("Loading...")
c_imgs, c_lbls = load_folder(DATASET_PATH+'chola',   0)
p_imgs, p_lbls = load_folder(DATASET_PATH+'pallava', 1)

all_imgs = c_imgs + p_imgs
all_lbls = c_lbls + p_lbls

combined = list(zip(all_imgs, all_lbls))
random.shuffle(combined)
all_imgs, all_lbls = zip(*combined)

X = preprocess_input(np.array(all_imgs))
y = np.array(all_lbls)

print(f"Total: {len(X)} | Chola: {sum(y==0)} | Pallava: {sum(y==1)}")

split   = int(0.8 * len(X))
X_train = X[:split]; y_train = y[:split]
X_val   = X[split:]; y_val   = y[split:]
print(f"Train: {len(X_train)} | Val: {len(X_val)}\n")

# ── AUGMENTATION ──────────────────────────────────────────
def augment(img, label):
    if random.random() > 0.5:
        img = np.fliplr(img)
    img = img + random.uniform(-20, 20)
    img = np.clip(img, -128, 128)
    if label == 1:
        if random.random() > 0.5:
            img = np.rot90(img)
        if random.random() > 0.5:
            zoom_factor = random.uniform(0.9, 1.1)
            h, w, _ = img.shape
            nh, nw = int(h*zoom_factor), int(w*zoom_factor)
            img = np.array(Image.fromarray(img.astype(np.uint8)).resize((nw, nh)))
            img = np.array(Image.fromarray(img.astype(np.uint8)).resize((w, h)))
        if random.random() > 0.5:
            img = img * random.uniform(0.9, 1.1)
            img = np.clip(img, -128, 128)
    return img

# ── MODEL: MobileNetV2 ────────────────────────────────────
base = MobileNetV2(weights='imagenet', include_top=False,
                   input_shape=(IMG_SIZE, IMG_SIZE, 3))
base.trainable = False

model = models.Sequential([
    base,
    layers.GlobalAveragePooling2D(),
    layers.BatchNormalization(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.4),
    layers.Dense(1, activation='sigmoid')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# ── PHASE 1: Head only ────────────────────────────────────
print("="*50)
print("PHASE 1: Training head (20 epochs max)...")
print("="*50)

best_acc  = 0
no_improv = 0

for epoch in range(20):
    idx = list(range(len(X_train)))
    random.shuffle(idx)
    losses = []
    for i in range(0, len(idx), BATCH_SIZE):
        b = idx[i:i+BATCH_SIZE]
        Xb = np.array([augment(X_train[j], y_train[j]) for j in b])
        yb = y_train[b]
        loss = model.train_on_batch(Xb, yb)
        losses.append(loss[0])

    preds   = (model.predict(X_val, verbose=0).ravel() >= 0.5).astype(int)
    val_acc = np.mean(preds == y_val)
    print(f"Epoch {epoch+1:02d} — loss: {np.mean(losses):.4f} — val_acc: {val_acc:.4f} ({int(val_acc*len(y_val))}/{len(y_val)})")

    if val_acc > best_acc:
        best_acc = val_acc
        model.save_weights('best_p1.weights.h5')
        no_improv = 0
        print(f"  ✓ Best: {best_acc:.4f}")
    else:
        no_improv += 1
        if no_improv >= 8:
            print("  Early stop")
            break

model.load_weights('best_p1.weights.h5')
print(f"\nPhase 1 best: {best_acc*100:.1f}%\n")

# ── PHASE 2: Fine-tuning ──────────────────────────────────
print("="*50)
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

best_acc2  = best_acc
no_improv2 = 0

for epoch in range(30):
    idx = list(range(len(X_train)))
    random.shuffle(idx)
    losses = []
    for i in range(0, len(idx), BATCH_SIZE):
        b = idx[i:i+BATCH_SIZE]
        Xb = np.array([augment(X_train[j], y_train[j]) for j in b])
        yb = y_train[b]
        loss = model.train_on_batch(Xb, yb)
        losses.append(loss[0])

    preds   = (model.predict(X_val, verbose=0).ravel() >= 0.5).astype(int)
    val_acc = np.mean(preds == y_val)
    print(f"Epoch {epoch+1:02d} — loss: {np.mean(losses):.4f} — val_acc: {val_acc:.4f} ({int(val_acc*len(y_val))}/{len(y_val)})")

    if val_acc > best_acc2:
        best_acc2 = val_acc
        model.save_weights('best_p2.weights.h5')
        no_improv2 = 0
        print(f"  ✓ Best: {best_acc2:.4f}")
    else:
        no_improv2 += 1
        if no_improv2 >= 10:
            print("  Early stop")
            break

if os.path.exists('best_p2.weights.h5'):
    model.load_weights('best_p2.weights.h5')
    print("Loaded Phase 2 best weights")
else:
    model.load_weights('best_p1.weights.h5')
    print("Phase 2 did not improve, using Phase 1")

# ── FINAL RESULTS ─────────────────────────────────────────
preds       = (model.predict(X_val, verbose=0).ravel() >= 0.5).astype(int)
final       = np.mean(preds == y_val)
chola_acc   = np.mean(preds[y_val==0] == 0) if (y_val==0).any() else 0
pallava_acc = np.mean(preds[y_val==1] == 1) if (y_val==1).any() else 0

print(f"\n{'='*50}")
print(f"FINAL ACCURACY  : {final*100:.1f}%")
print(f"Chola accuracy  : {chola_acc*100:.1f}%")
print(f"Pallava accuracy: {pallava_acc*100:.1f}%")

# Per-class report
print("\nDetailed Report:")
print(classification_report(y_val, preds, target_names=['Chola','Pallava']))
print(f"{'='*50}\n")

model.save('silailens_model.keras')
print("Saved: silailens_model.keras ✓")