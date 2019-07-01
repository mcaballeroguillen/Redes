import time
import numpy as np
from routing.topology import Topology
from routing.Analyzer import Analyzer
SLEEPING_TIME = 60

if __name__ == "__main__":
    SLEEPING_TIME = 30
    base= [[0, 10, 10, 0],
     [10, 0, 20, 5],
     [10, 20, 0, 0],
     [0, 5, 0, 0]]


    print("Creando Topología #5")
    analyzer = Analyzer()
    analyzer.set_base(np.asmatrix(base))
    topology = Topology("examples/topology5.json",analyzer)
    time.sleep(SLEEPING_TIME)
    print("Modificando el costo de enlace Router#2->Router#3 a 20...")
    analyzer.star()
    topology.change_cost("Router#2", "Router#3", 20)
    time.sleep(SLEEPING_TIME)
    print("Deteniendo topología...")
    topology.stop_topology()
    time.sleep(SLEEPING_TIME)
    analyzer.print_result()