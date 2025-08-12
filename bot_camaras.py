import requests
import os
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# --- LEER SECRETOS DESDE LAS VARIABLES DE ENTORNO ---
# (Estos los configurarás en Railway, no los escribas aquí)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- LISTA DE CÁMARAS ---
CAMERAS = [
    # --- Cámaras Simples (tipo 'image') ---
    {
        "name": "Cartago",
        "page_url": "https://cartagoenvivo.com/",
        "image_id": "liveImage",
        "type": "image",
    },
    {
        "name": "Volcan Turrialba",
        "page_url": "https://www.ovsicori.una.ac.cr/index.php/vulcanologia/camara-volcanes-2/camara-v-turrialba",
        "base_url": "https://www.ovsicori.una.ac.cr",
        "image_id": "camara",
        "type": "image",
    },
    {
        "name": "Volcan Irazu",
        "page_url": "https://www.ovsicori.una.ac.cr/index.php/vulcanologia/camara-volcanes-2/camara-2-v-turrialba",
        "base_url": "https://www.ovsicori.una.ac.cr",
        "image_id": "camara",
        "type": "image",
    },
    {
        "name": "Poas Crater",
        "page_url": "https://www.ovsicori.una.ac.cr/index.php/vulcanologia/camara-volcanes-2/camara-crater-v-poas",
        "base_url": "https://www.ovsicori.una.ac.cr",
        "image_id": "camara",
        "type": "image",
    },
    {
        "name": "Poas SO del Crater",
        "page_url": "https://www.ovsicori.una.ac.cr/index.php/vulcanologia/camara-volcanes-2/camara-v-poas-so-del-crater",
        "base_url": "https://www.ovsicori.una.ac.cr",
        "image_id": "camara",
        "type": "image",
    },
    {
        "name": "Poas Chahuites",
        "page_url": "https://www.ovsicori.una.ac.cr/index.php/vulcanologia/camara-volcanes-2/camara-v-poas-chahuites",
        "base_url": "https://www.ovsicori.una.ac.cr",
        "image_id": "camara",
        "type": "image",
    },
    {
        "name": "Rincon de la Vieja Sensoria",
        "page_url": "https://www.ovsicori.una.ac.cr/index.php/vulcanologia/camara-volcanes-2/rincon-de-la-vieja-sensoria2",
        "base_url": "https://www.ovsicori.una.ac.cr",
        "image_id": "camara",
        "type": "image",
    },
    {
        "name": "Rincon de la Vieja Curubande",
        "page_url": "https://www.ovsicori.una.ac.cr/index.php/vulcanologia/camara-volcanes-2/camara-v-rincon-de-la-vieja-curubande",
        "base_url": "https://www.ovsicori.una.ac.cr",
        "image_id": "camara",
        "type": "image",
    },
    {
        "name": "Rincon de la Vieja Gavilan",
        "page_url": "https://www.ovsicori.una.ac.cr/index.php/vulcanologia/camara-volcanes-2/rincon-de-la-vieja-gavilan",
        "base_url": "https://www.ovsicori.una.ac.cr",
        "image_id": "camara",
        "type": "image",
    },
    {
        "name": "Reserva Karen Mogensen",
        "page_url": "https://www.forestepersempre.org/fps/progetti/CostaRica/webcam/Karen-webcam.html",
        "base_url": "https://www.forestepersempre.org",
        "image_id": "webcam",
        "type": "image",
    },
]

# --- NUEVA CONSTANTE PARA AEROPUERTOS ---
AEROPUERTOS = {
    "MROC": "Juan Santamaría",
    "MRPV": "Tobías Bolaños (Pavas)",
    "MRLB": "Daniel Oduber (Liberia)",
}


def enviar_foto_telegram(imagen_bytes, caption=""):
    """
    Envía una imagen (en bytes) a un chat de Telegram.
    """
    print(f"Enviando foto '{caption}' a Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    files = {"photo": ("image.jpg", imagen_bytes, "image/jpeg")}
    data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption}
    try:
        response = requests.post(url, files=files, data=data, timeout=20)
        response.raise_for_status()
        if response.json().get("ok"):
            print(f"¡Foto '{caption}' enviada con éxito!")
        else:
            print(f"Error en respuesta de Telegram para '{caption}': {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error de red al enviar foto a Telegram: {e}")


# --- NUEVA FUNCIÓN PARA ENVIAR MENSAJES DE TEXTO ---
def enviar_mensaje_telegram(texto):
    """
    Envía un mensaje de texto a un chat de Telegram, usando formato HTML.
    """
    print("Enviando mensaje METAR a Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": texto, "parse_mode": "HTML"}
    try:
        response = requests.post(url, data=data, timeout=20)
        response.raise_for_status()
        if response.json().get("ok"):
            print("¡Mensaje METAR enviado con éxito!")
        else:
            print(f"Error en respuesta de Telegram para mensaje: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error de red al enviar mensaje a Telegram: {e}")


def procesar_y_enviar_camaras():
    """
    Recorre la lista de cámaras, obtiene la imagen y la envía.
    """
    for camera in CAMERAS:
        try:
            print(f"Procesando cámara: {camera['name']}")
            page_response = requests.get(camera["page_url"], timeout=15)
            page_response.raise_for_status()
            soup = BeautifulSoup(page_response.content, "lxml")
            img_tag = soup.find("img", id=camera["image_id"])
            if not img_tag:
                print(
                    f"No se encontró la etiqueta de imagen con ID '{camera['image_id']}' en {camera['page_url']}."
                )
                continue
            img_src = img_tag.get("src")
            full_img_url = urljoin(camera.get("base_url", camera["page_url"]), img_src)
            img_response = requests.get(full_img_url, timeout=15)
            img_response.raise_for_status()
            enviar_foto_telegram(img_response.content, caption=camera["name"])
            time.sleep(2)
        except Exception as e:
            print(f"Error procesando '{camera['name']}': {e}. Omitiendo.")
            continue


# --- NUEVA FUNCIÓN PARA PROCESAR Y ENVIAR REPORTES METAR ---
def procesar_y_enviar_metar():
    """
    Obtiene los reportes METAR y los devuelve como un solo texto formateado.
    """
    print("Procesando reportes METAR...")
    icaos_string = ",".join(AEROPUERTOS.keys())
    api_url = (
        f"https://aviationweather.gov/api/data/metar?ids={icaos_string}&format=json"
    )

    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        metar_data = response.json()

        if not metar_data:
            print("No se recibieron datos METAR de la API.")
            return

        # Formatear el mensaje para Telegram
        mensaje_partes = ["<b>🛰️ Datos METAR Recibidos</b>\n"]
        for reporte in metar_data:
            icao = reporte.get("icaoId")
            texto_crudo = reporte.get("rawOb")
            nombre_aeropuerto = AEROPUERTOS.get(
                icao, icao
            )  # Usa el nombre si lo encuentra
            mensaje_partes.append(
                f"\n<b>📍 {nombre_aeropuerto} ({icao})</b>\n<code>{texto_crudo}</code>"
            )

        mensaje_final = "\n".join(mensaje_partes)
        enviar_mensaje_telegram(mensaje_final)

    except requests.exceptions.RequestException as e:
        print(f"Error al contactar la API de METAR: {e}")
    except Exception as e:
        print(f"Error inesperado al procesar METAR: {e}")


if __name__ == "__main__":
    print("Iniciando bot de cámaras y METAR...")

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(
            "Error: Variables de entorno TELEGRAM_TOKEN y TELEGRAM_CHAT_ID no configuradas."
        )
    else:
        # Ejecuta las tareas una tras otra
        procesar_y_enviar_camaras()

        # Pausa opcional para que los mensajes no lleguen todos al mismo segundo
        time.sleep(5)

        procesar_y_enviar_metar()

    print("--- Script finalizado ---")
