TEMPLATE = lib
TARGET = teoh
DESTDIR = ../../lib

CONFIG += static mobility
QT       += network
MOBILITY = multimedia

HEADERS += \
    avstreamer.h \
    audioanalyzer.h

SOURCES += \
    avstreamer.cpp \
    audioanalyzer.cpp
