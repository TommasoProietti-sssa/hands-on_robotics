import struct
import json
import csv
import os
import random

# Define output file names
binary_file = "log.bin"
csv_file = "log.csv"
json_file = "log.json"

# Number of samples
n_samples = 1000

# Generate a random sample
def generate_sample(ts):
    return {
        "timestamp": ts,
        "data_1": random.uniform(-1.0, 1.0),
        "data_2": random.uniform(-1.0, 1.0),
        "event": random.randint(0, 5)
    }

# ---- BINARY LOGGING ----
with open(binary_file, "wb") as f_bin:
    for i in range(n_samples):
        sample = generate_sample(ts=1000000 + i * 100)
        f_bin.write(struct.pack('<IffB', # '<I' for unsigned int, 'ff' for two floats, 'B' for unsigned char
                                sample["timestamp"],
                                sample["data_1"],
                                sample["data_2"],
                                sample["event"]))

# ---- CSV LOGGING ----
with open(csv_file, "w", newline='') as f_csv:
    writer = csv.writer(f_csv)
    writer.writerow(["timestamp", "data_1", "data_2", "event"])  # header
    for i in range(n_samples):
        sample = generate_sample(ts=1000000 + i * 100)
        writer.writerow([sample["timestamp"],
                         sample["data_1"],
                         sample["data_2"],
                         sample["event"]])

# ---- JSON LOGGING ----
json_data = []
for i in range(n_samples):
    sample = generate_sample(ts=1000000 + i * 100)
    json_data.append(sample)

with open(json_file, "w") as f_json:
    json.dump(json_data, f_json, indent=2)

# ---- FILE SIZE COMPARISON ----
file_sizes = {
    "Binary (.bin)": os.path.getsize(binary_file),
    "CSV (.csv)": os.path.getsize(csv_file),
    "JSON (.json)": os.path.getsize(json_file)
}

print("File Size Comparison (in bytes):")
for fmt, size in file_sizes.items():
    print(f"{fmt:<15}: {size / 1024:.1f} KB")
