## 2023-07-06 - Image optimization in documentation-only repos
**Learning:** In repositories that are primarily documentation (like awesome lists), performance optimizations are centered around asset delivery (images) and Web Vitals (LCP, CLS).
**Action:** Use `width` and `height` attributes to prevent layout shifts, and consider stripping metadata/recompressing images if tools are available.

## 2026-07-08 - Responsive images for documentation
**Learning:** Serving a single 2x resolution image to all users is inefficient. Using `<picture>` with `srcset` allows serving optimized 1x assets and modern formats like AVIF, significantly reducing LCP payload for the majority of users.
**Action:** Implement responsive image logic (`<picture>`, `srcset`, AVIF/WebP) for prominent documentation assets.
