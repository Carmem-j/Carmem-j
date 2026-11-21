# AGENTS.md — Carmem Ferreira Portfolio

> Machine-readable project rules for LLMs and AI agents.
> Priority order: WCAG 2.1 > i18n correctness > design tokens in styles.css > everything else.

---

## STACK

```
CSS           : styles.css (plain CSS, design tokens in :root) — NO Tailwind, NO build, NO PostCSS
HTMX          : 1.9.12 CDN — partial HTML loading
Fonts         : Google Fonts — Outfit (300/400/500/600/700)
JS            : Vanilla ES6 — no frameworks
i18n          : translations.json + data-i18n attributes + runtime JS injection
Persistence   : localStorage (language), sessionStorage (scroll-after-reload)
```

Design: dark violet-charcoal theme + geometric shape vocabulary (circle, square, triangle, flower, moon). Each case has a color (`data-c="mint|pink|orange|cyan"`).

---

## CRITICAL CONSTRAINTS

1. **NEVER use `@apply` or Tailwind classes** — Tailwind was removed. All styling lives in `styles.css`.
2. **NEVER add `style="..."` inline attributes** — add a class in `styles.css` instead (colors: `.c-mint`, `.c-pink`, `.c-orange`, `.c-cyan`, `.c-violet`; case color via `data-c`; next-case color via `data-nc`).
3. **Use the design tokens** in `:root` of `styles.css` (`--bg`, `--surface`, `--line`, `--fg`, `--muted`, `--mint`, `--pink`, `--orange`, `--cyan`, `--violet`, `--ink`). Never hardcode new hex colors in markup.
4. **Shapes and icons** are SVG symbols in the sprite at the top of `index.html` (`#sh-circle`, `#sh-square`, `#sh-tri`, `#sh-moon`, `#sh-flower`, `#i-arrow`, `#i-info`, `#i-download`, `#i-copy`). Use `<svg aria-hidden="true"><use href="#id" /></svg>` and give every svg a size in CSS (an unsized svg renders 300x150).
5. **Contrast**: every text/background pair must pass 4.5:1. Magenta and deep violet are decorative only, never text.

---

## FILE ARCHITECTURE

```
index.html              Shell: head/SEO, SVG sprite, JS functions, HTMX loaders, lightbox
styles.css              All CSS: tokens, layout, components, case pages, responsive
translations.json       All i18n strings keyed by language then key
components/
  header.html           Sticky nav + PT/EN switch + mobile hamburger menu — always in DOM, NOT inside #app
  hero.html             Section id="top"
  impact.html           Sectors chips + 4 stats
  projects.html         Section id="projetos" — 4 case cards (order: case-4, case-3, case-2, case-1)
  about.html            Section id="sobre"
  case-1.html           Case study page (Data Navigation), replaces #app via HTMX
  case-2.html           Case study page (No-Code ROI), replaces #app via HTMX
  case-3.html           Case study page (Systemic UX, healthcare), replaces #app via HTMX
  case-4.html           Case study page (menu accessibility diagnosis), replaces #app via HTMX
  footer.html           Section id="contato" (CTA, e-mail, resume) + footer — always in DOM, NOT inside #app
images/                 avatar.png (hero), avatar-96.png (logo), profile.jpg (about), og-image.jpg (social thumbnail), case images
files/                  Resume PDFs (pt/eng)
```

### Case page template

Each `case-N.html` is a `<main id="main-content">` with: back link, kicker + h1 + lead, `.case-art` (same SVG as the card), `.case-meta` (4 items), `.disclaimer` (aligned to the right via `margin-left:auto`), `.case-body` (sticky `.toc` filled by `buildToc()` from each `section.cs > h2` + `.case-content` sections), `.next` link to the next case (order 4 → 3 → 2 → 1 → 4) and `.case-cta`.

---

## DOM LAYOUT (index.html body)

```html
<a class="skip" href="#main-content">...</a>
<!-- WCAG skip nav -->

<!-- header: always visible, outside #app -->
<div
  hx-get="components/header.html"
  hx-trigger="load"
  hx-swap="outerHTML"
></div>

<!-- #app: replaced by a case page (which brings its own <main id="main-content">) -->
<div id="app">
  <main id="main-content">
    <!-- hero, impact, projects and about loaded here -->
  </main>
</div>

<!-- footer: always visible, outside #app -->
<div
  hx-get="components/footer.html"
  hx-trigger="load"
  hx-swap="outerHTML"
></div>
```

**Rule:** `header.html` and `footer.html` are NEVER inside `#app`. All other sections are inside `#app`.

---

## NAVIGATION ARCHITECTURE

### Home view (default)

- All sections scroll in one page: `#top` (hero) → `#projetos` → `#sobre` → `#contato`
- Anchor links work directly via `href="#id"` or `navigateTo('id')`

### Case view (case-1 to case-4)

- Triggered by buttons in `projects.html` with `hx-target="#app" hx-swap="innerHTML"`
- Replaces entire `#app` content — hero, impact, projects, and about disappear
- Footer (`#contato`) and header remain visible at all times

### navigateTo(id) function

```js
function navigateTo(id) {
  const el = document.getElementById(id);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' }); // on home view
  } else {
    sessionStorage.setItem('scrollAfterLoad', id);
    window.location.reload(); // on case view — reload then scroll
  }
}
```

- Used by header nav links for `#sobre` and `#projetos`
- After reload, `initI18n()` reads `sessionStorage` and scrolls after 400ms delay (waits for HTMX components)

### Back from case

```html
<a href="/#projetos" onclick="navigateTo('projetos'); return false;" ...>Todos os projetos</a>
```

- `navigateTo('projetos')` stores the target in `sessionStorage` and reloads home, which then scrolls to the projects section

---

## I18N SYSTEM

### translations.json structure

```json
{
  "pt": { "key": "value in Portuguese" },
  "en": { "key": "value in English" }
}
```

### Markup pattern

```html
<element data-i18n="key"></element>
```

- The HTML carries the Portuguese text as default content (filled by `python tools/sync-pt.py` from `translations.json`); JS replaces it at runtime via `innerHTML` for the active language. `translations.json` is the source of truth: never edit the PT text only in the HTML
- Use `innerHTML` (not `textContent`) to support HTML tags in translation values (blockquotes, `<strong>`, etc.)

### JS runtime

```js
let currentLang = localStorage.getItem('preferredLang') || 'pt';

function translatePage() {
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    const key = el.getAttribute('data-i18n');
    if (translations[currentLang][key]) {
      el.innerHTML = translations[currentLang][key];
    }
  });
  document.documentElement.lang = currentLang === 'pt' ? 'pt-BR' : 'en';
}
```

### Language persistence

- Saved to `localStorage` key `preferredLang`
- Default: `'pt'`

### Adding a new translation key

1. Add to BOTH `pt` and `en` objects in `translations.json`
2. Add `data-i18n="new-key"` attribute to the HTML element
3. Leave the element empty and run `python tools/sync-pt.py` to write the PT text into the HTML: `<span data-i18n="new-key"></span>`

### Re-translation after HTMX load

```js
document.body.addEventListener('htmx:afterOnLoad', () => {
  translatePage();
  updateLanguageButtons();
  window.scrollTo(0, 0);
});
```

**Always call `translatePage()` after any HTMX swap.**

---

## HTMX PATTERNS

### Loading a component on page init

```html
<div
  hx-get="components/filename.html"
  hx-trigger="load"
  hx-swap="outerHTML"
></div>
```

### Replacing a section with case content

```html
<button hx-get="components/case-1.html" hx-target="#app" hx-swap="innerHTML">
  ...
</button>
```

### Rules

- Use `hx-swap="outerHTML"` when the placeholder `<div>` should be fully replaced
- Use `hx-swap="innerHTML"` when the target container should keep its element but have its content replaced
- Always add `translatePage()` in `htmx:afterOnLoad` — loaded fragments will have empty `data-i18n` elements

---

## ACCESSIBILITY (WCAG 2.1)

### Skip navigation

```html
<a href="#main-content" class="skip">Pular para o conteúdo principal</a>
```

CSS (`.skip`): visually hidden by default, revealed on `:focus`.

### Semantic HTML

- Use `<header>`, `<main>`, `<nav>`, `<footer>`, `<article>`, `<section>` appropriately
- `<nav>` must have `aria-label`
- Use `<h1>` through `<h3>` in correct hierarchy — never skip heading levels

### Interactive elements

- All `<a>` links must have accessible text via content, `data-i18n`, or `title` attribute
- All `<button>` elements must have accessible text via content, `data-i18n`, or `title` attribute
- `<img>` elements must have descriptive `alt` text — never `alt=""` unless decorative
- Case images use `<figure>` + `<figcaption data-i18n="...">`. Their alt text is translated via `data-i18n-alt="key"` (handled in `translatePage()`); the markup carries the Portuguese `alt` text directly (so it exists without JS) and JS swaps it for the active language; both `pt` and `en` must define the key. Always set `width`, `height` and `loading="lazy"`.
- Empty `data-i18n` elements that are links/buttons MUST have a `title` attribute as fallback

### Language

- `<html lang="...">` must match `currentLang`: `pt-BR` or `en`
- Updated in `translatePage()` on every language switch

- `aria-label` values are translated with `data-i18n-label="key"` (handled in `translatePage()`); never hardcode a single language in `aria-label`, skip link or dialog label
- `document.title` follows language and case (`updateDocumentTitle()`, key `page-title`)
- After a case loads via HTMX the focus moves to the case `<h1>` (`tabindex="-1"`); do not let focus fall back to `<body>`
- The hero ring animation (60s, infinite) has a visible pause/resume button (`#anim-toggle`, keys `anim-pause`/`anim-resume`, preference in `localStorage` key `animPaused`, class `anim-paused` on `<html>`); any new autoplay animation longer than 5s must be covered by it
- JS scrolling must use `scrollBehavior()` (respects `prefers-reduced-motion`); 
- Links with the same visible text (e.g. "Ler case completo") need `aria-describedby` pointing to the card heading; links with `target="_blank"` include a `sr-only` "opens in a new tab" notice (`new-tab` key)
- Decorative shapes must not sit behind text: confetti is masked away from text on mobile

### Color contrast

- Body text `--fg` and secondary `--muted` on `--bg`/`--surface` pass AA; dark text `--ink` on mint buttons
- Never use color alone to convey information

### Focus management

- Do not remove outlines (global `:focus-visible` ring in `styles.css`)
- After HTMX content loads into a case page, `window.scrollTo(0,0)` resets viewport
- Lightbox returns focus to the opener on close

---

## CSS RULES

- All CSS lives in `styles.css`. Plain CSS, mobile breakpoints at `960px` and `640px`.
- Do not add `@apply`, Tailwind classes or `style=""`. Add or reuse a class in `styles.css`.
- Respect `prefers-reduced-motion` (already handled globally at the end of `styles.css`).
- Visible focus: global `:focus-visible` ring (mint, 3px). Never remove outlines.

---

## COMPONENT PATTERNS

### Nav link (home anchor)

```html
<a href="#sobre" onclick="navigateTo('sobre'); return false;" title="Sobre" data-i18n="nav-about"></a>
```

### Mobile menu (header.html)

`#mobile-menu-toggle` (`.burger`, visible at <= 640px) toggles `#mobile-menu` (`hidden` attribute). `aria-expanded` and `aria-label` are synced by `syncMenuToggle()` using keys `menu-open` / `menu-close`. Esc, outside click, link click and resizing above 640px close it.

### Case open button (projects.html)

```html
<button type="button" class="more" title="case-1" hx-get="components/case-1.html" hx-target="#app" hx-swap="innerHTML" hx-push-url="#case-1">
  <span data-i18n="case1-btn"></span>
  <svg aria-hidden="true"><use href="#i-arrow" /></svg>
</button>
```

The whole card is clickable (`.more::after` covers the card).

### Case image with lightbox

```html
<figure class="shot">
  <button type="button" class="zoom" data-lightbox>
    <img src="images/x.png" alt="" data-i18n-alt="key-alt" width="W" height="H" loading="lazy" decoding="async" />
    <span class="zi" aria-hidden="true"><!-- zoom svg --></span>
    <span class="sr-only" data-i18n="lightbox-open"></span>
  </button>
  <figcaption data-i18n="key-caption"></figcaption>
</figure>
```

Use `class="shot narrow"` for tall/small screenshots. Metrics use `<div class="res"><div><b>value</b><small>label</small><span>description</span></div></div>`.

---

## TRANSLATION KEY GROUPS

| Prefix / key                                    | Purpose                                             |
| ----------------------------------------------- | --------------------------------------------------- |
| `nav-*`, `menu-open`, `menu-close`              | Header and mobile menu                              |
| `hero-*`, `btn-projects`                        | Hero (title and desc contain HTML: `.hl`, `strong`) |
| `impact-eyebrow`, `sector-*`, `stat-1..4`       | Impact strip                                        |
| `projects-*`, `caseN-tag/title/desc/btn/chip*`  | Project cards                                       |
| `about-*`, `skill-*`, `edu-*`                   | About section                                       |
| `contact-eyebrow`, `cta-title`, `copy-*`, `footer-*` | Contact and footer                             |
| `btn-back`, `case-toc`, `case-next`, `case-cta-*`    | Case page chrome                               |
| `meta-*`, `caseN-year/duration/team/focus`      | Case metadata                                       |
| `caseN-*`                                       | Case body content, images (`-img-*-alt/caption`), `-disclaimer-*` |
| `lightbox-open`, `lightbox-close`               | Lightbox labels                                     |

---

## CHECKLIST — Before submitting any change

- [ ] No `@apply` or Tailwind classes
- [ ] No `style=""` inline attributes
- [ ] Every `<img>` has a descriptive `alt`
- [ ] Every interactive empty element has `title` or `data-i18n` that resolves to text
- [ ] New text content has keys in BOTH `pt` and `en` in `translations.json`
- [ ] New HTML elements with text use `data-i18n`; run `python tools/sync-pt.py` after editing `translations.json` (it also fills `alt`, `aria-label` and the case TOC)
- [ ] Any new HTMX-loaded content will trigger `translatePage()` via `htmx:afterOnLoad`
- [ ] Sections that must always be visible (header, footer) are NOT inside `#app`
- [ ] Case content buttons target `#app` with `hx-swap="innerHTML"`
- [ ] Every svg has a size in CSS; colors come from tokens in `styles.css`
- [ ] `navigateTo()` used for header nav links that may not exist in case view
