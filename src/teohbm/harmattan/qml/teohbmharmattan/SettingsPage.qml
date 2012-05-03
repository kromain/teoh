import QtQuick 1.1
import com.nokia.meego 1.0

Page {
    width: 100

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
