# First check qmake variable, then environment variable, then use default
  isEmpty( LIBTEOHDIR ):LIBTEOHDIR=$$(LIBTEOHDIR)
  isEmpty( LIBTEOHDIR ):LIBTEOHDIR=$$PWD/libteoh
  !isEmpty( LIBTEOHDIR ) {
    !exists( $$LIBTEOHDIR/avstreamer.h ):error( "Cannot find avstreamer.h in $$LIBTEOHDIR" )
    unix:!exists( $$LIBTEOHDIR/../../lib/libteoh.a ):error( "Cannot find libteoh.a in $$LIBTEOHDIR/../../lib" )
    win32:!exists( $$LIBTEOHDIR/../../lib/libteoh.lib ):error( "Cannot find libteoh[d].lib in $$LIBTEOHDIR/../../lib" )

    INCLUDEPATH += $$LIBTEOHDIR
    DEPENDPATH += $$LIBTEOHDIR

    LIBS += -L$$LIBTEOHDIR/../../lib
    win32:CONFIG(debug, debug|release) {
        LIBS += -lteohd
    } else {
        LIBS += -lteoh
    }

    CONFIG += have_libteoh
    DEFINES += HAVE_LIBTEOH

  } else {
    warning( "LibTeoh not found! Please set LIBTEOHDIR either as an environment variable or on the qmake command line")
  }
