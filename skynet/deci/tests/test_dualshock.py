from skynet.deci.dualshock import DualShock,Buttons


def test_Buttons():
    """ Ensure all the expected defines exist, all refer to a single bit, and there are no duplicates """

    expected = ["UP", "LEFT", "RIGHT", "DOWN", "R1", "L1", "R2", "L2", "CROSS", "CIRCLE", "SQUARE", "TRIANGLE", "OPTION", "SHARE", "PS"]
    
    keymap = {}
    allbits = 0
    for b in expected:
        assert Buttons[b]
        assert Buttons[b].value not in keymap, "Multiple flags with same bit"
        assert bin(Buttons[b].value).count('1') == 1, "More than one bit in flag"
        keymap[Buttons[b].value] = True

    for b in dir(Buttons):
        if b[0] != "_":
            assert b in expected

def test_Dualshock():
    with DualShock(target_ip="43.138.15.26") as controller:
        assert controller


    controller = DualShock(target_ip="43.138.15.26")
    assert controller

    controller.start()

    controller.stop()

