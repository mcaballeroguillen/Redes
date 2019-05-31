Integrantes:
- Marco Antonio Caballero .......25694063-9	
- Santiago Rangel Mora...........26728993-k
Requerimientos: 
	-La tarea fue realizada en Python 3.6, por lo que se recomienda usar una versión igual o superior a esta.

Como hacerlo Funcionar:

	En el archivo Cliente.py  en la linea 119 ingrese los siguiente argumentos:
		1. IP del servidor al cual enviar los archivos.
		2. Nombre del archivo a enviar.
		3. Tamaño (en número de paquetes) de la ventana.
		4. Tamaño de los paquetes a enviar.
		5. Número máximo de números de secuencia.
		6. Puertos para: (1) enviar información, (2) recibir los ACKs.

	Luego se crea un thread que estará constante mente recienbiendo acks.
	Luego se ejecuta un thread con timer que se encarga de enviar la ventana.
	
Que imprime el Cliente:
	- Primero imprime el número total de paquetes a enviar.
	-  Luego impreme el paquete que se envió al servidor, identificado por el número de
	  pequete, no el número de secuencia.
	- Imprime que se recibió el ack, de un paquete específico y su número de secuencia.

Link de GitHub por si acaso:
https://github.com/mcaballeroguillen/Redes/blob/master/Tarea_Final.ipynb

Observaciones:

En la especifícaciones nunca se dijo que el  IP donde se va recibirlos acks debe ser ingresado por agumento, los
requirimeintos solicitados son los 6 antes mencionados, se nos pide que recibamos el Ip del server, pero no el IP
del del cliente, por lo que se escucha en el IP 127.0.0.1, si se desea cambiar esto se debe modifcar la linea 83 del
archivo.

Se corrió y probó  la tarea con la sigueintes lineas:

Server:  ./server 2 2030 2040 127.0.0.1
Cliente: Cliente_GBN("0.0.0.0","divina_comedia.txt",98,900,99,2030,2040)


