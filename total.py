
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
        self.jevis = JEVis(self.configData.jevisUser,self.configData.jevisPW,self.configData.webservice)

    def identification(self,filename,WeekendID, heaterdata, zonename, ID_heater,heaters_number,ID_disturbances,ID_temperature,ID_fullload,ID_energy,fromD,toD,fromT,toT,jevisUser,jevisPW,webservice,set_equalHeaterParameter):
        # Read and prepare measured Data of the given Timeperiod
        [Temperature,OUTTemperature,Disturbances,Heater,Energies,weekend_operation]=p.totalprep(WeekendID,heaterdata, ID_heater,heaters_number,ID_disturbances,ID_temperature,ID_fullload,ID_energy,fromD,toD,fromT,toT,jevisUser,jevisPW,webservice)
        # Parameteridentification into a decomposed Tensor, the outcome is a Python-List including all the Model-Data (Parametervector --> Value Information, Factormatrices --> Structure Information)
        Params=p.decparamIDD(Heater, Temperature, Disturbances, Energies, OUTTemperature, set_equalHeaterParameter = set_equalHeaterParameter)
        # Safe Model Data (Parametervector --> Value Information, Factormatrices --> Structure Information) as a JSON-String into the Model-File
        p.safe_model(filename, zonename, Params, fromD, toD)
        return Params

    def identification_with_calibration(self,filename,WeekendID, heaterdata, zonename, ID_heater,heaters_number,ID_disturbances,ID_temperature,ID_fullload,ID_energy,fromD,toD,fromT,toT,jevisUser,jevisPW,webservice,set_equalHeaterParameter):
        # Read and prepare measured Data of the given Timeperiod
        [Temperature,OUTTemperature,Disturbances,Heater,Energies,weekend_operation]=p.totalprep(WeekendID,heaterdata, ID_heater,heaters_number,ID_disturbances,ID_temperature,ID_fullload,ID_energy,fromD,toD,fromT,toT,jevisUser,jevisPW,webservice)
        # Parameteridentification into a decomposed Tensor, the outcome is a Python-List including all the Model-Data (Parametervector --> Value Information, Factormatrices --> Structure Infromation, Calibrationvectors --> Calibration Information)
        Params = p.decomposed_Parameteridentification_with_calibration(Heater, Temperature, Disturbances, Energies, OUTTemperature, set_equalHeaterParameter = set_equalHeaterParameter)
        # Safe Model Data (Parametervector --> Value Information, Factormatrices --> Structure Infromation, Calibrationvectors --> Calibration Information) as a JSON-String into the Model-File
        p.safe_model_with_calibration(filename, zonename, Params, fromD, toD)
        return Params

    #model validation/Plotting

    def Validation(self,WeekendID,heaterdata, zonename, ID_heater,heaters_number,ID_disturbances,ID_temperature,ID_fullload,ID_energies,fromDv,toDv,fromTv,toTv,scale,Params,jevisUser,jevisPW,webservice):
        # Read and prepare measured Data of the given Timeperiod
        [Temperature,OUTTemperature,Disturbances,Heater,Energies,weekend_operation]=p.totalprep(WeekendID,heaterdata, ID_heater,heaters_number,ID_disturbances,ID_temperature,ID_fullload,ID_energies,fromDv,toDv,fromTv,toTv,jevisUser,jevisPW,webservice)
        # Calculating Zonetemperature-Trend with the given Signals and the Model-Data, starting with the initial-measured Temperature
        Estimated_temp=p.decvalidS(zonename, Heater, Temperature[0], Disturbances, Energies, Params)
        # Dump Data
        p.DataDump_Validation(zonename, OUTTemperature, Estimated_temp, Heater, Disturbances, Energies, fromDv, toDv, fromTv,toTv)
        # Plotting measured Data and the calculated Temperature-Trend
        p.Modelvalidation_plot(zonename, fromDv,toDv,fromTv,toTv)
        return Estimated_temp

    def Validation_with_calibration(self,WeekendID,heaterdata, zonename, ID_heater,heaters_number,ID_disturbances,ID_temperature,ID_fullload,ID_energies,fromDv,toDv,fromTv,toTv,scale,Params,jevisUser,jevisPW,webservice):
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


    def Regulation(self,filename, TimeID, WeekendID, heaterdata, zonename,weightening_ratio,IDs_disturbances, ID_temperature,ID_heaters,ID_fullload,ID_energy,Setpoints,Heaters_number,fullload_hall,horizon,username,password,webservice,Setpoint_new):
        # loading model data of a given zone into a python-list from the modelfile
        ModellParam = r.load_model(filename, zonename)
        # read the current measured Data needed for the Control-Algortihm (Disturbances, Temperature, Heater)
        jevisValues=self.jevis.read(WeekendID, ID_heaters, IDs_disturbances, ID_energy, ID_temperature, username, password, webservice)
        # Read the current time and convert to a date- and a time-string
        [now_day, now_time] = r.Time_reader(TimeID,username,password,webservice)
        # create a Array of Setpoints for the given Control-Horizon
        Setpoint = r.Set_Setpoint(Setpoints[0], Setpoints[1], jevisValues.weekendOperation, now_day, now_time, horizon)
        print("Setpoint")
        print(Setpoint)
        # Control-Algorithm, calculating the optimal Controlvalues with the given Weightening for the next 3 Timesteps
        Controlvalues = r.Control(heaterdata, jevisValues.temperatureValues, Heaters_number, jevisValues.disturbancesValues, jevisValues.energyValues, Setpoint, ModellParam, fullload_hall,
                              weightening_ratio, horizon)
        # Split the Controlvalues into Heater (on/off) and fullload (on/off) signals
        [fullload, heaters] = r.Fullload_sep(heaterdata, Controlvalues, jevisValues.heaterValues, Heaters_number, fullload_hall)
        return fullload, heaters

    def Regulation_calibration(self,filename, TimeID, WeekendID, heaterdata, zonename,weightening_ratio,IDs_disturbances, ID_temperature,ID_heaters,ID_fullload,ID_energy,Setpoints,Heaters_number,fullload_hall,horizon,username,password,webservice, Setpoint_new):
        print(Setpoints)
        # loading model data of a given zone into a python-list from the modelfile
        ModellParam = r.load_model_with_calibration(filename, zonename)
        # read the current measured Data needed for the Control-Algortihm (Disturbances, Temperature, Heater)
        jevisValues = self.jevis.read(WeekendID,ID_heaters,IDs_disturbances, ID_energy, ID_temperature)
        # Read the current time and convert to a date- and a time-string
        [now_day, now_time] = r.Time_reader(TimeID,username,password,webservice)
        # create a Array of Setpoints for the given Control-Horizon
        print(Setpoints)
        Setpoint = r.Set_Setpoint(Setpoints[0], Setpoints[1], jevisValues.weekendOperation, now_day, now_time, horizon)
        # Control-Algorithm, calculating the optimal Controlvalues with the given Weightening for the next 3 Timesteps
        Controlvalues = r.Control_with_calibration(heaterdata, jevisValues.temperatureValues, Heaters_number, jevisValues.disturbancesValues, jevisValues.energyValues, Setpoint, ModellParam, fullload_hall,
                                               weightening_ratio, horizon)
        # Split the Controlvalues (0 / 1 / 2) into Heater ( on(1) / off(0) ) and fullload ( on(1) / off(0) ) signals
        [fullload, heaters] = r.Fullload_sep(heaterdata, Controlvalues, jevisValues.heaterValues, Heaters_number, fullload_hall)
        return fullload, heaters

    ########## CALL - FUNCTIONS ##########
    # Modelidentifcation: Call Functions for the model and parameter identifier
    # Loading data from JEVis and prepare Data (e.g. generating 5 min intervals)
    # Creating Modelstructure and calculating parameters
    # Write Models into Models.txt / JEVis

    def modelidentification(self,zonename, configurationfile, fromD, toD, calibration='true', set_equalHeaterParameter='false'):
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
            for j in range(len(self.configData.__systems)):
                # Iteration through all halls/systems j
                for n in range(len(self.configData.__systems[j])):
                    # Iteration through the zones n of hall/system j
                    if calibration=='true':
                        # Starting the identification-Function given above
                        self.identification_with_calibration(self.configData.modelfile, self.configData.objectIds.weekendOperationRead[i], self.configData.__heaterdata, self.configData.zonenames[i], self.configData.objectIds.heatersRead[i], np.size(self.configData.objectIds.heatersRead[i]),
                                                             self.configData.objectIds.disturbancesRead[i],
                                                             self.configData.objectIds.temperaturesRead[i], self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[i], fromD, toD, '00', '00', self.configData.jevisUser,
                                                             self.configData.jevisPW, self.configData.webservice, set_equalHeaterParameter)
                    elif calibration=='false':
                        # Starting the identification-Function given above
                        self.identification(self.configData.modelfile, self.configData.objectIds.weekendOperationRead[i], self.configData.__heaterdata, self.configData.zonenames[i], self.configData.objectIds.heatersRead[i], np.size(self.configData.objectIds.heatersRead[i]),
                                            self.configData.objectIds.disturbancesRead[i],
                                            self.configData.objectIds.temperaturesRead[i], self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[i], fromD, toD, '00', '00', self.configData.jevisUser,
                                            self.configData.jevisPW, self.configData.webservice, set_equalHeaterParameter)
                    else:
                        print('ERROR: calibration-variable can only be true or false!')
                    i = i + 1
        elif zonename in self.configData.systemnames:
            # Modelidentifiction for one system (e.g. Hall 1 and 3 (LF))
            # create index array for the zone according their position in the configuration-arrays
            index = self.configData.__systems
            i = 0
            for j in range(np.size(self.configData.__systems)):
                for n in range(np.size(self.configData.__systems[j])):
                    index[j][n] = i
                    i = i + 1
            j = self.configData.systemnames.index(zonename)
            for n in range(len(self.configData.__systems[j])):
                # Iteration through the zones n of hall/system j
                if calibration == 'true':
                    # Starting the identification-Function given above
                    self.identification_with_calibration(self.configData.modelfile, self.configData.objectIds.weekendOperationRead[index[j][n]], self.configData.__heaterdata, self.configData.zonenames[index[j][n]], self.configData.objectIds.heatersRead[index[j][n]],
                                                         np.size(self.configData.objectIds.heatersRead[index[j][n]]),
                                                         self.configData.objectIds.disturbancesRead[index[j][n]],
                                                         self.configData.objectIds.temperaturesRead[index[j][n]], self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[index[j][n]], fromD, toD, '00',
                                                    '00', self.configData.jevisUser,
                                                         self.configData.jevisPW, self.configData.webservice, set_equalHeaterParameter)
                elif calibration == 'false':
                    # Starting the identification-Function given above
                    self.identification(self.configData.modelfile, self.configData.objectIds.weekendOperationRead[index[j][n]], self.configData.__heaterdata, self.configData.zonenames[index[j][n]], self.configData.objectIds.heatersRead[index[j][n]], np.size(self.configData.objectIds.heatersRead[index[j][n]]),
                                        self.configData.objectIds.disturbancesRead[index[j][n]],
                                        self.configData.objectIds.temperaturesRead[index[j][n]], self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[index[j][n]], fromD, toD, '00', '00', self.configData.jevisUser,
                                        self.configData.jevisPW, self.configData.webservice, set_equalHeaterParameter)
                else:
                    print('ERROR: calibration-variable can only be true or false!')
                i = i + 1

        else:
            # Modelidentification of only one zone
            # Figure out the Position of the IDs associated to the given Zone
            i = self.configData.zonenames.index(zonename)
            print("zone name")
            print(i)
            for list in self.configData.__systems:
                for element in list:
                    if element == zonename:
                        j = self.configData.__systems.index(list)
            # Identification of the given Zone
            if calibration=='true':
                # Starting the identification-Function given above
                self.identification_with_calibration(self.configData.modelfile, self.configData.objectIds.weekendOperationRead[i], self.configData.__heaterdata, self.configData.zonenames[i], self.configData.objectIds.heatersRead[i], np.size(self.configData.objectIds.heatersRead[i]),
                                                     self.configData.objectIds.disturbancesRead[i], self.configData.objectIds.temperaturesRead[i], self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[i], fromD, toD, '00', '00',
                                                     self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice, set_equalHeaterParameter)
            elif calibration=='false':
                # Starting the identification-Function given above
                self.identification(self.configData.modelfile, self.configData.objectIds.weekendOperationRead[i], self.configData.__heaterdata, self.configData.zonenames[i], self.configData.objectIds.heatersRead[i], np.size(self.configData.objectIds.heatersRead[i]),
                                    self.configData.objectIds.disturbancesRead[i], self.configData.objectIds.temperaturesRead[i], self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[i], fromD, toD, '00', '00',
                                    self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice, set_equalHeaterParameter)
            else:
                print('ERROR: calibration-variable can only be true or false!')



# validation-plot-functions: call-functions for the ploting
    # ploting simulation results over a choosen timeperiod with the recent models

    def validation_plot(self,zonename, configurationfile, fromDv, toDv,calibration='true'):
        # load set-up information of all zones
        #[ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = ConfigLoader.configuration_loader(configurationfile)
        #configData = ConfigLoader.configuration_loader(configurationfile)
        if zonename == 'all':
            # Plotting of all zones i
            i = 0
            for j in range(np.size(self.configData.__systems)):
                # Iteration through all halls/systems j
                for n in range(np.size(self.configData.__systems[j])):
                    # Iteration through the zones n of hall/system j
                    if calibration=='true':
                        # load model-data into a python-list from the modelfile of the given zone
                        Params = r.load_model_with_calibration(self.configData.modelfile, self.configData.zonenames[i])
                        # Starting the Plotting-Function given above
                        self.Validation_with_calibration(self.configData.objectIds.weekendOperationRead[i], self.configData.__heaterdata, self.configData.zonenames[i], self.configData.objectIds.heatersRead[i], np.size(self.configData.objectIds.heatersRead[i]), self.configData.objectIds.disturbancesRead[i],
                                                         self.configData.objectIds.temperaturesRead[i],
                                                         self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[i], fromDv, toDv, '00',
                                            '00', 0, Params, self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice)
                    elif calibration=='false':
                        # load model-data into a python-list from the modelfile of the given zone
                        Params = r.load_model(self.configData.modelfile, self.configData.zonenames[i])
                        # Starting the Plotting-Function given above
                        self.Validation(self.configData.objectIds.weekendOperationRead[i], self.configData.__heaterdata, self.configData.zonenames[i], self.configData.ObjectIDs[0][i], np.size(self.configData.ObjectIDs[0][i]), self.configData.ObjectIDs[2][i],
                                        self.configData.objectIds.temperaturesRead[i],
                                        self.configData.objectIds_2[3][j], self.configData.objectIds[4][i], fromDv, toDv, '00',
                               '00', 0, Params, self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice)
                    else:
                        print('ERROR: calibration-variable can only be true or false!')
                    i = i + 1
        elif zonename in self.configData.systemnames:
            # Modelidentifiction for one system (e.g. Hall 1 and 3 (LF))
            # create index array for the zone according their position in the configuration-arrays
            index = self.configData.__systems
            i = 0
            for j in range(np.size(self.configData.__systems)):
                for n in range(np.size(self.configData.__systems[j])):
                    index[j][n] = i
                    i = i + 1
            j = self.configData.systemnames.index(zonename)
            for n in range(len(self.configData.__systems[j])):
                # Iteration through the zones n of hall/system j
                if calibration == 'true':
                    # load model-data into a python-list from the modelfile of the given zone
                    Params = r.load_model_with_calibration(self.configData.modelfile, self.configData.zonenames[index[j][n]])
                    # Starting the Plotting-Function given above
                    self.Validation_with_calibration(self.configData.ObjectIDs[7][index[j][n]], self.configData.__heaterdata, self.configData.zonenames[index[j][n]], self.configData.objectIds_2[0][index[j][n]], np.size(self.configData.objectIds_2[0][index[j][n]]),
                                                     self.configData.objectIds_2[2][index[j][n]],
                                                     self.configData.objectIds_2[1][index[j][n]],
                                                     self.configData.objectIds_2[3][j], self.configData.objectIds_2[4][index[j][n]], fromDv, toDv, '00',
                                            '00', 0, Params, self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice)
                elif calibration == 'false':
                    # load model-data into a python-list from the modelfile of the given zone
                    Params = r.load_model(self.configData.modelfile, self.configData.zonenames[index[j][n]])
                    # Starting the Plotting-Function given above
                    self.Validation(self.configData.objectIds_2[7][index[j][n]], self.configData.__heaterdata, self.configData.zonenames[index[j][n]], self.configData.objectIds_2[0][index[j][n]], np.size(self.configData.objectIds_2[0][index[j][n]]), self.configData.objectIds_2[2][index[j][n]],
                                    self.configData.objectIds_2[1][index[j][n]],
                                    self.configData.objectIds_2[3][j], self.configData.objectIds_2[4][index[j][n]], fromDv, toDv, '00',
                           '00', 0, Params, self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice)
                else:
                    print('ERROR: calibration-variable can only be true or false!')

        else:
            # Plotting of just one Zone
            # Figure out the Position of the IDs associated to the given Zone
            i = self.configData.zonenames.index(zonename)
            for list in self.configData.__systems:
                for element in list:
                    if element == zonename:
                        j = self.configData.__systems.index(list)
            if calibration=='true':
                # load model-data into a python-list from the modelfile of the given zone
                Params = r.load_model_with_calibration(self.configData.modelfile, self.configData.zonenames[i])
                # Starting the Plotting-Function given above
                self.Validation_with_calibration(self.configData.objectIds.weekendOperationRead[i], self.configData.__heaterdata, self.configData.zonenames[i], self.configData.objectIds.heatersRead[i], np.size(self.configData.objectIds.heatersRead[i]), self.configData.objectIds.disturbancesRead[i], self.configData.objectIds.temperaturesRead[i],
                                                 self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[i], fromDv, toDv, '00', '00', 0, Params, self.configData.jevisUser, self.configData.jevisPW,
                                                 self.configData.webservice)
            elif calibration=='false':
                # load model-data into a python-list from the modelfile of the given zone
                Params = r.load_model(self.configData.modelfile, self.configData.zonenames[i])
                # Starting the Plotting-Function given above
                self.Validation(self.configData.objectIds.weekendOperationRead[i], self.configData.__heaterdata, self.configData.zonenames[i], self.configData.objectIds.heatersRead[i], np.size(self.configData.objectIds.heatersRead[i]), self.configData.objectIds.disturbancesRead[i], self.configData.objectIds.temperaturesRead[i],
                                self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[i], fromDv,
                                toDv, '00', '00', 0, Params, self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice)
            else:
                print('ERROR: calibration-variable can only be true or false!')

# Control-Functions: Call Functions for the Regulation-Functions:
    # configuration loading
    # Model loading (calibrated or uncalibrated Model)
    # (Disturbance Observing)
    # Regulation - Algorithms
    # Writing on JEVis


    def Controlfunction(self,systemname,configurationfile,TimeID,calibration='true'):
        print("control")
        print(self.configData.jevisUser)
        
        #[ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = ConfigLoader.configuration_loader(configurationfile)
        #configData = ConfigLoader.configuration_loader(configurationfile)
        setpoints=self.jevis.readSetpoints(self.configData.objectIds.setpointsRead)
        #printconfig(configurationfile)
        # weightfactor: Ratio of the Cost of comfort (setpoint fulfillment) versus Cost of energy consumption (Sum of the heater/input/control signals)
        if systemname == 'all':
            # Control of all zones i
            index = self.configData.__systems
            # Creating array of indices for the different zones according to their representation in the ID-Arrays
            i=0
            for j in range(np.size(self.configData.__systems)):
                for n in range(np.size(self.configData.__systems[j])):
                    index[j][n] = i
                    i=i+1
            # Iteration through all zones
            for j in range(np.size(self.configData.__systems)):
                print(self.configData.systemnames[j])
                # initialize empty arrays for the calculated control-signals
                fullload = [''] * np.size(self.configData.__systems[j])
                heaters = [''] * np.size(self.configData.__systems[j])
                for n in range(np.size(self.configData.__systems[j])):
                    print('Zone ' + str(self.configData.__systems[j][n] + 1))
                    if calibration=='true':
                        # Starting Regulation-Function given above
                        #filename, TimeID, WeekendID, heaterdata, zonename,weightening_ratio,IDs_disturbances, ID_temperature,ID_heaters,ID_fullload,ID_energy,Setpoints,Heaters_number,fullload_hall,horizon,username,password,webservice
                        [fullload[n], heaters[n]] = self.Regulation_calibration(self.configData.modelfile, TimeID, self.configData.objectIds.weekendOperationRead[index[j][n]], self.configData.__heaterdata, self.configData.zonenames[index[j][n]], self.configData.weightfactor[index[j][n]], self.configData.objectIds.disturbancesRead[index[j][n]], self.configData.objectIds.temperaturesRead[index[j][n]], self.configData.objectIds.heatersRead[index[j][n]], self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[index[j][n]], self.configData.objectIds.setpointsValues[index[j][n]], len(self.configData.objectIds.heatersRead[index[j][n]]), [0, 0, 0], self.configData.horizon[index[j][n]], self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice, self.configData.objectIds.setpointsRead)
                    elif calibration=='false':
                        # Starting Regulation-Function given above
                        [fullload[n], heaters[n]] = self.Regulation(self.configData.modelfile, TimeID, self.configData.objectIds.weekendOperationRead[index[j][n]], self.configData.__heaterdata, self.configData.zonenames[index[j][n]],
                                                                    self.configData.weightfactor[index[j][n]], self.configData.objectIds.disturbancesRead[index[j][n]],
                                                                    self.configData.objectIds.temperaturesRead[index[j][n]],
                                                                    self.configData.objectIds.heatersRead[index[j][n]], self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[index[j][n]],
                                                                    setpoints[index[j][n]],
                                                                    len(self.configData.objectIds.heatersRead[index[j][n]]), [0, 0, 0], self.configData.horizon[index[j][n]],
                                                                    self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice, self.configData.objectIds.setpointsRead)
                    else:
                        print('ERROR: calibration-variable can only be true or false!')

                # fullload set parameter over the next 3 timesteps: if in a Hall is fullload set by one Zone, all other Zones of that hall need to be in fullload too!
                fullload_hall = np.zeros(int(len(fullload[0]) / len(self.configData.objectIds.heatersWrite[index[j][0]])))
                # Iteration through all systems and check if a Zone in the system needs Fullload
                # if so, all Control-Signals of the Zones of that system need to be recalculated, only allowing fullload or off signals (2 / 0)
                # Iteration through the systems
                for n in range(len(self.configData.__systems[j])):
                    # Iteration through the 3 timesteps, that will be written to JEVis
                    for z in range(len(fullload_hall)):
                        # Iteration through the zones of a system
                        for i in range(z * len(self.configData.objectIds.heatersWrite[index[j][n]]), (z + 1) * len(self.configData.objectIds.heatersWrite[index[j][n]])):
                            # check if Zone of the system needs fullload
                            if fullload[n][i] == 1:
                                fullload_hall[z] = 1
                    if calibration=='true':
                        # Starting Regulation-Function given above, with the given fullload-demand
                        [fullload[n], heaters[n]] = self.Regulation_calibration(self.configData.modelfile, TimeID, self.configData.objectIds.weekendOperationRead[index[j][n]], self.configData.__heaterdata, self.configData.zonenames[index[j][n]], self.configData.weightfactor[index[j][n]], self.configData.objectIds.disturbancesRead[index[j][n]],
                                                                                self.configData.objectIds.temperaturesRead[index[j][n]], self.configData.objectIds.heatersRead[index[j][n]], self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[index[j][n]],
                                                                                self.configData.objectIds.setpointsValues[index[j][n]], len(self.configData.objectIds.heatersRead[index[j][n]]), fullload_hall, self.configData.horizon[index[j][n]], self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice, self.configData.objectIds.setpointsRead)
                    elif calibration=='false':
                        # Starting Regulation-Function given above, with the given fullload-demand
                        [fullload[n], heaters[n]] = self.Regulation(self.configData.modelfile, TimeID, self.configData.objectIds.weekendOperationRead[index[j][n]], self.configData.__heaterdata, self.configData.zonenames[index[j][n]], self.configData.weightfactor[index[j][n]], self.configData.objectIds.disturbancesRead[index[j][n]],
                                                                    self.configData.objectIds.temperaturesRead[index[j][n]], self.configData.objectIds.heatersRead[index[j][n]], self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[index[j][n]],
                                                                    setpoints[index[j][n]], len(self.configData.objectIds.heatersRead[index[j][n]]), fullload_hall, self.configData.horizon[index[j][n]], self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice, self.configData.objectIds.setpointsRead)
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
            index = self.configData.__systems
            i = 0
            for j in range(np.size(self.configData.__systems)):
                for n in range(np.size(self.configData.__systems[j])):
                    index[j][n] = i
                    i = i + 1
            j = self.configData.systemnames.index(systemname)
            # initialize empty arrays for the calculated control-signals
            fullload = [''] * np.size(self.configData.__systems[j])
            heaters = [''] * np.size(self.configData.__systems[j])
            # Iteration through all Zones of one system
            for n in range(np.size(self.configData.__systems[j])):
                print(self.configData.zonenames[index[j][n]])
                if calibration=='true':
                    # Starting Regulation-Function given above
                    [fullload[n], heaters[n]] = self.Regulation_calibration(self.configData.modelfile, TimeID, self.configData.objectIds.weekendOperationRead[index[j][n]], self.configData.__heaterdata, self.configData.zonenames[index[j][n]], self.configData.weightfactor[index[j][n]], self.configData.objectIds.disturbancesRead[index[j][n]],
                                                                            self.configData.objectIds.temperaturesRead[index[j][n]], self.configData.objectIds.heatersRead[index[j][n]], self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[index[j][n]],
                                                                            self.configData.objectIds.setpointsValues[index[j][n]], len(self.configData.objectIds.heatersRead[index[j][n]]), [0, 0, 0], self.configData.horizon[index[j][n]], self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice, self.configData.objectIds.setpointsRead)
                elif calibration=='false':
                    # Starting Regulation-Function given above
                    [fullload[n], heaters[n]] = self.Regulation(self.configData.modelfile, TimeID, self.configData.objectIds.weekendOperationRead[index[j][n]], self.configData.__heaterdata, self.configData.zonenames[index[j][n]], self.configData.weightfactor[index[j][n]], self.configData.objectIds.disturbancesRead[index[j][n]],
                                                                self.configData.objectIds.temperaturesRead[index[j][n]], self.configData.objectIds.heatersRead[index[j][n]], self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[index[j][n]],
                                                                setpoints[index[j][n]], len(self.configData.objectIds_2[0][index[j][n]]), [0, 0, 0], self.configData.horizon[index[j][n]], self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice, self.configData.objectIds.setpointsRead)
                else:
                    print('ERROR: calibration-variable can only be true or false!')
            # fullload set parameter over the next 3 timesteps: if in a Hall is fullload set by one Zone, all other Zones of that hall need to be in fullload too!
            # Iteration through the system and check if a Zone in the system needs Fullload
            # if so, all Control-Signals of the Zones of that system need to be recalculated, only allowing fullload or off signals (2 / 0)
            fullload_hall = np.zeros(int(len(fullload[0]) / len(self.configData.objectIds.heatersWrite[index[j][0]])))
            for n in range(np.size(self.configData.__systems[j])):
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
                    [fullload[n], heaters[n]] = self.Regulation_calibration(self.configData.modelfile, TimeID, self.configData.objectIds.weekendOperationRead[index[j][n]], self.configData.__heaterdata, self.configData.zonenames[index[j][n]], self.configData.weightfactor[index[j][n]], self.configData.objectIds.disturbancesRead[index[j][n]],
                                                                            self.configData.objectIds.temperaturesRead[index[j][n]], self.configData.objectIds.heatersRead[index[j][n]], self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[index[j][n]],
                                                                            self.configData.objectIds.setpointsValues[index[j][n]], len(self.configData.objectIds.heatersRead[index[j][n]]), fullload_hall, self.configData.horizon[index[j][n]], self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice, self.configData.objectIds.setpointsRead)
                elif calibration=='false':
                    # Starting Regulation-Function given above, with the given fullload-demand
                    [fullload[n], heaters[n]] = self.Regulation(self.configData.modelfile, TimeID, self.configData.objectIds.weekendOperationRead[index[j][n]], self.configData.__heaterdata, self.configData.zonenames[index[j][n]], self.configData.weightfactor[index[j][n]], self.configData.objectIds.disturbancesRead[index[j][n]],
                                                                self.configData.objectIds.temperaturesRead[index[j][n]], self.configData.objectIds.heatersRead[index[j][n]], self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[index[j][n]],
                                                                setpoints[index[j][n]], len(self.configData.objectIds.heatersRead[index[j][n]]), fullload_hall, self.configData.horizon[index[j][n]], self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice, self.configData.objectIds.setpointsRead)
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
            index = self.configData.__systems
            i = self.configData.zonenames.index(zonename)
            for list in self.configData.__systems:
                for element in list:
                    if element == zonename:
                        j = self.configData.__systems.index(list)
            # initialize empty arrays for the calculated control-signals
            fullload = ['']
            heaters = ['']
            if calibration=='true':
                # Starting Regulation-Function given above
                [fullload, heaters] = self.Regulation_calibration(self.configData.modelfile, TimeID, self.configData.objectIds.weekendOperationRead[i], self.configData.__heaterdata, self.configData.zonenames[i], self.configData.weightfactor[i], self.configData.objectIds.disturbancesRead[i],
                                                                  self.configData.objectIds.temperaturesRead[i], self.configData.objectIds.heatersRead[i], self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[i],
                                                                  self.configData.objectIds.setpointsValues[i], len(self.configData.objectIds.heatersRead[i]), [0, 0, 0], self.configData.horizon[i], self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice, self.configData.objectIds.setpointsRead)
            elif calibration=='false':
                # Starting Regulation-Function given above
                [fullload, heaters] = self.Regulation(self.configData.modelfile, TimeID, self.configData.objectIds.weekendOperationRead[i], self.configData.__heaterdata, self.configData.zonenames[i], self.configData.weightfactor[i], self.configData.objectIds.disturbancesRead[i],
                                                      self.configData.objectIds.temperaturesRead[i], self.configData.objectIds.heatersRead[i], self.configData.objectIds.fullloadRead[j], self.configData.objectIds.energyRead[i],
                                                      setpoints[i], len(self.configData.objectIds.heatersRead[i]), [0, 0, 0], self.configData.horizon[i], self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice, self.configData.objectIds.setpointsRead)
            else:
                print('ERROR: calibration-variable can only be true or false!')
                # write controlvalues into JEVis
                self.jevis.controlWrite(self.configData.objectIds.heatersWrite[i], self.configData.objectIds.fullloadWrite[j], fullload, heaters, self.configData.jevisUser, self.configData.jevisPW, self.configData.webservice)