import re
import csv
from dateutil import parser as date_parser
import argparse
from datetime import datetime
import os

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

META_AI_PATRON = re.compile(r"^Meta AI$")
CONTACTO_NO_AÑADIDO_PATRON = re.compile(r"^\+\d[\d\s]+")

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

def es_mensaje_de_sistema(texto):
    texto = texto.replace('‎', '')
    return any(patron.match(texto) for patron in SISTEMA_PATRONES)

def es_mensaje_de_meta_ai(autor):
    return bool(META_AI_PATRON.match(autor.strip()))

def es_contacto_no_añadido(autor):
    return bool(CONTACTO_NO_AÑADIDO_PATRON.match(autor.strip()))

def normalizar_fecha(date_str, time_str):
    try:
        dt = date_parser.parse(f"{date_str} {time_str}", dayfirst=True)
        return dt.isoformat()
    except Exception:
        return None

def limpiar_csv_de_nuls(input_path):
    """
    Elimina caracteres NUL (\x00) del archivo CSV sobrescribiendo el original.
    """
    temp_path = input_path + ".tmp"
    with open(input_path, "r", encoding="utf-8", errors="replace") as fin, \
         open(temp_path, "w", encoding="utf-8", newline='') as fout:
        for line in fin:
            fout.write(line.replace('\x00', ''))
    os.replace(temp_path, input_path)
    print(f"🧹 Limpieza de caracteres NUL completada: {input_path}")

def preprocesar_chat(input_path, output_path):
    mensajes = []
    line_num = 0
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line_num += 1
            line = line.strip().replace('‎', '').replace('\x00', '')

            match = INPUT_PATTERN.match(line)
            if match:
                fecha, hora, autor, texto = match.groups()
                autor = autor.strip()

                if es_contacto_no_añadido(autor) or es_mensaje_de_meta_ai(autor) or es_mensaje_de_sistema(texto):
                    continue

                if autor in NICKNAME_MAPPING:
                    autor = NICKNAME_MAPPING[autor]

                fecha_normalizada = normalizar_fecha(fecha, hora)
                if fecha_normalizada:
                    mensaje_limpio = texto.strip().replace('\x00', '')
                    mensajes.append([fecha_normalizada, autor, mensaje_limpio])
            elif mensajes:
                mensajes[-1][2] += "\n" + line.replace('\x00', '')

    with open(output_path, "w", encoding="utf-8", newline='') as f_out:
        writer = csv.writer(f_out, quoting=csv.QUOTE_MINIMAL, escapechar='\\')
        writer.writerow(["fecha", "nombre", "mensaje"])
        writer.writerows(mensajes)

    print(f"☑️ {len(mensajes)} mensajes procesados. Guardado en: {output_path}")

    # Limpieza final de caracteres NUL en el archivo generado
    limpiar_csv_de_nuls(output_path)

def main():
    parser = argparse.ArgumentParser(description="Preprocesador de chats de WhatsApp (salida en CSV).")
    parser.add_argument("input_file", help="Ruta al archivo .txt original exportado de WhatsApp")
    parser.add_argument("output_file", help="Ruta al archivo de salida .csv")
    args = parser.parse_args()

    preprocesar_chat(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
