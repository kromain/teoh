#include "audioanalyzer.h"

#include <QAudioInput>
#include <QTime>
#include <QDebug>

class AudioAnalyzer::Private
{
    AudioAnalyzer* q;
public:
    Private( AudioAnalyzer* _q ) : q(_q) {}

    void readSamples();

    void setPeakValue( int );

    QAudioInput* audioInput;
    QIODevice*   samplesBuffer;

    int peakValue;

    int notificationThreshold;
    int alarmThreshold;
    int alarmTriggerPeriod;

    QTime alarmPeriod;
};

QDebug& operator <<(QDebug dbg, const QAudioFormat& format);

AudioAnalyzer::AudioAnalyzer(QObject *parent) :
    QObject(parent),
    d(new Private(this))
{
    d->peakValue = 0;
    d->notificationThreshold = 30;
    d->alarmThreshold = 60;
    d->alarmTriggerPeriod = 2;

    QAudioDeviceInfo inputDevice = QAudioDeviceInfo::defaultInputDevice();

    QAudioFormat recordingFormat;
    recordingFormat.setFrequency(8000);
    recordingFormat.setChannels(1);
    recordingFormat.setSampleSize(8);
    recordingFormat.setCodec("audio/pcm");
    recordingFormat.setByteOrder(QAudioFormat::LittleEndian);
    recordingFormat.setSampleType(QAudioFormat::UnSignedInt);
    if (!inputDevice.isFormatSupported(recordingFormat)) {
        recordingFormat = inputDevice.nearestFormat(recordingFormat);
        qWarning() << "recording format not supported, using nearest supported";
    }
    //qDebug() << "Selected recording format:" << recordingFormat;

    d->audioInput = new QAudioInput(inputDevice, recordingFormat, this);
    d->audioInput->setBufferSize(500);
    d->audioInput->setNotifyInterval(500);
    connect( d->audioInput, SIGNAL(notify()), SLOT(readSamples()) );

    d->samplesBuffer = d->audioInput->start();
}

AudioAnalyzer::~AudioAnalyzer()
{
}

int AudioAnalyzer::notificationThreshold() const
{
    return d->notificationThreshold;
}

void AudioAnalyzer::setNotificationThreshold(int threshold)
{
    if ( threshold != d->notificationThreshold ) {
        d->notificationThreshold = threshold;
        emit notificationThresholdChanged();
    }
}

int AudioAnalyzer::alarmThreshold() const
{
    return d->alarmThreshold;
}

void AudioAnalyzer::setAlarmThreshold(int threshold)
{
    if ( threshold != d->alarmThreshold ) {
        d->alarmThreshold = threshold;
        emit alarmThresholdChanged();
    }
}

int AudioAnalyzer::alarmTriggerPeriod() const
{
    return d->alarmTriggerPeriod;
}

void AudioAnalyzer::setAlarmTriggerPeriod(int period)
{
    if ( period != d->alarmTriggerPeriod ) {
        d->alarmTriggerPeriod = period;
        emit alarmTriggerPeriodChanged();
    }
}

bool AudioAnalyzer::isActive() const
{
    return d->audioInput->state() == QAudio::ActiveState;
}

int AudioAnalyzer::peakValue() const
{
    return d->peakValue;
}

void AudioAnalyzer::startCapture()
{
    d->audioInput->resume();
    emit activeChanged();
}

void AudioAnalyzer::stopCapture()
{
    d->audioInput->suspend();
    d->alarmPeriod = QTime();

    d->setPeakValue(0);

    emit activeChanged();
}

void AudioAnalyzer::Private::readSamples()
{
    QByteArray samples = samplesBuffer->readAll();
    //qDebug() << "Read" << samples.count() << "samples";

    int newPeak = 0;
    Q_FOREACH( quint8 sample, samples ) {
        newPeak = qMax( qAbs(static_cast<int>(sample)-127), newPeak );
    }
    setPeakValue(newPeak);
}

void AudioAnalyzer::Private::setPeakValue( int pv )
{
    if ( pv != peakValue ) {
        peakValue = pv;
        emit q->peakValueChanged(peakValue);
    }

    if ( alarmPeriod.isNull() ) {
        if ( peakValue >= alarmThreshold )
            alarmPeriod.start();
        else if ( peakValue >= notificationThreshold )
            emit q->notifyTriggered();
    } else if ( alarmPeriod.elapsed() >= alarmTriggerPeriod * 1000/*ms*/ ) {
        emit q->alarmTriggered();
    }
}

#include "moc_audioanalyzer.cpp"
