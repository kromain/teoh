#ifndef AUDIOANALYZER_H
#define AUDIOANALYZER_H

#include <QObject>
#include <QScopedPointer>

class AudioAnalyzer : public QObject
{
    Q_OBJECT
    Q_DISABLE_COPY(AudioAnalyzer)

    Q_PROPERTY(int notificationThreshold READ notificationThreshold WRITE setNotificationThreshold NOTIFY notificationThresholdChanged )
    Q_PROPERTY(int alarmThreshold READ alarmThreshold WRITE setAlarmThreshold NOTIFY alarmThresholdChanged )
    Q_PROPERTY(int alarmTriggerPeriod READ alarmTriggerPeriod WRITE setAlarmTriggerPeriod NOTIFY alarmTriggerPeriodChanged )

    Q_PROPERTY(bool active READ isActive NOTIFY activeChanged)
    Q_PROPERTY(int peakValue READ peakValue NOTIFY peakValueChanged)

public:
    explicit AudioAnalyzer(QObject *parent = 0);
    ~AudioAnalyzer();

    int notificationThreshold() const;
    void setNotificationThreshold( int threshold );
    int alarmThreshold() const;
    void setAlarmThreshold( int threshold );
    int alarmTriggerPeriod() const;
    void setAlarmTriggerPeriod( int period );

    bool isActive() const;
    int peakValue() const;

public slots:
    void startCapture();
    void stopCapture();

signals:
    void notifyTriggered();
    void alarmTriggered();

    void notificationThresholdChanged();
    void alarmThresholdChanged();
    void alarmTriggerPeriodChanged();

    void activeChanged();
    void peakValueChanged(int peakValue);

private:
    class Private;
    QScopedPointer<Private> d;

    Q_PRIVATE_SLOT(d, void readSamples())
};

#endif // AUDIOANALYZER_H
