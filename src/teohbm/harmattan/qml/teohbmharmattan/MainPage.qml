import QtQuick 1.1
import com.nokia.meego 1.0
import QtMobility.feedback 1.1

Page {

    TabGroup {
        id: tabGroup
        currentTab: monitorTab

       Page {
           id: monitorTab

           Column {
               anchors.fill: parent
               spacing: 50

               Label {
                   font: UiConstants.HeaderFont
                   anchors.topMargin: UiConstants.DefaultMargin
                   anchors.horizontalCenter: parent.horizontalCenter
                   id: statusLabel
                   text: "Listening..."

               }
               ProgressBar {
                   width: parent.width
                   minimumValue: 0
                   maximumValue: 127
                   value: audioAnalyzer.peakValue
               }
               Slider {
                   width: parent.width
                   minimumValue: 0
                   maximumValue: 127
                   value: audioAnalyzer.notificationThreshold
               }
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

               Connections {
                   target: audioAnalyzer
                   onNotifyTriggered: {
                       statusLabel.text = "Sound detected!";
                       avStreamer.startStreaming();
                   }
                   onAlarmTriggered: {
                       statusLabel.text = "ALARM !!!";
//                       vibrationEffect.start();
                       avStreamer.startStreaming();
                   }
               }
//               HapticsEffect {
//                   id: vibrationEffect
//                   duration: 3000
//                   period: 1000
//                   intensity: 1.0
//                   attackIntensity: 0.0
//                   attackTime: 250
//                   fadeIntensity: 0.0
//                   fadeTime: 250
//               }
           }
       }

       Page {
           id: receiverTab

           ProgressBar {
               width: parent.width
               minimumValue: 0
               maximumValue: 256
               value: audioAnalyzer.peakValue
           }

           Button{
               anchors.centerIn: parent
               text: (audioAnalyzer.active ? qsTr("Stop ") : qsTr("Start ")) + qsTr("Listening")
               onClicked: {
                   if ( audioAnalyzer.active )
                       audioAnalyzer.stopCapture();
                   else
                       audioAnalyzer.startCapture();
               }
           }
       }
    }

    tools: ToolBarLayout {
        ToolIcon {
            iconId: "toolbar-settings"
            onClicked: pageStack.push( settingsPage )
        }
        ButtonRow {
            TabButton {
                text: qsTr("Monitor")
                tab: monitorTab
            }
            TabButton {
                text: qsTr("Receiver")
                tab: receiverTab
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
