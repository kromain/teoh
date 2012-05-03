#include "avstreamer.h"

class AVStreamer::Private
{
    AVStreamer* q;
public:
    Private( AVStreamer* _q ) : q(_q) {}

    int notificationDuration;
};

AVStreamer::AVStreamer(QObject *parent) :
    QObject(parent),
    d(new Private(this))
{
    d->notificationDuration = 5;
}

AVStreamer::~AVStreamer()
{
}

int AVStreamer::notificationDuration() const
{
    return d->notificationDuration;
}

void AVStreamer::setNotificationDuration(int duration)
{
    if ( duration != d->notificationDuration ) {
        d->notificationDuration = duration;
        emit notificationDurationChanged();
    }
}

void AVStreamer::startStreaming()
{
}

void AVStreamer::stopStreaming()
{
}

#include "moc_avstreamer.cpp"
