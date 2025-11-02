#!/usr/bin/env python3
"""
UNPILAR - Facultad de Producción y Tecnología - Tecnicatura Universitaria en Desarrollo de Software
- Proyecto: Servidor UDP con verificación CRC y simulación de errores.
- Autores: Villarroel Giuliana y Parra Josefina
- Docente: Mariana Gil
- Materia: Redes de Datos


EL SERVIDOR DEBE:
- Recibir mensajes desde un cliente UDP
- Calcular y verificar el CRC
- Responder con ACK o NACK según corresponda
- Simular errores en los datos recibidos
"""

import socket 
import random

# ===================== CONFIGURACIÓN =====================
HOST = "127.0.0.1" # Dirección IP local
PORT = 5000 # Puerto de escucha del servidor
PROBABILIDAD_DE_ERROR = 0.6 # Probabilidad de error
# ==========================================================


def crc16_ccitt(data):
    """
    Calcula el crc16_ccitt del mensaje recibido
        - CRC -> es una suma de verificación que detecta si hubo errores durante la transmisión del mensaje
            - Usa polinomio estándar 0x1021 (definido por protocolo CCITT)
        - Crea un "código único" para cualquier mensaje -> si el mensaje cambia aunque sea UNA letra, el código cambia por COMPLETO

    - Parámetro -> data (str o bytes): el mensaje del cual se calculará el CRC
    - Return -> int: numero de 16 bits que representa el CRC
    
    """

    # Convierte el mensaje a bytes -> la computadora trabaja con números, no con letras
    if type(data) == str:
        data = data.encode("utf-8")

    # Se inicializa el CRC -> valor inicial estándar para CRC16-CCITT: 0xFFFF en hexa
    crc = 0xFFFF

    # Se procesa cada byte del mensaje -> cada byte modifica el crc de forma matemática
    for byte in data:
        # XOR (^) -> combina los bits del crc con los del byte desplazado. Si los bits son iguales -> resultado 0, sino resultado 1
        # Desplazamiento (byte << 8) -> desplaza el byte 8 posiciones a la izquierda
        crc = crc ^ (byte << 8)

        # Se procesa cada bit del byte usando el polinomio 0x1021
        for i in range(8):
            # Verificar si el el primer bit es 1 -> crc & 0x8000 verifica el primer bit >> si el resultado NO ES 0, el primer bit es 1
            if crc & 0x8000:
                # Si es 1 -> desplaza crc un bit a la izquierda (empuja todos los bits hacia izquierda. Por ej: 1011 << 1 = 0110)
                crc = (crc << 1) ^ 0x1021  # Se aplica XOR con el polinomio estándar
            else:
                # Si es 0 -> desplaza un bit a izquierda
                crc = crc << 1

            # Se mantienen solo 16 bits (en caso de generar más números con desplazamiento)
            crc = crc & 0xFFFF
    
    # Se retorna la "huella" única del mensaje
    return crc


def simular_error(mensaje: str, probabilidad: float):
    """
    Simula errores de transmisión corrompiendo el mensaje
        - Prueba que el CRC detecte errores de forma correcta
    
    - Parámetros:
        - mensaje (str) -> el mensaje que puede ser corrompido
        - probabilidad (float) -> numero entre 0 y 1

    - Return -> str, que representa el mensaje original o corrompido (con una letra cambiada), según la probabilidad de corrupción
    """

    # Genera un número random que determinará si habrá error o no
    numero_random = random.random()

    # Compara el número random con la probabilidad -> ej con probabilidad = 0.2 >>> si numero_random = 0.15 -> 0.15 < 0.2 == habrá error
    if numero_random < probabilidad:
        # Conversión del mensaje (str) en una lista de strings para poder modificarlo (corromperlo)
        lista_caracteres = list(mensaje)

        # Si el mensaje no está vacío
        if len(lista_caracteres) > 0:
            # Se genera un numero random entre 0 y la longitud de la lista - 1 -> decide una posición válida para insertar el cambio
            posicion = random.randint(0, len(lista_caracteres) - 1)
            
            # Se genera la corrupción del mensaje
            lista_caracteres[posicion] = "x"

            # Se le indica al usuario dónde ocurrió el error
            print(f"[Servidor] ¡Error simulado en la posición {posicion}!")

        # Se convierte nuevamente el mensaje a string para retornarlo en modo "texto" -> join() une todos los elementos de la lista en un solo string
        mensaje = "".join(lista_caracteres)

    # Se retorna el mensaje -> si hubo error, retorna el mensaje con una letra cambiada; si NO hubo error, retorna el mensaje original (sin cambios)
    return mensaje



# ===================== FUNCIÓN PRINCIPAL DEL SERVIDOR =====================
# Esta función controla todo el servidor:
# 1. Crea el socket (punto de comunicacion)
# 2. Espera mensajes de clientes
# 3. Verifica si hay errores usando CRC
# 4. Responde con ACK (OK) o NACK (error)

def main():
    """
    Función principal que ejecuta el servidor UDP:
        - Espera mensajes en un puerto específico
        - Simula errores de transmisión
        - Calcula el CRC del mensaje recibido
        - Compara con el CRC que envió el cliente
        - Responde ACK si está OK, NACK si hay error
        - Lleva control de secuencia para evitar mensajes duplicados
    """

    print(f"[Servidor] Iniciando servidor en {HOST}:{PORT}")
    print(f"[Servidor] Probabilidad de error: {PROBABILIDAD_DE_ERROR * 100}%")
    print()

    # Creación y configuración del socket UDP:
    # socket.AF_INET --> AF determina la familia de direcciones & INET usa direcciones IPv4 para la comunicación (Internet)
    # socket.SOCK_DGRAM --> DGRAM es el tipo unidad de dato usada en UDP (datagrama)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Se "amarra" el socket a una dirección y puertos especificos -> de esta forma, el servidor SOLO RECIBE mensajes EN ESTE PUERTO
    sock.bind((HOST, PORT)) 

    # Se inicia el control de secuencia -> evita procesar mensajes duplicados (alternando entre 0 y 1 para cada mensaje nuevo)
    secuencia_esperada = 0

    print("[Servidor] Esperando mensajes...\n")

    # Se genera la espera y procesamiento de mensajes
    while True:
        # Se reciben datos del cliente -> datos: bytes recibidos; direccion_cliente: tupla con (IP, puerto) del que se envió el mensaje
        datos, direccion_cliente = sock.recvfrom(1024)  # 1024 es el tamaño máximo del buffer (bytes a recibir)
        
        # Se decodifican los bytes a texto
        mensaje_completo = datos.decode("utf-8")

        print(f"[Servidor] Mensaje recibido de: {direccion_cliente}")
        print(f"\tContenido: {mensaje_completo}")

        # Se separa el mensaje en partes: secuencia|mensaje|crc
        partes = mensaje_completo.split("|")

        # Se valida que el formato sea el correcto -> el mensaje DEBE tener 3 partes, de lo contrario el formato será incorrecto
        if len(partes) != 3:
            print("[Servidor] Error: formato incorrecto")
            continue  # Ignora el mensaje actual y salta al siguiente

        # Se extraen las partes del mensaje: secuencia (0 - 1) -> se convierte a int; mensaje -> el mensaje en sí; crc_recibido -> crc recibido en hexadecimal
        secuencia = int(partes[0])
        mensaje = partes[1]
        crc_recibido = int(partes[2], 16) # Se convierte de hexa (base 16) a número decimal

        # Se simula error en el mensaje -> usando la probabilidad, corrompe el mensaje
        mensaje = simular_error(mensaje, PROBABILIDAD_DE_ERROR)

        # Se calcula el CRC del mensaje recibido -> calcula el crc del mensaje y este crc se comparará con el que envió el cliente
        crc_calculado = crc16_ccitt(mensaje)

        print(f"\tSecuencia: {secuencia}")
        print(f"\tCRC recibido: {crc_recibido}")
        print(f"\tCRC calculado: {crc_calculado}")


        # Se comparan los CRC -> es la verificación de INTEGRIDAD del mensaje
        if crc_calculado == crc_recibido:
            # CRC CORRECTO - sin errores
            print("\n[Servidor] CRC correcto")

            # Se verifica el número de secuencia -> ¿Es el mensaje esperado o es duplicado?
            if secuencia == secuencia_esperada:
                
                # Secuencia correcta -> mensaje NUEVO
                print(f"[Servidor] Mensaje aceptado: {mensaje}")
                respuesta = f"ACK {str(secuencia)}"

                # Se alterna la secuencia esperada (0 -> 1 -> 0 -> 1...) --> asegura que cada mensaje nuevo tenga un número diferente
                if secuencia_esperada == 0:
                    secuencia_esperada = 1
                else:
                    secuencia_esperada = 0
                
            else:
                # Secuencia incorrecta - mensaje DUPLICADO
                print("[Servidor] Mensaje duplicado (ya fue recibido)")
                respuesta = f"ACK {str(secuencia)}"

        else:
            # CRC INCORRECTO - hay error
            print("[Servidor] ERROR detectado en el mensaje")
            # Se envía el NACK al cliente -> indica que hubo un error y le pide que lo reenvíe
            respuesta = f"NACK {str(secuencia)}"
        

        # Se envia la respuesta al cliente -> sentdto() envía datos a una dirección específica
        # respuesta.encode() --> convierte str a bytes
        # direccion_cliente --> define a quién enviar (IP y puerto)
        sock.sendto(respuesta.encode("utf-8"), direccion_cliente)
        print(f"[Servidor] Respuesta enviada: {respuesta}\n")


# Punto de entrada del programa -> permite usar el script directamente o importarlo como módulo
if __name__ == "__main__":
    main()