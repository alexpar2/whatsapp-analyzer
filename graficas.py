import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import argparse
import ast # Para convertir la string de lista de palabras a lista
import re # Importar la librería de expresiones regulares
import calendar

def cargar_datos(usuarios_csv, mensual_csv, horas_csv, menciones_globales_csv, dia_semana_csv, menciones_por_autor_csv):
    """
    Carga los datos de los diferentes archivos CSV en DataFrames de pandas.

    Args:
        usuarios_csv (str): Ruta al CSV de estadísticas de usuarios.
        mensual_csv (str): Ruta al CSV de mensajes por mes.
        horas_csv (str): Ruta al CSV de mensajes por hora.
        menciones_globales_csv (str): Ruta al CSV de menciones globales.
        dia_semana_csv (str): Ruta al CSV de mensajes por día de la semana.
        menciones_por_autor_csv (str): Ruta al CSV de menciones por autor.

    Returns:
        tuple: Una tupla con los DataFrames cargados.
    """
    df_usuarios = pd.read_csv(usuarios_csv)
    df_mensual = pd.read_csv(mensual_csv)
    # Convierte las columnas de año y mes a un formato de fecha para la gráfica de línea.
    df_mensual["fecha"] = pd.to_datetime(dict(year=df_mensual["año"], month=df_mensual["mes"], day=1))
    
    df_horas = pd.read_csv(horas_csv)
    # Asegura que las horas estén ordenadas correctamente como una categoría.
    df_horas['hora'] = pd.Categorical(df_horas['hora'], categories=range(24), ordered=True)

    df_menciones_globales = pd.read_csv(menciones_globales_csv)

    df_dia_semana = pd.read_csv(dia_semana_csv)
    # Define el orden de los días de la semana para asegurar que se grafiquen correctamente.
    dias_orden = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    df_dia_semana['dia_semana'] = pd.Categorical(df_dia_semana['dia_semana'], categories=dias_orden, ordered=True)

    df_menciones_por_autor = pd.read_csv(menciones_por_autor_csv)

    return df_usuarios, df_mensual, df_horas, df_menciones_globales, df_dia_semana, df_menciones_por_autor

def grafica_pie_mensajes(df):
    """
    Genera un gráfico de pastel del porcentaje de mensajes por usuario.
    """
    fig = px.pie(df, names="nombre", values="num_mensajes", title="📊 Porcentaje de mensajes por usuario")
    return fig

def grafica_linea_mensajes_por_mes_agregado(df):
    """
    Genera un gráfico de líneas del total de mensajes por mes (suma de todos los usuarios).
    """
    # Agrupar por fecha sumando los mensajes de todos los usuarios
    df_agg = df.groupby('fecha', as_index=False).agg(num_mensajes=('num_mensajes', 'sum'))
    
    # Gráfico con una sola línea (sin distinción por usuario)
    fig = px.line(
        df_agg,
        x="fecha",
        y="num_mensajes",
        markers=True,
        title="📈 Total de mensajes por mes (todos los usuarios)",
        labels={
            "fecha": "Mes",
            "num_mensajes": "Número de mensajes (total)"
        }
    )
    return fig

def grafica_barras(df, columna, titulo, eje_x, eje_y):
    """
    Genera un gráfico de barras horizontal, ordenado de mayor a menor.

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        columna (str): Columna numérica para los valores de las barras.
        titulo (str): Título de la gráfica.
        eje_x (str): Etiqueta del eje X.
        eje_y (str): Etiqueta del eje Y.
    """
    # Ordenar el DataFrame de mayor a menor según la columna especificada
    df_sorted = df.sort_values(columna, ascending=False)
    fig = px.bar(
        df_sorted,
        x=columna, y="nombre",
        orientation='h', # Barras horizontales
        title=titulo,
        labels={columna: eje_x, "nombre": eje_y}
    )
    return fig



def grafica_longitud_promedio(df):
    """
    Genera un gráfico de barras de la longitud promedio de mensaje por usuario,
    con una línea para el promedio global. Las barras están ordenadas.
    """
    # Ordenar el DataFrame por la longitud promedio de mensaje de mayor a menor
    df_sorted = df.sort_values("media_longitud_mensaje", ascending=False)
    promedio_global = df_sorted["media_longitud_mensaje"].mean() # Calcular el promedio global después de ordenar
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_sorted["nombre"], # Usar el DataFrame ordenado
        y=df_sorted["media_longitud_mensaje"], # Usar el DataFrame ordenado
        name="Promedio por usuario",
        marker_color="indianred"
    ))
    fig.add_trace(go.Scatter(
        x=df_sorted["nombre"], # Usar el DataFrame ordenado para alinear la línea de promedio global
        y=[promedio_global] * len(df_sorted),
        mode="lines",
        name=f"Promedio global ({promedio_global:.2f})",
        line=dict(color="gray", dash="dash")
    ))
    fig.update_layout(
        title="📏 Longitud promedio de mensaje por usuario",
        yaxis_title="Longitud promedio de mensaje"
    )
    return fig

def grafica_emojis_por_mensaje(df):
    """
    Genera un gráfico de barras del promedio de emojis por mensaje, ordenado.
    """
    df["emojis_por_mensaje"] = df.apply(
        lambda row: row["num_emojis"] / row["num_mensajes"] if row["num_mensajes"] > 0 else 0,
        axis=1
    )
    # Ordenar y graficar horizontalmente
    df_sorted = df.sort_values("emojis_por_mensaje", ascending=False)
    fig = px.bar(df_sorted, x="emojis_por_mensaje", y="nombre", orientation='h',
                  title="🤪 Promedio de emojis por mensaje",
                  labels={"nombre": "Usuario", "emojis_por_mensaje": "Emojis por mensaje"})
    return fig

def grafica_top_hablante_mes(df):
    """
    Genera un gráfico de barras del usuario con más mensajes cada mes.
    """
    top_por_mes = df.loc[df.groupby("fecha")["num_mensajes"].idxmax()]
    fig = px.bar(top_por_mes, x="fecha", y="num_mensajes", color="usuario",
                  title="👑 Usuario con más mensajes cada mes")
    return fig


def grafica_enlaces_por_mensaje(df):
    """
    Genera un gráfico de barras del promedio de enlaces por mensaje, ordenado.
    """
    df["enlaces_por_mensaje"] = df.apply(
        lambda row: row["num_enlaces"] / row["num_mensajes"] if row["num_mensajes"] > 0 else 0,
        axis=1
    )
    # Ordenar y graficar horizontalmente
    df_sorted = df.sort_values("enlaces_por_mensaje", ascending=False)
    fig = px.bar(df_sorted, x="enlaces_por_mensaje", y="nombre", orientation='h',
                  title="🔗 Promedio de enlaces por mensaje",
                  labels={"nombre": "Usuario", "enlaces_por_mensaje": "Enlaces por mensaje"})
    return fig

def grafica_multimedia_por_mensaje(df):
    """
    Genera un gráfico de barras del promedio de elementos multimedia por mensaje, ordenado.
    """
    df["multimedia_por_mensaje"] = df.apply(
        lambda row: row["num_multimedia"] / row["num_mensajes"] if row["num_mensajes"] > 0 else 0,
        axis=1
    )
    # Ordenar y graficar horizontalmente
    df_sorted = df.sort_values("multimedia_por_mensaje", ascending=False)
    fig = px.bar(df_sorted, x="multimedia_por_mensaje", y="nombre", orientation='h',
                  title="🖼️ Promedio de elementos multimedia por mensaje",
                  labels={"nombre": "Usuario", "multimedia_por_mensaje": "Multimedia por mensaje"})
    return fig

def grafica_preguntas_por_mensaje(df):
    """
    Genera un gráfico de barras del promedio de preguntas por mensaje, ordenado.
    """
    df["preguntas_por_mensaje"] = df.apply(
        lambda row: row["num_preguntas"] / row["num_mensajes"] if row["num_mensajes"] > 0 else 0,
        axis=1
    )
    # Ordenar y graficar horizontalmente
    df_sorted = df.sort_values("preguntas_por_mensaje", ascending=False)
    fig = px.bar(df_sorted, x="preguntas_por_mensaje", y="nombre", orientation='h',
                 title="❓ Promedio de preguntas por mensaje",
                 labels={"nombre": "Usuario", "preguntas_por_mensaje": "Preguntas por mensaje"})
    return fig



def grafica_mensajes_por_dia_semana(df):
    """
    Gráfico de líneas de la actividad por día de la semana y usuario.
    """
    fig = px.line(df, x="dia_semana", y="num_mensajes", color="usuario", markers=True,
                  title="🗓️ Mensajes por día de la semana por usuario",
                  labels={"dia_semana": "Día de la semana", "num_mensajes": "Número de mensajes"})
    # Asegurarse de que los días estén ordenados en el eje X
    fig.update_xaxes(categoryorder='array', categoryarray=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
    return fig

def grafica_linea_mensajes_por_mes(df):
    """
    Genera un gráfico de líneas de mensajes por mes por usuario.
    """
    fig = px.line(df, x="fecha", y="num_mensajes", color="usuario", markers=True,
                  title="📈 Mensajes por mes por usuario")
    return fig

def grafica_linea_mensajes_por_hora(df):
    """
    Genera un gráfico de líneas de mensajes por hora del día por usuario.
    """
    fig = px.line(df, x="hora", y="num_mensajes", color="usuario", markers=True,
                  title="⏰ Mensajes por hora del día por usuario",
                  labels={"hora": "Hora del día (0-23)", "num_mensajes": "Número de mensajes"})
    # Asegura que todas las horas de 0 a 23 estén en el eje X.
    fig.update_xaxes(
        tickmode='array',
        tickvals=list(range(24)),
        title_text="Hora del día (0-23)"
    )
    return fig


def grafica_linea_mensajes_por_hora_normalizado(df_hora, df_usuario):
    """
    Genera un gráfico de líneas de mensajes por hora del día,
    normalizado por el total de mensajes de cada usuario.
    """
    # 1. Renombrar la columna de totales
    df_tot = df_usuario.rename(columns={'num_mensajes': 'total_mensajes'})

    # 2. Merge
    df = df_hora.merge(
        df_tot[['nombre', 'total_mensajes']],
        left_on='usuario',
        right_on='nombre',
        how='left'
    )

    # 3. Calcular ratio
    df['ratio'] = df['num_mensajes'] / df['total_mensajes']

    # 4. Gráfico
    fig = px.line(
        df,
        x="hora",
        y="ratio",
        color="usuario",
        markers=True,
        title="⏰ Proporción de mensajes por hora sobre el total por usuario",
        labels={
            "hora": "Hora del día (0-23)",
            "ratio": "Mensajes / Total mensajes"
        }
    )
    fig.update_xaxes(
        tickmode='array',
        tickvals=list(range(24)),
        title_text="Hora del día (0-23)"
    )
    fig.update_yaxes(tickformat=".0%")  # opcional: muestra el ratio en %
    return fig


def grafica_mensajes_por_dia_semana_normalizado(df_dia, df_usuario):
    """
    Genera un gráfico de líneas de la actividad por día de la semana,
    normalizado por el total de mensajes de cada usuario.
    """
    # 1. Renombrar la columna de totales
    df_tot = df_usuario.rename(columns={'num_mensajes': 'total_mensajes'})
    
    # 2. Merge con df_dia (tiene columnas dia_semana, usuario, num_mensajes)
    df = df_dia.merge(
        df_tot[['nombre', 'total_mensajes']],
        left_on='usuario',
        right_on='nombre',
        how='left'
    )
    
    # 3. Calcular ratio
    df['ratio'] = df['num_mensajes'] / df['total_mensajes']
    
    # 4. Gráfico
    fig = px.line(
        df,
        x="dia_semana",
        y="ratio",
        color="usuario",
        markers=True,
        title="🗓️ Proporción de mensajes por día de la semana por usuario",
        labels={
            "dia_semana": "Día de la semana",
            "ratio": "Mensajes / Total mensajes"
        }
    )
    # Ordenar los días de la semana
    fig.update_xaxes(
        categoryorder='array',
        categoryarray=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    )
    # Mostrar porcentajes
    fig.update_yaxes(tickformat=".0%")
    return fig


def grafica_linea_mensajes_por_mes_normalizado(df_mes, df_usuario):
    """
    Genera un gráfico de líneas de mensajes por mes,
    normalizado por el total de mensajes de cada usuario.
    
    df_mes debe tener al menos las columnas:
      - fecha (tipo datetime o string representando el mes)
      - usuario
      - num_mensajes
    """
    # 1. Renombrar la columna de totales
    df_tot = df_usuario.rename(columns={'num_mensajes': 'total_mensajes'})
    
    # 2. Merge con df_mes
    df = df_mes.merge(
        df_tot[['nombre', 'total_mensajes']],
        left_on='usuario',
        right_on='nombre',
        how='left'
    )
    
    # 3. Calcular ratio
    df['ratio'] = df['num_mensajes'] / df['total_mensajes']
    
    # 4. Gráfico
    fig = px.line(
        df,
        x="fecha",
        y="ratio",
        color="usuario",
        markers=True,
        title="📈 Proporción de mensajes por mes por usuario",
        labels={
            "fecha": "Mes",
            "ratio": "Mensajes / Total mensajes"
        }
    )
    # Opcional: formatear el eje Y como porcentaje
    fig.update_yaxes(tickformat=".0%")
    return fig


def grafica_linea_mensajes_por_mes_del_anyo_normalizado(df_mes, df_usuario):
    """
    Genera un gráfico de líneas de mensajes por mes del año (enero–diciembre),
    normalizado por el total de mensajes de cada usuario.
    
    Parámetros:
    - df_mes: DataFrame con al menos las columnas:
        * fecha: datetime (o string convertible) con fechas de los mensajes.
        * usuario: nombre del usuario.
        * num_mensajes: número de mensajes en esa fecha.
    - df_usuario: DataFrame con al menos las columnas:
        * nombre: nombre del usuario.
        * num_mensajes: total de mensajes del usuario.
    """
    # 1. Asegurar que 'fecha' es datetime y extraer mes numérico
    df = df_mes.copy()
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['mes'] = df['fecha'].dt.month
    
    # 2. Sumar los mensajes por usuario y mes
    df_agg = (
        df
        .groupby(['usuario', 'mes'], as_index=False)
        .agg(num_mensajes_mes=('num_mensajes', 'sum'))
    )
    
    # 3. Renombrar totales y merge
    df_tot = df_usuario.rename(columns={'num_mensajes': 'total_mensajes'})
    df_merged = df_agg.merge(
        df_tot[['nombre', 'total_mensajes']],
        left_on='usuario',
        right_on='nombre',
        how='left'
    )
    
    # 4. Calcular ratio
    df_merged['ratio'] = df_merged['num_mensajes_mes'] / df_merged['total_mensajes']
    
    # 5. Traducir mes numérico a nombre (opcional)
    df_merged['mes_nombre'] = df_merged['mes'].apply(lambda m: calendar.month_name[m].capitalize())
    
    # 6. Orden de meses
    orden = [calendar.month_name[i].capitalize() for i in range(1, 13)]
    
    # 7. Gráfico
    fig = px.line(
        df_merged,
        x="mes_nombre",
        y="ratio",
        color="usuario",
        markers=True,
        title="📊 Proporción de mensajes por mes del año por usuario",
        labels={
            "mes_nombre": "Mes",
            "ratio": "Mensajes / Total mensajes"
        }
    )
    fig.update_xaxes(categoryorder='array', categoryarray=orden)
    fig.update_yaxes(tickformat=".0%")
    return fig







def grafica_heatmap_menciones(df_menciones_por_autor, df_usuarios):
    """
    Heatmap de la frecuencia de menciones entre usuarios normalizada por mensajes del autor.
    Requiere:
    - df_menciones_por_autor: DataFrame con columnas 'autor_mencionador', 'usuario_mencionado', 'conteo'
    - df_usuarios: DataFrame con columnas 'nombre' y 'num_mensajes'
    """
    if df_menciones_por_autor.empty:
        fig = go.Figure().update_layout(title="👥 Frecuencia de Menciones entre Usuarios (No hay menciones registradas)")
        return fig

    # Combinar con los datos de total de mensajes por autor
    df_merged = df_menciones_por_autor.merge(
        df_usuarios[['nombre', 'num_mensajes']],
        left_on='autor_mencionador',
        right_on='nombre',
        how='left'
    ).fillna(0)  # Rellenar NaN con 0 si no hay coincidencia

    # Calcular menciones normalizadas por mensaje del autor
    df_merged['menciones_por_mensaje'] = df_merged.apply(
        lambda row: row['conteo'] / row['num_mensajes'] if row['num_mensajes'] > 0 else 0,
        axis=1
    )

    # Pivotar para obtener la matriz de menciones normalizadas
    mention_matrix = df_merged.pivot_table(
        index='autor_mencionador',
        columns='usuario_mencionado',
        values='menciones_por_mensaje'
    ).fillna(0)  # Rellenar NaN con 0 donde no hay menciones

    fig = px.imshow(
        mention_matrix,
        labels=dict(x="Usuario Mencionado", y="Autor Mencionador", color="Menciones por mensaje"),
        x=mention_matrix.columns.tolist(),
        y=mention_matrix.index.tolist(),
        title="👥 Frecuencia de Menciones por Mensaje del Autor (Heatmap)",
        color_continuous_scale="Viridis"
    )
    
    fig.update_xaxes(side="top")
    fig.update_layout(
        autosize=True,
        height=max(500, len(mention_matrix.index) * 50),
        width=max(700, len(mention_matrix.columns) * 50),
    )
    return fig

# --- FUNCIONES PARA GENERAR HTML DE DATOS TEXTUALES (sin cambios aquí) ---
def generar_html_palabras_mas_usadas(df_usuarios):
    html = "<h2>📝 Palabras más usadas por usuario (Top 10)</h2>"
    html += "<div style='display: flex; flex-wrap: wrap; justify-content: center;'>"
    for index, row in df_usuarios.iterrows():
        nombre = row['nombre']
        palabras = ast.literal_eval(row['palabras_mas_usadas'])
        
        if palabras:
            html += f"<div style='margin: 10px; padding: 15px; border: 1px solid #ddd; border-radius: 8px; width: 300px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);'>"
            html += f"<h3>{nombre}</h3>"
            html += "<ol>"
            for palabra, count in palabras:
                html += f"<li>{palabra} ({count})</li>"
            html += "</ol>"
            html += "</div>"
        else:
            html += f"<div style='margin: 10px; padding: 15px; border: 1px solid #ddd; border-radius: 8px; width: 300px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);'>"
            html += f"<h3>{nombre}</h3>"
            html += "<p>No hay datos de palabras.</p>"
            html += "</div>"
    html += "</div>"
    return html

def generar_html_menciones_por_persona(df_usuarios):
    html = "<h2>🗣️ Personas más mencionadas por cada usuario</h2>"
    html += "<div style='display: flex; flex-wrap: wrap; justify-content: center;'>"
    for index, row in df_usuarios.iterrows():
        nombre = row['nombre']
        menciones_str = row['menciones_hechas']
        
        if menciones_str:
            html += f"<div style='margin: 10px; padding: 15px; border: 1px solid #ddd; border-radius: 8px; width: 300px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);'>"
            html += f"<h3>{nombre} menciona a:</h3>"
            html += f"<p>{menciones_str}</p>"
            html += "</div>"
        else:
            html += f"<div style='margin: 10px; padding: 15px; border: 1px solid #ddd; border-radius: 8px; width: 300px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);'>"
            html += f"<h3>{nombre}</h3>"
            html += "<p>No menciona a otras personas.</p>"
            html += "</div>"
    html += "</div>"
    return html

def generar_html_persona_mas_mencionada_total(df_menciones_globales):
    html = "<h2>👑 La persona más mencionada en el chat</h2>"
    if not df_menciones_globales.empty:
        top_mencion = df_menciones_globales.iloc[0]
        usuario = top_mencion['usuario_mencionado']
        conteo = top_mencion['conteo']
        html += f"<p style='font-size: 1.2em; font-weight: bold;'>{usuario} con {conteo} menciones.</p>"
        
        if len(df_menciones_globales) > 1:
            html += "<h3>Otras personas mencionadas:</h3>"
            html += "<ul>"
            for index, row in df_menciones_globales.iloc[1:].iterrows():
                html += f"<li>{row['usuario_mencionado']} ({row['conteo']} menciones)</li>"
            html += "</ul>"
    else:
        html += "<p>No hay datos de menciones globales.</p>"
    return html

def guardar_dashboard(figs, html_sections, output_path):
    """
    Guarda las figuras de Plotly y las secciones HTML en un archivo HTML de dashboard.

    Args:
        figs (list): Lista de objetos Figure de Plotly.
        html_sections (list): Lista de cadenas HTML personalizadas.
        output_path (str): Ruta donde se guardará el archivo HTML.
    """
    from plotly.offline import plot

    html_parts = []
    # Genera el HTML para cada figura de Plotly
    for i, fig in enumerate(figs):
        # include_plotlyjs se establece en True solo para la primera figura
        # para evitar duplicar la librería Plotly JS, lo que puede causar problemas de rendimiento.
        inner_html = plot(fig, include_plotlyjs=(i == 0), output_type="div")
        html_parts.append(inner_html)

    # Une las secciones HTML personalizadas.
    custom_html_content = "".join(html_sections)

    full_html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard de WhatsApp</title>
        <style>
            body {{ font-family: 'Inter', sans-serif; margin: 20px; background-color: #f4f7f6; color: #333; }}
            h1, h2, h3 {{ color: #2c3e50; text-align: center; margin-bottom: 25px; }}
            .plotly-graph-div {{ margin-bottom: 40px; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
            div h3 {{ margin-top: 5px; margin-bottom: 10px; color: #555; }}
            ol, ul {{ margin-left: 20px; padding-left: 0; list-style-position: inside; }}
            li {{ margin-bottom: 5px; line-height: 1.5; }}
            .graph-container {{
                display: flex;
                flex-direction: column; /* Apila las gráficas verticalmente */
                align-items: center; /* Centra las gráficas */
                margin-bottom: 20px;
            }}
            .graph-item {{
                width: 95%; /* Ocupa casi todo el ancho disponible */
                max-width: 1200px; /* Ancho máximo para gráficas muy grandes */
                margin: 20px 0; /* Espacio vertical entre gráficas */
                border: 1px solid #e0e0e0;
                box-shadow: 0 0 10px rgba(0,0,0,0.05);
                border-radius: 12px;
                overflow: hidden;
                background-color: #ffffff;
            }}
            /* Estilos para las secciones de texto */
            .text-section {{
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                padding: 25px;
                margin: 30px auto;
                max-width: 1200px;
                text-align: center;
            }}
            .text-section h2 {{
                margin-top: 0;
                margin-bottom: 20px;
                color: #2c3e50;
            }}
            .text-section div {{
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 20px; /* Espacio entre los bloques de texto */
            }}
            .text-section .user-block {{
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 15px;
                box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
                width: 300px;
                text-align: left;
            }}
            .text-section .user-block h3 {{
                color: #34495e;
                font-size: 1.1em;
                margin-bottom: 10px;
            }}
            .text-section .user-block ul {{
                margin-left: 0;
                padding-left: 15px;
            }}
            .text-section p {{
                font-size: 1.1em;
            }}
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    </head>
    <body>
        <h1>📱 Dashboard de estadísticas de WhatsApp</h1>
        <div class="graph-container">
            {''.join([f'<div class="graph-item">{part}</div>' for part in html_parts])}
        </div>
        <div class="text-section">
            {custom_html_content}
        </div>
    </body>
    </html>
    """

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)

def main():
    """
    Función principal para cargar datos, generar gráficas y guardar el dashboard.
    """
    parser = argparse.ArgumentParser(description="Genera un dashboard de estadísticas de WhatsApp.")
    parser.add_argument("--usuarios", default="stats_usuarios.csv", help="Archivo CSV con estadísticas de usuarios.")
    parser.add_argument("--mensual", default="mensajes_por_mes.csv", help="Archivo CSV con mensajes por mes.")
    parser.add_argument("--horas", default="mensajes_por_hora.csv", help="Archivo CSV con estadísticas por hora y usuario.")
    parser.add_argument("--menciones_globales", default="menciones_globales.csv", help="Archivo CSV con estadísticas de menciones globales.")
    parser.add_argument("--dia_semana", default="mensajes_por_dia_semana.csv", help="Archivo CSV con estadísticas por día de la semana y usuario.")
    parser.add_argument("--menciones_por_autor", default="menciones_por_autor.csv", help="Archivo CSV de menciones detalladas por autor para heatmap.")
    parser.add_argument("--salida", default="dashboard_whatsapp.html", help="Nombre del archivo HTML de salida para el dashboard.")
    args = parser.parse_args()

    # Cargar todos los DataFrames necesarios
    usuarios_df, mensual_df, horas_df, menciones_globales_df, dia_semana_df, menciones_por_autor_df = cargar_datos(
        args.usuarios, args.mensual, args.horas, args.menciones_globales, args.dia_semana, args.menciones_por_autor
    )

    # Lista de figuras de Plotly a incluir en el dashboard
    figs = [
        grafica_pie_mensajes(usuarios_df),
        grafica_barras(usuarios_df, "num_mensajes", "💬 Total de mensajes por usuario", "Mensajes", "Usuario"),
        grafica_longitud_promedio(usuarios_df),
        grafica_emojis_por_mensaje(usuarios_df), # Se ha modificado para ordenar y ser horizontal
        grafica_enlaces_por_mensaje(usuarios_df), # Se ha modificado para ordenar y ser horizontal
        grafica_multimedia_por_mensaje(usuarios_df), # Se ha modificado para ordenar y ser horizontal
        grafica_preguntas_por_mensaje(usuarios_df), # Se ha modificado para ordenar y ser horizontal

        grafica_linea_mensajes_por_mes_agregado(mensual_df),
        grafica_linea_mensajes_por_mes(mensual_df),
        grafica_linea_mensajes_por_mes_normalizado(mensual_df, usuarios_df),
        grafica_linea_mensajes_por_mes_del_anyo_normalizado(mensual_df, usuarios_df), # Gráfico de líneas por mes del año, normalizado
        grafica_mensajes_por_dia_semana(dia_semana_df),
        grafica_mensajes_por_dia_semana_normalizado(dia_semana_df, usuarios_df), 
        grafica_linea_mensajes_por_hora(horas_df),
        grafica_linea_mensajes_por_hora_normalizado(horas_df, usuarios_df),
        grafica_top_hablante_mes(mensual_df), # Este no se ordena por los valores y es un gráfico de barras
        grafica_heatmap_menciones(menciones_por_autor_df, usuarios_df) # Heatmap, no aplica ordenación de la misma manera
    ]

    # Lista de secciones HTML personalizadas
    html_sections = []
    html_sections.append(generar_html_palabras_mas_usadas(usuarios_df))
    html_sections.append(generar_html_menciones_por_persona(usuarios_df))
    html_sections.append(generar_html_persona_mas_mencionada_total(menciones_globales_df))

    # Guardar el dashboard final
    guardar_dashboard(figs, html_sections, args.salida)
    print(f"✅ Dashboard generado en: {args.salida}")

if __name__ == "__main__":
    main()
