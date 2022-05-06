import configparser
import re
from typing import Any


class ConfigLoader:

    @staticmethod
    def configuration_loader(configurationfile):
        #print("config")

        configData = Config()

        config = configparser.ConfigParser()
        config.sections()
        config.read(configurationfile)

        ConfigLoader.jevisAccess(config, configData)

        # Read Heater-Data (in the Case of Siosta, how much percentage of load is in fullload/partload)

        ConfigLoader.heaterdata(config, configData)

        # Read in the System assigned Names and IDs of Signals (meaning the fullload-signals for SIOSTA)
        ConfigLoader.systems(config, configData)

        # read the Zone assigned Names and IDs of Signals
        # Define the sizes of the python arrays and initializing them
        zonecount = int(config['Systems']['Zone Count'])

        Outdoor_Temperature = config['IDs of Disturbances']['Outdoor Temperature']
        for i in configData.zonenames:
            configData.objectIds.weekend_operation.append(config['IDs for Weekend Operation']["IDs "+i])
            configData.objectIds.Temperatures.append(config['IDs of Temperature Measurements']["IDs "+i])
            print( "configData.objectIds.Temperatures")
            print(configData.objectIds.Temperatures)
            configData.objectIds.Heaters_measurement.append(config['IDs of Heater Measurements']["IDs "+i].replace(' ', '').split(';'))
            configData.horizon.append(int(config['control']['horizon ' + i]))
            configData.weightfactor.append(int(config['control']['weightfactor ' + i]))
            #configData.objectIds.Heaters_measurement.append(config['IDs of Heater Measurements']["IDs "+i].replace(' ', '').split(';'))
            if config['IDs of Disturbances']['Outdoor-Door ' + i] != '':
                configData.objectIds.Disturbances.append((Outdoor_Temperature + '; ' + config['IDs of Disturbances']['Outdoor-Door ' + i]).replace(' ', '').split(';'))
            else:
                configData.objectIds.Disturbances.append(Outdoor_Temperature)
            configData.objectIds.energetic_measurements.append(config['IDs of Energy Consumer Measurements']["IDs "+i].replace(' ', '').split(';'))
            Stepoint = []
            for j in (config["Setpoints2"]["Setpoint "+i]).split(";"):
                Stepoint2 = []
                for k in j.split(","):
                   if(":" not in k):
                        Stepoint2.append(float(k))
                   else:
                       Stepoint2.append(k.replace(" ",""))
                Stepoint.append(Stepoint2)
                StepointID = []
                for j in (config["Setpoints3"]["Setpoint " + i]).split(";"):
                    Stepoint2 = []
                    for k in j.split(","):
                            Stepoint2.append(k.replace(" ", ""))
                    StepointID.append(Stepoint2)


            #print(Stepoint)
            configData.objectIds.setpoints.append(Stepoint)
            configData.objectIds.setpoints_new.append(StepointID)
            print( configData.objectIds.setpoints_new)
            #print(configData.objectIds.setpoints)

            #print(configData.objectIds.energetic_measurements)

        #for i in range(len(configData.zonenames)):
            #name = 'Zone ' + str(i + 1)
            #configData.horizon.append(int(config['control']['horizon ' + name]))
            #configData.weightfactor.append(int(config['control']['weightfactor ' + name]))

        Outdoor_Temperature = config['IDs of Disturbances']['Outdoor Temperature']
        # Go through all Zones and read the needed Signal IDs
        for i in range(len(configData.zonenames)):
            # create the Zonename, that need to be searched in the Config-file
            name = 'IDs Zone ' + str(i + 1)
            #print(name)
            # Read IDs for weekend operation recognition
            #configData.objectIds.weekend_operation.append(config['IDs for Weekend Operation'][name])
            #print(configData.objectIds.weekend_operation)
            # create the Disturbancename, that need to be searched in the Config-file
            disturbance_name = 'Outdoor-Door Zone ' + str(i + 1)
            # Read the Zone-Temperature (that is the controlled value)
            #configData.objectIds.Temperatures.append(config['IDs of Temperature Measurements'][name])
            # Read the IDs of the Measurement of the Heater-Signals
            #configData.objectIds.Heaters_measurement.append(config['IDs of Heater Measurements'][name].replace(' ', '').split(';'))
            # Read the measured Disturbance-IDs (always starting with the outdoor-temperature)
            #if config['IDs of Disturbances'][disturbance_name] != '':
             #   configData.objectIds.Disturbances.append((Outdoor_Temperature + '; ' + config['IDs of Disturbances'][disturbance_name]).replace(' ', '').split(';'))
                #Disturbances[i] = Disturbances[i].replace(' ', '').split(';')
            #else:
               # configData.objectIds.Disturbances.append(Outdoor_Temperature)
            # Read the measured Energy-IDs
            #configData.objectIds.energetic_measurements.append(config['IDs of Energy Consumer Measurements'][name].replace(' ', '').split(';'))
            # Read the ID of the Heater-Signals to write on
            #Heaters_variables[i] = config['IDs of Heater Variables'][name].replace(' ', '').split(';')
            #Heaters_variables = []
            #for j in config['IDs of Heater Variables'][name].replace(' ', '').split(';'):
            #    configData.objectIds.Heaters_variables.append(j.split(','))


            #Heaters_variables = [''] * zonecount
            #Heaters_variables[i] = config['IDs of Heater Variables'][name].replace(' ', '').split(';')
            Heaters_variable = []
            for j in config['IDs of Heater Variables'][name].split(";"):
                Heaters_variable_2 = []
                for k in j.split(","):
                    #print("Heaters_variables ")
                   # print(k)
                    Heaters_variable_2.append(k.replace(" ",""))
                Heaters_variable.append(Heaters_variable_2)

            configData.objectIds.Heaters_variables.append(Heaters_variable)



                #Heaters_variables[i][j] = Heaters_variables[i][j].split(',')

           # configData.objectIds.Heaters_variables = Heaters_variables


            #for n in configData.zonenames:
                #print(n)
            #print(configData.objectIds.Heaters_variables)
            #for j in range(len(Heaters_variables[i])):
            #    Heaters_variables[i][j] = Heaters_variables[i][j].split(',')

            #print(Heaters_variables)
            # Read the Setpoint-Configurations
            #Setpoints = []
            #setpointname = 'Setpoint Zone ' + str(i + 1)
            #setpoint_str = config['Setpoints'][setpointname].replace(';', ',').replace(' ', '').split(',')
            #print(setpoint_str)
            #setpoint_array = [''] * int(len(setpoint_str) / 2)
            #time_array = [''] * int(len(setpoint_str) / 2)
            #if len(setpoint_str) > 2:
            #    for j in range(int(len(setpoint_str) / 2)):
            #        time_array[j] = setpoint_str[2 * j]
            #        setpoint_array[j] = float(setpoint_str[2 * j + 1])
            #else:
            #    time_array = setpoint_str[0]
            #    setpoint_array = float(setpoint_str[1])
            #Setpoints.append([setpoint_array, time_array])
            #configData.objectIds.setpoints.append(Setpoints)



        # Create a List with all IDs (read-IDs and write-IDs)
        configData.objectIds_2 = [configData.objectIds.Heaters_measurement, configData.objectIds.Temperatures, configData.objectIds.Disturbances, configData.objectIds.Fullload_measurements,
                     configData.objectIds.energetic_measurements,
                     configData.objectIds.Heaters_variables,
                     configData.objectIds.Fullload_variables,configData.objectIds.weekend_operation]
       # print("xxx")
        #print(configData.objectIds.setpoints)
       # print(ObjectIDs, configData.horizon, configData.weightfactor, configData.systems, configData.systemnames, configData.zonenames, configData.objectIds.setpoints, configData.jevisUser, configData.jevisPW, configData.webservice, configData.modelfile, configData.heaterdata)
        return configData

    @staticmethod
    def systems(config, configData):
        configData.systemnames = config['Systems']['Systemnames'].split('; ')
        for i in (configData.systemnames):
            #print(i)
            configData.systems.append(config['Systems'][i].split('; '))
            #print(configData.systems)
            x = re.findall("[0-9]", i)[0]
            #print(x)
            configData.objectIds.Fullload_measurements.append(config['Fullload Signal Measurements']['ID Fullload ' + x])
            #print(configData.objectIds.Fullload_measurements)
            configData.objectIds.Fullload_variables.append((config['Fullload Variables']['ID Fullload ' +x]).replace(' ', '').split(','))
            #configData.zonenames.append(c)
            #print(configData.systems)
            #configData.zonenames = configData.zonenames + configData.systems[x]
            #print(configData.zonenames)
            #print(configData.objectIds.Fullload_variables)
        #print(configData.zonenames)
        for i in configData.systems:
            for j in i:
                configData.zonenames.append(j)

    @staticmethod
    def heaterdata(config, configData):
        configData.heaterdata.append(float(config['Heater data sheet']['Fullload']))
        configData.heaterdata.append(float(config['Heater data sheet']['partial load']))

    @staticmethod
    def jevisAccess(config, configData):
        # Read URL, User and PW for the JEVis-Service
        configData.jevisUser = config['JEVis-Service']['jevisUser']
        configData.jevisPW = config['JEVis-Service']['jevisPW']
        configData.webservice = config['JEVis-Service']['webservice']
        # Read the model-file Name (probably also the path need to be in there!)
        configData.modelfile = config['Models']['File']


class Config:
    def __init__(self):
        self.jevisUser = None
        self.jevisPW = None
        self.webservice = None
        self.modelfile = None
        self.heaterdata = []
        self.systems = []
        self.systemnames = []
        # self.Fullload_measurements = []
        # self.Fullload_variables = []
        self.zonenames = []
        self.objectIds = ObjectIDs()
        self.weightfactor = []
        self.horizon = []
        self.setpoint = []
        #self.objectIds_2 = []


    def __str__(self):
        return "jevisUser: " +self.jevisUser +"jevisPW: "+self.jevisPW +"webservice: "+str(self.webservice)+"modelfile: "+self.modelfile +"heaterdata: "+str(self.heaterdata) +"systems: "+str(self.systems)+"systemnames: "+str(self.systemnames)+"zonenames: "+str(self.zonenames) + "objectIds: "+str(self.objectIds) + "weightfactor: "+str(self.weightfactor) +"horizon: "+ str(self.horizon)+ "setpoint" +str(self.setpoint) +"objectIds_2: "+str(self.objectIds_2)


class ObjectIDs:
    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)

    def __init__(self):
        self.Heaters_measurement = []
        self.Temperatures = []
        self.Disturbances = []
        self.Fullload_measurements = []
        self.energetic_measurements = []
        self.Heaters_variables = []
        self.Fullload_variables = []
        self.weekend_operation = []
        self.setpoints = []
        self.setpoints_new =[]

    def __str__(self):
        return "Heaters_measurement: " + str(self.Disturbances) +"Temperatures: " +str(self.Temperatures) +"Disturbances: " +str(self.Disturbances) +"Fullload_measurements: " +str(self.Fullload_measurements) + "energetic_measurements: " + str(self.energetic_measurements) +"Heaters_variables: " + str(self.Heaters_variables)+\
               "Fullload_variables: "+ str(self.Fullload_variables) + "weekend_operation: "+ str(self.weekend_operation) +"setpoints: "+str(self.setpoints) +"setpoints_new: "+str(self.setpoints_new)

