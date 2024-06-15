import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib.gridspec as gridspec
from matplotlib import pyplot, image

def plot_event(event, event_number, output_dir, run_number, evn_max_digits):
    emcal = event['emcal']
    minihodoT = event['minihodoT']
    minihodoB = event['minihodoB']
    fig = plt.figure(1, figsize=(5,8))

    evn_string = str(event_number).zfill(evn_max_digits)
    fig.suptitle(f'Run {run_number}, Event {evn_string}')

    gs = gridspec.GridSpec(3,2, height_ratios=[0.2,1,0.2], width_ratios=[1,1])
    gs.update(left=0.05, right=0.95, bottom=0.08, top=0.92, wspace=0.0001, hspace=0.0002)
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

    ax1 = plt.subplot(gs[1,:])
    cax = ax1.imshow(emcal, cmap='viridis', vmin = 0, vmax = 150)
    plt.axis('off')
    #fig.colorbar(cax)
    for (i, j), val in np.ndenumerate(emcal):
        ax1.text(j, i, f'{val}', ha='center', va='center', color='white')

    axt = plt.subplot(gs[0,0])
    plt.margins(y=0)
    plt.axis('off')
    caxt = axt.imshow(np.expand_dims(minihodoT, axis=0), cmap='viridis', aspect = 0.35, vmin = 0, vmax = 7000)
    for i, val in enumerate(minihodoT):
        axt.text( i, 0 , f'{val}', ha='center', va='center', color='white')
    
    axb = plt.subplot(gs[2,0])
    plt.axis('off')
    plt.tight_layout(pad=-5)
    caxb = axb.imshow(np.expand_dims(minihodoB, axis=0), cmap='viridis', aspect = 0.35, vmin = 0, vmax = 7000)
    for i, val in enumerate(minihodoB):
        axb.text( i, 0 , f'{val}', ha='center', va='center', color='white')
    axb.set_adjustable('box')

    output_path = os.path.join(output_dir, f'event_{evn_string}.png')
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0.25)
