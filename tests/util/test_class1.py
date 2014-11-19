from skynet import SkynetTestCase, DS


class SkynetTestCase1(SkynetTestCase):
    @classmethod
    def setUpClass(cls):
        print("setUpClass1")
        cls.skip("nope")

    @classmethod
    def tearDownClass(cls):
        print("tearDownClass1")

    def test_something1(self):
        print("test_something1")
        self.target.dualshock.press_buttons([DS.RIGHT, DS.LEFT])

    def test_somethingelse1(self):
        print("test_somethingelse1")
