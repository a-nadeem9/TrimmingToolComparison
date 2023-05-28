import sys
import re
import csv

# Function to parse fastq file
def fastq_reader(file="fastq_file"):
    with open(file, "r") as fastq_file:
        for line in fastq_file:
            header_1 = line.rstrip()
            read = next(fastq_file).rstrip()
            header_2 = next(fastq_file).rstrip()
            read_qual_asc = next(fastq_file).rstrip()
            yield header_1, read, header_2, read_qual_asc

# Check command-line arguments
if len(sys.argv) != 3:
    print("Usage: python adapter_length_analysis.py <input_fastq_file> <output_csv_file>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

# Parse the fastq file
simulated_fastq_parse = fastq_reader(file=input_file)

header_r1 = []
true_length_r1 = []
seq_length_r1 = []

# Extract header, true length, and sequence length
pattern = re.compile(r'\d+$')
for record in simulated_fastq_parse: 
    header_1, sequence, header_2, qual = record
    header_items = header_1.split(" ")
    header_r1.append(header_items)
    for item in header_items:
        if item.startswith("TRUE="):
            match = re.search(pattern, item)
            true_length_r1.append(int(match.group()))
        if item.startswith("SEQ_LENGTH="):
            match = re.search(pattern, item)
            seq_length_r1.append(int(match.group()))

adapter_length = [seq_length - true_length for seq_length, true_length in zip(seq_length_r1, true_length_r1)]
total_adapters = len(adapter_length)

# Count adapter lengths
adapter_length_counts = {}
for adapter_length in adapter_length:
    if adapter_length not in adapter_length_counts:
        adapter_length_counts[adapter_length] = 0
    adapter_length_counts[adapter_length] += 1

# Prepare counts for adapter lengths from 1 to 20
counts_1_to_20 = [adapter_length_counts.get(i, 0) for i in range(1, 21)]

# Write adapter length counts to CSV file
with open(output_file, 'w', newline='') as f:
    w = csv.writer(f)
    for i, count in enumerate(counts_1_to_20, start=1):
        w.writerow([i, count])

print("Read length computed successfully")
