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
from src.unscrambler import trigIdSort, bufferSort

def getEvents(filename, config):
    with open(filename, 'r') as file:
        lines = file.readlines()
    file.close()
        
    emcalCfg = config['emcalCfg']
    topHodoCfg = config['topHodoCfg']
    bottomHodoCfg = config['bottomHodoCfg']
    topHodoEnabled = config['topHodoEnabled']
    botHodoEnabled = config['botHodoEnabled']

    gain = config['gain']
    
    events = []
    totalEvents = 0
    currentTrigger = None

    lines = lines[9:]
    channelSum = 0
    
    buffer =[]
    for line in lines:
        parts = line.strip().split()

        # Check if the line starts a new EMCal event
        if len(parts) == 7 and int(parts[0]) == 1:
            timestamp = float(parts[4])
            if currentTrigger:
                totalEvents += 1
                currentTrigger['event_number'] = totalEvents
                currentTrigger['timestamp'] = timestamp
                currentTrigger['channelSum'] = channelSum
                events.append(currentTrigger)
                channelSum = 0
            currentTrigger = {
                'event_number': 0,
                'emcal': np.zeros((4, 4), dtype=int),
                'timestamp': timestamp,
                'channelSum': channelSum
            }
            if topHodoEnabled:
                currentTrigger.update({'minihodoT': np.zeros(2, dtype=int)})
            if botHodoEnabled:
                currentTrigger.update({'minihodoB': np.zeros(2, dtype=int)})
            
            board = int(parts[0])
            channel = int(parts[1])
            amplitude = int(parts[3])  # HG
            if gain.lower()=='lg':
                amplitude = int(parts[2]) # LG
            channelSum += amplitude
            row, col = remap(channel)
            currentTrigger['emcal'][row, col] = amplitude
        
        # All other lines, including minihodos
        elif len(parts) >= 4:
            board = int(parts[0])
            channel = int(parts[1])
            amplitude = int(parts[3])  # HG
            if gain.lower()=='lg':
                amplitude = int(parts[2]) # LG
                
            if board == 1:
                row, col = remap(channel)
                channelSum += amplitude
                currentTrigger['emcal'][row, col] = amplitude
                
            elif board == 0 and topHodoEnabled and channel < 2:
                amplitude = int(parts[2])  # LG
                currentTrigger['minihodoT'][channel % 2] = amplitude
                    
            elif board == 0 and botHodoEnabled and channel >= 2:
                amplitude = int(parts[2])  # LG
                currentTrigger['minihodoB'][channel % 2] = amplitude

    if currentTrigger:
        totalEvents += 1
        currentTrigger['event_number'] = totalEvents
        currentTrigger['timestamp'] = timestamp
        currentTrigger['channelSum'] = channelSum
    events.append(currentTrigger)

    
    return events
        
def getEventsTail(filename, config, timeWindow, log=False, outPath=''):
    with open(filename, 'r') as file:
        lines = file.readlines()
    file.close()
    
    emcalCfg = config['emcalCfg']
    topHodoCfg = config['topHodoCfg']
    bottomHodoCfg = config['bottomHodoCfg']
    topHodoEnabled = config['topHodoEnabled']
    botHodoEnabled = config['botHodoEnabled']

    gain = config['gain']
    
    events = []
    totalEvents = 0
    currentTrigger = None

    head = lines[:9]


    runNumber = spillNumber = 0
    if log ==True:
        runNumber = filename.split('Run')[1].split('_')[0]
        spillNumber = outPath.split('Spill')[1]
        with open(f'{outPath.split("/images")[0]}/logs/Spill{spillNumber}_list.txt', 'w') as f:
            for line in head:
                f.write(line) 
    
    # Start from the bottom of the file and work upwards
    data_lines = lines[9:][::-1]

    buffer = []
    ready = False

    channelSum = 0
    
    for line in data_lines:
        parts = line.strip().split()


        if (int(parts[1]) == 15 and timeWindow is not None) or currentTrigger is not None:
            ready = True

        if ready:
            buffer.append(line)
        else:
            continue

        # Check if the line starts a new EMCal event
        if len(parts) == 7 and int(parts[0]) == 1:
            timestamp = float(parts[4])

            if currentTrigger is None:
                currentTrigger = {
                    'event_number': 0,
                    'emcal': np.zeros((4, 4), dtype=int),
                    'timestamp': timestamp,
                    'channelSum': channelSum                    
                }
                if topHodoEnabled:
                    currentTrigger.update({'minihodoT': np.zeros(2, dtype=int)})
                if botHodoEnabled:
                    currentTrigger.update({'minihodoB': np.zeros(2, dtype=int)})

            # Process the buffered lines
            while buffer:
                buffered_line = buffer.pop()
                if log ==True:
                    with open(f'{outPath.split("/images")[0]}/logs/Spill{spillNumber}_list.txt', 'a') as f:
                        f.write(buffered_line)                    
                buffered_parts = buffered_line.strip().split()

                board = int(buffered_parts[0])
                channel = int(buffered_parts[1])
                amplitude = int(buffered_parts[3])  # HG
                if gain.lower()=='lg':
                    amplitude = int(buffered_parts[2])  # LG
                if board == 1:
                    channelSum += amplitude
                    row, col = remap(channel)
                    currentTrigger['emcal'][row, col] = amplitude

                elif board == 0 and topHodoEnabled and channel < 2:
                    amplitude = int(buffered_parts[2])  # LG
                    currentTrigger['minihodoT'][channel % 2] = amplitude

                elif board == 0 and botHodoEnabled and channel >= 2:
                    amplitude = int(buffered_parts[2])  # LG
                    currentTrigger['minihodoB'][channel % 2] = amplitude

            if currentTrigger:
                totalEvents += 1
                currentTrigger['event_number'] = totalEvents
                currentTrigger['timestamp'] = timestamp
                currentTrigger['channelSum'] = channelSum
                events.append(currentTrigger)
                currentTrigger = None

                if timeWindow is not None and len(events) > 1 and (events[0]['timestamp'] - timestamp) > (timeWindow * 1000000.0):  # Convert time window to seconds
                    break


    if currentTrigger and (timeWindow is None or len(events) == 0 or (events[0]['timestamp'] - currentTrigger['timestamp']) <= (timeWindow * 1000000.0)):
        totalEvents += 1
        currentTrigger['event_number'] = totalEvents
        currentTrigger['timestamp'] = timestamp
        currentTrigger['channelSum'] = channelSum
        events.append(currentTrigger)

    return events
        

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

