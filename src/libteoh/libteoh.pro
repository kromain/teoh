TEMPLATE = lib
DESTDIR = ../../lib
win32:CONFIG(debug, debug|release) {
    TARGET = teohd
} else {
    TARGET = teoh
}

CONFIG += static

QT += network
contains(MEEGO_EDITION,harmattan) {
    CONFIG += mobility
    MOBILITY = multimedia
} else {
    QT += multimedia
}

HEADERS += \
    libteoh.h.in \
    audioanalyzer.h \
    avstreamer.h \
    avreceiver.h

SOURCES += \
    audioanalyzer.cpp \
    avstreamer.cpp \
    avreceiver.cpp

QMAKE_SUBSTITUTES = $$PWD/libteoh.h.in
