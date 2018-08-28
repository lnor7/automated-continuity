# This program parse the output file "expected_result.txt" from "expected_values.py", calls on
# LUA functions that actually connect the channels and do the measurements, and
# check whether our measurement is within the expected range by comparing the result
# with the "expected_result.txt" file. Note that currently the LUA functions are not actually
# written. This program just generates some random number as result.  Those measurement functions
# should later be replaced by python interfaces that call on real LUA functions written by Eleanor at SLAC.
# This program, in the end, outputs two files. One that record all the test results of this continuity check,
# and the other outputs only the channel connections that didn't pass the continuity check.


import numpy as np
import pandas as pd
import time
import telnetlib
from decimal import Decimal

disconnected_lower = 40.0e6    # lower bound for the resistance between supposedly disconnected channels



def measure(row, f, signal_name_to_VIB, VIB_to_matrix_loc):
    """
    Perform measurement on the signal channels specified by one row (taken as an argument)
    of the expected values dataframe and record the result.
    :param row: a row in the dataframe that record the expected result of every connection measurement.
    It is supposed to contain information about the two channels being measured, the type of the measurement,
    the expected minimum value of the measurement, the expected maximum value of the measurement.
    :param f: a Python file object that
    :param signal_name_to_VIB: a mapping between signal name to VIB (created by parsing the excel file)
    :param VIB_to_matrix_loc: a mapping between VIB to matrix location
    :return: None
    """

    signal_name1, signal_name2 = row[0], row[1]
    matrix_loc1, matrix_loc2 = VIB_to_matrix_loc[signal_name_to_VIB[signal_name1]], \
                             VIB_to_matrix_loc[signal_name_to_VIB[signal_name2]]

    if row[2] == "Disconnected":
        #tn.write(("resistance_test(\""+matrix_loc1[2::].encode('ascii', 'ignore')+"\",\""+matrix_loc2[2::].encode('ascii', 'ignore')+"\")\n").encode('ascii'))
        tn.write(("resistance_test(\"" + matrix_loc1[2::] + "\",\"" + matrix_loc2[2::] + "\")\n").encode("ascii"))
        print(matrix_loc1)
        print(matrix_loc2)
        result = tn.read_until(("Ohm").encode("ascii"))
        result = result.split()
        result = float(result[0])
        exp_min = float(row[-2])
        exp_max = float(row[-1])
        #result = (exp_min + exp_max) / 2 + np.random.rand() * (exp_max - exp_min)
        satisfied = result > exp_min and result < exp_max
        if satisfied:
            test_pass = 'PASS'
        else:
            test_pass = 'FAIL'
        f.write('{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}'.format(signal_name1, signal_name2, 'Disconnected',
                                                                           '%.6E' % Decimal(exp_min), '%.6E' % Decimal(exp_max),
                                                                           '%.6E' % Decimal(result), test_pass))
        f.write('\n')



    elif row[2] == "Connected":
        #tn.write("resistance_test(\""+matrix_loc1[2::].encode('ascii', 'ignore')+"\",\""+matrix_loc2[2::].encode('ascii', 'ignore')+"\")\n")
        tn.write(("resistance_test(\"" + matrix_loc1[2::] + "\",\"" + matrix_loc2[2::] + "\")\n").encode("ascii"))
        #result = tn.read_until("Ohm")
        result = tn.read_until(("Ohm").encode("ascii"))
        result = result.split()
        result = float(result[0])
        exp_min = float(row[-2])
        exp_max = float(row[-1])
        #result = (exp_min + exp_max) / 2 + np.random.rand() * (exp_max - exp_min)
        satisfied = result > exp_min and result < exp_max
        if satisfied:
            test_pass = 'PASS'
        else:
            test_pass = 'FAIL'
        f.write('{:^20s}{:^20s}{:^20s}{:^20f}{:^20f}{:^20s}{:^20s}'.format(signal_name1, signal_name2, 'Connected',
                                                                           exp_min, exp_max,
                                                                           '%.6E' % Decimal(result), test_pass))
        f.write('\n')



    elif row[2] == "LED_forward":
        if signal_name1.split("_")[1] == "COM":
            matrix_loc_pos = matrix_loc2
            matrix_loc_neg = matrix_loc1
        else:
            matrix_loc_pos = matrix_loc1
            matrix_loc_neg = matrix_loc2
        tn.write("resistance_test(\""+matrix_loc_pos[2::].encode('ascii', 'ignore')\
                  +"\",\""+matrix_loc_neg[2::].encode('ascii', 'ignore')+"\")\n")
        result = tn.read_until(("Ohm").encode("ascii"))
        result = result.split()
        result = float(result[0])
        exp_min = float(row[-2])
        exp_max = float(row[-1])
        #result = (exp_min + exp_max) / 2 + np.random.rand() * (exp_max - exp_min)
        satisfied = result > exp_min and result < exp_max
        if satisfied:
            test_pass = 'PASS'
        else:
            test_pass = 'FAIL'
        f.write('{:^20s}{:^20s}{:^20s}{:^20f}{:^20f}{:^20s}{:^20s}'.format(signal_name1, signal_name2, 'LED_forward',
                                                                           exp_min, exp_max,
                                                                           '%.6E' % Decimal(result), test_pass))
        f.write('\n')


    elif row[2] == "LED_reverse":
        if signal_name1.split("_")[1] == "COM":
            matrix_loc_pos = matrix_loc2
            matrix_loc_neg = matrix_loc1
        else:
            matrix_loc_pos = matrix_loc1
            matrix_loc_neg = matrix_loc2
        tn.write(("resistance_test(\""+matrix_loc_neg[2::].encode('ascii', 'ignore')\
                 +"\",\""+matrix_loc_pos[2::].encode('ascii', 'ignore')+"\")\n").encode('ascii'))
        result = tn.read_until(("Ohm").encode("ascii"))
        result = result.split()
        result = float(result[0])
        exp_min = float(row[-2])
        exp_max = float(row[-1])
        #result = (exp_min + exp_max) / 2 + np.random.rand() * (exp_max - exp_min)
        satisfied = result > exp_min and result < exp_max
        if satisfied:
            test_pass = 'PASS'
        else:
            test_pass = 'FAIL'
        f.write('{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}'.format(signal_name1, signal_name2, 'LED_reverse',
                                                                           '%.6E' % Decimal(exp_min), '%.6E' % Decimal(exp_max),
                                                                           '%.6E' % Decimal(result), test_pass))
        f.write('\n')



    else:
        f.write('{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}'.format('ERROR', 'ERROR', 'ERROR',
                                                                           'ERROR', 'ERROR', 'ERROR',
                                                                           'ERROR'))
        f.write('\n')


def parallel_disconnected(signal_name1, signal_name2_list, f, signal_name_to_VIB, VIB_to_matrix_loc):
    """

    :param signal_name1: name of signal channel 1
    :param signal_name2_list: a list of channels that are all supposed to be open with signal 1;
    the program will call on a lua function that connect all the channels in signame2_list
    in parallel and measure the continuity between signame1 and signame2_list
    :param f: the file object to write our result in
    :return: if signame1 and signame2_list are disconnected/open (as expected), the function will write the
    corresponding results in the file F, and return True. If the connection is closed, the function will simply
    return False.
    """
    matrix_loc1 = VIB_to_matrix_loc[signal_name_to_VIB[signal_name1]]
    matrix_locs2 = []
    for name in signal_name2_list:
        matrix_locs2.append(VIB_to_matrix_loc[signal_name_to_VIB[name]])

    list_string = "\""
    for loc in matrix_locs2:
        #list_string += loc[2::].encode('ascii','ignore')+"\",\""
        list_string += loc[2::] + "\",\""

    list_string = list_string[:-2]
    print(list_string)

    # tn.write("open_test(\""+matrix_loc1[2::].encode('ascii', 'ignore')+"\",{"+list_string+"})\n")
    tn.write(("open_test(\"" + matrix_loc1[2::] + "\",{" + list_string + "})\n").encode("ascii"))
    result = tn.read_until(("Ohm").encode("ascii"))
    result = result.split()
    result = float(result[0])
    satisfied = result > disconnected_lower
    if satisfied:
        for sig in signal_name2_list:
            f.write('{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}'.format(signal_name1, sig, 'Disconnected',
                                                                               'Disconnected', 'Disconnected',
                                                                               '%.6E' % Decimal(result), 'PASS'))
            f.write('\n')
        return True
    else:
        return False

        

"""Making connection to DMM"""
HOST = "192.168.005.120"

tn = telnetlib.Telnet(HOST)

tn.write(("load_functions()\n").encode('ascii'))

"""Parsing expected_result.txt"""
expected = np.loadtxt(fname = "expected_result.txt", skiprows= 1, dtype = 'str')

"""Parsing Continuity_PCB.xlsx"""
xl = pd.ExcelFile("Continuity_PCB.xlsx")

df = xl.parse(xl.sheet_names[0])
df = df.dropna(axis='columns')

signal_name_to_VIB = {}
VIB_to_matrix_loc = {}

for index, row in df.iterrows():
    matrix_loc = row['Matrix location']
    VIB = row['VIB pin']
    if row['Signal name'] == 'x':
        continue
    signal_name = row['Signal name']
    signal_name_to_VIB[signal_name] = VIB
    VIB_to_matrix_loc[VIB] = matrix_loc


N_signal_name = len(signal_name_to_VIB.keys())
signal_names = []
for signal_name in signal_name_to_VIB.keys():
    signal_names.append(signal_name)

f = open("test_result_all.txt", "w+")
f.write('{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}'.format('Signal_1', 'Signal_2', 'Type', \
                                                     "Expected_Min", 'Expected_Max', \
                                                     'Measured_Result', 'Pass?'))
f.write('\n')

# One key idea of the following measurements is that if the channels we are trying to measure
# are supposed to be open (which is the case for most channel pairs), then we try not to measure
# it individually but save it to later, where we can connect multiple supposedly open channel pairs
# in parallel and measure them together. If the result is indeed open, that means each of the individual
# channel pair is open, thus we can save some time. Only when there is unexpected shorting do we
# go back and measure each of the connection individually and figure out which one is shorted. Since
# the expected_result.txt file is naturally clustered by signal 1, we group our parallel measurements
# according to signal 1.

curr_signal1 = expected[0][0]
parallel_list = []
parallel_index_list = []

start = time.time()
for i in range(len(expected)):
    row = expected[i]
    # checking whether we should save this measurement to later so that we can
    # save some time by measuring multiple supposedly disconnected connections together in parallel
    if row[0] == curr_signal1 and row[2] == 'Disconnected':
        parallel_list.append(row[1])
        parallel_index_list.append(i)
    elif row[0] == curr_signal1 and row[2] != 'Disconnected':
        measure(row, f, signal_name_to_VIB, VIB_to_matrix_loc)
    else:
        result = parallel_disconnected(curr_signal1, parallel_list, f, signal_name_to_VIB, VIB_to_matrix_loc)
        if not result:
            # The parallel measurements suggest some unexpected shorting between
            # supposedly disconnected channels. Need to go through these connections one
            # by one to figure out which one (or more) of them are shorted
            for j in parallel_index_list:
                row_second_check = expected[j]
                measure(row_second_check, f, signal_name_to_VIB, VIB_to_matrix_loc)
        curr_signal1 = row[0]
        parallel_list = []
        parallel_index_list = []
        if row[2] == 'Disconnected':
            parallel_list.append(row[1])
            parallel_index_list.append(i)
            if i == len(expected) - 1:
                measure(row, f, signal_name_to_VIB, VIB_to_matrix_loc)
        else:
            measure(row, f, signal_name_to_VIB, VIB_to_matrix_loc)

f.close()
# Generate a dataframe to manipulate our result easily
result_df = pd.read_csv("test_result_all.txt", sep='\s+', header=0)



failed_df = result_df[result_df['Pass?'] != 'PASS']

f_failed = open("test_result_failed.txt", "w+")
f_failed.write('{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}'.format('Signal_1', 'Signal_2', 'Type', \
                                                     "Expected_Min", 'Expected_Max', \
                                                     'Measured_Result', 'Pass?'))
f_failed.write('\n')

for index, row in failed_df.iterrows():
    f_failed.write('{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}'.format(row[0], row[1], row[2], \
                                                     str(row[3]), str(row[4]), \
                                                     str(row[5]), str(row[6])))
    f_failed.write('\n')
f_failed.close()


end = time.time()
print('Runtime:', round(end - start, 3), "s")

tn.close()











