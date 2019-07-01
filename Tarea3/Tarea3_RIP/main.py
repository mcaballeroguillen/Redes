import time

from routing.topology import Topology
from routing.Analyzer import Analyzer
SLEEPING_TIME = 120
#Subir el costo de una topología.
if __name__ == "__main__":
    SLEEPING_TIME = 60
    print("Creando Topología #5")
    analyzer = Analyzer()
    topology = Topology("examples/topology5.json", analyzer)
    time.sleep(SLEEPING_TIME)
    print("Modificando el costo de enlace Router#2->Router#3 a 20...")
    analyzer.star() # Punto donde comenzamos a contar,paquetes y tiempo.
    topology.change_cost("Router#2", "Router#3", 20)
    time.sleep(SLEEPING_TIME)
    print("Deteniendo topología...")
    topology.stop_topology()
    time.sleep(SLEEPING_TIME)
    analyzer.print_result()