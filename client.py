#!/usr/bin/env python3
"""
UNPILAR - Facultad de Producción y Tecnología - Tecnicatura Universitaria en Desarrollo de Software
- Proyecto: Servidor UDP con verificación CRC y simulación de errores.
- Autores: Villarroel Giuliana y Parra Josefina
- Docente: Mariana Gil
- Materia: Redes de Datos


EL CLIENTE DEBE:
- Enviar mensajes al servidor y asegurarse de que lleguen correctamente
- Calcular CRC (código de verificación) y adjuntarlo al mensaje
- Esperar respuesta -> ACK = OK | NACK = error
- Retransmitir mensaje si hay error o timeout
- Si luego de varios intentos no funciona -> informa el error
"""

import socket
import time


# =============================================== CONFIGURACIÓN ====================================================
HOST_SERVIDOR = "127.0.0.1" # IP del servidor en localhost -> se cambia la IP por la IP de la otra máquina para transmisión
PORT_SERVIDOR = 5000 # Puerto del servidor
MAX_TIEMPO_DE_ESPERA = 1.0 # (segundos)
MAX_INTENTOS = 5 # Cantidad máxima de reintentos -> luego de 5 intentos, abandona y reporta el error
# ==================================================================================================================


# Función para calcular CRC -> se utiliza el mismo algoritmo que en server.py para que funcione la verificación
def crc16_ccitt(data):
    """
    Calcula el CRC16-CCITT del mensaje a enviar
        - CRC (Verificación de Redundancia Cíclica) -> es un código matemático que identifica el mensaje de forma única
            - Si cambia un bit del mensaje, el código cambia por completo
        - Detecta errores de transmisión
        - Verifica la integridad del mensaje

    - Parámetros -> data: str o bytes >>> el mensaje del que se calcuralá el CRC
    - Return -> int, número de 16 bits que representa el CRC

    """

    # Convierte el mensaje a bytes -> la computadora trabaja con números, no con letras
    if type(data) == str:
        data = data.encode("utf-8")

    # Se inicializa el CRC -> valor inicial estándar para CRC16-CCITT: 0xFFFF en hexa
    crc = 0xFFFF

    # Se procesa cada byte del mensaje -> cada byte modifica el crc de forma matemática
    for byte in data:
        crc = crc ^ (byte << 8)

        # Se procesa cada bit del byte usando el polinomio 0x1021
        for i in range(8):
            # Verificar si el el primer bit es 1
            if crc & 0x8000:
                # Si es 1 -> desplaza crc un bit a la izquierda (empuja todos los bits hacia izquierda. Por ej: 1011 << 1 = 0110)
                crc = (crc << 1) ^ 0x1021
            else:
                # Si es 0 -> desplaza un bit a izquierda
                crc = crc << 1

            # Se mantienen solo 16 bits (en caso de generar más números con desplazamiento)
            crc = crc & 0xFFFF
    
    # Se retorna la "huella" del mensaje
    return crc



# FUNCIÓN: enviar mensaje con retransmisión automática -> implementa la lógica de transmisión confiable
def enviar_mensaje(sock, direccion_servidor, secuencia, mensaje):
    """
    Envía un mensaje al servidor y espera confirmación. Si hay problemas, retransmite automáticamente el mensaje
    
    - Funcionamiento:
        1. Calcula el CRC del mensaje
        2. Construye el paquete de datos -> secuencia|mensaje|crc
        3. Envia el paquete al servidor
        4. Espera respuesta -> ACK|NACK
            - ACK -> éxito
            - NACK -> reintenta
        5. Repite hasta MAX_INTENTOS veces
    
    - Parámetros:
        sock -> el socket UDP para enviar/recibir datos
        direccion_servidor -> tupla(IP, puerto) del servidor
        secuencia -> número de secuencia del mensaje (0 - 1)
        mensaje -> el texto a enviar
    
    - Return -> bool; True si el envío fue OK, False si falló después de todos los intentos

    """
    
    # Se calcula el CRC del mensaje -> este código será usado por el servidor para verificar la integridad del mensaje
    crc = crc16_ccitt(mensaje)

    # Construcción del paquete completo: secuencia|mensaje|crc
    # Conversión CRC a hexadecimal -> formato: 04x = 4 dígitos hex
    paquete = f"{str(secuencia)}|{mensaje}|{format(crc, "04X")}"

    # Se inicializa el contador de intentos
    intentos = 0

    # Bucle de reintentos -> implementación de "persistencia" del protocolo (intentará hasya MAX_INTENTOS o hasta recibir ACK)
    while intentos < MAX_INTENTOS:
        
        # Incrementar contador de intentos
        intentos += 1

        # Se informa al usuario sobre el envío
        print(f"\n[Cliente] Enviando... (intento {intentos} de {MAX_INTENTOS})")
        print(f"\tSecuencia: {secuencia}")
        print(f"\tMensaje: {mensaje}")
        print(f"\tCRC: {format(crc, "04X")}")

        # Envio del paquete al servidor -> sendto() envía datos por UDP a una dirección especifica
        # paquete.encode(...) -> convierte str a bytes
        # direccion_servidor -> tupla (IP, puerto) del destino
        sock.sendto(paquete.encode("utf-8"), direccion_servidor)

        print("[Cliente] Esperando respuesta...")

        # Intentar hasta recibir respuesta del servidor
        # Se usa try-except para manejar la respuesta recibida (y procesarla) y el timeout (para reintentar)
        try:
            # Se reciben datos del servidor -> recvfrom() espera hasta recibir datos o hasta timeout (si pasa el tiempo sin respuesta, lanza excepción)
            respuesta, direccion = sock.recvfrom(1024)

            # Se decodifican bytes a texto
            respuesta_texto = respuesta.decode("utf-8")
            
            print(f"[Cliente] Respuesta recibida: {respuesta_texto}")

            # Parsear la respuesta -> formato esperado: "ACK 0" | "NACK 1"
            partes_respuesta = respuesta_texto.split()

            # Se valida que tenga exactamente 2 partes (por formato esperado)
            if len(partes_respuesta) == 2:

                # Se extraen el tipo de respuesta y la secuencia
                tipo = partes_respuesta[0]  # ACK | NACK
                seq_respuesta = int(partes_respuesta[1]) # 0 | 1

                # ACK recibido -> el mensaje se recibió correctamente
                if tipo == "ACK" and seq_respuesta == secuencia:
                    # ACK con secuencia correcta -> transmisión de datos exitosa
                    print("[Cliente] ACK recibido - Mensaje entregado exitosamente")
                    return True  # Salir de la función, la transmisión del mensaje fue OK
                
                # NACK recibido -> el mensaje se recibió pero estaba corrupto (error de transmisión o CRC no coincide)
                elif tipo == "NACK":
                    print("[Cliente] NACK recibido - Error detectado, reintentando...")
                    
                    # Se espera 1s antes de reintentar la transmisión
                    time.sleep(1.0)
                    # El loop continua y reintenta...

        # Manejo del timeout -> recvfrom() no recibió nada en el tiempo límite, se lanzó la excepción
        except socket.timeout:
            # Si el servidor no respondió a tiempo y pasó el tiempo de respuesta -> reintenta
            print("[Cliente] Timeout - No hubo respuesta del servidor")
            print("[Cliente] Reintentando...")
            time.sleep(1.0)
            # El loop continua y reintenta

        
    # Si se llegó hasta acá, no hay más intentos -> No se pudo entregar el mensaje
    print(f"[Cliente] ERROR: No se pudo entregar el mensaje luego de {MAX_INTENTOS} intentos")
    return False  # Se indica el fracaso de la transmisión
    

# Prueba de funcionamiento -> realizado con el server.py corriendo
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(MAX_TIEMPO_DE_ESPERA)
direccion_servidor = (HOST_SERVIDOR, PORT_SERVIDOR)

res = enviar_mensaje(sock, direccion_servidor, 0, "Hola")