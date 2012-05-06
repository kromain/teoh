#include <QApplication>

#include "mainwindow.h"

#include <avreceiver.h>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    
    AVReceiver receiver;

    MainWindow w;
    w.show();

    return a.exec();
}
