# AXIOM Reporter

AXIOM Reporter es una herramienta de documentacion asistida por IA para pentesters y estudiantes de ciberseguridad. Permite generar informes mientras se trabaja sobre una maquina de Hack The Box, TryHackMe, un CTF o un laboratorio propio, simplemente subiendo capturas de pantalla.

## Caracteristicas

| Funcionalidad | Descripcion |
| --- | --- |
| Analisis con IA | LLaMA 4 Vision analiza cada captura e identifica herramientas, IP, puertos y vulnerabilidades. |
| Sesiones persistentes | Las sesiones se guardan localmente en `sessions.json`. |
| Historial de maquinas | La barra lateral permite recuperar sesiones anteriores. |
| Edicion de entradas | Cada entrada generada por la IA se puede editar o eliminar. |
| Notas manuales | Se puede anadir contexto antes de analizar una captura. |
| Severidad | Los hallazgos se clasifican como Critico, Alto, Medio, Bajo o Informativo. |
| Resumen ejecutivo | La IA genera un resumen de los hallazgos de la sesion. |
| Exportacion a PDF | Genera un informe preparado para imprimir o guardar como PDF. |
| Exportacion a Obsidian | Descarga Markdown junto con las imagenes de la sesion. |
| Almacenamiento local | Los datos se guardan en el equipo; las capturas solo se envian a Groq al solicitar un analisis. |

## Flujo de uso

1. Crea una sesion, por ejemplo, `Lame - Hack The Box`.
2. Sube una captura de un escaneo de Nmap.
3. La IA identifica los datos visibles, como la IP, los puertos y el comando.
4. AXIOM genera una entrada para el informe.
5. Repite el proceso para cada paso del pentest.
6. Exporta el resultado como PDF o Markdown para Obsidian.

Ejemplo de analisis generado:

```text
FASE: Reconocimiento
HERRAMIENTA / COMANDO: sudo nmap -p- -sS -sC -sV --min-rate 5000 -n -vvv -Pn 172.17.0.2 -oN escaneo
HALLAZGO:
  - IP: 172.17.0.2
  - Puertos abiertos: 22/tcp (SSH), 80/tcp (HTTP)
ANALISIS TECNICO: El escaneo SYN stealth revela dos servicios activos.
El puerto 22 sugiere acceso SSH potencialmente explotable si hay credenciales debiles. El puerto 80 indica presencia web y un posible vector de ataque.
SIGUIENTE PASO SUGERIDO: Enumerar el servicio web con gobuster o ffuf y verificar la version de SSH con nmap --script=ssh2-enum-algos.
```

## Requisitos

- Python 3.8 o superior.
- Una cuenta de [Groq](https://console.groq.com/) y una API key.
- Conexion a Internet para las llamadas a la API de Groq.

## Instalacion

### 1. Clonar el repositorio

```bash
git clone https://github.com/zafiro-exploit/-AXIOM-Reporter.git
cd ./-AXIOM-Reporter
```

### 2. Crear y activar un entorno virtual

Linux y macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Al activarlo, normalmente aparecera `(.venv)` al principio de la linea de comandos. Para salir del entorno virtual, ejecuta `deactivate`.

### 3. Instalar las dependencias

Con el entorno virtual activo:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configurar la API key de Groq

1. Accede a [Groq Console](https://console.groq.com/).
2. Crea una cuenta o inicia sesion.
3. Abre **API Keys**, selecciona **Create API Key** y copia la clave.

Define la variable solo para la terminal actual.

Linux y macOS:

```bash
export GROQ_API_KEY="gsk_TU_KEY_AQUI"
```

Windows (PowerShell):

```powershell
$env:GROQ_API_KEY = "gsk_TU_KEY_AQUI"
```

### 5. Iniciar la aplicacion

```bash
python app.py
```

La aplicacion intentara abrir automaticamente [`http://localhost:5000`](http://localhost:5000) en el navegador.

## Uso

### Crear una sesion

Pulsa **+ Nueva sesion** en la barra lateral e introduce el nombre de la maquina.

### Analizar una captura

1. Pulsa la zona de subida o arrastra una imagen sobre ella.
2. Anade contexto opcional en el campo de notas.
3. Selecciona la fase y la severidad del hallazgo.
4. Pulsa **Analizar con IA**.

### Editar entradas

Usa los botones **Editar** y **Borrar** de cada entrada para corregir el contenido generado.

### Generar el resumen ejecutivo

Pulsa **Resumen IA** para generar un parrafo con los hallazgos mas relevantes de la sesion.

### Exportar

- **Exportar PDF:** abre el informe en una ventana nueva. Usa `Ctrl+P` (o `Cmd+P` en macOS) y selecciona **Guardar como PDF**.
- **Exportar Obsidian (.md):** descarga el archivo Markdown y las imagenes para moverlos al vault de Obsidian.

## Estructura del proyecto

```text
-AXIOM-Reporter/
|-- app.py            # Servidor Flask e interfaz web
|-- requirements.txt  # Dependencias de Python
|-- sessions.json     # Datos locales; se crea al guardar una sesion
|-- .gitignore        # Archivos excluidos del control de versiones
`-- README.md         # Documentacion del proyecto
```

## Etica y privacidad

AXIOM Reporter esta disenado para utilizarse de forma explicita y controlada:

- No captura la pantalla automaticamente.
- No registra pulsaciones de teclado.
- No monitoriza procesos en segundo plano.
- El usuario decide que capturas se documentan.
- Las imagenes se envian a la API de Groq solo al solicitar un analisis.
- El resto de los datos se almacena localmente en `sessions.json`.

La herramienta esta destinada a fines educativos y a entornos donde se cuente
con autorizacion, como Hack The Box, TryHackMe o laboratorios propios.

## Stack tecnico

| Componente | Tecnologia |
| --- | --- |
| Backend | Python y Flask |
| Frontend | HTML, CSS y JavaScript sin frameworks |
| Modelo de vision | `meta-llama/llama-4-scout-17b-16e-instruct` mediante la API de Groq |
| Persistencia | JSON local |
| Exportacion | Impresion HTML a PDF y Markdown |

## Roadmap

- [ ] Soporte multiusuario con autenticacion basica.
- [ ] Integracion con la API de Notion.
- [ ] Timeline visual de la sesion.
- [ ] Arrastrar y soltar para reordenar entradas.
- [ ] Selector de modo oscuro o claro.
- [ ] Imagen Docker para facilitar el despliegue.

## Autor

**Zafiro**<br>
Estudiante de ciberseguridad - Blue Team / Pentesting

> Los informes son la parte mas tediosa del pentest. Esta herramienta los hace
> automaticamente mientras hackeas.

## Licencia

MIT License. Puedes usar, modificar y compartir el proyecto conforme a sus terminos.