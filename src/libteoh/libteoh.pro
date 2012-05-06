TEMPLATE = lib
TARGET = teoh
DESTDIR = ../../lib

QT += network multimedia
CONFIG += static

HEADERS += \
    avstreamer.h \
    audioanalyzer.h

SOURCES += \
    avstreamer.cpp \
    audioanalyzer.cpp
