# encodes physics of ball and bar
import numpy as np

def update_ball(t, ball, settings):
    # update ball coordinates
    # t is time within trial
    # ball is the ball stim

    # Only let the ball move once enough time has passed
    if t > settings['BallPauseStart']:
        x, y = ball.pos
        jx, jy = ball.joystick.CalibratedJoystickAxes()
        W, H = settings['ScreenRect']

        # update x (constant velocity)
        # Don't let it move outside the screen
        new_x = max(-W/2., min(x + settings['BallSpeed'], W/2.))

        # update y
        # BallJoystickPosition will lie between -1 and 1, so we multiply that
        # value by BallSpeed to get the amount it actually moves
        # in a given direction (this ensures that the ball's max
        # vertical speed is the same as its horizontal
        # speed). Also, we don't want to allow any of the ball
        # off the screen.
        new_y = max(-H/2. + settings['BallRadius'], min(y + settings['BallSpeed'] * jy, H/2 - settings['BallRadius']))
        ball.pos = (new_x, new_y)


def update_bar(t, bar, settings):
    # update bar coordinates
    # t is time within trial
    # bar is the bar stim
    pass
