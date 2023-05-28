import sys
import pandas as pd
import csv
import re

# Function to parse fastq file
def fastq_reader(file):
    fastq_file = open(file, "r")
    for line in fastq_file:
        header_1 = line.rstrip()
        read = next(fastq_file).rstrip()
        header_2 = next(fastq_file).rstrip()
        read_qual_asc = next(fastq_file).rstrip()
        yield header_1, read, header_2, read_qual_asc

# Get file paths and CSV file name from command-line arguments
simulated_file = sys.argv[1]
trimmed_file = sys.argv[2]
csv_file_name = sys.argv[3]

# Parsing each file
simulated_fastq_parse = fastq_reader(file=simulated_file)
trimmed_fastq_parse = fastq_reader(file=trimmed_file)


'''
F O R  S I M U L A T E D  R E A D  F I L E
Fetching relevant data.

'''
simulated_readIds = []
simulated_sequences = []
true_length = []

for record in simulated_fastq_parse:
    header_1, sequence, header_2, qual = record
    simulated_readIds.append(header_1.split(" ", 1)[0])
    simulated_sequences.append(sequence)

    # Extract true length from header
    match = re.search(r'TRUE=(\d+)', header_1)
    if match:
        true_length.append(int(match.group(1)))

simulated_reads = [seq[0:n].upper() + seq[n:].lower() for seq, n in zip(simulated_sequences, true_length)]
print("Simulated read processing done.")

'''
F O R  T R I M M E D  R E A D  F I L E
Fetching relevant data.

'''
trimmed_sequences = []

for trimrecord in trimmed_fastq_parse:
    trimheader_1, trimsequence, trimheader_2, fpqual = trimrecord
    trimmed_sequences.append(trimsequence)

trimmed_reads = [seq[0:n].upper() + seq[n:].lower() for seq, n in zip(trimmed_sequences, true_length)]
trimmed_read_length = [len(seq) for seq in trimmed_sequences]
print("Trimmed read processing done.")


'''
Creating a basic csv 

'''
headersCSV = ["ReadID", "SimulatedSequence", "TrimmedSequence"]

with open(csv_file_name, 'w', newline="") as f:
    w = csv.writer(f)
    w.writerow(headersCSV)
    for i in range(len(simulated_readIds)):
        w.writerow([simulated_readIds[i], simulated_reads[i], trimmed_reads[i]])
print("CSV file written successfully.")

# Using Pandas Dataframe to read, write (large) csv file faster.
trimmed_df = pd.read_csv(csv_file_name)

'''
COMPARISON OF TRIMMED AND SIMULATED SEQUENCES

1. classifying whether they are acuurately trimmed, overtrimmed, or undertrimmed.
2. the bases by which the reads are being overtrimmed/undertrimmed.

'''

# 1. classifying whether they are acuurately trimmed, overtrimmed, or undertrimmed.
decision = []

# 2. the bases by which the reads are being overtrimmed/undertrimmed.
difference = []

for trimmed_len, true_len in zip(trimmed_read_length, true_length):
    if trimmed_len == true_len:
        decision.append("accurate")
        difference.append(0)
    elif trimmed_len < true_len:
        decision.append('overtrim')
        difference.append(true_len - trimmed_len)
    else:
        decision.append('undertrim')
        difference.append(trimmed_len - true_len)

print("Comparison completed.")

# Inserting columns in pd dataframe then writing it to the csv file
trimmed_df['TrimVerdict'] = decision
trimmed_df['DifferenceInBases'] = difference

trimmed_df.to_csv(csv_file_name, index=False)
print("CSV file updated successfully.")

