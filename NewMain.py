### Modelidentification Methods ###
from Control import modelidentification

### Control Methods ###
from Control import Controlfunction

### Plot and Valuation of Models ###
from Control import validation_plot
from Auswertung import Controlvalidation
from Auswertung import ClosedLoopValidation

from Auswertung import MPC_Parameterstudies
from Auswertung import Parameter_Contour
from Auswertung import Parameter_Contour_Plot
from Auswertung import Comparison_of_multiple
from Auswertung import plot_Measurement
from Auswertung import Gasvergleich
from Auswertung import Stellgrößenvergleich
from Auswertung import moving_threshold
from Auswertung import compare_measurements


### Change working-directory to script-path:
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

### CALIBRATED VS NON-CALIBRATED MODEL ###
#modelidentification('Zone 1', 'config.txt', '20211108', '20211115',calibration='false')
#validation_plot('Zone 1', 'config.txt', '20211108', '20211115',calibration='false')
#modelidentification('Zone 1', 'config.txt', '20211108', '20211115',calibration='true')
#validation_plot('Zone 1', 'config.txt', '20211108', '20211115',calibration='true')

#modelidentification('Zone 6','config.txt','20220202','20220203',calibration='true', set_equalHeaterParameter='true')
#modelidentification('Zone 7','config.txt','20220202','20220203',calibration='true', set_equalHeaterParameter='true')

#modelidentification('Zone 10','config.txt','20220131','20220207',calibration='true', set_equalHeaterParameter = 'true')

#modelidentification('Zone 2','config.txt','20220130','20220203',calibration='true', set_equalHeaterParameter = 'true')
#modelidentification('Zone 1','config.txt','20220130','20220203',calibration='true', set_equalHeaterParameter = 'true')
#modelidentification('Zone 5','config.txt','20220130','20220203',calibration='true', set_equalHeaterParameter = 'true')
#validation_plot('System 1', 'config.txt', '20220126','20220202',calibration='true')

#modelidentification('all', 'config.txt','20211113','20211213',calibration='false', set_equalHeaterParameter = 'false')
#validation_plot('all', 'config.txt', '20211213','20211220',calibration='false')

### CONTROL-FUNKTIONS ###
#Controlfunction('Zone 1', 'config.txt', 25, horizon=24, calibration='true')
#Controlfunction('System 1', 'config.txt', 50, horizon=5, calibration='true')
#Controlfunction('all', 'config.txt', 50, horizon=5, calibration='true')

### CONTROL-Algorithm Validation and Plots ###
#Controlvalidation('Zone 1','config.txt', 25,'20220210','20220211','00', '00',horizon=24,calibration='true')
#Controlvalidation('Zone 2','config.txt', 25,'20220210','20220211','00', '00',horizon=24,calibration='true')
#Controlvalidation('Zone 3','config.txt', 25,'20220125','20220125','00', '08',horizon=24,calibration='true')
#Controlvalidation('Zone 4','config.txt', 25,'20220125','20220125','00', '08',horizon=24,calibration='true')
#Controlvalidation('Zone 5','config.txt', 25,'20220125','20220125','00', '08',horizon=24,calibration='true')
#Controlvalidation('Zone 6','config.txt', 1,'20220203','20220203','08', '10',horizon=24,calibration='true')
#Controlvalidation('Zone 7','config.txt', 25,'20220203','20220203','08', '10',horizon=24,calibration='false')
#Controlvalidation('Zone 10','config.txt', 25,'20220210','20220211','00', '00',horizon=24,calibration='true')

ClosedLoopValidation('Zone 1','config.txt',25,'20220210','20220210','00', '12',horizon=48,calibration='true')
#ClosedLoopValidation('Zone 2','config.txt',3,'20220203','20220203','08', '10',horizon=48,calibration='true')
#ClosedLoopValidation('Zone 3','config.txt',3,'20220203','20220203','08', '10',horizon=48,calibration='true')
#ClosedLoopValidation('Zone 4','config.txt',3,'20220203','20220203','08', '10',horizon=48,calibration='true')
#ClosedLoopValidation('Zone 5','config.txt',25,'20211213','20211220','00', '00',horizon=12,calibration='true')
#ClosedLoopValidation('Zone 6','config.txt', 10,'20220210','20220211','00', '00',horizon = 12,calibration='true')
#ClosedLoopValidation('Zone 7','config.txt', 10,'20220210','20220211','00', '00',horizon = 12,calibration='true')
#ClosedLoopValidation('all','config.txt', 25,'20211213','20211220','00', '00',horizon=12,calibration='true')

#plot_closeloop_simulation('Zone 1', '20220210','20220210','00', '01')

#MPC_Parameterstudies('Zone 7','config.txt', '20220210','20220211','04', '12', [25, 50], 24, [24, 48], 25, calibration='true')
#MPC_Parameterstudies('Zone 3','config.txt', '20220125','20220126','00', '08', [1, 2, 3], 48, [24, 48], 3, calibration='true')
#MPC_Parameterstudies('Zone 1','config.txt', '20211213','20211216','00', '00', [100, 25, 10, 5, 3], 24, [6, 12, 24, 48], 25, calibration='true')
#MPC_Parameterstudies('Zone 1','config.txt', '20211213','20211214','00', '00', [100, 3], 6, [6, 12], 25, calibration='true')
#[100, 50, 20, 10, 5, 3, 2, 1, 0.5], 12, [3, 6, 12, 18, 24, 36, 48], 50

#Parameter_Contour('Zone 1','config.txt', '20211213','20211227','00', '00', calibration='true')
#Parameter_Contour_Plot()

#Comparison_of_multiple('Zone 1', 'config.txt', '20210101', '20210129', '00', '00', [3, 25], [48, 48], calibration='true')

#plot_Measurement('System 2', 'config.txt', '20220110', '20220117', '00', '00', calibration='true')
#plot_Measurement('System 2', 'config.txt', '20220210', '20220217', '00', '00', calibration='true')

#plot_Measurement('System 1', 'config.txt', '20220210', '20220216', '00', '00', calibration='true')
#plot_Measurement('System 2', 'config.txt', '20220210', '20220216', '00', '00', calibration='true')
#plot_Measurement('System 3', 'config.txt', '20220210', '20220216', '00', '00', calibration='true')

#plot_Measurement('System 1', 'config.txt', '20220219', '20220226', '00', '00', calibration='true')
#plot_Measurement('System 2', 'config.txt', '20220219', '20220226', '00', '00', calibration='true')
#plot_Measurement('System 3', 'config.txt', '20220219', '20220226', '00', '00', calibration='true')

#plot_Measurement('System 1', 'config.txt', '20220221', '20220228', '00', '00', calibration='true')
#plot_Measurement('System 2', 'config.txt', '20220221', '20220228', '00', '00', calibration='true')
#plot_Measurement('System 3', 'config.txt', '20220221', '20220228', '00', '00', calibration='true')

#moving_threshold('Zone 1', 'config.txt', '20210301', '20210401', '00', '00')

#Gasvergleich('config.txt', '20220204-20220306', '20210301-20210331')
#Stellgrößenvergleich('System 1', 'config.txt', '20220210-20220310', '20210217-20210317')
#Stellgrößenvergleich('System 2', 'config.txt', '20220210-20220310', '20210217-20210317')
#Stellgrößenvergleich('System 3', 'config.txt', '20220210-20220310', '20210217-20210317')

#Stellgrößenvergleich('System 1', 'config.txt', '20220210-20220310', '20210101-20210129')
#Stellgrößenvergleich('System 2', 'config.txt', '20220210-20220310', '20210101-20210129')
#Stellgrößenvergleich('System 3', 'config.txt', '20220210-20220310', '20210101-20210129')

#Stellgrößenvergleich('System 1', 'config.txt', '20220210-20220310', '20210129-20210226')
#Stellgrößenvergleich('System 2', 'config.txt', '20220210-20220310', '20210129-20210226')
#Stellgrößenvergleich('System 3', 'config.txt', '20220210-20220310', '20210129-20210226')

#Stellgrößenvergleich('System 1', 'config.txt', '20220210-20220310', '20210226-20210326')
#Stellgrößenvergleich('System 2', 'config.txt', '20220210-20220310', '20210226-20210326')
#Stellgrößenvergleich('System 3', 'config.txt', '20220210-20220310', '20210226-20210326')

#Stellgrößenvergleich('System 1', 'config.txt', '20220210-20220310', '20201201-20201229')
#Stellgrößenvergleich('System 2', 'config.txt', '20220210-20220310', '20201201-20201229')
#Stellgrößenvergleich('System 3', 'config.txt', '20220210-20220310', '20201201-20201229')

#Stellgrößenvergleich('System 1', 'config.txt', '20220210-20220310', '20210326-20210423')
#Stellgrößenvergleich('System 2', 'config.txt', '20220210-20220310', '20210326-20210423')
#Stellgrößenvergleich('System 3', 'config.txt', '20220210-20220310', '20210326-20210423')

#plot_Measurement('Zone 1', 'config.txt', '20210218', '20210219', '00', '00', calibration='true') # Referenz
#plot_Measurement('Zone 1', 'config.txt', '20220215', '20220216', '00', '00', calibration='true') # 25 / 24
#plot_Measurement('Zone 1', 'config.txt', '20220223', '20220224', '00', '00', calibration='true') # 3 / 48
#plot_Measurement('Zone 1', 'config.txt', '20220308', '20220309', '00', '00', calibration='true') # 10 / 48

#compare_measurements('Zone 1', 'config.txt', '20210217-20210218', '20220215-20220216')
#compare_measurements('Zone 3', 'config.txt', '20210219-20210220', '20220223-20220224')
#compare_measurements('Zone 1', 'config.txt', '20210217-20210218', '20220308-20220309')

#compare_measurements('Zone 3', 'config.txt', '20210217-20210218', '20220215-20220216')
#compare_measurements('Zone 3', 'config.txt', '20220215-20220216', '20220223-20220224')

#compare_measurements('Zone 7', 'config.txt', '20210217-20210218', '20220215-20220216')
#compare_measurements('Zone 7', 'config.txt', '20220215-20220216', '20220223-20220224')

#compare_measurements('Zone 10', 'config.txt', '20210217-20210218', '20220215-20220216')
#compare_measurements('Zone 10', 'config.txt', '20220215-20220216', '20220223-20220224')