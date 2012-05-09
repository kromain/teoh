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
        width: settingsPage.width
        anchors.top: pageHeader.bottom
        anchors.bottom: settingsPage.bottom

        model: settingsModel
        delegate: ListDelegate {}

        section.property: "settingCategory"
        section.criteria: ViewSection.FullString
        section.delegate: GroupHeader {
            text: section
        }
    }

    ListModel {
        id: settingsModel
        ListElement {
            title: "Notification Threshold"
            subtitle: "Set noise threshold for notifications"
            settingCategory: "Emitter"
        }

        ListElement {
            title: "Notification duration"
            subtitle: "Set broadcast duration for notifications"
            settingCategory: "Emitter"
        }
        ListElement {
            title: "Alarm delay"
            subtitle: "Set duration before triggering alarms"
            settingCategory: "Receiver"
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
