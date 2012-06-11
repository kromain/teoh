
#include "receivertest.h"

#include <QtTest>
#include <QCoreApplication>
#include <QVector>

int main(int argc, char *argv[])
{
    QCoreApplication app(argc, argv);

    QVector<QObject*> tests;
    tests << new ReceiverTest;

    int returnCode = 0;
    Q_FOREACH( QObject* test, tests) {
        returnCode += QTest::qExec(test, argc, argv);
    }
    return returnCode;
}
