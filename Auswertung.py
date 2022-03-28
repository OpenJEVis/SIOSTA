
import ParamFUNKTIONS as p
import RegFUNKTIONS as r
import AlgorithmValidation as a
import total as t
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def Controlvalidation(systemname,configurationfile,weightening_ratio,fromDv,toDv,fromT,toT,horizon=5,calibration='true'):
    [ObjectIDs, horizon_config, weightfactor_config, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = t.configuration_loader(configurationfile)
    #print(Setpoints)
    if systemname == 'all':
        # Plotting of all zones i
        i = 0
        for j in range(np.size(systems)):
            # Iteration through all halls j
            for n in range(np.size(systems[j])):
                # Iteration through the zones n of hall j
                [Temperature, OUTTemperature, Disturbances, Heater, Energies, weekend_operation] = p.totalprep(ObjectIDs[7][i],heaterdata, ObjectIDs[0][i],
                                                                                            np.size(ObjectIDs[0][i]),
                                                                                            ObjectIDs[2][i],
                                                                                            ObjectIDs[1][i],
                                                                                            ObjectIDs[3][j],
                                                                                            ObjectIDs[4][i],
                                                                                            fromDv, toDv,
                                                                                            fromT, toT, jevisUser,
                                                                                            jevisPW,
                                                                                            webservice)
                [Heater_sum, Heater_simulation_sum, Setpoint_trend] = a.ControlCheck(weekend_operation,heaterdata, modelfile, zonenames[i], np.size(ObjectIDs[0][i]),
                                                                     Temperature, OUTTemperature, Disturbances, Heater,
                                                                     Energies, Setpoints[i], weightening_ratio,
                                                                     calibration, fromDv, toDv, fromT,
                                                                     toT, jevisUser, jevisPW, webservice, horizon)
                a.plot_ControlCheck(zonenames[i], Temperature, Heater_sum, Heater_simulation_sum, Setpoint_trend)
                i = i + 1
    else:
        i = zonenames.index(systemname)
        for list in systems:
            for element in list:
                if element == systemname:
                    j = systems.index(list)
        [Temperature, OUTTemperature, Disturbances, Heater, Energies, weekend_operation] = p.totalprep(ObjectIDs[7][i],heaterdata, ObjectIDs[0][i],
                                                                                    np.size(ObjectIDs[0][i]),
                                                                                    ObjectIDs[2][i],
                                                                                    ObjectIDs[1][i],
                                                                                    ObjectIDs[3][j], ObjectIDs[4][i],
                                                                                    fromDv, toDv,
                                                                                    fromT, toT, jevisUser,
                                                                                    jevisPW,
                                                                                    webservice)
        [Heater_sum, Heater_simulation_sum, Setpoint_trend] = a.ControlCheck(weekend_operation,heaterdata, modelfile,zonenames[i], np.size(ObjectIDs[0][i]), Temperature, OUTTemperature, Disturbances, Heater,
                       Energies, Setpoints[i], weightening_ratio, calibration, fromDv, toDv,fromT,toT, jevisUser, jevisPW, webservice,horizon)
        a.plot_ControlCheck(zonenames[i], Temperature, Heater_sum, Heater_simulation_sum, Setpoint_trend)

def ClosedLoopValidation(systemname,configurationfile,weightening_ratio,fromDv,toDv,fromT,toT,horizon=5,calibration='true'):
    [ObjectIDs, horizon_config, weightfactor_config, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = t.configuration_loader(configurationfile)

    if systemname == 'all':
        # Plotting of all zones i
        i = 0
        for j in range(np.size(systems)):
            # Iteration through all halls j
            for n in range(np.size(systems[j])):
                # Iteration through the zones n of hall j
                [Temperature, OUTTemperature, Disturbances, Heater, Energies, weekend_operation] = p.totalprep(ObjectIDs[7][i],heaterdata, ObjectIDs[0][i], np.size(ObjectIDs[0][i]),
                                                                                            ObjectIDs[2][i],
                                                                                            ObjectIDs[1][i],
                                                                                            ObjectIDs[3][j], ObjectIDs[4][i],
                                                                                            fromDv, toDv,
                                                                                            fromT, toT, jevisUser,
                                                                                            jevisPW,
                                                                                            webservice)
                [Estimated_temp, Heater_sum, Heater_simulation_sum, Setpoint_trend] = a.closedloop_simulation(weekend_operation,heaterdata, modelfile, zonenames[i],
                                                                                              np.size(ObjectIDs[0][i]),
                                                                                              Temperature,
                                                                                              OUTTemperature,
                                                                                              Disturbances, Heater,
                                                                                              Energies, Setpoints[i],
                                                                                              weightening_ratio,
                                                                                               calibration,
                                                                                              fromDv, toDv, fromT, toT,
                                                                                              jevisUser, jevisPW,
                                                                                              webservice, horizon)
                a.DataDump_simulation(zonenames[i], Temperature, Estimated_temp, Heater_sum,
                                            Heater_simulation_sum,
                                            Disturbances, Energies, Setpoint_trend, fromDv, toDv, fromT, toT)

                a.plot_closeloop_simulation(zonenames[i], fromDv, toDv, fromT, toT)

                i = i + 1
    else:
        i = zonenames.index(systemname)
        for list in systems:
            for element in list:
                if element == systemname:
                    j = systems.index(list)
        [Temperature, OUTTemperature, Disturbances, Heater, Energies, weekend_operation] = p.totalprep(ObjectIDs[7][i],heaterdata, ObjectIDs[0][i],
                                                                                    np.size(ObjectIDs[0][i]),
                                                                                    ObjectIDs[2][i],
                                                                                    ObjectIDs[1][i],
                                                                                    ObjectIDs[3][j], ObjectIDs[4][i],
                                                                                    fromDv, toDv,
                                                                                    fromT, toT, jevisUser,
                                                                                    jevisPW,
                                                                                    webservice)
        [Estimated_temp, Heater_sum, Heater_simulation_sum, Setpoint_trend] = a.closedloop_simulation(weekend_operation,heaterdata, modelfile,zonenames[i], np.size(ObjectIDs[0][i]), Temperature, OUTTemperature, Disturbances, Heater,
                       Energies, Setpoints[i], weightening_ratio, calibration, fromDv, toDv,fromT,toT, jevisUser, jevisPW, webservice,horizon)
        a.DataDump_simulation(zonenames[i], Temperature, Estimated_temp, Heater_sum,
                              Heater_simulation_sum,
                              Disturbances, Energies, Setpoint_trend, fromDv, toDv, fromT, toT)
        a.plot_closeloop_simulation(zonenames[i], fromDv, toDv, fromT, toT)

def MPC_Parameterstudies(systemname, configurationfile, fromDv, toDv, fromT, toT, weightening_ratio_array, horizon_for_weightvariation, horizon_array, weight_for_weihtvariation, calibration='true'):
    [ObjectIDs, horizon_config, weightfactor_config, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = t.configuration_loader(configurationfile)
    i = zonenames.index(systemname)
    for list in systems:
        for element in list:
            if element == systemname:
                j = systems.index(list)
    [Temperature, OUTTemperature, Disturbances, Heater, Energies, weekend_operation] = p.totalprep(ObjectIDs[7][i],heaterdata, ObjectIDs[0][i],
                                                                                np.size(ObjectIDs[0][i]),
                                                                                ObjectIDs[2][i],
                                                                                ObjectIDs[1][i],
                                                                                ObjectIDs[3][j], ObjectIDs[4][i],
                                                                                fromDv, toDv,
                                                                                fromT, toT, jevisUser,
                                                                                jevisPW,
                                                                                webservice)
    j = 0
    weightening_ratio_array = weightening_ratio_array
    Estimated_temp = np.zeros([np.size(weightening_ratio_array), np.size(Temperature)])
    Heater_simulation_sum = np.zeros([np.size(weightening_ratio_array), np.size(Temperature)])
    for w in weightening_ratio_array:
        horizon = horizon_for_weightvariation
        weightening_ratio = w
        [Estimated_temp[j], Heater_sum, Heater_simulation_sum[j], Setpoint_trend] = a.closedloop_simulation(weekend_operation,heaterdata, modelfile, zonenames[i],
                                                                                      np.size(ObjectIDs[0][i]),
                                                                                      Temperature, OUTTemperature,
                                                                                      Disturbances, Heater,
                                                                                      Energies, Setpoints[i],
                                                                                      weightening_ratio,
                                                                                      calibration, fromDv, toDv, fromT,
                                                                                      toT, jevisUser, jevisPW,
                                                                                      webservice, horizon)
        j = j + 1
    a.DataDump_weightstudies(zonenames[i], Temperature, Estimated_temp, Heater_sum, Heater_simulation_sum, Disturbances,
                          Energies, weightening_ratio_array, Setpoint_trend, fromDv, toDv, fromT, toT)
    [Temperature, Estimated_temp, Heater_sum, Heater_simulation_sum, Disturbances,
     Energies, weightening_ratio_array, Setpoint_trend] = a.DataLoad_weightstudies(zonenames[i], weightening_ratio_array, fromDv, toDv,
                                                                          fromT, toT)
    a.plot_Parameterstudies(zonenames[i], Temperature, Estimated_temp, Heater_sum, Heater_simulation_sum, Disturbances,
                          Energies, weightening_ratio_array, Setpoint_trend)
    j = 0
    horizon_array = horizon_array
    Estimated_temp = np.zeros([np.size(horizon_array), np.size(Temperature)])
    Heater_simulation_sum = np.zeros([np.size(horizon_array), np.size(Temperature)])
    for h in horizon_array:
        weightening_ratio = weight_for_weihtvariation
        horizon = h
        #print(np.size(Temperature))
        #print(Temperature)
        [Estimated_temp[j], Heater_sum, Heater_simulation_sum[j], Setpoint_trend] = a.closedloop_simulation(weekend_operation,heaterdata, modelfile, zonenames[i],
                                                                                      np.size(ObjectIDs[0][i]),
                                                                                      Temperature, OUTTemperature,
                                                                                      Disturbances, Heater,
                                                                                      Energies, Setpoints[i],
                                                                                      weightening_ratio,
                                                                                      calibration, fromDv, toDv, fromT,
                                                                                      toT, jevisUser, jevisPW,
                                                                                      webservice, horizon)
        j = j + 1
    a.DataDump_horizonstudies(zonenames[i], Temperature, Estimated_temp, Heater_sum, Heater_simulation_sum, Disturbances,
                             Energies, horizon_array, Setpoint_trend, fromDv, toDv, fromT, toT)
    [Temperature, Estimated_temp, Heater_sum, Heater_simulation_sum, Disturbances,
            Energies, horizon_array, Setpoint_trend] = a.DataLoad_horizonstudies(zonenames[i], horizon_array, fromDv, toDv, fromT, toT)
    a.plot_Parameterstudies(zonenames[i], Temperature, Estimated_temp, Heater_sum, Heater_simulation_sum, Disturbances,
                            Energies, horizon_array, Setpoint_trend)

def Parameter_csv(systemname, configurationfile, fromDv, toDv, fromT, toT, calibration='true'):

    N = [3, 6, 9, 12, 18, 24, 36, 48]
    Q = np.vstack([1, 2, 3, 5, 7, 10, 20, 30, 50, 70, 100])

    n1 = np.vstack(np.ones(np.size(Q)))
    n2 = np.ones(np.size(N))

    N = n1 * N
    Q = Q * n2

    setpoint_error = n1 * n2
    energie = n1 * n2
    setpoint_error_heating_time = np.zeros([np.size(setpoint_error,0), np.size(setpoint_error,1)])

    [ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = t.configuration_loader(configurationfile)
    i = zonenames.index(systemname)
    for list in systems:
        for element in list:
            if element == systemname:
                j = systems.index(list)
    [Temperature, OUTTemperature, Disturbances, Heater, Energies, weekend_operation] = p.totalprep(ObjectIDs[7][i],heaterdata, ObjectIDs[0][i],
                                                                                np.size(ObjectIDs[0][i]),
                                                                                ObjectIDs[2][i],
                                                                                ObjectIDs[1][i],
                                                                                ObjectIDs[3][j], ObjectIDs[4][i],
                                                                                fromDv, toDv,
                                                                                fromT, toT, jevisUser,
                                                                                jevisPW,
                                                                                webservice)
    for n1 in range(np.size(N,0)):
        for n2 in range(np.size(N,1)):
            horizon = int(N[n1, n2])
            weightening_ratio = Q[n1, n2]

            [Estimated_temp, Heater_sum, Heater_simulation_sum, Setpoint_trend] = a.closedloop_simulation(weekend_operation,
                heaterdata, modelfile, zonenames[i],
                np.size(ObjectIDs[0][i]),
                Temperature, OUTTemperature,
                Disturbances, Heater,
                Energies, Setpoints[i],
                weightening_ratio,
                calibration, fromDv, toDv, fromT,
                toT, jevisUser, jevisPW,
                webservice, horizon)

            setpoint_error[n1, n2] = sum(np.absolute(Estimated_temp - Setpoint_trend))
            energie[n1, n2] = sum(Heater_simulation_sum)
            for k in range(np.size(Setpoint_trend)):
                if Setpoint_trend[k]>16:
                    setpoint_error_heating_time[n1, n2] = setpoint_error_heating_time[n1, n2] + np.absolute(Estimated_temp[k] - Setpoint_trend[k])

    np.savetxt("horizon.csv", N, delimiter=",")
    np.savetxt("Weight.csv", Q, delimiter=",")
    np.savetxt("setpoint_error.csv", setpoint_error, delimiter=",")
    np.savetxt("setpoint_error_heating_time.csv", setpoint_error_heating_time, delimiter=",")
    np.savetxt("energie.csv", energie, delimiter=",")

def Parameter_Contour_Plot():
    N = np.genfromtxt('horizon.csv', delimiter=',')
    Q = np.genfromtxt('Weight.csv', delimiter=',')
    setpoint_error = np.genfromtxt('setpoint_error.csv', delimiter=',')
    setpoint_error_heating_time = np.genfromtxt('setpoint_error_heating_time.csv', delimiter=',')
    energie = np.genfromtxt('energie.csv', delimiter=',')

    Points = [[6, 12, 24, 24, 24, 24, 24, 48], [25, 25, 3, 5, 10, 25, 100, 25]]
    Points2 = [[12, 42], [50, 5]]

    fig0 = plt.contourf(N, Q, setpoint_error, 20)
    plt.yscale('log')
    plt.colorbar()
    plt.ylabel('weightening ratio [-]')
    plt.xlabel('horizon [-]')
    plt.title('sum of abs. setpoint error')
    plt.scatter(Points[0], Points[1], marker='x', c='red')
    plt.scatter(Points2[0], Points2[1], marker='s', c='black')
    #plt.scatter([24], [5], marker='o', c='red')

    fig1 = plt.figure()
    fig1 = plt.contourf(N, Q, energie, 20)
    plt.yscale('log')
    plt.colorbar()
    plt.ylabel('weightening ratio [-]')
    plt.xlabel('horizon [-]')
    plt.title('sum of heater signals')
    plt.scatter(Points[0], Points[1], marker='x', c='red')
    plt.scatter(Points2[0], Points2[1], marker='s', c='black')
    #plt.scatter([24], [5], marker='o', c='red')

    fig2 = plt.figure()
    fig2 = plt.contourf(N, Q, setpoint_error_heating_time, 20)
    plt.yscale('log')
    plt.colorbar()
    plt.ylabel('weightening ratio [-]')
    plt.xlabel('horizon [-]')
    plt.title('sum of abs. setpoint error\nduring heating period (5:00 to 18:00)')
    plt.scatter(Points[0], Points[1], marker='x', c='red')
    plt.scatter(Points2[0], Points2[1], marker='s', c='black')
    #plt.scatter([24], [5], marker='o', c='red')

    # fig, (ax0,ax1) = plt.subplots(1, 2) #, sharex=True, sharey=True)
    # cs0 = ax0.contourf(N, Q, setpoint_error, 20)
    # cbar0 = fig.colorbar(cs0)
    #
    # cs1 = ax1.contourf(N, Q, energie, 20)
    # cbar1 = fig.colorbar(cs1)
    #
    # #ax0.clabel(cs0)
    # #ax1.clabel(cs1)
    # ax0.set_title('sum of abs. setpoint error')
    # ax0.set_yscale('log')
    #
    # ax1.set_title('sum of heater signals')
    # ax1.set_yscale('log')
    # #plt.ylabel('weightening ratio [-]')
    # #plt.xlabel('horizon [-]')

def Parameter_Contour(systemname, configurationfile, fromDv, toDv, fromT, toT, calibration='true'):

    Parameter_csv(systemname, configurationfile, fromDv, toDv, fromT, toT, calibration)
    Parameter_Contour_Plot()

def Comparison_of_multiple(systemname, configurationfile, fromDv, toDv, fromT, toT, weight_array, horizon_array, calibration='true'):
    if len(weight_array) != len(horizon_array):
        print('ERROR: weight-array and horizon-array need to be the same size!')

    else:
        [ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = t.configuration_loader(configurationfile)
        i = zonenames.index(systemname)
        for list in systems:
            for element in list:
                if element == systemname:
                    j = systems.index(list)
        [Temperature, OUTTemperature, Disturbances, Heater, Energies, weekend_operation] = p.totalprep(ObjectIDs[7][i],heaterdata, ObjectIDs[0][i],
                                                                                np.size(ObjectIDs[0][i]),
                                                                                ObjectIDs[2][i],
                                                                                ObjectIDs[1][i],
                                                                                ObjectIDs[3][j], ObjectIDs[4][i],
                                                                                fromDv, toDv,
                                                                                fromT, toT, jevisUser,
                                                                                jevisPW,
                                                                                webservice)

        Estimated_temp = np.zeros([np.size(weight_array), np.size(Temperature)])
        Heater_simulation_sum = np.zeros([np.size(weight_array), np.size(Temperature)])
        for n in range(len(weight_array)):
            [Estimated_temp[n], Heater_sum, Heater_simulation_sum[n], Setpoint_trend] = a.closedloop_simulation(weekend_operation,
                heaterdata, modelfile, zonenames[i],
                np.size(ObjectIDs[0][i]),
                Temperature, OUTTemperature,
                Disturbances, Heater,
                Energies, Setpoints[i],
                weight_array[n],
                calibration, fromDv, toDv, fromT,
                toT, jevisUser, jevisPW,
                webservice, horizon_array[n])

        a.plot_comparison(zonenames[i], Temperature, Estimated_temp, Heater_sum, Heater_simulation_sum,
                                Disturbances,
                                Energies, weight_array, horizon_array, Setpoint_trend)



def plot_Measurement(systemname, configurationfile, fromDv, toDv, fromT, toT, calibration='true'):
    [ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = t.configuration_loader(configurationfile)

    if systemname == 'all':
        # Plotting of all zones i
        i = 0
        for j in range(np.size(systems)):
            # Iteration through all halls/systems j
            for n in range(np.size(systems[j])):
            # Iteration through the zones n of hall/system j
                [Temperature, OUTTemperature, Disturbances, Heater, Energies, weekend_operation] = p.totalprep(ObjectIDs[7][i],heaterdata, ObjectIDs[0][i],
                                                                                        np.size(ObjectIDs[0][i]),
                                                                                        ObjectIDs[2][i],
                                                                                        ObjectIDs[1][i],
                                                                                        ObjectIDs[3][j],
                                                                                        ObjectIDs[4][i],
                                                                                        fromDv, toDv,
                                                                                        fromT, toT, jevisUser,
                                                                                        jevisPW,
                                                                                        webservice)

                [Temperature, Setpoint_trend, Heater, Heater_sum, Disturbances, Energies] = a.import_measurement(zonenames[i],weekend_operation,
                Temperature, OUTTemperature, Disturbances, Heater, Energies, Setpoints[i], fromDv, toDv, fromT, toT,
                calibration='true')

                a.DataDump_Measurement(zonenames[i], Temperature, Setpoint_trend, Heater, Heater_sum, Disturbances, Energies,fromDv,toDv, fromT, toT)

                a.plot_measurement(zonenames[i],fromDv,toDv, fromT, toT)
                i=i+1

    elif systemname in systemnames:
        # Modelidentifiction for one system (e.g. Hall 1 and 3 (LF))
        # create index array for the zone according their position in the configuration-arrays
        index = systems
        i = 0
        for j in range(np.size(systems)):
            for n in range(np.size(systems[j])):
                index[j][n] = i
                i = i + 1
        j = systemnames.index(systemname)
        for n in range(len(systems[j])):
            [Temperature, OUTTemperature, Disturbances, Heater, Energies, weekend_operation] = p.totalprep(ObjectIDs[7][index[j][n]],heaterdata, ObjectIDs[0][index[j][n]],
                                                                                        np.size(ObjectIDs[0][index[j][n]]),
                                                                                        ObjectIDs[2][index[j][n]],
                                                                                        ObjectIDs[1][index[j][n]],
                                                                                        ObjectIDs[3][j],
                                                                                        ObjectIDs[4][index[j][n]],
                                                                                        fromDv, toDv,
                                                                                        fromT, toT, jevisUser,
                                                                                        jevisPW,
                                                                                        webservice)
            print('temp:', Temperature, '\nHeater:', Heater, '\nDisturbances:', Disturbances, '\nEnergie:', Energies)

            [Temperature, Setpoint_trend, Heater, Heater_sum, Disturbances, Energies] = a.import_measurement(zonenames[index[j][n]],weekend_operation,
                Temperature, OUTTemperature, Disturbances, Heater, Energies, Setpoints[index[j][n]], fromDv, toDv, fromT, toT,
                calibration='true')

            #print('temp:', Temperature, '\nSetpoint:', Setpoint_trend, '\nHeater:', Heater, '\nHeater sum:', Heater_sum, '\nDisturbances:', Disturbances, '\nEnergie:', Energies)
            a.DataDump_Measurement(zonenames[index[j][n]], Temperature, Setpoint_trend, Heater, Heater_sum, Disturbances,
                                   Energies, fromDv, toDv, fromT, toT)

            a.plot_measurement(zonenames[index[j][n]], fromDv, toDv, fromT, toT)
    else:
        i = zonenames.index(systemname)
        for list in systems:
            for element in list:
                if element == systemname:
                    j = systems.index(list)
        [Temperature, OUTTemperature, Disturbances, Heater, Energies, weekend_operation] = p.totalprep(ObjectIDs[7][i],heaterdata, ObjectIDs[0][i],
                                                                                np.size(ObjectIDs[0][i]),
                                                                                ObjectIDs[2][i],
                                                                                ObjectIDs[1][i],
                                                                                ObjectIDs[3][j], ObjectIDs[4][i],
                                                                                fromDv, toDv,
                                                                                fromT, toT, jevisUser,
                                                                                jevisPW,
                                                                                webservice)

        [Temperature, Setpoint_trend, Heater, Heater_sum, Disturbances, Energies] = a.import_measurement(systemname,weekend_operation, Temperature, OUTTemperature, Disturbances, Heater, Energies, Setpoints[i], fromDv, toDv, fromT, toT, calibration='true')

        a.DataDump_Measurement(systemname, Temperature, Setpoint_trend, Heater, Heater_sum, Disturbances, Energies,fromDv,toDv, fromT, toT)

        a.plot_measurement(systemname,fromDv,toDv, fromT, toT)

def Gasvergleich(configurationfile, Testzeitraum, Vergleichszeitraum):
    [ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = t.configuration_loader(configurationfile)

    gasID = '9833'
    LTGID = '7629'
    objID_temp = '9845'

    Testzeitraum = Testzeitraum.split('-')
    Vergleichszeitraum = Vergleichszeitraum.split('-')

    [gas_Test,fromD_utc, fromT_utc, toD_utc, toT_utc] = p.JEVISDataprep(gasID, Testzeitraum[0], Testzeitraum[1], '00', '00', jevisUser, jevisPW, webservice)
    [LTG_Test, fromD_utc, fromT_utc, toD_utc, toT_utc] = p.JEVISDataprep(LTGID, Testzeitraum[0], Testzeitraum[1], '00',
                                                                         '00', jevisUser, jevisPW, webservice)
    gas_Test = gas_Test[0] - LTG_Test[0]


    [gas_Vergleich, fromD_utc, fromT_utc, toD_utc, toT_utc] = p.JEVISDataprep(gasID, Vergleichszeitraum[0], Vergleichszeitraum[1], '00',
                                                                         '00', jevisUser, jevisPW, webservice)
    [LTG_Vergleich, fromD_utc, fromT_utc, toD_utc, toT_utc] = p.JEVISDataprep(LTGID, Testzeitraum[0], Testzeitraum[1], '00',
                                                                         '00', jevisUser, jevisPW, webservice)
    gas_Vergleich = gas_Vergleich[0] - LTG_Vergleich[0]

    [temperature_Test, fromD_utc, fromT_utc, toD_utc, toT_utc] = p.JEVISDataprep(objID_temp, Testzeitraum[0], Testzeitraum[1], '00', '00', jevisUser, jevisPW, webservice)

    [temperature_Vergleich, fromD_utc, fromT_utc, toD_utc, toT_utc] = p.JEVISDataprep(objID_temp, Vergleichszeitraum[0], Vergleichszeitraum[1], '00',
                                                                         '00', jevisUser, jevisPW, webservice)

    date0 = datetime.strptime(Testzeitraum[0], '%Y%m%d')
    date1 = datetime.strptime(Testzeitraum[1], '%Y%m%d')
    date2 = datetime.strptime(Vergleichszeitraum[0], '%Y%m%d')
    date3 = datetime.strptime(Vergleichszeitraum[1], '%Y%m%d')

    datedifference0 = (date1 - date0).days
    datedifference1 = (date3 - date2).days

    Heizgradtage_Test = np.zeros(datedifference0)
    Heizgradtage_Vergleich = np.zeros(datedifference1)

    for d in range(datedifference0):
        n = 0
        for i in range(len(temperature_Test[0])):
            if datetime.strftime(date0 + timedelta(days = d), '%Y-%m-%d') in str(temperature_Test[1][i]):
                Heizgradtage_Test[d] = Heizgradtage_Test[d] + temperature_Test[0][i]
                n = n + 1
        if Heizgradtage_Test[d] / n < 15:
            Heizgradtage_Test[d] = 15 - Heizgradtage_Test[d] / n
        else:
            Heizgradtage_Test[d] = 0

    for d in range(datedifference1):
        n = 0
        for i in range(len(temperature_Vergleich[0])):
            if datetime.strftime(date2 + timedelta(days=d), '%Y-%m-%d') in str(temperature_Vergleich[1][i]):
                Heizgradtage_Vergleich[d] = Heizgradtage_Vergleich[d] + temperature_Vergleich[0][i]
                n = n + 1
        if Heizgradtage_Vergleich[d] / n < 15:
            Heizgradtage_Vergleich[d] = 15 - Heizgradtage_Vergleich[d] / n
        else:
            Heizgradtage_Vergleich[d] = 0

    #print(Heizgradtage_Test, sum(Heizgradtage_Test))
    #print(Heizgradtage_Vergleich, sum(Heizgradtage_Vergleich))

    Heizgrad_Test = 15 - np.mean(temperature_Test[0])
    Heizgrad_Vergleich = 15 - np.mean(temperature_Vergleich[0])

    #for i in range(len(Heizgrad_Test)):
    #    if Heizgrad_Test[i] < 0:
    #        Heizgrad_Test[i] = 0

    #for i in range(len(Heizgrad_Vergleich)):
    #    if Heizgrad_Vergleich[i] < 0:
    #        Heizgrad_Vergleich[i] = 0

    print('Heizgradtage Test: ', sum(Heizgradtage_Test))
    print('Heizgradtage Vergleich: ', sum(Heizgradtage_Vergleich))

    gas_Test_clean = gas_Test * (sum(Heizgradtage_Vergleich))/(sum(Heizgradtage_Test))

    #print((gas_Test[0]))
    #print((gas_Vergleich[0]))
    #print((temperature_Test[0]))
    #print((temperature_Vergleich[0]))

    names = ['Referenz' , 'Test' , 'Test (witterungsbereinigt)']

    fig, ax = plt.subplots()
    b = ax.bar(names, [sum(gas_Vergleich), sum(gas_Test), sum(gas_Test_clean)])
    ax.bar_label(b)

def Stellgrößenvergleich(system, configurationfile, Testzeitraum, Vergleichszeitraum):
    [ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice, modelfile, heaterdata] = t.configuration_loader(configurationfile)

    Testzeitraum = Testzeitraum.split('-')
    Vergleichszeitraum = Vergleichszeitraum.split('-')

    #system = 'System 2'
    index = systems
    i = 0
    for j in range(np.size(systems)):
        for n in range(np.size(systems[j])):
            index[j][n] = i
            i = i + 1
    j = systemnames.index(system)

    Heater_Test = list(np.zeros(len(systems[j])))
    Heater_Vergleich = list(np.zeros(len(systems[j])))

    for n in range(len(systems[j])):
        Heater_Test[n] = [0,1]
        [Temperature,OUTTemperature,Disturbances,Heater_Test[n],Energies,weekend_operation] = p.totalprep(ObjectIDs[7][index[j][n]], heaterdata, ObjectIDs[0][index[j][n]],
                                                np.size(ObjectIDs[0][index[j][n]]),
                                                ObjectIDs[2][index[j][n]],
                                                ObjectIDs[1][index[j][n]], ObjectIDs[3][j], ObjectIDs[4][index[j][n]], Testzeitraum[0], Testzeitraum[1], '00',
                                                '00', jevisUser,
                                                jevisPW, webservice)
        #(WeekendID,heaterdata, ID_heater,heaters_number,ID_disturbances,ID_temperature,ID_fullload,ID_energy,fromD,toD,fromT,toT,jevisUser,jevisPW,webservice)

        [temperature_Test, fromD_utc, fromT_utc, toD_utc, toT_utc] = p.JEVISDataprep(ObjectIDs[2][0], Testzeitraum[0],
                                                                                     Testzeitraum[1], '00', '00',
                                                                                     jevisUser, jevisPW, webservice)

        [Temperature, OUTTemperature, Disturbances, Heater_Vergleich[n], Energies, weekend_operation] = p.totalprep(
            ObjectIDs[7][index[j][n]], heaterdata, ObjectIDs[0][index[j][n]],
            np.size(ObjectIDs[0][index[j][n]]),
            ObjectIDs[2][index[j][n]],
            ObjectIDs[1][index[j][n]], ObjectIDs[3][j], ObjectIDs[4][index[j][n]], Vergleichszeitraum[0],
            Vergleichszeitraum[1], '00',
            '00', jevisUser,
            jevisPW, webservice)
        # (WeekendID,heaterdata, ID_heater,heaters_number,ID_disturbances,ID_temperature,ID_fullload,ID_energy,fromD,toD,fromT,toT,jevisUser,jevisPW,webservice)

        [temperature_Vergleich, fromD_utc, fromT_utc, toD_utc, toT_utc] = p.JEVISDataprep(ObjectIDs[2][0],
                                                                                          Vergleichszeitraum[0],
                                                                                          Vergleichszeitraum[1], '00',
                                                                                          '00', jevisUser, jevisPW,
                                                                                          webservice)

    date0 = datetime.strptime(Testzeitraum[0], '%Y%m%d')
    date1 = datetime.strptime(Testzeitraum[1], '%Y%m%d')
    date2 = datetime.strptime(Vergleichszeitraum[0], '%Y%m%d')
    date3 = datetime.strptime(Vergleichszeitraum[1], '%Y%m%d')

    datedifference0 = (date1 - date0).days
    datedifference1 = (date3 - date2).days

    Heizgradtage_Test = np.zeros(datedifference0)
    Heizgradtage_Vergleich = np.zeros(datedifference1)

    for d in range(datedifference0):
        n = 0
        for i in range(len(temperature_Test[0])):
            if datetime.strftime(date0 + timedelta(days=d), '%Y-%m-%d') in str(temperature_Test[1][i]):
                Heizgradtage_Test[d] = Heizgradtage_Test[d] + temperature_Test[0][i]
                n = n + 1
        if Heizgradtage_Test[d] / n < 20:
            Heizgradtage_Test[d] = 20 - Heizgradtage_Test[d] / n
        else:
            Heizgradtage_Test[d] = 0

    for d in range(datedifference1):
        n = 0
        for i in range(len(temperature_Vergleich[0])):
            if datetime.strftime(date2 + timedelta(days=d), '%Y-%m-%d') in str(temperature_Vergleich[1][i]):
                Heizgradtage_Vergleich[d] = Heizgradtage_Vergleich[d] + temperature_Vergleich[0][i]
                n = n + 1
        if Heizgradtage_Vergleich[d] / n < 20:
            Heizgradtage_Vergleich[d] = 20 - Heizgradtage_Vergleich[d] / n
        else:
            Heizgradtage_Vergleich[d] = 0

    Sumed_Test = 0
    Sumed_Vergleich = 0
    print(Heater_Test[0])
    for n in range(len(systems[j])):
        Sumed_Test = Sumed_Test + sum(sum(Heater_Test[n]))
        Sumed_Vergleich = Sumed_Vergleich + sum(sum(Heater_Vergleich[n]))

    print(Sumed_Test, Sumed_Vergleich)

    print('Heizgradtage Test: ', sum(Heizgradtage_Test))
    print('Heizgradtage Vergleich: ', sum(Heizgradtage_Vergleich))

    Sumed_Test_clean = Sumed_Test * (sum(Heizgradtage_Vergleich)) / (sum(Heizgradtage_Test))

    # print((gas_Test[0]))
    # print((gas_Vergleich[0]))
    # print((temperature_Test[0]))
    # print((temperature_Vergleich[0]))

    names = ['Referenz', 'Test', 'Test (witterungsbereinigt)']
    titlenames = ['Leichtfass-Halle', 'Blechlager', 'Garagenfass-Halle']

    fig, ax = plt.subplots()
    b = ax.bar(names, [Sumed_Vergleich, Sumed_Test, Sumed_Test_clean])
    ax.bar_label(b)
    ax.set_title(titlenames[int(system[7])-1])

def moving_threshold(systemname, configurationfile, fromDv, toDv, fromT, toT):
    [ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice,
     modelfile, heaterdata] = t.configuration_loader(configurationfile)

    if systemname == 'all':
        # Plotting of all zones i
        i = 0
        for j in range(np.size(systems)):
            # Iteration through all halls/systems j
            for n in range(np.size(systems[j])):
                # Iteration through the zones n of hall/system j
                [Temperature, OUTTemperature, Disturbances, Heater, Energies, weekend_operation] = p.totalprep(
                    ObjectIDs[7][i], heaterdata, ObjectIDs[0][i],
                    np.size(ObjectIDs[0][i]),
                    ObjectIDs[2][i],
                    ObjectIDs[1][i],
                    ObjectIDs[3][j],
                    ObjectIDs[4][i],
                    fromDv, toDv,
                    fromT, toT, jevisUser,
                    jevisPW,
                    webservice)

                [Temperature, Setpoint_trend, Heater, Heater_sum, Disturbances, Energies] = a.import_measurement(
                    zonenames[i], weekend_operation,
                    Temperature, OUTTemperature, Disturbances, Heater, Energies, Setpoints[i], fromDv, toDv, fromT, toT,
                    calibration='true')
                a.threshold(Temperature, Setpoint_trend, Heater, Heater_sum, Disturbances, Energies)
                i = i + 1

    elif systemname in systemnames:
        # Modelidentifiction for one system (e.g. Hall 1 and 3 (LF))
        # create index array for the zone according their position in the configuration-arrays
        index = systems
        i = 0
        for j in range(np.size(systems)):
            for n in range(np.size(systems[j])):
                index[j][n] = i
                i = i + 1
        j = systemnames.index(systemname)
        for n in range(len(systems[j])):
            [Temperature, OUTTemperature, Disturbances, Heater, Energies, weekend_operation] = p.totalprep(
                ObjectIDs[7][index[j][n]], heaterdata, ObjectIDs[0][index[j][n]],
                np.size(ObjectIDs[0][index[j][n]]),
                ObjectIDs[2][index[j][n]],
                ObjectIDs[1][index[j][n]],
                ObjectIDs[3][j],
                ObjectIDs[4][index[j][n]],
                fromDv, toDv,
                fromT, toT, jevisUser,
                jevisPW,
                webservice)

            [Temperature, Setpoint_trend, Heater, Heater_sum, Disturbances, Energies] = a.import_measurement(
                zonenames[index[j][n]], weekend_operation,
                Temperature, OUTTemperature, Disturbances, Heater, Energies, Setpoints[index[j][n]], fromDv, toDv,
                fromT, toT,
                calibration='true')
            a.threshold(Temperature, Setpoint_trend, Heater, Heater_sum, Disturbances, Energies)
    else:
        i = zonenames.index(systemname)
        for list in systems:
            for element in list:
                if element == systemname:
                    j = systems.index(list)
        [Temperature, OUTTemperature, Disturbances, Heater, Energies, weekend_operation] = p.totalprep(ObjectIDs[7][i],
                                                                                                       heaterdata,
                                                                                                       ObjectIDs[0][i],
                                                                                                       np.size(
                                                                                                           ObjectIDs[0][
                                                                                                               i]),
                                                                                                       ObjectIDs[2][i],
                                                                                                       ObjectIDs[1][i],
                                                                                                       ObjectIDs[3][j],
                                                                                                       ObjectIDs[4][i],
                                                                                                       fromDv, toDv,
                                                                                                       fromT, toT,
                                                                                                       jevisUser,
                                                                                                       jevisPW,
                                                                                                       webservice)

        [Temperature, Setpoint_trend, Heater, Heater_sum, Disturbances, Energies] = a.import_measurement(systemname,
                                                                                                         weekend_operation,
                                                                                                         Temperature,
                                                                                                         OUTTemperature,
                                                                                                         Disturbances,
                                                                                                         Heater,
                                                                                                         Energies,
                                                                                                         Setpoints[i],
                                                                                                         fromDv, toDv,
                                                                                                         fromT, toT,
                                                                                                         calibration='true')
        a.threshold(Temperature, Setpoint_trend, Heater, Heater_sum, Disturbances, Energies)

def compare_measurements(systemname, configurationfile, Testzeitraum, Vergleichszeitraum):
    [ObjectIDs, horizon, weightfactor, systems, systemnames, zonenames, Setpoints, jevisUser, jevisPW, webservice,
     modelfile, heaterdata] = t.configuration_loader(configurationfile)

    Testzeitraum = Testzeitraum.split('-')
    Vergleichszeitraum = Vergleichszeitraum.split('-')
    print(Testzeitraum)
    print(Vergleichszeitraum)

    i = zonenames.index(systemname)
    for list in systems:
        for element in list:
            if element == systemname:
                j = systems.index(list)
    [Temperature, OUTTemperature, Disturbances, Heater, Energies, weekend_operation] = p.totalprep(ObjectIDs[7][i],heaterdata, ObjectIDs[0][i],
                                                                                np.size(ObjectIDs[0][i]),
                                                                                ObjectIDs[2][i],
                                                                                ObjectIDs[1][i],
                                                                                ObjectIDs[3][j], ObjectIDs[4][i],
                                                                                Testzeitraum[0],Testzeitraum[1],
                                                                                '00', '00', jevisUser,
                                                                                jevisPW,
                                                                                webservice)

    [Temperature_test, Setpoint_trend_test, Heater_test, Heater_sum_test, Disturbances_test, Energies_test] = a.import_measurement(systemname,weekend_operation, Temperature, OUTTemperature, Disturbances, Heater, Energies, Setpoints[i], Testzeitraum[0], Testzeitraum[1], '00', '00', calibration='true')

    a.DataDump_Measurement(systemname, Temperature_test, Setpoint_trend_test, Heater_test, Heater_sum_test, Disturbances_test, Energies_test, Testzeitraum[0], Testzeitraum[1], '00', '00',)


    [Temperature, OUTTemperature, Disturbances, Heater, Energies, weekend_operation] = p.totalprep(ObjectIDs[7][i],
                                                                                                   heaterdata,
                                                                                                   ObjectIDs[0][i],
                                                                                                   np.size(
                                                                                                       ObjectIDs[0][i]),
                                                                                                   ObjectIDs[2][i],
                                                                                                   ObjectIDs[1][i],
                                                                                                   ObjectIDs[3][j],
                                                                                                   ObjectIDs[4][i],
                                                                                                   Vergleichszeitraum[0],
                                                                                                   Vergleichszeitraum[1],
                                                                                                   '00','00', jevisUser,
                                                                                                   jevisPW,
                                                                                                   webservice)

    [Temperature_Vergleich, Setpoint_trend_Vergleich, Heater_Vergleich, Heater_sum_Vergleich, Disturbances_Vergleich,
     Energies_Vergleich] = a.import_measurement(systemname, weekend_operation, Temperature, OUTTemperature, Disturbances,
                                           Heater, Energies, Setpoints[i], Vergleichszeitraum[0], Vergleichszeitraum[1], '00', '00',
                                           calibration='true')

    a.DataDump_Measurement(systemname, Temperature_Vergleich, Setpoint_trend_Vergleich, Heater_Vergleich, Heater_sum_Vergleich, Disturbances_Vergleich,
     Energies_Vergleich, Vergleichszeitraum[0], Vergleichszeitraum[1], '00', '00', )

    a.plot_comparison_measurements(systemname, Testzeitraum[0], Testzeitraum[1], Vergleichszeitraum[0], Vergleichszeitraum[1])