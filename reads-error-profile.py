import re
import csv
import sys

'''
The following is the header of simulated reads file:

@PeReadSimulator2:1:1 TRUE=80 INSERT_SIZE=80 ERROR_RATE=0.00102 SEQ_LENGTH=100 ERROR_INSERT=0

Where
    TRUE = The length of the real inserted DNA.
    INSERT_SIZE = The length of the original inserted DNA before error simulation. (Indel might be introduced in error simulation, so the real insert size might vary.)

[Source: Atria Docs "https://github.com/cihga39871/Atria/blob/master/docs/3.Benchmark_toolkit.md"]

Therefore
    Substitution => if INSERT_SIZE == TRUE
    Deletion => if INSERT_SIZE > TRUE
    Insertion => if INSERT_SIZE < TRUE

'''

# Function to parse fastq file
def fastq_reader(file_path):
    with open(file_path, "r") as fastq_file:
        for line in fastq_file:
            header_1 = line.rstrip()
            read = next(fastq_file).rstrip()
            header_2 = next(fastq_file).rstrip()
            read_qual_asc = next(fastq_file).rstrip()
            yield header_1, read, header_2, read_qual_asc

# Check if the file path is provided as a command-line argument
if len(sys.argv) > 1:
    file_path = sys.argv[1]
else:
    # Prompt the user to enter the file path
    file_path = input("Enter the file path: ")

# Parsing the fastq file
simulated_fastq_parse = fastq_reader(file_path=file_path)

# Extracting error header list
error_header_lst = []
pattern = re.compile(r'ERROR_INSERT=(\d+)')
for record in simulated_fastq_parse:
    header_1, sequence, header_2, qual = record
    match = re.search(pattern, header_1)
    if match:
        error_insert = int(match.group(1))
        if error_insert > 0:
            error_header_lst.append(header_1.split())

print('error:', len(error_header_lst))

# Extracting true length and insert length
true_length = []
insert_length = []
pattern = re.compile(r'TRUE=(\d+)')
insert_size_pattern = re.compile(r'INSERT_SIZE=(\d+)')
for header in error_header_lst:
    for item in header:
        if item.startswith("TRUE="):
            match = re.search(pattern, item)
            true_length.append(int(match.group(1)))
        elif item.startswith("INSERT_SIZE="):
            match = re.search(insert_size_pattern, item)
            insert_length.append(int(match.group(1)))

print('true:', len(true_length))
print('insert:', len(insert_length))

# Calculating counts for substitution, deletion, and insertion
count_substitution = sum([1 for i in range(len(true_length)) if insert_length[i] == true_length[i]])
count_deletion = sum([1 for i in range(len(true_length)) if insert_length[i] > true_length[i]])
count_insertion = sum([1 for i in range(len(true_length)) if insert_length[i] < true_length[i]])

print("substitution: ", count_substitution)
print("deletion: ", count_deletion)
print("insertion: ", count_insertion)
