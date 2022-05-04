
import ParamFUNKTIONS as p
import RegFUNKTIONS as r
import AlgorithmValidation as a
import numpy as np
import configparser
import datetime
import matplotlib.pyplot as plt

#Loader for the Configurationfile , including Object IDs
from ConfigLoader import ConfigLoader
from JEVis import JEVis


def configuration_loader(configurationfile):
    config = configparser.ConfigParser()
    config.sections()
    config.read(configurationfile)

    # Read URL, User and PW for the JEVis-Service
    jevisUser = config['JEVis-Service']['jevisUser']
    jevisPW = config['JEVis-Service']['jevisPW']
    webservice = config['JEVis-Service']['webservice']

    # Read the model-file Name (probably also the path need to be in there!)
    modelfile = config['Models']['File']

    # Read Heater-Data (in the Case of Siosta, how much percentage of load is in fullload/partload)
    heaterdata = [''] * 2
    heaterdata[0] = float(config['Heater data sheet']['Fullload'])
    heaterdata[1] = float(config['Heater data sheet']['partial load'])

    # Read in the System assigned Names and IDs of Signals (meaning the fullload-signals for SIOSTA)
    hallcount = int(config['Systems']['System Count'])
    systems = [''] * hallcount
    Fullload_measurements = [''] * hallcount
    Fullload_variables = [''] * hallcount
    zonenames = []
    for i in range(hallcount):
        systemname = 'System ' + str(i + 1)
        systems[i] = config['Systems'][systemname].split('; ')
        Fullloadname = 'ID Fullload ' + str(i + 1)
        Fullload_measurements[i] = config['Fullload Signal Measurements'][Fullloadname]
        Fullload_variables[i] = config['Fullload Variables'][Fullloadname]
        Fullload_variables[i] = Fullload_variables[i].replace(' ', '').split(',')
        zonenames = zonenames + systems[i]

    systemnames = config['Systems']['Systemnames'].split('; ')

    # read the Zone assigned Names and IDs of Signals
    # Define the sizes of the python arrays and initializing them
    zonecount = int(config['Systems']['Zone Count'])

    weightfactor = [''] * zonecount
    horizon = [''] * zonecount
    for i in range(zonecount):
        name = 'Zone ' + str(i + 1)
        horizon[i] = int(config['control']['horizon ' + name])
        weightfactor[i] =  int(config['control']['weightfactor ' + name])

    Temperatures = [''] * zonecount
    Heaters_measurement = [''] * zonecount
    Outdoor_Temperature = config['IDs of Disturbances']['Outdoor Temperature']
    Disturbances = [''] * zonecount
    energetic_measurements = [''] * zonecount
    Heaters_variables = [''] * zonecount
    setpoint_str = [''] * zonecount
    Setpoints = [''] * zonecount
    weekend_operation = [''] * zonecount
    # Go through all Zones and read the needed Signal IDs
    for i in range(zonecount):
        # create the Zonename, that need to be searched in the Config-file
        name = 'IDs Zone ' + str(i + 1)
        # Read IDs for weekend operation recognition
        weekend_operation[i] = config['IDs for Weekend Operation'][name]
        # create the Disturbancename, that need to be searched in the Config-file
        disturbance_name = 'Outdoor-Door Zone ' + str(i + 1)
        # Read the Zone-Temperature (that is the controlled value)
        Temperatures[i] = config['IDs of Temperature Measurements'][name]
        # Read the IDs of the Measurement of the Heater-Signals
        Heaters_measurement[i] = config['IDs of Heater Measurements'][name].replace(' ', '').split(';')
        # Read the measured Disturbance-IDs (always starting with the outdoor-temperature)
        if config['IDs of Disturbances'][disturbance_name] != '':
            Disturbances[i] = Outdoor_Temperature + '; ' + config['IDs of Disturbances'][disturbance_name]
            Disturbances[i] = Disturbances[i].replace(' ', '').split(';')
        else:
            Disturbances[i] = Outdoor_Temperature
        # Read the measured Energy-IDs
        energetic_measurements[i] = config['IDs of Energy Consumer Measurements'][name].replace(' ', '').split(';')
        # Read the ID of the Heater-Signals to write on
        Heaters_variables[i] = config['IDs of Heater Variables'][name].replace(' ', '').split(';')
        for j in range(len(Heaters_variables[i])):
            Heaters_variables[i][j] = Heaters_variables[i][j].split(',')
        # Read the Setpoint-Configurations
        setpointname = 'Setpoint Zone ' + str(i + 1)
        setpoint_str = config['Setpoints'][setpointname].replace(';', ',').replace(' ', '').split(',')
        setpoint_array = [''] * int(len(setpoint_str)/2)
        time_array = [''] * int(len(setpoint_str)/2)
        if len(setpoint_str) > 2:
            for j in range(int(len(setpoint_str) / 2)):
                time_array[j] = setpoint_str[2 * j]
                setpoint_array[j] = float(setpoint_str[2 * j + 1])
        else:
            time_array = setpoint_str[0]
            setpoint_array = float(setpoint_str[1])
        Setpoints[i] = [setpoint_array, time_array]

    # Create a List with all IDs (read-IDs and write-IDs)
    ObjectIDs = [Heaters_measurement, Temperatures, Disturbances, Fullload_measurements, energetic_measurements, Heaters_variables,
                 Fullload_variables, weekend_operation]

    return ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata

#Identification-Functions:
        #importing data from JEVis using object IDs, dates and times
        #converting JEVis data into numPY array usable for parameter ID
        #Decomposed tensor model parameters from numPY data
def identification(filename,WeekendID, heaterdata, zonename, ID_heater,heaters_number,ID_disturbances,ID_temperature,ID_fullload,ID_energy,fromD,toD,fromT,toT,jevisUser,jevisPW,webservice,set_equalHeaterParameter):
    # Read and prepare measured Data of the given Timeperiod
    [Temperature,OUTTemperature,Disturbances,Heater,Energies,weekend_operation]=p.totalprep(WeekendID,heaterdata, ID_heater,heaters_number,ID_disturbances,ID_temperature,ID_fullload,ID_energy,fromD,toD,fromT,toT,jevisUser,jevisPW,webservice)
    # Parameteridentification into a decomposed Tensor, the outcome is a Python-List including all the Model-Data (Parametervector --> Value Information, Factormatrices --> Structure Information)
    Params=p.decparamIDD(Heater, Temperature, Disturbances, Energies, OUTTemperature, set_equalHeaterParameter = set_equalHeaterParameter)
    # Safe Model Data (Parametervector --> Value Information, Factormatrices --> Structure Information) as a JSON-String into the Model-File
    p.safe_model(filename, zonename, Params, fromD, toD)
    return Params
def identification_with_calibration(filename,WeekendID, heaterdata, zonename, ID_heater,heaters_number,ID_disturbances,ID_temperature,ID_fullload,ID_energy,fromD,toD,fromT,toT,jevisUser,jevisPW,webservice,set_equalHeaterParameter):
    # Read and prepare measured Data of the given Timeperiod
    [Temperature,OUTTemperature,Disturbances,Heater,Energies,weekend_operation]=p.totalprep(WeekendID,heaterdata, ID_heater,heaters_number,ID_disturbances,ID_temperature,ID_fullload,ID_energy,fromD,toD,fromT,toT,jevisUser,jevisPW,webservice)
    # Parameteridentification into a decomposed Tensor, the outcome is a Python-List including all the Model-Data (Parametervector --> Value Information, Factormatrices --> Structure Infromation, Calibrationvectors --> Calibration Information)
    Params = p.decomposed_Parameteridentification_with_calibration(Heater, Temperature, Disturbances, Energies, OUTTemperature, set_equalHeaterParameter = set_equalHeaterParameter)
    # Safe Model Data (Parametervector --> Value Information, Factormatrices --> Structure Infromation, Calibrationvectors --> Calibration Information) as a JSON-String into the Model-File
    p.safe_model_with_calibration(filename, zonename, Params, fromD, toD)
    return Params

#model validation/Plotting
def Validation(WeekendID,heaterdata, zonename, ID_heater,heaters_number,ID_disturbances,ID_temperature,ID_fullload,ID_energies,fromDv,toDv,fromTv,toTv,scale,Params,jevisUser,jevisPW,webservice):
    # Read and prepare measured Data of the given Timeperiod
    [Temperature,OUTTemperature,Disturbances,Heater,Energies,weekend_operation]=p.totalprep(WeekendID,heaterdata, ID_heater,heaters_number,ID_disturbances,ID_temperature,ID_fullload,ID_energies,fromDv,toDv,fromTv,toTv,jevisUser,jevisPW,webservice)
    # Calculating Zonetemperature-Trend with the given Signals and the Model-Data, starting with the initial-measured Temperature
    Estimated_temp=p.decvalidS(zonename, Heater, Temperature[0], Disturbances, Energies, Params)
    # Dump Data
    p.DataDump_Validation(zonename, OUTTemperature, Estimated_temp, Heater, Disturbances, Energies, fromDv, toDv, fromTv,toTv)
    # Plotting measured Data and the calculated Temperature-Trend
    p.Modelvalidation_plot(zonename, fromDv,toDv,fromTv,toTv)
    return Estimated_temp
def Validation_with_calibration(WeekendID,heaterdata, zonename, ID_heater,heaters_number,ID_disturbances,ID_temperature,ID_fullload,ID_energies,fromDv,toDv,fromTv,toTv,scale,Params,jevisUser,jevisPW,webservice):
    # Read and prepare measured Data of the given Timeperiod
    [Temperature,OUTTemperature,Disturbances,Heater,Energies,weekend_operation]=p.totalprep(WeekendID,heaterdata, ID_heater,heaters_number,ID_disturbances,ID_temperature,ID_fullload,ID_energies,fromDv,toDv,fromTv,toTv,jevisUser,jevisPW,webservice)
    # Calculating Zonetemperature-Trend with the given Signals and the Model-Data, starting with the initial-measured Temperature
    Estimated_temp=p.decvalidS_with_calibration(zonename, Heater, Temperature[0], Disturbances, Energies, Params)
    # Dump Data
    p.DataDump_Validation(zonename, OUTTemperature, Estimated_temp, Heater, Disturbances, Energies, fromDv, toDv,
                          fromTv, toTv)
    # Plotting measured Data and the calculated Temperature-Trend
    p.Modelvalidation_plot(zonename, fromDv, toDv, fromTv, toTv)
    return Estimated_temp

 #Regulation-Functions:
        #importing latest disturbances and temperature data from JEVis
        # (Disturbance Observing)
        #using the data to calculate heater signal values (predictive control)
        #preparing data to write in JEVis
        #write data in JEVis (seperate object IDs for write)

def Regulation(filename, TimeID, WeekendID, heaterdata, zonename,weightening_ratio,IDs_disturbances, ID_temperature,ID_heaters,ID_fullload,ID_energy,Setpoints,Heaters_number,fullload_hall,horizon,username,password,webservice):
    # loading model data of a given zone into a python-list from the modelfile
    ModellParam = r.load_model(filename, zonename)
    # read the current measured Data needed for the Control-Algortihm (Disturbances, Temperature, Heater)
    jevisValues=JEVis.controlRead(WeekendID,ID_heaters,IDs_disturbances, ID_energy,ID_temperature,username,password,webservice)
    # Read the current time and convert to a date- and a time-string
    [now_day, now_time] = r.Time_reader(TimeID,username,password,webservice)
    # create a Array of Setpoints for the given Control-Horizon
    Setpoint = r.Set_Setpoint(Setpoints[0], Setpoints[1], jevisValues.weekend_operation, now_day, now_time, horizon)
    print("Setpoint")
    print(Setpoint)
    # Control-Algorithm, calculating the optimal Controlvalues with the given Weightening for the next 3 Timesteps
    Controlvalues = r.Control(heaterdata, jevisValues.temperature_vals,Heaters_number,jevisValues.dist_vals,jevisValues.energie_vals, Setpoint, ModellParam, fullload_hall,
                              weightening_ratio,horizon)
    # Split the Controlvalues into Heater (on/off) and fullload (on/off) signals
    [fullload, heaters] = r.Fullload_sep(heaterdata, Controlvalues, jevisValues.heaters_vals, Heaters_number, fullload_hall)
    return fullload, heaters
def Regulation_calibration(filename, TimeID, WeekendID, heaterdata, zonename,weightening_ratio,IDs_disturbances, ID_temperature,ID_heaters,ID_fullload,ID_energy,Setpoints,Heaters_number,fullload_hall,horizon,username,password,webservice):
    # loading model data of a given zone into a python-list from the modelfile
    ModellParam = r.load_model_with_calibration(filename, zonename)
    # read the current measured Data needed for the Control-Algortihm (Disturbances, Temperature, Heater)
    jevisValues = JEVis.controlRead(WeekendID,ID_heaters,IDs_disturbances, ID_energy, ID_temperature, username, password, webservice)
    # Read the current time and convert to a date- and a time-string
    [now_day, now_time] = r.Time_reader(TimeID,username,password,webservice)
    # create a Array of Setpoints for the given Control-Horizon
    Setpoint = r.Set_Setpoint(Setpoints[0], Setpoints[1], jevisValues.weekend_operation, now_day, now_time, horizon)
    # Control-Algorithm, calculating the optimal Controlvalues with the given Weightening for the next 3 Timesteps
    Controlvalues = r.Control_with_calibration(heaterdata, jevisValues.temperature_vals,Heaters_number,jevisValues.dist_vals,jevisValues.energie_vals, Setpoint, ModellParam, fullload_hall,
                              weightening_ratio,horizon)
    # Split the Controlvalues (0 / 1 / 2) into Heater ( on(1) / off(0) ) and fullload ( on(1) / off(0) ) signals
    [fullload, heaters] = r.Fullload_sep(heaterdata, Controlvalues, jevisValues.heaters_vals, Heaters_number, fullload_hall)
    return fullload, heaters

########## CALL - FUNCTIONS ##########
# Modelidentifcation: Call Functions for the model and parameter identifier
    # Loading data from JEVis and prepare Data (e.g. generating 5 min intervals)
    # Creating Modelstructure and calculating parameters
    # Write Models into Models.txt / JEVis
def modelidentification(zonename, configurationfile, fromD, toD, calibration='true', set_equalHeaterParameter='false'):
    # zonename can be: Zone 1, System 1 or all
    # load set-up information of all zones
    [ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = configuration_loader(configurationfile)
    # ObjectIDs = [Heaters_measurement, Temperatures, Disturbances, Fullload_measurements, Heaters_variables, Fullload_variables]

    # Modelidentification for all Zones
    if zonename == 'all':
        # ObjectIDs include [Heaters_measurement, Temperatures, Disturbances, Fullload_measurements, Heaters_variables, Fullload_variables]
        i = 0
        for j in range(len(systems)):
            # Iteration through all halls/systems j
            for n in range(len(systems[j])):
                # Iteration through the zones n of hall/system j
                if calibration=='true':
                    # Starting the identification-Function given above
                    identification_with_calibration(modelfile,ObjectIDs[7][i], heaterdata, zonenames[i], ObjectIDs[0][i], np.size(ObjectIDs[0][i]),
                                                ObjectIDs[2][i],
                                                ObjectIDs[1][i], ObjectIDs[3][j], ObjectIDs[4][i], fromD, toD, '00', '00', jevisUser,
                                                jevisPW, webservice, set_equalHeaterParameter)
                elif calibration=='false':
                    # Starting the identification-Function given above
                    identification(modelfile,ObjectIDs[7][i], heaterdata, zonenames[i], ObjectIDs[0][i], np.size(ObjectIDs[0][i]),
                                                    ObjectIDs[2][i],
                                                    ObjectIDs[1][i], ObjectIDs[3][j], ObjectIDs[4][i], fromD, toD, '00', '00', jevisUser,
                                                    jevisPW, webservice, set_equalHeaterParameter)
                else:
                    print('ERROR: calibration-variable can only be true or false!')
                i = i + 1
    elif zonename in systemnames:
        # Modelidentifiction for one system (e.g. Hall 1 and 3 (LF))
        # create index array for the zone according their position in the configuration-arrays
        index = systems
        i = 0
        for j in range(np.size(systems)):
            for n in range(np.size(systems[j])):
                index[j][n] = i
                i = i + 1
        j = systemnames.index(zonename)
        for n in range(len(systems[j])):
            # Iteration through the zones n of hall/system j
            if calibration == 'true':
                # Starting the identification-Function given above
                identification_with_calibration(modelfile,ObjectIDs[7][index[j][n]], heaterdata, zonenames[index[j][n]], ObjectIDs[0][index[j][n]],
                                                np.size(ObjectIDs[0][index[j][n]]),
                                                ObjectIDs[2][index[j][n]],
                                                ObjectIDs[1][index[j][n]], ObjectIDs[3][j], ObjectIDs[4][index[j][n]], fromD, toD, '00',
                                                '00', jevisUser,
                                                jevisPW, webservice,set_equalHeaterParameter)
            elif calibration == 'false':
                # Starting the identification-Function given above
                identification(modelfile, ObjectIDs[7][index[j][n]], heaterdata, zonenames[index[j][n]], ObjectIDs[0][index[j][n]], np.size(ObjectIDs[0][index[j][n]]),
                               ObjectIDs[2][index[j][n]],
                               ObjectIDs[1][index[j][n]], ObjectIDs[3][j], ObjectIDs[4][index[j][n]], fromD, toD, '00', '00', jevisUser,
                               jevisPW, webservice, set_equalHeaterParameter)
            else:
                print('ERROR: calibration-variable can only be true or false!')
            i = i + 1

    else:
        # Modelidentification of only one zone
        # Figure out the Position of the IDs associated to the given Zone
        i = zonenames.index(zonename)
        for list in systems:
            for element in list:
                if element == zonename:
                    j = systems.index(list)
        # Identification of the given Zone
        if calibration=='true':
            # Starting the identification-Function given above
            identification_with_calibration(modelfile,ObjectIDs[7][i], heaterdata, zonenames[i], ObjectIDs[0][i], np.size(ObjectIDs[0][i]),
                                        ObjectIDs[2][i], ObjectIDs[1][i], ObjectIDs[3][j], ObjectIDs[4][i], fromD, toD, '00', '00',
                                        jevisUser, jevisPW, webservice,set_equalHeaterParameter)
        elif calibration=='false':
            # Starting the identification-Function given above
            identification(modelfile,ObjectIDs[7][i], heaterdata, zonenames[i], ObjectIDs[0][i], np.size(ObjectIDs[0][i]),
                                            ObjectIDs[2][i], ObjectIDs[1][i], ObjectIDs[3][j], ObjectIDs[4][i], fromD, toD, '00', '00',
                                            jevisUser, jevisPW, webservice, set_equalHeaterParameter)
        else:
            print('ERROR: calibration-variable can only be true or false!')

# validation-plot-functions: call-functions for the ploting
    # ploting simulation results over a choosen timeperiod with the recent models
def validation_plot(zonename, configurationfile, fromDv, toDv,calibration='true'):
    # load set-up information of all zones
    [ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = configuration_loader(configurationfile)
    if zonename == 'all':
        # Plotting of all zones i
        i = 0
        for j in range(np.size(systems)):
            # Iteration through all halls/systems j
            for n in range(np.size(systems[j])):
                # Iteration through the zones n of hall/system j
                if calibration=='true':
                    # load model-data into a python-list from the modelfile of the given zone
                    Params = r.load_model_with_calibration(modelfile, zonenames[i])
                    # Starting the Plotting-Function given above
                    Validation_with_calibration(ObjectIDs[7][i],heaterdata, zonenames[i],ObjectIDs[0][i], np.size(ObjectIDs[0][i]), ObjectIDs[2][i],
                                            ObjectIDs[1][i],
                                            ObjectIDs[3][j], ObjectIDs[4][i], fromDv, toDv, '00',
                                            '00', 0, Params, jevisUser, jevisPW, webservice)
                elif calibration=='false':
                    # load model-data into a python-list from the modelfile of the given zone
                    Params = r.load_model(modelfile, zonenames[i])
                    # Starting the Plotting-Function given above
                    Validation(ObjectIDs[7][i],heaterdata, zonenames[i], ObjectIDs[0][i], np.size(ObjectIDs[0][i]), ObjectIDs[2][i],
                               ObjectIDs[1][i],
                               ObjectIDs[3][j], ObjectIDs[4][i], fromDv, toDv, '00',
                               '00', 0, Params, jevisUser, jevisPW, webservice)
                else:
                    print('ERROR: calibration-variable can only be true or false!')
                i = i + 1
    elif zonename in systemnames:
        # Modelidentifiction for one system (e.g. Hall 1 and 3 (LF))
        # create index array for the zone according their position in the configuration-arrays
        index = systems
        i = 0
        for j in range(np.size(systems)):
            for n in range(np.size(systems[j])):
                index[j][n] = i
                i = i + 1
        j = systemnames.index(zonename)
        for n in range(len(systems[j])):
            # Iteration through the zones n of hall/system j
            if calibration == 'true':
                # load model-data into a python-list from the modelfile of the given zone
                Params = r.load_model_with_calibration(modelfile, zonenames[index[j][n]])
                # Starting the Plotting-Function given above
                Validation_with_calibration(ObjectIDs[7][index[j][n]], heaterdata, zonenames[index[j][n]], ObjectIDs[0][index[j][n]], np.size(ObjectIDs[0][index[j][n]]),
                                            ObjectIDs[2][index[j][n]],
                                            ObjectIDs[1][index[j][n]],
                                            ObjectIDs[3][j], ObjectIDs[4][index[j][n]], fromDv, toDv, '00',
                                            '00', 0, Params, jevisUser, jevisPW, webservice)
            elif calibration == 'false':
                # load model-data into a python-list from the modelfile of the given zone
                Params = r.load_model(modelfile, zonenames[index[j][n]])
                # Starting the Plotting-Function given above
                Validation(ObjectIDs[7][index[j][n]], heaterdata, zonenames[index[j][n]], ObjectIDs[0][index[j][n]], np.size(ObjectIDs[0][index[j][n]]), ObjectIDs[2][index[j][n]],
                           ObjectIDs[1][index[j][n]],
                           ObjectIDs[3][j], ObjectIDs[4][index[j][n]], fromDv, toDv, '00',
                           '00', 0, Params, jevisUser, jevisPW, webservice)
            else:
                print('ERROR: calibration-variable can only be true or false!')

    else:
        # Plotting of just one Zone
        # Figure out the Position of the IDs associated to the given Zone
        i = zonenames.index(zonename)
        for list in systems:
            for element in list:
                if element == zonename:
                    j = systems.index(list)
        if calibration=='true':
            # load model-data into a python-list from the modelfile of the given zone
            Params = r.load_model_with_calibration(modelfile, zonenames[i])
            # Starting the Plotting-Function given above
            Validation_with_calibration(ObjectIDs[7][i], heaterdata, zonenames[i],ObjectIDs[0][i], np.size(ObjectIDs[0][i]), ObjectIDs[2][i], ObjectIDs[1][i],
                                    ObjectIDs[3][j], ObjectIDs[4][i], fromDv, toDv, '00', '00', 0, Params, jevisUser, jevisPW,
                                    webservice)
        elif calibration=='false':
            # load model-data into a python-list from the modelfile of the given zone
            Params = r.load_model(modelfile, zonenames[i])
            # Starting the Plotting-Function given above
            Validation(ObjectIDs[7][i], heaterdata, zonenames[i], ObjectIDs[0][i], np.size(ObjectIDs[0][i]), ObjectIDs[2][i], ObjectIDs[1][i],
                       ObjectIDs[3][j], ObjectIDs[4][i], fromDv,
                       toDv, '00', '00', 0, Params, jevisUser, jevisPW, webservice)
        else:
            print('ERROR: calibration-variable can only be true or false!')

# Control-Functions: Call Functions for the Regulation-Functions:
    # configuration loading
    # Model loading (calibrated or uncalibrated Model)
    # (Disturbance Observing)
    # Regulation - Algorithms
    # Writing on JEVis

def Controlfunction(systemname,configurationfile,TimeID,calibration='true'):
    [ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = configuration_loader(configurationfile)
    # weightfactor: Ratio of the Cost of comfort (setpoint fulfillment) versus Cost of energy consumption (Sum of the heater/input/control signals)
    if systemname == 'all':
        # Control of all zones i
        index = systems
        # Creating array of indices for the different zones according to their representation in the ID-Arrays
        i=0
        for j in range(np.size(systems)):
            for n in range(np.size(systems[j])):
                index[j][n] = i
                i=i+1
        # Iteration through all zones
        for j in range(np.size(systems)):
            print(systemnames[j])
            # initialize empty arrays for the calculated control-signals
            fullload = [''] * np.size(systems[j])
            heaters = [''] * np.size(systems[j])
            for n in range(np.size(systems[j])):
                print('Zone '+str(systems[j][n]+1))
                if calibration=='true':
                    # Starting Regulation-Function given above
                    #filename, TimeID, WeekendID, heaterdata, zonename,weightening_ratio,IDs_disturbances, ID_temperature,ID_heaters,ID_fullload,ID_energy,Setpoints,Heaters_number,fullload_hall,horizon,username,password,webservice
                    [fullload[n], heaters[n]] = Regulation_calibration(modelfile, TimeID, ObjectIDs[7][index[j][n]], heaterdata, zonenames[index[j][n]],weightfactor[index[j][n]], ObjectIDs[2][index[j][n]], ObjectIDs[1][index[j][n]], ObjectIDs[0][index[j][n]], ObjectIDs[3][j], ObjectIDs[4][index[j][n]], Setpoints[index[j][n]], len(ObjectIDs[5][index[j][n]]),[0,0,0],horizon[index[j][n]],jevisUser, jevisPW,webservice)
                elif calibration=='false':
                    # Starting Regulation-Function given above
                    [fullload[n], heaters[n]] = Regulation(modelfile, TimeID, ObjectIDs[7][index[j][n]], heaterdata, zonenames[index[j][n]],
                                                                       weightfactor[index[j][n]], ObjectIDs[2][index[j][n]],
                                                                       ObjectIDs[1][index[j][n]],
                                                                       ObjectIDs[0][index[j][n]], ObjectIDs[3][j], ObjectIDs[4][index[j][n]],
                                                                       Setpoints[index[j][n]],
                                                                       len(ObjectIDs[5][index[j][n]]), [0, 0, 0],horizon[index[j][n]],
                                                                       jevisUser, jevisPW, webservice)
                else:
                    print('ERROR: calibration-variable can only be true or false!')

            # fullload set parameter over the next 3 timesteps: if in a Hall is fullload set by one Zone, all other Zones of that hall need to be in fullload too!
            fullload_hall = np.zeros(int(len(fullload[0]) / len(ObjectIDs[5][index[j][0]])))
            # Iteration through all systems and check if a Zone in the system needs Fullload
            # if so, all Control-Signals of the Zones of that system need to be recalculated, only allowing fullload or off signals (2 / 0)
            # Iteration through the systems
            for n in range(len(systems[j])):
                # Iteration through the 3 timesteps, that will be written to JEVis
                for z in range(len(fullload_hall)):
                    # Iteration through the zones of a system
                    for i in range(z * len(ObjectIDs[5][index[j][n]]), (z+1) * len(ObjectIDs[5][index[j][n]])):
                        # check if Zone of the system needs fullload
                        if fullload[n][i] == 1:
                            fullload_hall[z] = 1
                if calibration=='true':
                    # Starting Regulation-Function given above, with the given fullload-demand
                    [fullload[n], heaters[n]] = Regulation_calibration(modelfile, TimeID, ObjectIDs[7][index[j][n]], heaterdata, zonenames[index[j][n]],weightfactor[index[j][n]], ObjectIDs[2][index[j][n]],
                                                         ObjectIDs[1][index[j][n]], ObjectIDs[0][index[j][n]], ObjectIDs[3][j], ObjectIDs[4][index[j][n]],
                                                         Setpoints[index[j][n]], len(ObjectIDs[0][index[j][n]]), fullload_hall,horizon[index[j][n]], jevisUser, jevisPW,webservice)
                elif calibration=='false':
                    # Starting Regulation-Function given above, with the given fullload-demand
                    [fullload[n], heaters[n]] = Regulation(modelfile, TimeID, ObjectIDs[7][index[j][n]], heaterdata, zonenames[index[j][n]],weightfactor[index[j][n]], ObjectIDs[2][index[j][n]],
                                                         ObjectIDs[1][index[j][n]], ObjectIDs[0][index[j][n]], ObjectIDs[3][j], ObjectIDs[4][index[j][n]],
                                                         Setpoints[index[j][n]], len(ObjectIDs[0][index[j][n]]), fullload_hall,horizon[index[j][n]], jevisUser, jevisPW,webservice)
                else:
                    print('ERROR: calibration-variable can only be true or false!')
                # write controlvalues into JEVis
                JEVis.controlWrite(ObjectIDs[5][index[j][n]], ObjectIDs[6][j], fullload[n], heaters[n], jevisUser, jevisPW,webservice)
    elif systemname in systemnames:
        # Systemwise control of a area, where one fullload switch controls multiple zones at once!
        [ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = configuration_loader(configurationfile)
        # Control of all zones i of one system (hall)
        # create index array for the zone according their position in the configuration-arrays
        index = systems
        i = 0
        for j in range(np.size(systems)):
            for n in range(np.size(systems[j])):
                index[j][n] = i
                i = i + 1
        j = systemnames.index(systemname)
        # initialize empty arrays for the calculated control-signals
        fullload = [''] * np.size(systems[j])
        heaters = [''] * np.size(systems[j])
        # Iteration through all Zones of one system
        for n in range(np.size(systems[j])):
            print(zonenames[index[j][n]])
            if calibration=='true':
                # Starting Regulation-Function given above
                [fullload[n], heaters[n]] = Regulation_calibration(modelfile, TimeID, ObjectIDs[7][index[j][n]], heaterdata, zonenames[index[j][n]],weightfactor[index[j][n]], ObjectIDs[2][index[j][n]],
                                                         ObjectIDs[1][index[j][n]], ObjectIDs[0][index[j][n]], ObjectIDs[3][j], ObjectIDs[4][index[j][n]],
                                                         Setpoints[index[j][n]], len(ObjectIDs[0][index[j][n]]), [0, 0, 0],horizon[index[j][n]], jevisUser, jevisPW,webservice)
            elif calibration=='false':
                # Starting Regulation-Function given above
                [fullload[n], heaters[n]] = Regulation(modelfile, TimeID, ObjectIDs[7][index[j][n]], heaterdata, zonenames[index[j][n]],weightfactor[index[j][n]], ObjectIDs[2][index[j][n]],
                                                         ObjectIDs[1][index[j][n]], ObjectIDs[0][index[j][n]], ObjectIDs[3][j], ObjectIDs[4][index[j][n]],
                                                         Setpoints[index[j][n]], len(ObjectIDs[0][index[j][n]]), [0, 0, 0],horizon[index[j][n]], jevisUser, jevisPW,webservice)
            else:
                print('ERROR: calibration-variable can only be true or false!')
        # fullload set parameter over the next 3 timesteps: if in a Hall is fullload set by one Zone, all other Zones of that hall need to be in fullload too!
        # Iteration through the system and check if a Zone in the system needs Fullload
        # if so, all Control-Signals of the Zones of that system need to be recalculated, only allowing fullload or off signals (2 / 0)
        fullload_hall = np.zeros(int(len(fullload[0]) / len(ObjectIDs[5][index[j][0]])))
        for n in range(np.size(systems[j])):
            # Iteration through the 3 timesteps, that will be written to JEVis
            for z in range(np.size(fullload_hall)):
                # Iteration through the zones of a system
                for i in range(z * len(ObjectIDs[5][index[j][n]]), (z+1) * len(ObjectIDs[5][index[j][n]])):
                    # check if Zone of the system needs fullload
                    if fullload[n][i] == 1:
                        fullload_hall[z] = 1
            print(zonenames[index[j][n]])
            if calibration=='true':
                # Starting Regulation-Function given above, with the given fullload-demand
                [fullload[n], heaters[n]] = Regulation_calibration(modelfile, TimeID, ObjectIDs[7][index[j][n]], heaterdata, zonenames[index[j][n]],weightfactor[index[j][n]], ObjectIDs[2][index[j][n]],
                                                         ObjectIDs[1][index[j][n]], ObjectIDs[0][index[j][n]], ObjectIDs[3][j], ObjectIDs[4][index[j][n]],
                                                         Setpoints[index[j][n]], len(ObjectIDs[0][index[j][n]]), fullload_hall,horizon[index[j][n]], jevisUser, jevisPW,webservice)
            elif calibration=='false':
                # Starting Regulation-Function given above, with the given fullload-demand
                [fullload[n], heaters[n]] = Regulation(modelfile, TimeID, ObjectIDs[7][index[j][n]], heaterdata, zonenames[index[j][n]],weightfactor[index[j][n]], ObjectIDs[2][index[j][n]],
                                                         ObjectIDs[1][index[j][n]], ObjectIDs[0][index[j][n]], ObjectIDs[3][j], ObjectIDs[4][index[j][n]],
                                                         Setpoints[index[j][n]], len(ObjectIDs[0][index[j][n]]), fullload_hall,horizon[index[j][n]], jevisUser, jevisPW,webservice)
            else:
                print('ERROR: calibration-variable can only be true or false!')
                # write controlvalues into JEVis
            r.Control_write(ObjectIDs[5][index[j][n]], ObjectIDs[6][j], fullload[n], heaters[n], jevisUser, jevisPW,webservice)
    elif systemname in zonenames:
        zonename = systemname
        # zonewise control (In Siosta zonewise control is not correct, if multiple zones are controlled by the same switch/operator, because of the fullload signal!)
        # weightening_ratio: Ratio of the Cost of comfort (setpoint fulfillment) versus Cost of energy consumption
        [ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = configuration_loader(configurationfile)
        # Control of one zone i, checking index for the zone in configuration-arrays
        index = systems
        i = zonenames.index(zonename)
        for list in systems:
            for element in list:
                if element == zonename:
                    j = systems.index(list)
        # initialize empty arrays for the calculated control-signals
        fullload = ['']
        heaters = ['']
        if calibration=='true':
            # Starting Regulation-Function given above
            [fullload, heaters] = Regulation_calibration(modelfile, TimeID, ObjectIDs[7][i], heaterdata, zonenames[i],weightfactor[i], ObjectIDs[2][i],
                                                         ObjectIDs[1][i], ObjectIDs[0][i], ObjectIDs[3][j], ObjectIDs[4][i],
                                                         Setpoints[i], len(ObjectIDs[0][i]), [0, 0, 0], horizon[i], jevisUser, jevisPW,webservice)
        elif calibration=='false':
            # Starting Regulation-Function given above
            [fullload, heaters] = Regulation(modelfile, TimeID, ObjectIDs[7][i], heaterdata, zonenames[i],weightfactor[i], ObjectIDs[2][i],
                                                         ObjectIDs[1][i], ObjectIDs[0][i], ObjectIDs[3][j], ObjectIDs[4][i],
                                                         Setpoints[i], len(ObjectIDs[0][i]), [0, 0, 0],horizon[i], jevisUser, jevisPW,webservice)
        else:
            print('ERROR: calibration-variable can only be true or false!')
        # write controlvalues into JEVis
        r.Control_write(ObjectIDs[5][i], ObjectIDs[6][j], fullload, heaters, jevisUser, jevisPW,webservice)