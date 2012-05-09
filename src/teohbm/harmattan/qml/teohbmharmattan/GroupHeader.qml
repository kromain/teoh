import QtQuick 1.1
import com.nokia.meego 1.0

Item {
    id: groupHeader

    property string text : ""

    width: parent.width
    height: UiConstants.GroupHeaderHeight

    Image {
        anchors {
            left: groupHeader.left
            verticalCenter: groupHeader.verticalCenter
            right: sectionName.left
            rightMargin: UiConstants.DefaultMargin
        }

        source: "image://theme/meegotouch-groupheader" + (theme.inverted ? "-inverted" : "") + "-background"
    }
    Label {
        id: sectionName
        anchors {
            verticalCenter: groupHeader.verticalCenter
            right: groupHeader.right
        }

        font: UiConstants.GroupHeaderFont
        text: groupHeader.text
        color: "#8c8c8c"
    }
}

