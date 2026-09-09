package de.madebytimo.corporatedesign

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue

// theme switching analog of theme.ts: pass darkTheme=false to force light,
// darkTheme=true to force dark, default follows the system setting.
// persistence is the app's job (compose has no localStorage): hoist the choice
// into rememberCdThemeState, store changes via onThemeChange and feed them
// back as initial on the next launch, e.g. with dataStore.
@Composable
fun CdTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    MaterialTheme(
        colorScheme = if (darkTheme) CdDarkColors else CdLightColors,
        typography = CdTypography,
        shapes = CdShapes,
        content = content,
    )
}

// observable theme choice + toggle, theme.ts-style
class CdThemeState(
    initial: Boolean,
    private val onChange: (Boolean) -> Unit,
) {
    var isDark: Boolean by mutableStateOf(initial)
        private set

    fun set(dark: Boolean) {
        isDark = dark
        onChange(dark)
    }

    fun toggle() = set(!isDark)
}

/** creates toggleable theme state; persist via onThemeChange (e.g. dataStore). */
@Composable
fun rememberCdThemeState(
    initial: Boolean = isSystemInDarkTheme(),
    onThemeChange: (Boolean) -> Unit = {},
): CdThemeState {
    val currentOnChange by rememberUpdatedState(onThemeChange)
    return remember { CdThemeState(initial) { dark -> currentOnChange(dark) } }
}

@Composable
fun CdTheme(
    state: CdThemeState,
    content: @Composable () -> Unit,
) {
    CdTheme(darkTheme = state.isDark, content = content)
}
