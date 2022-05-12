import configparser
import re
from typing import Any


class ConfigLoader:

    def __init__(self,configfile) -> None:
        self.config = self.__loadConfigFile(configfile)
        self.configData = Config()
        super().__init__()


    def __loadConfigFile(self,configfile):

        config = configparser.ConfigParser()
        config.sections()
        config.read(configfile)
        return config

        #self.configData = Config()


    def load(self):
        configData = Config()



        self.__jevisAccess()

        # Read Heater-Data (in the Case of Siosta, how much percentage of load is in fullload/partload)

        self.__heaterdata()

        # Read in the System assigned Names and IDs of Signals (meaning the fullload-signals for SIOSTA)
        self.__systems()

        # read the Zone assigned Names and IDs of Signals
        # Define the sizes of the python arrays and initializing them
        zonecount = int(self.config['Systems']['Zone Count'])

        Outdoor_Temperature = self.config['IDs of Disturbances']['Outdoor Temperature']
        self.__loadObjectIds(Outdoor_Temperature)


        Outdoor_Temperature = self.config['IDs of Disturbances']['Outdoor Temperature']
        # Go through all Zones and read the needed Signal IDs
        self.__loadHeaterWrite(self.config, configData)

        self.__loadTimeId()
        self.__loadRunSystem()

        self.__loadModelidentification()

        self.__loadCalibartion()

        # Create a List with all IDs (read-IDs and write-IDs)
        #configData.objectIds_2 = [configData.objectIds.heatersRead, configData.objectIds.temperaturesRead, configData.objectIds.disturbancesRead, configData.objectIds.fullloadRead,
                                  #configData.objectIds.energyRead,
                                  #configData.objectIds.heatersWrite,
                                  #configData.objectIds.fullloadWrite, configData.objectIds.weekendOperationRead]
        return configData


    def __loadHeaterWrite(self):
        for i in range(len(self.configData.zonenames)):
            # create the Zonename, that need to be searched in the Config-file
            name = 'IDs Zone ' + str(i + 1)
            Heaters_variable = []
            for j in self.config['IDs of Heater Variables'][name].split(";"):
                Heaters_variable_2 = []
                for k in j.split(","):
                    Heaters_variable_2.append(k.replace(" ", ""))
                Heaters_variable.append(Heaters_variable_2)

            self.configData.objectIds.heatersWrite.append(Heaters_variable)


    def __loadObjectIds(self, Outdoor_Temperature):
        for i in self.configData.zonenames:
            self.configData.objectIds.weekendOperationRead.append(self.config['IDs for Weekend Operation']["IDs " + i])
            self.configData.objectIds.temperaturesRead.append(self.config['IDs of Temperature Measurements']["IDs " + i])
            print("configData.objectIds.Temperatures")
            print(self.configData.objectIds.temperaturesRead)
            self.configData.objectIds.heatersRead.append(
                self.config['IDs of Heater Measurements']["IDs " + i].replace(' ', '').split(';'))
            self.configData.horizon.append(int(self.config['control']['horizon ' + i]))
            self.configData.weightfactor.append(int(self.config['control']['weightfactor ' + i]))
            # configData.objectIds.Heaters_measurement.append(config['IDs of Heater Measurements']["IDs "+i].replace(' ', '').split(';'))
            if self.config['IDs of Disturbances']['Outdoor-Door ' + i] != '':
                self.configData.objectIds.disturbancesRead.append(
                    (Outdoor_Temperature + '; ' + self.config['IDs of Disturbances']['Outdoor-Door ' + i]).replace(' ',
                                                                                                              '').split(
                        ';'))
            else:
                self.configData.objectIds.disturbancesRead.append(Outdoor_Temperature)
            self.configData.objectIds.energyRead.append(
                self.config['IDs of Energy Consumer Measurements']["IDs " + i].replace(' ', '').split(';'))
            Stepoint = []
            for j in (self.config["Setpoints2"]["Setpoint " + i]).split(";"):
                Stepoint2 = []
                for k in j.split(","):
                    if (":" not in k):
                        Stepoint2.append(float(k))
                    else:
                        Stepoint2.append(k.replace(" ", ""))
                Stepoint.append(Stepoint2)
                StepointID = []
                for j in (self.config["Setpoints3"]["Setpoint " + i]).split(";"):
                    Stepoint2 = []
                    for k in j.split(","):
                        Stepoint2.append(k.replace(" ", ""))
                    StepointID.append(Stepoint2)

            self.configData.objectIds.setpointsValues.append(Stepoint)
            self.configData.objectIds.setpointsRead.append(StepointID)
            print(self.configData.objectIds.setpointsRead)


    def __systems(self):
        self.configData.systemnames = self.config['Systems']['Systemnames'].split('; ')
        for i in (self.configData.systemnames):
            self.configData.systems.append(self.config['Systems'][i].split('; '))
            x = re.findall("[0-9]", i)[0]
            self.configData.objectIds.fullloadRead.append(self.config['Fullload Signal Measurements']['ID Fullload ' + x])
            self.configData.objectIds.fullloadWrite.append((self.config['Fullload Variables']['ID Fullload ' + x]).replace(' ', '').split(','))
        for i in self.configData.systems:
            for j in i:
                self.configData.zonenames.append(j)


    def __heaterdata(self):
        self.configData.heaterdata.append(float(self.config['Heater data sheet']['Fullload']))
        self.configData.heaterdata.append(float(self.config['Heater data sheet']['partial load']))


    def __jevisAccess(self):
        # Read URL, User and PW for the JEVis-Service
        self.configData.jevisUser = self.config['JEVis-Service']['jevisUser']
        self.configData.jevisPW = self.config['JEVis-Service']['jevisPW']
        self.configData.webservice = self.config['JEVis-Service']['webservice']
        # Read the model-file Name (probably also the path need to be in there!)
        self.configData.modelfile = self.config['Models']['File']


    def __loadTimeId(self):
        self.configData.timeID = self.config['run']['TimeID']


    def __loadRunSystem(self):
        system = self.config['run']['System']
        self.configData.runSystems = system.split(', ')


    def __loadModelidentification(self):
        self.configData.runModellIdentification = self.config['modelidentification']['run']
        self.configData.modelidentificationFrom = self.config['modelidentification']['from']
        self.configData.toTime = self.config['modelidentification']['to']



    def __loadCalibartion(self):
        self.configData.calibrationValue = self.config['run']['calibration']

    def __loadRunControl(self):
        self.configData = self.config = self.config['control']['run']

class Config:
    def __repr__(self) -> str:
        return super().__repr__()

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
        self.timeID = None
        self.runSystems = None
        self.runModellIdentification = None
        self.runControl = None
        self.modelidentificationFrom = None
        self.modelidentificationTo = None
        self.calibrationValue = None


class ObjectIDs:
    def __repr__(self) -> str:
        return super().__repr__()

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