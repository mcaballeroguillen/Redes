Integrantes:
- Marco Antonio Caballero .......25694063-9	
- Santiago Rangel Mora...........26728993-k
Requerimientos: 
	-La tarea fue realizada en Python 3.6, por lo que se recomienda usar una versi�n igual o superior a esta.

Como hacerlo Funcionar:

	En el archivo Cliente.py  en la linea 119 ingrese los siguiente argumentos:
		1. IP del servidor al cual enviar los archivos.
		2. Nombre del archivo a enviar.
		3. Tama�o (en n�mero de paquetes) de la ventana.
		4. Tama�o de los paquetes a enviar.
		5. N�mero m�ximo de n�meros de secuencia.
		6. Puertos para: (1) enviar informaci�n, (2) recibir los ACKs.

	Luego se crea un thread que estar� constante mente recienbiendo acks.
	Luego se ejecuta un thread con timer que se encarga de enviar la ventana.
	
Que imprime el Cliente:
	- Primero imprime el n�mero total de paquetes a enviar.
	-  Luego impreme el paquete que se envi� al servidor, identificado por el n�mero de
	  pequete, no el n�mero de secuencia.
	- Imprime que se recibi� el ack, de un paquete espec�fico y su n�mero de secuencia.

Link de GitHub por si acaso:
https://github.com/mcaballeroguillen/Redes/blob/master/Tarea_Final.ipynb

Observaciones:

En la especif�caciones nunca se dijo que el  IP donde se va recibirlos acks debe ser ingresado por agumento, los
requirimeintos solicitados son los 6 antes mencionados, se nos pide que recibamos el Ip del server, pero no el IP
del del cliente, por lo que se escucha en el IP 127.0.0.1, si se desea cambiar esto se debe modifcar la linea 83 del
archivo.

Se corri� y prob�  la tarea con la sigueintes lineas:

Server:  ./server 2 2030 2040 127.0.0.1
Cliente: Cliente_GBN("0.0.0.0","divina_comedia.txt",98,900,99,2030,2040)


