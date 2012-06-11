TEMPLATE = subdirs

# no harmattan scope it seems :-(
contains(MEEGO_EDITION,harmattan):SUBDIRS += harmattan/teohbmharmattan.pro
else:SUBDIRS += desktop/teohbmdesktop.pro
