#ifndef AVRECEIVERTEST_H
#define AVRECEIVERTEST_H

#include <QObject>

class ReceiverTest : public QObject
{
    Q_OBJECT

public:
    ReceiverTest();

private Q_SLOTS:
    void initTestCase();
    void cleanupTestCase();
    void testConnectionFailure();
};

#endif // AVRECEIVERTEST_H
