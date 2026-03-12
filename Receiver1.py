# Forename: James
# Surname: Sungarda
# Matriculation Number: s2930228

from socket import socket, AF_INET, SOCK_DGRAM
import sys

port = int(sys.argv[1])
filename = sys.argv[2]

IP = "127.0.0.1"

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind((IP, port))

print(f"Receiver running on port {port} and waiting for '{filename}'...")

with open(filename, "wb") as f:
    while True:
        packet, addr = sock.recvfrom(1027)  # Receive a packet (header + data)

        if not packet:
            break

        # Extract header information
        seq_num = int.from_bytes(
            packet[0:2], byteorder="big"
        )  # Sequence number from first 2 bytes
        eof_flag = packet[2]  # EOF flag from the next byte
        data = packet[3:]  # Data starts from the 4th byte

        print(f"Received packet with sequence number {seq_num} and EOF flag {eof_flag}")

        f.write(data)  # Write the data to the file

        if eof_flag == 1:  # If EOF flag is set, we are done
            print("End of file received.")
            break
