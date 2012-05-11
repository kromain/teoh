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
        spacing: UiConstants.DefaultMargin

        model: VisualItemModel {
            GroupHeader {
                text: "Notifications"
            }
            ListItem {
                title: "Trigger Level"
                subtitle: "Noise level to trigger notifications"

                Slider {
                    minimumValue: 0
                    maximumValue: 127
                    value: audioAnalyzer.notificationThreshold
                    onValueChanged: audioAnalyzer.notificationThreshold = value
                }
            }
            ListItem {
                title: "Broadcast Duration"
                subtitle: avStreamer.notificationDuration + "s"
                icon: "icon-m-textinput-combobox-arrow"

                onClicked: durationSelection.open();
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
                title: "Trigger Level"
                subtitle: "Noise level to trigger alarms"

                Slider {
                    minimumValue: 0
                    maximumValue: 127
                    value: audioAnalyzer.alarmThreshold
                    onValueChanged: audioAnalyzer.alarmThreshold = value
                }
            }
            ListItem {
                title: "Trigger Period"
                subtitle: audioAnalyzer.alarmTriggerPeriod + "s"
                icon: "icon-m-textinput-combobox-arrow"

                onClicked: periodSelection.open();
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

    SelectionDialog {
        id: periodSelection
        titleText: "Alarm period:"

        model: ListModel {
            ListElement { name: "0s"; value: 0 }
            ListElement { name: "1s"; value: 1 }
            ListElement { name: "2s"; value: 2 }
            ListElement { name: "3s"; value: 3 }
        }

        onAccepted: audioAnalyzer.alarmTriggerPeriod = model.get(selectedIndex).value;
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
