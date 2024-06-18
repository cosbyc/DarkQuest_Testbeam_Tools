import os
import numpy as np
import matplotlib.pyplot as plt

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

    # Initialize a list of lists to hold ADC values for each channel
    adc_values = [[] for _ in range(16)]
    emcalCfg = config['emcalCfg']

    # Collect ADC values from each event
    for event in events:
        emcal = event['emcal']
        for row in range(4):
            for col in range(4):
                if emcalCfg[row][col] != 'x':
                    channel = row * 4 + col
                    adc_values[channel].append(emcal[row, col])

    # Plot histograms for each channel
    for channel in range(16):
        row, col = divmod(channel, 4)
        if emcalCfg[row][col] == 'x':
            continue

        plt.figure()
        plt.hist(adc_values[channel], bins=100, color='blue', alpha=0.7, range =(0, 500))
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

