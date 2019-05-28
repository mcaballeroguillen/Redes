import random
import socket
import threading
import hashlib
import time
import datetime
from IPython.display import clear_output
class Cliente_GBN:
    def __init__(self,Ip_server,file,le_wi,le_pa,max_sec,port_send,port_rec):
        self.serverIP=Ip_server # Ip del sevidor 
        self.file = file #Dirección del archivo a abrir 
        self.l_ventana= le_wi # Largo de la ventana
        self.largo_partes = le_pa # Largo de las partes en que se va dividir el archivo
        self.max_secuencia= max_sec # Número de secuencia máximo
        self.port_envio=port_send # Puerto de envío 
        self.port_recibo=port_rec # Puerto de entrada
        self.fill =0 # Largo de los números de secuencias
        self.data =[] # Los paquetes a enviar
        self.vi=0 # Indice inicial de la ventana
        self.vf=le_wi # Indice Final de la ventana
        self.tim= threading.Timer(1,self.enviar_ventana) #Timer para enviar la ventana 
        self.info=[] # info de cada paquete (num_secuencia,num_envios,hora_de_envío,hora_de_rec_ack)
        self.TimeoutInterval=1 # tiempo del timer
        self.EstimateRTT=1
        self.devRTT =0
        # Calcula el checksum de un mensaje en string (sí, es así de simple)
    def calculate_checksum(self,message):
        checksum = hashlib.md5(message.encode()).hexdigest()
        return checksum
    
    # Crear mensaje
    def create_message(self,message, seq_num):
        seq_num_padded = str(seq_num).zfill(self.fill)
        checksum = self.calculate_checksum(message)
        return "%s%s%s" % (str(seq_num_padded), str(checksum), message)
    
    def cargar_datos(self):
        archivo = open(self.file,'r') #Abrir el archivo
        mensaje = archivo.read() # Leer mensaje 
        archivo.close()
        parts = [mensaje[i:i+self.largo_partes] for i in range(0, len(mensaje), self.largo_partes)] # partir el archivo
        self.fill = len(str(self.max_secuencia)) #Sacar el número de caracteres de los numeros de secuencias
        num_secuencia=0 
        for part in parts: #para cada parte del archivo construimos su paquete para enviar.
            if(num_secuencia>self.max_secuencia): # resetear el número de secuencia
                num_secuencia=0
            paquete = self.create_message(part,num_secuencia) #paquete listo para enviar.
            self.data.append(paquete) #agregar paquete a la data
            self.info.append([num_secuencia,0,None,None]) # agregar info del paquete
           
            num_secuencia=num_secuencia+1
        
    # Envía el paquete con datos al servidor
    def send_packet(self,ip, port, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (ip, port)
        try:
            sock.sendto(message.encode(), server_address)
        finally:
            sock.close()
            
    def enviar_ventana(self):
           for x in range(self.vi, self.vf+1): #por cada paquete en la ventana
                print("Enviando paquete."+str(x)) 
                info1= self.info[x] #buscamos la info del paquete 
                info1[1] =info1[1]+1 # sumamos un envió del paquete
                info1[2] = datetime.datetime.now() # agregamos la hora d envió
                self.info[x]=info1 # guardamos la info
                self.send_packet(self.serverIP,self.port_envio,self.data[x]) #enviamos
            
    
    def calcEst(self, antEst, sample, desvAnt):
        a = 1/8
        est = (1-a)*antEst+(a*sample)
        b = 1/4
        desv = (1-b)*desvAnt + b*abs(sample-antEst)
        return est, desv

    def receive_ack(self):
       
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        sock.bind(('127.0.0.1', self.port_recibo))
        sock.settimeout(90)

        while (self.vi!=self.vf):
            data, address = sock.recvfrom(1024) #Esperamos acks
            self.tim.cancel() #Al llegar ack paramos los envios, vamos a ajustar la ventana
            ack = data.decode() 
            num_sec = ack[0:self.fill] # sacamos el número de secuencia.
           
            index=0
            num_sec = int(num_sec) #pasamos a entero el número de secuencia
            for x in range(self.vi, self.vf+1): #buscamos en que indice esta el paquete que llego
                if(self.info[x][0]==num_sec):
                    index=x 
                    break
            print("llego ack de : "+str(index) + " Numsec= "+str(num_sec) )
            self.vi=index #valor inicial de la ventana es el indice que llego.
            pvf= self.vi+self.l_ventana #  posible valor final de la ventana
            if(pvf>=len(self.data)): # el valor final de la ventana no puede ser mayor que la cantidad de datos.
                self.vf=len(self.data)-1
            else:
                self.vf=pvf
            self.info[index][3]= datetime.datetime.now() #Colocamos la hora de llegada
            if(self.info[index][1]==1): #Solo calculamos nuevo tiempo si solo se ha enviado una vez.
                self.info[index][1]=self.info[index][1]+1 #Para no calcular mas de una vez si llegan más acks
                Samplertt = (self.info[index][3]-self.info[index][2]).seconds #Tiempo desde envió hasta recibir acks
                newEst, newdesv= self.calcEst(self.EstimateRTT,Samplertt,self.devRTT) #nuevos valores
                self.EstimateRTT = newEst # setiamos
                self.devRTT=newdesv 
                self.TimeoutInterval = newEst + 4*newdesv
            print("Timer= "+ str(self.TimeoutInterval))
            self.tim= threading.Timer(self.TimeoutInterval,self.enviar_ventana) #volver a iniciar tread.
            self.tim.start()
        self.send_packet(self.serverIP,self.port_envio,"")
        
        
client = Cliente_GBN("0.0.0.0","divina_comedia.txt",98,900,99,2030,2040)
client.cargar_datos()
print("total de paquetes a enviar"+len(client.data))

ack_thread = threading.Thread(target=client.receive_ack)
ack_thread.start()

client.tim.start() 

