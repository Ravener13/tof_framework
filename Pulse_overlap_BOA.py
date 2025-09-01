
import os, glob, time
import numpy as np
from tqdm import tqdm
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import cumtrapz, trapezoid
from scipy.integrate import quad


# =============================================================================
#                           derivate
# =============================================================================

def derivate(xlist,ylist):
    yprime = np.diff(ylist)/np.diff(xlist)
    xprime=[]
    for i in range(len(yprime)):
        xtemp = (xlist[i+1]+xlist[i])/2
        xprime = np.append(xprime,xtemp)
    return xprime, yprime



# =============================================================================
#                           convert_TOF
# =============================================================================

def convert_tof (tof_values, flight_path = 1, result = 'wavelength'):
    conv_res = []
    if result == '':
        print('Please give me the format you want to convert the ToF (wavelength or energy)')
        return
    if type(tof_values) != list:
        if result == 'wavelength':
            conv_res = 3956.03401026312/(flight_path/tof_values)
        if result == 'energy':
            conv_res = ((flight_path/tof_values)/437.393364333048)**2
    else:
        
        if result == 'wavelength':
            for value in tof_values:
                conv_res.append(3956.03401026312/(flight_path/value))
        if result == 'energy':
            for value in tof_values:
                conv_res.append(((flight_path/value)/437.393364333048)**2)
    return conv_res



# =============================================================================
# 
#                          find_nearest_val
#
# takes a float, and retuns the nearest value in a list to that number
# =============================================================================

def find_nearest_val (val_list, value):
    
    index_value = min(enumerate(val_list), key=lambda x: abs(x[1]-value))
    return index_value[0], index_value[1]

# =============================================================================
#                           trapezoid_weight
# =============================================================================
def trapezoid_weight (orig_x, orig_y, point, base_bot_percentage = 32, base_top_percentage = 8, plot = False):
    '''
    takes a curve and gives a weight to their valiues according to a trapezoid shape of neutrons arrival time

    Parameters
    ----------
    curve_values : list
        y-axis values of the curve
    weight_triang : list of 2 int values
        Triangle weights, from the bottom to the top. The default is [0,1].
    weight_top : list of 2 int values
        top of the trapezoid weightening. The default is [1,1].
    zones_percentage : list of 2 int values in percentage
        first value is the triangles, the second is the rectangle. Twice the first value plus the second should give 1.0 . The default is [0.375,0.25].

    Returns
    -------
    weighted_array : list of values
        array weightened with a the shape of a trapezoid.

    '''
    
        # the value should be already in the spectrum

    idx, val = find_nearest_val (orig_x, point)
    
    left_min = idx- int(np.floor(0.005*base_bot_percentage*(len(orig_x)/3)))
    left_max = left_min + int(np.floor(0.005*(base_bot_percentage-base_top_percentage)*(len(orig_x)/3)))
   
    mid_min = left_max
    mid_max = idx + int(np.floor(0.005*base_top_percentage*(len(orig_x)/3)))
    
    right_min = mid_max
    right_max = idx + int(np.floor(0.005*base_bot_percentage*(len(orig_x)/3)))
    
        #this is to deal with the problem of negative and positive indixes for slices
    #left boundary
    
    left_x = orig_x[left_min:left_max]
    left_y = orig_y[left_min:left_max]
    mid_x = orig_x[mid_min:mid_max]
    mid_y = orig_y[mid_min:mid_max]
    right_x = orig_x[right_min:right_max]
    right_y = orig_y[right_min:right_max]
    
    # if len(left_x) == 0:
    #     left_x = np.array([i for i in orig_x if i not in orig_x[left_max:left_min]])
    #     left_y = np.array([i for i in orig_y if i not in orig_y[left_max:left_min]])
    #     print('one')
    # elif len(mid_x) == 0:
    #     mid_x = np.array([i for i in orig_x if i not in orig_x[mid_max:mid_min]])
    #     mid_y = np.array([i for i in orig_y if i not in orig_y[mid_max:mid_min]])
    #     print('two')
    # elif len(right_x) == 0:
    #     right_x = np.array([i for i in orig_x if i not in orig_x[right_max:right_min]])
    #     right_y = np.array([i for i in orig_y if i not in orig_y[right_max:right_min]])
    #     print('three')
        
    w1 = np.linspace(0,0.99,left_max-left_min)
    w2 = np.linspace(1,1,mid_max-mid_min)
    w3 = np.linspace(0.99,0,right_max-right_min)
    
    curve_y = [*(left_y*w1), *(mid_y*w2), *(right_y*w3)]
    curve_x = [*left_x, *mid_x, *right_x]
    
    if plot :
        plt.figure(figsize=(10,6))
        plt.plot(orig_x,orig_y,'g-', linewidth=4.0)
        plt.xlabel(' ToF '+ r'[ms]')
        plt.plot(left_x, left_y*w1, 'r*')
        plt.plot(mid_x, mid_y*w2, 'k*')
        plt.plot(right_x, right_y*w3, 'b*')
        plt.grid(True)

    return np.array(curve_x), np.array(curve_y)


# =============================================================================
#                           normal_weight
# =============================================================================
def normal_weight (orig_x, orig_y, point, base_bot_percentage = 32, base_top_percentage = 8, plot = False):
    '''
    takes a curve and gives a weight to their valiues according to a trapezoid shape of neutrons arrival time

    Parameters
    ----------
    curve_values : list
        y-axis values of the curve
    weight_triang : list of 2 int values
        Triangle weights, from the bottom to the top. The default is [0,1].
    weight_top : list of 2 int values
        top of the trapezoid weightening. The default is [1,1].
    zones_percentage : list of 2 int values in percentage
        first value is the triangles, the second is the rectangle. Twice the first value plus the second should give 1.0 . The default is [0.375,0.25].

    Returns
    -------
    weighted_array : list of values
        array weightened with a the shape of a trapezoid.

    '''
    
        # the value should be already in the spectrum

    idx, val = find_nearest_val (orig_x, point)
    
    left_min = idx- int(np.floor(0.005*base_bot_percentage*(len(orig_x)/3)))
    left_max = left_min + int(np.floor(0.005*(base_bot_percentage-base_top_percentage)*(len(orig_x)/3)))
   
    mid_min = left_max
    mid_max = idx + int(np.floor(0.005*base_top_percentage*(len(orig_x)/3)))
    
    right_min = mid_max
    right_max = idx + int(np.floor(0.005*base_bot_percentage*(len(orig_x)/3)))
    
        #this is to deal with the problem of negative and positive indixes for slices
    #left boundary
    
    left_x = orig_x[left_min:left_max]
    left_y = orig_y[left_min:left_max]
    mid_x = orig_x[mid_min:mid_max]
    mid_y = orig_y[mid_min:mid_max]
    right_x = orig_x[right_min:right_max]
    right_y = orig_y[right_min:right_max]
    
    # if len(left_x) == 0:
    #     left_x = np.array([i for i in orig_x if i not in orig_x[left_max:left_min]])
    #     left_y = np.array([i for i in orig_y if i not in orig_y[left_max:left_min]])
    #     print('one')
    # elif len(mid_x) == 0:
    #     mid_x = np.array([i for i in orig_x if i not in orig_x[mid_max:mid_min]])
    #     mid_y = np.array([i for i in orig_y if i not in orig_y[mid_max:mid_min]])
    #     print('two')
    # elif len(right_x) == 0:
    #     right_x = np.array([i for i in orig_x if i not in orig_x[right_max:right_min]])
    #     right_y = np.array([i for i in orig_y if i not in orig_y[right_max:right_min]])
    #     print('three')
        
    w1 = np.linspace(1,1,left_max-left_min)
    w2 = np.linspace(1,1,mid_max-mid_min)
    w3 = np.linspace(1,1,right_max-right_min)
    
    curve_y = [*(left_y*w1), *(mid_y*w2), *(right_y*w3)]
    curve_x = [*left_x, *mid_x, *right_x]
    
    if plot :
        plt.figure(figsize=(10,6))
        plt.plot(orig_x,orig_y,'g-', linewidth=4.0)
        plt.xlabel(' ToF '+ r'[ms]')
        plt.plot(left_x, left_y*w1, 'r*')
        plt.plot(mid_x, mid_y*w2, 'k*')
        plt.plot(right_x, right_y*w3, 'b*')
        plt.grid(True)

    return np.array(curve_x), np.array(curve_y)


def convert_wvl (wvl_values, flight_path = 1):
    conv_res_tof = []

    if type(wvl_values) != list:
        conv_res_tof = wvl_values / (3956.03401026312/flight_path)

    else:
        for value in wvl_values:
            conv_res_tof.append(value / (3956.03401026312/flight_path))

    return conv_res_tof



        
def dataframe_from_file (file, columns_list, header= None, sep = ' ', names = ['No name'], skiprows=''):
    import pandas as pd
    if '.txt' in file:
        sep = '\t'
    table = pd.read_csv(file,header=header, usecols=columns_list, sep=sep, names=names, skiprows=skiprows)
    return table




def BoaSpectrum():
    spectrum = np.array([[0.78878, 0],[0.81036, 0],[0.83194, 0.00028697],[0.85351, 0.0022001],[0.87509, 0.003635],[0.89667, 0.0011479],[0.91825, 0.0023914],[0.93983, 0.0059307],[0.96141, 0.0084178],
    [0.98298, 0.0046872],[1.0046, 0.0088005],[1.0261, 0.011861],[1.0477, 0.015783],[1.0693, 0.021332],[1.0909, 0.031949],[1.1125, 0.038837],[1.134, 0.040654],[1.1556, 0.040559],[1.1772, 0.044863],
    [1.1988, 0.056342],[1.2203, 0.064664],[1.2419, 0.081596],[1.2635, 0.083126],[1.2851, 0.086857],[1.3067, 0.099675],[1.3282, 0.11259],[1.3498, 0.12598],[1.3714, 0.12627],[1.393, 0.13909],[1.4146, 0.15324],
    [1.4361, 0.16903],[1.4577, 0.17132],[1.4793, 0.18165],[1.5009, 0.18557],[1.5224, 0.1917],[1.544, 0.207],[1.5656, 0.21647],[1.5872, 0.23293],[1.6088, 0.2532],[1.6303, 0.25875],[1.6519, 0.27368],
    [1.6735, 0.29328],[1.6951, 0.29175],[1.7166, 0.30639],[1.7382, 0.3304],[1.7598, 0.34035],[1.7814, 0.35259],[1.803, 0.3722],[1.8245, 0.39344],[1.8461, 0.41305],[1.8677, 0.43132],[1.8893, 0.45169],
    [1.9109, 0.43888],[1.9324, 0.46977],[1.954, 0.46872],[1.9756, 0.50182],[1.9972, 0.52822],[2.0187, 0.51684],[2.0403, 0.54993],[2.0619, 0.56112],[2.0835, 0.57069],[2.1051, 0.58427],[2.1266, 0.61661],
    [2.1482, 0.63775],[2.1698, 0.65209],[2.1914, 0.68672],[2.213, 0.69399],[2.2345, 0.72183],[2.2561, 0.74364],[2.2777, 0.74976],[2.2993, 0.76564],[2.3208, 0.77874],[2.3424, 0.80314],[2.364, 0.80113],
    [2.3856, 0.8391],[2.4072, 0.85498],[2.4287, 0.87632],[2.4503, 0.8789],[2.4719, 0.90511],[2.4935, 0.92797],[2.515, 0.93687],[2.5366, 0.94241],[2.5582, 0.95868],[2.5798, 0.97197],[2.6014, 0.96442],[2.6229, 0.97408],
[2.6445, 0.95973],[2.6661, 0.95782],[2.6877, 0.96872],[2.7093, 0.97063],[2.7308, 0.96719],[2.7524, 0.97092],[2.774, 0.95093],[2.7956, 0.97723],[2.8171, 0.9955],[2.8387, 0.97972],[2.8603, 0.96729],[2.8819, 0.97389],
[2.9035, 0.97054],[2.925, 0.98881],[2.9466, 1],[2.9682, 0.97398],[2.9898, 0.98747],[3.0114, 0.97647],[3.0329, 0.98345],[3.0545, 0.98967],[3.0761, 0.95284],[3.0977, 0.95657],[3.1192, 0.96088],[3.1408, 0.93036],
[3.1624, 0.92682],[3.184, 0.90893],[3.2056, 0.9207],[3.2271, 0.9097],[3.2487, 0.90922],[3.2703, 0.90951],[3.2919, 0.87861],[3.3134, 0.88894],[3.335, 0.89277],[3.3566, 0.89573],[3.3782, 0.87278],[3.3998, 0.84484],
[3.4213, 0.84838],[3.4429, 0.83834],[3.4645, 0.85058],[3.4861, 0.83155],[3.5077, 0.82944],[3.5292, 0.82016],[3.5508, 0.81462],[3.5724, 0.80486],
[3.594, 0.81022],[3.6155, 0.78764],[3.6371, 0.78152],[3.6587, 0.74699],[3.6803, 0.7444],[3.7019, 0.73924],[3.7234, 0.7335],[3.745, 0.72087],[3.7666, 0.74536],[3.7882, 0.70471],[3.8098, 0.70719],[3.8313, 0.69256],[3.8529, 0.685],[3.8745, 0.68787],[3.8961, 0.66807],[3.9176, 0.65611],[3.9392, 0.64243],[3.9608, 0.64033],
[3.9824, 0.62244],[4.004, 0.60245],[4.0255, 0.59614],[4.0471, 0.60321],[4.0687, 0.61488],[4.0903, 0.63889],[4.1118, 0.62694],[4.1334, 0.63277],[4.155, 0.62598],[4.1766, 0.61134],[4.1982, 0.61909],[4.2197, 0.60101],[4.2413, 0.58561],
[4.2629, 0.59843],[4.2845, 0.5661],[4.3061, 0.57375],[4.3276, 0.56447],[4.3492, 0.54285],[4.3708, 0.53329],[4.3924, 0.52831],[4.4139, 0.53501],[4.4355, 0.51645],[4.4571, 0.50344],[4.4787, 0.52583],[4.5003, 0.49168],[4.5218, 0.48297],
[4.5434, 0.48603],[4.565, 0.47169],[4.5866, 0.46824],[4.6082, 0.46642],[4.6297, 0.45131],[4.6513, 0.46068],[4.6729, 0.46384],[4.6945, 0.46432],[4.716, 0.46709],[4.7376, 0.45418],[4.7592, 0.44777],[4.7808, 0.44691],[4.8024, 0.44146],
[4.8239, 0.43381],[4.8455, 0.4252],[4.8671, 0.42166],[4.8887, 0.41955],[4.9102, 0.41974],[4.9318, 0.40205],[4.9534, 0.40549],[4.975, 0.40348],[4.9966, 0.40501],[5.0181, 0.38789],[5.0397, 0.38215],[5.0613, 0.37832],[5.0829, 0.37383],
[5.1045, 0.37306],[5.126, 0.37153],[5.1476, 0.37871],[5.1692, 0.36598],[5.1908, 0.36723],[5.2123, 0.34561],[5.2339, 0.35259],[5.2555, 0.36187],[5.2771, 0.34207],[5.2987, 0.33518],[5.3202, 0.32552],[5.3418, 0.33337],[5.3634, 0.32122],
[5.385, 0.32236],[5.4065, 0.31663],[5.4281, 0.31328],[5.4497, 0.29663],[5.4713, 0.30036],[5.4929, 0.28716],[5.5144, 0.2908],[5.536, 0.28525],[5.5576, 0.28372],[5.5792, 0.27884],[5.6008, 0.27874],[5.6223, 0.26956],[5.6439, 0.26401],
[5.6655, 0.26564],[5.6871, 0.26315],[5.7086, 0.2598],[5.7302, 0.24928],[5.7518, 0.2511],[5.7734, 0.2401],[5.795, 0.2467],[5.8165, 0.24584],[5.8381, 0.2444],[5.8597, 0.238],[5.8813, 0.22747],[5.9029, 0.22958],[5.9244, 0.22891],[5.946, 0.21848],[5.9676, 0.21599],[5.9892, 0.21925],
[6.0107, 0.22164],[6.0323, 0.20595],[6.0539, 0.20949],[6.0755, 0.20212],[6.0971, 0.20078],[6.1186, 0.2026],[6.1402, 0.19581],[6.1618, 0.20212],[6.1834, 0.19093],[6.2049, 0.19208],[6.2265, 0.18089],[6.2481, 0.18462],[6.2697, 0.18797],[6.2913, 0.17467],[6.3128, 0.17324],[6.3344, 0.1762],[6.356, 0.17658],[6.3776, 0.17897],
[6.3992, 0.17716],[6.4207, 0.17381],[6.4423, 0.16549],[6.4639, 0.16797],[6.4855, 0.16003],[6.507, 0.17008],[6.5286, 0.15956],[6.5502, 0.15678],[6.5718, 0.15487],[6.5934, 0.14942],[6.6149, 0.14626],[6.6365, 0.14999],[6.6581, 0.14224],
[6.6797, 0.13631],[6.7013, 0.15171],[6.7228, 0.13277],[6.7444, 0.13029],[6.766, 0.13335],[6.7876, 0.1299],[6.8091, 0.13134],[6.8307, 0.12349],[6.8523, 0.12388],[6.8739, 0.13],[6.8955, 0.11661],[6.917, 0.12789],[6.9386, 0.11861],
[6.9602, 0.11144],[6.9818, 0.11861],[7.0033, 0.11536],[7.0249, 0.11909],[7.0465, 0.10771],[7.0681, 0.1079],[7.0897, 0.10321],[7.1112, 0.10943],[7.1328, 0.10207],[7.1544, 0.10312],[7.176, 0.10522],[7.1976, 0.10446],[7.2191, 0.094318],
[7.2407, 0.092883],[7.2623, 0.092787],[7.2839, 0.096518],[7.3054, 0.084178],[7.327, 0.093361],[7.3486, 0.085996],[7.3702, 0.077578],[7.3918, 0.082074],[7.4133, 0.081596],[7.4349, 0.083604],[7.4565, 0.073752],[7.4781, 0.078917],
[7.4997, 0.07576],[7.5212, 0.081883],[7.5428, 0.075378],[7.5644, 0.071456],[7.586, 0.068299],[7.6075, 0.067056],[7.6291, 0.072126],[7.6507, 0.069734],[7.6723, 0.065812],[7.6939, 0.06476],[7.7154, 0.066099],[7.737, 0.063516],
[7.7586, 0.066577],[7.7802, 0.062847],[7.8017, 0.064856],[7.8233, 0.062082],[7.8449, 0.053664],[7.8665, 0.062368],[7.8881, 0.058829],[7.9096, 0.056629],[7.9312, 0.054333],[7.9528, 0.055768],[7.9744, 0.055385],[7.996, 0.052898],
[8.0175, 0.053472],[8.0391, 0.049359],[8.0607, 0.049455],[8.0823, 0.047446],[8.1038, 0.049742],[8.1254, 0.050316],[8.147, 0.050316],[8.1686, 0.043715],[8.1902, 0.045724],[8.2117, 0.040846],[8.2333, 0.040176],[8.2549, 0.047159],
[8.2765, 0.045437],[8.2981, 0.04075],[8.3196, 0.037498],[8.3412, 0.046298],[8.3628, 0.036254],[8.3844, 0.035967],[8.4059, 0.037115],[8.4275, 0.033384],[8.4491, 0.038359],[8.4707, 0.039219],[8.4923, 0.034628],[8.5138, 0.037785],
[8.5354, 0.034915],[8.557, 0.037306],[8.5786, 0.033863],[8.6001, 0.035202],[8.6217, 0.03568],[8.6433, 0.034628],[8.6649, 0.026593],[8.6865, 0.032523],[8.708, 0.032045],[8.7296, 0.026401],[8.7512, 0.027071],[8.7728, 0.027071],
[8.7944, 0.026019],[8.8159, 0.028506],[8.8375, 0.025062],[8.8591, 0.025732],[8.8807, 0.025732],[8.9022, 0.028601],[8.9238, 0.026306],[8.9454, 0.027071],[8.967, 0.023723],[8.9886, 0.022958],
[9.0101, 0.025062],[9.0317, 0.026019],[9.0533, 0.022288],[9.0749, 0.021523],[9.0964, 0.024297],[9.118, 0.02181],[9.1396, 0.017697],[9.1612, 0.022192],[9.1828, 0.018557],[9.2043, 0.019514],
[9.2259, 0.020566],[9.2475, 0.020758],[9.2691, 0.019992],[9.2907, 0.021714],[9.3122, 0.01961],[9.3338, 0.020662],[9.3554, 0.015783],[9.377, 0.020758],[9.3985, 0.020088],[9.3985, 0.020088],
    ])
    return spectrum


def IconSpectrum():
    spectrum = np.array([[0.39199, 0.34942],[0.4113, 0.34168],[0.43061, 0.33452],[0.44992, 0.31243],[0.46924, 0.27315],[0.48855, 0.2632],[0.50786, 0.244],[0.52717, 0.24753],
[0.54648, 0.24834],[0.56579, 0.22906],[0.5851, 0.24989],[0.60441, 0.23223],[0.62373, 0.24347],[0.64304, 0.2528],[0.66235, 0.26048],[0.68166, 0.26504],[0.70097, 0.26965],
[0.72028, 0.28695],[0.73959, 0.28439],[0.7589, 0.30345],[0.77821, 0.3461],[0.79753, 0.35111],[0.81684, 0.37839],[0.83615, 0.40014],[0.85546, 0.41165],[0.87477, 0.43106],[0.89408, 0.46219],
[0.91339, 0.49108],[0.9327, 0.48525],[0.95202, 0.50495],[0.97133, 0.53886],[0.99064, 0.55752],[1.0099, 0.58315],[1.0293, 0.60575],[1.0486, 0.61994],[1.0679, 0.66018],
[1.0872, 0.697],[1.1065, 0.71238],[1.1258, 0.73776],[1.1451, 0.75696],[1.1644, 0.76682],[1.1837, 0.78536],[1.2031, 0.80916],[1.2224, 0.83415],[1.2417, 0.8498],[1.261, 0.87663],
[1.2803, 0.87439],[1.2996, 0.90201],[1.3189, 0.90162],[1.3382, 0.91556],[1.3576, 0.92227],[1.3769, 0.93095],[1.3962, 0.97554],[1.4155, 0.96251],[1.4348, 0.99356],
[1.4541, 0.96146],[1.4734, 0.9754],[1.4927, 0.98961],[1.512, 1],[1.5314, 0.96659],[1.5507, 0.98724],[1.57, 0.9996],[1.5893, 0.96804],[1.6086, 0.99369],[1.6279, 0.9679],[1.6472, 0.9804],[1.6665, 0.97317],[1.6858, 0.95488],
[1.7052, 0.97356],[1.7245, 0.97593],[1.7438, 0.95225],[1.7631, 0.92173],[1.7824, 0.91226],[1.8017, 0.91174],[1.821, 0.91147],[1.8403, 0.89674],[1.8596, 0.89359],[1.879, 0.8928],[1.8983, 0.90595],
[1.9176, 0.83163],[1.9369, 0.86281],[1.9562, 0.84978],[1.9755, 0.82571],[1.9948, 0.80966],[2.0141, 0.83216],[2.0334, 0.81453],[2.0528, 0.81532],[2.0721, 0.80559],
[2.0914, 0.824],[2.1107, 0.79796],[2.13, 0.78309],[2.1493, 0.79296],[2.1686, 0.78599],[2.1879, 0.81545],[2.2072, 0.80769],[2.2266, 0.78217],[2.2459, 0.77494],[2.2652, 0.77902],
[2.2845, 0.75192],[2.3038, 0.76126],[2.3231, 0.75337],[2.3424, 0.73443],[2.3617, 0.74679],[2.381, 0.73285],[2.4004, 0.75074],[2.4197, 0.73666],[2.439, 0.71956],
[2.4583, 0.7318],[2.4776, 0.72706],[2.4969, 0.71812],[2.5162, 0.68142],[2.5355, 0.70536],[2.5548, 0.72154],[2.5742, 0.71614],[2.5935, 0.72811],[2.6128, 0.69746],[2.6321, 0.68536],
[2.6514, 0.70023],[2.6707, 0.69089],[2.69, 0.70601],[2.7093, 0.68826],[2.7286, 0.66603],[2.748, 0.69483],[2.7673, 0.67313],[2.7866, 0.66419],[2.8059, 0.66787],[2.8252, 0.65169],[2.8445, 0.65945],
[2.8638, 0.67024],[2.8831, 0.65314],[2.9024, 0.63854],[2.9218, 0.6509],[2.9411, 0.65406],[2.9604, 0.63946],[2.9797, 0.65011],[2.999, 0.63722],[3.0183, 0.6317],[3.0376, 0.64025],
[3.0569, 0.60657],[3.0762, 0.60552],[3.0956, 0.59592],[3.1149, 0.62301],[3.1342, 0.61026],[3.1535, 0.62551],[3.1728, 0.59986],[3.1921, 0.58513],[3.2114, 0.57658],[3.2307, 0.55948],
[3.25, 0.56908],[3.2694, 0.5604],[3.2887, 0.56395],[3.308, 0.53712],[3.3273, 0.53081],[3.3466, 0.51792],[3.3659, 0.52199],[3.3852, 0.54054],[3.4045, 0.52594],[3.4238, 0.50818],
[3.4432, 0.50082],[3.4625, 0.49122],[3.4818, 0.47096],[3.5011, 0.4707],[3.5204, 0.46517],[3.5397, 0.45452],[3.559, 0.42703],[3.5783, 0.39125],[3.5976, 0.41571],[3.617, 0.41348],
[3.6363, 0.45517],[3.6556, 0.46728],[3.6749, 0.45754],[3.6942, 0.43939],[3.7135, 0.45465],[3.7328, 0.43505],[3.7521, 0.43373],[3.7714, 0.43189],[3.7908, 0.43781],[3.8101, 0.4457],[3.8294, 0.4019],
[3.8487, 0.40098],[3.868, 0.39743],[3.8873, 0.39638],[3.9066, 0.39454],[3.9259, 0.37928],[3.9452, 0.39914],[3.9646, 0.38967],[3.9839, 0.36126],[4.0032, 0.35152],[4.0225, 0.35994],
[4.0418, 0.33192],[4.0611, 0.33732],[4.0804, 0.3431],[4.0997, 0.36783],[4.119, 0.36191],[4.1384, 0.35915],[4.1577, 0.34574],[4.177, 0.35442],[4.1963, 0.36113],[4.2156, 0.34074],
[4.2349, 0.36099],[4.2542, 0.35455],[4.2735, 0.34218],[4.2929, 0.36191],[4.3122, 0.32337],[4.3315, 0.32614],[4.3508, 0.3218],[4.3701, 0.3214],[4.3894, 0.31535],[4.4087, 0.30877],
[4.428, 0.31404],[4.4473, 0.30917],[4.4667, 0.32364],[4.486, 0.31838],[4.5053, 0.29996],[4.5246, 0.29562],[4.5439, 0.27707],[4.5632, 0.27878],[4.5825, 0.26958],[4.6018, 0.26247],
[4.6211, 0.27747],[4.6405, 0.24406],[4.6598, 0.27168],[4.6791, 0.25208],[4.6984, 0.26195],[4.7177, 0.2484],[4.737, 0.27523],[4.7563, 0.25524],[4.7756, 0.2434],[4.7949, 0.24037],
[4.8143, 0.24077],[4.8336, 0.22064],[4.8529, 0.21972],[4.8722, 0.22906],[4.8915, 0.21341],[4.9108, 0.21341],[4.9301, 0.22617],[4.9494, 0.23183],[4.9687, 0.21946],[4.9881, 0.21551],
[5.0074, 0.22433],[5.0267, 0.19684],[5.046, 0.20946],[5.0653, 0.2067],[5.0846, 0.20368],[5.1039, 0.20775],[5.1232, 0.20407],[5.1425, 0.19657],[5.1619, 0.21025],[5.1812, 0.20841],
[5.2005, 0.18697],[5.2198, 0.20354],[5.2391, 0.19447],[5.2584, 0.18592],[5.2777, 0.20946],[5.297, 0.20736],[5.3163, 0.19407],[5.3357, 0.18802],[5.355, 0.19947],[5.3743, 0.19236],
[5.3936, 0.20447],[5.4129, 0.17724],[5.4322, 0.19565],[5.4515, 0.17079],[5.4708, 0.17408],[5.4901, 0.17487],[5.5095, 0.1846],[5.5288, 0.17987],[5.5481, 0.18815],[5.5674, 0.15514],[5.5867, 0.16382],
[5.606, 0.16645],[5.6253, 0.15974],[5.6446, 0.15014],[5.6639, 0.15567],[5.6833, 0.16251],[5.7026, 0.18276],[5.7219, 0.15277],[5.7412, 0.15567],[5.7605, 0.14961],[5.7798, 0.14462],[5.7991, 0.1412],[5.8184, 0.12475],[5.8377, 0.14672],[5.8571, 0.1412],[5.8764, 0.13659],[5.8957, 0.12923],[5.915, 0.12883],[5.9343, 0.11528],[5.9536, 0.11502],
[5.9729, 0.13357],[5.9922, 0.13554],[6.0115, 0.12239],[6.0309, 0.11318],[6.0502, 0.11962],[6.0695, 0.11436],[6.0888, 0.1095],[6.1081, 0.10345],[6.1274, 0.11094],[6.1467, 0.11713],
[6.166, 0.10187],[6.1853, 0.10594],[6.2047, 0.10805],[6.224, 0.12002],[6.2433, 0.096869],[6.2626, 0.095685],[6.2819, 0.077796],[6.3012, 0.095027],[6.3205, 0.089634],[6.3398, 0.10371],
[6.3591, 0.091081],[6.3785, 0.088845],[6.3978, 0.084373],[6.4171, 0.078322],[6.4364, 0.098447],[6.4557, 0.084241],[6.475, 0.09016],[6.4943, 0.074376],[6.5136, 0.082531],
[6.5329, 0.10397],[6.5523, 0.08845],[6.5716, 0.067273],[6.5909, 0.081084],[6.6102, 0.089503],[6.6295, 0.073192],[6.6488, 0.06872],[6.6681, 0.088713],[6.6874, 0.079243],[6.7067, 0.067536],[6.7261, 0.078322],[6.7454, 0.079374],[6.7647, 0.073718],
[6.784, 0.068457],[6.8033, 0.071087],[6.8226, 0.050042],[6.8419, 0.057145],[6.8612, 0.064511],[6.8805, 0.067141],[6.8999, 0.055435],[6.9192, 0.05504],[6.9385, 0.060696],[6.9578, 0.062406],
[6.9771, 0.059249],[6.9964, 0.063985],[7.0157, 0.044912],[7.035, 0.059907],[7.0543, 0.041623],[7.0737, 0.051752],[7.093, 0.032679],[7.1123, 0.057145],[7.1316, 0.065826],
[7.1509, 0.052541],[7.1702, 0.061617],[7.1895, 0.063327],[7.2088, 0.05675],[7.2281, 0.053462],[7.2475, 0.055829],[7.2668, 0.054119],[7.2861, 0.055698],[7.3054, 0.045306],[7.3247, 0.048858],[7.344, 0.045964],
[7.3633, 0.040176],[7.3826, 0.054119],[7.402, 0.056224],[7.4213, 0.049647],[7.4406, 0.0482],[7.4599, 0.04307],[7.4792, 0.040571],[7.4985, 0.038335],[7.5178, 0.042149],[7.5371, 0.054645],[7.5564, 0.02768],
[7.5758, 0.038072],[7.5951, 0.022024],[7.6144, 0.035441],[7.6337, 0.032284],[7.653, 0.040308],[7.6723, 0.018604],[7.6916, 0.035441],[7.7109, 0.046096],[7.7302, 0.031758],[7.7496, 0.037414],
[7.7689, 0.038466],[7.7882, 0.036756],[7.8075, 0.033073],[7.8268, 0.028996],[7.8461, 0.019525],[7.8654, 0.035046],[7.8847, 0.039124],[7.904, 0.03623],[7.9234, 0.0092653],
[7.9427, 0.029522],[7.962, 0.03623],[7.9813, 0.016894],[8.0006, 0.018999],[8.0199, 0.02597],[8.0392, 0.032284],[8.0585, 0.0075554],[8.0778, 0.038072],[8.0972, 0.015579],
[8.1165, 0.016894],[8.1358, 0.019525],[8.1551, 0.020709],[8.1744, 0.028338],[8.1937, 0.02597],[8.213, 0.025576],[8.2323, 0.009923],[8.2516, 0.023471],[8.271, 0.012685],[8.2903, 0.014001],
[8.3096, 0.030969],[8.3289, 0.019525],[8.3482, 0.018341],[8.3675, 0.028996],[8.3868, 0.022814],[8.4061, 0.011501],[8.4254, 0.01479],[8.4448, 0.022945],[8.4641, 0.0021624],
[8.4834, 0.024787],[8.5027, 0.0054508],[8.522, 0.036493],[8.5413, 0.0063715],[8.5606, 0.016368],[8.5799, 0.0032147],[8.5992, 0.019394],[8.6186, 0.013211],[8.6379, 0.012422],[8.6572, 0.015316],
[8.6765, 0.01821],[8.6958, 0.027944],[8.7151, 0.0011101],[8.7344, 0.013738],[8.7537, 0.015579],[8.773, 0.0021624],[8.7924, 0.009923],[8.8117, 0.0098],[8.831, 0.0097],
[8.8503, 0.0096],[8.8696, 0.0095],[8.8889, 0.0094],[8.9082, 0.0093],[8.9275, 0.0092],[8.9468, 0.0091],[8.9662, 0.009],[8.9855, 0.0089],[9.0048, 0.0088],[9.0241, 0.0087],
[9.0434, 0.0086],[9.0627, 0.0085],[9.082, 0.0084],[9.1013, 0.0083],[9.1206, 0.0082],[9.14, 0.0081],[9.1593, 0.008],[9.1786, 0.0079],[9.1979, 0.0078],[9.2172, 0.0077],
[9.2365, 0.0076],[9.2558, 0.0075],[9.2751, 0.0074],[9.2944, 0.0073],[9.3138, 0.0072],[9.3331, 0.0071],[9.3524, 0.007],[9.3717, 0.0069],[9.391, 0.0068],[9.4103, 0.0067],[9.4296, 0.0066],
[9.4489, 0.0065],[9.4682, 0.0064],[9.4876, 0.0063],[9.5069, 0.0062],[9.5262, 0.0061],[9.5455, 0.006],[9.5648, 0.0059],[9.5841, 0.0058],[9.6034, 0.0057],[9.6227, 0.0056],
[9.642, 0.0055],[9.6614, 0.0054],[9.6807, 0.0053],[9.7, 0.0052],[9.7193, 0.0051],[9.7386, 0.005],[9.7579, 0.0049],[9.7772, 0.0048],[9.7965, 0.0047],[9.8158, 0.0046],[9.8352, 0.0045],[9.8545, 0.0044],
[9.8738, 0.0043],[9.8931, 0.0042]])
    return spectrum


# =============================================================================================================================================================
#                           Initial curves and data
# =============================================================================================================================================================

    # load IMAT CS values
CS_PE_IMAT = r"C:\Users\carreon_r\Desktop\CS_PE_IMAT.txt"
table_cs_imat = np.array(dataframe_from_file (CS_PE_IMAT, [0,1], sep = ',', header = None,  names = ['wvl','CS_PE'], skiprows = None))
# CS_PE_BOA = r"C:\Users\carreon_r\Desktop\CS_PE_BOA.txt"
# table_cs_boa = np.array(dataframe_from_file (CS_PE_BOA, [0,1], sep = ',', header = None,  names = ['wvl','CS_PE'], skiprows = None))

    # create arrays from IMAT original data
cs_arr = np.array(table_cs_imat)
cs_arr [:,0] =  convert_wvl (cs_arr [:,0], flight_path = 5.5)

    # load BOA original spectrum and create arrays (intensity vs tof)
spectrum = BoaSpectrum()
x = spectrum[:,0]
y = spectrum[:,1]
x = convert_wvl (x, flight_path = 5.5)

    # interpolate the missing values in the IMAT cross section arrays. X_CS = = x_boa
cs_x = x
cs_y = np.interp(cs_x, cs_arr[:,0], cs_arr[:,1])

    # create a simple function (wavelength dependent) for the detector efficiency
det_x = [0,0.1,0.2,0.4,0.6,0.8,1,1.2,1.45,1.7,2,2.5,3,3.5,4,4.5,5.5,6,7,8,9,10]
det_x = convert_wvl (det_x, flight_path = 5.5)
det_y = [0,0.04,0.08,0.20,0.64,0.74,0.78,0.82,0.855,0.88,0.90,0.92,0.935,0.945,0.955,0.97,0.975,0.98,0.99,1,1,1]

    # # interpolate the missing values for the detextor efficiency


    # interpolate the missing values. x_detector == x_boa
det_eff_x = x
det_eff_y = np.interp(det_eff_x, det_x, det_y)

    # enter constants
T=0.0113636 # pulse period in ms
pe_conc = 8.07245975939479E+22 #1/cm3
#pe_conc = 3.95035264821447E+22 #1/cm3
thick = 0.21 #cm
barns = 1e24 #cm2

    # stitch arrays in to have a -T pulse, 0 Pulse and T pulse
x = np.array([*x-T, *x, *x+T])
y = np.array([*y,*y,*y])

    # ditto for cross sections
cs_y=cs_y/barns
cs_x = np.array([*cs_x-T, *cs_x, *cs_x+T])
cs_y = np.array([*cs_y,*cs_y,*cs_y])

    # ditto for detector efficiency
det_eff_x = np.array([*det_eff_x-T,*det_eff_x,*det_eff_x+T])
det_eff_y = np.array([*det_eff_y,*det_eff_y,*det_eff_y])


# plt.figure(figsize=(10,6))
# plt.plot(cs_x,cs_y,'bo', linewidth=4.0)
# plt.xlabel(' ToF '+ r'[ms]')
# plt.grid(True)

plt.figure(figsize=(10,6))
plt.plot(x,y,'g-', linewidth=4.0)
plt.xlabel(' ToF '+ r'[ms]')
plt.grid(True)

# =============================================================================================================================================================
#                           SQUARED PULSE
# =============================================================================================================================================================

def squared_pulse (points):
    sigma_eff = []
    for t_det in points:
        
        integral_ioeff=[]
        integral_ieff =[]
        
        for i in range(-1,2,1):
            
            bound_max = i*T
            bound_min = i*T + 0.20*T
            
            i_o = y[np.logical_and(x >= (t_det - bound_min), x <= (t_det-bound_max))]
            f_e = np.exp(-cs_y[np.logical_and(x >= (t_det - bound_min), x <= (t_det-bound_max))]*pe_conc*thick)
            det_eff = det_eff_y[np.logical_and(x >= (t_det - bound_min), x <= (t_det-bound_max))]
            
            x_new = x[np.logical_and(x >= (t_det - bound_min), x <= (t_det-bound_max))]
            
            integral_ieff.append(trapezoid(i_o*f_e*det_eff))
            integral_ioeff.append(trapezoid(i_o*det_eff))
            
            # idx, val = find_nearest_val (x, t_det)
            # plt.plot (x[idx],y[idx], 'bo', linewidth=6.0)
            # plt.plot(x_new, i_o , 'r.', linewidth=2.0)
    
        i_eff = (sum(integral_ieff))
        io_eff = (sum(integral_ioeff))
    
        sigma_eff.append(-(1/(pe_conc*thick))*np.log(i_eff/io_eff)*barns)
    
    sigma_real = np.interp(points, cs_x, cs_y*barns)
        
    x_wvl = convert_tof (points, flight_path = 5.5, result = 'wavelength')
        
    plt.figure(figsize=(10,6))
    plt.ylabel(' Effective Cross-Section '+ r'[barns]')
    plt.plot(x_wvl, sigma_real, 'b', linewidth = 4.0)
    plt.plot(x_wvl, sigma_eff, 'ko', linewidth = 1.5)
    plt.xlabel(' Wavelenth '+ r'[$\AA$]')
    plt.grid(True)
    
    return


# =============================================================================================================================================================
#                           SQUARED PULSE INVERSE
# =============================================================================================================================================================

def squared_pulse_inverse (points):
    sigma_eff = []
    for t_det in points:
        
        integral_ioeff=[]
        integral_ieff =[]
        
        for i in range(-1,2,1):
            
            bound_max = i*T + 0.20*T
            bound_min = i*T 
            
            i_o = y[np.logical_and(x >= (t_det - bound_max), x <= (t_det-bound_min))]
            f_e = np.exp(-cs_y[np.logical_and(x >= (t_det - bound_max), x <= (t_det-bound_min))]*pe_conc*thick)
            det_eff = det_eff_y[np.logical_and(x >= (t_det - bound_max), x <= (t_det-bound_min))]
            
            x_new = x[np.logical_and(x >= (t_det - bound_max), x <= (t_det-bound_min))]
            
            integral_ieff.append(trapezoid(i_o*f_e*det_eff))
            integral_ioeff.append(trapezoid(i_o*det_eff))
            
            idx, val = find_nearest_val (x, t_det)
            plt.plot (x[idx],y[idx], 'bo', linewidth=6.0)
            plt.plot(x_new, i_o , 'r.', linewidth=2.0)
    
        i_eff = (sum(integral_ieff))
        io_eff = (sum(integral_ioeff))
    
        sigma_eff.append(-(1/(pe_conc*thick))*np.log(i_eff/io_eff)*barns)
    
    sigma_real = np.interp(points, cs_x, cs_y*barns)
        
    x_wvl = convert_tof (points, flight_path = 5.5, result = 'wavelength')
        
    plt.figure(figsize=(10,6))
    plt.ylabel(' Effective Cross-Section '+ r'[barns]')
    plt.plot(x_wvl, sigma_real, 'b', linewidth = 4.0)
    plt.plot(x_wvl, sigma_eff, 'ko', linewidth = 1.5)
    plt.xlabel(' Wavelenth '+ r'[$\AA$]')
    plt.grid(True)
    
    return


# =============================================================================================================================================================
#                           TRAPEZOID PULSE
# =============================================================================================================================================================

def trapezoid_pulse (points):
    sigma_eff = []
    for t_det in points:
        
        integral_ioeff=[]
        integral_ieff =[]
        
        for i in range(-1,2,1):
            
                # if limits do not change sign
            bound_min_left = i*T + 0.32*T
            bound_max_left = i*T + 0.20*T
            bound_max_mid = i*T + 0.12*T
            bound_max_right = i*T
        
            
            left = y[np.logical_and(x >= (t_det - bound_min_left), x < (t_det-bound_max_left))]
            p_left = left* np.linspace(0,0.99,len(left))
            mid = y[np.logical_and(x >= (t_det - bound_max_left), x <= (t_det-bound_max_mid))]
            p_mid = mid
            right = y[np.logical_and(x > (t_det - bound_max_mid), x <= (t_det-bound_max_right))]
            p_right = right* np.linspace(0.99,0,len(right))
            
            pulse_trap = np.array(list(p_left) + list(p_mid) + list(p_right))
            
            cs =  cs_y[np.logical_and(cs_x >= (t_det - bound_min_left), cs_x < (t_det-bound_max_right))]
            
            det_eff = det_eff_y[np.logical_and(x >= (t_det - bound_min_left), x <= (t_det-bound_max_right))]
            
            func = np.exp(-cs*pe_conc*thick)
            
            integral_ieff.append(trapezoid(pulse_trap*det_eff*func))
            integral_ioeff.append(trapezoid(pulse_trap*det_eff))

        
        
        i_eff = (sum(integral_ieff))
        io_eff = (sum(integral_ioeff))
    
        sigma_eff.append(-(1/(pe_conc*thick))*np.log(i_eff/io_eff)*barns)
    
    
    sigma_real = np.interp(points, cs_x, cs_y*barns)
        
    x_wvl = convert_tof (points, flight_path = 5.5, result = 'wavelength')
        
    plt.figure(figsize=(10,6))
    plt.ylabel(' Effective Cross-Section '+ r'[barns]')
    plt.plot(x_wvl, sigma_real, 'b', linewidth = 4.0)
    plt.plot(x_wvl, sigma_eff, 'ko', linewidth = 1.5)
    plt.xlabel(' Wavelenth '+ r'[$\AA$]')
    plt.grid(True)
    
    return


# =============================================================================================================================================================
#                           TRAPEZOID PULSE INVERSE
# =============================================================================================================================================================

def trapezoid_pulse_inverse (points):
    sigma_eff = []
    for t_det in points:
        
        integral_ioeff=[]
        integral_ieff =[]
        
        for i in range(-1,2,1):
            
                # if limits do not change sign
            
            bound_min_left = i*T 
            bound_max_left = i*T + 0.12*T
            bound_max_mid = i*T + 0.2*T
            bound_max_right = i*T + 0.32*T
            
            left = y[np.logical_and(x >= (t_det - bound_max_left), x < (t_det-bound_min_left))]
            p_left = left* np.linspace(0,0.99,len(left))
            cs_left =  cs_y[np.logical_and(cs_x >= (t_det - bound_max_left), cs_x < (t_det-bound_min_left))]
            #cs_left = cs_left*np.linspace(0,0.99,len(cs_left))
            
            mid = y[np.logical_and(x >= (t_det - bound_max_mid), x <= (t_det-bound_max_left))]
            p_mid = mid
            cs_mid = cs_y[np.logical_and(cs_x >= (t_det - bound_max_mid), cs_x <= (t_det-bound_max_left))]
            
            right = y[np.logical_and(x > (t_det - bound_max_right), x <= (t_det-bound_max_mid))]
            p_right = right* np.linspace(0.99,0,len(right))
            cs_right = cs_y[np.logical_and(cs_x > (t_det - bound_max_right), cs_x <= (t_det-bound_max_mid))]
           # cs_right = cs_right*np.linspace(0.99,0,len(cs_right))
            
            x_left = x[np.logical_and(x > (t_det - bound_max_left), x <= (t_det-bound_min_left))]
            x_mid = x[np.logical_and(x >= (t_det - bound_max_mid), x <= (t_det-bound_max_left))]
            x_right = x[np.logical_and(x >= (t_det - bound_max_right), x < (t_det-bound_max_mid))]
            
            det_eff_left = det_eff_y[np.logical_and(x >= (t_det - bound_max_left), x <= (t_det-bound_min_left))]
            det_eff_mid = det_eff_y[np.logical_and(x >= (t_det - bound_max_mid), x <= (t_det-bound_max_left))]
            det_eff_right = det_eff_y[np.logical_and(x >= (t_det - bound_max_right), x <= (t_det-bound_max_mid))]
            
            func_left = np.exp(-cs_left*pe_conc*thick)
            func_mid = np.exp(-cs_mid*pe_conc*thick)
            func_right = np.exp(-cs_right*pe_conc*thick)
            
            integral_ieff.append(trapezoid(p_left*func_left*det_eff_left) + trapezoid(p_mid*func_mid*det_eff_mid) + trapezoid(p_right*func_right*det_eff_right))
            integral_ioeff.append(trapezoid(p_left*det_eff_left) +trapezoid(p_mid*det_eff_mid) + trapezoid(p_right*det_eff_right))
            
            # idx, val = find_nearest_val (x, t_det)
            # plt.plot (x[idx],y[idx], 'bo', linewidth=6.0)
            # plt.plot(x_left, p_left , 'r.', linewidth=2.0)
            # plt.plot(x_mid, p_mid , 'k--', linewidth=2.0)
            # plt.plot(x_right, p_right , 'y*', linewidth=2.0)
        
        
        i_eff = (sum(integral_ieff))
        io_eff = (sum(integral_ioeff))
    
        sigma_eff.append(-(1/(pe_conc*thick))*np.log(i_eff/io_eff)*barns)
    
    
    sigma_real = np.interp(points, cs_x, cs_y*barns)
        
    x_wvl = convert_tof (points, flight_path = 5.5, result = 'wavelength')
        
    plt.figure(figsize=(10,6))
    plt.ylabel(' Effective Cross-Section '+ r'[barns]')
    plt.plot(x_wvl, sigma_real, 'b', linewidth = 4.0)
    plt.plot(x_wvl, sigma_eff, 'ko', linewidth = 1.5)
    plt.xlabel(' Wavelenth '+ r'[$\AA$]')
    plt.grid(True)
    
    return


# =============================================================================================================================================================
#                           TRAPEZOID PULSE_with function as trapezoid around a point
# =============================================================================================================================================================

def trapezoid_curves (points, integral_type = trapezoid, plot=False):
    
    sigma_eff = []
    if len(points)>20:
        print('WARNING: Too many points to plot (' + str(len(points))+'), setting plot = False to avoid crashes')
        plot = False
        
    for t_det in points:
        
        io_x, io_y = trapezoid_weight (x, y, t_det, plot=plot) 
        f_x, f_y = normal_weight (cs_x, cs_y, t_det, plot=plot) 
        func_f_y = np.exp(-f_y*pe_conc*thick)
        det_x, det_y = normal_weight (det_eff_x, det_eff_y, t_det, plot=plot) 
            
        integral_ieff = integral_type(io_y*det_y*func_f_y)
        integral_ioeff = integral_type(io_y*det_y)
    
        sigma_eff.append(-(1/(pe_conc*thick)*barns)*np.log(integral_ieff/integral_ioeff))
    
    
    sigma_real = np.interp(points, cs_x, cs_y*barns)
        
    x_wvl = convert_tof (points, flight_path = 5.5, result = 'wavelength')
        
    plt.figure(figsize=(10,6))
    plt.ylabel(' Cross-Section '+ r'[barns]')
    plt.plot(x_wvl, sigma_real, 'b', linewidth = 4.0, label = 'sigma_real')
    plt.plot(x_wvl, sigma_eff, 'ko', linewidth = 1.5, label = 'sigma_eff')
    plt.xlabel(' Wavelenth '+ r'[$\AA$]')
    plt.grid(True)
    
    return




# =============================================================================================================================================================


points = np.linspace(-0.5*T,1.5*T, num = 20)
squared_pulse(points)
#squared_pulse_inverse(points)
trapezoid_pulse(points)
#trapezoid_pulse_inverse(points)
#trapezoid_curves(points, integral_type = trapezoid, plot = True)




















