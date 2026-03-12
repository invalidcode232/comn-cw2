# Forename: James
# Surname: Sungarda
# Matriculation Number: s2930228

import sys
import time
import select
from socket import socket, AF_INET, SOCK_DGRAM

remote_host = sys.argv[1]
port = int(sys.argv[2])
filename = sys.argv[3]
retry_timeout = float(sys.argv[4]) / 1000.0
window_size = int(sys.argv[5])

# As specified by the requirements
DATA_SIZE = 1024

sock = socket(AF_INET, SOCK_DGRAM)

# Pre-read the entire file into packet chunks for easier window management
packets = []
total_data_bytes = 0

try:
    with open(filename, "rb") as f:
        chunk = f.read(DATA_SIZE)
        seq_num = 0
        while chunk:
            total_data_bytes += len(chunk)
            next_chunk = f.read(DATA_SIZE)
            eof_flag = 1 if not next_chunk else 0

            header = (seq_num % 65536).to_bytes(2, byteorder="big")
            header += eof_flag.to_bytes(1, byteorder="big")

            packets.append(header + chunk)
            chunk = next_chunk
            seq_num += 1
except FileNotFoundError:
    print(f"File '{filename}' not found.")
    sys.exit()

# Part 3: GBN Variables
base = 0
next_seq = 0
total_packets = len(packets)

timer_start = time.time()

# Sliding Window Loop
while base < total_packets:
    # 1. Fill the window: Send packets until we hit the Window Size limit
    while next_seq < base + window_size and next_seq < total_packets:
        sock.sendto(packets[next_seq], (remote_host, port))
        next_seq += 1

    # 2. Wait for ACKs (up to our timeout limit)
    # select.select() pauses until the socket has data OR the timeout is reached
    ready_to_read, _, _ = select.select([sock], [], [], retry_timeout)

    if ready_to_read:
        # We received at least one ACK. Drain the buffer of ALL available ACKs.
        while True:
            # Check if there are more ACKs waiting instantly (timeout=0)
            r, _, _ = select.select([sock], [], [], 0)
            if r:
                ack_data, _ = sock.recvfrom(2)
                ack_seq = int.from_bytes(ack_data, byteorder="big")

                # Check if this ACK is in our currently outstanding window
                outstanding_seqs = [(base + i) % 65536 for i in range(next_seq - base)]

                if ack_seq in outstanding_seqs:
                    # Cumulative ACK: Slide the window forward!
                    steps_forward = outstanding_seqs.index(ack_seq) + 1
                    base += steps_forward
            else:
                # The ACK buffer is empty, break out and send more packets
                break
    else:
        # 3. Timeout Occurred!
        # Go-Back-N dictates we reset next_seq to the base and resend the whole window.
        next_seq = base

timer_end = time.time()
transfer_time = timer_end - timer_start

# Calculate and print metrics strictly
file_size_kb = total_data_bytes / DATA_SIZE
throughput = file_size_kb / transfer_time if transfer_time > 0 else 0

print(f"{round(throughput)}")
sock.close()
