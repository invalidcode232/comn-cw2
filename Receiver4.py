# Forename: James
# Surname: Sungarda
# Matriculation Number: s2930228

import sys
from socket import socket, AF_INET, SOCK_DGRAM

DATA_SIZE = 1024

port = int(sys.argv[1])
filename = sys.argv[2]
window_size = int(sys.argv[3])

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(("", port))

rcv_base = 0
buffer = {}

with open(filename, "wb") as f:
    while True:
        msg, addr = sock.recvfrom(DATA_SIZE + 3)

        seq_num = int.from_bytes(msg[0:2], byteorder="big")
        eof_flag = int.from_bytes(msg[2:3], byteorder="big")
        data = msg[3:]

        # Calculate distance to handle wrapping sequence numbers safely
        dist = (seq_num - (rcv_base % 65536)) % 65536

        if dist < window_size:
            # Packet falls perfectly inside our receiving window!
            sock.sendto(seq_num.to_bytes(2, byteorder="big"), addr)

            absolute_seq = rcv_base + dist
            if absolute_seq not in buffer:
                buffer[absolute_seq] = (data, eof_flag)

            # If we finally got the base packet, write it and any consecutive buffered packets
            while rcv_base in buffer:
                buffered_data, buffered_eof = buffer.pop(rcv_base)
                f.write(buffered_data)

                if buffered_eof == 1:
                    # Final packet reached. Wait slightly to catch trailing lost ACKs
                    sock.settimeout(1.0)
                    try:
                        while True:
                            msg, addr = sock.recvfrom(DATA_SIZE + 3)
                            resend_seq = msg[0:2]
                            sock.sendto(resend_seq, addr)
                    except Exception:
                        pass
                    sock.close()
                    sys.exit()

                rcv_base += 1

        else:
            # The packet is outside our window. It is likely an old packet whose
            # ACK was lost. We MUST re-ACK it so the sender's timer stops.
            dist_prev = ((rcv_base % 65536) - seq_num) % 65536
            if dist_prev <= window_size and dist_prev > 0:
                sock.sendto(seq_num.to_bytes(2, byteorder="big"), addr)
