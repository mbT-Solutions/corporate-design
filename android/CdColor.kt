package de.madebytimo.corporatedesign

import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color

// generated from tokens.json by generate.py — keep both in sync via the script

// brand anchors: the original ral codes, do not modify
val CdRal7016 = Color(0xFF383E42) // anthracite grey
val CdRal9005 = Color(0xFF0A0A0A) // jet black
val CdRal9016 = Color(0xFFF1F0EA) // traffic white
val CdRal2004 = Color(0xFFE75B12) // pure orange
val CdRal5005 = Color(0xFF005387) // signal blue

// grey ramp (hue consistently derived from ral 7016, h≈204°)
val CdGray50 = Color(0xFFF7F7F8)
val CdGray100 = Color(0xFFEFF0F1)
val CdGray200 = Color(0xFFE1E3E5)
val CdGray300 = Color(0xFFC9CDCF)
val CdGray400 = Color(0xFFA2AAAF)
val CdGray500 = Color(0xFF7D8991)
val CdGray600 = Color(0xFF606A71)
val CdGray700 = Color(0xFF495055)
val CdGray800 = CdRal7016 // = ral 7016
val CdGray850 = Color(0xFF2C3032)
val CdGray900 = Color(0xFF212426)
val CdGray950 = Color(0xFF131516)

// orange ramp (derived from ral 2004, h≈21°)
val CdOrange50 = Color(0xFFF9F2EE)
val CdOrange100 = Color(0xFFF6E9E2)
val CdOrange200 = Color(0xFFF1D7C9)
val CdOrange300 = Color(0xFFEBBEA5)
val CdOrange400 = Color(0xFFFF8A3D) // dark mode accent
val CdOrange500 = CdRal2004 // = ral 2004, brand orange
val CdOrange600 = Color(0xFFB94F15) // unused by roles — hover is a state layer
val CdOrange700 = Color(0xFF954216) // link text on light (6.8:1)
val CdOrange800 = Color(0xFF723615)
val CdOrange900 = Color(0xFF4F2712)
val CdOrange950 = Color(0xFF391D0E)

// red ramp (h=0) — ramps are full scales; roles pick from them
val CdRed50 = Color(0xFFF9F0F0)
val CdRed100 = Color(0xFFF6E4E4)
val CdRed200 = Color(0xFFF59A9A) // dark mode error accent
val CdRed300 = Color(0xFFE08585)
val CdRed400 = Color(0xFFDA6262)
val CdRed500 = Color(0xFFCC3E3E)
val CdRed600 = Color(0xFFA33030) // light mode error accent
val CdRed700 = Color(0xFF862727)
val CdRed800 = Color(0xFF5C2323)
val CdRed900 = Color(0xFF3A1A1A) // dark mode error container
val CdRed950 = Color(0xFF2E1414)

// blue ramp (derived from ral 5005, h≈203°) — info/status only, never an accent
val CdBlue50 = Color(0xFFF0F6F9)
val CdBlue100 = Color(0xFFE4EFF7) // light mode info container
val CdBlue200 = Color(0xFFAAD4EE) // dark mode info accent, also on-info-container
val CdBlue300 = Color(0xFF7AC0EB)
val CdBlue400 = Color(0xFF45ACED)
val CdBlue500 = Color(0xFF1299ED)
val CdBlue600 = Color(0xFF0D7EC5)
val CdBlue700 = Color(0xFF0766A2)
val CdBlue800 = CdRal5005 // = ral 5005, brand blue, light mode info accent
val CdBlue900 = Color(0xFF083754) // light on-info-container, dark info container
val CdBlue950 = Color(0xFF092434) // dark mode on-info

// light scheme
val CdLightColors = lightColorScheme(
    // primary = the brand's black action color (buttons, switches, sliders)
    primary = CdRal9005,
    onPrimary = CdRal9016, // 17.3:1
    primaryContainer = CdRal7016,
    onPrimaryContainer = CdRal9016, // 9.5:1
    primaryFixed = CdRal7016,
    onPrimaryFixed = CdRal9016, // 9.5:1
    primaryFixedDim = CdGray700,
    onPrimaryFixedVariant = CdRal9016, // 7.2:1
    // secondary = muted grey for less prominent actions
    secondary = CdGray700,
    onSecondary = CdRal9016, // 7.2:1
    secondaryContainer = CdGray200,
    onSecondaryContainer = CdGray900, // 12.1:1
    secondaryFixed = CdGray200,
    onSecondaryFixed = CdGray900, // 12.1:1
    secondaryFixedDim = CdGray300,
    onSecondaryFixedVariant = CdGray900, // 9.8:1
    // tertiary = the orange cta / accent — use sparingly (see readme)
    tertiary = CdRal2004,
    onTertiary = CdRal9005, // 5.6:1
    tertiaryContainer = CdOrange100,
    onTertiaryContainer = CdOrange800, // 7.8:1
    tertiaryFixed = CdOrange400,
    onTertiaryFixed = CdRal9005, // 8.4:1
    tertiaryFixedDim = CdRal2004,
    onTertiaryFixedVariant = CdRal9005, // 5.6:1
    // error — on the red ramp (red:600/100 light, red:200/900 dark)
    error = CdRed600,
    onError = CdRal9016, // 6.1:1
    errorContainer = CdRed100,
    onErrorContainer = CdRed800, // 10.0:1
    // background & surfaces
    background = Color(0xFFFFFFFF),
    onBackground = CdRal9005, // 19.8:1
    surface = Color(0xFFFFFFFF),
    onSurface = CdRal9005, // 19.8:1
    surfaceVariant = CdRal9016,
    onSurfaceVariant = CdGray600, // 4.8:1
    surfaceDim = CdGray100,
    surfaceBright = Color(0xFFFFFFFF),
    surfaceContainerLowest = Color(0xFFFFFFFF),
    surfaceContainerLow = CdGray50,
    surfaceContainer = CdRal9016,
    surfaceContainerHigh = CdGray100,
    surfaceContainerHighest = CdGray200,
    // outlines
    outline = CdGray500,
    outlineVariant = CdGray200,
    // inverse (snackbars, tooltips)
    inverseSurface = CdGray900,
    inverseOnSurface = CdRal9016,
    inversePrimary = CdOrange400,
    // misc — surface-tint is deliberately css-off: no tint overlays; compose keeps the library default value for compatibility
    scrim = CdRal9005,
    surfaceTint = CdRal9005,
)

// dark scheme
// fixed roles repeat the light values: compose has no css cascade
val CdDarkColors = darkColorScheme(
    // primary = the brand's black action color (buttons, switches, sliders)
    primary = CdRal9016,
    onPrimary = CdRal9005, // 17.3:1
    primaryContainer = CdGray850,
    onPrimaryContainer = CdRal9016, // 11.7:1
    primaryFixed = CdRal7016,
    onPrimaryFixed = CdRal9016, // 9.5:1
    primaryFixedDim = CdGray700,
    onPrimaryFixedVariant = CdRal9016, // 7.2:1
    // secondary = muted grey for less prominent actions
    secondary = CdGray400,
    onSecondary = CdGray950, // 7.8:1
    secondaryContainer = CdGray700,
    onSecondaryContainer = CdGray100, // 7.2:1
    secondaryFixed = CdGray200,
    onSecondaryFixed = CdGray900, // 12.1:1
    secondaryFixedDim = CdGray300,
    onSecondaryFixedVariant = CdGray900, // 9.8:1
    // tertiary = the orange cta / accent — use sparingly (see readme)
    tertiary = CdOrange400,
    onTertiary = CdRal9005, // 8.4:1
    tertiaryContainer = CdOrange900,
    onTertiaryContainer = CdOrange300, // 7.6:1
    tertiaryFixed = CdOrange400,
    onTertiaryFixed = CdRal9005, // 8.4:1
    tertiaryFixedDim = CdRal2004,
    onTertiaryFixedVariant = CdRal9005, // 5.6:1
    // error — on the red ramp (red:600/100 light, red:200/900 dark)
    error = CdRed200,
    onError = CdRed900, // 7.4:1
    errorContainer = CdRed900,
    onErrorContainer = CdRed200, // 7.4:1
    // background & surfaces
    background = CdGray950,
    onBackground = CdRal9016, // 16.0:1
    surface = CdGray950,
    onSurface = CdRal9016, // 16.0:1
    surfaceVariant = CdGray900,
    onSurfaceVariant = CdGray400, // 6.6:1
    surfaceDim = CdRal9005,
    surfaceBright = CdGray900,
    surfaceContainerLowest = CdRal9005,
    surfaceContainerLow = CdGray950,
    surfaceContainer = CdGray900,
    surfaceContainerHigh = CdGray850,
    surfaceContainerHighest = CdGray800,
    // outlines
    outline = CdGray500,
    outlineVariant = Color(0xFF3A3F42),
    // inverse (snackbars, tooltips)
    inverseSurface = CdRal9016,
    inverseOnSurface = CdGray900,
    inversePrimary = CdRal2004,
    // misc — surface-tint is deliberately css-off: no tint overlays; compose keeps the library default value for compatibility
    scrim = CdRal9005,
    surfaceTint = CdRal9016,
)
