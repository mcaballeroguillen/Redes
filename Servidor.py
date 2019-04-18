import socket as libsock
import random
import struct
import time
import os
import time
import json
import sys
from datetime import timedelta
import datetime

class Server:
    def __init__(self,puerto,direc_local,direc_dns,cache_time):
        self.port=puerto
        self.anddres=direc_local
        self.cache=[]
        self.directory = os.getcwd()
        self.blackList=[]
        self.redirect={}
        self.anddres_dns=direc_dns
        self.cache_t= cache_time
        
        with open(self.directory+'/'+'Redirect.json') as f:
            d = json.load(f)
            for p in d['Redirect']:
                self.redirect[p['Dominio']]=p['IP']
                
        with open(self.directory+'/'+'Black_List.json') as f:
            d = json.load(f)
            for p in d['Black_list']:
                self.blackList.append(p['Dominio'])
                
        
    def extract_label(self,message, offset):
        labels = []

        while True:
            length, = struct.unpack_from("!B", message, offset) #Primer octeto =longitud. 

            if (length & 0xC0) == 0xC0: #Si es un puntero  
                pointer, = struct.unpack_from("!H", message, offset) #Se extrae el octeto
                offset += 2 #position más dos

                return labels + self.extract_label(message, pointer & 0x3FFF), offset

            if (length & 0xC0) != 0x00:
                raise StandardError("unknown label encoding")

            offset += 1

            if length == 0:
                return labels, offset

            labels.append(*struct.unpack_from("!%ds" % length, message, offset))
            offset += length

    def extract_header(self,data):
        DNS_HEADER = struct.Struct("!6H") # 6 linias de 2 bytes, ó 6 lineas de 16 bits. 
        id1, misc, qdcount, ancount, nscount, arcount = DNS_HEADER.unpack_from(data)
        headerinfo=[] #arreglo donde se va guardar la info del header, por si necesitamos  luego.
        headerinfo.append(id1)
        headerinfo.append(misc)
        headerinfo.append(qdcount)
        headerinfo.append(ancount)
        headerinfo.append(nscount)
        headerinfo.append(arcount)
        position= DNS_HEADER.size # Posición de lectura, de donde se debe seguir leyendo.  
        return headerinfo, position
        
        
    

    def extract_question_section(self, data, position):
        DNS_SECTION_FORMAT = struct.Struct("!2H")
        info = []
        qname, position = self.extract_label(data, position)
        qtype, qclass = DNS_SECTION_FORMAT.unpack_from(data, position)
        position += DNS_SECTION_FORMAT.size
        info.append(qname)
        info.append(qtype)
        info.append(qclass)
        
        

        return info, position
        
        
    def extract_record_data(self,data,position,type_question):
        if(type_question==28):
            position-=6
            position+=10
            info=[]
            DATA_LEN = struct.Struct("!H")
            DATA_LEN =DATA_LEN.unpack_from(data, position)
            
            
            position+=2
            if(DATA_LEN[0]==16):
                IPv6= struct.Struct("!8H")
                IPv6=IPv6.unpack_from(data, position)
                position+=16
                info.append(IPv6)
            else:
                info.append("NA")
            
                
            return info,position
        if(type_question==1):
            DNS_TTL = struct.Struct("!I") #Entero sin signo, de 32 bits.
            info=[]
            ttl = DNS_TTL.unpack_from(data, position)
            position +=4
            #info.append(ttl)
            DNS_RDLENGHT= struct.Struct("!H") 
            rdlenght = DNS_RDLENGHT.unpack_from(data, position)
            position += 2
            DNS_IP= struct.Struct("!4B")
            i1 = DNS_IP.unpack_from(data,position)
            #info.append(rdlenght)
            info.append(i1)
        
            return info,position
        if(type_question==15):
            position-=6
            position+=10
            info=[]
            DATA_LEN = struct.Struct("!H")
            DATA_LEN =DATA_LEN.unpack_from(data, position)
            DATA_LEN=DATA_LEN[0]-2
            position+=4
            listbytes=[]
            x=0
            while(x<DATA_LEN):
                nextbyte = struct.unpack_from("!B", data, position)
                
                if (nextbyte[0] & 0xC0) == 0xC0: #Es un puntero 
                    position+=1
                    x+=1
                    nextbyte = struct.unpack_from("!B", data, position)
                    position_p= nextbyte[0]
                    new_byte = struct.unpack_from("!B", data, position_p)
                    while(new_byte[0]!=0):
                        listbytes.append(new_byte[0])
                        position_p+=1
                        new_byte = struct.unpack_from("!B", data, position_p)
                   
                else:
                    listbytes.append(nextbyte[0])
                position+=1
                x+=1
            position+=14
            
            resp= bytearray(listbytes)
            
            info.append(resp.decode("utf-8"))
            
            
            return info,position
        return(["N/a"],position)
        
         
    
    def cache_search(self,info):
        if(len(self.cache)==0): #Si la caché esta vacia 
            return -1
        resp=-1
        for x in range(len(self.cache)): #Cada una de las tuplas de la caché
            if(info[1]!=self.cache[x][0][1]): #Si los tipos de la consulta son diferente, paso tupla
                continue
            if(info[2]!=self.cache[x][0][2]): #si la clase son diferentes paso tupla.
                continue
            if(len(info[0])!=len(self.cache[x][0][0])):#si los dominios tiene campos distintos. 
                continue
            resp=x
            for y in range(len(info[0])):
                if(info[0][y]!=self.cache[x][0][0][y]): #si unos de los campos consultados es distinto, pasamos.
                    resp=-1
                    break
        if(resp!=-1):
            a = self.cache[resp][2]
            a = a + timedelta(seconds=self.cache_t)
            if(a<=datetime.datetime.now()):
                self.cache.pop(resp)
                resp=-1
            
            
        
        return resp
                
  
    
    
    def builder_request(self,question,answer):
        questionid= struct.Struct("!2B") #Tamaño   de la id pregunta
        questionid= questionid.unpack_from(question) #Sacar id
        len_in_bytes= len(answer)  #largo de la respuesta
        len_data= len_in_bytes-2 # larga de la respuesta menos los dos byte de la id.
        s = "!"+str(len_data)+ "B" # número de tuplas a extraer.
        struct1= struct.Struct(s)  
        array_of_parts = struct1.unpack_from(answer,2) # Se extraen todos los bytes menos los dos inciales.
        
        listbytes=[]  #lista donde se iran guardando las partes de la respuesta.
        
        for x in questionid:
            listbytes.append(x)    # Agregar id de la pregunta
       
        for x in range(len(array_of_parts)):
            listbytes.append(array_of_parts[x]) # Resto de la respuesta
            
        resp= bytearray(listbytes) #pasar a un arreglo de bytes.
        
        
        return bytes(resp)  # pasar a bytes 
        
               
            
    def writelog(self,consulta,ip):
        sconsulta =""
        for x in range(len(consulta)):
            if(x==0):
                sconsulta=sconsulta+consulta[x].decode("utf-8") 
            else:
                sconsulta =sconsulta+'.'+ consulta[x].decode("utf-8") 
        sip=""
        for x in ip:
            sip=sip+str(x)
        f = open(self.directory+'/'+'log.txt','a')
        f.write('\n')
        f.write(time.strftime("%c"))
        f.write('\t')
        f.write(str(sconsulta))
        f.write('\t')
        f.write(str(ip))
        
            
    
    def black_list_search(self,dominio):
        sconsulta =""
        for x in range(len(dominio)):
            if(x==0):
                sconsulta=sconsulta+dominio[x].decode("utf-8") 
            else:
                sconsulta =sconsulta+'.'+ dominio[x].decode("utf-8") 
        for x in range(len(self.blackList)):
            if(sconsulta==self.blackList[x]):
                return x
        return -1
    
    
            
    def redirect_search(self,answer):
        header1 , position1 = self.extract_header(answer)
        info1, position1 = self.extract_question_section(answer,position1)
        info2, position2 = self.extract_record_data(answer,position1+6,info1[1])
        sconsulta =''
        for x in range(len(info1[0])):
            if(x==0):
                sconsulta=sconsulta+info1[0][x].decode("utf-8") 
            else:
                sconsulta =sconsulta+'.'+ info1[0][x].decode("utf-8") 
        
        if(info1[1]==1):
            if((sconsulta in self.redirect)==True):
                first_part= struct.Struct("!39B")
                first_part= first_part.unpack_from(answer)
            
                i=len(answer)-39-4
                s = "!"+str(i)+ "B"
                final_part=struct.Struct(s)
                final_part= final_part.unpack_from(answer,43)
                new_ip= self.redirect.get(sconsulta)
                part_ip= new_ip.split('.')
            
                listbytes=[]  #lista donde se iran guardando las partes de la respuesta.
        
                for x in first_part:
                    listbytes.append(x)    # Agregar id de la pregunta
       
            
            
                for x in part_ip:
                    listbytes.append(int(x))
            
                for x in final_part:
                    listbytes.append(x)
                
                resp= bytearray(listbytes) #pasar a un arreglo de bytes.
        
        
                return bytes(resp)  # pasar a bytes 
            
            
        return answer 
        
    def run(self):
        count=0
        while(True):
            count=count+1
            socket = libsock.socket(libsock.AF_INET, libsock.SOCK_DGRAM)  # SOCK_DGRAM es UDP
            print("listening on {}:{}...".format(self.anddres, self.port))  # logging
            socket.bind((self.anddres, self.port))  # enlazando al puerto
            data, address = socket.recvfrom(1024)  # recibe datos del cliente
            print("Data received from address {}".format(address))  # logging
            header , position = self.extract_header(data)     #Extraemos la info del header 
            info, position = self.extract_question_section(data,position)
            
            if(self.black_list_search(info[0])==-1):
                 
                fc=self.cache_search(info)
                
                if(fc==-1):
                    socket0 = libsock.socket(libsock.AF_INET, libsock.SOCK_DGRAM)
                    socket0.connect((self.anddres_dns, 53))
                    socket0.send(data)
            
                    answer, address1 = socket0.recvfrom(1024)
                    header1 , position1 = self.extract_header(answer)
                    info1, position1 = self.extract_question_section(answer,position1)
                    info2, position1 = self.extract_record_data(answer,position1+6,info[1])
                    print("Se consulto a serivor dns: ", self.anddres_dns)
                    print("Valor: ", info2)
                    self.cache.append([info,answer,datetime.datetime.now()])
                   
                    self.writelog(info[0],info2[0])
                else:
                    data1 = self.cache[fc][1]
                    answer= self.builder_request(data,data1)
                    header1 , position1 = self.extract_header(answer)
                    info1, position1 = self.extract_question_section(answer,position1)
                    info2, position1 = self.extract_record_data(answer,position1+6,info[1])
                    print("Se econtró respuesta en la caché ")
                    print("Valor: ", info2)
                    self.writelog(info[0],info2[0])
                   
                answer= self.redirect_search(answer)
                
                socket.sendto(answer, address)
                
Servidor1= Server(2035,"127.0.0.1","1.1.1.1",10)
Servidor1.run()
