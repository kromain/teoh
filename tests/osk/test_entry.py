#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import os
import pytest

from skynet import DS


@pytest.fixture(scope="module")
def osk_test_setup(regicam_webview):
    # Replace the regicam app with the test page
    testfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "keyevent.html")
    html = ''.join([x[:-1] for x in open(testfile).readlines()])
    regicam_webview.webview.execute_script("document.getElementsByTagName('html')[0].innerHTML = \'%s\';" % html)

    return regicam_webview


@pytest.mark.parametrize("elem_id,osk_text,osk_type,osk_lang", [
                         ("1", "Default BASIC test", "latin_basic", "en_"),
                         ("2", "Default TEXT test", "text", "en_"),
                         ("11", "name@email.com", "email", "en_"),
                         ("12", "password123", "password", "en_"),
                         ("13", "5105553854", "numeric", ""),
                         ("3", "Wie geht's dir/ Ihnen?", "latin_basic", "de_"),
                         ("4", "Wie geht's dir/ Ihnen?", "text", "de_"),
                         ("5", "Kak pazhivayesh?", "latin_basic", "ru_"),
                         ("6", "Как поживаешь?", "text", "ru_"),
                         ("7", "Ogenki desuka?", "latin_basic", "ja_"),
                         ("8", "こんばんは。おですか？", "text", "ja_"),
                         ("9", "Mucho gusto Encantado", "latin_basic", "es_"),
                         ("10", "Cómo está usted?", "text", "es_"),
                         ])
def test_osk_input(osk_test_setup, elem_id, osk_text, osk_type, osk_lang):
    """ Basic test for entry_osk """
    ps = osk_test_setup.osk
    ds = osk_test_setup.dualshock
    browser = osk_test_setup.webview

    elem = browser.find_element_by_id(elem_id)
    assert elem

    elem.click()
    ds.press_button(DS.CROSS, timetorelease=1)
    ps.entry_osk(osk_text, osk_type, osk_lang)
    assert elem.get_attribute('value') == osk_text
