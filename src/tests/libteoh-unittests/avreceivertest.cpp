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

void ReceiverTest::testConnection()
{
    AVReceiver avr;

    QCOMPARE(avr.state(), AVReceiver::Connecting);
}
