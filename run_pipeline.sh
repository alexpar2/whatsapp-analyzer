#!/bin/bash

# Script para ejecutar el pipeline de analisis de chats de WhatsApp para múltiples archivos.
# Uso: ./run_pipeline.sh <ruta_al_archivo_chat1.txt> [<ruta_al_archivo_chat2.txt> ...]

# Directorio para almacenar los resultados (archivos HTML finales)
OUTPUT_DIR="whatsapp_results2"
mkdir -p "$OUTPUT_DIR"

# Verifica que se hayan proporcionado archivos de entrada
if [ "$#" -eq 0 ]; then
    echo "Uso: $0 <ruta_al_archivo_chat1.txt> [<ruta_al_archivo_chat2.txt> ...]"
    exit 1
fi

# Itera sobre cada archivo de chat proporcionado como argumento
for chat_file in "$@"; do
    if [ ! -f "$chat_file" ]; then
        echo "Error: El archivo '$chat_file' no existe."
        continue
    fi

    echo "⚙️ Procesando chat: $chat_file"

    # Extrae el nombre base del archivo (sin extensión)
    base_name=$(basename -- "$chat_file")
    base_name="${base_name%.*}"

    # Define los nombres de los archivos intermedios y de salida
    preprocessed_csv="$OUTPUT_DIR/${base_name}_preprocessed.csv"
    stats_usuarios_csv="$OUTPUT_DIR/${base_name}_stats_usuarios.csv"
    mensajes_mensual_csv="$OUTPUT_DIR/${base_name}_mensajes_por_mes.csv"
    mensajes_por_hora_csv="$OUTPUT_DIR/${base_name}_mensajes_por_hora.csv"
    menciones_globales_csv="$OUTPUT_DIR/${base_name}_menciones_globales.csv"
    # --- NUEVOS ARCHIVOS INTERMEDIOS ---
    mensajes_por_dia_semana_csv="$OUTPUT_DIR/${base_name}_mensajes_por_dia_semana.csv"
    menciones_por_autor_csv="$OUTPUT_DIR/${base_name}_menciones_por_autor.csv"
    # -----------------------------------
    dashboard_html="$OUTPUT_DIR/${base_name}_dashboard.html"

    # 1. Preprocesamiento
    echo "  ➡️ Paso 1: Preprocesando '$chat_file' a '$preprocessed_csv'..."
    python3 prepocessing.py "$chat_file" "$preprocessed_csv"
    if [ $? -ne 0 ]; then
        echo "❌ Error en el preprocesamiento de '$chat_file'. Saltando al siguiente archivo."
        continue
    fi
    echo "  ✅ Preprocesamiento completado."

    # 2. Analisis
    echo "  ➡️ Paso 2: Analizando datos de '$preprocessed_csv'..."
    python3 analisis.py "$preprocessed_csv" \
        --out_usuarios "$stats_usuarios_csv" \
        --out_mensual "$mensajes_mensual_csv" \
        --out_horas "$mensajes_por_hora_csv" \
        --out_menciones_globales "$menciones_globales_csv" \
        --out_dia_semana "$mensajes_por_dia_semana_csv" \
        --out_menciones_por_autor "$menciones_por_autor_csv"
    if [ $? -ne 0 ]; then
        echo "❌ Error en el analisis de '$preprocessed_csv'. Saltando al siguiente archivo."
        continue
    fi
    echo "  ✅ Analisis completado."

    # 3. Generación de graficas
    echo "  ➡️ Paso 3: Generando dashboard en '$dashboard_html'..."
    python3 graficas.py \
        --usuarios "$stats_usuarios_csv" \
        --mensual "$mensajes_mensual_csv" \
        --horas "$mensajes_por_hora_csv" \
        --menciones_globales "$menciones_globales_csv" \
        --dia_semana "$mensajes_por_dia_semana_csv" \
        --menciones_por_autor "$menciones_por_autor_csv" \
        --salida "$dashboard_html"
    if [ $? -ne 0 ]; then
        echo "❌ Error al generar el dashboard para '$base_name'. Saltando al siguiente archivo."
        continue
    fi
    echo "  ✅ Dashboard generado."

    # 4. Limpieza: Eliminar archivos CSV intermedios
    echo "  🧹 Eliminando archivos intermedios..."
    rm -f "$preprocessed_csv" "$stats_usuarios_csv" "$mensajes_mensual_csv" "$mensajes_por_hora_csv" "$menciones_globales_csv" "$mensajes_por_dia_semana_csv" "$menciones_por_autor_csv"
    echo "  ✅ Archivos intermedios eliminados."
    echo "----------------------------------------------------"
done

echo "🎉 Pipeline completado para todos los archivos."
echo "Los dashboards finales se encuentran en el directorio '$OUTPUT_DIR'."