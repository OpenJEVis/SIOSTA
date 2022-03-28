import numpy as np
from casadi import *
from datetime import date
from datetime import datetime, timedelta
import json
from requests.auth import HTTPBasicAuth
import requests
from mip import Model, xsum, BINARY
import math
import ParamFUNKTIONS as p

def Set_Setpoint(Setpoint_array, Time_array, weekend_operation, daynow, time_now, horizon, time_interval="00:05:00"):
    # Function for returning the Setpoints of a given future (event/time) horizon in an array for further calculations (model prediction control methods)
    # Setpoint_array and Time_array need to be arrays of the same size
    # times need to be a 'HH:MM:SS'-string
    sizeS = np.size(Setpoint_array)
    sizeT = np.size(Time_array)
    # conversion of strings in datetime-data
    time_interval = datetime.strptime(time_interval, '%H:%M:%S')
    time_interval = timedelta(hours=time_interval.hour, minutes=time_interval.minute, seconds=time_interval.second)
    time_now = datetime.strptime(daynow + time_now, '%Y%m%d%H:%M:%S')
    # initiate setpoint-array
    Setpoints = np.zeros(horizon)
    if sizeS != sizeT:
        print('ERROR: Setpoint_array and Time_array need to be arrays of the same size')
    else:
        for n in range(horizon):
            # Fill Setpoints for the given horizon
            if weekend_operation == 1:
                if (time_now+ n * time_interval).weekday() < 6:
                    for i in range(sizeT):
                        if time_now + n * time_interval >= datetime.strptime(daynow + '00:00:00', '%Y%m%d%H:%M:%S') + timedelta(hours=datetime.strptime(Time_array[i], '%H:%M:%S').hour, minutes=datetime.strptime(Time_array[i], '%H:%M:%S').minute, seconds=datetime.strptime(Time_array[i], '%H:%M:%S').second):
                            Setpoints[n] = Setpoint_array[i]
                else:
                    Setpoints[n] = Setpoint_array[0]
            else:
                if (time_now+ n * time_interval).weekday() < 5:
                    for i in range(sizeT):
                        if time_now + n * time_interval >= datetime.strptime(daynow + '00:00:00', '%Y%m%d%H:%M:%S') + timedelta(hours=datetime.strptime(Time_array[i], '%H:%M:%S').hour, minutes=datetime.strptime(Time_array[i], '%H:%M:%S').minute, seconds=datetime.strptime(Time_array[i], '%H:%M:%S').second):
                            Setpoints[n] = Setpoint_array[i]
                else:
                    Setpoints[n] = Setpoint_array[0]

    return Setpoints

#Predictions
def myfunNEW(temperature_c,disturbance_c,energies_c,Params,inputs_number,horizon,setpoint,weightening_ratio):
    # Creation of the Costfunction with the prediction and control horizon
    # check numbers of Variables
    disturbances_number=np.size(disturbance_c)
    energies_number=np.size(energies_c)
    Factor_size=1+inputs_number+(2*disturbances_number)+energies_number
    # initiate symbolic input variables (future heater signals that need to be calculated -> the optimization variables)
    U=SX.sym('U',horizon,inputs_number)
    # initiate symbolic Model-Output (predicted Zonetemperature)
    X=SX.sym('X',horizon,1)
    # Create equation-terms for the whole horizon
    for i in range(horizon):
        if inputs_number==1:
            heater_term=np.matmul(np.transpose(Params[1][0]),([(1),U[i]]))
        else:
            heater_term=SX.ones(Factor_size,1)
            for j in range(inputs_number):
                heater_term=np.multiply(heater_term,np.matmul(np.transpose(Params[1][j]),[1,U[i * inputs_number + j]]))
        if disturbances_number==1:
            Disturbance_term=np.matmul(np.transpose(Params[3][0]),np.reshape(np.array([(1),disturbance_c]),(2,1)))
        else:
            Disturbance_term=np.ones((Factor_size,1))
            for k in range(disturbances_number):
                Disturbance_term=np.multiply(Disturbance_term,np.matmul(np.transpose(Params[3][k]),np.reshape(np.array([1,disturbance_c[k]]),(2,1))))
        if energies_number==1:
            energies_term=np.matmul(np.transpose(Params[4][0]),np.reshape(np.array([(1),energies_c]),(2,1)))
        else:
            energies_term = np.ones((Factor_size, 1))
            for n in range(energies_number):
                energies_term = np.multiply(energies_term, np.matmul(np.transpose(Params[4][n]),
                                                                           np.reshape(np.array([1, energies_c[n]]),
                                                                                      (2, 1))))
        if i==0:
            Temperature_term=(np.matmul(np.transpose(Params[2]),([1,temperature_c])))
        else:
            Temperature_term=(np.matmul(np.transpose(Params[2]),([1,X[i-1]])))

        # add up all model-terms for the Zonetemperature prediction (symbolic equation of U)
        X[i]=(np.matmul(Params[5],(Params[0]*heater_term*Disturbance_term*energies_term*Temperature_term)))
    # Resizing arrays
    U=reshape(U,horizon*inputs_number,1)
    if np.size(setpoint) == 1:
        Setpoint_horizon = setpoint * np.ones((horizon, 1))
    else:
        Setpoint_horizon = np.transpose(setpoint)

    # weightening_ratio = Q/R with R = 1 !
    # Weight of Setpoint-error-term
    Q=weightening_ratio*1*np.identity(horizon)
    # Weight of expenses (energie consumption)
    r=1*np.identity(inputs_number)
    R=np.kron(r,np.identity(horizon))
    # Setpoint-Error
    TError=X-Setpoint_horizon
    # Create Sum of Inputs
    z2 = 0
    for i in range(GenSX.size(U,1)):
        z2 = z2 + U[i]
    # Quadratic Setpoint-Error-term
    z1 = mtimes(mtimes((TError.T), Q), TError)
    # add up cost-function with the summed up quadratic setpoint-errors and the sum of the inputs
    Cost_function = z1 + z2
    #print(Cost_function)
    return [Cost_function,U]

def myfunNEW_with_calibration(temperature_c, disturbance_c, energies_c, Params, inputs_number, horizon, setpoint,
             weightening_ratio):
    # Creation of the Costfunction with the prediction and control horizon
    # load model data into variables
    Factor_matrix_temperature = Params[2]
    Factor_matrix_heater = Params[1]
    Factor_matrix_disturbance = Params[3]
    Factor_matrix_energies = Params[4]
    Model_params = Params[0]
    Fphi = Params[5]
    slopes = Params[6]  # slope(0): slope for temperature forecast; slope(1): " for measured temperature; slope(1+n): " for Heater Signals; slope(1+n+m): " for disturbances
    offsets = Params[7]  # offset(0): offset for temperature forecast; offset(1): " for measured temperature; offset(1+n): " for Heater Signals; offset(1+n+m): " for disturbances
    # check numbers of Variables
    disturbances_number = np.size(disturbance_c)
    energies_number = np.size(energies_c)
    Factor_size = 1 + inputs_number + (2 * disturbances_number) + energies_number
    # initiate symbolic input variables (future heater signals that need to be calculated -> the optimization variables)
    U = SX.sym('U', horizon, inputs_number)
    # initiate symbolic Model-Output (predicted Zonetemperature)
    X = SX.sym('X', horizon, 1)
    # Create equation-terms for the whole horizon
    for i in range(horizon):
        if inputs_number == 1:
            heater_term = np.matmul(np.transpose(Factor_matrix_heater[0]), ([(1), slopes[1] * U[i] + offsets[1]]))
        else:
            heater_term = SX.ones(Factor_size, 1)
            for j in range(inputs_number):
                heater_term = np.multiply(heater_term, np.matmul(np.transpose(Factor_matrix_heater[j]), [1, slopes[1+j] * U[i * inputs_number + j] + offsets[1+j]]))

        if disturbances_number == 1:
            Disturbance_term = np.matmul(np.transpose(Factor_matrix_disturbance[0]), np.reshape(np.array([(1), slopes[1+j+1] * disturbance_c + offsets[1+j+1]]), (2, 1)))
        else:
            Disturbance_term = np.ones((Factor_size, 1))
            for k in range(disturbances_number):
                Disturbance_term = np.multiply(Disturbance_term, np.matmul(np.transpose(Factor_matrix_disturbance[k]),
                                                                           np.reshape(np.array([1, slopes[1+j+1+k] * disturbance_c[k] + offsets[1+j+1+k]]),
                                                                                      (2, 1))))
        if energies_number==1:
            energies_term = np.matmul(np.transpose(Factor_matrix_energies[0]), np.reshape(np.array([(1), slopes[1 + j + disturbances_number + 1] * energies_c[0] + offsets[1 + j + disturbances_number + 1]]), (2, 1)))
        else:
            energies_term = np.ones((Factor_size, 1))
            for n in range(energies_number):
                energies_term = np.matmul(np.transpose(Factor_matrix_energies[n]), np.reshape(np.array([(1), slopes[
                    1 + j + disturbances_number + 1 + n] * energies_c[n] + offsets[1 + j + disturbances_number + 1 + n]]),
                                                                                 (2, 1)))
        if i == 0:
            Temperature_term = (np.matmul(np.transpose(Factor_matrix_temperature), ([1, slopes[0] * temperature_c + offsets[0]])))
        else:
            Temperature_term = (np.matmul(np.transpose(Factor_matrix_temperature), ([1, slopes[0] * X[i - 1] + offsets[0]])))

        # add up all model-terms for the Zonetemperature prediction (symbolic equation of U)
        X[i] = ((np.matmul(Fphi,
                          (Model_params * heater_term * Disturbance_term * energies_term * Temperature_term))) - offsets[0])/slopes[0]
    # Resizing arrays
    U = reshape(U, horizon * inputs_number, 1)
    if np.size(setpoint) == 1:
        Setpoint_horizon = setpoint * np.ones((horizon, 1))
    else:
        Setpoint_horizon = np.transpose(setpoint)
    #print(Setpoint_horizon)

    # weightening_ratio = Q/R with R = 1 !
    # Weight of Setpoint-error-term
    Q = weightening_ratio * 1 * np.identity(horizon)
    # Weight of expenses (energie consumption)
    r = 1 * np.identity(inputs_number)
    R = np.kron(r, np.identity(horizon))
    # Setpoint-Error
    TError = X - Setpoint_horizon
    # Create Sum of Inputs
    z2 = 0
    for i in range(GenSX.size(U, 1)):
        z2 = z2 + U[i]
    # Quadratic Setpoint-Error-term
    z1 = mtimes(mtimes((TError.T), Q), TError)
    # add up cost-function with the summed up quadratic setpoint-errors and the sum of the inputs
    Cost_function = z1 + z2
    return [Cost_function, U]

#Control Algorithm BnB
# Not used at the end of SIOSTA because of long run-time
def ControlBnB(current_temperature,Heaters_number,current_disturbances,Setpoint,Params,weightening_ratio):
    k=1
    for i in range(Heaters_number):
        Params[0][k]=Params[0][k]*2
        k=k+1
        
    horizon=3
    J=myfunNEW(current_temperature,current_disturbances,Params,Heaters_number,horizon,Setpoint,weightening_ratio)
    #creating a vector of trues (boolean)
    A=2*np.ones((2*horizon))
    B=(A==2) #vector of booleans
    
    #optimization problem 
    nlp={'x': J[1], 'f': J[0]} #J[1]: optimization variables J[0]: cost function
    # options to suppress output from CASADI
    opts = {'ipopt.print_level': 0, 'print_time': 0}
    S=nlpsol('S', 'bonmin', nlp, {"discrete": B}, opts)
    #Bounds
    lowerb=0
    upperb=1       
    #solving optimization problem     
    r=S(x0=1*np.ones((Heaters_number*horizon,1)),lbx=lowerb,ubx=upperb)
    xopt=r['x'] #optimzation problem solution
    print('xopt :' , xopt)
    U=np.array([xopt.full()])
    U=np.reshape(U,(horizon*Heaters_number))
    #U=reshape(U,(horizon*Heaters_number))

    return np.array(U) #U: heater signals

#Function for MILP based approximation

def approx(heaterdata,Continuous_signal,ParamsCPD,Heaters_number,fullload_hall,calibration):
    # Fullload solutions
    ps = np.zeros((Heaters_number))  # initializing heater constants vector
    slopes = np.ones((Heaters_number))
    #offsets = np.zeros((Heaters_number))
    j = 1
    for i in range(Heaters_number):
        ps[i] = ParamsCPD[0][j]  # extracting heater constants from weighting vector of CPD
        j = j + 1
        if calibration == 'true':
            slopes[i] = ParamsCPD[6][j]
            Continuous_signal[i] = Continuous_signal[i] * slopes[i]
            #offsets[i] = ParamsCPD[7][j]
    m = Model()
    m.verbose = 0
    l = -(np.matmul(ps, Continuous_signal))  # -thermal influence of continuous inputs

    xc = m.add_var(lb=l, ub=l)  # adding variable equal to ^
    n = Heaters_number
    # Solving mixed integer linear problems for approximation
    xint = [m.add_var(var_type=BINARY) for i in range(n)]
    w = - 2*heaterdata[0]*ps
    w1 = -1
    b = 0
    m += xsum(((w[i] * (slopes[i]*xint[i]))) for i in range(n)) + (w1 * l) <= b
    c = 2*heaterdata[0]*ps

    c1 = 1
    m.objective = xsum((c[i] * (slopes[i]*xint[i])) for i in range(n)) + (c1 * l)
    m.optimize(max_seconds=300)
    # extracting the obtained solutions to a variable called xvint
    j = 0
    xx = np.zeros((Heaters_number + 1))
    for v in m.vars:
        xx[j] = v.x
        j = j + 1
    xvint = 2 * heaterdata[0] * xx[1:Heaters_number + 1]
    #print(m.objective_value)

    # Fullload OFF solutions (partload)
    # procedure same as above for fullload. We just do not multiply 2 to w and c
    # anymore. That was done to get fullload solutions
    m1 = Model()
    m1.verbose = 0
    xc = m1.add_var(lb=l, ub=l)  # adding variable equal to ^
    xint = [m1.add_var(var_type=BINARY) for i in range(n)]
    w = - 2 * heaterdata[1] * ps
    w1 = -1
    b = 0
    m1 += xsum(((w[i] * (slopes[i] * xint[i]))) for i in range(n)) + (w1 * l) <= b
    c = 2 * heaterdata[1] * ps

    c1 = 1
    m1.objective = xsum((c[i] * (slopes[i] * xint[i])) for i in range(n)) + (c1 * l)
    status = m1.optimize(max_seconds=300)
    j = 0
    xx = np.zeros((Heaters_number + 1))
    for v in m1.vars:
        xx[j] = v.x
        j = j + 1
    #print(m1.objective_value)
    xtint = 2 * heaterdata[1] * xx[1:Heaters_number + 1]

    # Choosing the solution out of fullload and non fullload according to energy consumption
    if status.name == 'INFEASIBLE' or fullload_hall == 1:
        teilE = math.inf
    else:
        teilE = (np.matmul(ps, np.multiply(xtint, slopes)))

    VollE = (np.matmul(ps, np.multiply(xvint, slopes)))

    if teilE > VollE:
        U = xvint
    else:
        U = xtint
    return U #integer approximation

#Control Algorithm MILP based Approximation
def Control(heaterdata, current_temperature,Heaters_number,current_disturbances,current_energies,Setpoints,Params,fullload_hall,weightening_ratio,horizon):
    # Algorithm for relaxed optimization, after that a approximation of the discrete solution based on the relaxed solutions
    # Create Cost-Function, based on the current measurements
    J=myfunNEW(current_temperature,current_disturbances,current_energies,Params,Heaters_number,horizon,Setpoints,weightening_ratio)

    # optimization problem
    nlp={'x': J[1], 'f': J[0]} #J[1]: optimization variables (U -> Heater Signals) J[0]: cost function with symbolic notation
    # options to suppress output from CASADI
    opts = {'ipopt.print_level': 0, 'print_time': 0}
    # determine solve (interior point optimizer)
    S=nlpsol('S', 'ipopt', nlp, opts)

    # Bounds (0 -> off, 2 -> fullload)
    lowerb=0
    upperb=2
    # solving optimization problem (x0 -> initial guess)
    r=S(x0=2*np.ones((horizon*Heaters_number,1)),lbx=lowerb,ubx=upperb)
    xopt=r['x'] #optimal relaxed solution
    print('xopt :' , xopt)
    # reshape input array
    U=np.array([xopt.full()])
    U_continuous=np.reshape(U,(horizon*Heaters_number))
    # approximate discrete solution based on the relaxed solution
    U_integer1=approx(heaterdata, U_continuous[0:Heaters_number],Params,Heaters_number,fullload_hall[0], 'false')
    U_integer2=approx(heaterdata, U_continuous[Heaters_number:2*Heaters_number],Params,Heaters_number,fullload_hall[1], 'false')
    U_integer3=approx(heaterdata, U_continuous[2*Heaters_number:3*Heaters_number],Params,Heaters_number,fullload_hall[2], 'false')
    # reshape input arrays
    U_integer=np.array([U_integer1,U_integer2,U_integer3])
    U_integer=np.reshape(U_integer,(3*Heaters_number))
    print('U opt :', U_integer)

    return np.array(U_integer) #U: heater signals

def Control_with_calibration(heaterdata, current_temperature, Heaters_number, current_disturbances, current_energies, Setpoints, Params,
            fullload_hall, weightening_ratio,horizon):
    # Algorithm for relaxed optimization, after that a approximation of the discrete solution based on the relaxed solutions
    # Create Cost-Function, based on the current measurements
    J = myfunNEW_with_calibration(current_temperature, current_disturbances, current_energies, Params, Heaters_number, horizon, Setpoints,
                 weightening_ratio)

    # optimization problem
    nlp = {'x': J[1], 'f': J[0]}  #J[1]: optimization variables (U -> Heater Signals) J[0]: cost function
    # options to suppress output from CASADI
    opts = {'ipopt.print_level': 0, 'print_time': 0}
    S = nlpsol('S', 'ipopt', nlp, opts)
    # Bounds (0 -> off, 2 -> fullload)
    lowerb = 0
    upperb = 2
    # solving optimization problem
    r = S(x0=2 * np.ones((horizon * Heaters_number, 1)), lbx=lowerb, ubx=upperb)
    xopt = r['x']  # optimzation problem solution
    print('xopt :', xopt)
    # reshape input array
    U = np.array([xopt.full()])
    U_continuous = np.reshape(U, (horizon * Heaters_number))
    # approximate discrete solution based on the relaxed solution
    U_integer1 = approx(heaterdata, U_continuous[0:Heaters_number], Params, Heaters_number, fullload_hall[0], 'true')
    U_integer2 = approx(heaterdata, U_continuous[Heaters_number:2 * Heaters_number], Params, Heaters_number, fullload_hall[1], 'true')
    U_integer3 = approx(heaterdata, U_continuous[2 * Heaters_number:3 * Heaters_number], Params, Heaters_number, fullload_hall[2], 'true')
    # reshape input arrays
    U_integer = np.array([U_integer1, U_integer2, U_integer3])
    U_integer = np.reshape(U_integer, (3 * Heaters_number))
    print('U opt :', U_integer)

    return np.array(U_integer)  # U: heater signals

#Making heater signal=2 to heater signal=1 and fullload=1
def Fullload_sep(heaterdata,U,Heaters_past,Heaters_number,fullload_hall):
    # Seperate Heater signals into binary Heater and Fullload signal
    # initiate output-arrays
    heater_out=np.zeros((np.size(U)))
    fullload_out=np.zeros((np.size(U)))

    #print(Heaters_past)
    # for t in range(len(fullload_hall)):
    #     for i in range(Heaters_number):
    #         if t == 0:
    #             if Heaters_past[i] == 0:
    #                 U[Heaters_number * t + i] = 2
    #         else:
    #             if U[Heaters_number * (t-1) + i] == 0:
    #                 U[Heaters_number * t + i] = 2

    # Check state of heater signals and convert into Heater and Fullload signal for the next 3 steps
    for t in range(len(fullload_hall)):
        fl = 0
        for i in range(Heaters_number):
            if U[Heaters_number * t + i]==2*heaterdata[0]:
                heater_out[Heaters_number * t + i] = 1
                fullload_out[Heaters_number * t + i] = 1
            elif U[Heaters_number * t + i]==2*heaterdata[1]:
                heater_out[Heaters_number * t + i] = 1

                # Check for t = 0, if Heater were ON before, if not they need to be started with Fullload ON
                if t == 0:
                    if Heaters_past[i] == 0:
                        fullload_out[Heaters_number * t + i] = 1
                    else:
                        fullload_out[Heaters_number * t + i] = 0
                # Check for each timestep, if Heater were ON the step before, if not they need to be started with Fullload ON
                else:
                    if U[Heaters_number * (t-1) + i] == 0:
                        fullload_out[Heaters_number * t + i] = 1
                    else:
                        fullload_out[Heaters_number * t + i] = 0

            elif U[Heaters_number * t + i]==0 and fullload_hall[t]==1:
                heater_out[Heaters_number * t + i] = 0
                fullload_out[Heaters_number * t + i] = 1
            elif U[Heaters_number * t + i]==0 and fullload_hall[t]==0:
                heater_out[Heaters_number * t + i] = 0
                fullload_out[Heaters_number * t + i] = 0

            if fullload_out[Heaters_number * t + i] == 1:
                fl = 1
        if fl == 1:
            for i in range(Heaters_number):
                fullload_out[Heaters_number * t + i] = 1
    print('U: ', np.add(heater_out, np.multiply(fullload_out, heater_out)))
    return fullload_out,heater_out

def JEVisDataprep_Control(objID,username,password,webservice):
    # Function to export the most recent Measurement of an Object vie ID
    # Create the URL with the needed Measurement
    sampleurl=webservice+'/objects/'+objID+'/attributes/Value/samples'
    sampleurl = sampleurl + '?' + 'onlyLatest=true'

    # Username & Password
    jevisUser = username
    jevisPW = password

    # Read JEVis data with URL, Username & Password
    get = requests.get(sampleurl, auth=HTTPBasicAuth(jevisUser, jevisPW))

    # print data
    #print("Get status: ", get)
    #print("Samples in JEVis: ", get.content)

    # put the read JEVis data to variable
    #print(get.text)
    if get.text == 'Object not found':
        print('ID ', objID, 'not found!')
        json_data = []
    else:
        json_data = json.loads(get.text)

    # inserting values
    vals = np.zeros(1)
    if json_data == []:
        vals = json_data
    else:
        vals[0] = json_data['value']  # values (eg. values of the heater states, door states)
    # Output: latest Values corresponding to the Object ID given
    return [vals]

#JEVis --> NumPY for control
def Controlprep(WeekendID,objID_Heaters,objID_disturbances,objID_energy,objID_temperature,username,password,webservice):
    # Read all the needed Measurements to solve the control problem (read all recent measurements according to one Zone)

    Heaters_number = np.size(objID_Heaters)
    sizeD=np.size(objID_disturbances)
    sizeE=np.size(objID_energy)

    if WeekendID == '':
        weekend_operation = 0
    else:
        data = JEVisDataprep_Control(WeekendID, username, password, webservice)
        #print(data)
        if data != [] and data != [[]]:
            weekend_operation = int(data[0])
        else:
            weekend_operation = 0
            print('Weekend-ID empty or does not exist!')
    print('Weekend Operations: ', weekend_operation)

    heaters_vals = np.zeros((Heaters_number))
    if Heaters_number > 1:
        for i in range(Heaters_number):
            data = JEVisDataprep_Control(objID_Heaters[i], username, password, webservice)
            if data != []:
                heaters_vals[i] = data[0]
            else:
                heaters_vals[i] = 0
    else:
        data = JEVisDataprep_Control(objID_Heaters, username, password, webservice)
        if data != []:
            heaters_vals = data[0]
        else:
            heaters_vals = 0

    if sizeD>1:
        dist_vals=np.zeros((sizeD))
        for i in range(sizeD):
            data=JEVisDataprep_Control(objID_disturbances[i],username,password,webservice)
            if data != []:
                dist_vals[i]=data[0]
            else:
                dist_vals[i]=0
    else:
        data=JEVisDataprep_Control(objID_disturbances,username,password,webservice)
        dist_vals=data[0]

    if sizeE>1:
        energie_vals=np.zeros((sizeE))
        for i in range(sizeE):
            data=JEVisDataprep_Control(objID_energy[i],username,password,webservice)
            if data != []:
                energie_vals[i]=data[0]
            else:
                energie_vals[i]=0
    else:
        data=JEVisDataprep_Control(objID_energy[0],username,password,webservice)
        energie_vals=data[0]
      
    temperature=JEVisDataprep_Control(objID_temperature,username,password,webservice)
    temperature_vals=temperature[0]
    return heaters_vals,dist_vals,energie_vals,temperature_vals,weekend_operation

#Read values from JEVis for control
def Control_read(WeekendID,objID_Heaters,ID_disturbances,ID_energy,ID_temperature,username,password,webservice):
    #Read
    vals=Controlprep(WeekendID,objID_Heaters,ID_disturbances,ID_energy,ID_temperature,username,password,webservice) #Json lesen

    #Heater
    heaters_latest = vals[0]
    #Temperature
    temperature_latest=vals[3]
    print('Zonetemperature (latest in JEVis):', temperature_latest)
    #Disturbances
    dist_latest=vals[1]
    #Energies
    energie_latest=vals[2]
    #Weekend Operation value
    weekend_operation = vals[4]
    return heaters_latest,temperature_latest,dist_latest,energie_latest,weekend_operation

#write values from Control function (see above) to JEVis IDs
def JEVis_write(val,objID,fromD,toD,fromT,toT,gap,username,password,webservice):
    from datetime import datetime, timedelta
    # Write into JEVis ID
    sampleurl=webservice+'/objects/'+objID+'/attributes/Value/samples'
    sampleurl=sampleurl+'?'+'from='+fromD+'T'+fromT+'0000&until='+toD+'T'+toT+'0000'
    jevisUser = username
    jevisPW = password
    datetime=datetime.now()+timedelta(hours=00, minutes=gap)
    Zeit=datetime.astimezone().isoformat(timespec='milliseconds')
    payload = '[{"ts":'+'"'+ Zeit+'"'+',"value": '+'"'+val+'"''}]'
    post = requests.post(sampleurl, auth=HTTPBasicAuth(jevisUser, jevisPW), data=payload)
    #print("Post status: ",post)

def Control_write(ID_heaters, ID_fullload, fullload, heaters,username,password,webservice):
    # Function to iterate through all Signals that needed to be written in JEVis
    today=date.today()
    todayymd=today.strftime("%Y%m%d")
    now1=datetime.now()
    timestr1=now1.strftime("%H%M%S")
    sizeID=len(ID_heaters)
    for i in range(sizeID):
        for j in range(len(ID_heaters[i])):
            JEVis_write(str(heaters[i]),ID_heaters[i][j],todayymd,todayymd,timestr1,timestr1,0,username,password,webservice)
    for i in range(len(ID_fullload)):
        JEVis_write(str(fullload[0]),ID_fullload[i],todayymd,todayymd,timestr1,timestr1,0,username,password,webservice)

def load_model(filename, zonename):
    # loading model from a txt-file and convert JSON-Format (Dictionary) into a python-list
    file = open(filename, 'r')
    line_number = 0
    content = ''
    # content = file.read().splitlines(keepends=True)
    for num, line in enumerate(file, 1):
        if re.search(zonename + ':', line):
            line_number = num + 1
        if num == line_number:
            content = line
    file.close()

    params_dict = json.loads(content)

    params = [np.array(params_dict['Parameter']), params_dict['Heater'], np.array(params_dict['Temperature']),
              params_dict['Disturbances'], params_dict['Energies'], np.array(params_dict['Phi'])]
    for i in range(len(params[1])):
        params[1][i] = np.array(params_dict['Heater'][i])
    for i in range(len(params[3])):
        params[3][i] = np.array(params_dict['Disturbances'][i])

    return params

def load_model_with_calibration(filename, zonename):
    # loading model from a txt-file and convert JSON-Format (Dictionary) into a python-list
    file = open(filename, 'r')
    line_number = 0
    content = ''
    # content = file.read().splitlines(keepends=True)
    for num, line in enumerate(file, 1):
        if re.search(zonename + ':', line):
            line_number = num + 1
        if num == line_number:
            content = line
    file.close()

    params_dict = json.loads(content)

    params = [np.array(params_dict['Parameter']), params_dict['Heater'], np.array(params_dict['Temperature']),
              params_dict['Disturbances'], params_dict['Energies'], np.array(params_dict['Phi']), np.array(params_dict['slopes']), np.array(params_dict['offsets'])]
    for i in range(len(params[1])):
        params[1][i] = np.array(params_dict['Heater'][i])
    for i in range(len(params[3])):
        params[3][i] = np.array(params_dict['Disturbances'][i])

    return params

def Time_reader(TimeID,username,password,webservice):
    # When no Time ID (when no NTP Time available) use local Time
    if TimeID == '':
        now_day = datetime.utcnow().strftime("%Y%m%d")
        now_time = datetime.utcnow().strftime("%H:%M:%S")
        print('WARNING: No NTP-Time available! Local Server Time is used!')
    else:
        data = JEVisDataprep_Control(TimeID,username,password,webservice)
        if data != []:
            timestamp_seconds = int(data[0])
            time = datetime.fromtimestamp(timestamp_seconds)
            now_day = time.strftime("%Y%m%d")
            now_time = time.strftime("%H:%M:%S")
        else:
            now_day = datetime.utcnow().strftime("%Y%m%d")
            now_time = datetime.utcnow().strftime("%H:%M:%S")
            print('WARNING: No NTP-Time available! Local Server Time is used!')

    print('Date-Time UTC: ' + now_day + '-' + now_time)

    return [now_day, now_time]