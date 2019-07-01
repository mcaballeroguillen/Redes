import numpy as np
import datetime
import routing.router
class Analyzer:
    def __init__(self):
        self.rauters ={}
        self.timpo_de_inicio= None
        self.timpo_de_final=None
        self.tiempo_de_proceso={}
        self.horas_de_inicio={}
        self.paquetes ={}
        self.time_max={}
        self.v_star = False
        self.base = None
        self.terminados= set()

    def star(self):
        self.timpo_de_inicio= datetime.datetime.now()
        self.v_star=True

    def set_rauter(self,rauters):

        self.rauters=rauters

    def enalzar(self):
        for rauter in self.rauters.values():
            rauter.analizer=self
            self.paquetes[rauter.name]=0
            self.tiempo_de_proceso[rauter.name]=0


    def set_base(self,new_base):
        self.base=new_base

    def compare_base(self,rauter_name,matrix_adya):
        if self.v_star:
            matriz_adyace = matrix_adya
            matriz_adyace = np.asarray(matriz_adyace)
            base = np.asarray(self.base)
            indx=0
            resp=True
            resp= len(matriz_adyace)==len(base)
            if resp:
                for vector in matriz_adyace:
                    resp = np.array_equal(vector,base[indx])
                    if resp==False:
                        break
                    indx = indx+1
            if resp==True:
                self.terminados.add(rauter_name)
                if len(self.rauters)==len(self.terminados):
                    self.timpo_de_final = datetime.datetime.now()
                    self.v_star=False

    def sum_paquete(self,rauter_name):
        if self.v_star:
            self.paquetes[rauter_name]= self.paquetes.get(rauter_name,0)+1


    def marcar_inicio(self,rauter_name):
        if self.v_star:
            self.horas_de_inicio[rauter_name]=datetime.datetime.now()

    def marcar_final(self,rauter_name):
        if self.v_star:
            final = datetime.datetime.now()
            inicio = self.horas_de_inicio[rauter_name]
            self.tiempo_de_proceso[rauter_name]= (final-inicio).microseconds
    def rest_paquete(self,rauter_name):
        if self.v_star:
            self.paquetes[rauter_name]= self.paquetes.get(rauter_name,0)-1

    def print_result(self):
        print("Paquetes")
        print(self.paquetes)
        print("Tiempo Total")
        if self.timpo_de_final==None:
            self.timpo_de_final=datetime.datetime.now()
        print((self.timpo_de_final - self.timpo_de_inicio).seconds)
        print("Tiempo_de_Proceso_Tabla de Ruta")
        print(self.tiempo_de_proceso)
        print("Tabla de Rutas")
        for rauter in self.rauters.values():
            print("Tabla de Rutas de el: "+ rauter.name+ "\n")
            print(rauter.rute_table)
