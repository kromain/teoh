from pytest import skip
from skynet import SkynetTestCase, DS


class TestPSTestCase1(SkynetTestCase):
    @classmethod
    def setUpClass(cls):
        print("setUpClass1")
        skip("nope")

    @classmethod
    def tearDownClass(cls):
        print("tearDownClass1")

    def test_something1(self):
        print("test_something1")
        self.target.dualshock.press_buttons([DS.RIGHT, DS.LEFT])

    def test_somethingelse1(self):
        print("test_somethingelse1")
