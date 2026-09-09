package de.madebytimo.corporatedesign

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// generated from tokens.json by generate.py
// status/link colors live outside the m3 ColorScheme; pick per mode
private val successLight = Color(0xFF256E43)
private val successDark = Color(0xFF8FD5A8)
private val onSuccessLight = Color(0xFFF1F0EA)
private val onSuccessDark = Color(0xFF0F2A19)
private val successContainerLight = Color(0xFFD9EDE0)
private val successContainerDark = Color(0xFF1D4630)
private val onSuccessContainerLight = Color(0xFF1E5330)
private val onSuccessContainerDark = Color(0xFFC4EBD2)
private val warningLight = Color(0xFF8A5A00)
private val warningDark = Color(0xFFFFD48A)
private val onWarningLight = Color(0xFFF1F0EA)
private val onWarningDark = Color(0xFF2E2000)
private val warningContainerLight = Color(0xFFF7ECD0)
private val warningContainerDark = Color(0xFF46380F)
private val onWarningContainerLight = Color(0xFF5C3F00)
private val onWarningContainerDark = Color(0xFFFFE1A0)
private val infoLight = Color(0xFF005387)
private val infoDark = Color(0xFFAAD4EE)
private val onInfoLight = Color(0xFFF1F0EA)
private val onInfoDark = Color(0xFF092434)
private val infoContainerLight = Color(0xFFE4EFF7)
private val infoContainerDark = Color(0xFF083754)
private val onInfoContainerLight = Color(0xFF083754)
private val onInfoContainerDark = Color(0xFFAAD4EE)
private val linkLight = Color(0xFF954216)
private val linkDark = Color(0xFFFF8A3D)
private val linkHoverLight = Color(0xFF723615)
private val linkHoverDark = Color(0xFFEBBEA5)

data class CdSemanticColors(
    val success: Color,
    val onSuccess: Color,
    val successContainer: Color,
    val onSuccessContainer: Color,
    val warning: Color,
    val onWarning: Color,
    val warningContainer: Color,
    val onWarningContainer: Color,
    val info: Color,
    val onInfo: Color,
    val infoContainer: Color,
    val onInfoContainer: Color,
    val link: Color,
    val linkHover: Color,
)

@Composable
fun cdSemanticColors(darkTheme: Boolean = isSystemInDarkTheme()): CdSemanticColors {
    return if (darkTheme) CdSemanticColors(
        success = successDark,
        onSuccess = onSuccessDark,
        successContainer = successContainerDark,
        onSuccessContainer = onSuccessContainerDark,
        warning = warningDark,
        onWarning = onWarningDark,
        warningContainer = warningContainerDark,
        onWarningContainer = onWarningContainerDark,
        info = infoDark,
        onInfo = onInfoDark,
        infoContainer = infoContainerDark,
        onInfoContainer = onInfoContainerDark,
        link = linkDark,
        linkHover = linkHoverDark,
    ) else CdSemanticColors(
        success = successLight,
        onSuccess = onSuccessLight,
        successContainer = successContainerLight,
        onSuccessContainer = onSuccessContainerLight,
        warning = warningLight,
        onWarning = onWarningLight,
        warningContainer = warningContainerLight,
        onWarningContainer = onWarningContainerLight,
        info = infoLight,
        onInfo = onInfoLight,
        infoContainer = infoContainerLight,
        onInfoContainer = onInfoContainerLight,
        link = linkLight,
        linkHover = linkHoverLight,
    )
}

