import QtQuick 1.1
import com.nokia.meego 1.0

Image {
    property string text : ""

    width: parent.width
    height: screen.platformWidth < screen.platformHeight ? UiConstants.HeaderDefaultHeightPortrait
                                         : UiConstants.HeaderDefaultHeightLandscape
    source: "image://theme/meegotouch-view-header-fixed" + (theme.inverted ? "-inverted" : "")
    z: 1

    Label {
        id: label
        anchors {
            fill: parent
            topMargin: screen.platformWidth < screen.platformHeight ? UiConstants.HeaderDefaultTopSpacingPortrait
                                                    : UiConstants.HeaderDefaultTopSpacingLandscape
            bottomMargin: screen.platformWidth < screen.platformHeight ? UiConstants.HeaderDefaultBottomSpacingPortrait
                                                       : UiConstants.HeaderDefaultBottomSpacingLandscape
            rightMargin: UiConstants.DefaultMargin
            leftMargin: UiConstants.DefaultMargin
        }
        font: UiConstants.HeaderFont
        text: parent.text
    }
}
