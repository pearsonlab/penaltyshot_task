# Penalty Kick game by Jean-Francois Gariepy, overhauled by Bill
# Broderick. This version rewritten mostly from the ground up
# in PsychoPy by John Pearson.

from __future__ import division, print_function  # so that 1/3=0.333 instead of 1/3=0
import numpy as np
from psychopy import gui, visual, event, core, logging, data
from psychopy.constants import *  # things like STARTED, FINISHED
from psychopy.hardware import joystick
from input_handler import JoystickServer
import physics
from datetime import datetime
import sys
import os
import json
from utils import Flicker
from settings import *

############## Paths, config, logging ######################
# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

# This is the current date and time. The date will be scrubbed from it
# before saving to only record the day time in hours, mins, secs, microseconds.
t = datetime.now()
settings['overallStartTime'] = '%d.%d.%d' % (t.hour, t.minute, t.second)

# get setup info about current session:
config = get_settings()

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
filename = _thisDir + os.sep + u'data/%s_%s_%s' %(config['SubjName'], 'penaltyshot', settings['overallStartTime'])

#save a log file for detail verbose info
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

# log start time for the experiment
logging.log(level=logging.EXP, msg='Task start time: {}:{}:{}'.format(t.hour, t.minute, t.second))

# Remove currentDate information for privacy/identification purposes.
del t

########## Set up hardware #####################
full = False #config['full']
win = visual.Window(size=(800, 600), units='pix', winType = 'pygame', screen=1,
                    monitor='testMonitor', fullscr=full, colorSpace='rgb255',
                    color=(0, 0, 0))

# turn of mouse display
win.mouseVisible = False

# set up screen geometry based on window size
setup_geometry(settings, win, **config)

# Make sure one joystick is connected.
joystick.backend = 'pygame'
nJoysticks = joystick.getNumJoysticks()
logging.log(level=logging.EXP, msg='{} joysticks detected'.format(nJoysticks))

if nJoysticks == 0:
    print('There is no joystick connected!')
    core.quit()
else:
    J0 = JoystickServer(0, settings['Joystick0_DeadZone'])
    if nJoysticks > 1:
        J1 = JoystickServer(1, settings['Joystick1_DeadZone'])

# set up photodiode trigger
trigger = Flicker(win)

########## Set up stims #####################
fixation = visual.TextStim(win, text='+',
                            alignHoriz='center',
                            alignVert='center', units='norm',
                            pos=(0, 0), height=0.3,
                            color=[255, 255, 255], colorSpace='rgb255',
                            wrapWidth=2, name='fix_cross', autoLog=True)
display_text = visual.TextStim(win, text='Your text here',
                               font='Helvetica', alignHoriz='center',
                               alignVert='center', units='norm',
                               pos=(0, 0), height=0.1,
                               color=[255, 255, 255], colorSpace='rgb255',
                               wrapWidth=2, name='display_text',
                               autoLog=True)
line = visual.Line(win, start=(settings['FinalLine'],
                               settings['FinalLineHalfHeight']),
                        end=(settings['FinalLine'],
                               -settings['FinalLineHalfHeight']),
                        name='goal_line')
ball = visual.Circle(win, radius=settings['BallRadius'], fillColor='red',
                     lineColor='red', pos=(settings['BallStartingPosX'],
                     settings['BallStartingPosY']), name='ball')
barVertices = [ [-settings['BarWidth']/2., settings['BarLength']/2.],
                [settings['BarWidth']/2., settings['BarLength']/2.],
                [settings['BarWidth']/2., -settings['BarLength']/2.],
                [-settings['BarWidth']/2., -settings['BarLength']/2.] ]
bar = visual.ShapeStim(win,vertices=barVertices,fillColor='blue',
                       lineColor='blue', pos=(settings['BarStartingPosX'],
                       settings['BarStartingPosY']), name='bar')

############# match inputs to players ###############
# default to these assignments (can change by block)
ball.joystick = J0
bar.joystcik = J1

############# finalize setup ###############
# log all settings
logging.log(level=logging.EXP, msg='settings = {}'.format(repr(settings)))
# write out everything logged so far
logging.flush()

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
trialClock = core.Clock()  # time within trial
playClock = core.Clock()  # time within trial

############# prepare to start trial loop ###############
endExpNow = False  # flag for 'escape' or other condition => quit the exp
thisTrial = 0
logging.log(level=logging.EXP, msg='Starting task')

while not endExpNow:  # main experiment loop

    ###### set up for  trial ############
    endTrialNow = False  # flag for escape from trial
    trialOver = False  # has the trial completed
    playOn = False  # has play commenced
    thisTrial += 1
    event.clearEvents(eventType='keyboard')
    logging.log(level=logging.EXP, msg='Start trial {}'.format(thisTrial))

    # reset stims
    trialComponents = [fixation, display_text, ball, bar, line]
    for thisComponent in trialComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED

    # setup stim timing
    fixStart = 0.0
    fixTime = settings['FixCrossJitterMean']
    playStart = fixStart + fixTime

    # reset players
    ball.pos = (settings['BallStartingPosX'], settings['BallStartingPosY'])
    bar.pos = (settings['BarStartingPosX'], settings['BarStartingPosY'])
    ball.accel = 1.0

    # timing setup
    t = 0  # time in trial
    frameN = -1  # frame within trial
    trialClock.reset()  # reset trial clock

    ###### end trial setup ###############

    while not endTrialNow:  # trial loop
        t = trialClock.getTime()  # current trial time
        frameN += 1  # increment frame number

        # handle keyboard input
        theseKeys = event.getKeys(keyList=['escape'])

        # check for quit:
        if 'escape' in theseKeys:
            endTrialNow = True
            endExpNow = True

        # update fixation cross
        if t >= fixStart and fixation.status == NOT_STARTED:
            fixation.setAutoDraw(True)
        if fixation.status == STARTED and t >= (fixStart + (fixTime - win.monitorFramePeriod*0.75)): #most of one frame period left
            fixation.setAutoDraw(False)

        # update other stims
        if t >= playStart and ball.status == NOT_STARTED:
            ball.setAutoDraw(True)
            bar.setAutoDraw(True)
            line.setAutoDraw(True)
            playOn = True
            playClock.reset()

        if playOn:
            tt = playClock.getTime()
            physics.update_bar(tt, bar, settings)
            physics.update_ball(tt, ball, settings)

            # check outcome
            ballx, bally = ball.pos
            barx, bary = bar.pos
            ballrad = settings['BallRadius']
            barwid = settings['BarWidth']
            barlen = settings['BarLength']

            # if ball has crossed goal line
            if ballx + settings['BallRadius'] > settings['FinalLine']:
                # ball wins
                trialOver = True
            # if ball overlaps bar
            elif (ballx + ballrad >= barx - barwid/2. and
            ballx - ballrad <= barx - barwid/2. and
            bally + ballrad > bary - barlen/2. and
            bally - ballrad < bary + barlen/2.):
                # goalie wins
                trialOver = True

        if trialOver:
            ball.setAutoDraw(False)
            bar.setAutoDraw(False)
            line.setAutoDraw(False)
            endTrialNow = True

        # update screen
        win.flip()

    # clean up after trial
    logging.log(level=logging.EXP, msg='End trial {}'.format(thisTrial))
    logging.flush()


# clean up after task
logging.log(level=logging.EXP, msg='Ending task')
t = datetime.now()
# log end time for the experiment
logging.log(level=logging.EXP, msg='Task finish time: {}:{}:{}'.format(t.hour, t.minute, t.second))
logging.flush()
