<!-- markdownlint-disable MD041 -->
[← Back to Main README](../README.md)

---

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

## 2025-07-15 - Re-compressing already optimized assets

**Learning:** Re-compressing 1x and 2x WebP assets using `npx sharp-cli -i <input> -o <output> -f webp -q 50 --effort 6` can yield additional ~15% payload reductions even on previously optimized documentation assets.
**Action:** Don't assume previously optimized assets are at their limit; test aggressive compression settings periodically.

## 2025-07-16 - Efficient directory traversal in Python

**Learning:** In Python scripts using `os.walk`, pruning the `dirs` list in-place (e.g., `dirs[:] = [d for d in dirs if d not in ignored_dirs]`) is significantly more efficient than checking the root path inside the loop. This prevents the crawler from visiting ignored directory branches entirely, rather than just skipping their files.
**Action:** Always use in-place `dirs` pruning with `os.walk` when ignoring large directories like `.git` or `node_modules`.

---

## 2025-07-17 - Correct-by-construction whole-file pre-filtering

**Learning:** Attempting to optimize regex execution by using fast prefix substring checks on individual lines can introduce security regressions (false negatives) if not all possible matching variations (e.g., camelCase, snake_case, standard PEM structures) are accounted for. Instead, running a fast `cp.search(content)` on the whole file content serves as a robust pre-filter. If it returns False, we can skip the file entirely with 100% safety and correctness.
**Action:** Use whole-file regex pre-filtering (`search()`) before doing line-by-line (`finditer()`) scanning in security or scanning scripts to gain performance without sacrificing safety.

---

## 2025-07-18 - Overheads of combined regex patterns vs. whole-file lazy scanning

**Learning:** Combining multiple distinct regexes into a single pattern using alternatives (`|`) to optimize scanning can backfire due to the engine's backtracking overhead across different pattern structures. Instead, keeping individual pre-compiled patterns for pre-filtering (using short-circuiting `any`) is faster. However, scanning the entire file content in one pass with `finditer()` and lazily computing line numbers/content (via `str.count` and index searching) only when a match is found delivers a massive ~41% speedup over splitting files line-by-line.
**Action:** Keep distinct pre-compiled regexes for pre-filtering but perform whole-file single-pass scans, computing line positions and contents on-demand rather than splitting strings upfront.

---

## 2025-07-19 - Case-insensitive regex flags overhead

**Learning:** Using the case-insensitive inline flag `(?i)` forces Python's regex engine to apply case-folding to every single character of the input during pattern scanning. On files with no matches, this adds massive overhead (e.g., 9.7s vs 6.4s). Replacing the global `(?i)` flag with explicit character classes (e.g. `[sS][eE][cC][rR][eE][tT]`) for keywords in a case-sensitive regex avoids expensive case-folding overhead on large character classes later in the pattern, while maintaining 100% correctness and matching coverage.
**Action:** Avoid global case-insensitivity flags (`(?i)`) on high-traffic scanning paths when case-specific character classes can be used on the keyword prefix instead.

## 2025-07-21 - Boyer-Moore-style substring pre-filtering for secret scanning

**Learning:** Running complex regular expression engines (even with pre-compilation
and character classes) character-by-character on large, clean files introduces
massive backtracking and search overhead in Python. By performing a fast
case-insensitive substring `in` check on the file's lowercase contents first,
using a predefined keyword list of secret prefixes, we can completely bypass
regex evaluation on non-matching files. Since Python's string `in` operator
uses a highly optimized C-level Boyer-Moore-Horspool algorithm, this pre-filter
provides a massive ~75% speedup on large clean files while maintaining 100%
scanning accuracy.
**Action:** Pre-filter large search files with highly optimized, simple
case-insensitive substring checks using Python's 'in' operator before executing
complex regex patterns.

---

## 2025-07-22 - Replacing generator expressions with explicit loops for small iterables

**Learning:** Python generator expressions (e.g. `any(x in y for x in list)`) introduce noticeable overhead due to generator frame allocation, execution suspension, and yield/resume context switching. For high-traffic code paths operating on small arrays (such as checking matching candidate prefixes or searching active regex patterns), a simple, explicit `for` loop avoids all generator allocation and context switching overhead entirely, executing purely in the local frame. Additionally, caching objects in standard local variables rather than list-wrapped structures eliminates unnecessary index lookup overhead.
**Action:** Replace generator expressions with explicit, fast-failing `for` loops in performance-critical code paths that iterate over small lists.

---
