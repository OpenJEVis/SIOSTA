# This is the Run-File for the implementation in the demonstrator.
# The Script checks which mode is defined in the configuration-file to run (Parameteridentification-Algorithm or/and Control-Algorithm)
# and runs the choosen mode

# First the libraries get imported.
import configparser

### Modelidentification Methods ###
#from total import modelidentification

### Control Methods ###
import sys

from ConfigLoader import ConfigLoader
from Control import Control

import os
# Change the working directory to the script-path.
os.chdir(os.path.dirname(os.path.realpath(__file__)))
#print(sys.argv[0])
# Name of the configuration-file used (where all Parameters and Set-Ups are defined)
configurationfile = sys.argv[1]


configLoader = ConfigLoader(configurationfile)
confData = configLoader.load()
print(confData)
control = Control(confData)




if confData.runModellIdentification == 'yes':

    if len(confData.runSystems) > 1:
        for i in range(len(confData.runSystems)):
            control.modelidentification(confData.runSystems[i],  confData.modelidentificationFrom, confData.modelidentificationTo, calibration=confData.calibrationValue, set_equalHeaterParameter ='true')
    else:
        control.modelidentification(confData.runSystems[0],  confData.modelidentificationFrom, confData.modelidentificationTo, calibration=confData.calibrationValue, set_equalHeaterParameter = 'true')

# check and run of the control-algorithm
print(confData.runControl)
if confData.runControl == 'yes':
    if len(confData.runSystems) > 1:
        print("test")
        for i in range(len(confData.runSystems)):
            control.Controlfunction(confData.runSystems[i], configurationfile,
                            calibration=confData.calibrationValue)
    elif len(confData.runSystems) == 1:
        print("test2")
        control.Controlfunction(confData.runSystems[0], configurationfile, calibration=confData.calibrationValue)