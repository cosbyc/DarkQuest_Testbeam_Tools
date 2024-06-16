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
    print(f"Enter 4 rows of 4 characters each.")

    for i in range(4):
        while True:
            row = input(f"EMCal row {i + 1}: ").replace(" ", "").strip()
            if len(row) == 4 and all(c in 'oxTV' for c in row):
                layout.append(list(row))
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

def write_config_file(filename, top_rows, main_detector, bottom_rows, t_thresh, v_thresh):
    with open(filename, 'w') as file:
        file.write("EMCAL Run Layout\n")
        file.write("Modify the diagram below to represent the detector channels included in your run\n")
        file.write("(exact spacing needs not be perserved)\n")
        file.write("\n")
        file.write("  o  - Channel is enabled in the run and will have an ADC value in each event.\n")
        file.write("  x  - Channel is disabled in the run and will not have an ADC value. This applies to slots where the hodoscope are not sitting.\n")
        file.write("  T  - Triggered channel, which is also wanted for the offline analysis. This channel must read above T-thresh to be included in event loop.\n")
        file.write("  V  - Vetoed channel which is not desired in analyzed events. This channel must read below V-thresh to be included in the event loops.\n")
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

def main():
    print("Create Detector Configuration File")
    filename = input("Enter the configuration file name: ").strip()

    print("Use 'o' for enabled channels, 'x' for disabled channels, 'T' for triggered channels, 'V' for vetoed channels.")

    top_rows = get_hodo_layout("\nTop Hodoscope Layout (enter 'xxxx' if not using hodoscopes):")
    
    main_detector = get_emcal_layout("\nEMCal Layout (4x4):")
    
    bottom_rows = get_hodo_layout("\nBottom Hodoscopes Layout (enter 'xxxx' if not using hodoscopes):")
    
    t_thresh = get_threshold("Enter the T-thresh value: ")
    v_thresh = get_threshold("Enter the V-thresh value: ")
    
    write_config_file(filename, top_rows, main_detector, bottom_rows, t_thresh, v_thresh)
    
    print(f"\nConfiguration file '{filename}' created successfully!")

if __name__ == "__main__":
    main()
