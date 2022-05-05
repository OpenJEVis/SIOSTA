
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
    #print(ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata)
    print(Setpoints)
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
    print(Setpoints)
    # loading model data of a given zone into a python-list from the modelfile
    ModellParam = r.load_model_with_calibration(filename, zonename)
    # read the current measured Data needed for the Control-Algortihm (Disturbances, Temperature, Heater)
    jevisValues = JEVis.controlRead(WeekendID,ID_heaters,IDs_disturbances, ID_energy, ID_temperature, username, password, webservice)
    # Read the current time and convert to a date- and a time-string
    [now_day, now_time] = r.Time_reader(TimeID,username,password,webservice)
    # create a Array of Setpoints for the given Control-Horizon
    print(Setpoints)
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
    #[ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = ConfigLoader.configuration_loader(configurationfile)
    configData = ConfigLoader.configuration_loader(configurationfile)
    printconfig(configurationfile)
    # ObjectIDs = [Heaters_measurement, Temperatures, Disturbances, Fullload_measurements, Heaters_variables, Fullload_variables]

    # Modelidentification for all Zones
    if zonename == 'all':
        # ObjectIDs include [Heaters_measurement, Temperatures, Disturbances, Fullload_measurements, Heaters_variables, Fullload_variables]
        i = 0
        for j in range(len(configData.systems)):
            # Iteration through all halls/systems j
            for n in range(len(configData.systems[j])):
                # Iteration through the zones n of hall/system j
                if calibration=='true':
                    # Starting the identification-Function given above
                    identification_with_calibration(configData.modelfile,configData.objectIds_2[7][i], configData.heaterdata, configData.zonenames[i], configData.objectIds_2[0][i], np.size(configData.objectIds_2[0][i]),
                                                configData.objectIds_2[2][i],
                                                configData.objectIds_2[1][i], configData.objectIds_2[3][j], configData.objectIds_2[4][i], fromD, toD, '00', '00', configData.jevisUser,
                                                configData.jevisPW, configData.webservice, set_equalHeaterParameter)
                elif calibration=='false':
                    # Starting the identification-Function given above
                    identification(configData.modelfile,configData.objectIds_2[7][i], configData.heaterdata, configData.zonenames[i], configData.objectIds_2[0][i], np.size(configData.objectIds_2[0][i]),
                                                    configData.objectIds_2[2][i],
                                                    configData.objectIds_2[1][i], configData.objectIds_2[3][j], configData.objectIds_2[4][i], fromD, toD, '00', '00', configData.jevisUser,
                                                    configData.jevisPW, configData.webservice, set_equalHeaterParameter)
                else:
                    print('ERROR: calibration-variable can only be true or false!')
                i = i + 1
    elif zonename in configData.systemnames:
        # Modelidentifiction for one system (e.g. Hall 1 and 3 (LF))
        # create index array for the zone according their position in the configuration-arrays
        index = configData.systems
        i = 0
        for j in range(np.size(configData.systems)):
            for n in range(np.size(configData.systems[j])):
                index[j][n] = i
                i = i + 1
        j = configData.systemnames.index(zonename)
        for n in range(len(configData.systems[j])):
            # Iteration through the zones n of hall/system j
            if calibration == 'true':
                # Starting the identification-Function given above
                identification_with_calibration(configData.modelfile,configData.objectIds_2[7][index[j][n]], configData.heaterdata, configData.zonenames[index[j][n]], configData.objectIds_2[0][index[j][n]],
                                                np.size(configData.objectIds_2[0][index[j][n]]),
                                                configData.objectIds_2[2][index[j][n]],
                                                configData.objectIds_2[1][index[j][n]], configData.objectIds_2[3][j], configData.objectIds_2[4][index[j][n]], fromD, toD, '00',
                                                '00', configData.jevisUser,
                                                configData.jevisPW, configData.webservice,set_equalHeaterParameter)
            elif calibration == 'false':
                # Starting the identification-Function given above
                identification(configData.modelfile, configData.objectIds_2[7][index[j][n]], configData.heaterdata, configData.zonenames[index[j][n]], configData.objectIds_2[0][index[j][n]], np.size(configData.objectIds[0][index[j][n]]),
                               configData.objectIds_2[2][index[j][n]],
                               configData.objectIds_2[1][index[j][n]], configData.objectIds_2[3][j], configData.objectIds_2[4][index[j][n]], fromD, toD, '00', '00', configData.jevisUser,
                               configData.jevisPW, configData.webservice, set_equalHeaterParameter)
            else:
                print('ERROR: calibration-variable can only be true or false!')
            i = i + 1

    else:
        # Modelidentification of only one zone
        # Figure out the Position of the IDs associated to the given Zone
        i = configData.zonenames.index(zonename)
        print("zone name")
        print(i)
        for list in configData.systems:
            for element in list:
                if element == zonename:
                    j = configData.systems.index(list)
        # Identification of the given Zone
        if calibration=='true':
            # Starting the identification-Function given above
            identification_with_calibration(configData.modelfile,configData.objectIds_2[7][i], configData.heaterdata, configData.zonenames[i], configData.objectIds_2[0][i], np.size(configData.objectIds_2[0][i]),
                                        configData.objectIds_2[2][i], configData.objectIds_2[1][i], configData.objectIds_2[3][j], configData.objectIds_2[4][i], fromD, toD, '00', '00',
                                        configData.jevisUser, configData.jevisPW, configData.webservice,set_equalHeaterParameter)
        elif calibration=='false':
            # Starting the identification-Function given above
            identification(configData.modelfile,configData.objectIds_2[7][i], configData.heaterdata, configData.zonenames[i], configData.objectIds_2[0][i], np.size(configData.objectIds_2[0][i]),
                                            configData.objectIds_2[2][i], configData.objectIds_2[1][i], configData.objectIds_2[3][j], configData.objectIds_2[4][i], fromD, toD, '00', '00',
                                            configData.jevisUser, configData.jevisPW, configData.webservice, set_equalHeaterParameter)
        else:
            print('ERROR: calibration-variable can only be true or false!')


def printconfig(configurationfile):

    ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata = (configuration_loader(configurationfile))

    ObjectIDs2, horizon2, weightfactor2, systems2, systemnames2, zonenames2, Setpoints2, jevisUser2, jevisPW2, webservice2, modelfile2, heaterdata2 = (ConfigLoader.configuration_loader(configurationfile))
    xxxx(ObjectIDs[0],ObjectIDs2[0],"Heaters_measurement")
    xxxx(ObjectIDs[1], ObjectIDs2[1], "Temperatures")
    xxxx(ObjectIDs[2], ObjectIDs2[2], "Disturbances")
    xxxx(ObjectIDs[3], ObjectIDs2[3], "Fullload_measurements")
    xxxx(ObjectIDs[4], ObjectIDs2[4], "energetic_measurements")
    xxxx(ObjectIDs[5], ObjectIDs2[5], "Heaters_variables")
    xxxx(ObjectIDs[6], ObjectIDs2[6], "Fullload_variables")
    xxxx(ObjectIDs[7], ObjectIDs2[7], "weekend_operation")




    xxxx(horizon, horizon2,"horizon")
    xxxx(weightfactor, weightfactor2,"weightfactor")
    xxxx(systems, systems2,"systems")
    xxxx(systemnames, systemnames2,"systemnames")
    xxxx(zonenames, zonenames2,"zonenames")
    xxxx(Setpoints, Setpoints2,"Setpoints")
    xxxx(jevisUser, jevisUser2,"jevisUser")
    xxxx(jevisPW, jevisPW2,"jevisPW")
    xxxx(modelfile, modelfile2,"modelfile")
    xxxx(heaterdata, heaterdata2,"heaterdata")


def xxxx(var1, var2,var3):
    print(var3)
    print("not class")
    print(var1)
    print("class")
    print(var2)


# validation-plot-functions: call-functions for the ploting
    # ploting simulation results over a choosen timeperiod with the recent models
def validation_plot(zonename, configurationfile, fromDv, toDv,calibration='true'):
    # load set-up information of all zones
    #[ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = ConfigLoader.configuration_loader(configurationfile)
    configData = ConfigLoader.configuration_loader(configurationfile)
    if zonename == 'all':
        # Plotting of all zones i
        i = 0
        for j in range(np.size(configData.systems)):
            # Iteration through all halls/systems j
            for n in range(np.size(configData.systems[j])):
                # Iteration through the zones n of hall/system j
                if calibration=='true':
                    # load model-data into a python-list from the modelfile of the given zone
                    Params = r.load_model_with_calibration(configData.modelfile, configData.zonenames[i])
                    # Starting the Plotting-Function given above
                    Validation_with_calibration(configData.objectIds_2[7][i],configData.heaterdata, configData.zonenames[i],configData.objectIds_2[0][i], np.size(configData.objectIds_2[0][i]), configData.objectIds_2[2][i],
                                            configData.objectIds_2[1][i],
                                            configData.objectIds_2[3][j], configData.objectIds_2[4][i], fromDv, toDv, '00',
                                            '00', 0, Params, configData.jevisUser, configData.jevisPW, configData.webservice)
                elif calibration=='false':
                    # load model-data into a python-list from the modelfile of the given zone
                    Params = r.load_model(configData.modelfile, configData.zonenames[i])
                    # Starting the Plotting-Function given above
                    Validation(configData.objectIds_2[7][i],configData.heaterdata, configData.zonenames[i], configData.ObjectIDs[0][i], np.size(configData.ObjectIDs[0][i]), configData.ObjectIDs[2][i],
                               configData.objectIds_2[1][i],
                               configData.objectIds_2[3][j], configData.objectIds[4][i], fromDv, toDv, '00',
                               '00', 0, Params, configData.jevisUser, configData.jevisPW, configData.webservice)
                else:
                    print('ERROR: calibration-variable can only be true or false!')
                i = i + 1
    elif zonename in configData.systemnames:
        # Modelidentifiction for one system (e.g. Hall 1 and 3 (LF))
        # create index array for the zone according their position in the configuration-arrays
        index = configData.systems
        i = 0
        for j in range(np.size(configData.systems)):
            for n in range(np.size(configData.systems[j])):
                index[j][n] = i
                i = i + 1
        j = configData.systemnames.index(zonename)
        for n in range(len(configData.systems[j])):
            # Iteration through the zones n of hall/system j
            if calibration == 'true':
                # load model-data into a python-list from the modelfile of the given zone
                Params = r.load_model_with_calibration(configData.modelfile, configData.zonenames[index[j][n]])
                # Starting the Plotting-Function given above
                Validation_with_calibration(configData.ObjectIDs[7][index[j][n]], configData.heaterdata, configData.zonenames[index[j][n]], configData.objectIds_2[0][index[j][n]], np.size(configData.objectIds_2[0][index[j][n]]),
                                            configData.objectIds_2[2][index[j][n]],
                                            configData.objectIds_2[1][index[j][n]],
                                            configData.objectIds_2[3][j], configData.objectIds_2[4][index[j][n]], fromDv, toDv, '00',
                                            '00', 0, Params, configData.jevisUser, configData.jevisPW, configData.webservice)
            elif calibration == 'false':
                # load model-data into a python-list from the modelfile of the given zone
                Params = r.load_model(configData.modelfile, configData.zonenames[index[j][n]])
                # Starting the Plotting-Function given above
                Validation(configData.objectIds_2[7][index[j][n]], configData.heaterdata, configData.zonenames[index[j][n]], configData.objectIds_2[0][index[j][n]], np.size(configData.objectIds_2[0][index[j][n]]), configData.objectIds_2[2][index[j][n]],
                           configData.objectIds_2[1][index[j][n]],
                           configData.objectIds_2[3][j], configData.objectIds_2[4][index[j][n]], fromDv, toDv, '00',
                           '00', 0, Params, configData.jevisUser, configData.jevisPW, configData.webservice)
            else:
                print('ERROR: calibration-variable can only be true or false!')

    else:
        # Plotting of just one Zone
        # Figure out the Position of the IDs associated to the given Zone
        i = configData.zonenames.index(zonename)
        for list in configData.systems:
            for element in list:
                if element == zonename:
                    j = configData.systems.index(list)
        if calibration=='true':
            # load model-data into a python-list from the modelfile of the given zone
            Params = r.load_model_with_calibration(configData.modelfile, configData.zonenames[i])
            # Starting the Plotting-Function given above
            Validation_with_calibration(configData.objectIds_2[7][i], configData.heaterdata, configData.zonenames[i],configData.objectIds_2[0][i], np.size(configData.objectIds_2[0][i]), configData.objectIds_2[2][i], configData.objectIds_2[1][i],
                                    configData.objectIds_2[3][j], configData.objectIds_2[4][i], fromDv, toDv, '00', '00', 0, Params, configData.jevisUser, configData.jevisPW,
                                    configData.webservice)
        elif calibration=='false':
            # load model-data into a python-list from the modelfile of the given zone
            Params = r.load_model(configData.modelfile, configData.zonenames[i])
            # Starting the Plotting-Function given above
            Validation(configData.objectIds_2[7][i], configData.heaterdata, configData.zonenames[i], configData.objectIds_2[0][i], np.size(configData.objectIds_2[0][i]), configData.objectIds_2[2][i], configData.objectIds_2[1][i],
                       configData.objectIds_2[3][j], configData.objectIds_2[4][i], fromDv,
                       toDv, '00', '00', 0, Params, configData.jevisUser, configData.jevisPW, configData.webservice)
        else:
            print('ERROR: calibration-variable can only be true or false!')

# Control-Functions: Call Functions for the Regulation-Functions:
    # configuration loading
    # Model loading (calibrated or uncalibrated Model)
    # (Disturbance Observing)
    # Regulation - Algorithms
    # Writing on JEVis

def Controlfunction(systemname,configurationfile,TimeID,calibration='true'):
    print("control")
    #[ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = ConfigLoader.configuration_loader(configurationfile)
    configData = ConfigLoader.configuration_loader(configurationfile)
    #printconfig(configurationfile)
    # weightfactor: Ratio of the Cost of comfort (setpoint fulfillment) versus Cost of energy consumption (Sum of the heater/input/control signals)
    if systemname == 'all':
        # Control of all zones i
        index = configData.systems
        # Creating array of indices for the different zones according to their representation in the ID-Arrays
        i=0
        for j in range(np.size(configData.systems)):
            for n in range(np.size(configData.systems[j])):
                index[j][n] = i
                i=i+1
        # Iteration through all zones
        for j in range(np.size(configData.systems)):
            print(configData.systemnames[j])
            # initialize empty arrays for the calculated control-signals
            fullload = [''] * np.size(configData.systems[j])
            heaters = [''] * np.size(configData.systems[j])
            for n in range(np.size(configData.systems[j])):
                print('Zone '+str(configData.systems[j][n]+1))
                if calibration=='true':
                    # Starting Regulation-Function given above
                    #filename, TimeID, WeekendID, heaterdata, zonename,weightening_ratio,IDs_disturbances, ID_temperature,ID_heaters,ID_fullload,ID_energy,Setpoints,Heaters_number,fullload_hall,horizon,username,password,webservice
                    [fullload[n], heaters[n]] = Regulation_calibration(configData.modelfile, TimeID, configData.objectIds_2[7][index[j][n]], configData.heaterdata, configData.zonenames[index[j][n]],configData.weightfactor[index[j][n]], configData.objectIds_2[2][index[j][n]], configData.objectIds_2[1][index[j][n]], configData.objectIds_2[0][index[j][n]], configData.objectIds_2[3][j], configData.objectIds_2[4][index[j][n]], configData.objectIds.setpoints[index[j][n]], len(configData.objectIds_2[5][index[j][n]]),[0,0,0],configData.horizon[index[j][n]],configData.jevisUser, configData.jevisPW,configData.webservice)
                elif calibration=='false':
                    # Starting Regulation-Function given above
                    [fullload[n], heaters[n]] = Regulation(configData.modelfile, TimeID, configData.objectIds_2[7][index[j][n]],configData.heaterdata, configData.zonenames[index[j][n]],
                                                                       configData.weightfactor[index[j][n]], configData.objectIds_2[2][index[j][n]],
                                                                       configData.objectIds_2[1][index[j][n]],
                                                                       configData.objectIds_2[0][index[j][n]], configData.objectIds_2[3][j], configData.objectIds_2[4][index[j][n]],
                                                                       configData.objectIds.setpoints[index[j][n]],
                                                                       len(configData.objectIds_2[5][index[j][n]]), [0, 0, 0],configData.horizon[index[j][n]],
                                                                       configData.jevisUser, configData.jevisPW, configData.webservice)
                else:
                    print('ERROR: calibration-variable can only be true or false!')

            # fullload set parameter over the next 3 timesteps: if in a Hall is fullload set by one Zone, all other Zones of that hall need to be in fullload too!
            fullload_hall = np.zeros(int(len(fullload[0]) / len(configData.objectIds_2[5][index[j][0]])))
            # Iteration through all systems and check if a Zone in the system needs Fullload
            # if so, all Control-Signals of the Zones of that system need to be recalculated, only allowing fullload or off signals (2 / 0)
            # Iteration through the systems
            for n in range(len(configData.systems[j])):
                # Iteration through the 3 timesteps, that will be written to JEVis
                for z in range(len(fullload_hall)):
                    # Iteration through the zones of a system
                    for i in range(z * len(configData.objectIds_2[5][index[j][n]]), (z+1) * len(configData.objectIds_2[5][index[j][n]])):
                        # check if Zone of the system needs fullload
                        if fullload[n][i] == 1:
                            fullload_hall[z] = 1
                if calibration=='true':
                    # Starting Regulation-Function given above, with the given fullload-demand
                    [fullload[n], heaters[n]] = Regulation_calibration(configData.modelfile, TimeID, configData.objectIds_2[7][index[j][n]], configData.heaterdata, configData.zonenames[index[j][n]],configData.weightfactor[index[j][n]], configData.objectIds_2[2][index[j][n]],
                                                         configData.objectIds_2[1][index[j][n]], configData.objectIds_2[0][index[j][n]], configData.objectIds_2[3][j], configData.objectIds_2[4][index[j][n]],
                                                         configData.objectIds.setpoints[index[j][n]], len(configData.objectIds_2[0][index[j][n]]), fullload_hall,configData.horizon[index[j][n]], configData.jevisUser, configData.jevisPW,configData.webservice)
                elif calibration=='false':
                    # Starting Regulation-Function given above, with the given fullload-demand
                    [fullload[n], heaters[n]] = Regulation(configData.modelfile, TimeID, configData.objectIds_2[7][index[j][n]], configData.heaterdata, configData.zonenames[index[j][n]],configData.weightfactor[index[j][n]], configData.objectIds_2[2][index[j][n]],
                                                         configData.objectIds_2[1][index[j][n]], configData.objectIds_2[0][index[j][n]], configData.objectIds_2[3][j], configData.objectIds_2[4][index[j][n]],
                                                         configData.objectIds.setpoints[index[j][n]], len(configData.objectIds_2[0][index[j][n]]), fullload_hall,configData.horizon[index[j][n]], configData.jevisUser, configData.jevisPW,configData.webservice)
                else:
                    print('ERROR: calibration-variable can only be true or false!')
                # write controlvalues into JEVis
                JEVis.controlWrite(configData.objectIds_2[5][index[j][n]], configData.objectIds_2[6][j], fullload[n], heaters[n], configData.jevisUser, configData.jevisPW,configData.webservice)
    elif systemname in configData.systemnames:
        # Systemwise control of a area, where one fullload switch controls multiple zones at once!
        #[ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = ConfigLoader.configuration_loader(configurationfile)
        configData = ConfigLoader.configuration_loader(configurationfile)
        print(configuration_loader(configurationfile))
        print(ConfigLoader.configuration_loader(configurationfile))
        # Control of all zones i of one system (hall)
        # create index array for the zone according their position in the configuration-arrays
        index = configData.systems
        i = 0
        for j in range(np.size(configData.systems)):
            for n in range(np.size(configData.systems[j])):
                index[j][n] = i
                i = i + 1
        j = configData.systemnames.index(systemname)
        # initialize empty arrays for the calculated control-signals
        fullload = [''] * np.size(configData.systems[j])
        heaters = [''] * np.size(configData.systems[j])
        # Iteration through all Zones of one system
        for n in range(np.size(configData.systems[j])):
            print(configData.zonenames[index[j][n]])
            if calibration=='true':
                # Starting Regulation-Function given above
                [fullload[n], heaters[n]] = Regulation_calibration(configData.modelfile, TimeID, configData.objectIds_2[7][index[j][n]], configData.heaterdata, configData.zonenames[index[j][n]],configData.weightfactor[index[j][n]], configData.ObjectIDs[2][index[j][n]],
                                                         configData.objectIds_2[1][index[j][n]], configData.objectIds_2[0][index[j][n]], configData.objectIds_2[3][j], configData.objectIds_2[4][index[j][n]],
                                                         configData.objectIds.setpoints[index[j][n]], len(configData.objectIds_2[0][index[j][n]]), [0, 0, 0],configData.horizon[index[j][n]], configData.jevisUser, configData.jevisPW,configData.webservice)
            elif calibration=='false':
                # Starting Regulation-Function given above
                [fullload[n], heaters[n]] = Regulation(configData.modelfile, TimeID, configData.objectIds_2[7][index[j][n]], configData.heaterdata, configData.zonenames[index[j][n]],configData.weightfactor[index[j][n]], configData.objectIds_2[2][index[j][n]],
                                                         configData.objectIds_2[1][index[j][n]], configData.objectIds_2[0][index[j][n]], configData.objectIds_2[3][j], configData.objectIds_2[4][index[j][n]],
                                                         configData.objectIds.setpoints[index[j][n]], len(configData.objectIds_2[0][index[j][n]]), [0, 0, 0],configData.horizon[index[j][n]], configData.jevisUser, configData.jevisPW,configData.webservice)
            else:
                print('ERROR: calibration-variable can only be true or false!')
        # fullload set parameter over the next 3 timesteps: if in a Hall is fullload set by one Zone, all other Zones of that hall need to be in fullload too!
        # Iteration through the system and check if a Zone in the system needs Fullload
        # if so, all Control-Signals of the Zones of that system need to be recalculated, only allowing fullload or off signals (2 / 0)
        fullload_hall = np.zeros(int(len(fullload[0]) / len(configData.objectIds_2[5][index[j][0]])))
        for n in range(np.size(configData.systems[j])):
            # Iteration through the 3 timesteps, that will be written to JEVis
            for z in range(np.size(fullload_hall)):
                # Iteration through the zones of a system
                for i in range(z * len(configData.objectIds_2[5][index[j][n]]), (z+1) * len(configData.objectIds_2[5][index[j][n]])):
                    # check if Zone of the system needs fullload
                    if fullload[n][i] == 1:
                        fullload_hall[z] = 1
            print(configData.zonenames[index[j][n]])
            if calibration=='true':
                # Starting Regulation-Function given above, with the given fullload-demand
                [fullload[n], heaters[n]] = Regulation_calibration(configData.modelfile, TimeID, configData.objectIds_2[7][index[j][n]], configData.heaterdata, configData.zonenames[index[j][n]],configData.weightfactor[index[j][n]], configData.objectIds_2[2][index[j][n]],
                                                         configData.objectIds_2[1][index[j][n]], configData.objectIds_2[0][index[j][n]], configData.objectIds_2[3][j], configData.objectIds_2[4][index[j][n]],
                                                         configData.objectIds.setpoints[index[j][n]], len(configData.objectIds_2[0][index[j][n]]), fullload_hall,configData.horizon[index[j][n]], configData.jevisUser, configData.jevisPW,configData.webservice)
            elif calibration=='false':
                # Starting Regulation-Function given above, with the given fullload-demand
                [fullload[n], heaters[n]] = Regulation(configData.modelfile, TimeID, configData.objectIds_2[7][index[j][n]], configData.heaterdata, configData.zonenames[index[j][n]],configData.weightfactor[index[j][n]], configData.ObjectIDs[2][index[j][n]],
                                                         configData.objectIds_2[1][index[j][n]], configData.objectIds_2[0][index[j][n]], configData.objectIds_2[3][j], configData.objectIds_2[4][index[j][n]],
                                                         configData.objectIds.setpoints[index[j][n]], len(configData.objectIds_2[0][index[j][n]]), fullload_hall,configData.horizon[index[j][n]], configData.jevisUser, configData.jevisPW,configData.webservice)
            else:
                print('ERROR: calibration-variable can only be true or false!')
                # write controlvalues into JEVis
            r.Control_write(configData.objectIds_2[5][index[j][n]], configData.objectIds_2[6][j], fullload[n], heaters[n], configData.jevisUser, configData.jevisPW,configData.webservice)
    elif systemname in configData.zonenames:
        zonename = systemname
        # zonewise control (In Siosta zonewise control is not correct, if multiple zones are controlled by the same switch/operator, because of the fullload signal!)
        # weightening_ratio: Ratio of the Cost of comfort (setpoint fulfillment) versus Cost of energy consumption
        #[ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = ConfigLoader.configuration_loader(configurationfile)
        configData = ConfigLoader.configuration_loader(configurationfile)
        #print(configuration_loader(configurationfile))
       # print(ConfigLoader.configuration_loader(configurationfile))
        # Control of one zone i, checking index for the zone in configuration-arrays
        index = configData.systems
        i = configData.zonenames.index(zonename)
        for list in configData.systems:
            for element in list:
                if element == zonename:
                    j = configData.systems.index(list)
        # initialize empty arrays for the calculated control-signals
        fullload = ['']
        heaters = ['']
        if calibration=='true':
            # Starting Regulation-Function given above
            [fullload, heaters] = Regulation_calibration(configData.modelfile, TimeID, configData.objectIds_2[7][i], configData.heaterdata, configData.zonenames[i],configData.weightfactor[i], configData.objectIds_2[2][i],
                                                         configData.objectIds_2[1][i], configData.objectIds_2[0][i], configData.objectIds_2[3][j], configData.objectIds_2[4][i],
                                                         configData.objectIds.setpoints[i], len(configData.objectIds_2[0][i]), [0, 0, 0], configData.horizon[i], configData.jevisUser, configData.jevisPW,configData.webservice)
        elif calibration=='false':
            # Starting Regulation-Function given above
            [fullload, heaters] = Regulation(configData.modelfile, TimeID, configData.objectIds_2[7][i], configData.heaterdata, configData.zonenames[i],configData.weightfactor[i], configData.objectIds_2[2][i],
                                                         configData.objectIds_2[1][i], configData.objectIds_2[0][i], configData.objectIds_2[3][j], configData.objectIds_2[4][i],
                                                         configData.objectIds.setpoints[i], len(configData.objectIds_2[0][i]), [0, 0, 0],configData.horizon[i], configData.jevisUser, configData.jevisPW,configData.webservice)
        else:
            print('ERROR: calibration-variable can only be true or false!')
        # write controlvalues into JEVis
        r.Control_write(configData.objectIds_2[5][i], configData.objectIds_2[6][j], fullload, heaters, configData.jevisUser, configData.jevisPW,configData.webservice)