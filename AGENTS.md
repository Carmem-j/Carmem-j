# AGENTS.md — Carmem Ferreira Portfolio

> Machine-readable project rules for LLMs and AI agents.
> Priority order: WCAG 2.1 > i18n correctness > Tailwind utilities > custom CSS > inline styles.

---

## STACK

```
Tailwind CSS  : CDN (https://cdn.tailwindcss.com) — NO build, NO PostCSS
HTMX          : 1.9.12 CDN — partial HTML loading
Fonts         : Google Fonts — Inter (300/400/500/600/700)
JS            : Vanilla ES6 — no frameworks
i18n          : translations.json + data-i18n attributes + runtime JS injection
Persistence   : localStorage (language), sessionStorage (scroll-after-reload)
```

---

## CRITICAL CONSTRAINTS

1. **NEVER use `@apply`** — Tailwind CDN does not process PostCSS directives at runtime. `@apply` silently produces no CSS.
2. **NEVER add `style="..."` inline attributes** — use Tailwind utility classes in `class=""` instead.
3. **Arbitrary Tailwind values are allowed**: `h-[38px]`, `max-w-[120px]`, `tracking-[0.3em]`, etc.
4. **Descendant selectors** (`.case-text h2`, `.case-text p`) require plain CSS in `<style>` — Tailwind utilities cannot target child elements from a parent class.
5. **CSS custom properties** defined in `:root` are used for brand colors:
   - `--bg-primary: #ffffff`
   - `--text-primary: #18181b`
   - `--accent: #2563eb`

---

## FILE ARCHITECTURE

```
index.html              Shell: CDN imports, <style>, JS functions, HTMX loaders
translations.json       All i18n strings keyed by language then key
components/
  header.html           Fixed nav — always in DOM, NOT inside #app
  hero.html             Section id="sobre"
  brands.html           Logo carousel — infinite scroll animation
  projects.html         Section id="projetos" — case entry buttons
  case-1.html           Case study page, replaces #app via HTMX
  case-2.html           Case study page, replaces #app via HTMX
  footer.html           Section id="contato" — always in DOM, NOT inside #app
```

---

## DOM LAYOUT (index.html body)

```html
<a class="skip-link" href="#main-content">...</a>   <!-- WCAG skip nav -->

<!-- header: always visible, outside #app -->
<div hx-get="components/header.html" hx-trigger="load" hx-swap="outerHTML"></div>

<!-- #app: replaced by case-1 or case-2 on case load -->
<div id="app">
  <main id="main-content">
    <!-- hero loaded here -->
  </main>
  <!-- brands loaded here -->
  <!-- projects loaded here -->
</div>

<!-- footer: always visible, outside #app -->
<div hx-get="components/footer.html" hx-trigger="load" hx-swap="outerHTML"></div>
```

**Rule:** `header.html` and `footer.html` are NEVER inside `#app`. All other sections are inside `#app`.

---

## NAVIGATION ARCHITECTURE

### Home view (default)
- All sections scroll in one page: `#sobre` → `#projetos` → `#contato`
- Anchor links work directly via `href="#id"` or `navigateTo('id')`

### Case view (case-1, case-2)
- Triggered by buttons in `projects.html` with `hx-target="#app" hx-swap="innerHTML"`
- Replaces entire `#app` content — hero, brands, and projects disappear
- Footer (`#contato`) and header remain visible at all times

### navigateTo(id) function
```js
function navigateTo(id) {
  const el = document.getElementById(id);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' });  // on home view
  } else {
    sessionStorage.setItem('scrollAfterLoad', id);
    window.location.reload();  // on case view — reload then scroll
  }
}
```
- Used by header nav links for `#sobre` and `#projetos`
- After reload, `initI18n()` reads `sessionStorage` and scrolls after 400ms delay (waits for HTMX components)

### Back from case
```html
<a href="/" ...>Voltar</a>
```
- Plain `href="/"` reload — restores full home view cleanly

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
- Element content is EMPTY in HTML — JS populates it at runtime via `innerHTML`
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
3. Leave element content empty: `<span data-i18n="new-key"></span>`

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
<div hx-get="components/filename.html" hx-trigger="load" hx-swap="outerHTML"></div>
```

### Replacing a section with case content
```html
<button hx-get="components/case-1.html" hx-target="#app" hx-swap="innerHTML">...</button>
```

### Rules
- Use `hx-swap="outerHTML"` when the placeholder `<div>` should be fully replaced
- Use `hx-swap="innerHTML"` when the target container should keep its element but have its content replaced
- Always add `translatePage()` in `htmx:afterOnLoad` — loaded fragments will have empty `data-i18n` elements

---

## ACCESSIBILITY (WCAG 2.1)

### Skip navigation
```html
<a href="#main-content" class="skip-link">Pular para o conteúdo principal</a>
```
CSS: visually hidden by default (`top: -40px`), revealed on `:focus` (`top: 0`).

### Semantic HTML
- Use `<header>`, `<main>`, `<nav>`, `<footer>`, `<article>`, `<section>` appropriately
- `<nav>` must have `aria-label`
- Use `<h1>` through `<h3>` in correct hierarchy — never skip heading levels

### Interactive elements
- All `<a>` links must have accessible text via content, `data-i18n`, or `title` attribute
- All `<button>` elements must have accessible text via content, `data-i18n`, or `title` attribute
- `<img>` elements must have descriptive `alt` text — never `alt=""`  unless decorative
- Empty `data-i18n` elements that are links/buttons MUST have a `title` attribute as fallback

### Language
- `<html lang="...">` must match `currentLang`: `pt-BR` or `en`
- Updated in `translatePage()` on every language switch

### Color contrast
- Body text: `#18181b` on `#ffffff` — passes AA
- Secondary text: `#52525b` (zinc-600) — passes AA at large sizes
- Accent: `#2563eb` (blue-600) — use on white backgrounds only
- Never use color alone to convey information

### Focus management
- Do not remove outlines. If Tailwind `outline-none` is used, add a custom `focus-visible:ring` replacement
- After HTMX content loads into a case page, `window.scrollTo(0,0)` resets viewport

### Animations
- Carousel: `animation-play-state: paused` on hover — respects user preference indirectly
- For full compliance, consider: `@media (prefers-reduced-motion: reduce) { .carousel-track { animation: none; } }`

---

## TAILWIND USAGE RULES

### DO
```html
<!-- Use utility classes directly in markup -->
<img class="h-7 w-auto max-w-[120px] object-contain grayscale opacity-40
            transition-all duration-300 hover:grayscale-0 hover:opacity-100 hover:scale-105" />

<!-- Arbitrary values are fine -->
<span class="text-[10px] tracking-[0.3em] h-[38px]"></span>

<!-- Responsive and state variants work -->
<div class="hidden md:flex text-center md:text-left"></div>
```

### DO NOT
```css
/* INVALID in CDN Tailwind */
.my-class {
  @apply h-7 w-auto; /* silently fails — produces no CSS */
}
```

### When plain CSS is required
Use plain CSS in `<style>` only for:
1. Descendant selectors: `.case-text h2`, `.case-text blockquote`
2. Keyframe animations: `@keyframes scroll`
3. Pseudo-class behaviors not achievable with Tailwind variants: `.skip-link:focus`
4. One-off JavaScript-toggled classes: `.lang-btn-active`

### Active state pattern
```css
/* In <style> — not @apply */
.lang-btn-active {
  background-color: black;
  color: white !important; /* !important needed to override Tailwind text-zinc-900 */
}
```

---

## COMPONENT PATTERNS

### Nav link (home anchor)
```html
<a href="#section-id"
   onclick="navigateTo('section-id'); return false;"
   class="hover:text-black transition-colors"
   data-i18n="nav-key"
></a>
```

### Nav link (external / always present anchor like #contato)
```html
<a href="#contato"
   class="hover:text-black transition-colors"
   data-i18n="nav-contact"
   title="Contato"
></a>
```

### Case open button (in projects.html)
```html
<button
  title="case-1"
  hx-get="components/case-1.html"
  hx-target="#app"
  hx-swap="innerHTML"
  class="inline-flex items-center gap-2 bg-zinc-900 text-white px-7 py-3.5
         rounded-full font-bold hover:bg-zinc-800 transition-all"
>
  <span data-i18n="case1-btn"></span>
  <!-- svg arrow icon -->
</button>
```

### Case back link (in case-*.html)
```html
<a href="/"
   title="Voltar para projetos"
   class="text-zinc-500 hover:text-black mb-12 flex items-center gap-2 transition-colors"
>
  <!-- svg left arrow -->
  <span data-i18n="btn-back"></span>
</a>
```

### Logo image (brands.html)
```html
<img
  src="images/filename.png"
  alt="Company Name"
  class="h-7 w-auto max-w-[120px] object-contain grayscale opacity-40
         transition-all duration-300 hover:grayscale-0 hover:opacity-100 hover:scale-105"
/>
```
Height variants: `h-7` (28px default), `h-[38px]` (38px), `h-11` (44px).

---

## CURRENT TRANSLATIONS KEYS

| Key | Purpose |
|-----|---------|
| `nav-home` | Header: Home |
| `nav-about` | Header: About/Sobre |
| `nav-projects` | Header: Projects/Projetos |
| `nav-contact` | Header: Contact/Contato |
| `hero-tag` | Hero eyebrow label |
| `hero-title` | Hero H1 |
| `hero-desc` | Hero paragraph |
| `btn-projects` | Hero CTA button |
| `btn-back` | Case back link |
| `brands-title` | Carousel section heading |
| `projects-title` | Projects section H2 |
| `projects-desc` | Projects section subtitle |
| `case1-tag` / `case2-tag` | Case eyebrow label |
| `case1-title` / `case2-title` | Case H1/H3 |
| `case1-desc` / `case2-desc` | Case summary (in projects list) |
| `case1-btn` / `case2-btn` | Case open button text |
| `meta-role` / `meta-year` / `meta-duration` / `meta-team` / `meta-status` / `meta-focus` | Case metadata labels |
| `meta-role-val-1` | Case metadata value: role |
| `meta-status-val` | Case metadata value: status |
| `case1-duration` / `case1-team` | Case 1 metadata values |
| `case-disclaimer` | NDA notice shown in cases |
| `case-resp-title` | "Responsibilities" section heading |
| `case1-resp-1..5` | Case 1 responsibility list items |
| `case-overview-title` | "Overview" section heading |
| `case1-overview` | Case 1 overview paragraph |
| `case-problem-title` | "Problem" section heading |
| `case1-quote` | Case 1 blockquote |
| `case-results-title` | "Results" section heading |
| `case1-results` | Case 1 results paragraph |
| `case2-context-title` | Case 2 context H2 |
| `case2-problem-title` | Case 2 problem H3 |
| `case2-problem-desc` | Case 2 problem paragraph |
| `cta-title` | Footer CTA heading |
| `footer-name` | Footer designer name |
| `footer-copy` | Footer copyright text |
| `footer-email-link` | Footer email link label |
| `footer-linkedin` | Footer LinkedIn link label |

---

## CHECKLIST — Before submitting any change

- [ ] No `@apply` in `<style>` blocks
- [ ] No `style=""` inline attributes
- [ ] Every `<img>` has a descriptive `alt`
- [ ] Every interactive empty element has `title` or `data-i18n` that resolves to text
- [ ] New text content has keys in BOTH `pt` and `en` in `translations.json`
- [ ] New HTML elements with text use `data-i18n` and are empty in markup
- [ ] Any new HTMX-loaded content will trigger `translatePage()` via `htmx:afterOnLoad`
- [ ] Sections that must always be visible (header, footer) are NOT inside `#app`
- [ ] Case content buttons target `#app` with `hx-swap="innerHTML"`
- [ ] `navigateTo()` used for header nav links that may not exist in case view
