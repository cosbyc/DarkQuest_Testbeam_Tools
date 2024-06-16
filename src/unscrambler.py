import os

def fixTriggerOrder(input_filename):
    with open(input_filename, 'r') as file:
        lines = file.readlines()

    header = lines[:9]
    data = lines[9:]

    events = {}
    currentTrigID = 0

    for line in data:
        parts = line.strip().split()
        
        if len(parts) == 7:
            board = int(parts[0])
            trigID = int(parts[5]);
            currentTrigID = trigID
            if trigID not in events:
                events[trigID] = {0: [], 1: []}
            events[trigID][board].append(line)
        elif len(parts) == 4:
            board = int(parts[0])
            events[currentTrigID][board].append(line)

    correctedLines = []

    #for i in range(2409):
    #    if i not in events:
    #        print(f'Trigger ID {i} is missing.')
    
    for trigID in sorted(events.keys()):
        event = events[trigID]
        if len(event[1]) == 16 and len(event[0]) == 4:
            correctedLines.extend(event[1])
            correctedLines.extend(event[0])
    #    else:
    #        print(f"Event {trigID} found incomplete when unscrambling... Skipping for now. Check input file.")

    with open('tmp.txt', 'w') as file:
        file.writelines(header)
        file.writelines(correctedLines)

        

