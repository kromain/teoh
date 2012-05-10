import QtQuick 1.1
import com.nokia.meego 1.0

Item {
    default property alias contents: labels.data

    signal clicked

    property alias title: titleLabel.text
    property alias subtitle: subtitleLabel.text
    property string icon: ""

    width: parent.width
    height: container.height

    Image {
        id: background
        anchors.fill: parent
        source: "image://theme/meegotouch-list-fullwidth-" + (theme.inverted? "inverted-" : "") + "background" + (mouseArea.pressed ? "-pressed" : "")
    }

    Item {
        id: container
        height: childrenRect.height
        width: parent.width

        Column {
            id: labels
            Label {
                id: titleLabel
                font: UiConstants.TitleFont
                color: "#ffffff"
                text: "Title"

                visible: text.length > 0
            }
            Label {
                id: subtitleLabel
                font: UiConstants.SubtitleFont
                color: "#d2d2d2"
                text: "Subtitle"

                visible: text.length > 0
            }
        }
        Image {
            id: iconImage
            anchors.right: parent.right
            anchors.verticalCenter: labels.verticalCenter
            source: (icon.length ? "image://theme/" + icon : "")

            visible: icon.length
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        enabled: iconImage.visible

        onClicked: parent.clicked();
    }
}
