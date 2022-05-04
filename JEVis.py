import json
from datetime import datetime

import numpy as np
import requests
from requests.auth import HTTPBasicAuth

from RegFUNKTIONS import Controlprep



class JEVis:
    @staticmethod
    def controlRead(WeekendID, objID_Heaters, ID_disturbances, ID_energy, ID_temperature, username, password,
                    webservice):
        # Read
        conrolprepJevis = JEVis.controlprep(WeekendID, objID_Heaters, ID_disturbances, ID_energy, ID_temperature, username,
                                      password, webservice)  # Json lesen
        # Heater
        # heaters_latest = vals[0]
        # Temperature
        # temperature_latest=vals[3]
        # print('Zonetemperature (latest in JEVis):', conrolprepJevis.temperature_vals)
        print("Zonetemperature (latest in JEVis):", conrolprepJevis.temperature_vals)
        # Disturbances
        # dist_latest=vals[1]
        # Energies
        # energie_latest=vals[2]
        # Weekend Operation value
        # weekend_operation = vals[4]
        # return heaters_latest,temperature_latest,dist_latest,energie_latest,weekend_operation
        return conrolprepJevis

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
    def controlprep(WeekendID, objID_Heaters, objID_disturbances, objID_energy, objID_temperature, username, password,
                    webservice):
        # Read all the needed Measurements to solve the control problem (read all recent measurements according to one Zone)
        controlJevis = ControlJEVisObject()

        ids_setpoints = '25626', '25620', '25622', '25627', '25625'
        print(np.size(ids_setpoints))
        Heaters_number = np.size(objID_Heaters)
        sizeD = np.size(objID_disturbances)
        sizeE = np.size(objID_energy)

        if WeekendID == '':
            controlJevis.weekend_operation = 0
        else:
            data = JEVis.dataprepControl(WeekendID, username, password, webservice)
            # print(data)
            if data != [] and data != [[]]:
                controlJevis.weekend_operation = int(data[0])
            else:
                controlJevis.weekend_operation = 0
                print('Weekend-ID empty or does not exist!')
        print('Weekend Operations: ', controlJevis.weekend_operation)

        controlJevis.heaters_vals = np.zeros((np.size(objID_Heaters)))
        if np.size(objID_Heaters) > 1:
            for i in range(np.size(objID_Heaters)):
                data = JEVis.dataprepControl(objID_Heaters[i], username, password, webservice)
                if data != []:
                    controlJevis.heaters_vals[i] = data[0]
                else:
                    controlJevis.heaters_vals[i] = 0
        else:
            data = JEVis.dataprepControl(objID_Heaters, username, password, webservice)
            if data != []:
                controlJevis.heaters_vals = data[0]
            else:
                controlJevis.heaters_vals = 0

        if np.size(objID_disturbances) > 1:
            controlJevis.dist_vals = np.zeros((np.size(objID_disturbances)))
            for i in range(np.size(objID_disturbances)):
                data = JEVis.dataprepControl(objID_disturbances[i], username, password, webservice)
                if data != []:
                    controlJevis.dist_vals[i] = data[0]
                else:
                    controlJevis.dist_vals[i] = 0
        else:
            data = JEVis.dataprepControl(objID_disturbances, username, password, webservice)
            controlJevis.dist_vals = data[0]

        if np.size(objID_energy) > 1:
            controlJevis.energie_vals = np.zeros((np.size(objID_energy)))
            for i in range(np.size(objID_energy)):
                data = JEVis.dataprepControl(objID_energy[i], username, password, webservice)
                if data != []:
                    controlJevis.energie_vals[i] = data[0]
                else:
                    controlJevis.energie_vals[i] = 0
        else:
            data = JEVis.dataprepControl(objID_energy[0], username, password, webservice)
            controlJevis.energie_vals = data[0]

        if np.size(objID_energy) > 1:
            controlJevis.energie_vals = np.zeros((np.size(objID_energy)))
            for i in range(np.size(objID_energy)):
                data = JEVis.dataprepControl(objID_energy[i], username, password, webservice)
                if data != []:
                    controlJevis.energie_vals[i] = data[0]
                else:
                    controlJevis.energie_vals[i] = 0
        else:
            data = JEVis.dataprepControl(objID_energy[0], username, password, webservice)
            controlJevis.energie_vals = data[0]

            #   if data != []:
            #    controlJevis.energie_vals[i] = data[0]
            #  else:
            #     controlJevis.energie_vals[i] = 0
        # else:
        #    data = JEVisDataprep_Control(objID_energy[0], username, password, webservice)
        #    controlJevis.energie_vals = data[0]

       # print("test")
        #for i in ids_setpoints:
            #data = \
                #JEVis.dataprepControl(i, username, password, webservice,datatype="text")
            #print(data)

        temperature = JEVis.dataprepControl(objID_temperature, username, password, webservice)
        controlJevis.temperature_vals = temperature[0]
        print(controlJevis)
        return controlJevis
    @staticmethod
    def dataprepControl(objID, username, password, webservice, datatype="value"):
        # Function to export the most recent Measurement of an Object vie ID
        # Create the URL with the needed Measurement
        sampleurl = webservice + '/objects/' + objID + '/attributes/Value/samples'
        sampleurl = sampleurl + '?' + 'onlyLatest=true'

        # Username & Password
        jevisUser = username
        jevisPW = password

        # Read JEVis data with URL, Username & Password
        get = requests.get(sampleurl, auth=HTTPBasicAuth(jevisUser, jevisPW))


        # print data
        # print("Get status: ", get)
        # print("Samples in JEVis: ", get.content)

        # put the read JEVis data to variable
        # print(get.text)
        if get.text == 'Object not found':
            print('ID ', objID, 'not found!')
            json_data = []
        else:
            json_data = json.loads(get.text)
        print(get.text)
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



class ControlJEVisObject:
    def __init__(self):
        self.heaters_vals = None
        self.dist_vals = None
        self.energie_vals = None
        self.temperature_vals = None
        self.weekend_operation = None
        self.setpoint = None

    def __str__(self):
        return "heaters_vals: %s, dist_vals: %s, energie_vals: %s,temperature_vals: %s,weekend_operation: %s" % (self.heaters_vals, self.dist_vals, self.energie_vals, self.temperature_vals, self.weekend_operation)
