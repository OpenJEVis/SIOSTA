
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
class Control:
    def __init__(self,configData):
        #print("Class Generated")
        self.configData = configData
        #confloader = ConfigLoader("config.txt")
        #self.configData = confloader.load()
        self.jevis = JEVis(self.configData.jevisUser,self.configData.jevisPW,self.configData.webservice)

    def identification(self,fromD,toD,fromT,toT,set_equalHeaterParameter,index,indexFullload):
        # Read and prepare measured Data of the given Timeperiod
        [Temperature,OUTTemperature,Disturbances,Heater,Energies,weekend_operation]=p.totalprep(self.configData.timeID,self.configData.heaterdata, self.configData.objectIds.heatersRead[index],len(self.configData.objectIds.heatersRead[index]),self.configData.objectIds.disturbancesRead[index], self.configData.objectIds.temperaturesRead[index],self.configData.objectIds.fullloadRead[indexFullload],self.configData.objectIds.energyRead[index],fromD,toD,fromT,toT,self.jevis)
        # Parameteridentification into a decomposed Tensor, the outcome is a Python-List including all the Model-Data (Parametervector --> Value Information, Factormatrices --> Structure Information)
        Params=p.decparamIDD(Heater, Temperature, Disturbances, Energies, OUTTemperature, set_equalHeaterParameter = set_equalHeaterParameter)
        # Safe Model Data (Parametervector --> Value Information, Factormatrices --> Structure Information) as a JSON-String into the Model-File
        p.safe_model(self.configData.modelfile, self.configData.zonenames[index], Params, fromD, toD)
        return Params

    def identification_with_calibration(self,fromD,toD,fromT,toT,set_equalHeaterParameter,index,indexFullload):
        # Read and prepare measured Data of the given Timeperiod
        [Temperature,OUTTemperature,Disturbances,Heater,Energies,weekend_operation]=p.totalprep(self.configData.timeID,self.configData.heaterdata, self.configData.objectIds.heatersRead[index],len(self.configData.objectIds.heatersRead[index]),self.configData.objectIds.disturbancesRead[index], self.configData.objectIds.temperaturesRead[index],self.configData.objectIds.fullloadRead[indexFullload],self.configData.objectIds.energyRead[index],fromD,toD,fromT,toT,self.jevis)
        # Parameteridentification into a decomposed Tensor, the outcome is a Python-List including all the Model-Data (Parametervector --> Value Information, Factormatrices --> Structure Infromation, Calibrationvectors --> Calibration Information)
        Params = p.decomposed_Parameteridentification_with_calibration(Heater, Temperature, Disturbances, Energies, OUTTemperature, set_equalHeaterParameter = set_equalHeaterParameter)
        # Safe Model Data (Parametervector --> Value Information, Factormatrices --> Structure Infromation, Calibrationvectors --> Calibration Information) as a JSON-String into the Model-File
        p.safe_model_with_calibration(self.configData.modelfile, self.configData.zonenames[index], Params, fromD, toD)
        return Params

    #model validation/Plotting

    def Validation(self,fromDv,toDv,fromTv,toTv,scale,Params,index,indexFullload):
        # Read and prepare measured Data of the given Timeperiod
        [Temperature,OUTTemperature,Disturbances,Heater,Energies,weekend_operation]=p.totalprep(self.configData.timeID[index],self.configData.heaterdata, self.configData.objectIds.heatersRead[index],len(self.configData.objectIds.heatersRead[index]),self.configData.objectIds.disturbancesRead[index], self.configData.objectIds.temperaturesRead[index],self.configData.objectIds.fullloadRead[indexFullload],self.configData.objectIds.energyRead[index],fromDv,toDv,fromTv,toTv,self.jevis)
        # Calculating Zonetemperature-Trend with the given Signals and the Model-Data, starting with the initial-measured Temperature
        Estimated_temp=p.decvalidS(self.configData.zonenames[index], Heater, Temperature[0], Disturbances, Energies, Params)
        # Dump Data
        p.DataDump_Validation(self.configData.zonenames[index], OUTTemperature, Estimated_temp, Heater, Disturbances, Energies, fromDv, toDv, fromTv,toTv)
        # Plotting measured Data and the calculated Temperature-Trend
        p.Modelvalidation_plot(self.configData.zonenames[index], fromDv,toDv,fromTv,toTv)
        return Estimated_temp

    def Validation_with_calibration(self,fromDv,toDv,fromTv,toTv,scale,Params,index,indexFullload):
        # Read and prepare measured Data of the given Timeperiod
        [Temperature,OUTTemperature,Disturbances,Heater,Energies,weekend_operation]=p.totalprep(self.configData.timeID[index],self.configData.heaterdata, self.configData.objectIds.heatersRead[index],len(self.configData.objectIds.heatersRead[index]),self.configData.objectIds.disturbancesRead[index], self.configData.objectIds.temperaturesRead[index],self.configData.objectIds.fullloadRead[indexFullload],self.configData.objectIds.energyRead[index],fromDv,toDv,fromTv,toTv,self.jevis)
        # Calculating Zonetemperature-Trend with the given Signals and the Model-Data, starting with the initial-measured Temperature
        Estimated_temp=p.decvalidS_with_calibration(self.configData.zonenames[index], Heater, Temperature[0], Disturbances, Energies, Params)
        # Dump Data
        p.DataDump_Validation(self.configData.zonenames[index], OUTTemperature, Estimated_temp, Heater, Disturbances, Energies, fromDv, toDv,
                          fromTv, toTv)
        # Plotting measured Data and the calculated Temperature-Trend
        p.Modelvalidation_plot(self.configData.zonenames[index], fromDv, toDv, fromTv, toTv)
        return Estimated_temp

 #Regulation-Functions:
        #importing latest disturbances and temperature data from JEVis
        # (Disturbance Observing)
        #using the data to calculate heater signal values (predictive control)
        #preparing data to write in JEVis
        #write data in JEVis (seperate object IDs for write)


    def Regulation(self,fullload_hall,index,setpoints):
        # loading model data of a given zone into a python-list from the modelfile
        ModellParam = r.load_model(self.configData.modelfile, self.configData.zonenames[index])
        # read the current measured Data needed for the Control-Algortihm (Disturbances, Temperature, Heater)
        jevisValues = self.jevis.read(self.configData.objectIds.weekendOperationRead[index],self.configData.objectIds.heatersRead[index],self.configData.objectIds.disturbancesRead[index], self.configData.objectIds.energyRead[index], self.configData.objectIds.temperaturesRead[index])
        # Read the current time and convert to a date- and a time-string
        [now_day, now_time] = r.Time_reader(self.configData.timeID,self.jevis)
        # create a Array of Setpoints for the given Control-Horizon
        Setpoint = r.Set_Setpoint(setpoints[0], setpoints[1], jevisValues.weekendOperation, now_day, now_time, self.configData.horizon[index])
        print("Setpoint")
        print(Setpoint)
        # Control-Algorithm, calculating the optimal Controlvalues with the given Weightening for the next 3 Timesteps
        Controlvalues = r.Control(self.configData.heaterdata, jevisValues.temperatureValues, len(self.configData.objectIds.heatersRead[index]), jevisValues.disturbancesValues, jevisValues.energyValues, Setpoint, ModellParam, fullload_hall,
                                  self.configData.weightfactor[index], self.configData.horizon[index])
        # Split the Controlvalues into Heater (on/off) and fullload (on/off) signals
        [fullload, heaters] = r.Fullload_sep(self.configData.heaterdata, Controlvalues, jevisValues.heaterValues, len(self.configData.objectIds.heatersRead[index]), fullload_hall)
        return fullload, heaters

    def Regulation_calibration(self,fullload_hall,index,setpoints):
        print(setpoints[index])
        # loading model data of a given zone into a python-list from the modelfile
        ModellParam = r.load_model_with_calibration(self.configData.modelfile, self.configData.zonenames[index])
        # read the current measured Data needed for the Control-Algortihm (Disturbances, Temperature, Heater)
        jevisValues = self.jevis.read(self.configData.objectIds.weekendOperationRead[index],self.configData.objectIds.heatersRead[index],self.configData.objectIds.disturbancesRead[index], self.configData.objectIds.energyRead[index], self.configData.objectIds.temperaturesRead[index])
        # Read the current time and convert to a date- and a time-string
        [now_day, now_time] = r.Time_reader(self.configData.timeID,self.jevis)
        # create a Array of Setpoints for the given Control-Horizon

        #Setpoint = r.Set_Setpoint(self.configData.objectIds.setpointsValues[index][0], self.configData.objectIds.setpointsValues[index][0], jevisValues.weekendOperation, now_day, now_time, self.configData.horizon[index])
        Setpoint = r.Set_Setpoint(setpoints[index][0], setpoints[index][1], jevisValues.weekendOperation, now_day, now_time, self.configData.horizon[index])
        # Control-Algorithm, calculating the optimal Controlvalues with the given Weightening for the next 3 Timesteps

        Controlvalues = r.Control_with_calibration(self.configData.heaterdata, jevisValues.temperatureValues, len(self.configData.objectIds.heatersRead[index]), jevisValues.disturbancesValues, jevisValues.energyValues, Setpoint, ModellParam, fullload_hall,
                                               self.configData.weightfactor[index], self.configData.horizon[index])
        # Split the Controlvalues (0 / 1 / 2) into Heater ( on(1) / off(0) ) and fullload ( on(1) / off(0) ) signals
        [fullload, heaters] = r.Fullload_sep(self.configData.heaterdata, Controlvalues, jevisValues.heaterValues, len(self.configData.objectIds.heatersRead[index]), fullload_hall)
        return fullload, heaters

    ########## CALL - FUNCTIONS ##########
    # Modelidentifcation: Call Functions for the model and parameter identifier
    # Loading data from JEVis and prepare Data (e.g. generating 5 min intervals)
    # Creating Modelstructure and calculating parameters
    # Write Models into Models.txt / JEVis

    def modelidentification(self,zonename, fromD, toD, calibration='true', set_equalHeaterParameter='false'):
        # zonename can be: Zone 1, System 1 or all
        # load set-up information of all zones
        #[ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = ConfigLoader.configuration_loader(configurationfile)
        #configData = ConfigLoader.configuration_loader(configurationfile)
        #printconfig(configurationfile)
        # ObjectIDs = [Heaters_measurement, Temperatures, Disturbances, Fullload_measurements, Heaters_variables, Fullload_variables]

        # Modelidentification for all Zones
        if zonename == 'all':
            # ObjectIDs include [Heaters_measurement, Temperatures, Disturbances, Fullload_measurements, Heaters_variables, Fullload_variables]
            i = 0
            for j in range(len(self.configData.systems)):
                # Iteration through all halls/systems j
                for n in range(len(self.configData.systems[j])):
                    # Iteration through the zones n of hall/system j
                    if calibration=='true':
                        # Starting the identification-Function given above
                        self.identification_with_calibration(fromD, toD, '00', '00', set_equalHeaterParameter,i,j)
                    elif calibration=='false':
                        # Starting the identification-Function given above
                        self.identification(fromD, toD, '00', '00', set_equalHeaterParameter,i,j)
                    else:
                        print('ERROR: calibration-variable can only be true or false!')
                    i = i + 1
        elif zonename in self.configData.systemnames:
            # Modelidentifiction for one system (e.g. Hall 1 and 3 (LF))
            # create index array for the zone according their position in the configuration-arrays
            index = self.configData.systems
            i = 0
            for j in range(np.size(self.configData.systems)):
                for n in range(np.size(self.configData.systems[j])):
                    index[j][n] = i
                    i = i + 1
            j = self.configData.systemnames.index(zonename)
            for n in range(len(self.configData.systems[j])):
                # Iteration through the zones n of hall/system j
                if calibration == 'true':
                    # Starting the identification-Function given above
                    self.identification_with_calibration(fromD, toD, '00', '00', set_equalHeaterParameter, index[j][n], j)
                elif calibration == 'false':
                    # Starting the identification-Function given above
                    self.identification(fromD, toD, '00', '00', set_equalHeaterParameter, index[j][n], j)
                else:
                    print('ERROR: calibration-variable can only be true or false!')
                i = i + 1

        else:
            # Modelidentification of only one zone
            # Figure out the Position of the IDs associated to the given Zone
            i = self.configData.zonenames.index(zonename)
            print("zone name")
            print(i)
            for list in self.configData.systems:
                for element in list:
                    if element == zonename:
                        j = self.configData.systems.index(list)
            # Identification of the given Zone
            if calibration=='true':
                # Starting the identification-Function given above
                self.identification_with_calibration(fromD, toD, '00', '00', set_equalHeaterParameter, i, j)
            elif calibration=='false':
                # Starting the identification-Function given above
                self.identification(fromD, toD, '00', '00', set_equalHeaterParameter, i, j)
            else:
                print('ERROR: calibration-variable can only be true or false!')



# validation-plot-functions: call-functions for the ploting
    # ploting simulation results over a choosen timeperiod with the recent models

    def validation_plot(self,zonename, fromDv, toDv,calibration='true'):
        # load set-up information of all zones
        #[ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = ConfigLoader.configuration_loader(configurationfile)
        #configData = ConfigLoader.configuration_loader(configurationfile)
        if zonename == 'all':
            # Plotting of all zones i
            i = 0
            for j in range(np.size(self.configData.systems)):
                # Iteration through all halls/systems j
                for n in range(np.size(self.configData.systems[j])):
                    # Iteration through the zones n of hall/system j
                    if calibration=='true':
                        # load model-data into a python-list from the modelfile of the given zone
                        Params = r.load_model_with_calibration(self.configData.modelfile, self.configData.zonenames[i])
                        # Starting the Plotting-Function given above
                        self.Validation_with_calibration(fromDv, toDv, '00','00', 0, Params, i, j)
                    elif calibration=='false':
                        # load model-data into a python-list from the modelfile of the given zone
                        Params = r.load_model(self.configData.modelfile, self.configData.zonenames[i])
                        # Starting the Plotting-Function given above
                        self.Validation(fromDv, toDv, '00','00', 0, Params, i, j)
                    else:
                        print('ERROR: calibration-variable can only be true or false!')
                    i = i + 1
        elif zonename in self.configData.systemnames:
            # Modelidentifiction for one system (e.g. Hall 1 and 3 (LF))
            # create index array for the zone according their position in the configuration-arrays
            index = self.configData.systems
            i = 0
            for j in range(np.size(self.configData.systems)):
                for n in range(np.size(self.configData.systems[j])):
                    index[j][n] = i
                    i = i + 1
            j = self.configData.systemnames.index(zonename)
            for n in range(len(self.configData.systems[j])):
                # Iteration through the zones n of hall/system j
                if calibration == 'true':
                    # load model-data into a python-list from the modelfile of the given zone
                    Params = r.load_model_with_calibration(self.configData.modelfile, self.configData.zonenames[index[j][n]])
                    # Starting the Plotting-Function given above
                    self.Validation_with_calibration(fromDv, toDv, '00', '00', 0, Params, index[j][n], j)
                elif calibration == 'false':
                    # load model-data into a python-list from the modelfile of the given zone
                    Params = r.load_model(self.configData.modelfile, self.configData.zonenames[index[j][n]])
                    # Starting the Plotting-Function given above
                    self.Validation(fromDv, toDv, '00', '00', 0, Params, index[j][n], j)
                else:
                    print('ERROR: calibration-variable can only be true or false!')

        else:
            # Plotting of just one Zone
            # Figure out the Position of the IDs associated to the given Zone
            i = self.configData.zonenames.index(zonename)
            for list in self.configData.systems:
                for element in list:
                    if element == zonename:
                        j = self.configData.systems.index(list)
            if calibration=='true':
                # load model-data into a python-list from the modelfile of the given zone
                Params = r.load_model_with_calibration(self.configData.modelfile, self.configData.zonenames[i])
                # Starting the Plotting-Function given above
                self.Validation_with_calibration(fromDv, toDv, '00', '00', 0, Params, i, j)
            elif calibration=='false':
                # load model-data into a python-list from the modelfile of the given zone
                Params = r.load_model(self.configData.modelfile, self.configData.zonenames[i])
                # Starting the Plotting-Function given above
                self.Validation(fromDv, toDv, '00', '00', 0, Params, i, j)
            else:
                print('ERROR: calibration-variable can only be true or false!')

# Control-Functions: Call Functions for the Regulation-Functions:
    # configuration loading
    # Model loading (calibrated or uncalibrated Model)
    # (Disturbance Observing)
    # Regulation - Algorithms
    # Writing on JEVis


    def Controlfunction(self,systemname,configurationfile,calibration='true'):

        
        #[ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = ConfigLoader.configuration_loader(configurationfile)
        #configData = ConfigLoader.configuration_loader(configurationfile)
        setpoints=self.jevis.readSetpoints(self.configData.objectIds.setpointsRead)
        #printconfig(configurationfile)
        # weightfactor: Ratio of the Cost of comfort (setpoint fulfillment) versus Cost of energy consumption (Sum of the heater/input/control signals)
        if systemname == 'all':
            # Control of all zones i
            index = self.configData.systems
            # Creating array of indices for the different zones according to their representation in the ID-Arrays
            i=0
            for j in range(np.size(self.configData.systems)):
                for n in range(np.size(self.configData.systems[j])):
                    index[j][n] = i
                    print("index")
                    print(index)
                    i=i+1
            # Iteration through all zones
            for j in range(np.size(self.configData.systems)):
                print(self.configData.systemnames[j])
                # initialize empty arrays for the calculated control-signals
                fullload = [''] * np.size(self.configData.systems[j])
                heaters = [''] * np.size(self.configData.systems[j])
                for n in range(np.size(self.configData.systems[j])):
                    print("index[j][n]")
                    print(index[j][n])
                    print(self.configData.objectIds.heatersRead)
                    print('Zone ' + str(self.configData.systems[j][n] + 1))
                    if calibration=='true':
                        # Starting Regulation-Function given above
                        #filename, self.configData.timeID, WeekendID, heaterdata, zonename,weightening_ratio,IDs_disturbances, ID_temperature,ID_heaters,ID_fullload,ID_energy,Setpoints,Heaters_number,fullload_hall,horizon,username,password,webservice
                        [fullload[n], heaters[n]] = self.Regulation_calibration([0, 0, 0], index[j][n], setpoints)
                    elif calibration=='false':
                        # Starting Regulation-Function given above
                        [fullload[n], heaters[n]] = self.Regulation([0, 0, 0], index[j][n], setpoints)
                    else:
                        print('ERROR: calibration-variable can only be true or false!')

                # fullload set parameter over the next 3 timesteps: if in a Hall is fullload set by one Zone, all other Zones of that hall need to be in fullload too!
                fullload_hall = np.zeros(int(len(fullload[0]) / len(self.configData.objectIds.heatersWrite[index[j][0]])))
                # Iteration through all systems and check if a Zone in the system needs Fullload
                # if so, all Control-Signals of the Zones of that system need to be recalculated, only allowing fullload or off signals (2 / 0)
                # Iteration through the systems
                for n in range(len(self.configData.systems[j])):
                    # Iteration through the 3 timesteps, that will be written to JEVis
                    for z in range(len(fullload_hall)):
                        # Iteration through the zones of a system
                        for i in range(z * len(self.configData.objectIds.heatersWrite[index[j][n]]), (z + 1) * len(self.configData.objectIds.heatersWrite[index[j][n]])):
                            # check if Zone of the system needs fullload
                            if fullload[n][i] == 1:
                                fullload_hall[z] = 1
                    if calibration=='true':
                        # Starting Regulation-Function given above, with the given fullload-demand
                        [fullload[n], heaters[n]] = self.Regulation_calibration([0, 0, 0], index[j][n],setpoints)
                    elif calibration=='false':
                        # Starting Regulation-Function given above, with the given fullload-demand
                        [fullload[n], heaters[n]] = self.Regulation([0, 0, 0], index[j][n], setpoints)
                    else:
                        print('ERROR: calibration-variable can only be true or false!')
                    # write controlvalues into JEVis
                    self.jevis.controlWrite(self.configData.objectIds.heatersWrite[index[j][n]], self.configData.objectIds.fullloadWrite[j], fullload[n], heaters[n])
        elif systemname in self.configData.systemnames:
            # Systemwise control of a area, where one fullload switch controls multiple zones at once!
            #[ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = ConfigLoader.configuration_loader(configurationfile)
            self.configData = ConfigLoader.load(configurationfile)
            #print(configuration_loader(configurationfile))
            #print(ConfigLoader.configuration_loader(configurationfile))
            # Control of all zones i of one system (hall)
            # create index array for the zone according their position in the configuration-arrays
            index = self.configData.systems
            i = 0
            for j in range(np.size(self.configData.systems)):
                for n in range(np.size(self.configData.systems[j])):
                    index[j][n] = i
                    i = i + 1
            j = self.configData.systemnames.index(systemname)
            # initialize empty arrays for the calculated control-signals
            fullload = [''] * np.size(self.configData.systems[j])
            heaters = [''] * np.size(self.configData.systems[j])
            # Iteration through all Zones of one system
            for n in range(np.size(self.configData.systems[j])):
                print(self.configData.zonenames[index[j][n]])
                if calibration=='true':
                    # Starting Regulation-Function given above
                    [fullload[n], heaters[n]] = self.Regulation_calibration([0, 0, 0], index[j][n])
                elif calibration=='false':
                    # Starting Regulation-Function given above
                    [fullload[n], heaters[n]] = self.Regulation([0, 0, 0], index[j][n], setpoints)
                else:
                    print('ERROR: calibration-variable can only be true or false!')
            # fullload set parameter over the next 3 timesteps: if in a Hall is fullload set by one Zone, all other Zones of that hall need to be in fullload too!
            # Iteration through the system and check if a Zone in the system needs Fullload
            # if so, all Control-Signals of the Zones of that system need to be recalculated, only allowing fullload or off signals (2 / 0)
            fullload_hall = np.zeros(int(len(fullload[0]) / len(self.configData.objectIds.heatersWrite[index[j][0]])))
            for n in range(np.size(self.configData.systems[j])):
                # Iteration through the 3 timesteps, that will be written to JEVis
                for z in range(np.size(fullload_hall)):
                    # Iteration through the zones of a system
                    for i in range(z * len(self.configData.objectIds.heatersWrite[index[j][n]]), (z + 1) * len(self.configData.objectIds.heatersWrite[index[j][n]])):
                        # check if Zone of the system needs fullload
                        if fullload[n][i] == 1:
                            fullload_hall[z] = 1
                print(self.configData.zonenames[index[j][n]])
                if calibration=='true':
                    # Starting Regulation-Function given above, with the given fullload-demand
                    [fullload[n], heaters[n]] = self.Regulation_calibration([0, 0, 0], index[j][n])
                elif calibration=='false':
                    # Starting Regulation-Function given above, with the given fullload-demand
                    [fullload[n], heaters[n]] = self.Regulation([0, 0, 0], index[j][n], setpoints)
                else:
                    print('ERROR: calibration-variable can only be true or false!')
                    # write controlvalues into JEVis
                    self.jevis.controlWrite(self.configData.objectIds.heatersWrite[index[j][n]], self.configData.objectIds.fullloadWrite[j], fullload[n], heaters[n], self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice)
        elif systemname in self.configData.zonenames:
            zonename = systemname
            # zonewise control (In Siosta zonewise control is not correct, if multiple zones are controlled by the same switch/operator, because of the fullload signal!)
            # weightening_ratio: Ratio of the Cost of comfort (setpoint fulfillment) versus Cost of energy consumption
            #[ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = ConfigLoader.configuration_loader(configurationfile)
            self.configData = ConfigLoader.load(configurationfile)
            #print(configuration_loader(configurationfile))
            # print(ConfigLoader.configuration_loader(configurationfile))
            # Control of one zone i, checking index for the zone in configuration-arrays
            index = self.configData.systems
            i = self.configData.zonenames.index(zonename)
            for list in self.configData.systems:
                for element in list:
                    if element == zonename:
                        j = self.configData.systems.index(list)
            # initialize empty arrays for the calculated control-signals
            fullload = ['']
            heaters = ['']
            if calibration=='true':
                # Starting Regulation-Function given above
                [fullload, heaters] = self.Regulation_calibration([0, 0, 0], i, setpoints)
            elif calibration=='false':
                # Starting Regulation-Function given above
                [fullload, heaters] = self.Regulation([0, 0, 0], i, setpoints)
            else:
                print('ERROR: calibration-variable can only be true or false!')
                # write controlvalues into JEVis
                self.jevis.controlWrite(self.configData.objectIds.heatersWrite[i], self.configData.objectIds.fullloadWrite[j], fullload, heaters, self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice)