#!/usr/bin/python3
import json
import math
import sys
import time
from routing.router import Router
from settings.settings import TOPOLOGY_CREATION_TIMEOUT
from routing.Analyzer import Analyzer

class Topology:
    def __init__(self, topology_path,analyzer):
        self.routers = {}
        self.analyzer = analyzer
        self._start(topology_path)
        time.sleep(TOPOLOGY_CREATION_TIMEOUT)


    def _start(self, topology_path):
        """
        Read the topology file and create routers
        :param topology_path: file containing topology information
        :return:
        """

        with open(topology_path) as topology_file:
            topology = json.load(topology_file)

        routers = dict()
        routers_data = topology.get('routers', [])
        for router in routers_data:
            routers[router['name']] = Router(router.get('name', ''), router.get('ports', []))

        self.analyzer.set_rauter(routers)
        self.analyzer.enalzar()

        for router in routers.values():
            router.start()

        self.routers = routers

    def stop_topology(self):
        """
        Stops all routers and cease communication
        :return:
        """
        for _, router in self.routers.items():
            router.stop()

    def _get_router(self, name):
        """
        Get router by name
        :param name:
        :return:
        """
        try:
            return self.routers[name]
        except KeyError:
            print("Topology error: Non existant router {}".format(name))

    def change_cost(self, name1, name2, new_cost):
        """
        Change the cost of the link between two routers
        :param name1: endpoint 1
        :param name2: endpoint 2
        :param new_cost: cost to assign
        :return:
        """
        router1 = self._get_router(name1)
        router2 = self._get_router(name2)

        if router1 and router2:
            router1.change_connection_cost(name2, new_cost)
            router2.change_connection_cost(name1, new_cost)

    def break_connection(self, name1, name2):
        """
        Break the link between two connected routers (link cost set as infinity)
        :param name1: endpoint 1
        :param name2: endpoint 2
        :return:
        """

        router1 = self._get_router(name1)
        router2 = self._get_router(name2)

        if router1 and router2:
            router1.change_connection_cost(name2, sys.maxsize)
            router2.change_connection_cost(name1, sys.maxsize)
