import os

def trigIdSort(input_filename, run_number):
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

    missingIds=0
    brokenEvents=0
    for i in range(max(events.keys())):
        if i not in events:
            missingIds+=1
            #print(f'Trigger ID {i} is missing.')
    
    for trigID in sorted(events.keys()):
        event = events[trigID]
        if len(event[1]) == 16 and len(event[0]) == 4:
            correctedLines.extend(event[1])
            correctedLines.extend(event[0])
        else:
            brokenEvents+=1
            #print(f"Event {trigID} found incomplete when unscrambling... Skipping for now. Check input file.")
    if missingIds > 0:
        print(f'Found {missingIds} missing trigger IDs when parsing input.')
    if brokenEvents > 0:
        print(f'{brokenEvents} EMCal events could not be matched with a hodoscope events.\n')
    
    with open(f'runFiles/Run{run_number}_list_trigID_sorted.txt', 'w') as file:
        file.writelines(header)
        file.writelines(correctedLines)

def bufferSort(input_filename, run_number):
    with open(input_filename, 'r') as file:
        lines = file.readlines()

    header = lines[:9]
    data = lines[9:]

    emcalEvents = []
    hodoEvents = []

    for line in data:
        parts = line.strip().split()
        #if len(parts) < 6:
        #    continue

        board = int(parts[0])

        if board == 1:
            emcalEvents.append(line)
        elif board == 0:
            hodoEvents.append(line)

    correctedLines = []
    buffer = []

    while emcalEvents:
        buffer.extend(emcalEvents[:16])
        del emcalEvents[:16]

        if len(buffer) == 16 and hodoEvents:
            buffer.extend(hodoEvents[:4])
            del hodoEvents[:4]
            correctedLines.extend(buffer)
            buffer = []

    if buffer:
        print(f"Warning: Incomplete event(s) detected. Buffered lines hanging: {len(buffer)}")
        #for i in range(len(buffer)):
        #    print(f"{buffer[i]}")

    with open(f'runFiles/Run{run_number}_list_buffer_sorted.txt', 'w') as file:
        file.writelines(header)
        file.writelines(correctedLines)

