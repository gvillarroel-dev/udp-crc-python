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

# Prueba de funcionamiento
mensaje = "hola"
simular_error(mensaje, PROBABILIDAD_DE_ERROR)