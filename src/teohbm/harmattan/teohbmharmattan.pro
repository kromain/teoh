TEMPLATE = app
TARGET = Teoh-Harmattan
DESTDIR = ../../../bin

# Add more folders to ship with the application, here
folder_01.source = qml/teohbmharmattan
folder_01.target = qml
DEPLOYMENTFOLDERS = folder_01

# Additional import path used to resolve QML modules in Creator's code model
QML_IMPORT_PATH =

CONFIG += mobility
MOBILITY = multimedia

# Speed up launching on MeeGo/Harmattan when using applauncherd daemon
CONFIG += qdeclarative-boostable

include(../../libteoh.pri)

SOURCES += main.cpp

# Please do not modify the following two lines. Required for deployment.
include(qmlapplicationviewer/qmlapplicationviewer.pri)
qtcAddDeployment()
