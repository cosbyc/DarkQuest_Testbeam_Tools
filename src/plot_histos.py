import os
import numpy as np
import matplotlib.pyplot as plt
import statistics

def plotHistograms(events, config, run_number, output_dir, gain='HG'):
    """
    Plots histograms of ADC values for each of the 16 channels and saves them to the output directory.

    Args:
        events (list): List of EMCal events, where each event is a dictionary containing the 'emcal' key.
        config (dict): Run configuration containing the 'emcalCfg' key.
        output_dir (str): Directory to save the histogram plots.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    
        
    # Initialize a list of lists to hold ADC values for each channel and the sum
    adc_values = [[] for _ in range(16)]
    emcalCfg = config['emcalCfg']
    adcSum = []

    
    # Collect ADC values from each event
    for event in events:
        adcSum.append(event['channelSum'])
        emcal = event['emcal']
        for channel in range(16):
            row, col = remap(channel)
            if emcalCfg[row][col] != 'x':
                adc_values[channel].append(emcal[row, col])

    # Plot histograms channel sum
    plt.figure()
    plt.hist(adcSum, bins=100, color='blue', alpha=0.7, range =(0, 12000))
    plt.title(f'Run {run_number} {gain} ADC Histogram for sum of channels\n Mean: {round(statistics.mean(adcSum),2)}')
    plt.xlabel('ADC Value')
    plt.ylabel('Counts')
    plt.yscale('log')
    plt.grid(True)
    
    # Save the plot
    output_path = os.path.join(output_dir, f'channel_sum_histogram.png')
    plt.savefig(output_path)
    plt.close()


    # Plot histograms for each channel
    for channel in range(16):
        row, col = divmod(channel, 4)
        if emcalCfg[row][col] == 'x':
            continue

        plt.figure()
        plt.hist(adc_values[channel], bins=100, color='blue', alpha=0.7, range =(0, 5000))
        plt.title(f'Run {run_number} {gain} ADC Histogram for Channel {channel} \n{config["tag"]}')
        plt.xlabel('ADC Value')
        plt.ylabel('Counts')
        #plt.xscale('log')
        plt.grid(True)

        # Save the plot
        output_path = os.path.join(output_dir, f'channel_{str(channel).zfill(2)}_histogram.png')
        plt.savefig(output_path)
        plt.close()


        
        
    print(f"Histograms saved to {output_dir}")

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
