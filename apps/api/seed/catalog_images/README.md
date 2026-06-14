# Catalog reference images (delivery-time "birth certificate")

Drop a real photo of each demo SKU here to activate **real, zero-cost fingerprint
matching** for that SKU:

```
seed/catalog_images/SKU-HP-01.jpg
seed/catalog_images/SKU-SH-01.jpg
seed/catalog_images/SKU-AP-01.jpg
```

When present, the verify step embeds this image (local CLIP-style perceptual
embedding, `services/embeddings.py`) and compares it against the embedding of the
live scan frame. Same unit → high cosine similarity; swapped unit → lower.

If no image is here, the fingerprint falls back to the seeded deterministic
vectors, so the offline demo still works unchanged.

These represent the photo the courier captures at delivery in production.
