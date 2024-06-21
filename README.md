# DarkQuest Testbeam Tools
## Visualization and analysis tools for DarkQuest EMCal

To configure an analysis, first run:
```
python3 create_config.py
```
Follow the prompts to define the selections you wish to apply to the run file. You can select for combinations of events with threshold requirements for different channels, or cumulative sum of all channels.

For quick low-gain heatmaps of a run file, with no selections, the default configuration 'allChannels.cfg' can be used.


To produce heatmaps and histograms for a given run file and configuration, run:
```
$ python3 analsys.py <Janus_event_list>.txt -c <configuration_file>.cfg -p
```

The `-p` option causes a heat map to be created for every event in run file which passes the configuration selections. Remove it if you only wish to see the average ADC heat map and ADC histograms for each channel. If there are many events in your run, you can terminate the image generation with `ctrl + C` after enough have been generated.

Plots are saved in ./output/run<runNumber>_<configName>/

To see a summary of an active run, type:
```
python3 monitoring.py <current_Janus_event_list>.txt (-c <configuration_file>.cfg)
```
If no configuration file is provided, it will default to an inclusive analysis of all saved events since the last spill, updating every minute.