#ifndef AVRECEIVER_H
#define AVRECEIVER_H

#include <QObject>
#include <QScopedPointer>

class AVReceiver : public QObject
{
    Q_OBJECT
    Q_DISABLE_COPY(AVReceiver)

public:
    explicit AVReceiver(QObject *parent = 0);
    ~AVReceiver();

private:
    class Private;
    QScopedPointer<Private> d;

    Q_PRIVATE_SLOT( d, void socketError() )
    Q_PRIVATE_SLOT( d, void dataReceived() )
};

#endif // AVRECEIVER_H
