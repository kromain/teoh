#include "avreceiver.h"

#include <QAudioOutput>
#include <QAudioFormat>
#include <QAudioDeviceInfo>
#include <QUdpSocket>

class AVReceiver::Private
{
    AVReceiver* q;
public:
    Private( AVReceiver* _q ) : q(_q) {}

    void socketError();
    void dataReceived();

    QUdpSocket* socket;
    QAudioOutput* audioOutput;
    QIODevice* audioBuffer;
};

AVReceiver::AVReceiver(QObject *parent) :
    QObject(parent),
    d( new Private(this) )
{
    d->socket = new QUdpSocket(this);
    d->socket->bind(2012);
#if QT_VERSION >=0x040800
    d->socket->setSocketOption(QAbstractSocket::MulticastTtlOption, 1);
    d->socket->joinMulticastGroup( QHostAddress("239.51.67.81") );
#endif

    connect( d->socket, SIGNAL(readyRead()), SLOT(dataReceived()) );
    connect( d->socket, SIGNAL(error(QAbstractSocket::SocketError)), SLOT(socketError()) );

    QAudioFormat audioFormat;
    audioFormat.setFrequency(8000);
    audioFormat.setChannels(1);
    audioFormat.setSampleSize(8);
    audioFormat.setCodec("audio/pcm");
    audioFormat.setByteOrder(QAudioFormat::LittleEndian);
    audioFormat.setSampleType(QAudioFormat::UnSignedInt);

    QAudioDeviceInfo outputDevice = QAudioDeviceInfo::defaultOutputDevice();
    if (!outputDevice.isFormatSupported(audioFormat)) {
        audioFormat = outputDevice.nearestFormat(audioFormat);
        qWarning() << "recording format not supported, using nearest supported";
    }
    //qDebug() << "Selected recording format:" << audioFormat;

    d->audioOutput = new QAudioOutput(outputDevice, audioFormat, this);
    d->audioBuffer = d->audioOutput->start();
}

AVReceiver::~AVReceiver()
{
}

AVReceiver::State AVReceiver::state() const
{
    return Connecting;
}

void AVReceiver::Private::dataReceived()
{
    QByteArray data;
    while( socket->hasPendingDatagrams() ) {
        QByteArray datagram;
        datagram.resize(socket->pendingDatagramSize());
        socket->readDatagram(datagram.data(), datagram.size());
        if (data.isEmpty())
            data = datagram;
        else
            data.append(datagram);
    }
    qDebug() << "Received" << data.count() << "bytes (socket status:" << socket->errorString() << ")";

    audioBuffer->write(data);
    audioOutput->resume();
}

void AVReceiver::Private::socketError()
{
    qWarning() << "socket error:" << socket->error() << socket->errorString();
    // TODO better error handling
}

#include "moc_avreceiver.cpp"
