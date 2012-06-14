TEMPLATE = app

QT       -= gui
QT       += network multimedia testlib

# unneeded and annoying with QtCreator
#CONFIG   += console
CONFIG   -= app_bundle

include(../../libteoh.pri)

SOURCES += \
    main.cpp \
    avreceivertest.cpp

HEADERS += \
    avreceivertest.h
