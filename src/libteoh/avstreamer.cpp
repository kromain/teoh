#include "avstreamer.h"

#include <QTimer>
#include <QAudioInput>
#include <QHostAddress>
#include <QUdpSocket>
#include <QNetworkInterface>

class AVStreamer::Private
{
    AVStreamer* q;
public:
    Private( AVStreamer* _q ) : q(_q) {}

    void socketError();
    void dataSent(qint64 bytes);

    QAudioInput* audioInput;

    int notificationDuration;

    QUdpSocket*  streamSocket;
};

QDebug& operator <<(QDebug dbg, const QAudioFormat& format)
{
    return dbg << format.channelCount() << "channel(s)," << format.sampleRate() << "Hz," << format.sampleSize() << "bits," << format.sampleType() << "int/uint/float," << format.byteOrder() << "BE/LE";
}

AVStreamer::AVStreamer(QObject *parent) :
    QObject(parent),
    d(new Private(this))
{
    d->notificationDuration = 5;

    d->streamSocket = new QUdpSocket(this);
    connect( d->streamSocket, SIGNAL(error(QAbstractSocket::SocketError)), SLOT(socketError()) );
    connect( d->streamSocket, SIGNAL(bytesWritten(qint64)), SLOT(dataSent(qint64)) );
#if QT_VERSION >=0x040800
    d->streamSocket->setSocketOption(QAbstractSocket::MulticastTtlOption, 1);
    d->streamSocket->connectToHost( QHostAddress("239.51.67.81"), 2012 );
#else
    d->streamSocket->connectToHost( QHostAddress::Broadcast, 2012 );
#endif
    d->streamSocket->waitForConnected();

    QAudioDeviceInfo defaultInputDevice = QAudioDeviceInfo::defaultInputDevice();

    QAudioFormat recordingFormat;
    recordingFormat.setFrequency(8000);
    recordingFormat.setChannels(1);
    recordingFormat.setSampleSize(8);
    recordingFormat.setCodec("audio/pcm");
    recordingFormat.setByteOrder(QAudioFormat::LittleEndian);
    recordingFormat.setSampleType(QAudioFormat::UnSignedInt);
    if (!defaultInputDevice.isFormatSupported(recordingFormat)) {
        recordingFormat = defaultInputDevice.nearestFormat(recordingFormat);
        qWarning() << "recording format not supported, using nearest supported";
    }
    //qDebug() << "Selected recording format:" << recordingFormat;

    d->audioInput = new QAudioInput(recordingFormat, this);
    d->audioInput->start(d->streamSocket);
    d->audioInput->resume();
    d->audioInput->suspend();
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
    d->audioInput->resume();
}

void AVStreamer::stopStreaming()
{
    d->audioInput->suspend();
}

void AVStreamer::Private::socketError()
{
    qWarning() << "Broadcasting error:" << streamSocket->errorString();
    // TODO better error handling, use a direct TCP socket instead?
}

void AVStreamer::Private::dataSent(qint64 bytes)
{
    qDebug() << "Wrote" << bytes << "bytes (AudioInput state:" << audioInput->error() << ")";
}

#include "moc_avstreamer.cpp"
