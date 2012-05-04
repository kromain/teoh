#ifndef AVSTREAMER_H
#define AVSTREAMER_H

#include <QObject>
#include <QScopedPointer>

class AVStreamer : public QObject
{
    Q_OBJECT
    Q_DISABLE_COPY(AVStreamer)

    Q_PROPERTY(int notificationDuration READ notificationDuration WRITE setNotificationDuration NOTIFY notificationDurationChanged )

public:
    explicit AVStreamer(QObject *parent = 0);
    ~AVStreamer();

    int notificationDuration() const;
    void setNotificationDuration( int duration );

public slots:
    void startStreaming();
    void stopStreaming();

signals:
    void notificationDurationChanged();

private:
    class Private;
    QScopedPointer<Private> d;

    Q_PRIVATE_SLOT( d, void socketError() )
    Q_PRIVATE_SLOT( d, void dataSent(qint64) )
};

#endif // AVSTREAMER_H
