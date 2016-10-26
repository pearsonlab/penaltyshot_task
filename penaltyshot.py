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

# set up an object to store data as json
metadata = ({'experiment': 'penaltyshot',
             'subject': config['SubjName'],
             'start_time': '{}:{}:{}'.format(t.hour, t.minute, t.second),
             'day': config['Day'],
             'psychopy_start_time': core.getAbsTime(),
             'settings': settings, 'config': config
            })

# write out metadata
json_fp = open(filename+'.json', 'w', buffering=1)
json.dump(metadata, json_fp)
json_fp.write('\n')

# Remove currentDate information for privacy/identification purposes.
del t

########## Set up hardware #####################
full = config['full']
win = visual.Window(size=(800, 600), units='pix', winType = 'pygame', screen=1,
                    monitor='testMonitor', fullscr=full, colorSpace='rgb255',
                    color=(0, 0, 0))

# turn off mouse display
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
    else:
        print('You need two joysticks to play!')
        core.quit()

########## Set up stims #####################
fixation = visual.TextStim(win, text='+',
                            alignHoriz='center',
                            alignVert='center', units='norm',
                            pos=(0, 0), height=0.3,
                            color=[255, 255, 255], colorSpace='rgb255',
                            wrapWidth=2, name='fix_cross', autoLog=True)
message_text = visual.TextStim(win, text='Your text here',
                               font='Helvetica', alignHoriz='center',
                               alignVert='center', units='norm',
                               pos=(0, 0), height=0.1,
                               color=[255, 255, 255], colorSpace='rgb255',
                               wrapWidth=2, name='message_text',
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

# set up photodiode trigger
trigger = Flicker(win)

############# finalize setup ###############
# log all settings
logging.log(level=logging.EXP, msg='settings = {}'.format(repr(settings)))
# write out everything logged so far
logging.flush()

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
trialClock = core.Clock()  # time within trial
playClock = core.Clock()  # time within trial

############# prepare to start main experiment loop ###############
endExpNow = False  # flag for 'escape' or other condition => quit the exp
thisTrial = 0
logging.log(level=logging.EXP, msg='Starting task')
metadata['task_start_time'] = globalClock.getTime()

while not endExpNow:  # main experiment loop

    ###### set up for  trial ############
    thisTrial += 1
    logging.log(level=logging.EXP, msg='Start trial {}'.format(thisTrial))

    # sentinel variables for task state
    endTrialNow = False  # flag for escape from trial
    winner = None  # has the trial completed
    playOn = False  # has play commenced
    blockSwitch = False
    showMessage = False

    # block logic
    if thisTrial % config['trials_in_block'] == 1:
        if thisTrial == 1:
            # assign joysticks
            ball.joystick = J0
            bar.joystick = J1
        else:
            blockSwitch = True
            # swap joysticks
            J = ball.joystick
            ball.joystick = bar.joystick
            bar.joystick = J
            del J

        # log it
        if ball.joystick is J0:
            jmsg = 'Joysticks: Ball = 0, Bar = 1'
        else:
            jmsg = 'Joysticks: Ball = 1, Bar = 0'
        logging.log(level=logging.EXP, msg=jmsg)

    # reset stims
    trialComponents = [fixation, message_text, ball, bar, line]
    for thisComponent in trialComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED

    # setup stim timing
    # have to reset these to None because they don't necessarily
    # get set during trial
    tTrialStart = None
    tMsgOn = None
    tMsgOff = None
    tFixOn = None
    tFixOff = None
    tPlayStart = None
    tPlayEnd = None
    tTrialEnd = None
    if blockSwitch:
        showMessage = True
        msgStart = 0.0
        msgTime = settings['BlockMessageTime']
        message_text.setText('Switch roles!', log=False)
        fixStart = msgStart + msgTime
    else:
        fixStart = 0.0
    fixTime = settings['FixCrossJitterMean']
    playStart = fixStart + fixTime
    outcomeOverTime = np.inf

    # reset players
    ball.setPos((settings['BallStartingPosX'], settings['BallStartingPosY']), log=False)
    ball.history = []
    ball.jhistory = []
    bar.setPos((settings['BarStartingPosX'], settings['BarStartingPosY']), log=False)
    bar.history = []
    bar.jhistory = []
    bar.accel = []
    bar.maxmove = []

    # reset clocks
    t = 0  # time in trial
    frameN = -1  # frame within trial
    tTrialStart = globalClock.getTime()
    trialClock.reset()  # reset trial clock

    ###### end trial setup ###############

    while not endTrialNow:  # trial loop
        global_time = globalClock.getTime()  # current experiment time
        t = trialClock.getTime()  # current trial time
        frameN += 1  # increment frame number

        # handle keyboard input
        theseKeys = event.getKeys(keyList=['escape'])

        # check for quit:
        if 'escape' in theseKeys:
            endTrialNow = True
            endExpNow = True

        # clear event buffer
        event.clearEvents()

        # update message
        if showMessage and t >= msgStart and message_text.status == NOT_STARTED:
            message_text.setAutoDraw(True, log=False)
            tMsgOn = global_time
            logging.log(level=logging.EXP, msg='Message on')
            trigger.flicker(1)
        if message_text.status == STARTED and t >= (msgStart + (fixTime - win.monitorFramePeriod*0.75)): #most of one frame period left
            message_text.setAutoDraw(False, log=False)
            showMessage = False
            tMsgOff = global_time
            logging.log(level=logging.EXP, msg='Message off')

        # update fixation cross
        if t >= fixStart and fixation.status == NOT_STARTED:
            fixation.setAutoDraw(True, log=False)
            tFixOn = global_time
            logging.log(level=logging.EXP, msg='Fixation on')
            trigger.flicker(1)
        if fixation.status == STARTED and t >= (fixStart + (fixTime - win.monitorFramePeriod*0.75)): #most of one frame period left
            fixation.setAutoDraw(False, log=False)
            tFixOff = global_time
            logging.log(level=logging.EXP, msg='Fixation off')

        # update other stims
        if t >= playStart and ball.status == NOT_STARTED:
            ball.setAutoDraw(True, log=False)
            bar.setAutoDraw(True, log=False)
            line.setAutoDraw(True, log=False)
            tPlayStart = global_time
            logging.log(level=logging.EXP, msg='Start play')
            trigger.flicker(4)  # mark start of play; synced to playClock
            playOn = True
            playClock.reset()

        # handle actual game play
        if playOn:
            tt = playClock.getTime()
            physics.update_bar(global_time, tt, bar, settings)
            physics.update_ball(global_time, tt, ball, settings)

            # check outcome
            winner = physics.check_outcome(ball, bar, settings)

        # conclusion of play
        if winner and playOn:
            playOn = False
            tPlayEnd = global_time
            logging.log(level=logging.EXP, msg='End play')

            # start of outcome period
            trigger.flicker(16)
            outcomeOverTime = t + settings['TimeToWaitAfterOutcome']

        # end of outcome period
        if t > outcomeOverTime:
            # trial stim teardown
            ball.setAutoDraw(False, log=False)
            bar.setAutoDraw(False, log=False)
            line.setAutoDraw(False, log=False)
            endTrialNow = True

        # update screen
        win.flip()

    # clean up after trial
    tTrialEnd = global_time
    logging.log(level=logging.EXP, msg='End trial {}'.format(thisTrial))
    logging.flush()

    # save events to data object
    this_dat = ({'ball_history': ball.history,
                 'ball_joystick_history': ball.jhistory,
                 'bar_history': bar.history,
                 'bar_joystick_history': bar.jhistory,
                 'bar_acceleration': bar.accel,
                 'bar_max_move': bar.maxmove,
                 'winner': winner,
                 'times': ({'trial_start': tTrialStart,
                            'message_on': tMsgOn,
                            'message_off': tMsgOff,
                            'fixation_on': tFixOn,
                            'fixation_off': tFixOff,
                            'play_start': tPlayStart,
                            'play_end': tPlayEnd,
                            'trial_end': tTrialEnd
                            })
                })
    json.dump(this_dat, json_fp)  # dump to json
    json_fp.write('\n')  # write newline to flush buffer


# clean up after task
logging.log(level=logging.EXP, msg='Ending task')

# log end time for the experiment
t = datetime.now()
logging.log(level=logging.EXP, msg='Task finish time: {}:{}:{}'.format(t.hour, t.minute, t.second))
logging.flush()

# close out data object
metadata['psychopy_end_time'] = core.getAbsTime()
metadata['task_end_time'] = globalClock.getTime()
metadata['end_time'] = '{}:{}:{}'.format(t.hour, t.minute, t.second)
# re-dump metadata with end times included
json.dump(metadata, json_fp)
