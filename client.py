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


# - Prueba de funcionamiento -
mensaje = "Hello world"
codigo = crc16_ccitt(mensaje)
print(f"CRC de {mensaje}: {codigo}")