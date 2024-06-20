import warnings
warnings.simplefilter("ignore", UserWarning)

import numpy as np
import matplotlib.pyplot as plt
import argparse
from argcomplete.completers import ChoicesCompleter
import os
import matplotlib.gridspec as gridspec
from matplotlib import pyplot, image, transforms
from src.plot_event import plotEvent
from src.read_config import readConfig
from src.read_file import getEvents
from src.unscrambler import trigIdSort, bufferSort
from analyzer import averageADC, applyCuts
import glob

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help='Janus event list')
    parser.add_argument('-t', '--threshold', dest='threshold', type=int, help='Desired offline threshold for each column.', default='80')
    parser.add_argument('-v', '--veto', dest='veto', type=int, help='Desired veto threshold for unselected columns.', default='80')
    args = parser.parse_args()

    run_number = args.filename.split('Run')[1].split('_')[0]
    output_dir = f'output/run{run_number}_allChannelColumnAverage/'
    os.makedirs(output_dir, exist_ok=True)

    print('Reading in configurations of columnar trigger/vetoing.')
    print(f'Selection ADC is {args.threshold}')
    print(f'Veto threshold is ADC is {args.veto}')

    includedEvents=[]
    runConfig=None
    totalEvents = 0
    calibrationConfigs = ['selfTrigLeftSideLeftFile','selfTrigLeftSideRightFile', 'selfTrigRightSideLeftFile','selfTrigRightSideRightFile']
    channelAverages = np.zeros((4,4), dtype=float)
    for i in range(len(calibrationConfigs)):
        runConfig = readConfig(f'src/utilConfigs/{calibrationConfigs[i]}.cfg', talk=False)
        runConfig["triggerThresh"] = args.threshold
        runConfig["vetoThresh"] = args.veto
        
        events = getEvents(args.filename, runConfig)
        totalEvents = len(events)
        events = applyCuts(events, runConfig)
        
        for j in range(4):
            channelAverages[j][i] =  averageADC(events)['emcal'][j][i]
        includedEvents.append(len(events))
    allAvg = {
        'event_number': 0,
        'emcal': channelAverages
    }
    runConfig["name"] = 'Self Trigger, Columnar Selection ADC = 80'
    plotEvent(allAvg, output_dir, run_number, totalEvents, runConfig, avg=True, passingEvents = 'X', tag = f'X={str(includedEvents)}')
    print('Column averages created!')
    print(channelAverages)
    
if __name__ == "__main__":
    main()
