# TODO: replace this comment with your Forename, Surname, and Matriculation Number

import sys
import socket
import struct
import time
import os

remoteHost = sys.argv[1]
port = int(sys.argv[2])
filename = sys.argv[3]
retryTimeout = int(sys.argv[4])


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(retryTimeout / 1000.0)

    seq_num = 0
    retransmissions = 0

    file_size_bytes = os.path.getsize(filename)

    start_time = 0
    end_time = 0
    first_packet = True

    with open(filename, "rb") as f:
        while True:
            chunk = f.read(1024)
            eof = 1 if len(chunk) < 1024 else 0

            header = struct.pack(">H B", seq_num, eof)
            packet = header + chunk

            consecutive_timeouts = 0

            ack_received = False

            sock.sendto(packet, (remoteHost, port))

            while not ack_received:
                if first_packet:
                    start_time = time.time()
                    first_packet = False

                try:
                    ack_packet, _ = sock.recvfrom(2048)
                    ack_seq = struct.unpack(">H", ack_packet[:2])[0]

                    if ack_seq == seq_num:
                        ack_received = True
                        if eof == 1:
                            end_time = time.time()
                        break
                except socket.timeout:
                    retransmissions += 1
                    consecutive_timeouts += 1

                    sock.sendto(packet, (remoteHost, port))

                    if eof == 1 and consecutive_timeouts >= 20:
                        if end_time == 0:
                            end_time = max(
                                start_time, time.time() - (20 * retryTimeout / 1000.0)
                            )
                        break

            if eof == 1:
                break

            seq_num = (seq_num + 1) % 65536

    sock.close()

    transfer_time = end_time - start_time
    if transfer_time <= 0:
        transfer_time = 0.0001

    file_size_kb = file_size_bytes / 1024.0
    throughput = file_size_kb / transfer_time

    print(f"{retransmissions} {int(round(throughput))}")


if __name__ == "__main__":
    main()
