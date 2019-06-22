import time

from routing.topology import Topology

SLEEPING_TIME = 120

if __name__ == "__main__":
    # Con esto crean y parten la topología
    print("Creando Topología #2")
    topology = Topology("examples/topology2.json")
    time.sleep(SLEEPING_TIME)
    # con esto modifican el peso de un enlace
    #print("Modificando el costo de enlace Router#1->Router#2 a 50...")
    #topology.change_cost("Router#1", "Router#2", 50)
    #time.sleep(SLEEPING_TIME)
    # con esto matan un enlace (setean el link con peso infinito)
    # Ojo con no matar enlaces que dividan el grafo! (acá está bien, porque Router#1 está conectado a Router#3 igual
    #print("Cortando enlace Router#1->Router#3...")
    #topology.break_connection("Router#1", "Router#3")
    #time.sleep(SLEEPING_TIME)
    # Con esto detienen los nodos
    #print("Deteniendo topología...")
    #topology.stop_topology()
    #time.sleep(SLEEPING_TIME)
