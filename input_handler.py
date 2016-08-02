import numpy as np
from psychopy import visual, core, event
from psychopy.hardware import joystick

class JoystickServer(object):
    # This small class handles getting input from the joysticks.
    # On initialization, it opens the joystick
    # and sets the properties.
    #
    # To use, call JoystickServer (all variables are required). Then, call
    # CalibratedJoystickAxes to get the value of from the left joystick to
    # use. CalibratedJoystickAxes
    # sets anything within the DeadZone to zero before returning; this is
    # what is often wanted for use. NOTE that this value will always be
    # between -1 and 1 (where -1 is the farthest down/left the joystick
    # can be pressed and 1 is the farthest up/right), so it's up to you to
    # multiply this value by your "speed"
    #
    # JoystickEscape is used in place of 'escape' or 'q' during the game
    # due to problems with the keyboard and PsychoPy when a joystick is
    # being used. The specific button used doesn't matter, as long as
    # the participant isn't likely to hit it on accident. Use joystick_universal
    # demo in PsychoPy to test joystick button numbers.

    def __init__(self, JoystickNum, JoystickDeadZone):
        # The number of the joystick. Joystick numbers seem to be 0-indexed
        # and increase monotonically. This is used to switch between players
        # for Ball and Bar in 'Vs' mode.
        # JoystickNum

        self.JoystickNum = JoystickNum
        self.joy = joystick.Joystick(self.JoystickNum)
        self.JoystickDeadZone = JoystickDeadZone

    def JoystickEscape(self):
        # Number 5 corresponds to the Upper Right trigger on the F310 gamepad
        escapeCheck = self.joy.getButton(5)
        return escapeCheck

    def CalibratedJoystickAxes(self):
        # Return the processed joystick axes. We
        # zero them if they're within the
        # DeadZone. This is the function that's most commonly used.
        XX, YY = self.joy.getX(), -self.joy.getY()

        if abs(XX) < self.JoystickDeadZone:
            XX = 0
        if abs(YY) < self.JoystickDeadZone:
            YY = 0

        CalibratedJoystickAxesResult = XX, YY

        return CalibratedJoystickAxesResult
