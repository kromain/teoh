from pytest import mark
from skynet import SkynetTestCase, DS

incvar = 0

class SkynetTestCase2(SkynetTestCase):
    @classmethod
    def setUpClass(cls):
        print("setupClass2")

    @classmethod
    def tearDownClass(cls):
        print("tearDownClass2")

    def setUp(self):
        # self.skip("test")
        print("setUp2")

    def tearDown(self):
        print("tearDown2")

    def test_something2(self):
        print("test_something2")
        self.target.dualshock.press_buttons([DS.RIGHT, DS.LEFT])
        print(self.target.webview.title)

    def test_somethingelse2(self):
        global incvar
        incvar += 1
        assert incvar == 3
        print("test_somethingelse2")
        print(self.target.webview.title)

    @mark.skipif(True, reason="just because")
    def test_skipped(self):
        print("test_skipped")

    def test_skipped_partly(self):
        print("test_skipped_partly")
        print(self.target.webview.title)

        self.skip("skipped partly")
        assert False, "this shouldn't be reached"
