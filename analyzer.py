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
from src.unscrambler import fixTriggerOrder

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    if iteration == total: 
        print('')

        
def analyzeRun(filename, config):
    with open(filename, 'r') as file:
        lines = file.readlines()

    triggerThresh = config['triggerThresh']
    vetoThresh = config['vetoThresh']
    emcalCfg = config['emcalCfg']
    topHodoCfg = config['topHodoCfg']
    bottomHodoCfg = config['bottomHodoCfg']
    topHodoEnabled = config['topHodoEnabled']
    botHodoEnabled = config['botHodoEnabled']

    events = []
    totalEvents = 0
    
    current_trigger = None
    
    failedChannels = 0
    for line in lines[9:]:
        parts = line.strip().split()
        
        # Check if the line starts a new EMCal event
        if len(parts) == 7 and int(parts[0]) == 1:
            if current_trigger:
                # saving previous event before starting next one.
                # checking trigger and veto conditions
                totalEvents+=1
                if failedChannels == 0:
                    current_trigger['event_number'] = totalEvents
                    events.append(current_trigger)
                else:
                    failedChannels = 0 
            current_trigger = {
                'event_number': 0,
                'emcal': np.zeros((4, 4), dtype=int)
            }
            if topHodoEnabled:
                current_trigger.update({'minihodoT': np.zeros(2, dtype=int)})
            if botHodoEnabled:
                current_trigger.update({'minihodoB': np.zeros(2, dtype=int)})
            
            board = int(parts[0])
            channel = int(parts[1])
            amplitude = int(parts[3]) #HG
            row, col = remap(channel)

            if (emcalCfg[row][col] == 'T' and amplitude < triggerThresh) or (emcalCfg[row][col] == 'V' and amplitude > vetoThresh):
                failedChannels += 1
            if (emcalCfg[row][col] != 'x'):
                current_trigger['emcal'][row, col] = amplitude
        
        # all other lines, including minihodos
        elif len(parts) >= 4:
            board = int(parts[0])
            channel = int(parts[1])
            amplitude = int(parts[3])
            
            if board == 1:
                row, col = remap(channel)
                if (emcalCfg[row][col] == 'T' and amplitude < triggerThresh) or (emcalCfg[row][col] == 'V' and amplitude > vetoThresh):
                    failedChannels+=1
                if (emcalCfg[row][col] != 'x'):
                    current_trigger['emcal'][row, col] = amplitude
                
            elif board == 0 and topHodoEnabled and channel < 2:
                amplitude = int(parts[2]) #LG
                for j in range(len(topHodoCfg)):
                    if topHodoCfg[j] == 'x':
                        continue
                    if (topHodoCfg[channel % 2] == 'T' and amplitude < triggerThresh) or (topHodoCfg[channel % 2] == 'V' and amplitude > vetoThresh):
                        failedChannels+=1
                    current_trigger['minihodoT'][channel % 2] = amplitude
                    
            elif board == 0 and botHodoEnabled and channel >= 2:
                amplitude = int(parts[2]) #LG
                for j in range(len(bottomHodoCfg)):
                    if bottomHodoCfg[j] == 'x':
                        continue
                    if (bottomHodoCfg[channel % 2] == 'T' and amplitude < triggerThresh) or (bottomHodoCfg[channel % 2] == 'V' and amplitude > vetoThresh):
                        failedChannels+=1
                    current_trigger['minihodoB'][channel % 2] = amplitude                    
    return events, totalEvents

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
    
    return {'emcal': EMCalAvg}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help='Janus event list')
    parser.add_argument('-p', '--makePlots', action='store_true', dest='makePlots', help='Create maps for all events') 
    parser.add_argument('-c', '--configFile', dest='configFile', type=str, help='The name of the .cfg file for the input run file', default='.previous_run.cfg')
    args = parser.parse_args()

    runConfig = readConfig(args.configFile)
    run_number = args.filename.split('Run')[1].split('_')[0]
    output_dir = f'output/run{run_number}_{runConfig["name"][:-1]}'
    os.makedirs(output_dir, exist_ok=True)

    fixTriggerOrder(args.filename)    
    events, totalEvents = analyzeRun('tmp.txt', runConfig)
    os.system('rm tmp.txt')
    
    if len(events) == 0:
        print("No events passing selections\n")
        exit()
    else:
        print(f'{len(events)}/{totalEvents} events passed the selections.\n')
    
    # plotting loop
    if args.makePlots:
        print('Generating plots...\n')
        for i, event in enumerate(events):
            plotEvent(event, output_dir, run_number, totalEvents, runConfig)
            if ((i+1) % 20 == 0) or (i+1 == len(events)):
                printProgressBar (i+1, len(events), suffix=f'{i+1}/{len(events)}')
        print('\n')

    # plot average ADC per channel
    plotEvent(averageADC(events), output_dir, run_number, totalEvents, runConfig, avg=True)


if __name__ == "__main__":
    main()
