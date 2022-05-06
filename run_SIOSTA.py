# This is the Run-File for the implementation in the demonstrator.
# The Script checks which mode is defined in the configuration-file to run (Parameteridentification-Algorithm or/and Control-Algorithm)
# and runs the choosen mode

# First the libraries get imported.
import configparser

### Modelidentification Methods ###
#from total import modelidentification

### Control Methods ###
from total import Control

import os
# Change the working directory to the script-path.
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# Name of the configuration-file used (where all Parameters and Set-Ups are defined)
configurationfile = 'config.txt'

config = configparser.ConfigParser()
config.sections()
config.read(configurationfile)
control = Control(configurationfile)

system = config['run']['System']
system = system.split(', ')
calibrationvalue = config['run']['calibration']

# check and run of the modelidentification-algorithm
if config['modelidentification']['run'] == 'yes':
    fromTime = config['modelidentification']['from']
    toTime = config['modelidentification']['to']
    if len(system) > 1:
        for i in range(len(system)):
            control.modelidentification(system[i], configurationfile, fromTime, toTime, calibration=calibrationvalue, set_equalHeaterParameter = 'true')
    else:
        control.modelidentification(system[0], configurationfile, fromTime, toTime, calibration=calibrationvalue, set_equalHeaterParameter = 'true')

# check and run of the control-algorithm
if config['control']['run'] == 'yes':
    TimeID = config['run']['TimeID']
    #horizonperiod = int(config['control']['horizon'])
    #weightfactor = int(config['control']['weightfactor'])
    if len(system) > 1:
        print("test")
        for i in range(len(system)):
            control.Controlfunction(system[i], configurationfile, TimeID,
                            calibration=calibrationvalue)
    elif len(system) == 1:
        print("test2")
        control.Controlfunction(system[0], configurationfile, TimeID, calibration=calibrationvalue)