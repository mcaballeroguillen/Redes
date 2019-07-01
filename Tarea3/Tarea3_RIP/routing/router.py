import json
import sys
from json import JSONDecodeError
from threading import Timer, Thread
from settings.settings import LOG, UPDATE_TIME, TOPOLOGY_CREATION_TIMEOUT, PROGRAM_UPDATE

from routing.router_port import RouterPort


class Router:
    def __init__(self, name, ports):
        self.name = name
        self.ports = dict()
        self._init_ports(ports)
        self.timer = None
        self.distance_vectors = {self.name: self._reset_dv()}
        self.links = {self.name: (0, None)}
        self.analizer = None
    def _reset_dv(self):
        """
        Creates an empty distance vector with information about this router
        :return: new dv
        """
        return {self.name: (0, None)}

    def init_table(self):
        """
        method called in the constructor to create the inital
        routing table for every entrance known in this router
        default will have max-size hops
        :return:void
        """
        for port in self.ports.values():
            port.name_request()

    def _compare_dvs(self, neighbour, new_dv):
        """
        Compares received dv from neighbour with the last recorded one
        :param neighbour: where the dv came from
        :param new_dv: received dv
        :return:
        """

        differences = []

        if neighbour in self.distance_vectors:
            for name, cost in new_dv.items():
                new_cost = self.distance_vectors[neighbour].get(name, None)

                if new_cost is None or not new_cost[0] == cost[0] or not new_cost[1] == cost[1]:
                    differences.append(name)
        else:
            differences = list(new_dv.keys())

        if differences:
            self.distance_vectors[neighbour] = new_dv
            self._compute_table(differences)

    def _compute_table(self, destinations=None):

        """
        modifies current routing table if necessary,
        whenever a better routing path is found
        :param destinations: neighbours to recompute
        :return: void
        """
        self.analizer.marcar_inicio(self.name)
        nodes = set()

        for router, dv in self.distance_vectors.items():
            for name, _ in dv.items():
                nodes.add(name)

        if destinations is None:
            destinations = nodes

        for dest in destinations:
            distance = self.distance_vectors[self.name].get(dest, (sys.maxsize, None))

            for u in nodes:
                if u in self.distance_vectors:
                    link = self.links.get(u, (sys.maxsize, None))
                    dv_info = self.distance_vectors[u].get(dest, (sys.maxsize, None))

                    new_distance = int(link[0]) + int(dv_info[0])

                    if new_distance < distance[0]:
                        distance = (new_distance, link[1] if link[1] else dv_info[1])

            self.distance_vectors[self.name][dest] = distance
        self.analizer.set_vd(self.name,self.distance_vectors)
        self.analizer.marcar_final(self.name)
        self._broadcast_dv()

    def _success(self, message):
        """
        Internal method called when a packet is successfully received.
        :param message:
        :return:
        """
        print("[{}] {}: {}".format(self.name, 'Success! Data', message))

    def _log(self, message):
        """
        Internal method to log messages.
        :param message:
        :return: None
        """
        if LOG:
            print("[{}] {}".format(self.name, message))

    def _init_ports(self, ports):
        """
        Internal method to initialize the ports.
        :param ports:
        :return: None
        """
        for port in ports:
            input_port = port['input']
            output_port = port['output']
            cost = port.get('cost', 1)

            router_port = RouterPort(
                input_port, output_port, cost, lambda p: self._new_packet_received(p)
            )

            self.ports[output_port] = router_port

    def _new_packet_received(self, packet_tuple):
        """
        Internal method called as callback when a packet is received.
        :param packet_tuple packet received and interface from which it was received
        :return: None
        """
        packet = packet_tuple[0]
        interface = packet_tuple[1]

        message = packet.decode()

        try:
            message = json.loads(message)
        except JSONDecodeError:
            self._log("Malformed packet")
            return

        if 'destination' in message and 'data' in message:
            dest = message['destination']
            if dest == self.name:
                self._success(message['data'])
            elif message['type'] == "name_request":
                interface.name_response(self.name)
            elif message['type'] == "name_response":
                neighbour = message['data']
                self.links[neighbour] = (message['cost'], interface)
            elif message['type'] == "broadcast":
                table = message.get('data', {})
                self._compare_dvs(message['origin'], table)
            elif dest in self.distance_vectors[self.name]:
                interface = self.distance_vectors[self.name][dest][1]
                self._log("Forwarding to port {}".format(interface.output_port))
                interface.send_packet(packet)
        else:
            self._log("Malformed packet")

    def _broadcast_dv(self):
        """
        sends current table to neighbours
        :return: void
        """
        for conn in self.ports.values():
            self.analizer.sum_paquete(self.name)
            conn.broadcast(self.distance_vectors[self.name], self.name)

    def _broadcast(self):
        """
        Internal method to broadcast
        :return: None
        """
        self._log("Broadcasting")

        if LOG:
            printable_table = {k: (v[0], v[1].output_port if isinstance(v[1], RouterPort) else None) for k, v in self.distance_vectors[self.name].items()}
            self._log(printable_table)

        self._broadcast_dv()
        self.timer = Timer(UPDATE_TIME, lambda: self._broadcast())
        self.timer.start()

    def start(self):
        """
        Method to start the routing.
        :return: None
        """
        self._log("Starting")

        for port in self.ports.values():
            port.start()

        Timer(TOPOLOGY_CREATION_TIMEOUT, lambda: self.init_table()).start()

        self.timer = Timer(UPDATE_TIME, lambda: self._broadcast())
        self.timer.start()

    def stop(self):
        """
        Method to stop the routing.
        Is in charge of stop the router ports threads.
        :return: None
        """
        self._log("Stopping")
        if self.timer:
            self.timer.cancel()

        for port in self.ports.values():
            port.stop_running()

        for port in self.ports.values():
            port.join()

        self._log("Stopped")

    def update_table(self):
        """
        Updates table after change
        :return:
        """
        self._compute_table()
        self.timer = Timer(UPDATE_TIME, lambda: self._broadcast())
        self.timer.start()

    def change_connection_cost(self, neighbor_name, new_cost):
        """
        Changes the link cost between myself and a neighbour
        :param neighbor_name: other side of the link
        :param new_cost: new cost of the link
        :return:
        """
        try:
            _, interface = self.links[neighbor_name]
            self.links[neighbor_name] = (new_cost, interface)
            self.distance_vectors[self.name][neighbor_name] = (sys.maxsize, interface)
            self.timer.cancel()

            Timer(PROGRAM_UPDATE, lambda: self.update_table()).start()
        except KeyError:
            self._log("Non-existant neighbour {}".format(neighbor_name))