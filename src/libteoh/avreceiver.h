#ifndef AVRECEIVER_H
#define AVRECEIVER_H

#include <QObject>
#include <QScopedPointer>

class AVReceiver : public QObject
{
    Q_OBJECT
    Q_DISABLE_COPY(AVReceiver)

    Q_PROPERTY(State state READ state NOTIFY stateChanged)
    Q_ENUMS(State)
public:

    enum State {
        Connecting   = 0x01,
        Connected    = 0x10,
        Standby      = 0x11,
        Listening    = 0x12,
        Notification = 0x14,
        Alarm        = 0x18,
        Reconnecting = 0x20,
        Disconnected = 0x80
    };

    explicit AVReceiver(QObject *parent = 0);
    ~AVReceiver();

    State state() const;

Q_SIGNALS:
    void stateChanged();

private:
    class Private;
    QScopedPointer<Private> d;

    Q_PRIVATE_SLOT( d, void initializeConnection() )
    Q_PRIVATE_SLOT( d, void finalizeConnection() )
    Q_PRIVATE_SLOT( d, void socketError() )
    Q_PRIVATE_SLOT( d, void dataReceived() )
};

#endif // AVRECEIVER_H
