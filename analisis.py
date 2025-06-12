import csv
import argparse
from collections import defaultdict, Counter
from datetime import datetime
import re
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

try:
    nltk.data.find('corpora/stopwords')
except nltk.downloader.DownloadError:
    print("Descargando 'stopwords' de NLTK...")
    nltk.download('stopwords')
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    print("Descargando 'punkt' de NLTK...")
    nltk.download('punkt')

STOPWORDS_ES = set(stopwords.words('spanish'))
PALABRAS_A_EXCLUIR = {
    "multimedia", "omitido", "https", "http", "www", "com", 
    "q", "k", "xd", "jajaja", "jejeje", "xD", "jaja", "jajajaja", # Risas y abreviaturas
    "si", "no", "gracias", "ok", "vale", "claro", "bueno", "hola", "adios", # Respuestas cortas
    "un", "una", "unos", "unas", "el", "la", "los", "las", # Artículos
    "este", "esta", "estos", "estas", "ese", "esa", "esos", "esas", # Demostrativos
    "así", "más", "menos", "muy", "poco", "mucho", "demasiado", # Adverbios de cantidad/modo
    "todo", "nada", "algo", "nadie", "alguien", "siempre", "nunca", "aún", "ya", "ahora", # Indefinidos/temporales
    "bien", "mal", "mejor", "peor", "casi", "solo", "solo", "tampoco", # Adverbios
    "ser", "estar", "hacer", "ir", "tener", "decir", "poder", "querer", "haber", "ver", # Verbos comunes (en infinitivo)
    "que", "de", "en", "con", "por", "para", "sin", "sobre", "entre", "hasta", "desde", # Preposiciones/conjunciones comunes
    "mí", "ti", "él", "ella", "ello", "nosotros", "vosotros", "ellos", "ellas", # Pronombres
    "qué", "quién", "cómo", "cuándo", "dónde", "porqué", "cual", # Interrogativos/exclamativos
    "buenos", "días", "noches", "tardes", # Saludos comunes
    "whatsapp", "grupo", "chat", # Palabras relacionadas con el contexto
    "hoy", "mañana", "ayer", "semana", "mes", "año", # Tiempo
    # Añade más palabras que consideres irrelevantes para tus sustantivos principales
    "a", "ante", "bajo", "cabe", "con", "contra", "de", "desde", "durante", "en",
    "entre", "hacia", "hasta", "para", "por", "según", "sin", "so", "sobre", "tras",
     "voy","pa", "casa", "va", "puedo", "luego", "tarde", "aunq", "pos", "pues", "pablo", "anto", "deivi", "josemi", "david", "jj", "aj", "german", "alex",
    "pues", "porque", "aunque", "pero", "sino", "ya que", "como", "cuando",
    "vamos", "creo", "verdad", "hora", "puede"
}
STOPWORDS_ES.update(PALABRAS_A_EXCLUIR)

EMOJI_PATTERN = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)
URL_PATTERN = re.compile(r'https?://\S+|www\.\S+') # Expresión regular para detectar URLs
PREGUNTA_PATTERN = re.compile(r'.*\?(\s*)$') # Expresión regular para detectar mensajes que terminan en '?'

def cargar_mensajes_csv(path):
    mensajes = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                fecha = datetime.fromisoformat(row["fecha"])
                nombre = row["nombre"]
                mensaje = row["mensaje"]
                mensajes.append((fecha, nombre, mensaje))
            except Exception as e:
                continue
    return mensajes

def contar_emojis(texto):
    return len(EMOJI_PATTERN.findall(texto))

def contar_enlaces(texto):
    """Cuenta el número de URLs (enlaces) en un texto."""
    return len(URL_PATTERN.findall(texto))

def es_pregunta(texto):
    """Comprueba si un mensaje termina en un signo de interrogación."""
    return bool(PREGUNTA_PATTERN.match(texto.strip()))

# --- Funciones para análisis avanzado ---

def obtener_palabras_frecuentes(mensajes_usuario, num_top=10):
    """Obtiene las palabras más frecuentes de un usuario, excluyendo stopwords y palabras específicas."""
    all_words = []
    for msg in mensajes_usuario:
        words = word_tokenize(msg.lower())
        filtered_words = [word for word in words if word.isalpha() and word not in STOPWORDS_ES]
        all_words.extend(filtered_words)
    
    return Counter(all_words).most_common(num_top)


def analizar_menciones(mensajes_usuario, todos_los_usuarios_set):
    """
    Cuenta las menciones a otros usuarios en los mensajes de un usuario.
    La lógica de 'word boundary' (\b) ayuda a evitar subcadenas.
    """
    menciones_contador = Counter()
    for msg in mensajes_usuario:
        msg_lower = msg.lower()
        for usuario_mencionado in todos_los_usuarios_set:
            usuario_mencionado_lower = usuario_mencionado.lower()
            if len(usuario_mencionado_lower) > 2 and re.search(r'\b' + re.escape(usuario_mencionado_lower) + r'\b', msg_lower):
                menciones_contador[usuario_mencionado] += 1
    return menciones_contador


# --- Función principal de análisis (modificada) ---

def analizar_todo(mensajes):
    stats_usuarios = {}
    horas_por_usuario = defaultdict(list)
    dias_semana_por_usuario = defaultdict(list) # Nuevo: para contar mensajes por día de la semana
    
    todos_los_usuarios_set = set(nombre for _, nombre, _ in mensajes)
    mensajes_por_usuario = defaultdict(list)

    menciones_por_autor = defaultdict(Counter)
    menciones_globales = Counter()

    for fecha, nombre, mensaje in mensajes:
        mensajes_por_usuario[nombre].append(mensaje)

        if nombre not in stats_usuarios:
            stats_usuarios[nombre] = {
                "num_mensajes": 0, "num_palabras": 0, "total_longitud": 0,
                "num_emojis": 0, "num_multimedia": 0,
                "num_enlaces": 0, # <-- NUEVA MÉTRICA
                "num_preguntas": 0, # <-- NUEVA MÉTRICA
                "palabras_mas_usadas": [] 
            }
        
        stats_usuarios[nombre]["num_mensajes"] += 1
        stats_usuarios[nombre]["num_palabras"] += len(mensaje.split())
        stats_usuarios[nombre]["total_longitud"] += len(mensaje)
        stats_usuarios[nombre]["num_emojis"] += contar_emojis(mensaje)
        stats_usuarios[nombre]["num_enlaces"] += contar_enlaces(mensaje)
        if es_pregunta(mensaje): # <-- Contar preguntas aquí
            stats_usuarios[nombre]["num_preguntas"] += 1
        
        if mensaje.strip() == "<Multimedia omitido>":
            stats_usuarios[nombre]["num_multimedia"] += 1
        
        horas_por_usuario[nombre].append(fecha.hour)
        dias_semana_por_usuario[nombre].append(fecha.weekday()) # Almacenar día de la semana (0=Lunes)

        menciones_en_este_mensaje = analizar_menciones([mensaje], todos_los_usuarios_set)
        for mencionado, conteo in menciones_en_este_mensaje.items():
            if mencionado != nombre:
                menciones_por_autor[nombre][mencionado] += conteo
                menciones_globales[mencionado] += conteo


    # Procesar después de iterar todos los mensajes
    resultados_usuario = []
    for nombre, datos in stats_usuarios.items():
        datos['palabras_mas_usadas'] = obtener_palabras_frecuentes(mensajes_por_usuario[nombre])
        
        top_menciones_hechas = menciones_por_autor[nombre].most_common(3)
        datos['menciones_hechas'] = ", ".join([f"{u} ({c})" for u, c in top_menciones_hechas])

        media_long = 0
        if datos["num_mensajes"] > 0:
            media_long = datos["total_longitud"] / datos["num_mensajes"]
        
        hora_fav = None
        if horas_por_usuario[nombre]:
            hora_fav = Counter(horas_por_usuario[nombre]).most_common(1)[0][0]

        resultados_usuario.append({
            "nombre": nombre,
            "num_mensajes": datos["num_mensajes"],
            "num_palabras": datos["num_palabras"],
            "media_longitud_mensaje": round(media_long, 2),
            "hora_favorita": hora_fav,
            "num_emojis": datos["num_emojis"],
            "num_multimedia": datos["num_multimedia"],
            "num_enlaces": datos["num_enlaces"],
            "num_preguntas": datos["num_preguntas"], # <-- Incluir en los resultados
            "palabras_mas_usadas": str(datos["palabras_mas_usadas"]), 
            "menciones_hechas": str(datos["menciones_hechas"])
        })
    
    persona_mas_mencionada = None
    if menciones_globales:
        persona_mas_mencionada = menciones_globales.most_common(1)[0]
    
    # Convertir menciones_por_autor a un formato de DataFrame para el heatmap
    menciones_por_autor_lista = []
    for autor, menciones in menciones_por_autor.items():
        for mencionado, conteo in menciones.items():
            menciones_por_autor_lista.append({
                "autor_mencionador": autor,
                "usuario_mencionado": mencionado,
                "conteo": conteo
            })
    df_menciones_por_autor = pd.DataFrame(menciones_por_autor_lista)

    return resultados_usuario, {
        "persona_mas_mencionada": persona_mas_mencionada,
        "todas_las_menciones_globales": menciones_globales.most_common(5),
        "df_menciones_por_autor": df_menciones_por_autor # <-- Nuevo: DataFrame para heatmap
    }


# --- El resto de funciones existentes ---

def contar_mensajes_por_mes_y_usuario(mensajes):
    contador = defaultdict(int)
    for fecha, nombre, _ in mensajes:
        clave = (fecha.year, fecha.month, nombre)
        contador[clave] += 1
    resultado = [{"año": año, "mes": mes, "usuario": usuario, "num_mensajes": total}
                 for (año, mes, usuario), total in sorted(contador.items())]
    return resultado

def contar_mensajes_por_hora_y_usuario(mensajes):
    contador = defaultdict(int)
    for fecha, nombre, _ in mensajes:
        clave = (fecha.hour, nombre)
        contador[clave] += 1
    
    resultado = []
    usuarios_unicos = sorted(list(set(nombre for _, nombre, _ in mensajes)))

    for hora in range(24):
        for usuario in usuarios_unicos:
            num_mensajes = contador[(hora, usuario)]
            resultado.append({
                "hora": hora,
                "usuario": usuario,
                "num_mensajes": num_mensajes
            })
    resultado.sort(key=lambda x: (x['hora'], x['usuario']))
    
    return resultado

# --- NUEVA FUNCIÓN: Contar mensajes por día de la semana y usuario ---
def contar_mensajes_por_dia_semana_y_usuario(mensajes):
    contador = defaultdict(int)
    for fecha, nombre, _ in mensajes:
        # fecha.weekday() devuelve 0 para lunes, 1 para martes, ..., 6 para domingo
        clave = (fecha.weekday(), nombre)
        contador[clave] += 1
    
    resultado = []
    usuarios_unicos = sorted(list(set(nombre for _, nombre, _ in mensajes)))
    dias_semana_nombres = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    for dia_num in range(7): # Días de 0 a 6
        for usuario in usuarios_unicos:
            num_mensajes = contador[(dia_num, usuario)]
            resultado.append({
                "dia_semana_num": dia_num,
                "dia_semana": dias_semana_nombres[dia_num],
                "usuario": usuario,
                "num_mensajes": num_mensajes
            })
    # Ordenar por día de la semana numérico y luego por usuario
    resultado.sort(key=lambda x: (x['dia_semana_num'], x['usuario']))
    
    return resultado


def guardar_csv(diccionarios, output_path, columnas):
    with open(output_path, "w", encoding="utf-8", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()
        writer.writerows(diccionarios)

def main():
    parser = argparse.ArgumentParser(description="Analizador de estadísticas de chats de WhatsApp (entrada CSV).")
    parser.add_argument("input_file", help="Archivo CSV preprocesado")
    parser.add_argument("--out_usuarios", default="stats_usuarios.csv", help="Archivo de salida de stats por usuario")
    parser.add_argument("--out_mensual", default="mensajes_por_mes.csv", help="Archivo de salida de stats por mes y usuario")
    parser.add_argument("--out_horas", default="mensajes_por_hora.csv", help="Archivo de salida de stats por hora y usuario")
    parser.add_argument("--out_menciones_globales", default="menciones_globales.csv", help="Archivo de salida para la persona más mencionada y otras menciones globales.")
    # --- NUEVOS ARGUMENTOS ---
    parser.add_argument("--out_dia_semana", default="mensajes_por_dia_semana.csv", help="Archivo de salida de stats por día de la semana y usuario.")
    parser.add_argument("--out_menciones_por_autor", default="menciones_por_autor.csv", help="Archivo de salida de menciones detalladas por autor para heatmap.")
    # --------------------------
    args = parser.parse_args()

    mensajes = cargar_mensajes_csv(args.input_file)

    print(f"📥 {len(mensajes)} mensajes cargados")

    stats_usuarios, analisis_global = analizar_todo(mensajes)

    # Guardar estadísticas de usuarios (con las nuevas columnas)
    columnas_usuarios = [
        "nombre", "num_mensajes", "num_palabras", "media_longitud_mensaje",
        "hora_favorita", "num_emojis", "num_multimedia", "num_enlaces", "num_preguntas", # <-- ¡Añadidas!
        "palabras_mas_usadas", "menciones_hechas"
    ]
    guardar_csv(stats_usuarios, args.out_usuarios, columnas_usuarios)
    print(f"📊 Estadísticas de usuarios (incl. palabras más usadas, menciones) guardadas en {args.out_usuarios}")

    stats_mes = contar_mensajes_por_mes_y_usuario(mensajes)
    guardar_csv(stats_mes, args.out_mensual, ["año", "mes", "usuario", "num_mensajes"])
    print(f"📆 Estadísticas por mes y usuario guardadas en {args.out_mensual}")

    stats_horas = contar_mensajes_por_hora_y_usuario(mensajes)
    guardar_csv(stats_horas, args.out_horas, ["hora", "usuario", "num_mensajes"])
    print(f"⏰ Estadísticas por hora y usuario guardadas en {args.out_horas}")

    # --- NUEVOS GUARDADOS ---
    stats_dia_semana = contar_mensajes_por_dia_semana_y_usuario(mensajes)
    guardar_csv(stats_dia_semana, args.out_dia_semana, ["dia_semana_num", "dia_semana", "usuario", "num_mensajes"])
    print(f"🗓️ Estadísticas por día de la semana y usuario guardadas en {args.out_dia_semana}")
    
    # Guardar DataFrame de menciones por autor para el heatmap
    # Usaremos el método to_csv de Pandas directamente, ya que ya es un DataFrame
    analisis_global["df_menciones_por_autor"].to_csv(args.out_menciones_por_autor, index=False, encoding="utf-8")
    print(f"👥 Estadísticas de menciones por autor para heatmap guardadas en {args.out_menciones_por_autor}")
    # -----------------------

    if analisis_global["persona_mas_mencionada"]:
        mencion_principal = analisis_global["persona_mas_mencionada"]
        print(f"👑 La persona más mencionada globalmente es: {mencion_principal[0]} con {mencion_principal[1]} menciones.")
    
    menciones_globales_data = [{"usuario_mencionado": u, "conteo": c} for u, c in analisis_global["todas_las_menciones_globales"]]
    guardar_csv(menciones_globales_data, args.out_menciones_globales, ["usuario_mencionado", "conteo"])
    print(f"🗣️ Estadísticas de menciones globales guardadas en {args.out_menciones_globales}")


if __name__ == "__main__":
    main()