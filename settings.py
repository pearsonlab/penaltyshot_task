from psychopy import gui
import sys

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
    dlg.addField('Day', 0)
    dlg.addText('')
    dlg.addText('VS Variables', color="Blue")
    dlg.addField('Number of VS Trials', 20)
    dlg.addText('')
    dlg.addText('Ball Parameters', color="Blue")
    dlg.addField('BallSpeed Factor', 1.0)
    dlg.addText('')
    dlg.addField('FullScreen', True, choices=[False,True])
    dlg.addText('')

    fieldnames = ['SubjName', 'P2', 'Day', 'trials_in_block', 'BallSpeed', 'full']

    dlg.show()
    if dlg.OK:
        return dict(zip(fieldnames, dlg.data))
    else:
        sys.exit()

def setup_geometry(settings, win, **kwargs):
    # set up the geometry of the screen given a settings object and a
    # window to attach to

    # store frame rate of monitor if we can measure it successfully
    settings['frameRate'] = win.getActualFrameRate()
    if settings['frameRate'] != None:
        frameDur = 1.0/round(settings['frameRate'])
    else:
        frameDur = 1.0/60.0 # couldn't get a reliable measure so guess
    settings['frameDur'] = frameDur

    settings['ScreenRect'] = tuple(win.size)
    W = float(settings['ScreenRect'][0])
    H = float(settings['ScreenRect'][1])
    settings['BallRadius'] = W / 128.;
    settings['BarWidth'] = settings['BallRadius'];
    settings['BarLength'] = H / 4.0;
    settings['BallStartingPosX'] = W* -3./ 8.;
    settings['BallStartingPosY'] = 0.;
    settings['BarStartingPosX'] = W * 3./8.;
    settings['BarStartingPosY'] = settings['BallStartingPosY'];
    settings['FinalLine'] = settings['BarStartingPosX'] + 3 * settings['BarWidth']
    settings['FinalLineHalfHeight'] = H/2.

    #This is how fast the ball moves horizontally. When we get the
    #position of the joystick vertical axis (which lies between -1 and
    #1), we multiply that value by BallSpeed, ensuring that the
    #ball's max vertical speed is the same as its horizontal speed
    ball_velocity = 1500. * kwargs['BallSpeed']  # in pix/s
    settings['BallSpeed'] = ball_velocity * settings['frameDur'] # in pix/frame

    # To allow for bar acceleration, we start them with a slower speed and
    # an acceleration parameter, which determines how much their
    # speed increases each move they continue in the same direction
    settings['BarJoystickBaseSpeed'] = settings['BallSpeed'] / 1.5
    settings['BarJoystickAccelIncr'] = settings['BallSpeed'] / 90.

    return

settings = {
    # Default variables
    'RewardForBlockingBall': 0.5,
    'RewardForScoring': 0.5,

    # Timing variables
    'BallPauseStart': 0.3,
    'TimeToWaitAfterOutcome': 1.5,
    'TimeToWaitWithOppPic': 2.0,

    'CpuBarLagMinValue': 0.12,

    'ScreenRefreshInterval': 60,
    'FixCrossJitterMean': 2,
    'BlockMessageTime': 3,
    'Joystick0_DeadZone':0.1,
    'Joystick1_DeadZone': 0.1,
    'ActiveScreen': 0,

    # Variables set before run
    'CurrentDate': 0,
    'runType': 0,  # train, experiment, Vs
    'goalieType': 0,
    'P1Name': 0,
    'P2Name': 0,
    'RunLength': 0,
    'BarJoystickConnected': 0, # P2 joystick for VS mode
    'OpponentOrder': [], # for experiment trials
    'FixCrossJitterOrder': [],

    # Variables set at run-time
    'ScreenRect': [0, 0],  # size of screen - window.size [width, height]
    'BallRadius': 0,  # width of screen/64
    'BarWidth': 0, # width of screen/128
    'BarLength': 0, # height/6
    'BallStartPosX': 0, # width/8
    'BallStartPosY': 0, # height/2
    'BarStartPosX': 0, # width*7/8
    'BarStartPosY': 0,
    'FinalLine': 0, # = barstartx + 2*barwidth
    'BallSpeed': 0, # width of screen/100
    'BarJoystickBaseSpeed': 0, # ballspeed/1.5 (can be modified)
    'BarJoystickAccelIncr': 0 # ballspeed/60 (can be modified)
}
