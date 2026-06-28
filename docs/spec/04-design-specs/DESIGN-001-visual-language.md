# Design Spec: DESIGN-001 Visual Language

## Metadata

- Design spec ID: `DESIGN-001`
- Status: accepted
- Related feature specs: `8-1` through `8-7` (Web UI), `10-1` (Onboarding Wizard)
- Related requirements: FR-14 through FR-20 (Web UI), FR-24 (Onboarding)
- Related ADRs: Architecture decision — FastAPI + HTMX + Jinja2 + Pico.css, light mode default

---

## Context

Lede produces editorial output — a dated, journalism-grade briefing synthesized from newsletters. The UI should reflect that identity. A tool that outputs something with the care of a byline should feel like it belongs in the same world as the content it creates.

This spec defines Lede's visual language: color system, typography, elevation, spacing, component conventions, and dark/light mode behavior. All Epic 8 and Epic 10 stories reference this document when making visual decisions. Pico.css provides the CSS reset and base component primitives; this spec overrides and extends it via CSS custom properties.

**Design lineage:** The system is synthesized from lessons across five reference design systems — Claude/Anthropic (editorial warmth, parchment palette, serif/sans split), Notion (warm neutrals, whisper borders, multi-layer micro-shadows), Linear (luminance-step elevation, dark-mode discipline), Stripe (letter-spacing rhythm, shadow philosophy), and Mintlify (reading-optimized hierarchy, sparse accent use). No single template is adopted wholesale.

**Design rubric:** All components are evaluated against the seven-rule UI Design Rubric (see `~/.claude/skills/ui-design-rubric/SKILL.md`): surface levels, 8pt grid, borders vs shadows, typeface zones, accent restraint, semantic color use, and touch target minimums.

---

## Personality

Lede is a **local editorial tool for builders and PMs**. The visual language should feel like:

- A well-designed newsroom dashboard — precise, readable, purposeful
- A tool that respects the content it produces — not a dev-tool grid, not a SaaS marketing page
- Calm and confident — warm not cold, never aggressive

It should **not** feel like: a generic dark-mode app, a Notion clone, a fintech dashboard.

---

## Screen Architecture

The UI has three screens (not four). Dashboard and Briefing are collapsed into one — the briefing displays inline on the dashboard. This follows the "Don't Make Me Think" principle: fewer destinations, less navigation overhead.

| Screen | Purpose |
|---|---|
| Dashboard | Feed selector, run status, today's briefing inline |
| Archive | Past briefings — browse, read, download, retry |
| Settings | Feed configurations, AI provider, schedule, troubleshooting (pipeline log) |

**Empty state:** Dashboard shows an empty state with a single "Run your first briefing" CTA when no briefings exist yet.

---

## Feed Concept

A **feed** is a named inbox pull configuration: a Gmail label, a schedule, and a lookback window. Users can have multiple feeds (e.g. "Newsletters" pulling daily, "Job Leads" pulling every Wednesday). The feed selector on Dashboard and Archive is a dropdown — not tabs — so it scales beyond 2–3 feeds without breaking the layout.

Feed settings live in Settings → Feeds as an add/remove list (+ / − controls). Free-text inputs that could break the backend are normalized to dropdowns: lookback window (12h, 24h, 48h, 7d, 14d, 30d), schedule (predefined list), timezone (US only in V1).

---

## Color System

### Philosophy

Every neutral carries a warm undertone. There are no cool blue-grays anywhere in the system. The dark and light modes share the same warm bias — they are not independent palettes but inversions of the same tone family. The single accent color is used only for the highest-signal moments.

### Accent

| Name | Value | Role |
|---|---|---|
| Terracotta | `#c96442` | Primary CTA, active nav state, audio play button |
| Terracotta Hover | `#b5572f` | Hover/pressed state on terracotta elements |
| Terracotta Muted | `rgba(201,100,66,0.10)` | Badge backgrounds, tinted surfaces |

Terracotta is the **only chromatic color** in the UI chrome. It appears on: the primary Run button, active nav item, and audio play button. Nowhere else.

### Light Mode (default)

| Token | Value | Role |
|---|---|---|
| `--bg-canvas` | `#f5f4ed` | Page background (warm parchment) |
| `--bg-surface` | `#faf9f5` | Sidebar, persistent bars, cards, panels — all Level-1 surfaces |
| `--bg-overlay` | `#ffffff` | Dropdowns, modals only |
| `--bg-subtle` | `#eceae0` | Alternating section backgrounds, hover states |
| `--text-primary` | `#141413` | Headings, body copy |
| `--text-secondary` | `#5e5d59` | Descriptions, secondary labels |
| `--text-muted` | `#87867f` | Timestamps, metadata, placeholders |
| `--text-disabled` | `#b0aea5` | Disabled states |
| `--border-subtle` | `rgba(0,0,0,0.07)` | Default borders — cards, dividers |
| `--border-standard` | `rgba(0,0,0,0.13)` | Input borders, prominent separators |
| `--shadow-sm` | `rgba(0,0,0,0.04) 0px 1px 3px, rgba(0,0,0,0.03) 0px 4px 12px` | Subtle card lift |
| `--shadow-md` | `rgba(0,0,0,0.04) 0px 4px 18px, rgba(0,0,0,0.027) 0px 2px 7.8px, rgba(0,0,0,0.02) 0px 0.8px 2.9px` | Content cards, panels, dropdowns |

### Dark Mode

| Token | Value | Role |
|---|---|---|
| `--bg-canvas` | `#141413` | Page background (warm near-black) |
| `--bg-surface` | `#1e1d1b` | Sidebar, persistent bars, cards, panels |
| `--bg-overlay` | `#2a2926` | Dropdowns, modals |
| `--bg-subtle` | `#242320` | Alternating section backgrounds |
| `--text-primary` | `#f5f4ed` | Headings, body copy (warm near-white, not pure white) |
| `--text-secondary` | `#b0aea5` | Descriptions, secondary labels |
| `--text-muted` | `#87867f` | Timestamps, metadata, placeholders |
| `--text-disabled` | `#5e5d59` | Disabled states |
| `--border-subtle` | `rgba(255,255,255,0.06)` | Default borders |
| `--border-standard` | `rgba(255,255,255,0.10)` | Input borders, prominent separators |
| `--shadow-sm` | `rgba(0,0,0,0.2) 0px 1px 3px, rgba(0,0,0,0.15) 0px 4px 12px` | Subtle card lift |
| `--shadow-md` | `rgba(0,0,0,0.3) 0px 4px 18px, rgba(0,0,0,0.2) 0px 2px 7.8px, rgba(0,0,0,0.12) 0px 0.8px 2.9px` | Content cards, panels |

### Status Colors (both modes)

| Name | Value | Role |
|---|---|---|
| Success Green | `#2a9d5c` | Completed run, QA passed |
| Warning Amber | `#c47d0e` | Hold state, retry warning |
| Error Red | `#b53333` | Failed stage, QA rejected |
| Info (Live) | `#c96442` (terracotta) | Pipeline running — reuse accent, do not introduce a fourth color |

---

## Typography

### Philosophy

Two typefaces, each with a distinct register. Serif for content identity (briefing titles, reading view, history headings) — these surfaces are editorial and should feel like they belong to the output. Sans for UI chrome (nav, settings, pipeline log, badges, buttons) — functional and precise.

### Typefaces

| Role | Typeface | Google Fonts link |
|---|---|---|
| Editorial / Headlines | Playfair Display | `family=Playfair+Display:wght@400;500;600` |
| UI / Body | Inter | `family=Inter:wght@300;400;500;600` |
| Code / Pipeline log | JetBrains Mono | `family=JetBrains+Mono:wght@400;500` |

**Font stack CSS:**
```css
--font-editorial: 'Playfair Display', Georgia, 'Times New Roman', serif;
--font-ui:        'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
--font-mono:      'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, monospace;
```

### Type Scale

| Role | Font | Size | Weight | Line Height | Letter Spacing | Usage |
|---|---|---|---|---|---|---|
| Display | Editorial | 48px | 500 | 1.10 | -1.0px | Briefing date header, onboarding headline |
| Heading 1 | Editorial | 32px | 500 | 1.20 | -0.5px | Briefing main headline (dashboard) |
| Heading 2 | Editorial | 21px | 500 | 1.25 | -0.3px | Section headings within briefing reading view |
| Heading 3 | UI | 18px | 600 | 1.30 | -0.2px | Settings section labels |
| Body Large | UI | 16px | 400 | 1.72 | normal | Briefing body copy (reading view) |
| Body | UI | 15px | 400 | 1.50 | normal | Standard UI text, card descriptions |
| Label | UI | 13px | 500 | 1.40 | normal | Nav links, form labels, button text, audio title |
| Caption | UI | 12px | 400 | 1.40 | normal | Timestamps, run metadata, source attribution |
| Badge | UI | 11px | 500 | 1.00 | 0.3px | Status badges |
| Code | Mono | 13px | 400 | 1.60 | normal | Pipeline log lines (Settings → Troubleshooting only) |

### Rules

- Playfair Display for **briefing content surfaces only**: dashboard briefing headline, section headings in reading view, archive card titles, and the "Lede" wordmark. Nowhere in nav items, settings, status bars, forms, or any interactive element.
- Inter carries all other text. Weight 400 for reading, 500 for navigation and labels, 600 for active/strong emphasis.
- No Inter at weight 700 — 600 is the ceiling.
- Positive letter-spacing (0.3px) only on badge text at 11px and below.

---

## Elevation & Depth

### Philosophy

Depth is communicated through **background luminance steps** and **border separation**, not through heavy drop shadows. Persistent UI chrome (sidebar, audio bar, status bar) all share `--bg-surface` — they are at the same elevation level and must use the same token. Only transient elements (dropdowns, modals) step up to `--bg-overlay`.

### Levels

| Level | Token | Usage | Separation |
|---|---|---|---|
| 0 — Canvas | `--bg-canvas` | Page background only | None |
| 1 — Surface | `--bg-surface` | Sidebar, audio bar, status bar, cards, panels | Border against canvas |
| 2 — Overlay | `--bg-overlay` | Dropdowns, modals, tooltips | Shadow-md, no border |
| 3 — Focus | `2px solid #c96442` outline | Keyboard focus on all interactive elements | — |

**Rule:** Two adjacent Level-1 elements must share `--bg-surface`. Never use `--bg-overlay` for a persistent element sitting next to another persistent element.

### Borders vs Shadows

- **Borders** express separation at the same elevation (sidebar right edge, status bar outline, section dividers)
- **Shadows** express lift above the canvas (cards, dropdowns)
- A persistent bar (audio, status, nav) uses `border` only — no `box-shadow`
- A card uses `shadow-sm` or `shadow-md` — no border
- A dropdown uses `shadow-md` only

---

## Spacing System

Base unit: **8px** (4px minimum step)

Scale: 4 · 8 · 12 · 16 · 24 · 32 · 40 · 48 · 64 · 80 · 96

```css
--space-1:  4px;
--space-2:  8px;
--space-3:  12px;
--space-4:  16px;
--space-6:  24px;
--space-8:  32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
--space-20: 80px;
```

**Component heights (all on 8pt grid):**
- 32px — small controls (badges, compact tags)
- 40px — medium controls (buttons, inputs)
- 48px — nav items, status bar, touch targets (WCAG minimum)
- 56px — audio bar, toolbars
- 220px — sidebar width

No CSS spacing value should use an off-grid number (14px, 18px, 20px, 22px, 28px, 46px). Exceptions: `border-radius`, `font-size`, `line-height`.

---

## Border Radius Scale

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | 4px | Badges, status indicators |
| `--radius-md` | 8px | Buttons, inputs, small cards, status bar |
| `--radius-lg` | 12px | Content cards, archive cards, dropdown menus |
| `--radius-xl` | 16px | Modal containers |

`--radius-md` (8px) is the workhorse. Never use `--radius-xl` on buttons.

---

## Component Conventions

### Sidebar Navigation

- Width: 220px, fixed left
- Background: `--bg-surface`
- Right edge: `1px solid --border-subtle` (separates from canvas)
- Wordmark: "Lede" in Playfair Display 18px weight 500 — only editorial type in nav
- Nav items: Inter 13px weight 500, `--text-secondary`, 40px min-height, 12px horizontal padding
- Active item: `--text-primary` + terracotta left border (2px) + `--bg-subtle` background
- Dark mode toggle: pinned to bottom of sidebar

### Feed Selector + Status Bar

These two elements stack vertically at the top of the main content area and travel together across Dashboard and Archive screens.

**Feed selector:**
- A labeled dropdown button (feed name + chevron) left-aligned, "Run now" button right-aligned
- Dropdown menu: `--bg-overlay`, `shadow-md`, `radius-lg`, opens below the button
- No stacking context (`position: relative` with no `z-index`) — dropdown uses `position: absolute; z-index: 200` within its wrapper only

**Status bar:**
- Sits below the feed selector, above the briefing content
- Background: `--bg-surface`, border: `1px solid --border-subtle`, radius: `--radius-md`
- Min-height: 48px
- Idle state: green "Up to date" badge + last run / next run text
- Running state: terracotta "Running" badge + progress pips + human-readable stage label + ETA
- No raw log output here — friendly language only ("Fetching your newsletters…", "Generating briefing…")

### Buttons

**Primary (Terracotta)**
- Background: `#c96442`, Text: `#faf9f5`, Radius: `--radius-md`, Padding: 10px 20px
- Font: Inter 14px weight 500, Hover: `#b5572f`
- Use: "Run now" — the single most important action

**Secondary**
- Background: `--bg-surface`, Border: `1px solid --border-standard`, Radius: `--radius-md`
- Use: Download, save, secondary actions

**Ghost**
- Background: transparent, Text: `--text-secondary`, Hover: `--text-primary`
- Use: Cancel, dismiss, icon actions

### Status Badges

Inter 11px weight 500, letter-spacing 0.3px, `--radius-sm`, padding 3px 8px.

| Status | Background | Text |
|---|---|---|
| Running | `rgba(201,100,66,0.12)` | `#c96442` |
| Complete | `rgba(42,157,92,0.12)` | `#2a9d5c` |
| Failed | `rgba(181,51,51,0.12)` | `#b53333` |
| Hold | `rgba(196,125,14,0.12)` | `#c47d0e` |
| Queued | `--bg-subtle` | `--text-muted` |

### Cards (Archive)

- Background: `--bg-surface`, Border: `1px solid --border-subtle`, Radius: `--radius-lg`, Shadow: `--shadow-sm`
- Internal padding: 24px
- Title: Playfair Display (heading 1 scale), Inter body, terracotta "Read" link
- Actions: Read / Download / Retry — ghost buttons right-aligned

### Inputs & Forms

- Background: `--bg-surface`, Border: `1px solid --border-standard`, Radius: `--radius-md`
- Padding: 10px 14px, Font: Inter 15px weight 400, Min-height: 40px
- Focus: border becomes `2px solid #c96442`, shadow `0 0 0 3px rgba(201,100,66,0.15)`
- Label: Inter 13px weight 500, `--text-secondary`, 8px below label
- **All inputs that accept structured values use dropdowns** — no free-text for schedule, timezone, lookback window

### Audio Bar

Docked at the bottom of the main content area. Visible once a briefing has audio available.

- Position: `fixed; bottom: 0; left: 220px; right: 0`
- Height: 56px (on 8pt grid)
- Background: `--bg-surface` (same as sidebar — Level-1 surface, Rule 1 compliant)
- Border: `border-top: 1px solid --border-subtle` only — no shadow (Rule 3)
- Contents left→right: briefing title (truncated) + feed name / duration · play/pause button (terracotta, 38px) · scrubber with progress dot · timestamp (mono) · download icon
- Play button uses accent color — one of its three permitted uses (Rule 5)
- Content area gets `padding-bottom: 64px` when audio bar is visible

### Pipeline Log

The raw pipeline log is **not shown on the Dashboard**. It lives exclusively in Settings → Troubleshooting. This keeps the main flow clean — users who want to debug can find it; users who don't aren't exposed to terminal output.

- Background: `--bg-canvas`
- Font: JetBrains Mono 13px weight 400
- Text: `--text-secondary` for standard lines, `--text-muted` for timestamps
- Error lines: `#b53333`, Success lines: `#2a9d5c`

---

## Mode Switching

- Default: **light mode**
- Toggle: bottom of sidebar, persisted to SQLite `user_preferences` or config file
- Implementation: `<html data-theme="light|dark">` with CSS custom properties redefined per `[data-theme]` selector
- No system preference detection in V1 — explicit user choice only

---

## Alternatives Considered

| Option | Pros | Cons | Decision |
|---|---|---|---|
| Linear design system (direct) | Dark-native, precise, well-specced | Inverts awkwardly to light mode; personality too cold for editorial content | Not adopted; luminance stepping concept borrowed |
| Notion design system (direct) | Warm neutrals, good light mode | No serif, no dark mode spec, personality too productivity-app | Not adopted; warm neutral palette and shadow philosophy borrowed |
| Claude/Anthropic design system (direct) | Perfect editorial warmth, parchment palette | Designed for marketing page, not local app | Not adopted; serif split, warm neutrals, and terracotta accent borrowed |
| Dark mode as default | Felt premium initially | Warm parchment palette reads better in light mode; editorial content benefits from high contrast | Reversed to light default |
| Tab switcher for feeds | Simple, visible | Breaks at 4+ feeds | Replaced with dropdown selector |
| Separate Briefing screen | Clearer hierarchy | Extra navigation step; briefing is the point of the app | Collapsed into Dashboard |
| Topics & Sections in Settings | User control | Content grouping is automatic (Gmail label determines it) | Removed |
| Inline play button in briefing byline | Discoverable | Conflicts with docked audio bar; redundant | Removed; audio bar is the only entry point |

---

## Impacted Files

- `app/static/css/theme.css` — CSS custom property definitions for both modes
- `app/templates/base.html` — Google Fonts `<link>` tags, `data-theme` attribute, sidebar structure
- `app/templates/components/` — badge, card, button, input, status-bar, audio-bar partials
- `app/templates/dashboard.html` — feed selector, status bar, briefing reading view
- `app/templates/archive.html` — briefing cards with Playfair Display headings
- `app/templates/settings/` — feeds panel, schedule, AI provider, troubleshooting (pipeline log)

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Playfair Display CDN unavailable in offline use | Medium | Low — Georgia fallback is acceptable | Georgia fallback specified in font stack |
| Pico.css base styles conflict with custom tokens | Medium | Medium | Scope all custom properties under `[data-theme]` selector; override Pico variables directly |
| Warm dark mode feels muddy on low-quality displays | Low | Low | `#141413` is dark enough to maintain contrast ratios |
| Two-typeface system misapplied | Medium | Medium | Strictly enforce: Playfair Display only on briefing content surfaces, never in UI chrome |
| Feed dropdown z-index conflicts | Low | Low | Never add `z-index` to `.feed-bar` container — only the dropdown menu itself carries z-index |
