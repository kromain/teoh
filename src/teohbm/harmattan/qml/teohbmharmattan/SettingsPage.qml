import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

Page {
    id: settingsPage

    PageHeader {
        id: pageHeader
        anchors.top: settingsPage.top
        text: "Settings"
    }

    ListView {
        id: settingsList
        anchors.top: pageHeader.bottom
        anchors.bottom: settingsPage.bottom
        anchors.left: settingsPage.left
        anchors.right: settingsPage.right
        anchors.margins: UiConstants.DefaultMargin

        model: VisualItemModel {
            GroupHeader {
                text: "Notifications"
            }
            ListItem {
                title: "Trigger Level"
                subtitle: "Noise level to start broadcast"

                Slider {
//                    width: settingsList.width
                    minimumValue: 0
                    maximumValue: 127
                    value: audioAnalyzer.notificationThreshold
                }
            }
            ListItem {
                title: "Broadcast duration"
                subtitle: avStreamer.notificationDuration + "s"
                icon: "icon-m-textinput-combobox-arrow"

                onClicked: durationSelection.open();
            }
        }
    }

    SelectionDialog {
        id: durationSelection
        titleText: "Broadcast duration:"

        model: ListModel {
            ListElement { name: "5s"; value: 5 }
            ListElement { name: "10s"; value: 10 }
            ListElement { name: "15s"; value: 15 }
            ListElement { name: "20s"; value: 20 }
            ListElement { name: "25s"; value: 25 }
            ListElement { name: "30s"; value: 30 }
        }

        onAccepted: avStreamer.notificationDuration = model.get(selectedIndex).value;
    }

    ListModel {
        id: settingsModel
        ListElement {
            title: "Notification Threshold"
            subtitle: "Set noise threshold for notifications"
            settingCategory: "Notification"
        }

        ListElement {
            title: "Notification duration"
            subtitle: "Set broadcast duration for notifications"
            settingCategory: "Emitter"
        }
        ListElement {
            title: "Alarm delay"
            subtitle: "Set duration before triggering alarms"
            settingCategory: "Alarm"
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
