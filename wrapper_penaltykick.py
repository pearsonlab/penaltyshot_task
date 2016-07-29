import numpy as np
from psychopy import gui, visual, event, core
from psychopy.hardware import joystick
from datetime import datetime
import sys
import os
import json

from settings import Settings
from goalie_react_guess import Goalie
from penaltykick_run import Penaltykick_run

# This is the wrapper for the task script. It is what the experimenter
# actually runs: it loads the Settings class, sets some of their
# values, opens the Screen, monitors runs, gets joystick-related
# values set, calls penaltykick_run.py, and then displays and saves
# the overall performance and Results.
#
# The majority of the parameters for the task that can be modified
# are presented in the dlg at the beginning of the task.
# 
# The runType argument should be a string which specifies how you
# want the task to be played. The following options are currently
# implemented:
# 
#  - 'train': participant play against a computer every trial, to get
#    a feel for the controls. Only one run is played, relatively
#    small number of trials. Fixation crosses between trials all
#    last 1 second.
# 
#  - 'experiment': participant plays against a human and a computer
#    opponent, randomly picking which they play on each trial. This is
#    the mode to use for the actual experiment. Four runs
#    are played. The durations of the fixation crosses between trials
#    are jittered.
# 
#  - 'Vs': used primarily for testing, participant plays against a
#    human opponent. Two trials are played and the control of the bar and ball
#    switches between runs (so both players have the opportunity to
#    play as both bar and ball). Fixation crosses between trials
#    all last 1 second.
# 
# The goalieType argument is a string that specifies the computer
# goalie's strategy. The following options are currently available:
# 
#  - 'react': the goalie simply tracks the ball, with a small lag to
#    simulate reaction time. This reaction time has its parameters set
#    in Settings (CpuBarLagMinValue and CpuBarLagDist), and every
#    trial the cpu's reaction time is `CpuBarLagMinValue + (.1 *
#    CpuBarLagDist.random())`. In effect, we take the minimum value
#    and add one observation from the distribution (we multiply by
#    .1 because the distribution lies on the interval [0,1] and we
#    want values from the interval [0, .1]).
# 
#  - 'guess': this goalie tracks the ball (just like react) up to a
#    certain point and then, once the ball is about to reach the
#    "critical point" where the ball could outrace the goalie
#    (determined analytically based on the ball's speed and the
#    goalie's speed, acceleration, and average reaction time), the
#    goalie makes a guess from five possibilities for what it should
#    do next: continue to track, up-up, up-down, down-up, and
#    down-down. This attempts to emulate how goalies perform in an
#    actual penalty kick: at some point, they just have to
#    guess. The goalie can be set to learn, in which case it will
#    update its probabilities of choosing the different guesses
#    based on what choices it has seen the ball make.

def text_draw(win, text, position=(0,0)):
	# This function draws the stimuli at the end of the trial for outcomes,
	# setting all the necessary text features ahead of time.
	display_text = visual.TextStim(win, text=text,
                                   font='Helvetica', alignHoriz='center',
                                   alignVert='center', units='norm',
                                   pos=position, height=0.1,
                                   color=[255, 255, 255], colorSpace='rgb255',
                                   wrapWidth=2)                                   
	display_text.draw()
	return display_text

def get_settings():
	# This function defines the DLG at the beginning of the experiment where
	# the experimenter can set information and make decisions about parameters.
	# File name is ultimately saved based on several of these characteristics,
	# (namely runType, SubjID, P2 and a counter for how many times that combination
	# of settings has been used (to avoid overwriting files)).
	runType_options = ['experiment', 'train', 'Vs']
	goalieType_options = ['guess', 'react']
    
	dlg = gui.Dlg(title='Choose Settings')
	dlg.addText('Penalty Kick Task', color="Blue")
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

def Wrapper_Penaltykick():
	
	# DLG
	SubjName, P2, runType, VS_trials, VS_runs, goalieType, prior, BallSpeed, full = get_settings()
	
	# We load the settings class from Settings.py (see
    # README.md for a description of the fields it contains)
	settings = Settings()
	
	# This is the current date and time. The date will be scrubbed from it before saving
	# to only record the day time in hours, mins, secs, microseconds.
	settings.CurrentDate = datetime.now()
		
	settings.runType = runType
	settings.goalieType = goalieType
	
	# Make sure runType is implemented and set the relevant variables.
	if runType == 'experiment':
		settings.SubjName = SubjName
		settings.RunLength = 60
		OpponentOrder = np.tile(['human', 'cpu'],settings.RunLength/2)
		allRuns = 4
		# This returns a vector of jitter values. We then make sure there are
		# none less than 1 and round them to the nearest half
		# second. Since we set the seed of the rng above, exprnd will
		# return the same sequence every time. Thus, every subject, every
		# run will have a different permutation of the same vector.
		numpy.random.seed(0)
		FixCrossJitterOrder = np.random.exponential(settings.FixCrossJitterMean, settings.RunLength)
		FixCrossJitterOrder = FixCrossJitterOrder+1
		FixCrossJitterOrder = np.floor(FixCrossJitterOrder/0.5)*0.5
	elif runType == 'train':
		settings.SubjName = SubjName
		settings.RunLength = 20
		OpponentOrder = np.tile(['cpu'], settings.RunLength)
		allRuns = 1
		# If this is runType train, we don't need different jitters, we just
        # want a small length of time between trials.
		FixCrossJitterOrder = np.tile(1, settings.RunLength)
	elif runType == 'Vs':
		settings.SubjName = SubjName
		settings.P2Name = P2
		settings.RunLength = VS_trials
		OpponentOrder = np.tile(['human'], settings.RunLength)
		allRuns = VS_runs
		# If this is runType Vs, we don't need different jitters, we just
        # want a small length of time between trials.
		FixCrossJitterOrder = np.tile(1, settings.RunLength)

		settings.BallJoystickNum = 0
		settings.BarJoystickNum = 1
	else:
		raise ValueError("Wrapper: runType not found. Can't find runType %s!" % runType)
	
	# Make sure one joystick is connected.	
	joystick.backend = 'pygame'
	nJoysticks = joystick.getNumJoysticks()
	
	if nJoysticks == 0:
		print 'There is no joystick connected!'
		core.quit()
	
	# Open up a screen in PsychoPy. Arrange the settings for the ball, bar,
    # and final line positions based on the resolution of that screen.
	win = visual.Window(size=(800, 600), units='pix', winType = 'pygame', screen=0, 
						monitor='testMonitor', fullscr=full, colorSpace='rgb255', 
						color=(0, 0, 0))
	settings.ScreenRect = win.size
	W = float(settings.ScreenRect[0])
	H = float(settings.ScreenRect[1])
	settings.BallRadius = W / 128.;
	settings.BarWidth = settings.BallRadius;
	settings.BarLength = H / 4.0;
	settings.BallStartingPosX = W* -3./ 8.;
	settings.BallStartingPosY = 0.;
	settings.BarStartingPosX = W * 3./8.;
	settings.BarStartingPosY = settings.BallStartingPosY;
	settings.FinalLine = settings.BarStartingPosX + 3*settings.BarWidth;

	#This is how fast the ball moves horizontally. When we get the
	#position of the joystick vertical axis (which lies between -1 and
	#1), we multiply that value by BallSpeed, ensuring that the
	#ball's max vertical speed is the same as its horizontal speed	
	settings.BallSpeed = (W / 200.) * BallSpeed
	
	# To allow for bar acceleration, we start them with a slower speed and
	# an acceleration parameter, which determines how much their
	# speed increases each move they continue in the same direction
	settings.BarJoystickBaseSpeed = settings.BallSpeed / 1.5
	settings.BarJoystickAccelIncr = settings.BallSpeed / 90.
	
	# Initialize the goalie        
	if settings.goalieType == 'react':
		goalie_class = Goalie('react', False, 1, settings)
		goalie = goalie_class.goalie_react_guess()
	elif settings.goalieType == 'guess':
		goalie_class = Goalie('guess', True, prior, settings)
		goalie = goalie_class.goalie_react_guess()
	else:
		# Else, we're not sure what kind of goalie we want
		raise ValueError("This goalieType has not be implemented- %s" % settings.goalieType)
    
	win.mouseVisible = False

	# Set variables for running list of outcomes and opponents
	# to be used for final scoring screen.
	# Not all variables will be used for each runType.
	p1_ball_win = 0.0
	p2_bar_win = 0.0
	first_round = 0.0

	p1_bar_win = 0.0
	p2_ball_win = 0.0
	second_round = 0.0
	
	player_win = 0.0
	human_opponent_win = 0.0
	human_opponent_round = 0.0

	# Iterate through the runs we specified (all differences
    # between train and experiment run have already been set above)
	for run in range(allRuns):
    	
    	# We generate a new order for the opponents and jitters every run.
    	# This ensures we have a random ordering of our opponents, but we will
    	# have exactly half and half human and cpu opponents (unless
    	# runType is train, then they're all cpu)
		settings.OpponentOrder = np.random.permutation(OpponentOrder)
		
		# This is a random permutation of the FixCrossJitterOrder vector.
		settings.FixCrossJitterOrder = np.random.permutation(FixCrossJitterOrder)

		# Give some time to regroup before each run
		core.wait(2)
		
		# Run through runs and trials from penaltykick_run.py
		Results, escapeCheck = Penaltykick_run(settings, SubjName, run, win, goalie)
		
		# Save Data
		saveVarsAndData(run, SubjName, settings, Results, P2)
		
		# If the experimenter pressed, escape, we don't want to
		# gather overall results		
		if escapeCheck:
			break
    	
    	# We add the outcomes (and opponents) of our trials onto our running
    	# list of outcomes (and opponents).
		if runType == 'Vs':

			# If it's run 0 or an even numbered run.
			if run % 2 == 0:
				for i in range(len(Results)):
					if Results[i]['outcome'] == 'win':
						p1_ball_win += 1.0
					else:
						p2_bar_win += 1.0
					first_round += 1.0
			
			# If it's run 1 or an odd numbered run.
			else:
				for i in range(len(Results)):
					if Results[i]['outcome'] == 'win':
						p2_ball_win += 1.0
					else:
						p1_bar_win += 1.0
					second_round += 1.0
    		
    		# Swap numbers for Bar and Ball Joysticks for next round
			temp = settings.BarJoystickNum
			settings.BarJoystickNum = settings.BallJoystickNum
			settings.BallJoystickNum = temp
		else:

			for i in range(len(Results)):
				if Results[i]['Opponent'] == 'human':
					human_opponent_round += 1.0
					if Results[i]['outcome'] == 'loss':
						human_opponent_win  += 1.0


				if Results[i]['outcome'] == 'win':
					player_win += 1.0
    		
			BallWinPercentage = player_win/float(len(Results))
			if human_opponent_round != 0.0:
				BarWinPercentage = human_opponent_win/human_opponent_round
	
	# If escape was pressed, we don't want to calculate win
	# percentages and we just quit.
	if escapeCheck:
		core.quit()

	# Display final screen with outcomes and percentages on it,
	# based on runType and Results (as calculated above).
	if runType == 'Vs':
		P1BallWinPercentage = p1_ball_win/first_round
		P2BarWinPercentage = p2_bar_win/first_round
		P1BarWinPercentage = p1_bar_win/second_round
		P2BallWinPercentage = p2_ball_win/second_round

		text = "As ball - %.1f %%" % ((100*P1BallWinPercentage))
		text2 = "As bar - %.1f %%" % ((100*P1BarWinPercentage))
		text3 = "As ball - %.1f %%" % ((100*P2BallWinPercentage))
		text4 = "As bar - %.1f %%" % ((100*P2BarWinPercentage))

		p1 = text_draw(win, SubjName+" Win Percentage:", (0, 0.5))
		p1ball = text_draw(win, text, (0, .35))
		p1bar = text_draw(win, text2, (0, 0.2))
		p2 = text_draw(win, P2+" Win Percentage:", (0, -.05))
		p2ball = text_draw(win, text3, (0, -0.2))
		p2bar = text_draw(win, text4, (0, -0.35))
		
		win.flip()
		core.wait(10)

	elif runType == 'experiment':
		# If runType is experiment, then we also want to calculate the Bar's
		# win percentage.  We only calculate the bar's win percentage
		# based on the games that they actually played in, ie those
		# with a human opponent
		text = "Ball player's win percentage: %.1f %%" % (100*BallWinPercentage)
		text2 = "Bar player's win percentage: %.1f %%" % (100*BarWinPercentage)

		p1ball = text_draw(win, text, (0, 0.25))
		p2bar = text_draw(win, text2, (0, -.25))
		
		win.flip()
		core.wait(10)
		
	elif runType == 'train':
		# if runType is train, we only need to calculate the
		# BallWinPercentage, since there was no bar player.
		text = "Ball player's win percentage: %.1f %%" % (100*BallWinPercentage)
		
		train = text_draw(win, text)
		win.flip()
		core.wait(5)
    	
def saveVarsAndData(currentRun, SubjName, Settings, Results, P2):
	# This function is responsible for making the json file at the end of the experiment
	# and saving the Settings and Results to it. It is called immediately after each run
	# (and therefore doesn't save automatically the outcomes calculations, since these can
	# can be easily recreated from the data).
	
	# Make sure the behavioral directory exists.
	if not os.path.exists('behavioral/'):
		os.makedirs('behavioral')

	# This loop is designed to create unique file names for each time the same set of characteristics
	# are used for a certain experiment. All runs (and therefore all trials) are saved within the same file.
	i = 0
	while True:
		if Settings.runType == 'train':
			filename = 'behavioral/pkick_%s_%s_%d.json' % (SubjName, Settings.runType, i)
		else:	
			filename = 'behavioral/pkick_%s_%s_%s_%d.json' % (SubjName, Settings.runType, P2, i)	

		if currentRun == 0:
			if not os.path.exists(filename):
				break
			else:
				i += 1
		else:
			i += 1
			if Settings.runType == 'train':
				filename_next = 'behavioral/pkick_%s_%s_%d.json' % (SubjName, Settings.runType, i)
			else:	
				filename_next = 'behavioral/pkick_%s_%s_%s_%d.json' % (SubjName, Settings.runType, P2, i)
			if os.path.exists(filename) and not os.path.exists(filename_next):
				break

	# If it's the first run, save the settings to the file. This makes it the first line on the json file.
	if currentRun == 0:
		settings = vars(Settings)
		t = settings['CurrentDate']
		settings['overallStartTime'] = '%d:%d:%d:%d' % (t.hour, t.minute, t.second, t.microsecond)
		# Remove currentDate information for privacy/identification purposes.
		del settings['CurrentDate']
		settings['ScreenRect'] = settings['ScreenRect'].tolist()
		settings['OpponentOrder'] = settings['OpponentOrder'].tolist()
		settings['FixCrossJitterOrder'] = settings['FixCrossJitterOrder'].tolist()

		with open(filename, 'a') as f:
			f.write(json.dumps(settings))
			f.write('\n')
	
	# For each run, save Results (as long as Results is not empty).
	if Results:
		for i in range(len(Results)):
			if not Results[i]:
				break
			
			# All of these pieces must be python-native format (i.e. lists)
			# Also, the goalie object doesn't have useful information for data purposes
			# that isn't recorded elsewhere.	
			del Results[i]['goalie']
			if type(Results[i]['BarJoystickHistory']) == np.ndarray:
				Results[i]['BarJoystickHistory'] = Results[i]['BarJoystickHistory'].tolist()
			if type(Results[i]['BallJoystickHistory']) == np.ndarray:
				Results[i]['BallJoystickHistory'] = Results[i]['BallJoystickHistory'].tolist()
			if type(Results[i]['BallPositions']) == np.ndarray:
				Results[i]['BallPositions'] = Results[i]['BallPositions'].tolist()
			
			with open(filename, 'a') as f:
				f.write(json.dumps(Results[i]))
				f.write('\n')
	else: 
		json.dumps("Didn't begin any trials in run %d." % currentRun, filename)
	return

	
if __name__ == '__main__':
	Wrapper_Penaltykick()
	