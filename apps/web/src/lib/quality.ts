// Client-side capture quality gate (Section 2 Step 2 / Section 3.1).
// Cheap, real, on-device heuristics that feel magically responsive:
//   - blur via Laplacian variance (low variance = blurry)
//   - brightness via mean luma (too dark / blown out)
//   - fill via center-vs-edge contrast proxy (object should fill the frame)
// These run on a downscaled canvas every frame, so they're fast.

export type QualityReport = {
  blurVariance: number;
  brightness: number;
  fill: number;
  ok: boolean;
  reason?: string;
};

// thresholds tuned for laptop/phone webcams; conservative so the demo flows
const BLUR_MIN = 8; // Laplacian variance floor
const BRIGHT_MIN = 35;
const BRIGHT_MAX = 245;
const FILL_MIN = 0.04;

export function assessFrame(video: HTMLVideoElement, work: HTMLCanvasElement): QualityReport {
  const w = 160;
  const h = Math.round((video.videoHeight / video.videoWidth) * w) || 120;
  work.width = w;
  work.height = h;
  const ctx = work.getContext("2d", { willReadFrequently: true })!;
  ctx.drawImage(video, 0, 0, w, h);
  const { data } = ctx.getImageData(0, 0, w, h);

  // grayscale + brightness
  const gray = new Float32Array(w * h);
  let sum = 0;
  for (let i = 0; i < w * h; i++) {
    const r = data[i * 4],
      g = data[i * 4 + 1],
      b = data[i * 4 + 2];
    const y = 0.299 * r + 0.587 * g + 0.114 * b;
    gray[i] = y;
    sum += y;
  }
  const brightness = sum / (w * h);

  // Laplacian variance (4-neighbour kernel)
  let lapSum = 0,
    lapSqSum = 0,
    n = 0;
  for (let y = 1; y < h - 1; y++) {
    for (let x = 1; x < w - 1; x++) {
      const i = y * w + x;
      const lap =
        4 * gray[i] - gray[i - 1] - gray[i + 1] - gray[i - w] - gray[i + w];
      lapSum += lap;
      lapSqSum += lap * lap;
      n++;
    }
  }
  const mean = lapSum / n;
  const blurVariance = lapSqSum / n - mean * mean;

  // fill proxy: how much the center region differs from the border (an object
  // filling the frame raises center detail/contrast vs a far-away object)
  let centerVar = 0,
    cN = 0;
  const cx0 = Math.floor(w * 0.3),
    cx1 = Math.floor(w * 0.7),
    cy0 = Math.floor(h * 0.3),
    cy1 = Math.floor(h * 0.7);
  let cMean = 0;
  for (let y = cy0; y < cy1; y++)
    for (let x = cx0; x < cx1; x++) cMean += gray[y * w + x];
  cMean /= (cx1 - cx0) * (cy1 - cy0);
  for (let y = cy0; y < cy1; y++) {
    for (let x = cx0; x < cx1; x++) {
      const d = gray[y * w + x] - cMean;
      centerVar += d * d;
      cN++;
    }
  }
  const fill = Math.min(1, Math.sqrt(centerVar / cN) / 64);

  let reason: string | undefined;
  if (brightness < BRIGHT_MIN) reason = "Too dark — find better light";
  else if (brightness > BRIGHT_MAX) reason = "Too bright — reduce glare";
  else if (blurVariance < BLUR_MIN) reason = "Hold steady — image is blurry";
  else if (fill < FILL_MIN) reason = "Move closer — fill the frame";

  return {
    blurVariance: Math.round(blurVariance * 10) / 10,
    brightness: Math.round(brightness),
    fill: Math.round(fill * 100) / 100,
    ok: !reason,
    reason,
  };
}

export function captureBlob(video: HTMLVideoElement, canvas: HTMLCanvasElement): Promise<Blob> {
  const w = Math.min(720, video.videoWidth || 720);
  const h = Math.round((video.videoHeight / video.videoWidth) * w) || 540;
  canvas.width = w;
  canvas.height = h;
  canvas.getContext("2d")!.drawImage(video, 0, 0, w, h);
  return new Promise((resolve) =>
    canvas.toBlob((b) => resolve(b!), "image/jpeg", 0.85)
  );
}
