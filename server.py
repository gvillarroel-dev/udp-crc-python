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



# Código de pruebas de funcionamiento:
mensaje = "Hola hola"
codigo = crc16_ccitt(mensaje)
print(f"CRC de '{mensaje}': {codigo}")