#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.
import string

from skynet.osk.latin_basic import BasicLatinOsk

class PasswordOsk(BasicLatinOsk):
    """
    Creates password mode SDK 
    Handles mapping of password keyboard

    locale - The expected keyboard locale, default is English. 
    """
    def __init__(self, locale):
    	
        super(PasswordOsk,self).__init__(locale)
        self.graph = "password"

