import numpy as np
import matplotlib.pyplot as plt
import datetime

import pytz
from requests.auth import HTTPBasicAuth
import requests
import json
from casadi import *
import RegFUNKTIONS as r

######Function to convert JEVis data to NUMPy
##objID= object ID
##fromD = from (Date)
##toD = to (Date)
##fromT = from time (according to UST standard)
##toT = to time (according to UST standard)
##username = jevisUser
##password = jevisPW

def JEVISDataprep(objID,fromD,toD,fromT,toT,username,password,webservice):
    # Data preparation for importing Signal-trends for a given time Period
    ##Username & Password
    jevisUser = username
    jevisPW = password

    # starting Time as datetime class
    start = datetime.datetime.strptime(fromD + 'T:' + fromT, '%Y%m%dT:%H')

    # get latest data to get information about timezone:
    sampleurl = webservice + '/objects/' + objID + '/attributes/Value/samples'
    sampleurl = sampleurl + '?' + 'onlyLatest=true'
    get = requests.get(sampleurl, auth=HTTPBasicAuth(jevisUser, jevisPW))

    if get.text == 'Object not found':
        print('ID ', objID, 'not found!')
        json_data = []
    else:
        json_data = json.loads(get.text)

    #print(json_data)
    t = datetime.datetime.strptime(json_data['ts'], "%Y-%m-%dT%H:%M:%S.000%z")
    timezone = t.strftime('%z')

    # convert local time to utc time:
    start = datetime.datetime.strptime(fromD + 'T:' + fromT + timezone, '%Y%m%dT:%H%z')
    start = start.astimezone(pytz.utc)
    end = datetime.datetime.strptime(toD + 'T:' + toT + timezone, '%Y%m%dT:%H%z')
    end = end.astimezone(pytz.utc)
    fromD = start.strftime('%Y%m%d')
    fromT = start.strftime('%H')
    toD = end.strftime('%Y%m%d')
    toT = end.strftime('%H')

    # URL Construction for Data download
    sampleurl=webservice+'/objects/'+objID+'/attributes/Value/samples'
    sampleurl=sampleurl+'?'+'from='+fromD+'T'+fromT+'0000&until='+toD+'T'+toT+'0000'

    # Read JEVis data with URL, Username & Password
    get = requests.get(sampleurl, auth=HTTPBasicAuth(jevisUser, jevisPW))
    
    ##print data
    #print("Get status: ",get)
    #print("Samples in JEVis: ",get.content)
    
    # put the read JEVis data as new variable
    if get.text == 'Object not found':
        print('ID ', objID, 'not found!')
        json_data = []
    else:
        json_data = json.loads(get.text)
    
    # convert the data from json format to numpy array format
    length_json=np.size(json_data) #size detection of json 
    
    # initialization of variables with values and times
    vals=np.zeros((length_json)) #values (eg. values of the heater states, door states)
    times=np.empty((length_json),dtype="S29") #times 
    
    #  inserting values and time data to initialized variables
    for i in range(length_json):
        vals[i]=json_data[i]['value']
        #times[i]=json_data[i]['ts']

        ts = datetime.datetime.strptime(json_data[i]['ts'], "%Y-%m-%dT%H:%M:%S.000%z")
        ts_utc = ts.astimezone(pytz.utc)
        times[i] = datetime.datetime.strftime(ts_utc, '%Y-%m-%dT%H:%M:%S.000%z')

    ##Output: Values and times corresponding to the Object ID given
    return [vals, times], fromD, fromT, toD, toT



######Function to convert output of JEVISDataprep to minute basis data
##Data: Values and times(vals & times of previous function). Python list with
#values and times arrays
##daysnumber: no. of days (creation of minute basis data for daysnumber days)
def Minutebasis(Data,fromD,toD,fromT,toT):
    vals=Data[0] #extract values
    length=np.size(vals) #size calculation
    dates=Data[1] #extract dates and times
    # conversion of dates to an array of date strings
    strdates=[]
    strtimes=[]        
    for i in range(np.size(dates)):
        # extract date & time and convert to string
        strdates.append("")
        strdates[i]=str(dates[i])
        # extract time from date time string
        start=strdates[i].find('T')+1
        end=strdates[i].find('.000')
        strtimes.append("")
        strtimes[i]=strdates[i][start:end]
        strdates[i] = strdates[i][0:start]

    lentimes=np.size(strtimes) #size of the time array
    # add minutes and seconds to time string
    times = fromT + ':00:00'
    # change format of the date string
    dates = "b'" + fromD[0:4] + "-" + fromD[4:6] + "-" + fromD[6:8] + "T"

    for j in range(lentimes):
        times=np.append(times,strtimes[j])
        dates=np.append(dates,strdates[j])
    times=np.array(times) #conversion to string array
    lentimes=np.size(times) #size of the time array
    # initialize Input vector
    Outdata=[]
    #This loop creates minute seperated input vector from JEVis input/disturbance
    for i in range(lentimes-1):
        #calculate time gap in seconds between consecutive elements of vector
        chk=datetime.datetime.strptime(dates[i+1] + times[i+1],"b'%Y-%m-%dT%H:%M:%S")-datetime.datetime.strptime(dates[i] + times[i],"b'%Y-%m-%dT%H:%M:%S")

        #convert to minutes
        sec=int(int(chk.seconds/60))

        #Build array acc. to the time (min) between 2 consecutive inputs
        if i==0:
            if vals[i]==0.0:
                Outdata = np.concatenate((Outdata, np.kron(1, np.zeros(sec))), axis=0)
            elif vals[i]==1.0:
                Outdata = np.concatenate((Outdata, np.kron(0, np.zeros(sec))), axis=0)
            else:
                Outdata = np.concatenate((Outdata, np.kron(vals[i], np.zeros(sec))), axis=0)
        else:
            Outdata=np.concatenate((Outdata,np.kron(vals[i-1],np.ones(sec))),axis=0)
    #Fill the last values after the latest measurement in the dataset
    datasize=np.size(Outdata)
    datedifference = (datetime.datetime.strptime(toD+':'+toT, '%Y%m%d:%H') - datetime.datetime.strptime(fromD+':'+fromT, '%Y%m%d:%H'))
    minutes = datedifference.seconds/60 + datedifference.days * 24 * 60
    diff=int((minutes)-datasize)

    Outdata=np.concatenate((Outdata,vals[length-1]*np.ones(diff)))
    Outdata=np.reshape(Outdata,(int(minutes),1))

    # Create array on 5 min array
    k=0
    FOut=np.zeros(int(np.size(Outdata)/5))
    for i in range(np.size(FOut)):
        FOut[i]=Outdata[k]
        k=k+5
    Fout=np.reshape(FOut,(int(np.size(Outdata)/5),1))
    return Fout

######Function to convert heater and fullload values to 0, 1, 2 for heaters
##heater : Heater value (0 off or 1 on)
##fullload: Fullload value (0 off or 1 on)
##number_heaters: number of heaters
def Fullload(heaterdata, heater,fullload):
    heater_all = heater[0]
    for i in range(1,len(heater)):
        heater_all = np.hstack((heater_all, heater[i]))
    vv=np.where(fullload==1,2 * heaterdata[0],fullload)
    full_load=np.where(vv==0,2 * heaterdata[1],vv)
    full_load = np.hstack([full_load] * len(heater))
    finalval=np.multiply(heater_all,full_load)
    return finalval


######Function to convert all signals in numpy form for the parameter identification from JEVis IDs
# objID_heater: Heater ID
# number_heaters: number of heaters
# objID_disturbance: IDs of the disturbances (external temperature, doors)(can be an array)
# objID_temp: ID of Zone temperature
# objID_fullload: ID of Volllast
# fromD: From date
# toD: till date
# fromT: From time
# toT: Till time
# days: Number of days (no.of days of the data used for identification)
# example:
# [temperature,temperatureout,Disturbancesp,heater]=totalprep('18886',2,'9845','19847','19851','20210206','20210216','23','23',10)

def totalprep(WeekendID, heaterdata, objID_heater,number_heaters,objID_disturbance,objID_temp,objID_fullload,objID_energy,fromD,toD,fromT,toT,username,password,webservice):
    # initialize measurement arrays
    heater = [''] * number_heaters
    heaterm = [''] * number_heaters
    # Iteration through all heaters
    for i in range(number_heaters):
        # import from JEVis
        [heater[i],fromD_utc, fromT_utc, toD_utc, toT_utc]  = JEVISDataprep(objID_heater[i], fromD, toD, fromT, toT, username, password, webservice)
        if len(heater[i][0]) == 0:
            heater[i][0] = r.read(objID_heater[i], username, password, webservice)
        # Convert to a 5 minute-basis
        heaterm[i] = Minutebasis(heater[i],fromD_utc,toD_utc,fromT_utc,toT_utc)
    # Importing Temperature States
    [temperature,fromD_utc, fromT_utc, toD_utc, toT_utc] = JEVISDataprep(objID_temp, fromD, toD, fromT, toT, username, password, webservice)
    temperaturem = Minutebasis(temperature, fromD_utc, toD_utc, fromT_utc, toT_utc)

    # create second temperature array shifted by one timestep for the parameteridentification
    temperatureout = np.append(temperaturem[1:np.size(temperaturem)], temperature[0][np.size(temperature[0])-1])

    temperature = temperaturem

    # Import fullload Signal
    if objID_fullload == '':
        # if fullload ID is empty, create a array of ones. Then only fullload occurs in the given Zone
        Floadm = np.ones((int(np.size(heaterm)/len(heaterm)), 1))
    else:
        # Import from JEVis
        [Fload,fromD_utc, fromT_utc, toD_utc, toT_utc] = JEVISDataprep(objID_fullload, fromD, toD, fromT, toT, username, password, webservice)
        # Convert to a 5 minute-basis
        Floadm = Minutebasis(Fload,fromD_utc,toD_utc,fromT_utc,toT_utc)
    # Check how many Disturbances the Zone has, fist Disturbance always is the Outside Temperature
    if isinstance(objID_disturbance, list) == False:
        # If a Zone has just one Disturbance (meaning the outside Temperature)
        # Import from JEVis
        [Disturbances,fromD_utc, fromT_utc, toD_utc, toT_utc] = JEVISDataprep(objID_disturbance, fromD, toD, fromT, toT, username, password, webservice)
        # Convert to a 5 minute-basis
        if np.size(Disturbances) > 0:
            Disturbancesp = Minutebasis(Disturbances,fromD_utc,toD_utc,fromT_utc,toT_utc)
    else:
        # check the number of disturbances
        nd = np.size(objID_disturbance)
        # check the number of needed samples
        nsamples = np.size(temperature)
        # initialize a list consisting of all disturbances
        Disturbancesp = np.zeros((nsamples, nd))

        for i in range(nd):
            # import from JEVis
            [Disturbances,fromD_utc, fromT_utc, toD_utc, toT_utc] = JEVISDataprep(objID_disturbance[i], fromD, toD, fromT, toT, username, password, webservice)
            # Convert to a 5 minute-basis
            if np.size(Disturbances) > 0:
                Disturbancesp[:, i] = np.reshape(Minutebasis(Disturbances,fromD_utc,toD_utc,fromT_utc,toT_utc), (nsamples))
            else:
                Disturbancesp[i] = 0

        # convert doorsignals from (0 - open / 1 - closed) to (0 - closed / 1 - open)
        k = 1
        while k < nd:
            for i in range(nsamples):
                if Disturbancesp[i, k] == 0:
                    Disturbancesp[i, k] = 1
                else:
                    Disturbancesp[i, k] = 0
            k = k + 1

    nsamples = np.size(temperature)

    if WeekendID == '':
        weekend_operation = np.zeros((nsamples, 1))
    else:
        [weekend_operation_read, fromD_utc, fromT_utc, toD_utc, toT_utc] = JEVISDataprep(WeekendID, fromD, toD, fromT, toT, username, password, webservice)

        if weekend_operation_read != [] and weekend_operation_read != [[]]:
            weekend_operation = Minutebasis(weekend_operation_read, fromD_utc, toD_utc, fromT_utc, toT_utc)
        else:
            weekend_operation = np.zeros((nsamples, 1))

    # Check if energy measurements are available
    if objID_energy != ['']:
        # check if more than one energy measurements are available
        if isinstance(objID_energy, list) == False:
            # if only one is avaiable
            # import from JEVis
            [Energies,fromD_utc, fromT_utc, toD_utc, toT_utc] = JEVISDataprep(objID_energy, fromD, toD, fromT, toT, username, password, webservice)
            # convert to a 5 minute-basis
            Energiesp = Minutebasis(Energies,fromD_utc,toD_utc,fromT_utc,toT_utc)
        else:
            # if multiple energy measurements are avaiable
            # check how many
            ne = np.size(objID_energy)
            # initialize array for the energy measurements
            Energiesp = np.zeros((nsamples, ne))

            for i in range(ne):
                # Iteration through the Energy IDs
                # Import from JEVis
                #print(objID_energy[i])
                [Energies,fromD_utc, fromT_utc, toD_utc, toT_utc] = JEVISDataprep(objID_energy[i], fromD, toD, fromT, toT, username, password, webservice)

                # convert to a 5 minute-basis
                Energiesp[:, i] = np.reshape(Minutebasis(Energies,fromD_utc,toD_utc,fromT_utc,toT_utc), (nsamples))
    else:
        # if no energy measurements are available, create a 0 array to access generic calculation for the parameteridentifictaion (can be optimized, probably with some if-clauses)
        Energiesp = np.zeros((nsamples, 1))

    # convert heater and fullload measurements to trinary (0 / 1 / 2) signals for the heaters
    heater = Fullload(heaterdata, heaterm, Floadm)
    
    return [temperature,temperatureout,Disturbancesp,heater,Energiesp,weekend_operation]


#####Model parameter Identification
#NumPY Data ---> Model parameters as decomposed tensors
#According to Kai PhD


#CP Tensor Factor matrices construction
#size_factor: size of the factor matrix
#position: position of terms
def Factors1(size_factor,position):
    # Check if the variable just has one position
    if np.isscalar(position)==True:
        n=1
        # initialize Matrix of the correct size (2 times number of terms in the state-function)
        Factor_matrix=np.ones((2,size_factor))
        # set lower Values to 0 (values of the second row)
        Factor_matrix[1][0:size_factor]=np.zeros((1,size_factor))
        # set upper value (in first row) of the variable-position to 0 and the lower value (in second row) to 1
        Factor_matrix[0][position-1]=0
        Factor_matrix[1][position-1]=1
        # output: Python list with all the factor matrices corresponding to temperature, heaters and disturbances
        # in the Factor-Matrix now is represented in which term the measured Data will be added in the function
        return Factor_matrix  
    else:
        n=np.size(position,0)
        # initialize Matrix of the correct size (2 times number of terms in the state-function)
        Factor_matrix=np.ones((2,size_factor))
        # set lower Values to 0 (values of the second row)
        Factor_matrix[1][0:size_factor]=np.zeros((1,size_factor))
        for i in range(n):
            # Iteration through all Positions where the Variable should be
            # set upper value (in first row) of the variable-position to 0 and the lower value (in second row) to 1
            Factor_matrix[0][int(position[i]-1)]=0
            Factor_matrix[1][int(position[i]-1)]=1
        # output: Python list with all the factor matrices corresponding to temperature, heaters and disturbances
        # in the Factor-Matrix now is represented in which term the measured Data will be added in the function
        return Factor_matrix     

def decparamIDD(heater,temperature,Disturbances,Energies,Outtemperature, set_equalHeaterParameter = 'false'):
    # sizes calculation
    Values_number=np.size(heater,0)
    heaters_number=np.size(heater,1)    
    Disturbances_number=np.size(Disturbances,1)
    energies_number=np.size(Energies,1)
    
    #according to number of variables, set size of factor matrices (input for Factors1 function)
    sze=1+heaters_number+(2*Disturbances_number)+energies_number
    
    # initialize factor matrices lists    
    Factor_matrix_heater=[np.zeros((2,sze))] * heaters_number
    Factor_matrix_temperature=[np.zeros((2,sze))] 
    Factor_matrix_Disturbances=[np.zeros((2,sze))] * (Disturbances_number)
    Factor_matrix_energie = [np.zeros((2,sze))] * energies_number
    
    # construct factor matrices:
    # Factor matrices corresponding to heaters
    k=2 #starting position of heater terms
    for i in range(heaters_number):
        Factor_matrix_heater[i]=Factors1(sze,k)
        k=k+1
    
    #Factor matrices corresponding to temperatures
    m = 1+heaters_number+1 #position of temperature term for heatloss calculation
    Positions_temperature = np.ones((1+Disturbances_number)) #initialize position vector for temperatures according
    #to number of disturbances
    for i in range(Disturbances_number):
        Positions_temperature[i+1]=m
        m=m+2
    Factor_matrix_temperature=Factors1(sze,Positions_temperature) #factor matrix corresponding to temperature

    for i in range(energies_number):
        Factor_matrix_energie[i]=Factors1(sze,1+heaters_number+(2*Disturbances_number)+1+i)

    # Factor matrix corresponding to disturbances
    # create positions for disturbances
    ind = [''] * Disturbances_number
    pos_doors = [''] * (Disturbances_number - 1)  # Position of binary Disturbances (eg outdoor-Doors)
    for i in range(Disturbances_number):
        if i == 0:
            pos_outdoor_temperature = heaters_number + 3  # Position of outdoor Temperature
        else:
            pos_outdoor_temperature = np.append(pos_outdoor_temperature, pos_outdoor_temperature + 2)
            ind[i] = [2 * i + heaters_number + 2, 2 * i + heaters_number + 3]
    ind[0] = pos_outdoor_temperature
    # create factor matrices corresponding to disturbances
    for i in range(Disturbances_number):
        Factor_matrix_Disturbances[i] = Factors1(sze, ind[i])
    
    # Optimization problem for parameter identification:
    # Define Optimization variables (with symbolic programming)
    model_params=SX.sym('L',(sze),1)
    # Initialize set of output signals, that the model should calculate when identified
    Outtemperatureest=SX.sym('Y',Values_number,1)
    # Vector/Matrix needed to create a function out of the Matrices and Vectors (just needed for the math in SIOSTA, in more complexe systems this Matrix would define in which function the different terms need to be added)
    Fphi=np.ones((1,sze))
    
    # estimated temperatures from the model in terms of unknown parameters
    for i in range(Values_number):
        # Iterate through all measurements
        # initialize the different terms that need to be added
        terms_heaters=np.ones((sze,1))
        terms_disturbances=np.ones((sze,1))
        terms_energies=np.ones((sze,1))
        # Calculate the Input-Term with the measurements of the heater signals
        for j in range(heaters_number):
            terms_heaters=np.multiply(terms_heaters,np.matmul(np.transpose(Factor_matrix_heater[j]),np.array([[1],[heater[i][j]]])))
        # Calculate the Disturbance-Term with the measurements of the disturbance signals
        for k in range(Disturbances_number):
            terms_disturbances=np.multiply(terms_disturbances,np.matmul(np.transpose(Factor_matrix_Disturbances[k]),np.array([[1],[Disturbances[i][k]]])))
        # Calculate the Energie-Term with the measurements of the energie consumption signals
        for n in range(energies_number):
            terms_energies=np.multiply(terms_energies,np.matmul(np.transpose(Factor_matrix_energie[n]),np.array([[1],[Energies[i][n]]])))
        # Calculate the Temperature-Term with the measurements of the zonetemperature signals
        terms_temp=(np.matmul(np.transpose(Factor_matrix_temperature),np.array([[1],[temperature[i]]])))
        # Output-Equation: Multiply the different Terms with the Parameters that need to be found and all those terms together
        Outtemperatureest[i]=mtimes(Fphi,(model_params*terms_heaters*terms_disturbances*terms_energies*terms_temp))

    # Create Cost-Function for Optimization: squared Error between measured Temperature and estimated Temperature by the model need to be minimized
    J=Outtemperature-Outtemperatureest #estimation error
    Cost_function=mtimes(J.T,J)/2   #least squares cost function
    
    # Optimization problem equality constraints
    # the parameter of the Zone- and Outside-Temperature in the disturbance term need to be the same size, but with different algebraic sign
    lim=SX.sym('lim',Disturbances_number,1)

    if set_equalHeaterParameter == 'true':
        lim=SX.sym('lim', heaters_number - 1 + Disturbances_number,1)
    elif set_equalHeaterParameter == 'false':
        lim=SX.sym('lim',Disturbances_number,1)
    else:
        print('ERROR: equalHeaterParameter-Value must be true or false!')

    if set_equalHeaterParameter == 'true':
        for i in range((heaters_number - 1)):
            lim[i] = model_params[1 + i] - model_params[1 + i + 1]

    k=1
    for i in range(Disturbances_number):
        if set_equalHeaterParameter == 'true':
            lim[(heaters_number - 1) + i] = model_params[heaters_number + k] + model_params[heaters_number + k + 1]
            k = k + 2
        else:
            lim[i] = model_params[heaters_number + k] + model_params[heaters_number + k + 1]
            k = k + 2

    # Defining the Non-linear Problem ( x -> optimization variables, f -> Optimization function, g -> boundary function)
    nlp={'x': model_params, 'f': Cost_function, 'g':(lim)}
    # Defining the solver to use (ipopt -> interior point optimizer)
    S=nlpsol('S', 'ipopt', nlp)
    
    # bound constraints of optimization problem
    lb=1
    lb=np.append(lb,np.zeros((heaters_number))) # lower bound of the heater Parameters
    lb=np.append(lb,-np.inf*(np.ones((2*Disturbances_number)))) # lower bound of the Disturbance Parameters
    lb = np.append(lb, np.zeros((energies_number))) # lower bound of the Energy Consumption Parameters
    
    ub=1
    ub=np.append(ub,np.ones((heaters_number))) # upper bound of the heater Parameters
    ub=np.append(ub,np.inf*(np.ones((2*Disturbances_number)))) # upper bound of the Disturbance Parameters
    ub = np.append(ub, np.inf * (np.ones((energies_number)))) # upper bound of the Energy Consumption Parameters

    # boundarys for secondary equations (e.g. equality constraints)
    if set_equalHeaterParameter == 'true':
        lbg = np.zeros(((heaters_number - 1) + Disturbances_number, 1))
        ubg = np.zeros(((heaters_number - 1) + Disturbances_number, 1))
    else:
        lbg = np.zeros((Disturbances_number, 1))
        ubg = np.zeros((Disturbances_number, 1))

    #Optimization problem solution (x0 -> initial guess)
    r = S(x0=np.ones((sze,1)),lbx=(lb),ubx=(ub), lbg=(lbg), ubg=(ubg))
    xopt=r['x'] # optimal solution
    print('xopt :' , xopt)
    Fc=xopt.full() # Fc = model params (lambda of CP-decomposed Tensor-form)
    # Output: decomposed parameter tensor (representing the values) and Factor matrices (representing the structure)
    return [Fc, Factor_matrix_heater, Factor_matrix_temperature, Factor_matrix_Disturbances, Factor_matrix_energie, Fphi]

# Model Validation (simulate with given input signals to calculate expected Zonetemperatures)
def decvalidS(zonename, heater, temp_start, Disturbances, Energies, Params):
    # Check numbers of the different types of signals
    if heater.ndim == 1:
        # if only the next temperature need to be calculated (for closed-loop simulations)
        Values_number = 1
        Heaters_number = np.size(heater)
        Disturbances_number = np.size(Disturbances)
        Energies_number = np.size(Energies)
    else:
        # if a given timeperiod need to be calculated (for valuating the models)
        Values_number = np.size(heater, 0)
        Heaters_number = np.size(heater, 1)
        Disturbances_number = np.size(Disturbances, 1)
        Energies_number = np.size(Energies, 1)
    # Initiate estimated Temperatur-Array
    Estimated_temp=np.zeros((Values_number))
    Temperature=[]

    # Read Model-Data
    Factor_matrix_temperature=Params[2]
    Factor_matrix_heater=Params[1]
    Factor_matrix_disturbance=Params[3]
    Factor_matrix_energies=Params[4]
    Model_params=Params[0]
    Fphi=Params[5]

    # Simulate / Iterate through timesteps of the given timeperiod
    for i in range(Values_number):
        if i==0:
            # Initiate the starting Temperature
            X=temp_start;
        else:
            # Set calculated Temperature as State
            X=Temperature
        # Clear Temperature-Value
        Temperature=[]
        #Initiate Heater-Terms
        terms_heater=np.ones((np.size(Fphi,1),1))
        #Iteration through all heater signals
        for j in range(Heaters_number):
            # Calculate the Input-Terms with the measurements of the heater signals
            if Values_number == 1: # (needed for correct indexing)
                terms_heater = np.multiply(terms_heater, np.matmul(np.transpose(Factor_matrix_heater[j]),
                                                                   np.array([[1], [heater[j]]])))
            else:
                terms_heater=np.multiply(terms_heater,np.matmul(np.transpose(Factor_matrix_heater[j]),np.array([[1],[heater[i][j]]])))
        # Calculate the Disturbance-Term with the measurements of the Disturbance signals
        if Disturbances_number == 1: # if there is just one disturbance (needed for correct indexing)
            if Values_number == 1:
                terms_disturbances = (
                    np.matmul(np.transpose(Factor_matrix_disturbance[0]),
                              np.array([[1], Disturbances])))
            else:
                terms_disturbances = (
                    np.matmul(np.transpose(Factor_matrix_disturbance[0]),
                              np.array([[1], Disturbances[i]])))
        else: # if there are multiple disturbances
            terms_disturbances = np.ones((np.size(Fphi, 1), 1))
            for k in range(Disturbances_number):
                if Values_number == 1: # (needed for correct indexing)
                    terms_disturbances = np.multiply(terms_disturbances,
                                                     np.matmul(np.transpose(Factor_matrix_disturbance[k]),
                                                               np.array([[1], [Disturbances[k]]])))
                else:
                    terms_disturbances = np.multiply(terms_disturbances,
                                                     np.matmul(np.transpose(Factor_matrix_disturbance[k]),
                                                               np.array([[1], [Disturbances[i][k]]])))
        # Calculate the Energie-Terms with the measurements of the energie consumption signals
        if Energies_number == 1: # (needed for correct indexing)
            if Values_number == 1: # (needed for correct indexing)
                terms_energies = (np.matmul(np.transpose(Factor_matrix_energies[0]),
                                            np.array([[1], Energies])))
            else:
                terms_energies = (np.matmul(np.transpose(Factor_matrix_energies[0]),
                                            np.array([[1], Energies[i]])))
        else:
            terms_energies = np.ones((np.size(Fphi, 1), 1))
            for n in range(Energies_number):
                if Values_number == 1: # (needed for correct indexing)
                    terms_energies = np.multiply(terms_energies, np.matmul(np.transpose(Factor_matrix_energies[n]),
                                                                           np.array([[1], [Energies[n]]])))
                else:
                    terms_energies = np.multiply(terms_energies, np.matmul(np.transpose(Factor_matrix_energies[n]),
                                                                           np.array([[1], [Energies[i][n]]])))
        # Calculate the Temperature-Terms with the measurement of the current Temperature signals
        if i==0:
            terms_temperature=(np.matmul(np.transpose(Factor_matrix_temperature),np.array([1,X])))
        else:
            terms_temperature=(np.matmul(np.transpose(Factor_matrix_temperature),np.array([1,X[0]])))
        terms_temperature=np.reshape(terms_temperature,(np.size(terms_temperature),1))
        # Calculation of the estimated Temperature for the next time-step
        Temperature=np.matmul(Fphi,(Model_params*terms_heater*terms_disturbances*terms_energies*terms_temperature))
        Temperature=np.reshape(Temperature,1)

        Estimated_temp[i]=Temperature

    return Estimated_temp

def safe_model(filename, zonename, params, fromD, toD):
    # Dump model-data into json-String and write in txt-file
    converted_params = params
    converted_params[0] = params[0].tolist()
    for j in range(1, 6):
        for i in range(0, len(params[j])):
            converted_params[j][i] = params[j][i].tolist()
    converted_params[2] = params[2].tolist()
    converted_params[5] = params[5].tolist()

    timeperiod = fromD[0:4] + '-' + fromD[4:6] + '-' + fromD[6:8] + ':' + toD[0:4] + '-' + toD[4:6] + '-' + toD[6:8]

    Model = {"Name": zonename,
             "Parameter": params[0],
             "Heater": params[1],
             "Temperature": params[2],
             "Disturbances": params[3],
             "Energies":params[4],
             "Phi": params[5],
             "timeperiod": timeperiod}
    print(Model)
    file = open(filename, 'r')
    replace_content = ''
    for line in file:
        if re.search(zonename + ':', line):
            line = line + json.dumps(Model) + '\n'
        replace_content = replace_content + line
    file.close()
    if replace_content.find(zonename + ':') == -1:
        file = open(filename, 'a')
        line = '\n' + zonename + ':\n' + json.dumps(Model) + '\n'
        file.write(line)
    else:
        file = open(filename, 'w')
        file.write(replace_content)
    file.close()

def decomposed_Parameteridentification_with_calibration(heater,temperature,Disturbances,Energies,Outtemperature, set_equalHeaterParameter='false'):
    # sizes calculation
    Values_number = np.size(heater, 0)
    heaters_number = np.size(heater, 1)
    Disturbances_number = np.size(Disturbances, 1)
    Energies_number= np.size(Energies,1)

    # according to number of variables, set size of factor matrices (input for Factors1 function)
    sze = 1 + heaters_number + (2 * Disturbances_number) + Energies_number

    # initialize factor matrices lists
    Factor_matrix_heater = [np.zeros((2, sze))] * heaters_number
    Factor_matrix_temperature = [np.zeros((2, sze))]
    Factor_matrix_Disturbances = [np.zeros((2, sze))] * (Disturbances_number)
    Factor_matrix_Energies = [np.zeros((2, sze))] * Energies_number

    # construct factor matrices
    # Factor matrices corresponding to heaters
    k = 2  # starting position of heater terms
    for i in range(heaters_number):
        Factor_matrix_heater[i] = Factors1(sze, k)
        k = k + 1

    # Factor matrices corresponding to temperatures
    m = 1 + heaters_number + 1  # position of temperature term corresponding to disturbances
    Positions_temperature = np.ones((1 + Disturbances_number))  # initialize position vector for temperatures according
    # to number of disturbances
    for i in range(Disturbances_number):
        Positions_temperature[i + 1] = m
        m = m + 2
    Factor_matrix_temperature = Factors1(sze, Positions_temperature)  # factor matrix corresponding to temperature

    # Factor matrix corresponding to disturbances
    # create positions for disturbances
    ind = [''] * Disturbances_number
    pos_doors = [''] * (Disturbances_number - 1) # Position of binary Disturbances (eg outdoor-Doors)
    for i in range(Disturbances_number):
        if i == 0:
            pos_outdoor_temperature = heaters_number + 3 # Position of outdoor Temperature
        else:
            pos_outdoor_temperature = np.append(pos_outdoor_temperature, pos_outdoor_temperature + 2)
            ind[i] = [2 * i + heaters_number + 2,2 * i + heaters_number + 3]
    ind[0] = pos_outdoor_temperature
    # create factor matrices corresponding to disturbances
    for i in range(Disturbances_number):
        Factor_matrix_Disturbances[i] = Factors1(sze, ind[i])

    for i in range(Energies_number):
        Factor_matrix_Energies[i]=Factors1(sze,1+heaters_number+(2*Disturbances_number)+1+i)

    # Optimization problem for parameter identification:
    # Define Optimization variables (with symbolic programming)
    model_params = SX.sym('L', (sze), 1)
    # Initialize set of output signals, that the model should calculate when identified
    Outtemperatureest = SX.sym('Y', Values_number, 1)
    # Vector/Matrix needed to create a function out of the Matrices and Vectors (just needed for the math in SIOSTA, in more complexe systems this Matrix would define in which function the different terms need to be added)
    Fphi = np.ones((1, sze))

    # Calibration:
    # Initialize Calibration Variables (with symbolic programming)
    variable_number = (1 + heaters_number + Disturbances_number + Energies_number)
    slope = SX.sym('a', variable_number, 1)
    offset = SX.sym('b', variable_number, 1)

    # temperature_calibrated = slope[0] * temperature + offset[0]
    # heater_calibrated = [] * heaters_number
    # for j in range(heaters_number):
    #     heater_calibrated[j] = slope[1 + j] * heater[:][j] + offset[1 + j]
    # Disturbances_calibrated = [] * Disturbances_number
    # for k in range(Disturbances_number):
    #     Disturbances_calibrated = slope[1 + heaters_number + k] * Disturbances[:][k] + offset[1 + heaters_number + k]
    # Energies_calibrated = [] * Energies_number
    # for n in range(Energies_number):
    #     Energies_calibrated = slope[1 + heaters_number + Disturbances_number + n] * Energies[:][n] + offset[1 + heaters_number + Disturbances_number + n]


    # estimated temperatures from the model in terms of unknown parameters
    for i in range(Values_number):
        # Iterate through all measurements
        # initialize the different terms that need to be added
        terms_heaters = np.ones((sze, 1))
        terms_disturbances = np.ones((sze, 1))
        terms_energies = np.ones((sze,1))
        # Calculate the Input-Term with the measurements of the heater signals
        for j in range(heaters_number):
            terms_heaters = np.multiply(terms_heaters, np.matmul(np.transpose(Factor_matrix_heater[j]), np.array(
                [[1], [slope[j + 1] * heater[i][j] + offset[j + 1]]])))
        # Calculate the Disturbance-Term with the measurements of the disturbance signals
        for k in range(Disturbances_number):
            terms_disturbances = np.multiply(terms_disturbances, np.matmul(np.transpose(Factor_matrix_Disturbances[k]),
                                                                           np.array([[1], [
                                                                               slope[1 + j + 1 + k] * Disturbances[i][
                                                                                   k] +
                                                                               offset[1 + j + 1 + k]]])))
        # Calculate the Energie-Term with the measurements of the energie consumption signals
        for n in range(Energies_number):
            terms_energies = np.multiply(terms_energies, np.matmul(np.transpose(Factor_matrix_Energies[n]),
                                                                   np.array([[1], [
                                                                       slope[1 + j + 1 + k + 1 + n] * Energies[i][n]
                                                                       + offset[1 + j + 1 + k + 1 + n]]])))
        # Calculate the Temperature-Term with the measurements of the zonetemperature signals
        terms_temp = (
            np.matmul(np.transpose(Factor_matrix_temperature),
                      np.array([[1], [slope[0] * temperature[i] + offset[0]]])))
        # Output-Equation: Multiply the different Terms with the Parameters that need to be found and all those terms together
        Outtemperatureest[i] = (mtimes(Fphi, (model_params * terms_heaters * terms_disturbances * terms_energies * terms_temp)) - offset[
            0]) / slope[0]

    # Create Cost-Function for Optimization: squared Error between measured Temperature and estimated Temperature by the model need to be minimized
    J = Outtemperature - Outtemperatureest  # estimation error
    Cost_function = mtimes(J.T, J) / 2  # least squares cost function

    # Optimization problem equality constraints
    # the parameter of the Zone- and Outside-Temperature in the disturbance term need to be the same size, but with different algebraic sign

    if set_equalHeaterParameter == 'true':
        lim = SX.sym('lim', 3 * (heaters_number - 1) + Disturbances_number + 3, 1)
    elif set_equalHeaterParameter == 'false':
        lim = SX.sym('lim', Disturbances_number + 3, 1)
    else:
        print('ERROR: equalHeaterParameter-Value must be true or false!')

    if set_equalHeaterParameter == 'true':
        for i in range((heaters_number - 1)):
            lim[i] = model_params[1 + i] - model_params[1 + i + 1]
            lim[(heaters_number - 1) + i] = slope[1 + i] - slope[1 + i + 1]
            lim[2 * (heaters_number - 1) + i] = offset[1 + i] - offset[1 + i + 1]

    k = 1
    for i in range(Disturbances_number):
        if set_equalHeaterParameter == 'true':
            lim[3 * (heaters_number - 1) + i] = model_params[heaters_number + k] + model_params[heaters_number + k + 1]
            k = k + 2
        else:
            lim[i] = model_params[heaters_number + k] + model_params[heaters_number + k + 1]
            k = k + 2

    # Offset Constraint: Offsets need to fully resolve ("source-free" model)
    terms_heaters = np.ones((sze, 1))
    terms_disturbances = np.ones((sze, 1))
    terms_energies = np.ones((sze, 1))
    for j in range(heaters_number):
        terms_heaters = np.multiply(terms_heaters, np.matmul(np.transpose(Factor_matrix_heater[j]), np.array(
            [[1], [offset[j + 1]]])))
    for k in range(Disturbances_number):
        terms_disturbances = np.multiply(terms_disturbances, np.matmul(np.transpose(Factor_matrix_Disturbances[k]),
                                                                       np.array([[1], [offset[1 + j + 1 + k]]])))
    for n in range(Energies_number):
        terms_energies = np.multiply(terms_energies, np.matmul(np.transpose(Factor_matrix_Energies[n]),
                                                               np.array([[1], [offset[1 + j + 1 + k + 1 + n]]])))
    #terms_temp = (np.matmul(np.transpose(Factor_matrix_temperature), np.array([[1], [offset[0]]])))
    if set_equalHeaterParameter == 'true':
        lim[3 * (heaters_number - 1) + Disturbances_number] = (mtimes(Fphi,(model_params * terms_heaters * terms_disturbances * terms_energies )))
    else:
        lim[Disturbances_number] = (mtimes(Fphi, (model_params * terms_heaters * terms_disturbances * terms_energies)))

    #lim[Disturbances_number + 1] = slope[0]

    if set_equalHeaterParameter == 'true':
        lim[3 * (heaters_number - 1) + Disturbances_number +1] = slope[heaters_number + 1] - slope[0]
        lim[3 * (heaters_number - 1) + Disturbances_number + 2] = offset[heaters_number + 1] - offset[0]
    else:
        lim[Disturbances_number + 1] = slope[heaters_number + 1] - slope[0]
        lim[Disturbances_number + 2] = offset[heaters_number + 1] - offset[0]

    # Defining the Non-linear Problem ( x -> optimization variables, f -> Optimization function, g -> boundary function)
    # solving Model-Parameters, slopes and offsets simultaneously
    parameters = vertcat(model_params, slope, offset)
    nlp = {'x': parameters, 'f': Cost_function, 'g': (lim)}
    # Defining the solver to use (ipopt -> interior point optimizer)
    S = nlpsol('S', 'ipopt', nlp)

    # bound constraints of optimization problem
    lb = 1
    lb = np.append(lb, np.zeros((heaters_number))) # lower bound of the heater Parameters
    lb = np.append(lb, -np.inf * (np.ones((2 * Disturbances_number)))) # lower bound of the Disturbance Parameters
    lb = np.append(lb, np.zeros((Energies_number))) # lower bound of the Energy Consumption Parameters
    lb = np.append(lb, 10**(-12) * (np.ones((variable_number)))) # lower boundarys for Slopes
    lb = np.append(lb, -np.inf * (np.ones((variable_number)))) # lower boundarys for offsets

    ub = 1
    ub = np.append(ub, np.inf * np.ones((heaters_number))) # upper bound of the heater Parameters
    ub = np.append(ub, np.inf * (np.ones((2 * Disturbances_number)))) # upper bound of the Disturbance Parameters
    ub = np.append(ub, np.inf * (np.ones((Energies_number)))) # upper bound of the Energy Consumption Parameters
    ub = np.append(ub, np.inf * (np.ones((variable_number)))) # upper boundarys for Slopes
    ub = np.append(ub, np.inf * (np.ones((variable_number)))) # upper boundarys for offsets

    # boundarys for secondary equations (e.g. equality constraints)
    if set_equalHeaterParameter == 'true':
        lbg = np.zeros((3 * (heaters_number - 1) + Disturbances_number + 3, 1))
        ubg = np.zeros((3 * (heaters_number - 1) + Disturbances_number + 3, 1))
    else:
        lbg = np.zeros((Disturbances_number + 3, 1))
        ubg = np.zeros((Disturbances_number + 3, 1))

    # Optimization guess for the solution
    x_0 = vertcat(np.zeros(sze), np.ones(variable_number), np.zeros(variable_number))
    #Optimization problem solution (x0 -> initial guess)
    r = S(x0=(x_0), lbx=(lb), ubx=(ub), lbg=(lbg),
          ubg=(ubg))

    xopt = r['x'] # optimal solution
    print('Parameters :', xopt)
    xopt = xopt.full()

    Fc = xopt[0:sze]  # Fc= model parameter (lambda)
    slope = xopt[sze:(
                sze + variable_number)]  # slope a of the variable calibration (linear transformation): a(0): temperature forecast; a(1): current temperature; a(1+i): heater and disturbances (in that order)
    offset = xopt[(sze + variable_number):(
                sze + 2 * variable_number)]  # offset b of the variable calibration (linear transformation): b(0): temperature forecast; b(1): current temperature; b(1+i): heater and disturbances (in that order)
    # Output: decomposed parameter tensor (representing the values) and Factor matrices (representing the structure)
    return [Fc, Factor_matrix_heater, Factor_matrix_temperature, Factor_matrix_Disturbances, Factor_matrix_Energies, Fphi, slope, offset]

def safe_model_with_calibration(filename, zonename, params, fromD, toD):
    # Dump model-data into json-String and write in txt-file
    converted_params = params
    converted_params[0] = params[0].tolist()
    for j in range(1, 7):
        for i in range(0, len(params[j])):
            converted_params[j][i] = params[j][i].tolist()
    converted_params[2] = params[2].tolist()
    converted_params[5] = params[5].tolist()
    converted_params[6] = params[6].tolist()
    converted_params[7] = params[7].tolist()

    timeperiod = fromD[0:4] + '-' + fromD[4:6] + '-' + fromD[6:8] + ':' + toD[0:4] + '-' + toD[4:6] + '-' + toD[6:8]

    Model = {"Name": zonename,
             "Parameter": params[0],
             "Heater": params[1],
             "Temperature": params[2],
             "Disturbances": params[3],
             "Energies": params[4],
             "Phi": params[5],
             "slopes": params[6],
             "offsets": params[7],
             "timeperiod": timeperiod}

    print(Model)

    file = open(filename, 'r')
    replace_content = ''
    for line in file:
        if re.search(zonename + ':', line):
            line = line + json.dumps(Model) + '\n'
        replace_content = replace_content + line
    file.close()
    if replace_content.find(zonename + ':') == -1:
        file = open(filename, 'a')
        line = '\n' + zonename + ':\n' + json.dumps(Model) + '\n'
        file.write(line)
    else:
        file = open(filename, 'w')
        file.write(replace_content)
    file.close()


def decvalidS_with_calibration(zonename, heater, temp_start, Disturbances, Energies, Params):
    # Check numbers of the different types of signals
    if  heater.ndim == 1:
        # if only the next temperature need to be calculated (for closed-loop simulations)
        Values_number = 1
        Heaters_number = np.size(heater)
        Disturbances_number = np.size(Disturbances)
        Energies_number = np.size(Energies)
    else:
        # if a given timeperiod need to be calculated (for valuating the models)
        Values_number = np.size(heater, 0)
        Heaters_number = np.size(heater, 1)
        Disturbances_number = np.size(Disturbances, 1)
        Energies_number = np.size(Energies, 1)
    # Initiate estimated Temperatur-Array
    Estimated_temp = np.zeros((Values_number))
    Temperature = []
    # Read Model-Data
    Factor_matrix_temperature = Params[2]
    Factor_matrix_heater = Params[1]
    Factor_matrix_disturbance = Params[3]
    Factor_matrix_energies = Params[4]
    Model_params = Params[0]
    Fphi = Params[5]
    slope = Params[6] # slope(0): slope for temperature forecast; slope(1): " for measured temperature; slope(1+n): " for Heater Signals; slope(1+n+m): " for disturbances
    offset = Params[7] # offset(0): offset for temperature forecast; offset(1): " for measured temperature; offset(1+n): " for Heater Signals; offset(1+n+m): " for disturbances

    # Simulate / Iterate through timesteps of the given timeperiod
    for i in range(Values_number):
        if i == 0:
            # Initiate the starting Temperature
            X = temp_start;
        else:
            # Set calculated Temperature as State
            X = Temperature
        # Clear Temperature-Value
        Temperature = []
        # Initiate Heater-Terms
        terms_heater = np.ones((np.size(Fphi, 1), 1))
        # Iteration through all heater signals
        for j in range(Heaters_number):
            # Calculate the Input-Terms with the measurements of the heater signals
            if Values_number == 1: # (needed for correct indexing)
                terms_heater = np.multiply(terms_heater, np.matmul(np.transpose(Factor_matrix_heater[j]),
                                                                   np.array([[1], [
                                                                       slope[1 + j] * heater[j] + offset[1 + j]]])))
            else:
                terms_heater = np.multiply(terms_heater, np.matmul(np.transpose(Factor_matrix_heater[j]),
                                                               np.array([[1], [slope[1+j] * heater[i][j] + offset[1+j]]])))
        # Calculate the Disturbance-Term with the measurements of the Disturbance signals
        if Disturbances_number == 1: # if there is just one disturbance (needed for correct indexing)
            if Values_number == 1:
                terms_disturbances = (
                    np.matmul(np.transpose(Factor_matrix_disturbance[0]),
                              np.array([[1], slope[1 + j + 1] * Disturbances + offset[1 + j + 1]])))
            else:
                terms_disturbances = (
                np.matmul(np.transpose(Factor_matrix_disturbance[0]), np.array([[1], slope[1+j+1] * Disturbances[i] + offset[1+j+1]])))
        else: # if there are multiple disturbances
            terms_disturbances = np.ones((np.size(Fphi, 1), 1))
            for k in range(Disturbances_number):
                if Values_number == 1:
                    terms_disturbances = np.multiply(terms_disturbances,
                                                     np.matmul(np.transpose(Factor_matrix_disturbance[k]),
                                                               np.array([[1], [
                                                                   slope[1 + j + 1 + k] * Disturbances[k] + offset[
                                                                       1 + j + 1 + k]]])))
                else:
                    terms_disturbances = np.multiply(terms_disturbances,
                                                 np.matmul(np.transpose(Factor_matrix_disturbance[k]),
                                                           np.array([[1], [slope[1+j+1+k] * Disturbances[i][k] + offset[1+j+1+k]]])))
        # Calculate the Energie-Terms with the measurements of the energie consumption signals
        if Energies_number == 1: # (needed for correct indexing)
            if Values_number == 1: # (needed for correct indexing)
                terms_energies = (np.matmul(np.transpose(Factor_matrix_energies[0]),
                                            np.array([[1], slope[1 + j + Disturbances_number + 1] * Energies
                                                      + offset[1 + j + Disturbances_number + 1]])))
            else:
                terms_energies=(np.matmul(np.transpose(Factor_matrix_energies[0]),np.array([[1],slope[1 + j + Disturbances_number + 1] * Energies[i]
                                                                       + offset[1 + j + Disturbances_number + 1]])))
        else:
            terms_energies=np.ones((np.size(Fphi,1),1))
            for n in range(Energies_number):
                if Values_number == 1: # (needed for correct indexing)
                    terms_energies = np.multiply(terms_energies, np.matmul(np.transpose(Factor_matrix_energies[n]),
                                                                           np.array([[1], [slope[
                                                                                               1 + j + Disturbances_number + 1 + n] *
                                                                                           Energies[n]
                                                                                           + offset[
                                                                                               1 + j + Disturbances_number + 1 + n]]])))
                else:
                    terms_energies=np.multiply(terms_energies,np.matmul(np.transpose(Factor_matrix_energies[n]),np.array([[1],[slope[1 + j + Disturbances_number + 1 + n] * Energies[i][n]
                                                                       + offset[1 + j + Disturbances_number + 1 + n]]])))
        # Calculate the Temperature-Terms with the measurement of the current Temperature signals
        if i == 0:
            terms_temperature = (np.matmul(np.transpose(Factor_matrix_temperature), np.array([1, slope[0] * X + offset[0]])))
        else:
            terms_temperature = (np.matmul(np.transpose(Factor_matrix_temperature), np.array([1, slope[0] * X[0] + offset[0]])))

        terms_temperature = np.reshape(terms_temperature, (np.size(terms_temperature), 1))
        # Calculation of the estimated Temperature for the next time-step
        Temperature = (np.matmul(Fphi, (Model_params * terms_heater * terms_disturbances * terms_energies * terms_temperature)) - offset[0]) / slope[0]
        Temperature = np.reshape(Temperature, 1)

        Estimated_temp[i] = Temperature
    return Estimated_temp

def DataDump_Validation(zonename, Temperature, Estimated_temp, heater, Disturbances, Energies, fromDv, toDv, fromT, toT):
    import json

    data = {'Temperature': Temperature.tolist(),
            'Estimated_temp': Estimated_temp.tolist(),
            'Heater': heater.tolist(),
            'Disturbances': Disturbances.tolist(),
            'Energies': Energies.tolist()}
    # print(data)

    filename = zonename + ' validation ' + fromDv + '-' + fromT + '--' + toDv + '-' + toT + '.txt'

    file = open('DataDump/' + filename, 'w')
    data_string = json.dumps(data)
    file.write(data_string)
    file.close()

def DataLoad_Validation(zonename, fromDv, toDv, fromT, toT):
    import json

    filename = zonename + ' validation ' + fromDv + '-' + fromT + '--' + toDv + '-' + toT + '.txt'
    file = open('DataDump/' + filename, 'r')
    content = file.read()
    file.close()
    data_dictionary = json.loads(content)
    Temperature = data_dictionary['Temperature']
    Estimated_temp = data_dictionary['Estimated_temp']
    heater = data_dictionary['Heater']
    Disturbances = data_dictionary['Disturbances']
    Energies = data_dictionary['Energies']

    # print('Temperature',Temperature,'Estimated_temp',Estimated_temp,'Setpoint_trend',Setpoint_trend,'Heater_sum',Heater_sum,'Heater_simulation_sum',Heater_simulation_sum,'Disturbances',Disturbances,'Energies',Energies)
    return [Temperature, Estimated_temp, heater, Disturbances, Energies]

    ##PLOT##
def Modelvalidation_plot(zonename, fromDv, toDv, fromT, toT):
    [temperatureout, Estimated_temp, heater, Disturbances, Energies] = DataLoad_Validation(zonename, fromDv, toDv, fromT, toT)
    # Values of the x-axes
    xvals = np.array(range(5, 5 * np.size(temperatureout)+5, 5))/60

    from datetime import datetime
    dates = list([datetime(int(fromDv[0:4]), int(fromDv[4:6]), int(fromDv[6:8]))])
    date0 = datetime(int(fromDv[0:4]), int(fromDv[4:6]), int(fromDv[6:8]))
    n = 0
    for i in range(len(xvals)):
        T = int(fromT) + xvals[i] - n * 24
        if T >= 24:
            n = n + 1
        if i > 0:
            dates.append(datetime(int(fromDv[0:4]), int(fromDv[4:6]), int(fromDv[6:8]) + n))

    # Open sub-plots of different sizes according to the number of disturbances
    if isinstance(np.size(Disturbances), int) == 1:
        fig, (ax0, ax1, ax2, ax3) = plt.subplots(4, 1, figsize=(8,8))
    elif isinstance(np.size(Disturbances), int) != 1:
        fig, (ax0, ax1, ax2, ax3, ax4) = plt.subplots(5, 1, figsize=(8,10))
        ax4.plot(xvals, np.transpose(Disturbances)[1])
    # Plot measured temperature-trend
    ax0.plot(xvals, temperatureout, zorder = 0)
    # plot calculated / simulated temperature-trend
    ax0.plot(xvals, Estimated_temp, zorder=1)

    ax0.legend(['Messung', 'Simulation'], loc='upper right')
    ax0.set_ylabel('Temperatur [°C]')
    # ax0.xlabel('Zeit (min)')
    # ax0.ylabel('Temperatur (C)')
    ax0.set_ylim(13, 25)
    # plot measured heater-trend (input signals)
    ax1.plot(xvals, sum(np.transpose(heater)), zorder = 1)
    ax1.set_ylabel('Stellsignale [-]')
    # plot all disturbance measurements
    for i in range(min(np.size(Disturbances,0), np.size(Disturbances,1))):
        ax2.plot(xvals, np.transpose(Disturbances)[i], zorder = 0)
    ax2.set_ylabel('Störgößen [°C / -]')
    ax2.legend(['Außen-Temperatur [°C]', 'Tor-Signal [0/1]', 'Tor-Signal [0/1]'], loc='upper right')
    # plot energie consumption measurements
    ax3.plot(xvals, Energies)
    #ax3.plot_date(dates, Energies, 'g')
    ax3.set_ylabel('Energieverbrauch\nProduktionsanlagen [-]')
    ax3.set_xlabel('Zeit [h]')
    fig.suptitle(zonename)
    # plt.xlim(0,100)
    # plt.grid(True)
    # plt.xtticks([],xvals)
    # plt.legend()