import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

Page {
    id: rxSettingsPage

    PageHeader {
        id: pageHeader
        anchors.top: rxSettingsPage.top
        text: "Receiver Settings"
    }

    ListView {
        id: settingsList
        anchors.top: pageHeader.bottom
        anchors.bottom: rxSettingsPage.bottom
        anchors.left: rxSettingsPage.left
        anchors.right: rxSettingsPage.right
        anchors.margins: UiConstants.DefaultMargin
        spacing: UiConstants.DefaultMargin

        model: VisualItemModel {
            GroupHeader {
                text: "Notifications"
            }
            ListItem {
                title: "Show Banner"
                subtitle: "Show a system banner for notifications"
                onOff: true
            }

            GroupHeader {
                text: "Alarms"
            }
            ListItem {
                title: "Show Popup"
                subtitle: "Show a popup window for alarms"
                onOff: true
            }
            ListItem {
                title: "Vibrate Phone"
                subtitle: "Vibrate the phone during alarms"
                onOff: true
            }
        }
    }

    tools: ToolBarLayout {
        ToolIcon {
            iconId: "toolbar-back"
            onClicked: pageStack.pop()
        }
        ToolIcon {
            iconId: "toolbar-add"
            onClicked: addSheet.open()
        }
        ToolIcon {
            iconId: "toolbar-delete"
        }
        ToolIcon {
            iconId: "toolbar-list"
        }
    }

    Sheet {
        id: addSheet

        acceptButtonText: qsTr("Add");
        rejectButtonText: qsTr("Cancel");
    }
}
