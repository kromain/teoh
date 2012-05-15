import QtQuick 1.1
import com.nokia.meego 1.0

PageStackWindow {
    id: appWindow

    Component.onCompleted: theme.inverted = true;

    initialPage: mainPage

    MainPage { id: mainPage }
    TransmitterSettings { id: txSettingsPage }
    ReceiverSettings { id: rxSettingsPage }
}
