import configparser
import re
from typing import Any


class ConfigLoader:

    @staticmethod
    def configuration_loader(configurationfile):
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
        ConfigLoader.loadObjectIds(Outdoor_Temperature, config, configData)


        Outdoor_Temperature = config['IDs of Disturbances']['Outdoor Temperature']
        # Go through all Zones and read the needed Signal IDs
        ConfigLoader.loadHeaterWrite(config, configData)

        # Create a List with all IDs (read-IDs and write-IDs)
        #configData.objectIds_2 = [configData.objectIds.heatersRead, configData.objectIds.temperaturesRead, configData.objectIds.disturbancesRead, configData.objectIds.fullloadRead,
                                  #configData.objectIds.energyRead,
                                  #configData.objectIds.heatersWrite,
                                  #configData.objectIds.fullloadWrite, configData.objectIds.weekendOperationRead]
        return configData

    @staticmethod
    def loadHeaterWrite(config, configData):
        for i in range(len(configData.zonenames)):
            # create the Zonename, that need to be searched in the Config-file
            name = 'IDs Zone ' + str(i + 1)
            Heaters_variable = []
            for j in config['IDs of Heater Variables'][name].split(";"):
                Heaters_variable_2 = []
                for k in j.split(","):
                    Heaters_variable_2.append(k.replace(" ", ""))
                Heaters_variable.append(Heaters_variable_2)

            configData.objectIds.heatersWrite.append(Heaters_variable)

    @staticmethod
    def loadObjectIds(Outdoor_Temperature, config, configData):
        for i in configData.zonenames:
            configData.objectIds.weekendOperationRead.append(config['IDs for Weekend Operation']["IDs " + i])
            configData.objectIds.temperaturesRead.append(config['IDs of Temperature Measurements']["IDs " + i])
            print("configData.objectIds.Temperatures")
            print(configData.objectIds.temperaturesRead)
            configData.objectIds.heatersRead.append(
                config['IDs of Heater Measurements']["IDs " + i].replace(' ', '').split(';'))
            configData.horizon.append(int(config['control']['horizon ' + i]))
            configData.weightfactor.append(int(config['control']['weightfactor ' + i]))
            # configData.objectIds.Heaters_measurement.append(config['IDs of Heater Measurements']["IDs "+i].replace(' ', '').split(';'))
            if config['IDs of Disturbances']['Outdoor-Door ' + i] != '':
                configData.objectIds.disturbancesRead.append(
                    (Outdoor_Temperature + '; ' + config['IDs of Disturbances']['Outdoor-Door ' + i]).replace(' ',
                                                                                                              '').split(
                        ';'))
            else:
                configData.objectIds.disturbancesRead.append(Outdoor_Temperature)
            configData.objectIds.energyRead.append(
                config['IDs of Energy Consumer Measurements']["IDs " + i].replace(' ', '').split(';'))
            Stepoint = []
            for j in (config["Setpoints2"]["Setpoint " + i]).split(";"):
                Stepoint2 = []
                for k in j.split(","):
                    if (":" not in k):
                        Stepoint2.append(float(k))
                    else:
                        Stepoint2.append(k.replace(" ", ""))
                Stepoint.append(Stepoint2)
                StepointID = []
                for j in (config["Setpoints3"]["Setpoint " + i]).split(";"):
                    Stepoint2 = []
                    for k in j.split(","):
                        Stepoint2.append(k.replace(" ", ""))
                    StepointID.append(Stepoint2)

            configData.objectIds.setpointsValues.append(Stepoint)
            configData.objectIds.setpointsRead.append(StepointID)
            print(configData.objectIds.setpointsRead)

    @staticmethod
    def systems(config, configData):
        configData.systemnames = config['Systems']['Systemnames'].split('; ')
        for i in (configData.systemnames):
            configData.systems.append(config['Systems'][i].split('; '))
            x = re.findall("[0-9]", i)[0]
            configData.objectIds.fullloadRead.append(config['Fullload Signal Measurements']['ID Fullload ' + x])
            configData.objectIds.fullloadWrite.append((config['Fullload Variables']['ID Fullload ' + x]).replace(' ', '').split(','))
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
        self.zonenames = []
        self.objectIds = ObjectIDs()
        self.weightfactor = []
        self.horizon = []
        self.setpoint = []


    def __str__(self):
        return "jevisUser: " +self.jevisUser +"jevisPW: "+self.jevisPW +"webservice: "+str(self.webservice)+"modelfile: "+self.modelfile +"heaterdata: "+str(self.heaterdata) +"systems: "+str(self.systems)+"systemnames: "+str(self.systemnames)+"zonenames: "+str(self.zonenames) + "objectIds: "+str(self.objectIds) + "weightfactor: "+str(self.weightfactor) +"horizon: "+ str(self.horizon)+ "setpoint" +str(self.setpoint) +"objectIds_2: "+str(self.objectIds_2)


class ObjectIDs:
    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)

    def __init__(self):
        self.heatersRead = []
        self.temperaturesRead = []
        self.disturbancesRead = []
        self.fullloadRead = []
        self.energyRead = []
        self.heatersWrite = []
        self.fullloadWrite = []
        self.weekendOperationRead = []
        self.setpointsValues = []
        self.setpointsRead =[]

    def __str__(self):
        return "Heaters_measurement: " + str(self.disturbancesRead) + "Temperatures: " + str(self.temperaturesRead) + "Disturbances: " + str(self.disturbancesRead) + "Fullload_measurements: " + str(self.fullloadRead) + "energetic_measurements: " + str(self.energyRead) + "Heaters_variables: " + str(self.heatersWrite) +\
               "Fullload_variables: " + str(self.fullloadWrite) + "weekend_operation: " + str(self.weekendOperationRead) + "setpoints: " + str(self.setpointsValues) + "setpoints_new: " + str(self.setpointsRead)

