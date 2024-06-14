import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
import matplotlib.gridspec as gridspec 
from matplotlib import pyplot, image, transforms

def read_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    events = []
    current_trigger = None
    for line in lines[9:]:
        parts = line.strip().split()
        
        # Check if the line starts a new EMCal event
        if len(parts) == 7 and int(parts[0]) == 1:
            if current_trigger:
                events.append(current_trigger)
            current_trigger = {
                'emcal': np.zeros((4, 4), dtype=int),
                'minihodoT': np.zeros(2, dtype=int),
                'minihodoB': np.zeros(2, dtype=int)
            }
            board = int(parts[0])
            channel = int(parts[1])
            amplitude = int(parts[3]) #HG
            row, col = remap(channel)
            current_trigger['emcal'][row, col] = amplitude
        
        # all other lines, including minihodos
        elif len(parts) >= 4:
            board = int(parts[0])
            channel = int(parts[1])
            amplitude = int(parts[3])
            if board == 1:
                row, col = remap(channel)
                current_trigger['emcal'][row, col] = amplitude
            else:
                #print(amplitude)
                if channel == 0:
                    current_trigger['minihodoT'][1] = amplitude
                elif channel == 1:
                    current_trigger['minihodoT'][0] = amplitude
                elif channel == 2:
                    current_trigger['minihodoB'][0] = amplitude
                elif channel == 3:
                    current_trigger['minihodoB'][1] = amplitude
                    
                    
    if current_trigger:
        events.append(current_trigger)

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

def hodomap(channel):
    topBottom = 0
    leftRight = 0
    if channel % 1 == 1:
        leftRight += 1
    if channel >= 2:
        topBottom += 1
    return topBottom, leftRight

def plot_event(event, event_number, output_dir, filename):
    emcal = event['emcal']
    minihodoT = event['minihodoT']
    minihodoB = event['minihodoB']
    
    fig = plt.figure(1, figsize=(5,8))

    run_number = filename.split('_')[0][3:]
    fig.suptitle(f'Run {run_number}, Event {event_number}')

    fig.show()

    gs = gridspec.GridSpec(3,2, height_ratios=[0.2,1,0.2], width_ratios=[1,1])
    gs.update(left=0.05, right=0.95, bottom=0.08, top=0.92, wspace=0.0001, hspace=0.0002)
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
    fig.show()

    ax1 = plt.subplot(gs[1,:])
    cax = ax1.imshow(emcal, cmap='viridis', vmin = 0, vmax = 150)
    plt.axis('off')
    #fig.colorbar(cax)
    for (i, j), val in np.ndenumerate(emcal):
        ax1.text(j, i, f'{val}', ha='center', va='center', color='white')

    axt = plt.subplot(gs[0,0])
    plt.margins(y=0)
    plt.axis('off')
    caxt = axt.imshow(np.expand_dims(minihodoT, axis=0), cmap='viridis', aspect = 0.35, vmin = 0, vmax = 1000)
    for i, val in enumerate(minihodoT):
        axt.text( i, 0 , f'{val}', ha='center', va='center', color='white')
    
    axb = plt.subplot(gs[2,0])
    plt.axis('off')
    plt.tight_layout(pad=-5)
    caxb = axb.imshow(np.expand_dims(minihodoB, axis=0), cmap='viridis', aspect = 0.35, vmin = 0, vmax = 1000)
    for i, val in enumerate(minihodoB):
        axb.text( i, 0 , f'{val}', ha='center', va='center', color='white')
    axb.set_adjustable('box')

    evn_string = str(event_number).zfill(2)
    output_path = os.path.join(output_dir, f'event_{evn_string}.png')
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0.25)
    plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help='Janus event list')
    args = parser.parse_args()

    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    events = read_file(args.filename)
    
    for i, event in enumerate(events):
        plot_event(event, i + 1, output_dir, args.filename)

if __name__ == "__main__":
    main()
