TEMPLATE = lib
DESTDIR = ../../lib
win32:CONFIG(debug, debug|release) {
    TARGET = teohd
} else {
    TARGET = teoh
}

QT += network multimedia
CONFIG += static

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
