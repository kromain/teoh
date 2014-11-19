from pytest import mark
from skynet import SkynetTestCase, DS


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

    def test_somethingelse2(self):
        print("test_somethingelse2")

    @mark.skipif(True, reason="just because")
    def test_skipped(self):
        print("test_skipped")

    def test_skipped_partly(self):
        print("test_skipped_partly")

        self.skip("skipped partly")
        assert False, "this shouldn't be reached"
