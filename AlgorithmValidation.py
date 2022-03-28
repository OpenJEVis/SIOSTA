import ParamFUNKTIONS as p
import RegFUNKTIONS as r
import numpy as np
from datetime import date
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pickle

def ControlCheck(weekend_operation, heaterdata, modelfile, zonename, heaters_number, Temperature, OUTTemperature, Disturbances, Heater, Energies, Setpoint,weightening_ratio, calibration,fromDv,toDv,fromTv,toTv,jevisUser,jevisPW,webservice,horizon):
    #import model data:
    Params = r.load_model_with_calibration(modelfile, zonename)

    #run a algorithm simulation over all timeestamps:
    Heater_simulation = [''] * np.size(Temperature)
    Heater_sum = [''] * np.size(Temperature)
    Heater_simulation_sum = [''] * np.size(Temperature)
    Setpoint_trend = [''] * np.size(Temperature)

    # starting time:
    time = datetime.strptime(fromDv + fromTv, '%Y%m%d%H') - timedelta(hours=1)
    time_interval = timedelta(minutes=5)

    for i in range(np.size(Temperature)):
        Setpoints = r.Set_Setpoint(Setpoint[0], Setpoint[1], weekend_operation[i], time.strftime("%Y%m%d"),  time.strftime("%H:%M:%S"), horizon,
                                 time_interval=(datetime.strptime('00:00:00', '%H:%M:%S') + time_interval).strftime(
                                     "%H:%M:%S"))
        #print('Setpoints:', Setpoints)
        time = time + time_interval

        if calibration == 'true':
            Heater_simulation[i] = r.Control_with_calibration(heaterdata, Temperature[i], heaters_number, Disturbances[i], Energies[i],
                                             Setpoints,
                                             Params, [0, 0, 0],
                                             weightening_ratio,horizon)
        elif calibration == 'false':
            Heater_simulation[i] = r.Control(heaterdata, Temperature[i], heaters_number, Disturbances[i], Energies[i], Setpoints,
                                  Params, [0,0,0],
                                  weightening_ratio,horizon)
        else:
            print('ERROR: calibration-Variable can only be true or false!')
        for n in range(heaters_number):
            if n == 0:
                Heater_simulation_sum[i] = Heater_simulation[i][n]
            else:
                Heater_simulation_sum[i] = Heater_simulation_sum[i] + Heater_simulation[i][n]
        Heater_sum[i] = sum(Heater[i])
        Setpoint_trend[i] = Setpoints[0]
    return Heater_sum, Heater_simulation_sum, Setpoint_trend

def plot_ControlCheck(zonename, Temperature, Heater_sum, Heater_simulation_sum, Setpoint_trend):
    #Plot
    xvals = np.array(range(5, 5 * np.size(Temperature)+5, 5))/60
    fig, (ax0,ax1) = plt.subplots(2,1)
    ax0.plot(xvals,Temperature)
    ax0.plot(xvals, Setpoint_trend, color='black', linewidth=0.5)
    #ax0.ylabel('Temperatur [°C]')
    ax1.plot(xvals,Heater_sum)
    ax1.plot(xvals, Heater_simulation_sum)
    #ax1.ylabel('Kummulierte Stellsignale [-]')
    #ax1.xlabel('Zeit [min]')
    ax1.legend(['measured','simulated with control-algorithm'],loc='upper right')
    fig.suptitle(zonename)

    print('energy consumed by conservative control (measured): ', sum(Heater_sum),
          '\nenergy consumed by mpc (simulated): ', sum(Heater_simulation_sum))

def closedloop_simulation(weekend_operation, heaterdata, modelfile, zonename, heaters_number, Temperature, OUTTemperature, Disturbances, Heater, Energies, Setpoint,weightening_ratio, calibration,fromDv,toDv,fromTv,toTv,jevisUser,jevisPW,webservice,horizon):
    #import model data:
    if calibration == 'true':
        Params = r.load_model_with_calibration(modelfile, zonename)
    elif calibration == 'false':
        Params = r.load_model(modelfile, zonename)
    else:
        print('ERROR: calibration-Variable can only be true or false!')

    Estimated_temp = np.zeros(np.size(Temperature))
    Estimated_temp[0] = Temperature[0][0]

    #run a algorithm simulation over all timeestamps:
    Heater_simulation = np.zeros((np.size(Temperature),heaters_number))
    Heater_sum = [''] * np.size(Temperature)
    Heater_simulation_sum = [''] * np.size(Temperature)
    Setpoint_trend = [''] * np.size(Temperature)

    # starting time:
    time = datetime.strptime(fromDv + fromTv, '%Y%m%d%H') - timedelta(hours=1)
    time_interval = timedelta(minutes=5)
    Values_old = np.zeros((heaters_number))

    for i in range(np.size(Temperature)):
        Setpoints = r.Set_Setpoint(Setpoint[0], Setpoint[1], weekend_operation[i], time.strftime("%Y%m%d"), time.strftime("%H:%M:%S"),horizon,
                                 time_interval=(datetime.strptime('00:00:00','%H:%M:%S')+time_interval).strftime("%H:%M:%S"))
        #print('Setpoints:', Setpoints)
        time = time + time_interval
        if calibration == 'true':
            Values = r.Control_with_calibration(heaterdata, Estimated_temp[i], heaters_number, Disturbances[i], Energies[i],
                                             Setpoints,
                                             Params, [0, 0, 0],
                                             weightening_ratio, horizon)
        elif calibration == 'false':
            Values = r.Control(heaterdata, Estimated_temp[i], heaters_number, Disturbances[i], Energies[i], Setpoints,
                                  Params, [0,0,0],
                                  weightening_ratio,horizon)
        else:
            print('ERROR: calibration-Variable can only be true or false!')

        [fullload, heater] = r.Fullload_sep(heaterdata, Values, Values_old, heaters_number, [0,0,0])
        #print(heater, fullload)

        for n in range(heaters_number):
            if np.add(heater, np.multiply(fullload, heater))[n] == 2:
                Values[n] = heaterdata[0] * 2
            elif np.add(heater, np.multiply(fullload, heater))[n] == 1:
                Values[n] = heaterdata[1] * 2
            else:
                Values[n] = 0

            if Estimated_temp[i] < 13:
                if Values[n] < 2:
                    Values[n] = 2

        for n in range(heaters_number):
            Heater_simulation[i][n] = Values[n]
        #print(Heater_simulation[i])
        Heater_simulation_sum[i] = sum(Heater_simulation[i])
        Heater_sum[i] = sum(Heater[i])

        #Simulation of the model  reaction:
        if i < np.size(Temperature)-1:
            if calibration == 'true':
                Estimated_temp[i+1]=p.decvalidS_with_calibration(zonename, Heater_simulation[i], Estimated_temp[i], Disturbances[i], Energies[i],
                                                            Params)
            elif calibration == 'false':
                Estimated_temp[i+1]= p.decvalidS(zonename, Heater_simulation[i], Estimated_temp[i], Disturbances[i], Energies[i],
                                                              Params)
            else:
                print('ERROR: calibration-Variable can only be true or false!')

        Setpoint_trend[i] = Setpoints[0]
        Values_old = Values

    return Estimated_temp, Heater_sum, Heater_simulation_sum, Setpoint_trend

def DataDump_simulation(zonename, Temperature, Estimated_temp, Heater_sum,
                                            Heater_simulation_sum,
                                            Disturbances, Energies, Setpoint_trend, fromDv, toDv, fromT, toT):
    import json

    data = {'Temperature':Temperature.tolist(),
            'Estimated_temp':Estimated_temp.tolist(),
            'Setpoint_trend':Setpoint_trend,
            'Heater_sum':Heater_sum,
            'Heater_simulation_sum':Heater_simulation_sum,
            'Disturbances':Disturbances.tolist(),
            'Energies':Energies.tolist()}
    #print(data)

    filename = zonename + ' simulation ' + fromDv + '-' + fromT + '--' + toDv + '-' + toT + '.txt'

    file = open('DataDump/' + filename, 'w')
    data_string = json.dumps(data)
    file.write(data_string)
    file.close()

def DataLoad_simulation(zonename, fromDv, toDv, fromT, toT):
    import json

    filename = zonename + ' simulation ' + fromDv + '-' + fromT + '--' + toDv + '-' + toT + '.txt'
    file = open('DataDump/' + filename, 'r')
    content = file.read()
    file.close()
    data_dictionary = json.loads(content)
    Temperature = data_dictionary['Temperature']
    Estimated_temp = data_dictionary['Estimated_temp']
    Setpoint_trend = data_dictionary['Setpoint_trend']
    Heater_sum = data_dictionary['Heater_sum']
    Heater_simulation_sum = data_dictionary['Heater_simulation_sum']
    Disturbances = data_dictionary['Disturbances']
    Energies = data_dictionary['Energies']

    #print('Temperature',Temperature,'Estimated_temp',Estimated_temp,'Setpoint_trend',Setpoint_trend,'Heater_sum',Heater_sum,'Heater_simulation_sum',Heater_simulation_sum,'Disturbances',Disturbances,'Energies',Energies)
    return Temperature, Estimated_temp, Heater_sum, Heater_simulation_sum, Disturbances, Energies, Setpoint_trend

def plot_closeloop_simulation(zonename, fromDv, toDv, fromT, toT):
    [Temperature, Estimated_temp, Heater_sum,
     Heater_simulation_sum,
     Disturbances, Energies, Setpoint_trend] = DataLoad_simulation(zonename, fromDv, toDv, fromT, toT)
    #Plot
    xvals = np.array(range(5, 5 * np.size(Temperature)+5, 5))/60
    fig, (ax0,ax1,ax2,ax3) = plt.subplots(4,1, figsize=(8,8))
    ax0.plot(xvals, Temperature)
    ax0.set_ylim(13, 23)
    ax0.plot(xvals, Estimated_temp)
    ax0.plot(xvals, Setpoint_trend, color='black', linewidth=0.5)
    ax0.legend(['Messung', 'Simulation', 'Sollwert'], loc='upper right')
    ax0.set_ylabel('Temperatur [°C]')
    ax1.set_ylabel('Stellsignale [-]')
    ax1.plot(xvals,Heater_sum)
    ax1.plot(xvals, Heater_simulation_sum)

    ax1.legend(['Messung','Simulation'],loc='upper right')
    ax2.plot(xvals,Disturbances)
    ax2.set_ylabel('Störgrößen [°C / -]')
    ax2.legend(['Außen-Temperatur [°C]', 'Tor-Signal [0/1]', 'Tor-Signal [0/1]'], loc='upper right')
    ax3.plot(xvals,Energies)
    ax3.set_ylabel('Energieverbrauch\nProduktionsanlagen [-]')
    ax3.set_xlabel('Zeit [h]')
    fig.suptitle(zonename)

    print('energy consumed by conservative control (measured): ', sum(Heater_sum),
          '\nenergy consumed by mpc (simulated): ', sum(Heater_simulation_sum))

def DataDump_weightstudies(zonename, Temperature, Estimated_temp, Heater_sum, Heater_simulation_sum, Disturbances,
                          Energies, weightening_ratio_array, Setpoint_trend, fromDv, toDv, fromT, toT):
    import json
    if isinstance(Temperature, list) != 1:
        Temperature = Temperature.tolist()
    if isinstance(Estimated_temp, list) != 1:
        Estimated_temp = Estimated_temp.tolist()
    if isinstance(Heater_simulation_sum, list) != 1:
        Heater_simulation_sum = Heater_simulation_sum.tolist()
    if isinstance(Disturbances, list) != 1:
        Disturbances = Disturbances.tolist()
    if isinstance(Energies, list) != 1:
        Energies = Energies.tolist()

    data = {'Temperature': Temperature,
            'Estimated_temp': Estimated_temp,
            'Setpoint_trend': Setpoint_trend,
            'Heater_sum': Heater_sum,
            'Heater_simulation_sum': Heater_simulation_sum,
            'Disturbances': Disturbances,
            'Energies': Energies,
            'Weights': weightening_ratio_array}
    # print(data)

    filename = zonename + ' weightstudies ' + fromDv + '-' + fromT + '--' + toDv + '-' + toT + ': ' + str(weightening_ratio_array) +'.txt'

    file = open('DataDump/' + filename, 'w')
    data_string = json.dumps(data)
    file.write(data_string)
    file.close()

def DataLoad_weightstudies(zonename, weightening_ratio_array, fromDv, toDv, fromT, toT):
    import json

    filename = zonename + ' weightstudies ' + fromDv + '-' + fromT + '--' + toDv + '-' + toT + ': ' + str(weightening_ratio_array) +'.txt'
    file = open('DataDump/' + filename, 'r')
    content = file.read()
    file.close()
    data_dictionary = json.loads(content)
    Temperature = data_dictionary['Temperature']
    Estimated_temp = data_dictionary['Estimated_temp']
    Setpoint_trend = data_dictionary['Setpoint_trend']
    Heater_sum = data_dictionary['Heater_sum']
    Heater_simulation_sum = data_dictionary['Heater_simulation_sum']
    Disturbances = data_dictionary['Disturbances']
    Energies = data_dictionary['Energies']
    weightening_ratio_array = data_dictionary['Weights']

    # print('Temperature',Temperature,'Estimated_temp',Estimated_temp,'Setpoint_trend',Setpoint_trend,'Heater_sum',Heater_sum,'Heater_simulation_sum',Heater_simulation_sum,'Disturbances',Disturbances,'Energies',Energies)
    return [Temperature, Estimated_temp, Heater_sum, Heater_simulation_sum, Disturbances,
                          Energies, weightening_ratio_array, Setpoint_trend]

def DataDump_horizonstudies(zonename, Temperature, Estimated_temp, Heater_sum, Heater_simulation_sum, Disturbances,
                          Energies, horizon_array, Setpoint_trend, fromDv, toDv, fromT, toT):
    import json
    if isinstance(Temperature, list) != 1:
        Temperature = Temperature.tolist()
    if isinstance(Estimated_temp, list) != 1:
        Estimated_temp = Estimated_temp.tolist()
    if isinstance(Heater_simulation_sum, list) != 1:
        Heater_simulation_sum = Heater_simulation_sum.tolist()
    if isinstance(Disturbances, list) != 1:
        Disturbances = Disturbances.tolist()
    if isinstance(Energies, list) != 1:
        Energies = Energies.tolist()


    data = {'Temperature': Temperature,
            'Estimated_temp': Estimated_temp,
            'Setpoint_trend': Setpoint_trend,
            'Heater_sum': Heater_sum,
            'Heater_simulation_sum': Heater_simulation_sum,
            'Disturbances': Disturbances,
            'Energies': Energies,
            'Horizon': horizon_array}
    # print(data)

    filename = zonename + ' horizonstudies ' + fromDv + '-' + fromT + '--' + toDv + '-' + toT + ': ' + str(horizon_array) +'.txt'

    file = open('DataDump/' + filename, 'w')
    data_string = json.dumps(data)
    file.write(data_string)
    file.close()

def DataLoad_horizonstudies(zonename, horizon_array, fromDv, toDv, fromT, toT):
    import json

    filename = zonename + ' horizonstudies ' + fromDv + '-' + fromT + '--' + toDv + '-' + toT + ': ' + str(
        horizon_array) + '.txt'
    file = open('DataDump/' + filename, 'r')
    content = file.read()
    file.close()
    data_dictionary = json.loads(content)
    Temperature = data_dictionary['Temperature']
    Estimated_temp = data_dictionary['Estimated_temp']
    Setpoint_trend = data_dictionary['Setpoint_trend']
    Heater_sum = data_dictionary['Heater_sum']
    Heater_simulation_sum = data_dictionary['Heater_simulation_sum']
    Disturbances = data_dictionary['Disturbances']
    Energies = data_dictionary['Energies']
    horizon_array = data_dictionary['Horizon']

    # print('Temperature',Temperature,'Estimated_temp',Estimated_temp,'Setpoint_trend',Setpoint_trend,'Heater_sum',Heater_sum,'Heater_simulation_sum',Heater_simulation_sum,'Disturbances',Disturbances,'Energies',Energies)
    return [Temperature, Estimated_temp, Heater_sum, Heater_simulation_sum, Disturbances,
            Energies, horizon_array, Setpoint_trend]

def plot_Parameterstudies(zonename, Temperature, Estimated_temp, Heater_sum, Heater_simulation_sum, Disturbances, Energies, Parameter_array, Setpoint_trend):
    # Plot
    xvals = np.array(range(5, 5 * np.size(Temperature)+5, 5))/60
    fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(8,6))
    ax0.plot(xvals, Temperature)
    ax0.set_ylim(13, 25)
    ax1.plot(xvals, Heater_sum)
    legend_array = ['Messung']
    for i in range(np.size(Parameter_array)):
        ax0.plot(xvals, Estimated_temp[i])
        ax1.plot(xvals, Heater_simulation_sum[i])
        legend_array.append('Simulation: ' + str(Parameter_array[i]))
    legend_array.append('Setpoints')
    ax0.plot(xvals, Setpoint_trend, color='black', linewidth=0.5)
    ax0.legend(legend_array, loc='upper right')
    ax0.set_ylabel('Temperatur [°C]')
    ax1.set_ylabel('Stellsignale [-]')
    # ax1.set_xlabel('Zeit [min]')
    ax1.legend(legend_array, loc='upper right')
    ax1.set_xlabel('Zeit [h]')
    # energy = np.zeros(np.size(Parameter_array)+1)
    # energy[0] = sum(Heater_sum)
    # for i in range(np.size(Parameter_array)):
    #     energy[i+1] = sum(Heater_simulation_sum[i])
    # x = 0.5 + np.arange(np.size(Parameter_array)+1)
    # rects = ax2.bar(x, energy, tick_label = legend_array[0:np.size(Parameter_array)+1])
    # ax2.set_ylabel('Summe der\nStellsignale [-]')
    # #ax2.set_xticks(x, tick_label = legend_array)
    # ax2.bar_label(rects, label_type='edge')
    fig.suptitle(zonename)

    #pickle.dump(fig, open(zonename + ' Parameterstudies' + '.fig.pickle', 'wb'))

def plot_comparison(zonename, Temperature, Estimated_temp, Heater_sum, Heater_simulation_sum, Disturbances, Energies, weight_array, horizon_array, Setpoint_trend):
    xvals = np.array(range(5, 5 * np.size(Temperature)+5, 5))/60
    fig, (ax0, ax1, ax2) = plt.subplots(3, 1, figsize=(8, 6))
    ax0.plot(xvals, Temperature)
    ax1.plot(xvals, Heater_sum)
    legend_array = ['measured']
    for i in range(np.size(weight_array)):
        ax0.plot(xvals, Estimated_temp[i])
        ax1.plot(xvals, Heater_simulation_sum[i])
        legend_array.append('weight=' + str(weight_array[i]) + ', horizon=' + str(horizon_array[i]))
    legend_array.append('Setpoints')
    ax0.plot(xvals, Setpoint_trend, color='black', linewidth=0.5)
    ax0.legend(legend_array, loc='upper right')
    ax0.set_ylabel('Temperatur [°C]')
    ax1.set_ylabel('Stellsignale [-]')
    # ax1.set_xlabel('Zeit [min]')
    ax1.legend(legend_array, loc='upper right')
    energy = np.zeros(np.size(weight_array) + 1)
    energy[0] = sum(Heater_sum)
    for i in range(np.size(weight_array)):
        energy[i + 1] = sum(Heater_simulation_sum[i])
    x = 0.5 + np.arange(np.size(weight_array) + 1)
    rects = ax2.bar(x, energy, tick_label=legend_array[0:np.size(weight_array) + 1])
    ax2.set_ylabel('Summe der\nStellsignale [-]')
    # ax2.set_xticks(x, tick_label = legend_array)
    ax2.bar_label(rects, label_type='edge')
    fig.suptitle(zonename)

def import_measurement(systemname,weekend_operation,Temperature, OUTTemperature, Disturbances, Heater, Energies, Setpoint, fromDv, toDv, fromT, toT, calibration='true'):
    horizon = 6
    Heater_sum = [''] * np.size(Temperature)
    Setpoint_trend = [''] * np.size(Temperature)

    time = datetime.strptime(fromDv + fromT, '%Y%m%d%H') - timedelta(hours=1)
    time_interval = timedelta(minutes=5)

    for i in range(np.size(Temperature)):
        time = time + time_interval
        Setpoints = r.Set_Setpoint(Setpoint[0], Setpoint[1],weekend_operation[i], time.strftime("%Y%m%d"), time.strftime("%H:%M:%S"),
                                   horizon,
                                   time_interval=(datetime.strptime('00:00:00', '%H:%M:%S') + time_interval).strftime(
                                       "%H:%M:%S"))
        Setpoint_trend[i] = Setpoints[0]
        Heater_sum[i] = sum(Heater[i])
    return [Temperature, Setpoint_trend, Heater, Heater_sum, Disturbances, Energies]

def DataDump_Measurement(zonename, Temperature, Setpoint_trend, Heater, Heater_sum, Disturbances, Energies, fromDv,
                         toDv, fromT, toT):
    import json

    data = {'Temperature': Temperature.tolist(),
            'Setpoint_trend': Setpoint_trend,
            'Heater': Heater.tolist(),
            'Heater_sum': Heater_sum,
            'Disturbances': Disturbances.tolist(),
            'Energies': Energies.tolist()}
    # print(data)

    filename = zonename + ' measurement ' + fromDv + '-' + fromT + '--' + toDv + '-' + toT + '.txt'

    file = open('DataDump/' + filename, 'w')
    data_string = json.dumps(data)
    file.write(data_string)
    file.close()

def DataLoad_measurement(zonename, fromDv, toDv, fromT, toT):
    import json

    filename = zonename + ' measurement ' + fromDv + '-' + fromT + '--' + toDv + '-' + toT + '.txt'
    file = open('DataDump/' + filename, 'r')
    content = file.read()
    file.close()
    data_dictionary = json.loads(content)
    Temperature = data_dictionary['Temperature']
    Setpoint_trend = data_dictionary['Setpoint_trend']
    Heater = data_dictionary['Heater']
    Heater_sum = data_dictionary['Heater_sum']
    Disturbances = data_dictionary['Disturbances']
    Energies = data_dictionary['Energies']

    #print('Temperature',Temperature,'Estimated_temp',Estimated_temp,'Setpoint_trend',Setpoint_trend,'Heater_sum',Heater_sum,'Heater_simulation_sum',Heater_simulation_sum,'Disturbances',Disturbances,'Energies',Energies)
    return [Temperature,  Heater, Heater_sum, Disturbances, Energies, Setpoint_trend]

def plot_measurement(systemname,fromDv, toDv, fromT, toT):
    [Temperature,  Heater, Heater_sum, Disturbances, Energies, Setpoint_trend] = DataLoad_measurement(systemname, fromDv, toDv, fromT, toT)

    xvals = np.array(range(5, 5 * np.size(Temperature)+5, 5))/60
    #labelticks = str(np.array(range(int(fromT), int(fromT) + 5 * np.size(Temperature), 60)))

    fig, (ax0, ax1, ax2, ax3) = plt.subplots(4, 1, figsize=(8, 8))
    ax0.plot(xvals, Temperature)
    ax0.plot(xvals, Setpoint_trend, color='black', linewidth=0.5)
    ax0.set_ylabel('Temperatur [°C]')
    ax0.set_ylim(13, 23)
    #ax0.set_xticks(np.array(range(0, 5 * np.size(Temperature), 60))) #, labels=labelticks)
    ax1.set_ylabel('Stellsignale [-]')

    ax1.stackplot(xvals, np.transpose(Heater))
    # ax1.plot(xvals, Heater_sum)

    ax2.plot(xvals, Disturbances)
    ax2.set_ylabel('Störgrößen [°C / -]')
    ax2.legend(['Außen-Temperatur [°C]', 'Tor-Signal [0/1]', 'Tor-Signal [0/1]'], loc='upper right')
    ax2.set_ylim(-10, 20)
    ax3.plot(xvals, Energies)
    ax3.set_ylabel('Energieverbrauch\nProduktionsanlagen [-]')
    ax3.set_xlabel('Zeit [h]')
    fig.suptitle(systemname)

    return [Temperature, Setpoint_trend, Heater, Heater_sum, Disturbances, Energies]

def threshold(Temperature, Setpoint_trend, Heater, Heater_sum, Disturbances, Energies):
    import pandas as pd
    #datalist = list([Temperature, Setpoint_trend, Heater_sum])
    #names = ['Temperature', 'Setpoint', 'U']

    Temperature_array = np.zeros(len(Setpoint_trend))
    for i in range(len(Setpoint_trend)):
        Temperature_array[i] = Temperature[i]

    data = pd.DataFrame({'Temperature': Temperature_array,
                        'Setpoint':Setpoint_trend,
                        'U':Heater_sum})

    data['Threshold'] = data['Setpoint']-data['Temperature']

    print(data)

    data.sort_values('Threshold', ascending=True)

    plt.scatter(data['Threshold'], data['U'])
    #plt.plot(data['Setpoint'])

def plot_comparison_measurements(systemname, Testzeitraum_0, Testzeitraum_1, Vergleichszeitraum_0, Vergleichszeitraum_1):
    [Temperature_test, Heater_test, Heater_sum_test, Disturbances_test, Energies_test, Setpoint_trend_test] = DataLoad_measurement(systemname, Testzeitraum_0, Testzeitraum_1, '00', '00')
    [Temperature_Vergleich, Heater_Vergleich, Heater_sum_Vergleich, Disturbances_Vergleich, Energies_Vergleich, Setpoint_trend_Vergleich] = DataLoad_measurement(systemname, Vergleichszeitraum_0, Vergleichszeitraum_1, '00', '00')

    xvals = np.array(range(5, 5 * np.size(Temperature_test) + 5, 5)) / 60

    fig, axs = plt.subplots(4, 2, figsize=(8, 8))

    axs[0, 0].plot(xvals, Temperature_test)
    axs[0, 0].plot(xvals, Setpoint_trend_test, color='black', linewidth=0.5)
    axs[0, 0].set_ylabel('Temperatur [°C]')
    axs[0, 0].set_ylim(13, 23)
    axs[0, 0].set(title='Referenz')

    axs[0, 1].plot(xvals, Temperature_Vergleich)
    axs[0, 1].plot(xvals, Setpoint_trend_Vergleich, color='black', linewidth=0.5)
    #ax1.set_ylabel('Temperatur [°C]')
    axs[0, 1].set_ylim(13, 23)
    axs[0, 1].set(title='Test')

    #ax0.set_xticks(np.array(range(0, 5 * np.size(Temperature), 60))) #, labels=labelticks)
    axs[1, 0].set_ylabel('Stellsignale [-]')
    axs[1, 0].stackplot(xvals, np.transpose(Heater_test))

    #ax3.set_ylabel('Stellsignale [-]')
    axs[1, 1].stackplot(xvals, np.transpose(Heater_Vergleich))

    # ax1.plot(xvals, Heater_sum)

    axs[2, 0].plot(xvals, Disturbances_test)
    axs[2, 0].set_ylabel('Störgrößen [°C / -]')
    axs[2, 0].legend(['Außen-Temperatur [°C]', 'Tor-Signal [0/1]', 'Tor-Signal [0/1]'], loc='upper right')
    axs[2, 0].set_ylim(-10, 20)

    axs[2, 1].plot(xvals, Disturbances_Vergleich)
    #axs[2, 1].set_ylabel('Störgrößen [°C / -]')
    axs[2, 1].legend(['Außen-Temperatur [°C]', 'Tor-Signal [0/1]', 'Tor-Signal [0/1]'], loc='upper right')
    axs[2, 1].set_ylim(-10, 20)

    axs[3, 0].plot(xvals, Energies_test)
    axs[3, 0].set_ylabel('Energieverbrauch\nProduktionsanlagen [-]')
    axs[3, 0].set_xlabel('Zeit [h]')

    axs[3, 1].plot(xvals, Energies_Vergleich)
    #axs[3, 1].set_ylabel('Energieverbrauch\nProduktionsanlagen [-]')
    axs[3, 1].set_xlabel('Zeit [h]')

    fig.suptitle(systemname)