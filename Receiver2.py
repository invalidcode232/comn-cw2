# Forename: James
# Surname: Sungarda
# Matriculation Number: s2930228
#
import sys
import socket

port = int(sys.argv[1])
filename = sys.argv[2]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind to all interfaces (empty string) so it works with localhost or real IPs
sock.bind(("", port))

expected_seq_num = 0
MAX_PACKET_SIZE = 1027

with open(filename, "wb") as f:
    while True:
        message, addr = sock.recvfrom(MAX_PACKET_SIZE)

        # Deconstruct header
        seq_num = int.from_bytes(message[0:2], byteorder="big")
        eof_flag = int.from_bytes(message[2:3], byteorder="big")
        data = message[3:]

        # If it is the expected packet, write it and advance our expected number
        if seq_num == expected_seq_num:
            f.write(data)
            expected_seq_num = (expected_seq_num + 1) % 65536

        # Send a 2-byte ACK echoing the received sequence number.
        # Note: If it was a duplicate, this safely ACKs the duplicate so the
        # sender knows it can stop retransmitting it and move on.
        ack_msg = seq_num.to_bytes(2, byteorder="big")
        sock.sendto(ack_msg, addr)

        # Stop listening if we successfully processed the EOF packet
        if eof_flag == 1 and seq_num == (expected_seq_num - 1) % 65536:
            break

sock.close()
