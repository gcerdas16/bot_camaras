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


def enviar_foto_telegram(imagen_bytes, caption=""):
    """
    Envía una imagen (en bytes) a un chat de Telegram.
    """
    print(f"Enviando foto '{caption}' a Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    files = {"photo": ("image.jpg", imagen_bytes, "image/jpeg")}
    data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption}
    try:
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()  # Lanza un error si la petición falló
        if response.json().get("ok"):
            print(f"¡Foto '{caption}' enviada con éxito!")
        else:
            print(f"Error en respuesta de Telegram para '{caption}': {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error de red al enviar a Telegram: {e}")


def procesar_y_enviar_camaras():
    """
    Recorre la lista de cámaras, obtiene la imagen y la envía.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(
            "Error: Variables de entorno TELEGRAM_TOKEN y TELEGRAM_CHAT_ID no configuradas."
        )
        return

    for camera in CAMERAS:
        try:
            print(f"Procesando cámara: {camera['name']}")

            # 1. Obtener el HTML de la página
            page_response = requests.get(camera["page_url"], timeout=15)
            page_response.raise_for_status()
            soup = BeautifulSoup(page_response.content, "lxml")

            # 2. Encontrar la etiqueta de la imagen por su ID
            img_tag = soup.find("img", id=camera["image_id"])
            if not img_tag:
                print(
                    f"No se encontró la etiqueta de imagen con ID '{camera['image_id']}' en {camera['page_url']}. Omitiendo."
                )
                continue

            # 3. Obtener la URL (src) de la imagen
            img_src = img_tag.get("src")
            # Construir la URL completa si es relativa
            full_img_url = urljoin(camera.get("base_url", camera["page_url"]), img_src)

            # 4. Descargar la imagen
            img_response = requests.get(full_img_url, timeout=15)
            img_response.raise_for_status()
            imagen_bytes = img_response.content

            # 5. Enviar a Telegram
            enviar_foto_telegram(imagen_bytes, caption=camera["name"])

            # Pequeña pausa para no saturar la API de Telegram
            time.sleep(2)

        except Exception as e:
            # Si algo falla, lo imprime en los logs de Railway y continúa
            print(f"Error procesando '{camera['name']}': {e}. Omitiendo.")
            continue


if __name__ == "__main__":
    print("Iniciando bot de cámaras...")
    # Ciclo infinito para que se ejecute cada hora
    while True:
        procesar_y_enviar_camaras()
        print(
            "Ciclo completado. Esperando 1 hora (3600 segundos) para el próximo ciclo."
        )
        time.sleep(3600)
