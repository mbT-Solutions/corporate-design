#!/usr/bin/env python3
"""single source of truth: tokens.json -> tokens.css, android/*.kt, readme table.

usage: python3 generate.py          # write all outputs
       python3 generate.py --check  # only verify contrast + readme sync
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
FAILURES = []


def load():
    return json.loads((ROOT / "tokens.json").read_text())


# ---------- color resolution ----------

def toks(group):
    """token dict of a group, comment keys stripped."""
    return {k: v for k, v in group.items() if k != "comment"}


def resolve(ref, data):
    """'ral:9005' / 'gray:850' / '#FFFFFF' -> '#0A0A0A' style hex (uppercase)."""
    if ref.startswith("#"):
        return ref.upper()
    kind, step = ref.split(":")
    if kind == "ral":
        return data["brand"][f"ral{step}"]["hex"].upper()
    return data["ramps"][kind][step].upper()


def contrast(a, b):
    def lum(h):
        h = h.lstrip("#")
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def check(name, fg, bg, minimum, mode, label=None):
    ratio = contrast(fg, bg)
    if ratio < minimum:
        FAILURES.append(
            f"{mode} {name}: {fg} on {bg} = {ratio:.2f}:1, needs {minimum}:1"
            + (f" ({label})" if label else "")
        )
    return ratio


def pair_base(name):
    """container a token sits on; on-x-fixed-variant pairs with x-fixed-dim."""
    base = name[3:] if name.startswith("on-") else None
    if base and base.endswith("-fixed-variant"):
        return base[: -len("-variant")] + "-dim"
    return base


def verify(data):
    """on-* pairs and links >= 4.5:1, outline >= 3:1 against the mode background."""
    for group in data["roles"] + data["semantic"]:
        for mode in ("light", "dark"):
            toks = {}
            for name, spec in group["tokens"].items():
                val = spec.get(mode)
                toks[name] = resolve(val, data) if val else None
            for name, fg in toks.items():
                if fg is None:
                    continue
                base = pair_base(name)
                if base and toks.get(base):
                    check(name, fg, toks[base], 4.5, mode)
    bg_group = next(g["tokens"] for g in data["roles"] if "background" in g["tokens"])
    for mode in ("light", "dark"):
        bg = resolve(bg_group["background"][mode], data)
        for group in data["roles"]:
            for name, spec in group["tokens"].items():
                if name == "outline" and spec.get(mode):
                    check("outline", resolve(spec[mode], data), bg, 3.0, mode,
                          "non-text")
        for group in data["semantic"]:
            for name in ("link", "link-hover"):
                spec = group["tokens"].get(name)
                if spec and spec.get(mode):
                    check(name, resolve(spec[mode], data), bg, 4.5, mode,
                          "link text")


# ---------- naming ----------

def css_color_name(role):
    return f"--md-sys-color-{role}"


def camel(role):
    parts = role.split("-")
    return parts[0] + "".join(p.title() for p in parts[1:])


def kt_const(ref):
    """ref -> kotlin constant expression, reusing anchors/ramp vals."""
    if ref.startswith("#"):
        h = ref.lstrip("#").upper()
        return f"Color(0xFF{h})"
    kind, step = ref.split(":")
    if kind == "ral":
        return f"CdRal{step}"
    return f"Cd{kind.title()}{step}"


def fmt_ratio(ratio):
    return f"{ratio:.1f}" .rstrip("0").rstrip(".") if ratio else ""


# ---------- emitters ----------

def emit_css(data):
    lines = [
        "/* ==========================================================================",
        "   Corporate Design — Material 3 tokens for Svelte / SvelteKit",
        "   GENERATED from tokens.json by generate.py — do not edit here.",
        "   Integration:  import in your root layout (+layout.svelte) or app.css",
        "   Theme switch: <html data-theme=\"light\">  or  <html data-theme=\"dark\">",
        "                 (light is the :root fallback; initTheme()/the head script",
        "                 pick stored-or-system on first visit)",
        "   All Material 3 tokens follow the official --md-sys-color-* names, so",
        "   @material/web components pick them up automatically.",
        "   ========================================================================== */",
        "",
        ":root {",
        "  color-scheme: light;",
        "",
        "  /* ---- Brand anchors: the original RAL codes, do not modify ---- */",
    ]
    for key, spec in toks(data["brand"]).items():
        lines.append(f"  --cd-{key}: {spec['hex']};  /* {spec['name']} */")

    lines.append("")
    for ramp, comment in data["ramps"]["ramp_comments"].items():
        lines.append(f"  /* ---- {comment} ---- */")
        for step, hexv in data["ramps"][ramp].items():
            note = data["ramp_notes"].get(f"{ramp}:{step}")
            note = f"  /* {note} */" if note else ""
            pad = " " * (max(0, 18 - len(f"--cd-{ramp}-{step}:")) )
            lines.append(f"  --cd-{ramp}-{step}: {hexv};{pad}{note}".rstrip())
        lines.append("")

    lines.append("  /* ---- Material 3 system tokens: LIGHT (:root fallback) ---- */")
    for group in data["roles"]:
        lines.append("")
        lines.append(f"  /* {group['comment']} */")
        for name, spec in group["tokens"].items():
            if spec.get("css") is False:
                continue
            light = resolve(spec["light"], data)
            bg = None
            base = pair_base(name)
            if base and base in group["tokens"]:
                bg = resolve(group["tokens"][base]["light"], data)
                note = f"  /* {contrast(light, bg):.1f}:1 */"
            else:
                note = ""
            pad = " " * max(1, 31 - len(f"{css_color_name(name)}: {light};"))
            lines.append(f"  {css_color_name(name)}: {light};{pad}{note}".rstrip())

    for group in data["semantic"]:
        lines.append("")
        lines.append(f"  /* {group['comment']} */")
        for name, spec in group["tokens"].items():
            light = resolve(spec["light"], data)
            bg = None
            base = pair_base(name)
            if base and base in group["tokens"]:
                bg = resolve(group["tokens"][base]["light"], data)
                note = f"  /* {contrast(light, bg):.1f}:1 */"
            else:
                note = ""
            pad = " " * max(1, 31 - len(f"--cd-{name}: {light};"))
            lines.append(f"  --cd-{name}: {light};{pad}{note}".rstrip())

    t = data["typography"]
    lines += ["", f"  /* ---- {t['comment']} ---- */",
              f"  --cd-font-family: {t['family']};",
              f"  --cd-font-family-mono: {t['family_mono']};"]
    for style, s in t["styles"].items():
        lines.append(
            f"  --md-sys-typescale-{style}: "
            f"{s['weight']} {s['size']}px/{s['line']}px "
            f"{s['tracking']}px var(--cd-font-family);"
        )

    sh = data["shapes"]
    lines += ["", f"  /* ---- {sh['comment']} ---- */"]
    for name, v in sh.items():
        if name == "comment":
            continue
        val = "9999px" if v is None else f"{v}px"
        lines.append(f"  --md-sys-shape-corner-{name}: {val};")

    el = data["elevation"]
    lines += ["", f"  /* ---- {el['comment']} ---- */"]
    for name, v in el.items():
        if name == "comment":
            continue
        lines.append(f"  --md-sys-elevation-{name[5:]}: {v}px;")

    sl = data["state_layers"]
    lines += ["", f"  /* ---- {sl['comment']} ---- */"]
    for name, v in sl.items():
        if name == "comment":
            continue
        lines.append(f"  --cd-state-{name}: {v};")

    fr = data["focus_ring"]
    lines += ["", f"  /* ---- {fr['comment']} ---- */",
              f"  --cd-focus-ring-width: {fr['width']}px;",
              f"  --cd-focus-ring-offset: {fr['offset']}px;",
              f"  --cd-focus-ring-color: var(--md-sys-color-{fr['color']});"]
    lines.append("}")

    lines += ["", '[data-theme="dark"] {', "  color-scheme: dark;", ""]
    first = True
    for group in data["roles"] + data["semantic"]:
        emitted = []
        for name, spec in group["tokens"].items():
            if spec.get("css") is False:
                continue
            dark = spec.get("dark")
            nm = css_color_name(name) if group not in data["semantic"] else f"--cd-{name}"
            if dark is None:
                continue
            dark_hex = resolve(dark, data)
            light_hex = resolve(spec["light"], data)
            if dark_hex == light_hex and group not in data["semantic"]:
                continue  # same in both modes: cascade provides it
            bg = None
            base = pair_base(name)
            if base and base in group["tokens"]:
                bgspec = group["tokens"][base]
                bg_ref = bgspec.get("dark") or bgspec["light"]
                bg = resolve(bg_ref, data)
            note = f"  /* {contrast(dark_hex, bg):.1f}:1 */" if bg else ""
            pad = " " * max(1, 31 - len(f"{nm}: {dark_hex};"))
            emitted.append(f"  {nm}: {dark_hex};{pad}{note}".rstrip())
        if emitted:
            if not first:
                lines.append("")
            lines.append(f"  /* {group['comment']} */")
            lines += emitted
            first = False
    # fixed-role note: css cascade means light values carry over
    lines += [
        "",
        "  /* *-fixed* roles are not redefined: the css cascade keeps the light",
        "     values, which is exactly the m3 fixed-role semantics (compose has",
        "     no cascade, so CdColor.kt repeats them explicitly) */",
    ]
    t = data["typography"]
    lines += ["", "  /* typography, shapes, elevation, state layers are theme-independent */"]
    lines.append("}")
    return "\n".join(lines) + "\n"


def kt_role_lines(group, mode, data, all_groups):
    out = []
    for name, spec in group["tokens"].items():
        if spec.get("kt") is False:
            continue
        ref = spec.get(mode) or spec["light"]
        dark_note = ""
        if mode == "dark" and spec.get("dark") is None and group in data["roles"]:
            # fixed role: repeat light value, no cascade in compose
            pass
        val = kt_const(ref)
        base = pair_base(name)
        note = ""
        if base and base in group["tokens"]:
            bgspec = group["tokens"][base]
            bg_ref = bgspec.get(mode) or bgspec["light"]
            note = f" // {contrast(resolve(ref, data), resolve(bg_ref, data)):.1f}:1"
        out.append(f"    {camel(name)} = {val},{note}")
    return out


def emit_kt_colors(data):
    lines = [
        "package de.madebytimo.corporatedesign",
        "",
        "import androidx.compose.material3.darkColorScheme",
        "import androidx.compose.material3.lightColorScheme",
        "import androidx.compose.ui.graphics.Color",
        "",
        "// generated from tokens.json by generate.py — keep both in sync via the script",
        "",
        "// brand anchors: the original ral codes, do not modify",
    ]
    for key, spec in toks(data["brand"]).items():
        h = spec["hex"].lstrip("#").upper()
        lines.append(f"val Cd{key[:3].title()}{key[3:]} = Color(0xFF{h}) // {spec['name']}")

    for ramp, comment in data["ramps"]["ramp_comments"].items():
        lines += ["", f"// {comment}"]
        for step, hexv in data["ramps"][ramp].items():
            note = data["ramp_notes"].get(f"{ramp}:{step}")
            anchor = {"gray:800": "CdRal7016", "orange:500": "CdRal2004",
                      "blue:800": "CdRal5005"}.get(f"{ramp}:{step}")
            val = anchor or f"Color(0xFF{hexv.lstrip('#').upper()})"
            cmt = f" // {note}" if note else ""
            lines.append(f"val Cd{ramp.title()}{step} = {val}{cmt}")

    for title, mode, ctor in (("light", "light", "lightColorScheme"),
                              ("dark", "dark", "darkColorScheme")):
        lines += ["", f"// {title} scheme"]
        if mode == "dark":
            lines.append("// fixed roles repeat the light values: compose has no css cascade")
        lines.append(f"val Cd{title.title()}Colors = {ctor}(")
        for group in data["roles"]:
            role_lines = kt_role_lines(group, mode, data, data["roles"])
            if role_lines:
                lines.append(f"    // {group['comment']}")
                lines += role_lines
        lines.append(")")
    return "\n".join(lines) + "\n"


def emit_kt_type(data):
    t = data["typography"]
    lines = [
        "package de.madebytimo.corporatedesign",
        "",
        "import androidx.compose.material3.Typography",
        "import androidx.compose.ui.text.TextStyle",
        "import androidx.compose.ui.text.font.FontFamily",
        "import androidx.compose.ui.text.font.FontWeight",
        "import androidx.compose.ui.unit.sp",
        "",
        "// generated from tokens.json by generate.py",
        "// dejavu sans is not bundled on android: FontFamily.Default maps to roboto",
        "// bundle dejavu sans as res/font and swap the family in one place",
        "val CdFontFamily = FontFamily.Default",
        "val CdFontFamilyMono = FontFamily.Monospace",
        "",
        "val CdTypography = Typography(",
    ]
    for style, s in t["styles"].items():
        weight = f"FontWeight({s['weight']})"
        track = f"{s['tracking']}".rstrip("0").rstrip(".") or "0"
        track = f"({track}).sp" if s["tracking"] < 0 else f"{track}.sp"
        lines += [
            f"    {camel(style)} = TextStyle(",
            f"        fontFamily = CdFontFamily,",
            f"        fontWeight = {weight},",
            f"        fontSize = {s['size']}.sp,",
            f"        lineHeight = {s['line']}.sp,",
            f"        letterSpacing = {track},",
            f"    ),",
        ]
    lines.append(")")
    return "\n".join(lines) + "\n"


def emit_kt_shape(data):
    sh = data["shapes"]
    lines = [
        "package de.madebytimo.corporatedesign",
        "",
        "import androidx.compose.foundation.shape.RoundedCornerShape",
        "import androidx.compose.material3.Shapes",
        "",
        "// generated from tokens.json by generate.py",
        "// corner-none and corner-full (pill) are not Shapes slots:",
        "// use RoundedCornerShape(0) / RoundedCornerShape(percent = 50) directly",
        "val CdShapes = Shapes(",
    ]
    for name, v in sh.items():
        if name in ("comment", "none") or v is None:
            continue
        lines.append(f"    {camel(name)} = RoundedCornerShape({v}),")
    lines.append(")")
    return "\n".join(lines) + "\n"


def emit_kt_status(data):
    """semantic colors have no ColorScheme slot: expose both modes + accessor."""
    lines = [
        "package de.madebytimo.corporatedesign",
        "",
        "import androidx.compose.runtime.Composable",
        "import androidx.compose.runtime.staticCompositionLocalOf",
        "import androidx.compose.ui.graphics.Color",
        "",
        "// generated from tokens.json by generate.py",
        "// status/link colors live outside the m3 ColorScheme; pick per mode",
    ]
    group = data["semantic"][0]
    lgroup = data["semantic"][1]
    names = {**group["tokens"], **lgroup["tokens"]}
    for name, spec in names.items():
        lh = resolve(spec["light"], data).lstrip("#")
        dh = resolve(spec["dark"], data).lstrip("#")
        lines.append(
            f"private val {camel(name)}Light = Color(0xFF{lh})"
        )
        lines.append(
            f"private val {camel(name)}Dark = Color(0xFF{dh})"
        )
    lines += [
        "",
        "data class CdSemanticColors(",
    ]
    for name in names:
        lines.append(f"    val {camel(name)}: Color,")
    lines += [")", ""]
    for suffix in ("Light", "Dark"):
        lines.append(f"val CdSemanticColors{suffix} = CdSemanticColors(")
        for name in names:
            lines.append(f"    {camel(name)} = {camel(name)}{suffix},")
        lines += [")", ""]
    lines += [
        "val LocalCdSemanticColors = staticCompositionLocalOf { CdSemanticColorsLight }",
        "",
        "@Composable",
        "fun cdSemanticColors(darkTheme: Boolean? = null): CdSemanticColors =",
        "    when (darkTheme) {",
        "        true -> CdSemanticColorsDark",
        "        false -> CdSemanticColorsLight",
        "        null -> LocalCdSemanticColors.current",
        "    }",
        "",
    ]
    return "\n".join(lines) + "\n"


def readme_table(data):
    usage = data["role_usage"]
    flat = {}
    for group in data["roles"] + data["semantic"]:
        for name, spec in group["tokens"].items():
            flat[name] = (
                resolve(spec["light"], data),
                resolve(spec["dark"], data) if spec.get("dark") else None,
            )

    def light_cell(name):
        return f"`{flat[name][0]}`"

    def dark_cell(name):
        dark = flat[name][1]
        if dark is None:
            return "—"
        return f"`{dark}`" if dark != flat[name][0] else "(same)"

    def pair(primary, on):
        return light_cell(primary) + " / " + light_cell(on)

    def pair_dark(primary, on):
        p, o = dark_cell(primary), dark_cell(on)
        if p == "—" and o == "—":
            return "—"
        return p + " / " + o

    def render_table(rows):
        widths = [max(len(r[i]) for r in rows) + 2 for i in range(4)]
        out = [
            "| " + "Role".ljust(widths[0] - 2) + " | "
            + "Light".ljust(widths[1] - 2) + " | "
            + "Dark".ljust(widths[2] - 2) + " | "
            + "Usage".ljust(widths[3] - 2) + " |",
            "|" + "-" * widths[0] + "|" + "-" * widths[1]
            + "|" + "-" * widths[2] + "|" + "-" * widths[3] + "|",
        ]
        for row in rows:
            out.append(
                "| " + " | ".join(c.ljust(widths[i] - 2) for i, c in enumerate(row)) + " |"
            )
        return "\n".join(out)

    r = []
    r.append(("`primary` / `on-primary`", pair("primary", "on-primary"), pair_dark("primary", "on-primary"), usage.get("primary / on-primary", "")))
    r.append(("`primary-container` / `on-`", pair("primary-container", "on-primary-container"), pair_dark("primary-container", "on-primary-container"), usage.get("primary-container / on-", "")))
    r.append(("`tertiary` / `on-tertiary`", pair("tertiary", "on-tertiary"), pair_dark("tertiary", "on-tertiary"), usage.get("tertiary / on-tertiary", "")))
    r.append(("`tertiary-container` / `on-`", pair("tertiary-container", "on-tertiary-container"), pair_dark("tertiary-container", "on-tertiary-container"), usage.get("tertiary-container / on-", "")))
    r.append(("`surface` / `on-surface`", pair("surface", "on-surface"), pair_dark("surface", "on-surface"), usage.get("surface / on-surface", "")))
    r.append(("`surface-container-highest`", light_cell("surface-container-highest"), dark_cell("surface-container-highest"), usage.get("surface-container-highest", "")))
    r.append(("`surface-variant` / `on-`", pair("surface-variant", "on-surface-variant"), pair_dark("surface-variant", "on-surface-variant"), usage.get("surface-variant / on-", "")))
    r.append(("`outline` / `outline-variant`", light_cell("outline") + " / " + light_cell("outline-variant"), dark_cell("outline") + " / " + dark_cell("outline-variant"), usage.get("outline / outline-variant", "")))
    r.append(("`error` / `on-error`", pair("error", "on-error"), pair_dark("error", "on-error"), usage.get("error / on-error", "")))
    r.append(("`inverse-surface` / `inverse-on-surface`", pair("inverse-surface", "inverse-on-surface"), pair_dark("inverse-surface", "inverse-on-surface"), usage.get("inverse-surface / inverse-on-surface", "")))
    r.append(("`inverse-primary`", light_cell("inverse-primary"), dark_cell("inverse-primary"), usage.get("inverse-primary", "")))

    s = []
    s.append(("`success` / `on-success`", pair("success", "on-success"), pair_dark("success", "on-success"), usage.get("success / on-success", "")))
    s.append(("`warning` / `on-warning`", pair("warning", "on-warning"), pair_dark("warning", "on-warning"), usage.get("warning / on-warning", "")))
    s.append(("`info` / `on-info`", pair("info", "on-info"), pair_dark("info", "on-info"), usage.get("info / on-info", "")))
    s.append(("`link` / `link-hover`", light_cell("link") + " / " + light_cell("link-hover"), dark_cell("link") + " / " + dark_cell("link-hover"), usage.get("link", "")))

    return "\n\n".join([
        "**Material roles** (`--md-sys-color-*`):",
        render_table(r),
        "**Semantic extensions** (`--cd-*`):",
        render_table(s),
        "`(same)` = identical to the light value; `—` = not defined for that mode.",
    ])


README_MARKERS = ("<!-- key-tokens:start (generated by generate.py) -->",
                  "<!-- key-tokens:end (generated by generate.py) -->")


def update_readme(data):
    path = ROOT / "Readme.md"
    text = path.read_text()
    table = readme_table(data)
    start, end = README_MARKERS
    if start not in text or end not in text:
        return False
    pre, rest = text.split(start, 1)
    _, post = rest.split(end, 1)
    path.write_text(pre + start + "\n\n" + table + "\n" + end + post)
    return True


def main():
    data = load()
    verify(data)
    outputs = {
        "tokens.css": emit_css(data),
        "android/CdColor.kt": emit_kt_colors(data),
        "android/CdType.kt": emit_kt_type(data),
        "android/CdShape.kt": emit_kt_shape(data),
        "android/CdSemantic.kt": emit_kt_status(data),
    }
    if FAILURES:
        print("CONTRAST FAILURES:", file=sys.stderr)
        for f in FAILURES:
            print("  " + f, file=sys.stderr)
        sys.exit(1)
    check_only = "--check" in sys.argv
    if check_only:
        for rel, content in outputs.items():
            cur = (ROOT / rel).read_text() if (ROOT / rel).exists() else ""
            if cur != content:
                print(f"OUT OF SYNC: {rel} (run generate.py)", file=sys.stderr)
                sys.exit(1)
        readme = (ROOT / "Readme.md").read_text()
        if readme_table(data) not in readme:
            print("OUT OF SYNC: Readme.md table (run generate.py)", file=sys.stderr)
            sys.exit(1)
        print("all outputs in sync, contrast ok")
        return
    for rel, content in outputs.items():
        (ROOT / rel).write_text(content)
        print(f"wrote {rel}")
    if update_readme(data):
        print("updated Readme.md key-tokens table")
    else:
        print("NOTE: Readme.md has no key-tokens markers — table not updated")


if __name__ == "__main__":
    main()
