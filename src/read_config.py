import os

def readConfig(config_filename, talk = True):
    try:
        with open(config_filename, 'r') as file:
            lines = file.readlines()
    except:
        print('Could not load configiration...')
        exit()

    config = []
    t_thresh = 0
    v_thresh = 0
    s_thresh = 0
    s_max = 0
    gain = 'LG'
    timerange = [-1,-1]
    
    tag=''
    name = lines[0]
    for line in lines[11:]:
        stripped = line.strip()
        if stripped.startswith('#'):
            continue
        if 'T-thresh' in stripped:
            t_thresh = int(stripped.split('=')[1])
        elif 'V-thresh' in stripped:
            v_thresh = int(stripped.split('=')[1])
        elif 'S-thresh' in stripped:
            s_thresh = int(stripped.split('=')[1])
        elif 'S-max' in stripped:
            s_max = int(stripped.split('=')[1])
        elif 'Gain= ' in stripped:
            gain = stripped.split('=')[1].stripped()
        elif 'Tag:' in stripped:
            tag = stripped[4:]
        elif stripped:
            if stripped[0] in 'TxVo|S':
                config.append(stripped)

    emcal_cfg = []
    top_hodo_cfg = []
    bottom_hodo_cfg = []
    current_section = 'top'
    
    for row in config:
        if current_section == 'top':
            top_hodo_cfg.append(row.split())
            current_section = 'emcal'
        elif current_section == 'emcal' and len(emcal_cfg)!=4:
            emcal_cfg.append(row.strip('|').split())
        else:
            bottom_hodo_cfg.append(row.split())

    allConfiguration= {
        'name' : name,
        'tag' : tag,
        'triggerThresh' : t_thresh,
        'vetoThresh' : v_thresh,
        'sumThresh' : s_thresh,
        'sumMax' : s_max,
        'gain' : gain,
        'emcalCfg' : emcal_cfg,
        'topHodoCfg' : top_hodo_cfg[0],
        'bottomHodoCfg' : bottom_hodo_cfg[0],
        'topHodoEnabled' : not all(channel == 'x' for channel in top_hodo_cfg[0]), # true, unless all channels are 'x'
        'botHodoEnabled' : not all(channel == 'x' for channel in bottom_hodo_cfg[0])
    }

    if talk == True:
        if config_filename == '.previous_run.cfg':
            print(f'No config file provided.\n')
            print(f'Loading previous settings...\n')
        else:
            print(f'Loading {config_filename}...\n')
            os.system(f'cp {config_filename} .previous_run.cfg')
            print('Detector configuration:')
            for i in range(11,19):
                print(lines[i],end='')
            print('')
            print(f'Trigger threshold = {t_thresh}')
            print(f'Veto threshold = {v_thresh}')
            print(f'Sum threshold = {s_thresh}')
            if (s_max < 128400):
                print(f'Sum max = {s_max}')

            print(f'\nAnalyzing {gain} channel')
        if ((allConfiguration['topHodoEnabled'] or allConfiguration['botHodoEnabled']) and (talk==True)):
            print('\nHodoscope channels enabled in config. Expecting a run file with external trigger info.')
        elif(talk==True):
            print('\nHodoscopes disabled in config. Expecting a self triggered run file.')
        print('')
    return allConfiguration
