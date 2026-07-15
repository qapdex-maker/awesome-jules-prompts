## 2023-07-06 - Image optimization in documentation-only repos

**Learning:** In repositories that are primarily documentation (like awesome lists), performance optimizations are centered around asset delivery (images) and Web Vitals (LCP, CLS).
**Action:** Use `width` and `height` attributes to prevent layout shifts, and consider stripping metadata/recompressing images if tools are available.

## 2026-07-08 - Responsive images for documentation

**Learning:** Serving a single 2x resolution image to all users is inefficient. Using `<picture>` with `srcset` allows serving optimized 1x assets and modern formats like AVIF, significantly reducing LCP payload for the majority of users.
**Action:** Implement responsive image logic (`<picture>`, `srcset`, AVIF/WebP) for prominent documentation assets.

## 2025-05-15 - Precision in asset dimensions

**Learning:** Even a 1px discrepancy in image height attributes (e.g., 253 vs 252) can trigger sub-pixel layout shifts and inefficient browser painting, especially on high-DPI displays where these values are scaled.
**Action:** Always verify actual asset dimensions (using `file` or `identify`) before setting `width` and `height` in Markdown/HTML to ensure zero CLS.

## 2026-07-11 - Proportional precision in responsive assets

**Learning:** When using `srcset` for high-DPI displays (2x, 3x), non-proportional dimensions (e.g., 600x252 vs 1200x505) can cause sub-pixel rendering artifacts and inefficient browser painting during scaling.

**Action:** Ensure high-resolution assets are exact multiples of the base 1x dimensions (e.g., exactly 2:1 ratio) to guarantee pixel-perfect scaling and zero layout shift across all resolutions.

## 2025-07-13 - AVIF re-compression for documentation assets

**Learning:** Re-compressing existing AVIF assets using `sharp-cli` with optimized settings (`-q 30 --effort 6`) can yield significant payload reductions (~27-37%) without visible quality loss, further improving LCP for modern browsers.

**Action:** Periodically audit and re-compress documentation image assets to ensure minimal delivery weight.

## 2025-07-14 - WebP and aggressive AVIF re-compression

**Learning:** Documentation assets can often tolerate more aggressive compression than standard web assets. Re-compressing already-optimized AVIF assets at `-q 20` and WebP assets at `-q 50` with `--effort 6` achieved an additional ~15-20% payload reduction without visible degradation in the context of documentation headers.

**Action:** Use aggressive quality settings (`-q 20` for AVIF, `-q 50` for WebP) with maximum effort for static documentation assets to minimize LCP.

---
