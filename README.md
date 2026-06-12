# -AXIOM-Reporter
¿Qué es AXIOM Reporter?  AXIOM Reporter es una herramienta de documentación asistida por IA diseñada para pentesters y estudiantes de ciberseguridad. Permite generar informes profesionales de forma automática mientras avanzas en una máquina (HackTheBox, TryHackMe, CTFs...), simplemente subiendo capturas de pantalla.
✨ Características

FuncionalidadDescripción🤖 Análisis IALLaMA-4 Vision analiza cada captura e identifica herramientas, IPs, puertos y vulnerabilidades reales💾 Sesiones persistentesLas sesiones se guardan localmente en sessions.json. Nunca pierdes tu trabajo🗂️ Historial de máquinasSidebar con todas tus sesiones anteriores, accesibles en cualquier momento✏️ Edición de entradasPuedes editar o borrar cualquier entrada generada por la IA📝 Notas manualesAñade contexto a cada captura antes de analizarla🎯 SeveridadEtiqueta cada hallazgo como Crítico / Alto / Medio / Bajo / Informativo📋 Resumen ejecutivoLa IA genera automáticamente un párrafo ejecutivo de toda la sesión📄 Exportar a PDFInforme profesional listo para imprimir con tu firma🔮 Exportar a ObsidianMarkdown con imágenes listas para importar en tu vault🔒 100% local y privadoLa app corre en tu máquina. Tus capturas nunca salen de tu red


🖼️ Demo

Flujo de uso:
1. Creas una sesión  →  "Lame — HackTheBox"
2. Subes una captura de tu nmap
3. La IA detecta: IP real, puertos reales, comando exacto
4. Se genera el bloque del informe automáticamente
5. Repites por cada paso del pentest
6. Al terminar: exportas PDF o Markdown para Obsidian

Ejemplo de análisis generado:

FASE: Reconocimiento
HERRAMIENTA / COMANDO: sudo nmap -p- -sS -sC -sV --min-rate 5000 -n -vvv -Pn 172.17.0.2 -oN escaneo
HALLAZGO:
  - IP: 172.17.0.2
  - Puertos abiertos: 22/tcp (SSH), 80/tcp (HTTP)
ANÁLISIS TÉCNICO: El escaneo SYN stealth revela dos servicios activos.
El puerto 22 sugiere acceso SSH potencialmente explotable si hay credenciales
débiles. El puerto 80 indica presencia web — vector prioritario de ataque.
SIGUIENTE PASO SUGERIDO: Enumerar el servicio web con gobuster/ffuf y
verificar versión SSH con nmap --script=ssh2-enum-algos.


⚙️ Requisitos


Python 3.8 o superior
Cuenta gratuita en Groq (sin tarjeta de crédito)
Conexión a internet (solo para las llamadas a la API de Groq)



🚀 Instalación

1. Clona el repositorio

bashgit clone https://github.com/zafiro-exploit/axiom-reporter.git
cd axiom-reporter

2. Instala las dependencias

bashpip install flask flask-cors requests

3. Obtén tu API key de Groq (gratis)


Ve a console.groq.com
Crea una cuenta gratuita (no requiere tarjeta)
Ve a API Keys → Create API Key
Copia tu key (empieza por gsk_...)


4. Configura la API key

Linux / Mac:

bashexport GROQ_API_KEY="gsk_TU_KEY_AQUI"

Para hacerlo permanente añádelo a tu ~/.bashrc o ~/.zshrc:

bashecho 'export GROQ_API_KEY="gsk_TU_KEY_AQUI"' >> ~/.bashrc
source ~/.bashrc

Windows (PowerShell):

powershell[System.Environment]::SetEnvironmentVariable("GROQ_API_KEY","gsk_TU_KEY_AQUI","User")

Cierra y vuelve a abrir PowerShell para que se aplique.

5. Lanza la app

bashpython app.py

El navegador se abrirá automáticamente en http://localhost:5000


📖 Uso

Crear una sesión

Haz clic en + Nueva sesión en el sidebar e introduce el nombre de la máquina.

Añadir una captura


Haz clic en la zona de subida (o arrastra la imagen directamente)
Añade contexto opcional en el campo de notas
Selecciona la Fase y la Severidad del hallazgo
Pulsa Analizar con IA


Editar entradas

Cada entrada tiene botones de Editar y Borrar para corregir el análisis si es necesario.

Generar resumen ejecutivo

Pulsa Resumen IA para que el modelo genere automáticamente un párrafo ejecutivo con los hallazgos más relevantes de toda la sesión.

Exportar


Exportar PDF → Abre una ventana nueva con el informe. Usa Ctrl+P → Guardar como PDF.
Exportar Obsidian (.md) → Descarga el .md y todas las imágenes. Muévelos a tu vault de Obsidian.



🗂️ Estructura del proyecto

axiom-reporter/
├── app.py           # Servidor Flask + interfaz web completa
├── sessions.json    # Sesiones guardadas (se crea automáticamente)
└── README.md        # Este archivo


🔐 Ética y privacidad

AXIOM Reporter está diseñado con un enfoque explícitamente ético:


❌ No captura pantalla automáticamente
❌ No registra pulsaciones de teclado
❌ No monitoriza procesos en background
✅ Tú decides qué capturas se documentan
✅ Las imágenes solo se envían a la API de Groq en el momento del análisis
✅ Todo el resto de datos se almacena localmente en tu máquina



Esta herramienta está pensada para uso educativo y en entornos de práctica legal como HackTheBox, TryHackMe o laboratorios propios.




🛠️ Stack técnico

ComponenteTecnologíaBackendPython + FlaskFrontendHTML/CSS/JS vanilla (sin frameworks)Modelo de visiónmeta-llama/llama-4-scout-17b-16e-instruct via Groq APIPersistenciaJSON localExportaciónHTML print-to-PDF + Markdown


🗺️ Roadmap


 Soporte multi-usuario con autenticación básica
 Integración con Notion API para exportar directamente
 Timeline visual de la sesión
 Drag & drop para reordenar entradas
 Modo oscuro / claro
 Docker para despliegue rápido



👤 Autor

Zafiro
Estudiante de ciberseguridad · Blue Team / Pentesting


"Los informes son la parte más tediosa del pentest. Esta herramienta los hace automáticamente mientras hackeas."




📄 Licencia

MIT License — úsalo, modifícalo y compártelo libremente.
