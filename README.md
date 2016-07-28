# PenaltyKik task

This contains the files necessary to run the Penalty Kik task

Modified from MATLAB code from Bill Broderick, Huettel Lab.

Requirements:

 - Python
 - Numpy
 - SciPy
 - [PsychoPy](psychopy.org/)


## The task itself

The best way to understand what the task looks like is to just play it
yourself. On each trial, the participant sees a centered fixation
cross for a jittered amount of time and a picture of their opponent
for a set amount of time before they start playing the game. During
the game, the ball moves forward at a constant rate, with the
participant able to use the joystick they have (the left joystick of
the controller if they're using an XBox or Logitech controller) to
move the ball up and down. The bar / goalie is controlled by either
one of several computer algorithms or another player using a separate
joystick. The goalie can move only up and down and, while it's
initially slower than the ball, it will accelerate if it continues to
move in a given direction. The game ends when the ball either hits the
goalie (and therefore loses) or makes it to the line behind the goalie
(and therefore wins), at which point small text saying "WIN" or "LOSS"
appears on the screen and the game pauses for a set amount of
time. The next trial then begins with another fixation cross.

## Running the task

Before you get started, make sure you know which joystick number
corresponds to which controller. On a Mac, this depends on which
joystick was plugged in first.

Then, simply open wrapper_penaltykick.py within PsychoPy. All the relevant
parameters that can be changed are set in the DLG at the beginning
of the task.

## Joysticks

Logitech controllers can be used as is; just plug it in and
go. No need to re-center between trials.

# Settings

This describes the list of settings that control the parameters of the
game. When values are given, they are the values found in
`settings.py`, the default values, and do not change. If there is no
value, just a description, then the value of that field may change.

## Values specified at run-time

 - `CurrentDate`; this is the current date

 - `runType`: 'train', 'experiment', or 'Vs'; specifies whether the
    participant will be playing an actual experiment, training, or
    playing a versus mode against another player. 

 - `goalieType`: 'react', 'guess'; specifies how the
    computer goalie plays the game. 
    
 - `P1Name` and `P2Name`: the names of players 1 and 2. Only used when
   `runType` is 'Vs'.

 - `RunLength`: how many trials we should play in a single
    run. Depends on whether `runType` is 'train' or 'experiment'.
    
 - `BallJoystickNum` and `BarJoystickNum`: the numbers for the bar and
    ball joysticks. If only one joystick is plugged in, it's assumed
    that `BallJoystickNum=0` and `BarJoystickNum` is unset.

 - `OpponentOrder`, the order of opponents used in this run (for
    `runType==trial`, this will be a vector of `'cpu'`s with length
    equal to `RunLength`; for `runType==experiment`, this will be a
    random permutation of `'human'`s and `'cpu'`s with length
    `RunLength).

 - `FixCrossJitterOrder`, the order of jitters (in seconds) used in
    this run. This is always a permutation of the same sequence
    (since we set the rng seed to 0 first).

The following settings are generated at runtime because the resolution
of the screen may vary and we want their relative (not absolute)
proportions to be constant.

 - `ScreenRect`: this is returned by the
   `win.size` command from PsychoPy and is a list
   containing Width and Height of the screen (all in pixels).

 - `BallRadius`, this is the width of the screen divided by
   64.

 - `BarWidth`, this is half `BallRadius`, or the
   width of the screen divided by 128.

 - `BarLength`, this is the height of the screen divided by
   6.

 - `BallStartingPosX`: the x position where the ball starts,
   equal to one eighth of the total screen width

 - `BallStartingPosY`: the y position where the ball starts,
   equal to one half of the total screen height

 - `BarStartingPosX`: the x position where the bar starts,
   equal to 7/8 of the total screen width
 
 - `BarStartingPosY`: the y position where the bar starts,
   the same as BallStartingPosY, equal to one half of the total screen
   height
 
 - `FinalLine`: the x position of the final line, equal to
   the bar's starting x position plus twice the bar's width (so it's
   behind the goalie).

 - `BallSpeed`: how fast the ball moves horizontally, in pixels per
   screen refresh, equal to the width of the screen divided by 100. We
   multiply this by the ball joystick's vertical axis (which lies
   between -1 and 1) to get its vertical move; this ensures the max
   vertical speed is the same as the ball's horizontal speed.
   
 - `BarJoystickBaseSpeed`: the base speed of the goalie. When the
   goalie has no acceleration, this is how fast it moves. Should
   always be smaller than the ball's (since the goalie has
   acceleration and the ball doesn't). Tweaking this value, currently
   equal to `BallSpeed / 1.5`.

 - `BarJoystickAccelIncr`: this is how much the maximum move value
   increases if the goalie continues to move in the same
   direction. This allows the goalie to accelerate, but it loses speed
   when it switches direction. This is being tweaked to find the best
   value, but it's currently `BallSpeed / 60`.
   
 - `ScreenRefreshInterval`: the result of
   `Screen('GetFlipInterval',DisplayWindow)`, this is the approximate
   number of seconds between moves / screen refreshes. We use this to
   let the guess goalie translate between seconds and moves without
   seeing `TimingSequence` (for determining lag)
 
## Default values (found in Settings.py)

 - `Experiment = 'Penalty Kick'`

 - `FixCrossJitterMean = 2`; this is determines the mean number of
   seconds to wait before the trial starts (with the fixation cross on
   the screen). For each subject, each run, we take permutation of a
   "master vector" of observations from an exponential distribution
   with this mean, add 1 to every value (so that we're pulling from an
   exponential distribution with a minimum value of 1), then round
   them all to the nearest .5. The master vector is the same for all
   subjects, all runs, but the specific permutation is
   different. Then, on trial `i` we take the `i`th value of this
   vector for the jitter.

 - `TimeToWaitAfterOutcome = 1.5`; this is number of seconds to wait
   after the game has ended (ball/bar still displayed).
   
 - `TimeToWaitWithOppPic = 2`; this is the number of seconds to wait
   with the picture of the opponent on the screen.

 - `RewardForBlockingBall = 0.5`; this is the reward obtained by P2
   for effectively blocking the ball

 - `RewardForScoring = 0.5`; this is the reward obtained by P1 for
   reaching the final line

 - `BallJoystickDeadZone = 0.1`; this is a deadzone for the the
   joystick controlling the ball to avoid capturing movements that are
   too small

 - `BarJoystickDeadZone = 0.1`; this is a deadzone for the the
   joystick controlling the bar to avoid capturing movements that are
   too small

 - `BallPauseStart = 0.3`; the number of seconds to wait after the
   trial is drawn on screen before the ball start moving. This gives
   the participant some time to examine play before they begin.
   
 - `CpuBarLagMinValue = .12`; the minimum number of seconds that bar's
   tracking of the ball can lag behind the ball's actual
   movements. This is to give it a feeling of "response time", so it
   feels more real.
   
 - `CpuBarLagDist = beta(2,5)`; the distribution of
   reaction time values. On a given trial, we take an observation from
   this distribution, multiply it by .1 (because we want values on the
   interval [0, .1]) and add it to `CpuBarLagMinValue` to get the
   cpu's "reaction time" for that trial. The value here is a beta
   distribution with alpha=2, beta=5.`

# Results

We also save another list, which contains the Settings dictionary at run
time, and the
`Results` struct, which contains the following. It will be saved in
a directory named 'behavioral' as
`pkick_P1Name_runType_P2Name(ifapplicable)_expNum.json`.

## Results list contents

 - `SubjName`: name of the subject, filled in at prompt at the
   beginning.

 - `currentRun`: what run this represents. If `runType` is
   'train', there's only one run, if it's 'experiment', then there
   are four.
         
 - `runStart`: the time (returned by PsychoPy's `GetTime`) when
   the run started

 - `trial`: the number of the current trial.

 - `trialStart`: how many seconds after `runStart` this trial started

 - `BarY`: 1xN array, where N is the number of time points in the
    trial. Contains the y position of the bar (x position is constant
    and always `Settings.BarStartingPosX`)

 - `BallPositions`: 2xN array, where N is the number of time points in
   the trial. Contains the x and y position of the bar.
   
 - `BallJoystickHistory`: 2xN array, where N is the number of time
   points in the trial. Contains the positions of the ball player's
   joystick, first position is x, second is y. Close to 0 is close to
   center.
    
 - `BarJoystickHistory`: 2xN array, where N is the number of time
   points in the trial. Contains the positions of the bar player's
   joystick, first position is x, second is y. Close to 0 is close to
   center. If `Results.Opponent` is 'cpu', then this will be [0 0].

 - `TimingSequence`: 1xN array, where N is the number of time points
   in the trial. The value is the number of seconds since the
   beginning of the trial. 
 
 - `dest`: 1x(N-1) array, where N is the number of time points in the
   trial (this has N-1 values because there's no destination on the
   first trial, since neither of the required vectors (`BallPosition`,
   `TimingSequence`) have been created yet). The value is the y
   position that the goalie is trying to reach, as returned by
   `goalie.move()`. The goalie will move as close as it can to this
   value, constrained by `maxMove`.
   
 - `accel`: 1xN array, where N is the number of time points in the
   trial. The value is the acceleration parameter, which is used to
   calculate `maxMove`. It starts out at 1 and increases by
   `BarJoystickAccelIncr` everytime the goalie is moving the same
   direction it had been going at the previous time point and they
   used traveled their `maxMove` on the previous trial (this ensures
   that the goalie's movements appear smooth; otherwise `accel` can
   get very large while the goalie is moving slowly and, if `dest`
   shifts suddenly (e.g., due to shift in strategy), the goalie can
   appear to "teleport"). If the goalie has not traveled their
   `maxMove`, then `accel` stays at its current value; when the goalie
   stops moving or changes direction, `accel` resets to 1.
 
 - `maxMove`: 1xN array, where N is the number of time points in the
   trial. The value is the maximum possible y distance the bar can
   move, which is equal to `accel * BarJoystickBaseSpeed`. Therefore,
   this increases at the same rate as `accel`.
 
 Note: `BarY`, `BallPositions`, `BallJoystickHistory`,
 `BarJoystickHistory`, `TimingSequence`, `dest`, `accel`, and
 `maxMove` are updated every "time point" in the trial. This
 corresponds to an iteration of the while loop in the `playGame`
 function, which should be the same as a screen refresh. Note also
 that they start accumulating data at start of the game, not the start
 of the trial; there's a fixation cross and a brief image of their
 opponent between the start of the trial and the start of the game. In
 particular, this means the first value of `TimingSequence` will never
 be 0, as some amount of seconds will always have passed before the
 game starts.

 - `RewardBall`: how much reward the ball received on this trial (0.5
   if the ball won, 0 else)

 - `RewardBar`: how much reward the bar received on this trial (0.5 if
   the ball lost, 0 else)

 - `Opponent`: 'cpu' or 'human'; whether the goalie was controlled by
   a human on a second joystick or a computer

 - `outcome`: 'win' or 'loss'; the outcome of the game, with respect
   to the participant/ball. So 'win' means that the ball won, 'loss'
   that the bar won.

 - `StartOfGame`: how many seconds have passed since `runStart`.

 - `trialLength`: how many seconds have passed since `StartOfGame`;
   used to check for timeout.

 - `FixCrossJitterThisTrial`: how many seconds the participant
   waited before the game started with the fixation cross on the
   screen. This is a random number from an exponential distribution
   with `Settings.TimeToWaitWithFixCross` as its mean.

 - `CpuBarLagThisTrial`: how many seconds the bar lags this
   trial. Only set if the goalie is type `react` or `guess`, this
   determines how many seconds behind the current time the goalie
   looks for the ball position to respond to. Different value every
   trial, equal to `CpuBarLagMinValue+.1*CpuBarLagDist.random()` (set
   in `goalie.trial_start()`).
