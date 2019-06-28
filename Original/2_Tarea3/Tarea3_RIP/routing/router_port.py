from queue import Queue
from threading import Thread
import socket
import json


class RouterPort(Thread):
    def __init__(self, input_port, output_port, cost, callback_new_packet):
        Thread.__init__(self)
        self.input_port = input_port
        self.output_port = output_port
        self.listener = None
        self.callback_method = callback_new_packet
        self.queue = Queue()
        self.running = True
        self.jump_cost = cost

    def name_request(self):
        """
        request end-point neighbours's name
        for this connection
        :return: void
        """

        message = json.dumps({'destination': "unknown",
                             'type': "name_request", 'data': "request for name"}).encode()
        self.queue.put(message)

    def name_response(self, name):
        """
        sends this routers name to end-point neighbour
        :param name: name of this router
        :return: void
        """
        message = json.dumps({'destination': "unknown", 'type': "name_response",
                              'data': name, 'cost': self.jump_cost}).encode()
        self.queue.put(message)

    def _manage_output_packet(self):
        """
        Internal method to send packets.
        :return: None
        """
        while not self.queue.empty():
            packet = self.queue.get()

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_address = ('localhost', self.output_port)

            try:
                sock.sendto(packet, server_address)
            finally:
                sock.close()

    def _get_packets(self):
        """
        Internal method to get the packets from the socket and send them to the
        orchestrator to deliver them to the correct owner.
        :return: None
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to the port
        server_address = ('localhost', self.input_port)
        sock.bind(server_address)

        while self.running:
            data, address = sock.recvfrom(1024)

            if data:
                self.callback_method((data, self))

    def broadcast(self, table, name):
        """
        Only sends table info about reachable
        router, from this interface
        :param table:
        :return: None
        """

        data = {}

        for key, value in table.items():
            data[key] = (str(value[0]), str(value[1]))

        message = json.dumps({
            'origin': name,
            'destination': "all",
            'type': "broadcast",
            'data': data
        }).encode()

        self.queue.put(message)

    def send_packet(self, packet):
        """
        Method to internally enqueue a packet to be send in a future.
        :param packet:
        :return: None
        """
        self.queue.put(packet)

    def stop_running(self):
        """
        Method to stop the thread.
        :return:
        """
        self.running = False

    def run(self):
        """
        Run method of the thread.
        :return: None
        """
        self.listener = Thread(target=self._get_packets)
        self.listener.start()

        while self.running:
            self._manage_output_packet()

