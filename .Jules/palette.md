## 2025-05-15 - [README Navigation & Visual Cues]

**Learning:** In long documentation files, providing visual cues like emojis and quick navigation links ("Back to top") significantly improves scannability and user experience.
**Action:** Always consider adding a Table of Contents with quick return links for READMEs exceeding a few screen heights.

## 2025-07-07 - [Consistent Sectional Navigation]

**Learning:** For long lists of items (like prompts), adding 'Back to top' links to *every* major section ensures users never feel 'lost' or have to scroll excessively to return to the navigation hub.
**Action:** Implement 'Back to top' links at the end of every markdown section that contains more than 5 lines of content.

## 2026-07-08 - [Prompt Placeholder Clarity & Sectional separation]

**Learning:** Users benefit from explicit instructions on how to use placeholder syntax ({placeholder}) in prompt libraries. Additionally, adding horizontal separators before navigation links creates a clearer mental model of where one section ends and another begins.
**Action:** Always include a 'How to Use' tip in prompt collections and use visual dividers (---) to separate content blocks from boilerplate navigation links.

## 2026-07-08 - [Unified Documentation Navigation & Disambiguation]

**Learning:** Providing clear navigation paths between disparate documentation files (e.g., Back to README links) reduces user friction. Additionally, explicitly linking to specific policies from similar-sounding content sections (like linking the Security Policy from a list of Security prompts) helps users find the right information quickly.
**Action:** Implement bidirectional navigation between sub-docs and the main README, and add disambiguation links in sections that might be confused with official repository policies.

## 2026-07-09 - [Accessible External Links & Heading Consistency]

**Learning:** External links that open in new tabs require `aria-label` to inform screen reader users of the context switch. Furthermore, matching emojis between README navigation and sub-doc headings provides a strong visual "handshake" that confirms the user has reached the correct destination.
**Action:** Use `aria-label="... (opens in a new tab)"` for all `target="_blank"` links and ensure sub-document headings mirror the visual style (emojis) of their parent links in README.md.
