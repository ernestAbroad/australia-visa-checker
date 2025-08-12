import requests
from bs4 import BeautifulSoup
import os

# --- CONFIGURACIÓN ---
# La URL de la página que vamos a revisar.
URL = "https://immi.homeaffairs.gov.au/what-we-do/whm-program/status-of-country-caps"
# El país que nos interesa. ¡Asegúrate de que coincide con el texto de la web!
PAIS_OBJETIVO = "Argentina"
# El estado que estamos esperando.
ESTADO_DESEADO = "Open"

# --- NOTIFICACIÓN (se configurará más adelante) ---
# Usaremos "Secrets" de GitHub para guardar la URL de notificación de forma segura.
# Si la variable de entorno IFTTT_WEBHOOK_URL existe, la usaremos.
IFTTT_WEBHOOK_URL = os.environ.get("IFTTT_WEBHOOK_URL")

def enviar_notificacion(mensaje):
    """Envía una notificación si la URL del webhook está configurada."""
    if IFTTT_WEBHOOK_URL:
        try:
            # El webhook de IFTTT espera datos en un JSON con "value1"
            payload = {'value1': mensaje}
            response = requests.post(IFTTT_WEBHOOK_URL, json=payload)
            response.raise_for_status() # Lanza un error si la petición falla
            print("¡Notificación enviada con éxito!")
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la notificación: {e}")
    else:
        print("No se ha configurado la URL del webhook. Imprimiendo notificación en la consola.")
        print(mensaje)


def chequear_estado_visa():
    """Chequea la página web y busca el estado de la visa para España."""
    try:
        print(f"Haciendo petición a {URL}...")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        pagina = requests.get(URL, headers=headers, timeout=30)
        pagina.raise_for_status() # Lanza un error si la página no carga (e.g. error 404 o 500)
        
        soup = BeautifulSoup(pagina.content, "html.parser")
        
        # Buscamos todas las filas <tr> de la tabla
        filas = soup.find_all("tr")
        
        encontrado = False
        for fila in filas:
            # Buscamos la celda <td> que contiene nuestro país
            celda_pais = fila.find("td", string=lambda text: PAIS_OBJETIVO in text if text else False)
            if celda_pais:
                encontrado = True
                # La celda del estado es la siguiente celda hermana
                celda_estado = celda_pais.find_next_sibling("td")
                estado_actual = celda_estado.get_text(strip=True) if celda_estado else "No encontrado"
                
                print(f"Estado encontrado para {PAIS_OBJETIVO}: '{estado_actual}'")
                
                # ¡La comprobación clave!
                if ESTADO_DESEADO.lower() in estado_actual.lower():
                    print(f"¡¡¡ALERTA!!! El estado para {PAIS_OBJETIVO} es '{estado_actual}'.")
                    mensaje = f"La visa de Australia para {PAIS_OBJETIVO} está ABIERTA!"
                    enviar_notificacion(mensaje)
                else:
                    print(f"El estado sigue siendo '{estado_actual}'. Volveremos a intentarlo más tarde.")
                break # Salimos del bucle una vez que encontramos España
        
        if not encontrado:
            print(f"No se ha podido encontrar la fila para '{PAIS_OBJETIVO}'. La estructura de la web puede haber cambiado.")

    except requests.exceptions.RequestException as e:
        print(f"Error al intentar acceder a la página: {e}")
    except Exception as e:
        print(f"Ha ocurrido un error inesperado: {e}")

if __name__ == "__main__":
    chequear_estado_visa()
