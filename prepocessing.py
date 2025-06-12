import re
import csv
from dateutil import parser as date_parser
import argparse
from datetime import datetime # Asegurarse de que datetime esté importado para isoformat si no lo está

# Este patrón es clave. Si tus chats tienen un formato ligeramente diferente,
# no se detectará ningún mensaje. Ejemplo: "DD/MM/AAAA, HH:MM - Nombre: Mensaje"
INPUT_PATTERN = re.compile(r"^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}) - ([^:]+): (.+)$")

SISTEMA_PATRONES = [
    re.compile(r"^‎?.*creó el grupo"),
    re.compile(r"^‎?.*añadió a"),
    re.compile(r"^‎?.*te añadió"),
    re.compile(r"^‎?.*cambió el asunto del grupo"),
    re.compile(r"^‎?.*salió del grupo"),
    re.compile(r"^‎?.*fue eliminado"),
    re.compile(r"^‎?.*cambió el icono del grupo"),
    re.compile(r"^‎?.*cambió la foto del grupo"),
]

# Patrón para identificar el autor "Meta AI". Asegúrate de que el nombre sea exacto.
META_AI_PATRON = re.compile(r"^Meta AI$")

# Identifica autores que son números de teléfono (contactos no guardados).
# Busca una cadena que empieza con '+' seguido de dígitos y espacios.
CONTACTO_NO_AÑADIDO_PATRON = re.compile(r"^\+\d[\d\s]+")

# --- NUEVO: Mapeo de nicknames a nombres reales ---
# Define aquí tus nicknames y los nombres a los que quieres mapearlos.
# Las claves son los nicknames tal como aparecen en el chat.
# Los valores son los nombres estandarizados que quieres usar para el análisis.
NICKNAME_MAPPING = {
    "Galletita Ginger": "Pablo",
    "Davidinchi": "David",
    "Joseja": "JJ",
    "Alba Malbada😈": "Alba",
    "Alii": "Alicia",
    "Anaaa": "Ana",
    "ElQuique🦍": "Quique",
    "ElNachos": "Nacho",
    "Elena S": "Elena",
    "Ivanosaurio": "Iván",
    "Miri": "Miriam",
    "Jose G": "Jose",
    "~𝙷𝚎𝚕𝚎𝚗 ❀": "Helen"
}
# --------------------------------------------------

def es_mensaje_de_sistema(texto):
    texto = texto.replace('‎', '')  # Elimina caracteres invisibles
    for patron in SISTEMA_PATRONES:
        if patron.match(texto):
            return True
    return False

def es_mensaje_de_meta_ai(autor):
    # Limpia el nombre del autor antes de comparar, por si hay espacios extra
    return bool(META_AI_PATRON.match(autor.strip()))

def es_contacto_no_añadido(autor):
    """Comprueba si el autor parece ser un número de teléfono (contacto no guardado)."""
    return bool(CONTACTO_NO_AÑADIDO_PATRON.match(autor.strip()))

def normalizar_fecha(date_str, time_str):
    try:
        # Esto debería manejar varios formatos de fecha (ej. DD/MM/YY, DD/MM/YYYY)
        # y hora (ej. HH:MM, HH.MM) de forma robusta.
        dt = date_parser.parse(f"{date_str} {time_str}", dayfirst=True)
        return dt.isoformat()
    except Exception as e:
        # print(f"Error normalizando fecha/hora '{date_str} {time_str}': {e}") # Para depuración
        return None

def preprocesar_chat(input_path, output_path):
    mensajes = []
    line_num = 0 # No se usa en el código actual, pero se mantuvo de tu versión
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line_num += 1
            # original_line = line.strip() # No se usa en el código actual, pero se mantuvo de tu versión
            line = line.strip().replace('‎', '') # Limpieza invisible de WhatsApp

            match = INPUT_PATTERN.match(line)
            if match:
                fecha, hora, autor, texto = match.groups()

                autor = autor.strip() # Limpiar espacios extra del autor

                # --- FILTROS DE MENSAJES DE SISTEMA/BOT/NÚMEROS ---
                # Filtrar mensajes de contactos no añadidos (números de teléfono)
                if es_contacto_no_añadido(autor):
                    continue # Ignora esta línea y pasa a la siguiente

                # Filtrar mensajes de Meta AI
                if es_mensaje_de_meta_ai(autor):
                    continue

                # Filtrar mensajes del sistema
                if es_mensaje_de_sistema(texto):
                    continue
                # --------------------------------------------------
                
                # --- APLICAR MAPEO DE NICKNAMES (¡después de los filtros!) ---
                if autor in NICKNAME_MAPPING:
                    autor = NICKNAME_MAPPING[autor]
                # ------------------------------------------------------------

                fecha_normalizada = normalizar_fecha(fecha, hora)
                if fecha_normalizada:
                    mensajes.append([fecha_normalizada, autor, texto.strip()]) # Usar el 'autor' ya mapeado
            elif mensajes:
                # Si no coincide el patrón pero ya hay mensajes, es una continuación de línea
                # Asegúrate de limpiar también la línea de continuación
                mensajes[-1][2] += "\n" + line

    with open(output_path, "w", encoding="utf-8", newline='') as f_out:
        writer = csv.writer(f_out, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["fecha", "nombre", "mensaje"])  # Cabecera
        writer.writerows(mensajes)

    print(f"☑️ {len(mensajes)} mensajes procesados. Guardado en: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Preprocesador de chats de WhatsApp (salida en CSV).")
    parser.add_argument("input_file", help="Ruta al archivo .txt original exportado de WhatsApp")
    parser.add_argument("output_file", help="Ruta al archivo de salida .csv")
    args = parser.parse_args()

    preprocesar_chat(args.input_file, args.output_file)

if __name__ == "__main__":
    main()