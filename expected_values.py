
# This program parse the file "Continuity_PCB.xlsx" to acquire the mapping
# between signal channels and VIB pin as well as matrix location. It then loops through
# all the possible pairs of two channels, and write the expected
# measurement values of the channel pair to a file called "expected_result.txt".


import numpy as np
import pandas as pd
from decimal import Decimal
import csv

disconnected_lower = 40.0e6      # lower bound of expected resistance between supposedly disconnected channels
disconnected_upper = 1.0e38      # upper bound of expected resistance between supposedly disconnected channels
TES_lower = 100.0                # lower bound of expected resistance for TES connections
TES_upper = 400.0                # upper bound of expected resistance for TES connections
SQ_lower = 8.0e3                 # lower bound of expected resistance for SQUID Bias connections
SQ_upper = 12.0e3                # upper bound of expected resistance for SQUID Bias connections
SQF_lower = 5.0e3                # lower bound of expected resistance for SQUID Feedback Bias connections
SQF_upper = 8.0e3                # upper bound of expected resistance for SQUID Feedback Bias connections


def write_connected(signal_name1, signal_name2, f):
    """
        Write a row in the file F, which is supposed to be the file
        displaying the expected values for our continuity measurements.
        The two signals SIGNAME1 and SIGNAME2 are expected to be connected.
    """
    f.write('{:^20s}{:^20s}{:^20s}{:^20f}{:^20f}' \
            .format(signal_name1, signal_name2, "Connected", \
                    round(np.random.rand(), 3), round(np.random.rand(), 3) + 3))
    f.write('\n')
    return


def write_disconnected(signal_name1, signal_name2, f):
    """
        Write a row in the file F, which is supposed to be the file
        displaying the expected values for our continuity measurements.
        The two signals SIGNAME1 and SIGNAME2 are expected to be disconnected.
    """
    f.write('{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}' \
            .format(signal_name1, signal_name2, "Disconnected", \
                    '%.6E' % Decimal(disconnected_lower), '%.6E' % Decimal(disconnected_upper)))
    f.write('\n')
    return


def write_LED(LED_sig, LED_com, f):
    """
        Write a row in the file F, which is supposed to be the file
        displaying the expected values for our continuity measurements.
        One signal, LED_sig is the LED channel, and LED_com is the LED common
        channel.
    """
    f.write('{:^20s}{:^20s}{:^20s}{:^20f}{:^20f}'
            .format(LED_sig, LED_com, "LED_forward",
                    round(np.random.rand(), 3), round(np.random.rand(), 3) + 3))
    f.write('\n')

    f.write('{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}'
            .format(LED_sig, LED_com, "LED_reverse",
                    '%.6E' % Decimal(disconnected_lower), '%.6E' % Decimal(disconnected_upper)))
    f.write('\n')
    return

##########################
##########################
##########################

# """Parsing continuity_test_pinout.xlsx"""
#
# xl = pd.ExcelFile("continuity_test_pinout.xlsx")
# df = xl.parse("Sheet1")
# df = df.dropna(axis='columns', how = 'all')
# df_connection_pairs = df.dropna(how = 'all')
# #print(df_connection_pairs)


# Parsing Continuity_PCB.xlsx

xl = pd.ExcelFile("Continuity_PCB.xlsx")

df = xl.parse(xl.sheet_names[0])
df = df.dropna(axis='columns')


# Generates a mapping between signal name (like SQ_6) to VIB,
# and a mapping between VIB to matrix location of the switch card (?).

signal_name_to_VIB = {}
VIB_to_matrix_loc = {}

for index, row in df.iterrows():
    matrix_loc = row['Matrix location']
    VIB = row['VIB pin']
    if row['Signal name'] == "x":
        continue
    signal_name = row['Signal name']
    signal_name_to_VIB[signal_name] = VIB
    VIB_to_matrix_loc[VIB] = matrix_loc

print(len(signal_name_to_VIB.keys()))
print(len(VIB_to_matrix_loc.keys()))

N_signal_name = len(signal_name_to_VIB.keys())
signal_names = []
for signal_name in signal_name_to_VIB.keys():
    signal_names.append(signal_name)
f = open("expected_result.txt", "w+")
f.write('{:^20s}{:^20s}{:^20s}{:^20s}{:^20s}'.format('Signal_1', 'Signal_2', 'Expected Continuity', \
                                                     "min", 'max'))
f.write('\n')



def is_ground(signal_name):
    signal_name_decomp = signal_name.split("_")
    return signal_name_decomp[0] == "AGND"



connections_values = {}

# a dictionary with keys being channels connected with ground and
# values being the expected resistance of the connection
connect_w_groud = {}

with open('all_connections.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        signal_1, signal_2 = row["Signal_1"], row["Signal_2"]
        key = {signal_1, signal_2}

        if is_ground(signal_1) and not is_ground(signal_2):
            if signal_2[0:3] == "TES":
                connect_w_groud[signal_2] = [TES_lower, TES_upper]


    print(f'Processed {line_count} lines.')



# Actually looping through all the possible pairs

for i in range(N_signal_name):
    for j in range(i + 1, N_signal_name):
        signal_name1 = signal_names[i]
        signal_name2 = signal_names[j]
        signal_name1_decomp = signal_name1.split("_")
        signal_name2_decomp = signal_name2.split("_")


        #checking whether there is a return channel

        if len(signal_name1_decomp) == 1 or signal_name1_decomp[1] != "RTN":
            contain_rtn1 = False
        else:
            contain_rtn1 = True

        if len(signal_name2_decomp) == 1 or signal_name2_decomp[1] != "RTN":
            contain_rtn2 = False
        else:
            contain_rtn2 = True


        if contain_rtn1 and not contain_rtn2:
            if len(signal_name1_decomp) == len(signal_name2_decomp) + 1 \
                and signal_name1_decomp[0] == signal_name2_decomp[0] \
                and signal_name1_decomp[-1] == signal_name2_decomp[-1]:

                write_connected(signal_name1, signal_name2, f)
            else:
                write_disconnected(signal_name1, signal_name2, f)

        elif contain_rtn2 and not contain_rtn1:
            if len(signal_name2_decomp) == len(signal_name1_decomp) + 1 \
                and signal_name1_decomp[0] == signal_name2_decomp[0] \
                and signal_name1_decomp[-1] == signal_name2_decomp[-1]:

                write_connected(signal_name1, signal_name2, f)
            else:
                write_disconnected(signal_name1, signal_name2, f)

        elif len(signal_name1) >= 4 and signal_name1[0:4] == 'AGND' and \
                len(signal_name2) >= 4 and signal_name2[0:4] == 'AGND':
            write_connected(signal_name1, signal_name2, f)   # Ground and ground should be connected

        elif signal_name1_decomp[0] == 'LED' and signal_name1_decomp[1] != 'COM' \
                and signal_name2_decomp[0] == 'LED' and signal_name2_decomp[1] == 'COM':
            write_LED(signal_name1, signal_name2, f)

        elif signal_name2_decomp[0] == 'LED' and signal_name2_decomp[1] != 'COM' \
                and signal_name1_decomp[0] == 'LED' and signal_name1_decomp[1] == 'COM':
            write_LED(signal_name2, signal_name1, f)

        else:
            write_disconnected(signal_name1, signal_name2, f)

f.close()







