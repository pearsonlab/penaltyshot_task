# encodes physics of ball and bar
import numpy as np
from psychopy import logging

def update_ball(t, ball, settings):
    # update ball coordinates
    x, y = ball.pos
    ball.history.append((t, x, y))

    # Only let the ball move once enough time has passed
    if t > settings['BallPauseStart']:
        jx, jy = ball.joystick.CalibratedJoystickAxes()
        ball.jhistory.append((t, jx, jy))

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
        ball.setPos((new_x, new_y), log=False)
    else:
        ball.jhistory.append((t, 0., 0.))  # i.e., "disallow joystick input"


def update_bar(t, bar, settings):
    # update bar coordinates
    x, y = bar.pos
    bar.history.append((t, x, y))
    jx, jy = bar.joystick.CalibratedJoystickAxes()
    bar.jhistory.append((t, jx, jy))

    # check conditions under which bar accelerates
    accel = 1.0  # default to 1.0

    # now check if we need to change
    if len(bar.history) > 2:
        y_prev = bar.history[-1][2]
        y_pprev = bar.history[-2][2]
        y_ppprev = bar.history[-3][2]
        logging.log(level=logging.DEBUG, msg='previous y: ({}, {}, {})'.format(y_ppprev, y_pprev, y_prev))

        # check whether or not y coordinate has changed over the last two frames
        has_moved = not np.isclose(y_pprev, y_prev)
        # and whether movements have been in same direction
        same_direction = np.sign(y_prev - y_pprev) == np.sign(y_pprev - y_ppprev)
        if has_moved and same_direction:
            if np.isclose(np.abs(jy), 1, atol=0.2):  # if |jy| > 0.8
                # increase acceleration
                accel = bar.accel[-1] + settings['BarJoystickAccelIncr']
                logging.log(level=logging.DEBUG, msg='accel = {}'.format(accel))

    bar.accel.append(accel)

    # set maximum move
    maxmove = accel * settings['BarJoystickBaseSpeed']
    bar.maxmove.append(maxmove)

    # update bar
    W, H = settings['ScreenRect']
    barlen = settings['BarLength']
    new_y = y + maxmove * jy

    # don't let it run off the screen
    new_y = max(-H/2. + barlen/2., min(new_y, H/2. - barlen/2.))

    bar.setPos((x, new_y), log=False)
