#include "qmlapplicationviewer.h"

#include <audioanalyzer.h>
#include <avstreamer.h>

#include <QApplication>
#include <QDeclarativeEngine>
#include <QDeclarativeContext>

Q_DECL_EXPORT int main(int argc, char *argv[])
{
    QScopedPointer<QApplication> app(createApplication(argc, argv));

    AudioAnalyzer audioAnalyzer;
    AVStreamer avStreamer;

    QmlApplicationViewer viewer;
    viewer.setOrientation(QmlApplicationViewer::ScreenOrientationAuto);

    viewer.engine()->rootContext()->setContextProperty("audioAnalyzer", &audioAnalyzer);
    viewer.engine()->rootContext()->setContextProperty("avStreamer", &avStreamer);
    viewer.setMainQmlFile( QLatin1String("qml/teohbmharmattan/main.qml") );
    viewer.showExpanded();

    return app->exec();
}
