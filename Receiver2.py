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

expected_seq = 0

with open(filename, "wb") as f:
    while True:
        msg, addr = sock.recvfrom(
            DATA_SIZE + HEADER_SIZE
        )  # Receive a packet (header + data)

        # Deconstruct header
        seq_num = int.from_bytes(msg[0:2], byteorder="big")
        eof_flag = int.from_bytes(msg[2:3], byteorder="big")
        data = msg[3:]

        # If it is the expected packet, write it and advance our expected number
        if seq_num == expected_seq:
            f.write(data)
            expected_seq = (expected_seq + 1) % 65536

        # Send a 2-byte ACK echoing the received sequence number.
        # Note: If it was a duplicate, this safely ACKs the duplicate so the
        # sender knows it can stop retransmitting it and move on.
        ack_msg = seq_num.to_bytes(2, byteorder="big")
        if eof_flag == 1:
            for _ in range(20):
                sock.sendto(ack_msg, addr)
        else:
            sock.sendto(ack_msg, addr)

        # Stop listening if we successfully processed the EOF packet
        if eof_flag == 1 and seq_num == (expected_seq - 1) % 65536:
            break

sock.close()
