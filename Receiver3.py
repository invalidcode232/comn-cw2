import sys
from socket import socket, AF_INET, SOCK_DGRAM

# python3 Receiver3.py <Port> <Filename>
if len(sys.argv) != 3:
    sys.exit()

port = int(sys.argv[1])
filename = sys.argv[2]

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(("", port))

expected_seq = 0

with open(filename, "wb") as f:
    while True:
        msg, addr = sock.recvfrom(1027)

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
                # Edge case safety: Wait 1 second before fully closing in case
                # our final ACK dropped and the sender retransmits the EOF packet.
                sock.settimeout(1.0)
                try:
                    while True:
                        msg, addr = sock.recvfrom(1027)
                        sock.sendto(seq_num.to_bytes(2, byteorder="big"), addr)
                except:
                    break  # Timeout triggered, safe to close
                break
        else:
            # Out-of-order or duplicate packet! Discard data and resend LAST valid ACK.
            # Example: If expecting 5 but got 6, we re-ACK 4.
            last_ack = (expected_seq - 1) % 65536
            sock.sendto(last_ack.to_bytes(2, byteorder="big"), addr)

sock.close()
