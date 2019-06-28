import time

from routing.topology import Topology
from routing.Analyzer import Analyzer
SLEEPING_TIME = 120

if __name__ == "__main__":
    # Con esto crean y parten la topología
    SLEEPING_TIME = 60
    print("Creando Topología #1")
    analyzer = Analyzer()

    topology = Topology("examples/topology.json", analyzer)
    time.sleep(SLEEPING_TIME)


    # con esto modifican el peso de un enlace
    print("Modificando el costo de enlace Router#1->Router#2 a 10...")
    analyzer.star()
    topology.change_cost("Router#1", "Router#2", 10)
    time.sleep(SLEEPING_TIME)
    # con esto matan un enlace (setean el link con peso infinito)
    # Ojo con no matar enlaces que dividan el grafo! (acá está bien, porque Router#1 está conectado a Router#3 igual
    #print("Cortando enlace Router#1->Router#3...")
    #topology.break_connection("Router#1", "Router#3")
    #time.sleep(SLEEPING_TIME)
    # Con esto detienen los nodos
    print("Deteniendo topología...")
    topology.stop_topology()
    time.sleep(SLEEPING_TIME)
    analyzer.print_result()