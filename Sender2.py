# Forename: James
# Surname: Sungarda
# Matriculation Number: s2930228

from socket import socket, AF_INET, SOCK_DGRAM, timeout
import time
import sys

remote_host = sys.argv[1]
port = int(sys.argv[2])
filename = sys.argv[3]
retry_timeout = int(sys.argv[4])

# As specified by the requirements
DATA_SIZE = 1024

# (DATA_SIZE + 3 bytes) = 1027 bytes packet size with 10 Mbps bandwidth
# SLEEP_TIME = DATA_SIZE / 1250000.0

sock = socket(AF_INET, SOCK_DGRAM)

# Part 2: configure the socket to have timeout specified in retry_timeout_ms
sock.settimeout(retry_timeout / 1000.0)

print(
    f"Sender running on port {port} and sending '{filename}' to {remote_host}:{port}..."
)

# Keep track of our sequence number
seq_num = 0

# Part 2: Variables for metrics calculation
# Keep track of timer
timer_start = None
timer_end = None

# Keep track of retransmissions, which would be incremented in the case of a timeout
retransmissions = 0

# Keep track of bytes read
total_data_bytes = 0

try:
    with open(filename, "rb") as f:
        # Read a chunk of data of size specified by DATA_SIZE
        cur_chunk = f.read(DATA_SIZE)

        while cur_chunk:
            total_data_bytes += len(cur_chunk)

            # Check if we have reached the end of the file for this chunk
            next_chunk = f.read(DATA_SIZE)
            eof_flag = 1 if not next_chunk else 0

            # Define header
            header = (seq_num % 65536).to_bytes(
                2, byteorder="big"
            )  # 3-byte header for sequence number
            header += eof_flag.to_bytes(
                1, byteorder="big"
            )  # 1-byte header for EOF flag

            packet = header + cur_chunk

            # In part 1, we would send the packet here
            # sock.sendto(packet, (remoteHost, port))

            # Part 2: Stop and wait
            ack_received = False

            # Start timer if it hasn't started yet
            if timer_start is None:
                timer_start = time.time()

            while not ack_received:
                sock.sendto(packet, (remote_host, port))
                try:
                    ack_data, _ = sock.recvfrom(
                        2
                    )  # Expecting a 2-byte ACK with seq number

                    if (
                        int.from_bytes(ack_data, byteorder="big") % 65536
                        == seq_num % 65536
                    ):
                        ack_received = True

                        if eof_flag == 1:
                            timer_end = time.time()
                    else:
                        print(
                            f"Unexpected ACK received: {ack_data}. Expected: {seq_num % 65536}"
                        )
                except timeout as te:
                    print(
                        f"Timeout waiting for ACK for sequence number {seq_num - 1}. Resending packet | err: {te}"
                    )
                    retransmissions += 1
                except Exception as e:
                    print(f"Err: {e}")

            # Package sent and received
            seq_num += 1
            cur_chunk = next_chunk
            # time.sleep(SLEEP_TIME) # Sleep to simulate bandwidth limit
except FileNotFoundError:
    print(f"File '{filename}' not found.")
    sys.exit()
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit()

# Calculate metrics and output it
if timer_start is not None and timer_end is not None:
    transfer_time = timer_end - timer_start
    file_size_kb = total_data_bytes / DATA_SIZE  # Convert bytes to KB
    throughput = file_size_kb / transfer_time if transfer_time > 0 else 0

    # Strict single-line output: <retransmissions> <throughput_in_KB/s>
    print(f"{retransmissions} {round(throughput)}")
else:
    print("Could not calculate metrics due to missing timer values.")

sock.close()
