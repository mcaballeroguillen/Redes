import time
import numpy as np
from routing.topology import Topology
from routing.Analyzer import Analyzer
SLEEPING_TIME = 30

if __name__ == "__main__":
    base=[[0,50,10,0],
          [50,0,10,0],
          [10,10,0,10],
          [0,0,10,0]]

    # Con esto crean y parten la topología
    print("Creando Topología #2")
    analyzer = Analyzer()
    analyzer.set_base(np.asmatrix(base))
    topology = Topology("examples/topology2.json",analyzer)
    time.sleep(SLEEPING_TIME)

    # con esto modifican el peso de un enlace
    print("Modificando el costo de enlace Router#1->Router#2 a 50...")
    analyzer.star()
    topology.change_cost("Router#1", "Router#2", 50)
    time.sleep(SLEEPING_TIME)
    print("Deteniendo topología...")
    topology.stop_topology()
    time.sleep(SLEEPING_TIME)
    analyzer.print_result()
    # con esto matan un enlace (setean el link con peso infinito)
    # Ojo con no matar enlaces que dividan el grafo! (acá está bien, porque Router#1 está conectado a Router#3 igual
    #print("Cortando enlace Router#1->Router#3...")
    #topology.break_connection("Router#1", "Router#3")
    #time.sleep(SLEEPING_TIME)
    # Con esto detienen los nodos
    #print("Deteniendo topología...")
    #topology.stop_topology()
    #time.sleep(SLEEPING_TIME)
