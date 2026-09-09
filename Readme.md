# Corporate Design — Svelte + Material 3

> ⚠&#xFE0F; This project contains significant AI-generated code. Token values and contrast ratios are
> verified by `generate.py`; `theme.ts` and the `android/*.kt` files compile clean under tsc 7
> (strict) and kotlinc 2.4 / Compose 1.9 / Material 3 1.4. Runtime behavior is not yet
> battle-tested in a shipped app. Use at your own risk.

Color world: **Jet Black · Anthracite Grey · Traffic White** with **Pure Orange** as the only accent
color and **Signal Blue** reserved for info/status.

Two targets: **Svelte / SvelteKit applications using Material 3**
([`@material/web`](https://github.com/material-components/material-web) components) and **Android
apps using Jetpack Compose Material 3**. Light is the default theme; dark mode is controlled via
`data-theme` on `<html>` (web) or the `darkTheme` parameter (Android).

| File                    | Purpose                                                                                                 |
| ----------------------- | ------------------------------------------------------------------------------------------------------- |
| `tokens.json`           | **Single source of truth**: brand anchors, ramps, roles, semantic colors, typography, shapes, elevation  |
| `generate.py`           | Emits everything below from `tokens.json` and verifies WCAG contrast (`--check` verifies without writing) |
| `tokens.css`            | All Material 3 system tokens (`--md-sys-color-*`) for light and dark, plus brand anchors and ramps       |
| `theme.ts`              | Svelte store: `initTheme()` applies `data-theme` to `<html>`, persists the choice, reads the system pref |
| `android/CdColor.kt`    | The same tokens as Compose `ColorScheme`s (`CdLightColors`, `CdDarkColors`) plus brand/ramp constants    |
| `android/CdType.kt`     | `CdTypography` — the typescale (`FontFamily.Default` maps to Roboto; swap in one place)                  |
| `android/CdShape.kt`    | `CdShapes` — the corner-radius scale                                                                     |
| `android/CdSemantic.kt` | Success/warning/info/link colors — outside the M3 `ColorScheme`, via `cdSemanticColors()`                |
| `android/CdTheme.kt`    | `CdTheme()` composable — the `theme.ts` analog: system dark mode by default, override via `darkTheme`    |

Brand anchors (original RAL codes — do not modify): RAL 9005 `#0A0A0A`, RAL 7016 `#383E42`, RAL 9016
`#F1F0EA`, RAL 2004 `#E75B12`, RAL 5005 `#005387`.

---

## Setup

### 1. Import the tokens once

In SvelteKit, in your root layout:

```svelte
<!-- src/routes/+layout.svelte -->
<script>
  import '@corporate-design/tokens.css';
  import { initTheme } from '@corporate-design/theme.ts';

  initTheme();
</script>

<slot />
```

`initTheme()` reads the stored or system preference, applies it to `<html>`, and wires
persistence — importing the module alone has no side effects. It is SSR-safe (no-op on the
server), so calling it in the root layout is enough.

### 2. Avoid the flash of light theme

Put this inline script at the end of `<head>` in `app.html` (before the app renders):

```html
<script>
    const t = localStorage.getItem("cd-theme");
    document.documentElement.dataset.theme =
        t === "dark" || (!t && matchMedia("(prefers-color-scheme: dark)").matches)
            ? "dark"
            : "light";
</script>
```

### 3. Toggle the theme anywhere

```svelte
<script lang="ts">
  import { theme, toggleTheme } from '@corporate-design/theme.ts';
</script>

<button onclick={toggleTheme}>
  {$theme === 'light' ? 'Dark mode' : 'Light mode'}
</button>
```

(`onclick` is Svelte 5 syntax; use `on:click` in Svelte 4.)

### 4. Use Material 3 components

```bash
npm install @material/web
```

```svelte
<script>
  import '@material/web/button/filled-button.js';
  import '@material/web/button/text-button.js';
</script>

<md-filled-button>Primary action</md-filled-button>
```

The components read the `--md-sys-color-*` tokens automatically — no further wiring needed. The
**primary/CTA distinction** is a styling choice: primary buttons use `primary` out of the box, and
the orange CTA uses the tertiary colors:

```css
md-filled-button.cta {
    --md-filled-button-container-color: var(--md-sys-color-tertiary);
    --md-filled-button-label-text-color: var(--md-sys-color-on-tertiary);
}
```

---

## Android (Jetpack Compose Material 3)

### 1. Copy the five files

Copy `android/CdColor.kt`, `android/CdType.kt`, `android/CdShape.kt`, `android/CdSemantic.kt` and
`android/CdTheme.kt` into your app module (e.g.
`app/src/main/kotlin/<your-package>/corporatedesign/`). Adjust the `package` line to your module's
package path — they are plain Kotlin files, no dependency beyond Compose Material 3.

Requires **Material 3 1.4.0+**: the `*Fixed` roles (`primaryFixed`, …) became `lightColorScheme()` /
`darkColorScheme()` constructor parameters only in 1.4.0. On older versions drop those lines (the
fixed roles then fall back to library defaults).

### 2. Wrap your app

```kotlin
CdTheme {
    AppNavHost() // your content
}
```

By default `CdTheme` follows the system dark-mode setting. To override it, pass
`darkTheme = true` / `darkTheme = false`. `CdTheme` also applies `CdTypography` and `CdShapes`.

**Persisted choice (the `theme.ts` analog):** Compose has no `localStorage` — persistence is the
app's job. `rememberCdThemeState` gives you toggleable state and a hook to store it:

```kotlin
val themeState = rememberCdThemeState(
    initial = savedDark,                       // e.g. read from DataStore
    onThemeChange = { dark -> saveDark(dark) }, // e.g. write to DataStore
)

CdTheme(state = themeState) { /* ... */ }
// themeState.toggle() from any settings screen
```

### 3. Use the colors

All UI colors flow through `MaterialTheme.colorScheme` — never hardcode. Components then pick up
the corporate scheme automatically, and the orange CTA rule maps directly:

```kotlin
Button(
    onClick = { /* ... */ },
    colors = ButtonDefaults.buttonColors(
        containerColor = MaterialTheme.colorScheme.tertiary,
        contentColor = MaterialTheme.colorScheme.onTertiary,
    ),
) {
    Text("Continue")
}
```

The `Cd*` ramp constants (`CdOrange500` = RAL 2004, `CdGray800` = RAL 7016, `CdBlue800` = RAL 5005)
are for cases outside the role system — link text (`CdOrange700`), charts, branded splash surfaces.
Prefer roles first.

### 4. Platform theme (status bar / window)

`CdTheme` themes Compose only. Keep the platform theme minimal — e.g. a transparent status bar over
`CdTheme`'s `surface` color, `windowLightStatusBar` = `true` in light / `false` in dark
(`values/themes.xml` + `values-night/themes.xml`).

---

## Key tokens

<!-- key-tokens:start (generated by generate.py) -->

| Role                          | Light                         | Dark                  | Usage                                       |
|-------------------------------|-------------------------------|-----------------------|---------------------------------------------|
| `primary` / `on-primary`      | `#0A0A0A` / `#F1F0EA`         | `#F1F0EA` / `#0A0A0A` | buttons, switches, sliders                  |
| `primary-container` / `on-`   | `#383E42` / `#F1F0EA`         | `#2C3032` / (same)    | tonal containers, selected states           |
| `tertiary` / `on-tertiary`    | `#E75B12` / `#0A0A0A`         | `#FF8A3D` / (same)    | the orange cta — the only orange button     |
| `tertiary-container` / `on-`  | `#F6E9E2` / `#723615`         | `#4F2712` / `#EBBEA5` | orange-tinted chips, highlights             |
| `success` / `on-success`      | `#256E43` / `#F1F0EA`         | `#8FD5A8` / `#0F2A19` | confirmations, online states                |
| `warning` / `on-warning`      | `#8A5A00` / `#F1F0EA`         | `#FFD48A` / `#2E2000` | cautions, degraded states                   |
| `info` / `on-info`            | `#005387` / `#F1F0EA`         | `#AAD4EE` / `#092434` | neutral hints, tips (signal blue, ral 5005) |
| `link` / `link-hover`         | `#954216` / `#723615`         | `#FF8A3D` / `#EBBEA5` | text links on body surfaces                 |
| `surface` / `on-surface`      | `#FFFFFF` / `#0A0A0A`         | `#131516` / `#F1F0EA` | backgrounds / text                          |
| `surface-container-highest`   | `#E1E3E5`                     | `#383E42`             | elevated cards, sheets                      |
| `surface-variant` / `on-`     | `#F1F0EA` / `#606A71`         | `#212426` / `#A2AAAF` | input fills, secondary text                 |
| `outline` / `outline-variant` | `#7D8991` / `#E1E3E5`         | — / `#3A3F42`         | input borders / decorative lines            |
| `error` / `on-error`          | `#A33030` / `#F1F0EA`         | `#F59A9A` / `#3A1A1A` | error states                                |
| `inverse-*`                   | snackbars, tooltips (defined) |                       |                                             |
<!-- key-tokens:end (generated by generate.py) -->

The full set of roles (including `*-fixed`, `surface-container-*`, `scrim`, `shadow`) is in
`tokens.css`.

---

## Design rules

1. **Page background is always white** in light mode (`--md-sys-color-surface: #FFFFFF`). Grey is
   structure (borders, chrome, dark surfaces), not a background color. RAL 9016 as
   `surface-variant` is deliberate: traffic white doubles as the warm off-white for input fills
   and quiet containers — a surface tint, not white used as an accent.
2. **Orange has three fixed jobs:** CTA button, active navigation item, chart highlight. Do not
   scatter orange decoratively — its impact lives in its scarcity.
3. **Text on orange is always black** (`--md-sys-color-on-tertiary`), never white (white on RAL 2004
   = 3.6:1, fails AA for body text).
4. **Primary ≠ CTA:** primary is jet black (light) / traffic white (dark). The CTA is the only
   orange button on the page (tertiary styling, see snippet above). Max. one CTA per view.
5. **Text links** use the `--cd-link` / `--cd-link-hover` tokens: orange-700 (`#954216`, 6.8:1) on
   light, orange-400 (`#FF8A3D`, 7.8:1) on dark. Never RAL 2004 directly.
6. **Keep dynamic color off.** Do not use Material You / wallpaper theming — it would replace the
   brand palette. Do not call `ColorScheme.fromSeed()` equivalents; the tokens above are the scheme.
7. **RAL 7016 appears on hero/brand surfaces and `surface-container-highest` (dark) only** — not as
   a page or card background.
8. **Status colors** stay tinted background + dark text (success/warning/error/info pattern);
   warning is deliberately yellow/amber, never orange.
9. **Signal Blue (RAL 5005) is info only.** It backs the `info` status family (solid accent, tinted
   container) — never a button, nav item or accent. Info-adjacent visuals may use the blue ramp (see
   ramp guide).

---

## Changing tokens (codegen)

`tokens.json` is the single source; everything else is generated. Never edit `tokens.css` or the
`android/*.kt` files by hand:

```bash
python3 generate.py          # regenerate all outputs, fails on WCAG violations
python3 generate.py --check  # verify outputs are in sync + contrast, write nothing
```

The script re-computes every `on-*` contrast ratio (≥ 4.5:1) and `outline` against the background
(≥ 3:1) and refuses to emit anything that fails. The key-tokens table above is regenerated in
place between the `key-tokens` markers.

**Versioning:** `Version.txt` holds the version (semver). Any change to token *values* is at least
a minor bump; refactors without value changes bump the patch. A bump moves all artifacts in
lockstep — they are one design, emitted five ways.

---

## Ramp guide

The ramps are full scales; roles and rules pick from them. When something sits outside the role
system, pick by job, not by taste:

| Job                                   | Light mode                | Dark mode                 |
| ------------------------------------- | ------------------------- | ------------------------- |
| Hover / pressed on a light surface    | one step darker (e.g. orange-600 for the CTA) | —              |
| Disabled element                      | gray-400 (outline tone)   | gray-600                  |
| Decorative hairline                   | gray-200 (`outline-variant`) | `outline-variant`      |
| Chart series (beyond the orange highlight) | gray-500, gray-300, gray-700 | gray-400, gray-300, gray-600 |
| Illustration / brand surfaces         | RAL anchors and ramp steps around 500 | steps around 300–400 |

Grey steps not named by a role are intentionally free — but prefer roles first; reach for raw ramp
steps only for cases the role system does not cover (charts, illustrations, brand moments). The blue
ramp is derived from RAL 5005 and backs the `info` role — outside that, use it only for info-adjacent
visuals (help illustrations, info charts), never as an accent.

---

## Interaction states & focus

- **State layers** (hover/focus/pressed/dragged) follow the M3 overlay opacities, exposed as
  `--cd-state-hover: 0.08`, `--cd-state-focus: 0.12`, `--cd-state-pressed/dragged: 0.16`. Overlay
  `on-*` color at these opacities on top of the container color; never swap container colors for
  hover — the brand colors stay put and the state reads as a veil.
- **Focus ring**: `--cd-focus-ring-*` (2px `outline` color, 2px offset). Visible keyboard focus is
  mandatory; `outline` at 3.6:1 on white clears the 3:1 non-text minimum.
- Compose: M3 components apply state layers automatically; for custom composables use
  `Modifier.clickable` with the same 0.08/0.12/0.16 opacities.

---

## Typography

The typescale is M3's role/size grid set in **DejaVu Sans** (mono: DejaVu Sans Mono). CSS exposes
it as `--md-sys-typescale-*` shorthand values plus `--cd-font-family`; the family is one variable,
so swapping the brand font later touches exactly one line in `tokens.json`.

Emoji render through per-glyph font fallback (Noto/Apple/Segoe emoji) — no font stacks emoji
natively; DejaVu's missing emoji are a non-issue on the web.

On Android, DejaVu Sans is not part of the system: `CdType.kt` ships `FontFamily.Default` (Roboto)
and the typescale on top. To use DejaVu there, bundle the TTFs in `res/font/` and change
`CdFontFamily` — one place.
