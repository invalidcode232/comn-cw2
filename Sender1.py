# Forename: James
# Surname: Sungarda
# Matriculation Number: s2930228

import sys
from socket import socket, AF_INET, SOCK_DGRAM

remote_host = sys.argv[1]
port = int(sys.argv[2])
filename = sys.argv[3]

# As specified by the requirements
DATA_SIZE = 1024

sock = socket(AF_INET, SOCK_DGRAM)

print(
    f"Sender running on port {port} and sending '{filename}' to {remote_host}:{port}..."
)

# Keep track of our sequence number
seq_num = 0

try:
    with open(filename, "rb") as f:
        # Read a chunk of data of size specified by DATA_SIZE
        cur_chunk = f.read(DATA_SIZE)

        while cur_chunk:
            # Check if we have reached the end of the file for this chunk
            next_chunk = f.read(DATA_SIZE)
            eof_flag = 1 if not next_chunk else 0

            # Define header
            header = (seq_num % 65536).to_bytes(2, byteorder="big")
            header += eof_flag.to_bytes(1, byteorder="big")

            packet = header + cur_chunk

            # Send the packet
            sock.sendto(packet, (remote_host, port))
            print(f"Sent packet with sequence number {seq_num} and EOF flag {eof_flag}")

            seq_num += 1
            cur_chunk = next_chunk
except FileNotFoundError:
    print(f"File '{filename}' not found.")
    sys.exit()
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit()
finally:
    print("File sent successfully.")
    sock.close()
