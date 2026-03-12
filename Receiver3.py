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
        msg, addr = sock.recvfrom(DATA_SIZE + HEADER_SIZE)

        seq_num = int.from_bytes(msg[0:2], byteorder="big")
        eof_flag = int.from_bytes(msg[2:3], byteorder="big")
        data = msg[3:]

        if seq_num == expected_seq:
            # In-order packet received! Write data and move expectation forward.
            f.write(data)
            sock.sendto(seq_num.to_bytes(2, byteorder="big"), addr)

            expected_seq = (expected_seq + 1) % 65536

            # If this was the last packet, gracefully exit
            if eof_flag == 1:
                # Set a 1-second timeout. If we don't hear anything for 1 second,
                # we assume the sender got our ACK and we can safely close.
                sock.settimeout(1.0)
                try:
                    while True:
                        # Wait to see if the sender retransmits the EOF packet
                        msg, addr = sock.recvfrom(1027)

                        # If they do, just resend the ACK! No need to write data.
                        sock.sendto(seq_num.to_bytes(2, byteorder="big"), addr)
                except Exception:
                    break  # Safe to close!
        else:
            # Out-of-order or duplicate packet! Discard data and resend LAST valid ACK.
            # Example: If expecting 5 but got 6, we re-ACK 4.
            last_ack = (expected_seq - 1) % 65536
            sock.sendto(last_ack.to_bytes(2, byteorder="big"), addr)

sock.close()
