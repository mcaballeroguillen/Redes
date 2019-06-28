import json
import sys
from json import JSONDecodeError
from threading import Timer, Thread
from settings.settings import LOG, UPDATE_TIME, TOPOLOGY_CREATION_TIMEOUT, PROGRAM_UPDATE
import networkx as nx
import numpy as np
from routing.router_port import RouterPort
from routing.Analyzer import Analyzer

class Router:
    def __init__(self, name, ports):
        self.name = name
        self.ports = dict()
        self._init_ports(ports)
        self.timer = None

        self.links = {self.name: (0, None)}
        self.toplogy = dict()
        self.Adjacency_matrix = None
        self.rute_table = dict()
        self.analizer =None

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

    def _compare_topology(self, neighbour, toplogy):
        """
        Compares received topology from neighbour with the last recorded one
        :param neighbour: where the dv came from
        :param toplogy: received toplogy
        :return:
        """

        cambios =0
        for enlace in toplogy.keys():
            costo = self.toplogy.get(enlace,None) #Saco el costo de cada enlace
            if costo==None or costo != toplogy[enlace]: # Si no se tiene registro de este enlace, o se cambió el valor de uno.
                self.toplogy[enlace] = toplogy.get(enlace) # Se agrega o se modifica.
                cambios = cambios +1 #Sumamos que hubo un cambio

        if cambios != 0: # si hubieron cambios, reenvió este mensaje, y actulizo la tabla de adyacencia.
            self._flooding_topology(toplogy, neighbour)
            self._compute_table()


    def _compute_table(self):
        self.analizer.marcar_inicio(self.name)  # Le aviso al analizador que voy a empezar a calcular mi tabla de rutas.
        Rauters_pars = self.toplogy.keys() # Saco los pares de rauters en los enaces ej: Rauter1 $$ Raueter2
        Rauster_set = set()
        for par in Rauters_pars:
            rauters = par.split("$$") #Separo
            for ra in rauters:
                Rauster_set.add(ra) # Conjunto donde voy a aguardar todos los raueters que tengo en mi topología
        Rauster_set = sorted(Rauster_set) # ordeno los rauters, para luego hacer más fácil la ruta.
        matrix = []  # Futura matriz de adyacencia
        for ra in Rauster_set: # Por cada rauter voy a construir su vector.

            vector = []
            for ra1 in Rauster_set:

                par= ra+"$$"+ra1    # Posible forma en que se pudo a ver guardado en el enlace, se deben verificar las dos
                                    # ya que si existe un enlace de x a y en las coordenads (x,y) y (y,x) de la matriz de
                                    # adyacencia  se deben colocar el costo  ya que los enlaces son bidireccionales.
                cost = self.toplogy.get(par,0)
                if cost==0:
                    par = ra1+"$$"+ra
                    cost = self.toplogy.get(par,0)
                vector.append(cost)  #Agregamos el costo.
            matrix.append(vector)

        self.Adjacency_matrix = np.asmatrix(matrix)
        self.analizer.compare_base(self.name,self.Adjacency_matrix)
        rauter_index = Rauster_set.index(self.name,0)  # Encuentro  el índice del este rauter en el conjunto ordenado.
        x=0
        for raute in Rauster_set:
            G = nx.from_numpy_matrix(self.Adjacency_matrix, create_using=nx.DiGraph())
            ruta = nx.dijkstra_path(G, rauter_index, x) # Calculo con djstra la ruta de este rauter a los otros rauter en la topolgía.
            key = self.name + "to" + raute  # Llave de la tabla de ruta.
            ruta_name = []
            for ind in ruta:
                ruta_name.append(Rauster_set.__getitem__(ind))
            self.rute_table[key]= ruta_name
            x=x+1
        self.analizer.marcar_final(self.name) # Le notifíco la analizador que ya termine de calcular mi tabla de ruta.


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
                self.add_link_topology(self.name,neighbour,message['cost'])
            elif message['type'] == "flooding":
                table = message.get('data', {})
                self._compare_topology(message['origin'], table)
            elif self.name + "to" + dest in self.rute_table.keys():
                rauter_salida = self.rute_table.get(self.name + "to" + dest)[1]

                interface = self.links[self.name + "to" + dest][1]
                self._log("Forwarding to port {}".format(interface.output_port))
                interface.send_packet(packet)
        else:
            self._log("Malformed packet")

    def _flooding_topology(self, topoly, name):
        """
        sends current table to neighbours
        :return: void
        """

        for conn in self.ports.values():
            self.analizer.sum_paquete(self.name)
            conn.flooding(topoly, name)  # Le aviso al analizador que este rauter va mandar un paquete.
        #self.analizer.rest_paquete(self.name)
    def _flooding(self):
        """
        Internal method to broadcast
        :return: None
        """
        self._log("flooding")

        if LOG:
            #printable_table = {k: (v[0], v[1].output_port if isinstance(v[1], RouterPort) else None) for k, v in self.distance_vectors[self.name].items()}
            printable_table = self.toplogy
            self._log(printable_table)

        self._flooding_topology(self.toplogy, self.name)
        #self.timer = Timer(UPDATE_TIME, lambda: self._flooding())
        #self.timer.start()

    def start(self):
        """
        Method to start the routing.
        :return: None
        """
        self._log("Starting")

        for port in self.ports.values():
            port.start()

        Timer(TOPOLOGY_CREATION_TIMEOUT, lambda: self.init_table()).start()

        self.timer = Timer(UPDATE_TIME, lambda: self._flooding())
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
        self.timer = Timer(UPDATE_TIME, lambda: self._flooding())
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
            self.add_link_topology(self.name,neighbor_name,new_cost)
            self.timer.cancel()

            Timer(PROGRAM_UPDATE, lambda: self.update_table()).start()
        except KeyError:
            self._log("Non-existant neighbour {}".format(neighbor_name))

    def add_link_topology(self, neighbour2, neighbour1, cost):
        if neighbour2 > neighbour1:
            self.toplogy[neighbour1+"$$"+neighbour2]= cost
        else:
            self.toplogy[neighbour2 + "$$" + neighbour1] = cost
        self._compute_table()