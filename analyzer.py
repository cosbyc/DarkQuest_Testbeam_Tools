
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
from src.plot_histos import plotHistograms
from src.read_config import readConfig
from src.unscrambler import trigIdSort, bufferSort
from src.read_file import getEvents, getEventsTail

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    if iteration == total: 
        print('')


def applyCuts(events, config):
    triggerThresh = config['triggerThresh']
    vetoThresh = config['vetoThresh']
    sumThresh = config['sumThresh']
    sumMax = config['sumMax']
    gain = config['gain']
    #timeRange = config['timeRange']
    emcalCfg = config['emcalCfg']
    topHodoCfg = config['topHodoCfg']
    bottomHodoCfg = config['bottomHodoCfg']
    topHodoEnabled = config['topHodoEnabled']
    botHodoEnabled = config['botHodoEnabled']

    passed_events = []
    for event in events:
        failedEvent = False

        sectorSum = 0
        for row in range(4):
            for col in range(4):
                amplitude = event['emcal'][row, col]
                if (emcalCfg[row][col] == 'T' and amplitude < triggerThresh) or (emcalCfg[row][col] == 'V' and amplitude > vetoThresh):
                    failedEvent = True
                if emcalCfg[row][col] == 'S':
                    sectorSum += amplitude

        if sectorSum < sumThresh:
            failedEvent = True

        if event['channelSum'] > sumMax:
            failedEvent = True
            
        #if (((timeRange[0] is not -1) and (event['timestamp'] < timeRange[0])) or ((timeRange[1] is not -1) and (event['timestamp'] > timeRange[1])))
            #failedEvent = True
        
        if topHodoEnabled:
            for j in range(4):
                if topHodoCfg[j] == 'x':
                    continue
                amplitude = event['minihodoT'][j%2]
                if (((topHodoCfg[j] == 'T' and amplitude < triggerThresh) or (topHodoCfg[j] == 'V' and amplitude > vetoThresh))):
                    failedEvent = True

        if botHodoEnabled:
            for j in range(4):
                if bottomHodoCfg[j] == 'x':
                    continue
                amplitude = event['minihodoB'][j%2]
                if (((bottomHodoCfg[j] == 'T' and amplitude < triggerThresh) or (bottomHodoCfg[j] == 'V' and amplitude > vetoThresh))):
                    failedEvent = True

        if failedEvent is False:
            passed_events.append(event)

    return passed_events

def remap(channel):
    rowOffset = colOffset = 0
    if channel % 4 == 1:
        colOffset += 1
        rowOffset += 1
    elif channel % 4 == 0:
        colOffset += 1
    elif channel % 4 == 3:
        rowOffset += 1
    if channel < 8:
        colOffset += 2
    if channel % 8 > 3:
        rowOffset += 2 
    # Has to be transposed because of ndenum
    return colOffset, rowOffset

def averageADC(events):
    num_events = len(events)
    if num_events == 0:
        return None

    EMCalAvg = np.zeros((4,4), dtype=float)

    for event in events:
        EMCalAvg += event['emcal']
    EMCalAvg /= num_events

    maxChannel = 0
    bestYet = 0
    for channel in range(16):
        row, col = remap(channel)
        if EMCalAvg[row][col] > bestYet:
            bestYet = EMCalAvg[row][col]
            maxChannel = channel

    return {'emcal': EMCalAvg}, maxChannel

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help='Janus event list')
    parser.add_argument('-p', '--makePlots', action='store_true', dest='makePlots', help='Create maps for all events') 
    parser.add_argument('-c', '--configFile', dest='configFile', type=str, help='The name of the .cfg file for the input run file', default='.previous_run.cfg')
    args = parser.parse_args()

    runConfig = readConfig(args.configFile)
    runNumber = args.filename.split('Run')[1].split('_')[0]
    outputDir = f'output/run{runNumber}_{runConfig["name"][:-1]}'
    os.makedirs(outputDir, exist_ok=True)

    
    allEvents =  None
    if (runConfig['topHodoEnabled'] and runConfig['botHodoEnabled']):
        #trigIdSort(args.filename, runNumber) # DOES NOT WORK: DO NOT USE
        #events, totalEvents = analyzeRun(f'runFiles/Run{runNumber}_trigID_sorted.txt', runConfig)
        bufferSort(args.filename, runNumber)
        allEvents = getEvents(f'runFiles/Run{runNumber}_list_buffer_sorted.txt', runConfig)
    else:
        #allEvents = getEventsTail(args.filename, runConfig, gain=gain, timeWindow=60)
        allEvents = getEvents(args.filename, runConfig)
        
    events = applyCuts(allEvents, runConfig)
    
    #print(events[0])
    #print(events[1])
    #print(events[2])
    
    if len(events) == 0:
        print("No events passing selections\n")
        exit()
    else:
        print(f'{len(events)}/{len(allEvents)} events passed the selections.\n')
    
    # plot average ADC per channel
    plt.cla()
    plt.close()
    plotEvent(averageADC(events)[0], outputDir, runNumber, len(allEvents), runConfig, avg=True, passingEvents = len(events), tag=f' max channel: {averageADC(events)[1]}')

    
    # produce histograms for all unmasked channels
    plotHistograms(events, runConfig, runNumber, outputDir, talk = True)
    # plotting loop
    if args.makePlots:
        print('Generating plots...\n')
        for i, event in enumerate(events):
            plotEvent(event, outputDir, runNumber, len(allEvents), runConfig)
            if ((i+1) % 20 == 0) or (i+1 == len(events)):
                printProgressBar (i+1, len(events), suffix=f'{i+1}/{len(events)}')
        print('\n')


    
if __name__ == "__main__":
    main()
