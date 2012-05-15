import QtQuick 1.1
import com.nokia.meego 1.0
import QtMobility.feedback 1.1

Page {

    TabGroup {
        id: tabGroup
        currentTab: txTab

       Page {
           id: txTab

           PageHeader {
               id: txPageHeader
               anchors.top: txTab.top
               text: qsTr("Transmitter")
           }

           Item {
               anchors.top: txPageHeader.bottom
               anchors.bottom: txTab.bottom
               anchors.left: txTab.left
               anchors.right: txTab.right

               Column {
                   anchors.verticalCenter: parent.verticalCenter
                   width: parent.width
                   spacing: UiConstants.DefaultMargin

                   Button {
                       width: parent.width
                       text: (audioAnalyzer.active ? qsTr("Stop ") : qsTr("Start ")) + qsTr("Monitoring")
                       onClicked: {
                           if ( audioAnalyzer.active )
                               audioAnalyzer.stopCapture();
                           else
                               audioAnalyzer.startCapture();

                           avStreamer.stopStreaming();
                       }
                   }
                   Label {
                       font: UiConstants.HeaderFont
                       anchors.topMargin: UiConstants.DefaultMargin
                       anchors.horizontalCenter: parent.horizontalCenter
                       color: audioAnalyzer.active ? "#ffffff" : "#d2d2d2"
                       text: audioAnalyzer.active ? qsTr("Listening...") : qsTr("Stopped")

                   }
               }
           }

       }

       Page {
           id: rxTab

           PageHeader {
               id: rxPageHeader
               anchors.top: rxTab.top
               text: qsTr("Receiver")
           }

           Item {
               anchors.top: rxPageHeader.bottom
               anchors.bottom: rxTab.bottom
               anchors.left: rxTab.left
               anchors.right: rxTab.right

               Column {
                   anchors.verticalCenter: parent.verticalCenter
                   width: parent.width
                   spacing: UiConstants.DefaultMargin

                   Button{
                       width: parent.width
                       text: "Listen"
                       checkable: true
                       onClicked: {
                           if ( checked )
                               audioAnalyzer.stopCapture();
                           else
                               audioAnalyzer.startCapture();
                       }
                   }
                   ProgressBar {
                       width: parent.width
                       minimumValue: 0
                       maximumValue: 127
                       value: audioAnalyzer.peakValue
                   }
                   Label {
                       font: UiConstants.HeaderFont
                       anchors.topMargin: UiConstants.DefaultMargin
                       anchors.horizontalCenter: parent.horizontalCenter
                       text: "TODO"
                   }
               }
           }

//           HapticsEffect {
//               id: vibrationEffect
//               duration: 3000
//               period: 1000
//               intensity: 1.0
//               attackIntensity: 0.0
//               attackTime: 250
//               fadeIntensity: 0.0
//               fadeTime: 250
//           }
       }
    }

    tools: ToolBarLayout {
        ToolIcon {
            iconId: "toolbar-settings"
            onClicked: pageStack.push( tabGroup.currentTab == rxTab ? rxSettingsPage : txSettingsPage )
        }
        ButtonRow {
            TabButton {
                text: qsTr("Transmitter")
                tab: txTab
            }
            TabButton {
                text: qsTr("Receiver")
                tab: rxTab
            }
        }
        ToolIcon {
           iconId: "toolbar-view-menu"
           onClicked: (myMenu.status === DialogStatus.Closed) ? myMenu.open() : myMenu.close()
        }
    }

    Menu {
        id: myMenu
        MenuLayout {
            MenuItem { text: qsTr("Sample menu item") }
        }
    }

}
