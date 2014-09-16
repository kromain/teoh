import sys, time

from skynet.deci.dualshock import DualShock, Buttons

#run on dashboard on video icon (or any with at least 4 to the left)
press = 0.04
release = 0.04
with DualShock(target_ip=sys.argv[1], force=True) as controller:
    for i in range(100):
        controller.press_buttons([Buttons.LEFT] * 1 + [Buttons.RIGHT] * 1, timetopress=press, timetorelease=release)
        controller.press_buttons([Buttons.LEFT] * 2 + [Buttons.RIGHT] * 2, timetopress=press, timetorelease=release)
        controller.press_buttons([Buttons.LEFT] * 3 + [Buttons.RIGHT] * 3, timetopress=press, timetorelease=release)
        controller.press_buttons([Buttons.LEFT] * 4 + [Buttons.RIGHT] * 4, timetopress=press, timetorelease=release)
