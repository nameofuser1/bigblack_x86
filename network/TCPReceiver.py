from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import Event

import sys
import socket

import network.network_exceptions as ex

import logging

if sys.version_info <= (3, 3):
    from Queue import Empty
else:
    from queue import Empty


class TCPReceiver(object):

    def __init__(self, sock_):
        self.sock = sock_
        self.packet_length = 0
        self.packets_queue = Queue()
        self.stop_event = Event()
        self.proc = None

        self.network_logger = logging.getLogger("network_logger")

    def __recv_n_bytes(self, sock, n):
        data = bytearray()
        remaining_bytes = n

        while remaining_bytes > 0:
            buf = bytearray(sock.recv(remaining_bytes))

            if len(buf) == 0:
                raise socket.timeout()

            data.extend(buf)
            remaining_bytes -= len(buf)

        return data

    def listen_proc(self, pack_queue, sock, stop_event):
        sock.settimeout(1)
        packet_length = 0

        while not stop_event.is_set():
            try:
                if packet_length == 0:
                    length = self.__recv_n_bytes(sock, 2)

                    packet_length = ((int(length[0]) << 8) & 0xFF00) |\
                        (int(length[1]) & 0xFF)

                    self.network_logger.debug("Got packet length: " +
                                              str(packet_length))

                else:
                    data = self.__recv_n_bytes(sock, packet_length - 2)

                    packet = bytearray(2)
                    packet[0] = (packet_length >> 8) & 0xFF
                    packet[1] = packet_length & 0xFF

                    for byte in data:
                        packet.append(int(byte))

                    self.network_logger.debug("Received full packet")
                    packet_length = 0
                    pack_queue.put(packet)

            except socket.timeout:
                print("TIMEOUT WHILE READING TCP RECEIVER")

    def start(self):
        if self.proc is None:
            self.stop_event.clear()
            self.proc = Process(target=self.listen_proc,
                                args=(self.packets_queue,
                                      self.sock,
                                      self.stop_event))
            self.proc.start()

    def stop(self):
        if self.proc is not None:
            self.network_logger.debug("Stopping listener...")

            self.stop_event.set()
            self.proc.join()
            self.proc = None

            self.network_logger.debug("Stopped listener")
            # self.packets_queue.put("Stop")

    def available(self):
        return not self.packets_queue.empty()

    def read(self, timeout=None):
        try:
            return self.packets_queue.get(block=True, timeout=timeout)
        except Empty:
            raise ex.NetworkTimeoutError()
