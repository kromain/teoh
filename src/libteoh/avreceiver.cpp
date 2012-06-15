#include "avreceiver.h"

#include <QAudioOutput>
#include <QAudioFormat>
#include <QAudioDeviceInfo>
#include <QTcpSocket>
#include <QUdpSocket>
#include <QStateMachine>
#include <QState>
#include <QHistoryState>
#include <QFinalState>
#include <QTimer>

namespace {
    const char* STATE_ID = "stateId";
    const int CONNECTION_TIMEOUT_S = 10;
}

class AVReceiver::Private
{
    AVReceiver* q;
public:
    Private( AVReceiver* _q ) : q(_q) {}

    void initializeConnection();
    void finalizeConnection();
    void socketError();
    void dataReceived();

    QTcpSocket* connectionSocket;
    QUdpSocket* streamingSocket;

    QHostAddress streamerAddress;

    QAudioOutput* audioOutput;
    QIODevice* audioBuffer;

    QTimer* connectionTimer;

    QStateMachine* stateMachine;
};

AVReceiver::AVReceiver(QObject *parent) :
    QObject(parent),
    d( new Private(this) )
{
    d->connectionSocket = new QTcpSocket(this);
    d->streamingSocket = new QUdpSocket(this);
    d->streamingSocket->bind(2012);
#if QT_VERSION >=0x040800
    d->streamingSocket->setSocketOption(QAbstractSocket::MulticastTtlOption, 1);
    d->streamingSocket->joinMulticastGroup( QHostAddress("239.51.67.81") );
#endif

    connect( d->streamingSocket, SIGNAL(readyRead()), SLOT(dataReceived()) );
    connect( d->streamingSocket, SIGNAL(error(QAbstractSocket::SocketError)), SLOT(socketError()) );

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

    d->connectionTimer = new QTimer(this);
    d->connectionTimer->setInterval(CONNECTION_TIMEOUT_S * 1000);
    d->connectionTimer->setSingleShot(true);

    d->stateMachine = new QStateMachine(this);

    QState* connectingState = new QState;
    connectingState->setProperty(STATE_ID, Connecting);
    QState* connectedState = new QState;
    connectedState->setProperty(STATE_ID, Connected);
    QState* reconnectingState = new QState;
    reconnectingState->setProperty(STATE_ID, Reconnecting);
    QFinalState* disconnectedState = new QFinalState;
    disconnectedState->setProperty(STATE_ID, Disconnected);
    QState* standbyState = new QState(connectedState);
    standbyState->setProperty(STATE_ID, Standby);
    connectedState->setInitialState(standbyState);
    QState* listeningState = new QState(connectedState);
    listeningState->setProperty(STATE_ID, Listening);
    QState* notificationState = new QState(connectedState);
    notificationState->setProperty(STATE_ID, Notification);
    QState* alarmState = new QState(connectedState);
    alarmState->setProperty(STATE_ID, Alarm);
    QHistoryState* historyState = new QHistoryState(connectedState);
    historyState->setDefaultState(standbyState);

    d->stateMachine->addState(connectingState);
    d->stateMachine->addState(connectedState);
    d->stateMachine->addState(reconnectingState);
    d->stateMachine->addState(disconnectedState);
    d->stateMachine->setInitialState(connectingState);

    connectingState->addTransition(d->connectionSocket, SIGNAL(connected()), connectedState);
    connectingState->addTransition(d->connectionTimer, SIGNAL(timeout()), disconnectedState);
    connectingState->addTransition(d->connectionSocket, SIGNAL(error(QAbstractSocket::SocketError)), disconnectedState);
    connectedState->addTransition(d->connectionSocket, SIGNAL(error(QAbstractSocket::SocketError)), reconnectingState);
    reconnectingState->addTransition(d->connectionSocket, SIGNAL(connected()), historyState);
    reconnectingState->addTransition(d->connectionTimer, SIGNAL(timeout()), disconnectedState);

    Q_FOREACH( QAbstractState* s, d->stateMachine->findChildren<QAbstractState*>() ) {
        connect(s, SIGNAL(entered()), this, SIGNAL(stateChanged()));
    }

    connect( connectingState, SIGNAL(entered()), this, SLOT(initializeConnection()) );
    d->stateMachine->start();
}

AVReceiver::~AVReceiver()
{
}

AVReceiver::State AVReceiver::state() const
{
    QAbstractState* foundState = 0;
    Q_FOREACH( QAbstractState* s, d->stateMachine->configuration() ) {
        foundState = s;
        // ensure we use the child state if we have nested states
        if ( s->parentState() )
            break;
    }

    return foundState ? static_cast<State>(foundState->property(STATE_ID).toInt()) : Disconnected;
}

void AVReceiver::Private::initializeConnection()
{
    // Broadcast a message on the LAN to find the emitter
    streamingSocket->writeDatagram( "PING", QHostAddress::Broadcast, 2011 );
    // We'll timeout after 10s if we don't receive an answer
    connectionTimer->start();
}

void AVReceiver::Private::finalizeConnection()
{
    connectionTimer->stop();
    // set up the tcp connection to the streamer
    connectionSocket->connectToHost(streamerAddress, 2011);
}

void AVReceiver::Private::dataReceived()
{
    QByteArray data;
    QHostAddress senderAddress;
    while( streamingSocket->hasPendingDatagrams() ) {
        QByteArray datagram;
        datagram.resize(streamingSocket->pendingDatagramSize());
        streamingSocket->readDatagram(datagram.data(), datagram.size(), &senderAddress);
        if (data.isEmpty())
            data = datagram;
        else
            data.append(datagram);
    }
    qDebug() << "Received" << data.count() << "bytes (socket status:" << streamingSocket->errorString() << ")";

    switch( q->state() ) {

    case Connecting:
        if ( data.startsWith("PONG") ) {
            // yay, we got our answer from the streamer,
            // we can now set up the real connection using the tcp socket
            streamerAddress = senderAddress;
            finalizeConnection();
        } else {
            // hmm that was not what we expected, just ignore
            // (could be broadcast streaming)
        }
        break;

    case Listening:
    case Notification:
    case Alarm:
        audioBuffer->write(data);
        audioOutput->resume();
        break;

    default:
        qWarning() << "Ignoring data from emitter (not in a ready state)";
        break;
    }

}


void AVReceiver::Private::socketError()
{
    qWarning() << "socket error:" << streamingSocket->error() << streamingSocket->errorString();
    // TODO better error handling
}

#include "moc_avreceiver.cpp"
