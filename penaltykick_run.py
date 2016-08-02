import numpy as np
from psychopy import gui, visual, event, core
import sys
import os
import json
from input_handler import JoystickServer
from goalie_wrapper import computer_goalie
import random
import pygame
from utils import flicker

# Penalty Kick game by Jean-Francois Gariepy, overhauled by Bill
# Broderick. Python version from John Pearson's lab.
#
# This script corresponds to one run of the Penalty Kick game, for one
# subject. It is called by wrapper_penaltykick.py and passed a Settings
# class, the SubjName of the current subject, the currentRun, and the
# display window we're showing things on. This script should *not* be
# run directly, as all of the commands to set up the screen are in
# wrapper_penaltykick.py.
#
# This script loops through a certain number of runs (specified in
# Settings) and creates a Results list which stores all of the
# variables we care about for the results (path of the ball, path of
# the bar, outcome, etc.). This Results list is multidimensional,
# with one dictionary for each trial. It is saved after each run, but that
# path it's stored at is specified by the date, SubjName, and runType,
# so one call to this script will write to the same file
# several times.
#
# This script returns the Results list (so the outcomes and
# opponents can be extracted for overall win percentages) as well as
# escapeCheck, a boolean that specifies whether the experimenter
# pressed escape during play. When escape is pressed, we save
# everything, return from this script immediately (assuming we're not
# in the middle of a WaitSecs command), close the screen,
# and exit. Otherwise, wrapper will
# calculate the overall win percentages and display them to the
# user.
#
# Note also that this function does not open or close any screens;
# that's handled by the Wrapper.

def drawFixationCross(win, Settings):
    # This function draws a fixation cross in the center of the given
    # screen.
    #
    # win: which window to draw the fixation cross on
    #
    # Settings: the Settings struct, used because it contains the origin
    # of the display
    fixation = visual.TextStim(win, text='+',
                                alignHoriz='center',
                                alignVert='center', units='norm',
                                pos=(0, 0), height=0.3,
                                color=[255, 255, 255], colorSpace='rgb255',
                                wrapWidth=2)
    fixation.draw()
    win.flip()

def text_draw(win, text):
    # This function is used to set autoDraw as True,
    # since joystick positions are only updated when the
    # screen flips (which would otherwise wipe the text off).
    # This function is most relevant for the beginning of each run,
    # when the run doesn't begin until the participant provides some input.
    display_text = visual.TextStim(win, text=text,
                                   font='Helvetica', alignHoriz='center',
                                   alignVert='center', units='norm',
                                   pos=(0, 0), height=0.1,
                                   color=[255, 255, 255], colorSpace='rgb255',
                                   wrapWidth=2)
    display_text.autoDraw=True

    return display_text

def playGame(Settings, Results, BallJoystick, BarJoystick, win, trial):
    # This function is a giant while loop that continues until a result is
    # reached: either via the ball crossing the final line or the ball
    # hitting the goalie. At that point, the Results struct is
    # returned. It takes the Settings, the two Joysticks, the Results
    # struct, the current window and the experiment log as inputs. It
    # initializes all the relevant variables (BallY/X, BarY/X) in this
    # function. It updates TimingSequence, BarY, BallPositions,
    # BallJoystickHistory, and BarJoystickHistory each iteration of the
    # loop and will add the outcome, trialLength, and trialStart to the
    # Results struct.


    # Initialize the trial-related variables.

    BallX, BallY = Settings.BallStartingPosX, Settings.BallStartingPosY
    BarX, BarY = Settings.BarStartingPosX, Settings.BarStartingPosY
    Results[trial]['StartOfGame'] =  core.getTime() - Results[trial]['runStart']
    escapeCheck = False
    accel = 1.0

    # If the goalie has a lag, we record it.
    try:
        Results[trial]['CpuBarLagThisTrial'] = Results[trial]['goalie'].LagThisTrial
    except AttributeError:
        pass

    # Here, we set the tolerance for the comparison between the goalie's
    # most recent move and their maxMove (if the goalie's most
    # recent move is within tolerance of their maxMove, then
    # acceleration increases, otherwise it stays constant).
    # For cpu, the tolerance
    # is 1e-12, which is the default (because with cpu, we're
    # just dealing with small precision errors).
    if Results[trial]['Opponent'] == 'human':
        tol = 1e-1
    elif Results[trial]['Opponent'] == 'cpu':
        tol = 1e-12

    flicker(win, 127)

    while Results[trial]['outcome'] == 0:
        # First, check to see if the user wants to quit
        escapeCheck = BallJoystick.JoystickEscape()

        if escapeCheck:
            return Results, escapeCheck

        # Extract the position of the ball joystick
        BallJoystickPosition = BallJoystick.CalibratedJoystickAxes()
        # Only let the ball move once enough time has passed
        if Results[trial]['trialLength'] > Settings.BallPauseStart:
            # Don't let it move outside the screen
            BallX = max(-Settings.ScreenRect[0]/2., min(BallX + Settings.BallSpeed, Settings.ScreenRect[0]/2.))
            # BallJoystickPosition will lie between -1 and 1, so we multiply that
            # value by BallSpeed to get the amount it actually moves
            # in a given direction (this ensures that the ball's max
            # vertical speed is the same as its horizontal
            # speed). Also, we don't want to allow any of the ball
            # off the screen.
            BallY = max(-Settings.ScreenRect[1]/2.+Settings.BallRadius, min(BallY + Settings.BallSpeed*BallJoystickPosition[1], Settings.ScreenRect[1]/2 - Settings.BallRadius))

        # If the trial has been going on for long enough to check, the
        # goalie's moving, and it's moving in the same direction we
        # were during the last refresh, accelerate. We use
        # np.isclose here because precision errors may make them
        # trivially different.
        if len(Results[trial]['BarY'])>=3.0 and not np.isclose(Results[trial]['BarY'][-1], Results[trial]['BarY'][-2]) and np.sign(Results[trial]['BarY'][-1]-Results[trial]['BarY'][-2]) == np.sign(Results[trial]['BarY'][-2]-Results[trial]['BarY'][-3]):
            if Results[trial]['Opponent'] == 'cpu':
                # We only increase accel if they used their max
                # move, otherwise it stays the same. This is to
                # prevent "teleportations" when the goalie's
                # strategy changes. For computers, we're only
                # dealing with small precision errors.
                if np.isclose(Results[trial]['maxMove'][-1], abs(Results[trial]['BarY'][-1]-Results[trial]['BarY'][-2]), atol=tol):
                    accel = accel + Settings.BarJoystickAccelIncr
            elif Results[trial]['Opponent'] == 'human':
                # When the human is controlling the goalie, we're not only dealing
                # with precision errors, but also issues getting input
                # from the controller. To deal
                # with this, instead of looking at the move, which
                # will vary in magnitude much more, we look at the
                # joystick input, since that's where the issue
                # originates. We then increment accel when the
                # joystick input is in [-1, -.8] or [.8, 1] instead of
                # just when its 1 or -1. This should hopefully make
                # acceleration more consistent. I'm (Bill) less worried about
                # the "teleportation" with the human goalie and more
                # about them being unable to accelerate, so setting
                # larger and larger tolerance values here is fine.
                if np.isclose(abs(Results[trial]['BarJoystickHistory'][-1]),1, atol=0.2).any():
                    accel = accel + Settings.BarJoystickAccelIncr
        # Otherwise, reset the acceleration value
        else:
            accel = 1.0
        Results[trial]['accel'].append(accel)

        # The maxMove value here is the magnitude of the largest possible move
        # the bar could make. Since BarJoystickPosition will lie
        # between -1 and 1, it will be the percentage of the largest
        # possible move. This is also used for the computer, to
        # determine how far it can go in one step.
        maxMove = accel*Settings.BarJoystickBaseSpeed
        Results[trial]['maxMove'].append(maxMove)

        # if the goalie is 'human', update the bar position according to the
        # joystick position of Player 2, similar to how we updated
        # the positions of the ball
        if Results[trial]['Opponent'] == 'human':
            BarJoystickPosition = BarJoystick.CalibratedJoystickAxes() # Joystick
            # Get the bar position from the joystick.
            BarY = BarY + maxMove*BarJoystickPosition[1] # Joystick
        else:
            # If the goalie is 'cpu', we don't do anything with the
            # BarJoystick. But we still put values here so we can
            # update Results.BarJoystickHistory
            BarJoystickPosition = [0, 0]
            # if this is false, then there hasn't been any movement to respond to
            # (and the calls to computer_goalie would throw an error).
            if np.array(Results[trial]['BallPositions']).shape[1] > 0.:
                BarY, Results[trial]['goalie'], new_dest = computer_goalie(Results[trial]['goalie'], Results[trial]['BarY'][-1], maxMove, Results[trial]['BallPositions'][1], Results[trial]['BallPositions'][0], Results[trial]['TimingSequence'])
                Results[trial]['dest'].append(new_dest)

        # We don't want to allow any of the bar off the screen.
        BarY = max(-Settings.ScreenRect[1]/2+Settings.BarLength/2, min(BarY, Settings.ScreenRect[1]/2 - Settings.BarLength/2))

        W=Settings.ScreenRect[0]
        H=Settings.ScreenRect[1]

        # Draw the Ball
        ball = visual.Circle(win, radius=Settings.BallRadius, fillColor='red', lineColor='red')
        ball.pos = [BallX, BallY]
        ball.draw()

        # Draw Bar
        barVertices = [ [-Settings.BarWidth/2., Settings.BarLength/2.],
                        [Settings.BarWidth/2., Settings.BarLength/2.],
                        [Settings.BarWidth/2., -Settings.BarLength/2.],
                        [-Settings.BarWidth/2., -Settings.BarLength/2.] ]

        bar = visual.ShapeStim(win,vertices=barVertices,fillColor='blue', lineColor='blue')
        bar.pos = [BarX, BarY]
        bar.draw()

        # Draw Final Line
        line = visual.Line(win, start=(Settings.FinalLine, H/2.), end=(Settings.FinalLine, -H/2.))
        line.draw()

        # Check how long the game has gone on for. Need to subtract both
        # Results.StartOfGame and Results.runStart to get the
        # amount of time (in seconds) passed since Results.StartOfGame
        Results[trial]['trialLength'] = core.getTime() - Results[trial]['runStart'] - Results[trial]['StartOfGame']

        # Check for result conditions
        if BallX+Settings.BallRadius >= BarX-Settings.BarWidth/2. and BallX-Settings.BallRadius <= BarX+Settings.BarWidth/2. and BallY+Settings.BallRadius > BarY-Settings.BarLength/2. and BallY-Settings.BallRadius < BarY+Settings.BarLength/2:
            Results[trial]['outcome'] = 'loss'
            # With the parameter clearBuffer set to False, the display will not be
            # overwritten at the next flip, allowing us to add text
            # saying "win" over the final state of the game
            win.flip(clearBuffer=False)
        elif BallX+Settings.BallRadius > Settings.FinalLine:
            Results[trial]['outcome'] = 'win'
            # With the parameter clearBuffer set to False, the display will not be
            # overwritten at the next flip, allowing us to add text
            # saying "win" over the final state of the game
            win.flip(clearBuffer=False)
        else:
            # Refresh the screen.
            win.flip()

        # Update the timing, position, and joystick variables.
        Results[trial]['TimingSequence'].append(core.getTime() - Results[trial]['runStart'] - Results[trial]['trialStart'])
        Results[trial]['BarY'].append(BarY)
        Results[trial]['BallPositions'] = np.append(Results[trial]['BallPositions'], [[BallX],[BallY]], axis=1)
        Results[trial]['BallJoystickHistory'] = np.append(Results[trial]['BallJoystickHistory'], [[BallJoystickPosition[0]], [BallJoystickPosition[1]]],axis=1)
        Results[trial]['BarJoystickHistory'] = np.append(Results[trial]['BarJoystickHistory'], [[BarJoystickPosition[0]], [BarJoystickPosition[1]]],axis=1)

    flicker(win, 170)

    return Results, escapeCheck

def Penaltykick_run(Settings, SubjName, currentRun, DisplayWindow, goalie):
    # Main function call.
    #
    # Arguments:
    #
    #  - Settings: class, contains the various settings necessary to run
    #    the task. These relate to the joysticks, screen, speed, reward
    #    and everything. Note that these will all be the same for a given
    #    call to Wrapper (most likely, a given subject) and the subset of
    #    variables that are constant across all calls are saved
    #    as the first line of the json file for each participant.
    # 	 The entire Settings struct is saved
    #    along with the Results.
    #
    #  - SubjName: string, the name of the current subject. Can be
    #    anything, used only for determining the save path. Typed in by
    #    the experimenter in Wrapper.
    #
    #  - currentRun: int, the number of the current run. Used for
    #    determining the save path, 'Vs' mode players, and display purposes.
    #
    #  - DisplayWindow: window, from PscyhoPy on which we are
    #    currently drawing everything on.
    #
    #  - goalie: goalie obj, this object is the goalie, with various
    #    properties and methods. It's initialized in the Wrapper so that it
    #    can learn over the course of the subject and to set a couple
    #    trial-independent variables.

    # Connect the gamepads. We do this here (instead of in
    # Wrapper) because if runType is Vs, we switch which joystick
    # controls the bar and which the ball each run.
    BallJoystick = JoystickServer(Settings.BallJoystickNum, Settings.BallJoystickDeadZone)
    if Settings.runType != 'train':
        # We want to allow input from the BarJoystick if runType is not train
        # (in which case they only play against the computer).
        try:
            BarJoystick = JoystickServer(Settings.BarJoystickNum, Settings.BarJoystickDeadZone)
        except pygame.error:
            print "You don't have two joysticks connected!"
            core.quit()
    else:
        # There are instances when we want to pass BarJoystick around. Instead
        # of checking if runType == 'experiment' check everytime,
        # we make sure that BarJoystick is defined and then have the
        # function make the appropriate check.
        BarJoystick = []

    win = DisplayWindow

    escapeCheck = False

    # If runType is Vs, we specify which player is controlling the ball.
    if Settings.runType == 'Vs':
        if currentRun%2 == 0:
            curPlayer = Settings.SubjName
        else:
            curPlayer = Settings.P2Name
        text = "For this run, %s will control the ball." % curPlayer
    else:
        # Otherwise we just say press X or Trigger to begin
        curPlayer = Settings.SubjName
        text = "You will control the ball."

    # This function is used so that window can be flipped to accept Joystick input (later on).
    player_text = text_draw(win, text)
    win.flip()
    core.wait(2)
    player_text.autoDraw = False
    win.flip()
    core.wait(2)


    if Settings.runType == 'Vs':
        text = "%s, press X to begin run %d" % (curPlayer, currentRun+1)
    else:
        text = "Press X to begin run %d" % currentRun+1

    intro_text = text_draw(win, text)
    win.flip()

    # wait for input from participant to begin run
    # Input must be received from player controlling the ball in 'Vs' mode
    while 1:
        win.flip()
        buttons = BallJoystick.joy.getButton(0)
        escapeCheck	= BallJoystick.JoystickEscape()
        if buttons:
            intro_text.autoDraw = False
            break
        elif escapeCheck:
            # need to set Results so we have something to return
            Results = []
            return Results, escapeCheck

    # Draw a fixation cross
    drawFixationCross(win, Settings)

    runStart = core.getTime()

    Results = []

    # This is the loop that goes through each trial in the run.
    for trial in np.arange(Settings.RunLength):

        Results.append({})

        # This is so we don't have to worry about indexing on Results
        # if there's only one dictionary (and setting up all the exceptions for trial 0.
        # It's removed at the end of trial 0.
        if trial == 0:
            Results.append({})

        # These will always be the same.
        Results[trial]['SubjName'] = SubjName
        Results[trial]['BallPlayer'] = curPlayer
        Results[trial]['currentRun'] = currentRun
        Results[trial]['runStart'] = runStart

        # We update goalie every time because (if it's hmm or hmm_pretrain),
        # it will be learning every trial.
        Results[trial]['goalie'] = goalie
        Results[trial]['trial'] = trial

        #Record the start of the trial
        Results[trial]['trialStart'] = core.getTime() - runStart

        win.flip()

        # This resets all the trial-specific variables to their defaults.
        Results[trial]['BarY'] = []
        Results[trial]['BallPositions'] = [[],[]]
        Results[trial]['BallJoystickHistory'] = [[],[]]
        Results[trial]['BarJoystickHistory'] = [[],[]]
        Results[trial]['TimingSequence'] = []
        Results[trial]['RewardBall'] = 0
        Results[trial]['RewardBar'] = 0

        # Fixation Cross -- since we're just using this as something for them
        # to look at, we just have this show up in the center.
        drawFixationCross(win, Settings)

        # Pick the fixation cross duration for this trial and wait that length
        # of time (FixCrossJitterOrder is set in Wrapper). Only matters for 'experiment' trials.
        # Kind of a hold out from fMRI. Might not be necessary in ECoG cases.
        Results[trial]['FixCrossJitterThisTrial'] = Settings.FixCrossJitterOrder[trial]
        core.wait(Results[trial]['FixCrossJitterThisTrial'])
        win.flip()

        #Check to see if escape has been pressed. If it has, return.
        escapeCheck = BallJoystick.JoystickEscape()
        if escapeCheck:
            return Results, escapeCheck

        # Pick the opponent for this trial (OpponentOrder is set in Wrapper).
        Results[trial]['Opponent'] = Settings.OpponentOrder[trial]

        # Display an image specifying which opponent the
        # participant will be playing
        if Settings.runType == 'train':
            myimgfile = 'SmileyFace.jpg'
        else:
            if Results[trial]['Opponent'] == 'human':
                #opponents = [f for f in os.listdir('opponents')
                #		if os.path.isfile(os.path.join('opponents', f))
                #		if f.endswith('.jpg')]
                #myimgfile = 'opponents/'+random.choice(opponents)
                myimgfile = 'SmileyFace.jpg'
            else:
                myimgfile = 'Computer.jpg'

        image = visual.ImageStim(win, image=myimgfile, size=10, units='cm')
        image.draw()
        win.flip()

        core.wait(Settings.TimeToWaitWithOppPic)

        # All of these are initialized here so we can assign the
        # results of this function to Results[trial] (otherwise it
        # gives an error).
        Results[trial]['outcome'] = 0
        Results[trial]['StartOfGame'] = 0
        Results[trial]['trialLength'] = 0
        Results[trial]['CpuBarLagThisTrial'] = 0
        Results[trial]['maxMove'] = []
        Results[trial]['dest'] = []
        Results[trial]['accel'] = []

        win.flip()

        #Check to see if escape has been pressed. If it has, return.
        escapeCheck = BallJoystick.JoystickEscape()

        if escapeCheck:
            return Results, escapeCheck

        win.flip()

        # We call goalie.trial_start to get some trial-specific things set
        # up. for react or guess, this sets the lag for a given
        # trial and updates any learning we're doing. We call it
        # here because we want access to the last trial.
        if trial > 0:
            Results[trial]['goalie'] = Results[trial]['goalie'].trial_start(Results[trial-1]['BallPositions'][0], Results[trial-1]['BallPositions'][1])
        # Only pass the last trial if there was a last trial.
        else:
            Results[trial]['goalie'] = Results[trial]['goalie'].trial_start()

        # Play the game
        Results, escapeCheck = playGame(Settings, Results, BallJoystick, BarJoystick, win, trial)

        # Check for escapeCheck
        if escapeCheck:
            return Results, escapeCheck

        # Update the reward, displaying the results.
        if Results[trial]['outcome'] == 'win':
            Results[trial]['RewardBall'] = Settings.RewardForScoring
            finaltext = 'Win!'

        elif Results[trial]['outcome'] == 'loss':
            Results[trial]['RewardBar'] = Settings.RewardForBlockingBall
            finaltext = 'Loss!'
        else:
            final_text = "This isn't supposed to happen"

        final_text = visual.TextStim(win, finaltext, font='Helvetica', alignHoriz='center',
                                        alignVert='center', units='norm',
                                        pos=(0, 0), height=0.1,
                                        color=[255, 255, 255], colorSpace='rgb255',
                                        wrapWidth=2)
        final_text.draw()
        win.flip()

        core.wait(Settings.TimeToWaitAfterOutcome)

        win.flip()

        #Check to see if escape has been pressed. If it has, return.
        escapeCheck = BallJoystick.JoystickEscape()

        if escapeCheck:
            return Results, escapeCheck

        # Remove the extra dictionary that we added for trial 0.
        if trial == 0:
            Results.pop()

    return Results, escapeCheck
