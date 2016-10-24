# Penalty Kick game by Jean-Francois Gariepy, overhauled by Bill
# Broderick. This version rewritten mostly from the ground up
# in PsychoPy by John Pearson.

from __future__ import division  # so that 1/3=0.333 instead of 1/3=0
import numpy as np
from psychopy import gui, visual, event, core, logging, data
from psychopy.constants import *  # things like STARTED, FINISHED
from psychopy.hardware import joystick
from datetime import datetime
import sys
import os
import json
from utils import Flicker
from settings import Settings, get_settings

############## Preamble ######################
# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

# We load the settings class from Settings.py (see
# README.md for a description of the fields it contains)
settings = Settings()

# This is the current date and time. The date will be scrubbed from it
# before saving to only record the day time in hours, mins, secs, microseconds.
settings.CurrentDate = datetime.now()
t = settings.CurrentDate
settings.overallStartTime = '%d:%d:%d:%d' % (t.hour, t.minute, t.second, t.microsecond)
# Remove currentDate information for privacy/identification purposes.
del settings.CurrentDate

# get setup info about current session:
SubjName, P2, runType, VS_trials, VS_runs, goalieType, prior, BallSpeed, full = get_settings()

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
filename = _thisDir + os.sep + u'data/%s_%s_%s' %(SubjName, 'penaltyshot', settings.overallStartTime)

#save a log file for detail verbose info
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

endExpNow = False  # flag for 'escape' or other condition => quit the exp
