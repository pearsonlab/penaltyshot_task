import numpy as np
from scipy.stats import beta
from psychopy import gui

def get_settings():
    # This function defines the DLG at the beginning of the experiment where
    # the experimenter can set information and make decisions about parameters.
    # File name is ultimately saved based on several of these characteristics,
    # (namely runType, SubjID, P2 and a counter for how many times that combination
    # of settings has been used (to avoid overwriting files)).
    runType_options = ['experiment', 'train', 'Vs']
    goalieType_options = ['guess', 'react']

    dlg = gui.Dlg(title='Choose Settings')
    dlg.addText('Penalty Shot Task', color="Blue")
    dlg.addText('Players', color="Blue")
    dlg.addField('Subject ID/P1:', 'practice1')
    dlg.addField('P2', 'practice2')
    dlg.addText('')
    dlg.addText('Modes and VS Variables', color="Blue")
    dlg.addField('RunType','Vs', choices=runType_options)
    dlg.addField('Number of VS Trials', 20)
    dlg.addField('Number of VS Runs', 2)
    dlg.addText('')
    dlg.addText('Goalie Parameters', color="Blue")
    dlg.addField('GoalieType','guess', choices=goalieType_options)
    dlg.addField('prior', 1)
    dlg.addField('BallSpeed Factor', 1.0)
    dlg.addText('')
    dlg.addField('FullScreen', True, choices=[False,True])
    dlg.addText('')

    dlg.show()
    if dlg.OK:
        return dlg.data
    else:
        sys.exit()

class Settings(object):
    # Default variables
    RewardForBlockingBall = 0.5
    RewardForScoring = 0.5

    # Timing variables
    BallPauseStart = 0.3
    TimeToWaitAfterOutcome = 1.5
    TimeToWaitWithOppPic = 2.0

    CpuBarLagMinValue = 0.12
    CpuBarLagDist = beta(2, 5)

    ScreenRefreshInterval = 60
    FixCrossJitterMean = 2
    BallJoystickNum = 0
    BarJoystickNum = 1
    BallJoystickDeadZone = 0.1
    BarJoystickDeadZone = 0.1
    ActiveScreen = 0

    # Variables set before run
    CurrentDate = 0
    runType = 0 # train, experiment, Vs
    goalieType = 0
    P1Name = 0
    P2Name = 0
    RunLength = 0
    BarJoystickConnected = 0 # P2 joystick for VS mode
    OpponentOrder = [] # for experiment trials
    FixCrossJitterOrder = []

    # Variables set at run-time
    ScreenRect = [0, 0] # size of screen - window.size [width, height]
    BallRadius = 0 # width of screen/64
    BarWidth = 0 # width of screen/128
    BarLength = 0 # height/6
    BallStartPosX = 0 # width/8
    BallStartPosY = 0 # height/2
    BarStartPosX = 0 # width*7/8
    BarStartPosY = 0
    FinalLine = 0 # = barstartx + 2*barwidth
    BallSpeed = 0 # width of screen/100
    BarJoystickBaseSpeed = 0 # ballspeed/1.5 (can be modified)
    BarJoystickAccelIncr = 0 # ballspeed/60 (can be modified)
