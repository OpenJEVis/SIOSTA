import dataclasses
import json
import datetime

import numpy as np
import requests
from requests.auth import HTTPBasicAuth

import pytz
from ConfigLoader import *




class JEVis:

    def __init__(self,username,password,webservice):
        self.username = username
        self.password = password
        self.webservice = webservice


    def readSetpoints(self,SetpointIDS):
        #controlJevis = ControlJEVisObject()
        list = []
        for i in SetpointIDS:
            list2 = []
            for j in i:
                list1 = []
                for k in j:
                    #print(k)
                    list1.append(self.requestLastValue(k,datatype="value"))
                list2.append(list1)
            list.append(list2)
        return list

    def write(self,val, objID, fromD, toD, fromT, toT, gap):
        from datetime import datetime, timedelta
        # Write into JEVis ID
        sampleurl = self.webservice + '/objects/' + objID + '/attributes/Value/samples'
        sampleurl = sampleurl + '?' + 'from=' + fromD + 'T' + fromT + '0000&until=' + toD + 'T' + toT + '0000'
        jevisUser = self.username
        jevisPW = self.password
        datetime = datetime.now() + timedelta(hours=00, minutes=gap)
        Zeit = datetime.astimezone().isoformat(timespec='milliseconds')
        payload = '[{"ts":' + '"' + Zeit + '"' + ',"value": ' + '"' + val + '"''}]'
        post = requests.post(sampleurl, auth=HTTPBasicAuth(jevisUser, jevisPW), data=payload)
        # print("Post status: ",post)

    def controlWrite(self,ID_heaters, ID_fullload, fullload, heaters):
        # Function to iterate through all Signals that needed to be written in JEVis
        today = datetime.datetime.today()
        #print(today)
        todayymd = today.strftime("%Y%m%d")
        now1 = datetime.datetime.now()
        timestr1 = now1.strftime("%H%M%S")
        sizeID = len(ID_heaters)
        for i in range(sizeID):
            for j in range(len(ID_heaters[i])):
                self.write(str(heaters[i]), ID_heaters[i][j], todayymd, todayymd, timestr1, timestr1, 0)
        for i in range(len(ID_fullload)):
            self.write(str(fullload[0]), ID_fullload[i], todayymd, todayymd, timestr1, timestr1, 0)
    def read(self,WeekendID, objID_Heaters, objID_disturbances, objID_energy, objID_temperature):
        controlJevis = ControlJEVisObject()
        #controlJevis.setpointValues



        if WeekendID == '':
            controlJevis.weekendOperation = 0
        else:
            data = self.requestLastValue(WeekendID)
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
                data = self.requestLastValue(objID_Heaters[i])
                if data != []:
                    controlJevis.heaterValues[i] = data[0]
                else:
                    controlJevis.heaterValues[i] = 0
        else:
            data = JEVis.requestLastValue(objID_Heaters)
            if data != []:
                controlJevis.heaterValues = data[0]
            else:
                controlJevis.heaterValues = 0

        if np.size(objID_disturbances) > 1:
            controlJevis.disturbancesValues = np.zeros((np.size(objID_disturbances)))
            for i in range(np.size(objID_disturbances)):
                data = self.requestLastValue(objID_disturbances[i])
                if data != []:
                    controlJevis.disturbancesValues[i] = data[0]
                else:
                    controlJevis.disturbancesValues[i] = 0
        else:
            data = self.requestLastValue(objID_disturbances)
            controlJevis.disturbancesValues = data[0]

        if np.size(objID_energy) > 1:
            controlJevis.energyValues = np.zeros((np.size(objID_energy)))
            for i in range(np.size(objID_energy)):
                data = self.requestLastValue(objID_energy[i])
                if data != []:
                    controlJevis.energyValues[i] = data[0]
                else:
                    controlJevis.energyValues[i] = 0
        else:
            data = self.requestLastValue(objID_energy[0])
            controlJevis.energyValues = data[0]

        if np.size(objID_energy) > 1:
            controlJevis.energyValues = np.zeros((np.size(objID_energy)))
            for i in range(np.size(objID_energy)):
                data = self.requestLastValue(objID_energy[i])
                if data != []:
                    controlJevis.energyValues[i] = data[0]
                else:
                    controlJevis.energyValues[i] = 0
        else:
            data = self.requestLastValue(objID_energy[0])
            controlJevis.energyValues = data[0]

        temperature = self.requestLastValue(objID_temperature)
        controlJevis.temperatureValues = temperature[0]
        print(controlJevis)
        return controlJevis
    def requestLastValue(self, objID, datatype="array"):
        print(objID)
        # Function to export the most recent Measurement of an Object vie ID
        # Create the URL with the needed Measurement
        sampleurl = self.webservice + '/objects/' + objID + '/attributes/Value/samples'
        sampleurl = sampleurl + '?' + 'onlyLatest=true'

        # Username & Password
        jevisUser = self.username
        jevisPW = self.password

        # Read JEVis data with URL, Username & Password
        get = requests.get(sampleurl, auth=HTTPBasicAuth(jevisUser, jevisPW))
        print(get.text)

        if get.text == 'Object not found':
            print('ID ', objID, 'not found!')
            json_data = []
        else:
            json_data = json.loads(get.text)
        if(datatype == "array"):
            # inserting values
            vals = np.zeros(1)
            if json_data == []:
                vals = json_data
            else:
                vals[0] = json_data['value']  # values (eg. values of the heater states, door states)
            # Output: latest Values corresponding to the Object ID given
            return [vals]
        else:
            return json_data["value"].replace("\"","")



    # def requestLastValueSetpoint(self, objID, datatype="value"):
    #     # Function to export the most recent Measurement of an Object vie ID
    #     # Create the URL with the needed Measurement
    #     sampleurl = self.webservice + '/objects/' + str(objID) + '/attributes/Value/samples'
    #     sampleurl = sampleurl + '?' + 'onlyLatest=true'
    #
    #     # Username & Password
    #     try:
    #         # Read JEVis data with URL, Username & Password
    #         get = requests.get(sampleurl, auth=HTTPBasicAuth(self.username, self.password))
    #         print(get.text)
    #         if get.text == 'Object not found':
    #             print('ID ', objID, 'not found!')
    #             return 0
    #         else:
    #             json_data = json.loads(get.text)
    #             print(json_data)
    #             return json_data["value"]
    #     except Exception:
    #         print("error")


    def requestDataBetween(self, objID, startDate, startTime, endDate, endTime):
        print(objID)

        sampleurl = self.webservice + '/objects/' + str(objID) + '/attributes/Value/samples'
        sampleurl = sampleurl + '?' + 'from=' + startDate + 'T' + startTime + '0000&until=' + endDate + 'T' + endTime + '0000'
        #print(self.username)
        #print(self.password)
        print(sampleurl)
        get = requests.get(sampleurl, auth=HTTPBasicAuth(self.username, self.password))
        print(get.text)
        if get.text == 'Object not found':
            print('ID ', objID, 'not found!')
            json_data = []
        else:
            json_data = json.loads(get.text)
        #print(json_data)
        length_json = np.size(json_data)  # size detection of json

        # initialization of variables with values and times
        vals = np.zeros((length_json))  # values (eg. values of the heater states, door states)
        times = np.empty((length_json), dtype="S29")  # times

        for i in range(length_json):
            vals[i] = json_data[i]['value']
            # times[i]=json_data[i]['ts']

            ts = datetime.datetime.strptime(json_data[i]['ts'], "%Y-%m-%dT%H:%M:%S.000%z")
            ts_utc = ts.astimezone(pytz.utc)
            times[i] = datetime.datetime.strftime(ts_utc, '%Y-%m-%dT%H:%M:%S.000%z')


        return vals ,times


    def requestTimeZone(self,objID,):

        sampleurl = self.webservice + '/objects/' + objID + '/attributes/Value/samples'
        sampleurl = sampleurl + '?' + 'onlyLatest=true'
        get = requests.get(sampleurl, auth=HTTPBasicAuth(self.username, self.password))

        if get.text == 'Object not found':
            print('ID ', objID, 'not found!')
            json_data = []
        else:
            json_data = json.loads(get.text)

        t = datetime.datetime.strptime(json_data['ts'], "%Y-%m-%dT%H:%M:%S.000%z")
        timezone = t.strftime('%z')

        return timezone


@dataclasses.dataclass
class ControlJEVisObject:

    heaterValues : []
    disturbancesValues : []
    energyValues : []
    temperatureValues : []
    weekendOperation : []

    def __init__(self):
        self.heaterValues = []
        self.disturbancesValues = []
        self.energyValues = []
        self.temperatureValues = []
        self.weekendOperation = []