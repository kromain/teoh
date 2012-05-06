TEMPLATE = subdirs

# no harmattan scope it seems :-(
contains(MEEGO_EDITION,harmattan):SUBDIRS += harmattan/teohbmharmattan.pro
win32:SUBDIRS += desktop/teohbmdesktop.pro
