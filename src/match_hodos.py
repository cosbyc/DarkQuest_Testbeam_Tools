import os
def bufferSortEvents(input_filename, output_filename):
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

    corrected_lines = []
    buffer = []

    while emcalEvents:
        buffer.extend(emcalEvents[:16])
        del emcalEvents[:16]

        if len(buffer) == 16 and hodoEvents:
            buffer.extend(hodoEvents[:4])
            del hodoEvents[:4]
            corrected_lines.extend(buffer)
            buffer = []

    if buffer:
        print(f"Warning: Incomplete event(s) detected. Buffered lines hanging: {len(buffer)}")
        for i in range(len(buffer)):
            print(f"{buffer[i]}")

    with open(output_filename, 'w') as file:
        file.writelines(header)
        file.writelines(corrected_lines)

    with open(f'runFiles/Run{run_number}_list_buffer_sorted.txt', 'w') as file:
        file.writelines(header)
        file.writelines(correctedLines)

if __name__ == "__main__":
    main()
