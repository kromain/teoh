isEmpty( LIBTEOH_SRCDIR ):LIBTEOH_SRCDIR=$$PWD/libteoh
!exists( $$LIBTEOH_SRCDIR/libteoh.h.in ):error( "Cannot find libteoh.h.in in $$LIBTEOH_SRCDIR" )

isEmpty( LIBTEOH_BUILDDIR ):LIBTEOH_BUILDDIR=$$OUT_PWD/../../libteoh
!exists( $$LIBTEOH_BUILDDIR/libteoh.h ):error( "Cannot find libteoh.h in $$LIBTEOH_BUILDDIR" )

INCLUDEPATH += $$LIBTEOH_SRCDIR
DEPENDPATH += $$LIBTEOH_SRCDIR

LIBS += -L$$LIBTEOH_BUILDDIR/../../lib
win32:CONFIG(debug, debug|release) {
    LIBS += -lteohd
    POST_TARGETDEPS += $$LIBTEOH_BUILDDIR/../../lib/teohd.lib
} else {
    LIBS += -lteoh
    win32:POST_TARGETDEPS += $$LIBTEOH_BUILDDIR/../../lib/teoh.lib
    else:POST_TARGETDEPS += $$LIBTEOH_BUILDDIR/../../lib/libteoh.a
}

CONFIG += have_libteoh
DEFINES += HAVE_LIBTEOH

QT += network
contains(MEEGO_EDITION,harmattan) {
    CONFIG += mobility
    MOBILITY = multimedia
} else {
    QT += multimedia
}
