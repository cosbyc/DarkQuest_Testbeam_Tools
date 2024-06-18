def get_threshold(prompt):
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("Please enter a valid integer.")

def get_emcal_layout(prompt):
    layout = []
    print(prompt)
    print(f"Enter 4 rows of 4 characters each OR press ENTER to enable all channels.")

    done = False
    for i in range(4):
        while done == False:
            row = input(f"EMCal row {i + 1}: ").replace(" ", "").strip()
            if len(row) == 4 and all(c in 'oxTVS' for c in row):
                layout.append(list(row))
                break
            elif len(row) == 0 and i == 0:
                for j in range(4):
                    layout.append('oooo')
                    print('oooo')
                done = True
                break
            else:
                print(f"Invalid row. Each row must be exactly 4 characters long and contain only 'o', 'x', 'T', or 'V'.")
    return layout

def get_hodo_layout(prompt):
    layout = []
    print(prompt)
    while True:
        row = input(f"Hodoscope: ").replace(" ", "").strip()
        if len(row) == 4 and all(c in 'oxTV' for c in row):
            layout.append(list(row))
            break
        else:
            print(f"Invalid row. Each row must be exactly 4 characters long and contain only 'o', 'x', 'T', or 'V'.")
    return layout

def write_config_file(name, top_rows, main_detector, bottom_rows, t_thresh, v_thresh, s_thresh, tag):
    with open(f'{name}.cfg', 'w') as file:
        file.write(f"{name}\n")
        file.write("Modify the diagram below to represent the detector channels included in your run\n")
        file.write("(exact spacing needs not be perserved)\n")
        file.write("\n")
        file.write("  o  - Channel is enabled in the run and will have an ADC value in each event.\n")
        file.write("  x  - Channel is disabled in the run and will not have an ADC value. This applies to slots where the hodoscope are not sitting.\n")
        file.write("  T  - Triggered channel, which is also wanted for the offline analysis. This channel must read above T-thresh to be included in event loop.\n")
        file.write("  V  - Vetoed channel which is not desired in analyzed events. This channel must read below V-thresh to be included in the event loops.\n")
        file.write("  S  - Channels to have their ADC summed, for a the total ADC calculation, and compared to the cut-off\n")
        file.write("\n")
        file.write("________________________________________\n ")


        for row in top_rows:
            file.write(' '.join(row) + '\n')

        file.write("_________\n")

        for row in main_detector:
            file.write('|' + ' '.join(row) + '|\n')

        file.write("¯¯¯¯¯¯¯¯¯\n ")

        for row in bottom_rows:
            file.write(' '.join(row) + '\n')
        file.write("________________________________________\n")
        file.write("\n")
        file.write(f"T-thresh = {t_thresh}\n")
        file.write(f"V-thresh = {v_thresh}\n")
        file.write(f"S-thresh = {s_thresh}\n")
        file.write(f"Tag: {tag}\n")

def main():
    print("Create Detector Configuration File")
    name = input("Give this configuration a short, descriptive title: ").replace(" ", "").strip()

    print("Use 'o' for enabled channels, 'x' for disabled channels, 'T' for triggered channels, 'V' for vetoed channels, and 'S' for channels that you want to get summed ADC of.")

    top_rows = get_hodo_layout("\nTop Hodoscope Layout (enter 'xxxx' if not using hodoscopes):")
    
    main_detector = get_emcal_layout("\nEMCal Layout (4x4):")
    
    bottom_rows = get_hodo_layout("\nBottom Hodoscopes Layout (enter 'xxxx' if not using hodoscopes):")

    t_thresh = v_thresh = s_thresh = -1
    if (('T' in top_rows[0]) or  ('T' in bottom_rows[0]) or  ('T' in main_detector[0] or  ('T' in main_detector[1]) or  ('T' in main_detector[2]) or  ('T' in main_detector[3]))):
        t_thresh = get_threshold("Enter the T-thresh value: ")
    if (('V' in top_rows[0]) or  ('V' in bottom_rows[0]) or  ('V' in main_detector[0] or  ('V' in main_detector[1]) or  ('V' in main_detector[2]) or  ('V' in main_detector[3]))):
        v_thresh = get_threshold("Enter the V-thresh value: ")
    if (('S' in main_detector[0] or  ('S' in main_detector[1]) or  ('S' in main_detector[2]) or  ('S' in main_detector[3]))):
        s_thresh = get_threshold("Enter the S-thresh value: ")
    tag = input("(Optional) Enter a short description of this configuration: ")
    
    write_config_file(f'{name}', top_rows, main_detector, bottom_rows, t_thresh, v_thresh, s_thresh, tag)
    
    print(f"\nConfiguration file '{name}.cfg' created successfully!")

if __name__ == "__main__":
    main()
