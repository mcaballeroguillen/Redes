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
        self.base = {}
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


    def set_vd(self,rauter_name,vd):
        self.base[rauter_name]=vd
        self.compare_VD()

    def compare_VD(self):
        if self.v_star:
            resp=len(self.base)==len(self.rauters)  #Primero verifico si tengo todos los VD
            if resp:
                rauter1=None
                for rauter in self.base.keys():
                    rauter1=rauter
                    break
                vd_r1 = self.base[rauter1]    # Saco el primer vector de distancia
                for rauterx in self.base.keys():
                    vd_rx = self.base[rauterx]
                    if len(vd_rx)!= len(vd_r1): #Sin los vectores tienen tamaño diferente.
                        resp=False
                        break
                    for rauterx1 in vd_r1.keys():
                        vd_rauter1 = vd_r1[rauterx1] # Valor del Rauter 1
                        vd_rauter2 = vd_rx.get(rauterx1,None)
                        if vd_rauter2 == None:
                            resp=False
                            break
                        for r_final in vd_rauter1.keys():
                            tuple_1 = vd_rauter1[r_final]
                            tuple_2 = vd_rauter2.get(r_final,None)
                            if tuple_2==None:
                                resp=False
                                break
                            if tuple_1[0]!=tuple_2[0] or tuple_1[1]!=tuple_2[1]:  #Si tiene valores distintos
                                resp=False
                                break
                            if resp==False:
                                break
                    if resp ==False:
                        break
            if resp:
                self.v_star=False
                self.timpo_de_final = datetime.datetime.now()

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

