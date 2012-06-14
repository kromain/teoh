#include "avreceivertest.h"

#include <avreceiver.h>
#include <QtTest>

ReceiverTest::ReceiverTest()
{
}

void ReceiverTest::initTestCase()
{
}

void ReceiverTest::cleanupTestCase()
{
}

void ReceiverTest::testConnectionFailure()
{
    AVReceiver avr;
    QSignalSpy stateChangedSignalSpy( &avr, SIGNAL(stateChanged()) );
    int signalCount = 0;

    // We're in disconnected state initially, before the SM is up
    QCOMPARE(avr.state(), AVReceiver::Disconnected);

    // to initialize the internal SM
    QCoreApplication::processEvents();

    QCOMPARE(stateChangedSignalSpy.count(), ++signalCount);
    QCOMPARE(avr.state(), AVReceiver::Connecting);

    // wait for 10s connection timeout
    QTest::qWait(12000); // add a couple of seconds to make sure the timeout is received

    QCOMPARE(stateChangedSignalSpy.count(), ++signalCount);
    QCOMPARE(avr.state(), AVReceiver::Disconnected);
}
