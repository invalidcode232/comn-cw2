# Forename: James
# Surname: Sungarda
# Matriculation Number: s2930228

import sys
from socket import socket, AF_INET, SOCK_DGRAM

DATA_SIZE = 1024
HEADER_SIZE = 3

port = int(sys.argv[1])
filename = sys.argv[2]

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(("", port))

print(f"Receiver running on port {port} and waiting for '{filename}'...")

with open(filename, "wb") as f:
    while True:
        msg, addr = sock.recvfrom(
            DATA_SIZE + HEADER_SIZE
        )  # Receive a packet (header + data)

        if not msg:
            break

        # Extract header information
        seq_num = int.from_bytes(
            msg[0:2], byteorder="big"
        )  # Sequence number from first 2 bytes
        eof_flag = msg[2]  # EOF flag from the next byte
        data = msg[3:]  # Data starts from the 4th byte

        print(f"Received packet with sequence number {seq_num} and EOF flag {eof_flag}")

        f.write(data)  # Write the data to the file

        if eof_flag == 1:  # If EOF flag is set, we are done
            print("End of file received.")
            break
