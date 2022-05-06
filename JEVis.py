import json
from datetime import datetime

import numpy as np
import requests
from requests.auth import HTTPBasicAuth
from ConfigLoader import *

from RegFUNKTIONS import Controlprep



class JEVis:

    def __init__(self,username,password,webservice):
        self.username = username
        self.password = password
        self.webservice = webservice

    @staticmethod
    def readSetpoints(SetpointIDS,username,password,webservice):
        #controlJevis = ControlJEVisObject()
        list = []
        for i in SetpointIDS:
            list2 = []
            for j in i:
                list1 = []
                for k in j:
                    print(k)
                    list1.append(JEVis.requestSetpoint(k, username, password, webservice))
                list2.append(list1)
            list.append(list2)
            return list


    @staticmethod
    def write(val, objID, fromD, toD, fromT, toT, gap, username, password, webservice):
        from datetime import datetime, timedelta
        # Write into JEVis ID
        sampleurl = webservice + '/objects/' + objID + '/attributes/Value/samples'
        sampleurl = sampleurl + '?' + 'from=' + fromD + 'T' + fromT + '0000&until=' + toD + 'T' + toT + '0000'
        jevisUser = username
        jevisPW = password
        datetime = datetime.now() + timedelta(hours=00, minutes=gap)
        Zeit = datetime.astimezone().isoformat(timespec='milliseconds')
        payload = '[{"ts":' + '"' + Zeit + '"' + ',"value": ' + '"' + val + '"''}]'
        post = requests.post(sampleurl, auth=HTTPBasicAuth(jevisUser, jevisPW), data=payload)
        # print("Post status: ",post)

    @staticmethod
    def controlWrite(ID_heaters, ID_fullload, fullload, heaters, username, password, webservice):
        # Function to iterate through all Signals that needed to be written in JEVis
        today = datetime.today()
        print(today)
        todayymd = today.strftime("%Y%m%d")
        now1 = datetime.now()
        timestr1 = now1.strftime("%H%M%S")
        sizeID = len(ID_heaters)
        for i in range(sizeID):
            for j in range(len(ID_heaters[i])):
                JEVis.write(str(heaters[i]), ID_heaters[i][j], todayymd, todayymd, timestr1, timestr1, 0, username,
                            password, webservice)
        for i in range(len(ID_fullload)):
            JEVis.write(str(fullload[0]), ID_fullload[i], todayymd, todayymd, timestr1, timestr1, 0, username, password,
                        webservice)
    @staticmethod
    def read(WeekendID, objID_Heaters, objID_disturbances, objID_energy, objID_temperature, username, password,
             webservice):
        # Read all the needed Measurements to solve the control problem (read all recent measurements according to one Zone)
        print("test3")
        #print(SetpointIDS)
        controlJevis = ControlJEVisObject()


        if WeekendID == '':
            controlJevis.weekendOperation = 0
        else:
            data = JEVis.request(WeekendID, username, password, webservice)
            # print(data)
            if data != [] and data != [[]]:
                controlJevis.weekendOperation = int(data[0])
            else:
                controlJevis.weekendOperation = 0
                print('Weekend-ID empty or does not exist!')
        print('Weekend Operations: ', controlJevis.weekendOperation)

        controlJevis.heaterValues = np.zeros((np.size(objID_Heaters)))
        if np.size(objID_Heaters) > 1:
            for i in range(np.size(objID_Heaters)):
                data = JEVis.request(objID_Heaters[i], username, password, webservice)
                if data != []:
                    controlJevis.heaterValues[i] = data[0]
                else:
                    controlJevis.heaterValues[i] = 0
        else:
            data = JEVis.request(objID_Heaters, username, password, webservice)
            if data != []:
                controlJevis.heaterValues = data[0]
            else:
                controlJevis.heaterValues = 0

        if np.size(objID_disturbances) > 1:
            controlJevis.disturbancesValues = np.zeros((np.size(objID_disturbances)))
            for i in range(np.size(objID_disturbances)):
                data = JEVis.request(objID_disturbances[i], username, password, webservice)
                if data != []:
                    controlJevis.disturbancesValues[i] = data[0]
                else:
                    controlJevis.disturbancesValues[i] = 0
        else:
            data = JEVis.request(objID_disturbances, username, password, webservice)
            controlJevis.disturbancesValues = data[0]

        if np.size(objID_energy) > 1:
            controlJevis.energyValues = np.zeros((np.size(objID_energy)))
            for i in range(np.size(objID_energy)):
                data = JEVis.request(objID_energy[i], username, password, webservice)
                if data != []:
                    controlJevis.energyValues[i] = data[0]
                else:
                    controlJevis.energyValues[i] = 0
        else:
            data = JEVis.request(objID_energy[0], username, password, webservice)
            controlJevis.energyValues = data[0]

        if np.size(objID_energy) > 1:
            controlJevis.energyValues = np.zeros((np.size(objID_energy)))
            for i in range(np.size(objID_energy)):
                data = JEVis.request(objID_energy[i], username, password, webservice)
                if data != []:
                    controlJevis.energyValues[i] = data[0]
                else:
                    controlJevis.energyValues[i] = 0
        else:
            data = JEVis.request(objID_energy[0], username, password, webservice)
            controlJevis.energyValues = data[0]

        temperature = JEVis.request(objID_temperature, username, password, webservice)
        controlJevis.temperatureValues = temperature[0]
        print(controlJevis)
        return controlJevis
    @staticmethod
    def request(objID, username, password, webservice, datatype="value"):
        # Function to export the most recent Measurement of an Object vie ID
        # Create the URL with the needed Measurement
        sampleurl = webservice + '/objects/' + objID + '/attributes/Value/samples'
        sampleurl = sampleurl + '?' + 'onlyLatest=true'

        # Username & Password
        jevisUser = username
        jevisPW = password

        # Read JEVis data with URL, Username & Password
        get = requests.get(sampleurl, auth=HTTPBasicAuth(jevisUser, jevisPW))

        if get.text == 'Object not found':
            print('ID ', objID, 'not found!')
            json_data = []
        else:
            json_data = json.loads(get.text)
        if(datatype == "value"):
            # inserting values
            vals = np.zeros(1)
            if json_data == []:
                vals = json_data
            else:
                vals[0] = json_data['value']  # values (eg. values of the heater states, door states)
            # Output: latest Values corresponding to the Object ID given
            return [vals]
        else:
            print(json_data['value'])

    @staticmethod
    def requestSetpoint(objID, username, password, webservice, datatype="value"):
        # Function to export the most recent Measurement of an Object vie ID
        # Create the URL with the needed Measurement
        sampleurl = webservice + '/objects/' + str(objID) + '/attributes/Value/samples'
        sampleurl = sampleurl + '?' + 'onlyLatest=true'

        # Username & Password
        jevisUser = username
        jevisPW = password
        try:
            # Read JEVis data with URL, Username & Password
            get = requests.get(sampleurl, auth=HTTPBasicAuth(jevisUser, jevisPW))
            print(get.text)
            if get.text == 'Object not found':
                print('ID ', objID, 'not found!')
                return 0
            else:
                json_data = json.loads(get.text)
                print(json_data)
                return json_data["value"]
        except Exception:
            print("error")



class ControlJEVisObject:
    def __init__(self):
        self.heaterValues = []
        self.disturbancesValues = []
        self.energyValues = []
        self.temperatureValues = []
        self.weekendOperation = []
        self.setpointValues = []

    def __str__(self):
        return "heaters_vals: %s, dist_vals: %s, energie_vals: %s,temperature_vals: %s,weekend_operation: %s" % (self.heaterValues, self.disturbancesValues, self.energyValues, self.temperatureValues, self.weekendOperation)
