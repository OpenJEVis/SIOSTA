# This is the Run-File for the implementation in the demonstrator.
# The Script checks which mode is defined in the configuration-file to run (Parameteridentification-Algorithm or/and Control-Algorithm)
# and runs the choosen mode

# First the libraries get imported.
import configparser

### Modelidentification Methods ###
#from total import modelidentification

### Control Methods ###
from ConfigLoader import ConfigLoader
from total import Control

import os
# Change the working directory to the script-path.
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# Name of the configuration-file used (where all Parameters and Set-Ups are defined)
configurationfile = 'config.txt'

configLoader = ConfigLoader(configurationfile)
confData = configLoader.load()
control = Control(configurationfile)


if confData.runModellIdentification == 'yes':

    if len(confData.runSystems) > 1:
        for i in range(len(confData.runSystems)):
            control.modelidentification(confData.runSystems[i], configurationfile, confData.modelidentificationFrom, confData.modelidentificationTo, calibration=confData.calibrationValue, set_equalHeaterParameter ='true')
    else:
        control.modelidentification(confData.system[0], configurationfile, confData.modelidentificationFrom, confData.modelidentificationTo, calibration=confData.calibrationValue, set_equalHeaterParameter = 'true')

# check and run of the control-algorithm
if confData.runControl == 'yes':
    if len(confData.runSystems) > 1:
        print("test")
        for i in range(len(confData.runSystems)):
            control.Controlfunction(confData.system[i], configurationfile, confData.timeID,
                            calibration=confData.calibrationValue)
    elif len(confData.runSystems) == 1:
        print("test2")
        control.Controlfunction(confData.system[0], configurationfile, confData.timeID, calibration=confData.calibrationValue)