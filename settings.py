import numpy as np
from scipy.stats import beta

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
