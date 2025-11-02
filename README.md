# 🌐 Comunicación Confiable con CRC y Retransmisión

Implementación de un sistema de comunicación UDP confiable usando CRC-16-CCITT y mecanismos ACK/NACK

---

## Descripción

Este proyecto es un **Trabajo Práctico Integrador** correspondiente a la materia **Redes de Datos** de la Universidad Nacional de Pilar. El mismo implementa un sistema de comunicación cliente-servidor sobre UDP que garantiza la entrega condiable de mensajes mediante:

-   **Detección de errores** con CRC-16-CCITT
-   **Confirmación de entrega** con ACK/NACK
-   **Retransmisión automática** en caso de errores
-   **Control de duplicados** con números de secuencia
-   **Simulación de errores** para pruebas (_basados en probabilidades modificables_)

### Contexto Académico:

-   **Universidad:** Universidad Nacional de Pilar - UNPILAR
-   **Facultad:** Producción y Tecnología
-   **Carrera:** Tecnicatura Universitaria en Desarrollo de Software
-   **Materia:** Redes de Datos
-   **Docente:** Mariana Gil
-   **Autores:** Villarroel Giuliana y Parra Josefina
-   **Año:** 2025

---

## Funcionalidades

-   Comunicación UDP bidireccional
-   Simulación de errores de transmisión
-   Interfa de línea de comandos interactiva
-   Logs detallados de todas las operaciones
-   Soporte para mensajes de texto arbitrarios

---

## Uso

### 1. Clonar el Repositorio

```bash
# Clonar usando HTTPD
git clone https://github.com/gvillarroel-dev/udp-crc-python.git

# Navegar al directorio del proyecto
cd udp-crc-python
```

### 2. Iniciar el servidor

Abre una terminal y ejecuta:

```bash
python server.py
```

**Salida esperada:**

```bash
[Servidor] Iniciando servidor en 127.0.0.1:5000
[Servidor] Probabilidad de error: 60.0%
[Servidor] Esperando mensajes...
```

### 3. Iniciar el Cliente

Abre otra terminal y ejecuta:

```bash
python client.py
```

**Salida esperada:**

```
[Cliente] Iniciando cliente
[Cliente] Servidor: 127.0.0.1:5000
[Cliente] Timeout: 1.0s
[Cliente] Máximo número de intentos: 5

**************************************************
Escribe un mensaje y presiona 'Enter' para enviarlo
Presiona 'Enter' para salir
**************************************************

Mensaje a enviar:
```

### 4. Enviar Mensajes

Escribe un mensaje y presiona 'Enter':

```bash
Mensaje a enviar: Hola mundo

[Cliente] Enviando... (intento 1 de 5)
        Secuencia: 0
        Mensaje: Hola mundo
        CRC: 4A3F
[Cliente] Esperando respuesta...
[Cliente] Respuesta recibida: ACK 0
[Cliente] ACK recibido - Mensaje entregado exitosamente
[Cliente] Próxima secuencia: 1

Mensaje a enviar:
```

### 5. Salir

Presiona 'Enter' sin escribir nada para cerrar el cliente:

```bash
Mensaje a enviar:
[Cliente] Cerrando cliente...
[Cliente] Cliente cerrado
```

Para detener el servidor, presiona `Ctrl+C`

---

### Configuración Avanzada

#### Cambiar Puerto del Servidor

**En `server.py`:**

```python
PORT = 8080  # Cambiar de 5000 a 8080
```

**En `client.py`:**

```python
PORT_SERVIDOR = 8080  # Debe coincidir con el servidor
```

#### Ajustar Probabilidad de Error

**En `server.py`:**

```python
PROBABILIDAD_DE_ERROR = 0.5  # 50% de errores
```

#### Modificar Timeout y Reintentos

**En `client.py`:**

```python
MAX_TIEMPO_DE_ESPERA = 2.0  # 2 segundos
MAX_INTENTOS = 10  # 10 reintentos
```

#### Usar en Red Local

Para comunicar dos computadoras diferentes:

**En el servidor:**

```python
HOST = "0.0.0.0"  # Escuchar en todas las interfaces
```

**En el cliente:**

```python
HOST_SERVIDOR = "192.168.1.100"  # IP del servidor
```

---

## 🔌 Protocolo de Comunicación

### Formato del Mensaje

```
secuencia|mensaje|CRC
```

**Ejemplo:**

```
0|Hola mundo|A3F1
```

**Componentes:**

-   `secuencia`: Número 0 o 1 (previene duplicados)
-   `mensaje`: Texto a transmitir
-   `CRC`: Código de verificación en hexadecimal (4 dígitos)

### Respuestas del Servidor

-   `ACK 0` -> Mensaje con secuencia=0 recibido correctamente (_cliente cambia a secuencia=1 para siguiente mensaje_)
-   `ACK 1` -> Mensaje con secuencia=1 recibido correctamente (_cliente cambia a secuencia=0 para siguiente mensaje_)
-   `NACK 0` -> Error en mensaje con secuencia=0 (_se reenvía el mismo mensaje_)
-   `NACK 1` -> Error en mensaje con secuencia=1 (_se reenvía el mismo mensaje_)

---

## Autores

### Estudiantes

-   **Villarroel Giuliana**

    -   Email: giu.villarroel@gmail.com
    -   Tecnicatura en Desarrollo de Software

-   **Parra Josefina**
    -   Email: josefinamercedesparra8@gmail.com
    -   Tecnicatura en Desarrollo de Software

### Docente

-   **Mariana Gil**
    -   Universidad Nacional de Pilar
    -   Materia: Redes de Datos

---

<div align="center">

**Hecho con ❤️ por estudiantes de UNPILAR**

[⬆ Volver arriba](#-comunicación-confiable-con-crc-y-retransmisión)

</div>
