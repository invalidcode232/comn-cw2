# Forename: James
# Surname: Sungarda
# Matriculation Number: s2930228

import sys
import time
import select
from socket import socket, AF_INET, SOCK_DGRAM

DATA_SIZE = 1024

remote_host = sys.argv[1]
port = int(sys.argv[2])
filename = sys.argv[3]
retry_timeout = float(sys.argv[4]) / 1000.0  # Convert ms to seconds
window_size = int(sys.argv[5])

sock = socket(AF_INET, SOCK_DGRAM)

# Pre-read the file into packets
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
    sys.exit()

total_packets = len(packets)
base = 0
next_seq = 0

# SR specific tracking arrays
acked = [False] * total_packets
send_times = [0.0] * total_packets

timer_start = time.time()

while base < total_packets:
    # 1. Send new packets that fall within the current window
    while next_seq < base + window_size and next_seq < total_packets:
        sock.sendto(packets[next_seq], (remote_host, port))
        send_times[next_seq] = time.time()
        next_seq += 1

    # 2. Check for incoming ACKs (non-blocking using select)
    # Use a tiny timeout so we can frequently check our individual packet timers
    ready = select.select([sock], [], [], 0.002)

    if ready[0]:
        while True:
            r, _, _ = select.select([sock], [], [], 0)
            if r:
                msg, _ = sock.recvfrom(2)
                ack_seq = int.from_bytes(msg, byteorder="big")

                # Map the modulo sequence number back to our absolute index
                for i in range(base, next_seq):
                    if i % 65536 == ack_seq:
                        acked[i] = True
                        break

                # If the base packet was ACKed, slide the window forward!
                while base < total_packets and acked[base]:
                    base += 1
            else:
                break

    # 3. Check individual timers for unACKed packets in the window
    current_time = time.time()
    for i in range(base, next_seq):
        if not acked[i] and (current_time - send_times[i] > retry_timeout):
            # Timeout occurred for this specific packet! Resend ONLY this one.
            sock.sendto(packets[i], (remote_host, port))
            send_times[i] = current_time

timer_end = time.time()
transfer_time = timer_end - timer_start

# Calculate and strictly print metrics
file_size_kb = total_data_bytes / DATA_SIZE
throughput = file_size_kb / transfer_time if transfer_time > 0 else 0

print(f"{round(throughput)}")
sock.close()
