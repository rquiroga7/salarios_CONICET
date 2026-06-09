import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from adjustText import adjust_text

# Format y-axis labels for per-hour plots: show integer values with dot as thousands separator
def miles_formatter_dot(x, pos):
    try:
        return f"{int(x):,}".replace(',', '.')
    except Exception:
        return f"{x}"


# Format y-axis labels for axc: show values in millions with a decimal comma (e.g. 1.2M -> 1,2M)
def millones_coma(x, pos):
    s = f"{x/1e6:,.1f}M"
    # swap thousand separator and decimal point: '1,234.5' -> '1.234,5'
    return s.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')

# Add generation date to first two plots
current_date = pd.Timestamp.now().strftime("%d/%m/%Y")
_AUTHOR = "Por Rodrigo Quiroga. Ver github.com/rquiroga7/salarios_CONICET"
footnote_text = (
    f"Inflación según INDEC (IPC). Se estima IPC constante para el último mes si no hay dato disponible.\n"
    f"Serie reconstruida en base a actas paritarias de UPCN. Gráfico generado el {current_date}.\n{_AUTHOR}"
)


# Leer el archivo CSV
df = pd.read_csv("datos/cic.csv", parse_dates=["fecha"])

# Crear figura
fig, ax = plt.subplots(figsize=(3840/300, 2700/300), dpi=300)

# Definir períodos presidenciales
periodos = [
    ("Menem", "1989-07-01", "1999-11-30", "#d9d9d9"),            # gris
    ("De la Rúa", "1999-12-01", "2001-12-20", "#ffccdf"),      # rosa
    ("Duhalde", "2002-01-02", "2003-05-24", "#d6f5d6"),        # verde claro
    ("Néstor Kirchner", "2003-05-25", "2007-12-09", "#d9eefc"),# celeste claro
    ("Cristina Fernández", "2007-12-10", "2015-12-09", "#bfe6ff"), # celeste
    ("Macri", "2015-12-10", "2019-12-09", "#fff3b0"),         # amarillo pálido
    ("Fernández", "2019-12-10", "2023-11-30", "#cce5ff"),     # celeste pálido
    ("Milei", "2023-12-01", df["fecha"].max(), "#e6ccff")     # violeta pálido
]

# Dibujar fondos de colores por período
# Para el gráfico CIC (serie iniciando en 2015) sólo mostrar presidencias
# que se solapen con 2015 en adelante
periodos_cic = [p for p in periodos if pd.to_datetime(p[2]) >= pd.to_datetime("2015-01-01")]
for nombre, inicio, fin, color in periodos_cic:
    # Exclude Cristina Fernández from the CIC legend (still draw the span)
    label_name = '_nolegend_' if 'Cristina' in nombre else nombre
    ax.axvspan(pd.to_datetime(inicio), pd.to_datetime(fin), color=color, label=label_name)

# Dibujar línea con puntos
ax.plot(df["fecha"], df["salario_real"], color="black", linewidth=2,
        marker='o', markersize=3, label="Salario")

# Eje Y: límites y ticks basados en los datos
min_value = df["salario_real"].min()
max_value = df["salario_real"].max()
ylim_min = np.floor(0.95 * min_value / 100000) * 100000
ylim_max = np.ceil(1.05 * max_value / 100000) * 100000

ax.set_ylim(ylim_min, ylim_max)
yticks = np.arange(ylim_min, ylim_max + 100000, 100000)
ax.set_yticks(yticks)

ax.yaxis.set_major_formatter(plt.FuncFormatter(millones_coma))

# Líneas horizontales en cada tick
for y in yticks:
    ax.axhline(y=y, color='gray', linestyle='--', linewidth=0.5)

# Mirror y-axis labels on the right side for CIC
ax_right = ax.twinx()
ax_right.set_ylim(ylim_min, ylim_max)
ax_right.set_yticks(yticks)
ax_right.yaxis.set_major_formatter(plt.FuncFormatter(millones_coma))
# Copy font properties from left y-tick labels so size and font match exactly
left_labels = ax.yaxis.get_ticklabels()
if len(left_labels) > 0:
    left_fp = left_labels[0].get_fontproperties()
    for lbl in ax_right.yaxis.get_ticklabels():
        lbl.set_fontproperties(left_fp)
else:
    ax_right.tick_params(axis='y', labelsize=20)

# Formatear eje de fechas
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
# Explicit January ticks for CIC so year labels align with January data points
start_year = 2016
end_year = 2026
ticks = [pd.to_datetime(f"{y}-01-01") for y in range(start_year, end_year+1)]
ax.set_xticks(ticks)
ax.tick_params(axis='x', rotation=45)
for lbl in ax.get_xticklabels():
    lbl.set_ha('right')
# Force CIC x-axis start at January 2016 and limit to July 2026
ax.set_xlim(left=pd.to_datetime("2016-01-01"), right=pd.to_datetime("2026-07-01"))
# Get the last date from the data
MONTH_NAMES = {
    1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
    5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
    9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
}
last_date = df["fecha"].max()
last_date_str = f"{MONTH_NAMES[last_date.month]} de {last_date.year}"

# Update title with dynamic date reference
ax.set_title(f"Salario de bolsillo ajustado por IPC\nInvestigador asistente (pesos de {last_date_str})", fontsize=28)
ax.set_xlabel("Fecha", fontsize=20)
ax.set_ylabel("Salario real (millones)", fontsize=20)
ax.legend(fontsize=20)

plt.figtext(0.98, 0.01, footnote_text,
            ha="right", fontsize=14, style='italic')

# Ajustar diseño y guardar
plt.tight_layout(rect=[0, 0.06, 1, 1])  # Increased bottom margin
plt.savefig("plots/grafico_salarios_CIC.png")
plt.close()


# =====================
# Gráfico Beca Doctoral CONICET (format/style matched to grafico_salarios_CIC.png)
# =====================

# Leer el archivo CSV de CONICET
df_con = pd.read_csv("datos/beca_conicet.csv", parse_dates=["fecha"]) 

# Crear figura
figc, axc = plt.subplots(figsize=(3840/300, 2700/300), dpi=300)

# Dibujar fondos de colores por período (usar same selection as CIC: desde 2015 en adelante)
for nombre, inicio, fin, color in periodos_cic:
    # Exclude Cristina Fernández from the legend (same behavior as CIC)
    label_name = '_nolegend_' if 'Cristina' in nombre else nombre
    axc.axvspan(pd.to_datetime(inicio), pd.to_datetime(fin), color=color, alpha=0.6, label=label_name)


# Dibujar línea con puntos
axc.plot(df_con["fecha"], df_con["salario_real"], color="black", linewidth=2,
         marker='o', markersize=3, label="Beca Doctoral")

# Eje Y: igual que CIC (ticks cada 100k, formatter millones_coma)
min_value_c = df_con["salario_real"].min()
max_value_c = df_con["salario_real"].max()
ylim_min_c = np.floor(0.95 * min_value_c / 100000) * 100000
ylim_max_c = np.ceil(1.05 * max_value_c / 100000) * 100000
axc.set_ylim(ylim_min_c, ylim_max_c)
yticks_c = np.arange(ylim_min_c, ylim_max_c + 100000, 100000)
axc.set_yticks(yticks_c)
axc.yaxis.set_major_formatter(plt.FuncFormatter(millones_coma))

# Líneas horizontales en cada tick
for y in yticks_c:
    axc.axhline(y=y, color='gray', linestyle='--', linewidth=0.5)

# Mirror y-axis labels on the right side (copy font properties)
axc_right = axc.twinx()
axc_right.set_ylim(ylim_min_c, ylim_max_c)
axc_right.set_yticks(yticks_c)
axc_right.yaxis.set_major_formatter(plt.FuncFormatter(millones_coma))
left_labels_c = axc.yaxis.get_ticklabels()
if len(left_labels_c) > 0:
    left_fp_c = left_labels_c[0].get_fontproperties()
    for lbl in axc_right.yaxis.get_ticklabels():
        lbl.set_fontproperties(left_fp_c)
else:
    axc_right.tick_params(axis='y', labelsize=20)

# Formatear eje de fechas (same styling as CIC)
axc.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
start_year_c = max(2016, df_con['fecha'].min().year)
end_year_c = max(df_con['fecha'].max().year, 2026)
ticks_c_years = [pd.to_datetime(f"{y}-01-01") for y in range(start_year_c, end_year_c+1)]
axc.set_xticks(ticks_c_years)
axc.tick_params(axis='x', rotation=45)
for lbl in axc.get_xticklabels():
    lbl.set_ha('right')

# Set x-limits similar to CIC (but anchored to data range if earlier)
axc.set_xlim(left=pd.to_datetime("2016-01-01"), right=pd.to_datetime("2026-07-01"))

# Update title with dynamic date reference
last_date_c = df_con["fecha"].max()
last_date_str_c = f"{MONTH_NAMES[last_date_c.month]} de {last_date_c.year}"
axc.set_title(f"Beca Doctoral CONICET\n(ajustado por inflación, en pesos de {last_date_str_c})", fontsize=28)
axc.set_xlabel("Fecha", fontsize=20)
axc.set_ylabel("Salario real (millones)", fontsize=20)
axc.legend(fontsize=20)

# Footnote specific to CONICET (centered like other plots)
footnote_con = (
    f"Inflación según INDEC (IPC). Se estima IPC constante para el último mes si no hay dato disponible.\n"
    f"Serie reconstruida en base a publicaciones periódicas de CONICET y actas paritarias de UPCN. Gráfico generado el {current_date}.\n{_AUTHOR}"
)
plt.figtext(0.5, 0.01, footnote_con, ha="center", fontsize=14, style='italic')

# Ajustar diseño y guardar
plt.tight_layout(rect=[0, 0.06, 1, 1])
plt.savefig("plots/grafico_beca_doctoral.png")
plt.close()




# =====================
# Segundo gráfico: índice base 100 en 2015-12-01
# =====================

# Calcular índice base 100
base_fecha = pd.to_datetime("2015-12-01")
base_valor = df.loc[df["fecha"] == base_fecha, "salario_real"].values
if base_valor.size == 0:
    raise ValueError("No se encontró la fecha base 2015-12-01 en los datos.")
base_valor = base_valor[0]
df["indice_base_100"] = df["salario_real"] / base_valor * 100

# Crear figura para el gráfico con base 100
fig2, ax2 = plt.subplots(figsize=(3840/300, 2700/300), dpi=300)

# Fondos presidenciales
for nombre, inicio, fin, color in periodos:
    ax2.axvspan(pd.to_datetime(inicio), pd.to_datetime(fin), color=color, label=nombre)

# Serie índice
ax2.plot(df["fecha"], df["indice_base_100"], color="black", linewidth=2,
         marker='o', markersize=3, label="Salario real")

# Líneas horizontales
yticks2 = np.arange(50, 110, 10)
ax2.set_yticks(yticks2)
for y in yticks2:
    ax2.axhline(y=y, color='gray', linestyle='--', linewidth=0.5)

# Ejes
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax2.xaxis.set_major_locator(mdates.YearLocator())
ax2.set_title("Salario de bolsillo ajustado por inflación\nBase 100 = diciembre de 2015", fontsize=28)
ax2.set_xlabel("Fecha", fontsize=20)
ax2.set_ylabel("Salario (base 100)", fontsize=20)
ax2.legend(fontsize=18)
plt.xticks(rotation=45)

# Comentario
plt.figtext(0.5, 0.01, footnote_text,
            ha="center", fontsize=14, style='italic')


# Guardar
plt.tight_layout(rect=[0, 0.06, 1, 1])  # Increased bottom margin from 0.03 to 0.06
plt.savefig("plots/grafico_indice_base_100.png")
plt.close()



##### GRAFICO SALARIO NOMINAL VERSUS AJUSTADO #####
def plot_nominal_vs_adjusted(csv_file, title_prefix,subtitle, output_filename, footnote=None):
    """
    Create a comparative plot of nominal vs adjusted salaries
    
    Parameters:
    -----------
    csv_file : str
        Path to CSV file containing 'fecha', 'nominal' and 'ajustado' columns
    title_prefix : str
        Text to prepend to the standard title format
    output_filename : str
        Name of the output PNG file
    footnote : str, optional
        Custom footnote text (defaults to standard UPCN text if None)
    """
    # Read data
    df = pd.read_csv(csv_file, parse_dates=["fecha"])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(3840/300, 2700/300), dpi=300)
    
    # Plot series
    ax.plot(df["fecha"], df["nominal"], color="blue", linewidth=4, 
            marker='o', markersize=6, label="Salario de bolsillo", zorder=2.7)
    ax.plot(df["fecha"], df["ajustado"], color="red", linewidth=4,
            marker='o', markersize=6, label="Salario ajustado por inflación", zorder=2.6)
    
    # Define point properties for labels
    points = [
        (df["fecha"].iloc[0], df["nominal"].iloc[0], 'blue', 25, 2),      # First nominal
        (df["fecha"].iloc[-1], df["nominal"].iloc[-1], 'blue', -5, 15),    # Last nominal
        (df["fecha"].iloc[-1], df["ajustado"].iloc[-1], 'red', -5, 15)     # Last adjusted
    ]
    
    # Create text labels with boxes
    texts = []
    for date, value, color, dx, dy in points:
        bbox_props = dict(
            boxstyle='round,pad=0.5',
            fc='white',
            ec=color,
            alpha=1,
            zorder=3
        )
        
        annotation = ax.annotate(
            f'${value:,.0f}',
            xy=(date, value),           # Point to annotate (arrow end)
            xycoords='data',            # Use data coordinates for point
            xytext=(dx, dy),      # Offset for label position
            textcoords='offset points', # Use offset points for label
            color=color,
            fontsize=13,
            fontweight='bold',
            bbox=bbox_props,
            horizontalalignment='right' if dx < 0 else 'left',
            verticalalignment='bottom' if dy > 0 else 'top',
            arrowprops=dict(
                arrowstyle='->',
                connectionstyle='arc3,rad=0',
                color=color,
                shrinkB=4,
                lw=2,
                zorder=2.5
            ),
            zorder=3
        )
        texts.append(annotation)

    # Y axis setup
    min_value = min(df["nominal"].min(), df["ajustado"].min())
    max_value = max(df["nominal"].max(), df["ajustado"].max())
    ylim_min = np.floor(0.9 * min_value / 100000) * 100000
    ylim_max = np.ceil(1.09 * max_value / 100000) * 100000
    
    ax.set_ylim(ylim_min, ylim_max)
    yticks = np.arange(ylim_min+100000, ylim_max, 100000)
    ax.set_yticks(yticks)
    
    # Add horizontal grid lines
    for y in yticks:
        ax.axhline(y=y, color='gray', linestyle='--', linewidth=0.5)
    
    # Secondary Y axis
    ax2 = ax.twinx()
    ax2.set_ylim(ylim_min, ylim_max)
    ax2.set_yticks(yticks)
    
    # Custom formatter for y-axis labels
    def millones_formatter(x, p):
        return f"{x/1000000:,.1f}M".replace(".", ",")
    
    ax.yaxis.set_major_formatter(plt.FuncFormatter(millones_formatter))
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(millones_formatter))
    


    # X axis formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.tick_params(axis='x', rotation=90, labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    ax2.tick_params(axis='y', labelsize=12)
    
    # Labels and title
    full_title = f"{title_prefix}\n{subtitle}"
    ax.set_title(full_title, fontsize=28)
    ax.set_xlabel("Fecha", fontsize=20)
    ax.set_ylabel("Salario", fontsize=20)
    ax2.set_ylabel("Salario", fontsize=20)
    ax.legend(fontsize=20, loc='upper left')
    
    # Footnote
    # Footnote with generation date
    if footnote is None:
        footnote = (
            f"Inflación según INDEC (IPC). Se estima IPC constante para el último mes si no hay dato disponible.\n"
            f"Serie reconstruida en base a actas paritarias de UPCN. Gráfico generado el {current_date}.\n{_AUTHOR}"
        )
    else:
        footnote = f"{footnote}. Gráfico generado el {current_date}.\n{_AUTHOR}"
    plt.figtext(0.5, 0.01, footnote, ha="center", fontsize=14, style='italic')
    
    # Save plot
    plt.tight_layout(rect=[0, 0.06, 1, 1])  # Increased bottom margin
    #Add "plots/" to output_filename
    output_filename = "plots/" + output_filename
    plt.savefig(output_filename)
    plt.close()

# Usage examples:
plot_nominal_vs_adjusted(
    "datos/cic_ajustado.csv",
    "Salario de bolsillo vs Ajustado por inflación",
    "Investigador asistente",
    "grafico_nominal_vs_ajustado_cic.png",
    "Inflación según INDEC (IPC). Se estima IPC constante para el último mes si no hay dato disponible.\nSerie salarial reconstruida en base a actas paritarias de UPCN"
)

plot_nominal_vs_adjusted(
    "datos/beca_conicet_ajustado.csv",
    "Salario de bolsillo vs Ajustado por inflación",
    "Beca Doctoral CONICET",
    "grafico_nominal_vs_ajustado_beca_conicet.png",
    "Inflación según INDEC (IPC). Se estima IPC constante para el último mes si no hay dato disponible.\nSerie salarial reconstruida en base a recibos de sueldo de CONICET"
)

plot_nominal_vs_adjusted(
    "datos/foncyt_ajustado.csv",
    "Salario de bolsillo vs Ajustado por inflación",
    "Beca Doctoral FONCyT",
    "grafico_nominal_vs_ajustado_foncyt.png",
    "Inflación según INDEC (IPC). Se estima IPC constante para el último mes si no hay dato disponible.\nSerie salarial reconstruida en base a recibos de sueldo de FONCyT"
)

plot_nominal_vs_adjusted(
    "datos/profasis_ajustado.csv",
    "Salario de bolsillo vs Ajustado por inflación",
    "Profesor Asistente (JTP) - Dedicación Exclusiva",
    "grafico_nominal_vs_ajustado_profasis.png",
    "Inflación según INDEC (IPC). Se estima IPC constante para el último mes si no hay dato disponible.\nSerie salarial reconstruida en base a recibos de sueldo de UNC"
)

plot_nominal_vs_adjusted(
    "datos/art9_ajustado.csv",
    "Salario de bolsillo vs Ajustado por inflación",
    "Art. 9 - Personal contratado CONICET",
    "grafico_nominal_vs_ajustado_art9.png",
    "Inflación según INDEC (IPC). Se estima IPC constante para el último mes si no hay dato disponible.\nSerie salarial reconstruida en base a recibos de sueldo de UNC"
)

plot_nominal_vs_adjusted(
    "datos/resgarrahan_ajustado.csv",
    "Salario de bolsillo vs Ajustado por inflación",
    "Salario para residentes de 1er año del Hospital Garrahan",
    "grafico_nominal_vs_ajustado_resgarrahan.png",
    "Inflación según INDEC (IPC). Se incluye el bono incluído en el decreto 527/2025.\nSe estima IPC constante para el último mes si no hay dato disponible.\nSerie salarial estimada a partir de actas paritarias de ATE"
)


# =====================
# Gráfico: Salario por hora Profasis (176 horas mensuales) - Serie histórica desde 2020
# =====================

# Leer datos profasis (desde 2020)
df_prof_crudo = pd.read_csv("datos/crudo_profasis.csv", parse_dates=["fecha"])

# Leer índice IPC para ajuste por inflación
df_ipc = pd.read_csv("datos/ipc_nuevo.csv", parse_dates=["fecha"])

# Calcular salario por hora usando 176 horas mensuales
HORAS_MENSUALES = 176
df_prof_crudo["salario_hora"] = df_prof_crudo["salario"] / HORAS_MENSUALES

# Fusionar con IPC para ajuste
df_prof_hora = df_prof_crudo.merge(df_ipc, on="fecha", how="left")

# Obtener el último índice IPC disponible
ultimo_indice = df_ipc["indice"].iloc[-1]
ultima_fecha = df_ipc["fecha"].iloc[-1]

# Ajustar salario por hora a pesos de la última fecha
# Fórmula: salario_ajustado = salario_nominal * (indice_ultimo / indice_mes)
df_prof_hora["salario_hora_ajustado"] = df_prof_hora["salario_hora"] * (ultimo_indice / df_prof_hora["indice"])

# Crear figura
fig_prof_hora, ax_prof_hora = plt.subplots(figsize=(3840/300, 2700/300), dpi=300)

# Dibujar fondos de colores por período (Macri sin leyenda, otros con nombres modificados)
ax_prof_hora.axvspan(pd.to_datetime("2015-12-01"), pd.to_datetime("2019-11-30"), color="#fff3b0")  # Macri sin leyenda
ax_prof_hora.axvspan(pd.to_datetime("2019-12-01"), pd.to_datetime("2023-11-30"), color="#cce5ff", label="Presidencia Fernández")  # Fernández
ax_prof_hora.axvspan(pd.to_datetime("2023-12-01"), df_prof_hora["fecha"].max(), color="#e6ccff", label="Presidencia Milei")  # Milei

# Plot única serie: salario por hora ajustado por inflación (curva negra)
ax_prof_hora.plot(df_prof_hora["fecha"], df_prof_hora["salario_hora_ajustado"], color="black", linewidth=4,
                  marker='o', markersize=4, label="Salario por hora", zorder=2.7)

# Encontrar el punto de Noviembre 2023 (cambio de fuente de datos)
nov_2023 = pd.to_datetime("2023-11-01")
nov_2023_idx = df_prof_hora[df_prof_hora["fecha"] == nov_2023].index
if len(nov_2023_idx) > 0:
    nov_2023_idx = nov_2023_idx[0]
    nov_2023_value = df_prof_hora.loc[nov_2023_idx, "salario_hora_ajustado"]
else:
    # Si no encuentra exacto, buscar el más cercano
    nov_2023_idx = (df_prof_hora["fecha"] - nov_2023).abs().argmin()
    nov_2023_value = df_prof_hora.iloc[nov_2023_idx]["salario_hora_ajustado"]
    nov_2023_date = df_prof_hora.iloc[nov_2023_idx]["fecha"]

# Línea horizontal punteada gris oscura desde nov-2023 hasta el final
last_date = df_prof_hora["fecha"].max()
ax_prof_hora.hlines(y=nov_2023_value, xmin=nov_2023, xmax=last_date, 
                    colors='#404040', linestyles='dotted', linewidth=2, 
                    label='Ley de Financiamiento Universitario', zorder=2.6)

# Texto sobre la línea punteada (movido más a la derecha y más cerca de la línea)
ax_prof_hora.text(pd.to_datetime("2025-01-01"), nov_2023_value * 1.01, 
                  "Ley de Financiamiento Universitario", 
                  color='#404040', fontsize=13, fontweight='bold', 
                  ha='center', va='bottom', zorder=2.8)

# Etiqueta al final de la línea punteada (con borde gris oscuro, alineada a la derecha)
ax_prof_hora.annotate(f'${nov_2023_value:.0f}', 
                      xy=(last_date, nov_2023_value),
                      xytext=(5, 0),
                      textcoords='offset points',
                      color='#404040',
                      fontsize=13,
                      fontweight='bold',
                      bbox=dict(
                          boxstyle='round,pad=0.5',
                          fc='white',
                          ec='#404040',
                          alpha=1,
                          zorder=3
                      ),
                      ha='left',
                      va='center',
                      arrowprops=dict(
                          arrowstyle='->',
                          connectionstyle='arc3,rad=0',
                          color='#404040',
                          shrinkB=4,
                          lw=2,
                          zorder=2.5
                      ),
                      zorder=3)

# Flecha vertical desde el último punto negro hasta la línea punteada (ROJA, más gruesa)
last_value = df_prof_hora["salario_hora_ajustado"].iloc[-1]
ax_prof_hora.annotate('', 
                      xy=(last_date, nov_2023_value),
                      xytext=(last_date, last_value),
                      arrowprops=dict(
                          arrowstyle='->',
                          color='red',
                          lw=3,
                          zorder=2.8
                      ))

# Calcular porcentaje de aumento necesario
pct_increase = ((nov_2023_value - last_value) / last_value) * 100

# Texto del porcentaje a la derecha de la flecha (ROJO, font size grande, bold)
mid_y = (last_value + nov_2023_value) / 2
ax_prof_hora.text(last_date, mid_y, 
                  f'+{pct_increase:.0f}%', 
                  color='red', 
                  fontsize=18, 
                  fontweight='bold',
                  ha='left', 
                  va='center', 
                  zorder=2.9)

# Definir puntos para etiquetas (último, nov-2023) - removido el primero
points_prof = [
    (df_prof_hora["fecha"].iloc[-1], df_prof_hora["salario_hora_ajustado"].iloc[-1], 'black', 5, 15),   # Last (moved to right)
    (df_prof_hora["fecha"].iloc[nov_2023_idx], df_prof_hora["salario_hora_ajustado"].iloc[nov_2023_idx], 'black', 5, -20),  # Nov 2023
]

# Crear etiquetas de texto con cajas
texts_prof = []
for i, (date, value, color, dx, dy) in enumerate(points_prof):
    bbox_props = dict(
        boxstyle='round,pad=0.5',
        fc='white',
        ec=color,
        alpha=1,
        zorder=3
    )

    # Etiqueta especial para Nov 2023 (indice 1)
    if i == 1:
        label_text = f'nov-2023\n${value:.0f}'
    else:
        label_text = f'${value:.0f}'

    annotation = ax_prof_hora.annotate(
        label_text,
        xy=(date, value),
        xycoords='data',
        xytext=(dx, dy),
        textcoords='offset points',
        color=color,
        fontsize=13,
        fontweight='bold',
        bbox=bbox_props,
        horizontalalignment='right' if dx < 0 else 'left',
        verticalalignment='bottom' if dy > 0 else 'top',
        arrowprops=dict(
            arrowstyle='->',
            connectionstyle='arc3,rad=0',
            color=color,
            shrinkB=4,
            lw=2,
            zorder=2.5
        ),
        zorder=3
    )
    texts_prof.append(annotation)

# Y axis setup
min_value_h = df_prof_hora["salario_hora_ajustado"].min()
max_value_h = df_prof_hora["salario_hora_ajustado"].max()
ylim_min_h = np.floor(0.9 * min_value_h / 1000) * 1000
ylim_max_h = np.ceil(1.09 * max_value_h / 1000) * 1000

ax_prof_hora.set_ylim(ylim_min_h, ylim_max_h)
yticks_h = np.arange(ylim_min_h + 1000, ylim_max_h, 1000)
ax_prof_hora.set_yticks(yticks_h)

# X-axis: start from first data point
first_date = df_prof_hora["fecha"].min()
ax_prof_hora.set_xlim(left=first_date)

# Add horizontal grid lines
for y in yticks_h:
    ax_prof_hora.axhline(y=y, color='gray', linestyle='--', linewidth=0.5)

# Custom formatter for y-axis labels (show values in thousands with dot as decimal separator, 0 decimals)
def miles_formatter(x, p):
    return f"{x/1000:.0f}".replace(",", ".")

ax_prof_hora.yaxis.set_major_formatter(plt.FuncFormatter(miles_formatter))

# X axis formatting
ax_prof_hora.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax_prof_hora.xaxis.set_major_locator(mdates.YearLocator())
ax_prof_hora.tick_params(axis='x', rotation=45, labelsize=12)
ax_prof_hora.tick_params(axis='y', labelsize=12)

# Get last date for title
last_date_prof = df_prof_hora["fecha"].max()
last_date_str_prof = f"{MONTH_NAMES[last_date_prof.month]} de {last_date_prof.year}"

# Labels and title
ax_prof_hora.set_title(f"Salario por hora Profesor Universitario\nSalario real de bolsillo (en pesos de {last_date_str_prof})", fontsize=28)
ax_prof_hora.set_xlabel("Fecha", fontsize=20)
ax_prof_hora.set_ylabel("Salario por hora (miles de pesos)", fontsize=16)
ax_prof_hora.legend(fontsize=20, loc='lower left')

# Footnote
footnote_prof = f"Inflación según INDEC (IPC). Se estima IPC constante para el último mes si no hay dato disponible.\nSerie salarial reconstruida en base a recibos de sueldo de UNC y simulador de ADIUC.\nCorresponde a un cargo de Profesor Asistente (JTP) con 10 años de antigüedad. Por Rodrigo Quiroga, ver github.com/rquiroga7/salarios_CONICET\nEl cálculo ya incluye el aumento del 6.85% anunciado por el gobierno de Milei el martes 17 de marzo. Gráfico generado el {current_date}"
plt.figtext(0.5, 0.01, footnote_prof, ha="center", fontsize=11, style='italic')

# Save plot
try:
    plt.tight_layout(rect=[0, 0.08, 1, 1])
    plt.savefig("plots/grafico_salario_por_hora_profasis.png")
except Exception:
    pass
plt.close()



# =====================
# Gráficos: Proyección histórica Profasis a pesos actuales (y por hora)
# =====================

# Leer datos nominales recientes
df_prof_nominal = pd.read_csv("datos/crudo_profasis.csv", parse_dates=["fecha"]) 

# Leer serie índice base 100 (ya ajustada por inflación)
df_prof_index = pd.read_csv("datos/profasis_base100.csv", header=None,
                            names=["fecha", "indice"], parse_dates=["fecha"],
                            skipinitialspace=True)

# Determinar fecha y salario nominal más reciente
last_nominal_date = df_prof_nominal["fecha"].max()
last_nominal_value = df_prof_nominal.loc[df_prof_nominal["fecha"] == last_nominal_date, "salario"].values
if last_nominal_value.size == 0:
    # fallback to last available nominal
    last_nominal_value = df_prof_nominal["salario"].iloc[-1]
else:
    last_nominal_value = last_nominal_value[0]

# Obtener el último índice disponible y asegurar que el salario nominal usado
# corresponde a la misma fecha del índice (si el índice no llega hasta el
# último nominal, elegir el nominal más cercano al último índice disponible).
last_index_date = df_prof_index["fecha"].max()
last_index_value = df_prof_index.loc[df_prof_index["fecha"] == last_index_date, "indice"].values[0]
if last_nominal_date != last_index_date:
    # intentar usar el salario nominal en la fecha del último índice
    nominal_on_index = df_prof_nominal.loc[df_prof_nominal["fecha"] == last_index_date, "salario"]
    if nominal_on_index.size > 0:
        last_nominal_value = nominal_on_index.values[0]
        last_nominal_date = last_index_date
    else:
        # usar el nominal más cercano en el tiempo al último índice
        idx_near = (df_prof_nominal["fecha"] - last_index_date).abs().argmin()
        last_nominal_value = df_prof_nominal.iloc[idx_near]["salario"]
        last_nominal_date = df_prof_nominal.iloc[idx_near]["fecha"]

# Calcular proyección de la serie histórica en pesos de la última fecha
# Paso 1: ajustar crudo_profasis por IPC para obtener salarios "reales" (pesos de la última fecha IPC)
df_ipc = pd.read_csv("datos/ipc_nuevo.csv", parse_dates=["fecha"])

# Extender IPC si falta algún mes (como hace actualiza_datos_IPC.py)
last_nominal_date_ext = df_prof_nominal['fecha'].max()
while df_ipc["fecha"].max() < last_nominal_date_ext:
    next_date = df_ipc["fecha"].max() + pd.DateOffset(months=1)
    projected = df_ipc["indice"].iloc[-1] * (df_ipc["indice"].iloc[-1] / df_ipc["indice"].iloc[-2])
    df_ipc = pd.concat([df_ipc, pd.DataFrame({"fecha": [next_date], "indice": [projected]})], ignore_index=True)

ultimo_indice_ipc = df_ipc["indice"].iloc[-1]

# Fusionar IPC con crudo nominal
df_prof_nominal = df_prof_nominal.merge(df_ipc, on='fecha', how='left')
df_prof_nominal['salario_real_ipc'] = df_prof_nominal['salario'] * (ultimo_indice_ipc / df_prof_nominal['indice'])

# Paso 2: extendemos la serie base100 hasta el último mes nominal disponible
last_nominal_date = df_prof_nominal['fecha'].max()
nominal_last_value = df_prof_nominal.loc[df_prof_nominal['fecha'] == last_nominal_date, 'salario'].values[0]

# referencia: valor base100 en su última fecha
base_last_date = df_prof_index['fecha'].max()
base_last_value = df_prof_index.loc[df_prof_index['fecha'] == base_last_date, 'indice'].values[0]

# referencia para escala temporal: usar salario real de referencia en 2026-01-01 (o nearest)
ref_date = pd.to_datetime('2026-01-01')
if ref_date not in df_prof_nominal['fecha'].values:
    # choose nearest previous
    ref_date = df_prof_nominal.loc[df_prof_nominal['fecha'] <= ref_date, 'fecha'].max()
ref_real = df_prof_nominal.loc[df_prof_nominal['fecha'] == ref_date, 'salario_real_ipc'].values[0]

# crear rango mensual desde primer mes del base100 hasta último nominal
full_dates = pd.date_range(start=df_prof_index['fecha'].min(), end=last_nominal_date, freq='MS')
df_index_full = pd.DataFrame({'fecha': full_dates})

# incorporar índice original donde exista
df_index_full = df_index_full.merge(df_prof_index, on='fecha', how='left')

# incorporar salario_real_ipc por fecha si existe (no traer la columna nominal 'salario')
df_index_full = df_index_full.merge(df_prof_nominal[['fecha','salario_real_ipc']], on='fecha', how='left')

# Calcular indice_ext: para fechas posteriores al último base100, usar
# indice_ext[month] = salario_real_ipc[month] / ref_real * base_last_value
idx_ext = []
for _, row in df_index_full.iterrows():
    d = row['fecha']
    if pd.notna(row.get('indice')):
        idx_ext.append(row['indice'])
    else:
        if pd.notna(row.get('salario_real_ipc')):
            val = row['salario_real_ipc'] / ref_real * base_last_value
            idx_ext.append(val)
        else:
            idx_ext.append(np.nan)

df_index_full['indice_ext'] = idx_ext
df_index_full['indice_ext'] = df_index_full['indice_ext'].ffill()

# Paso 3: escalar indice_ext para que su valor en last_nominal_date corresponda
# al último salario nominal disponible
if last_nominal_date in df_index_full['fecha'].values:
    idx_at_last = df_index_full.loc[df_index_full['fecha'] == last_nominal_date, 'indice_ext'].values[0]
else:
    idx_at_last = df_index_full['indice_ext'].iloc[-1]

df_index_full['salario_pesos_actuales'] = df_index_full['indice_ext'] / idx_at_last * nominal_last_value

# Guardar CSV de depuración con sólo las columnas solicitadas
df_index_full[['fecha','indice','indice_ext','salario_real_ipc','salario_pesos_actuales']].to_csv('plots/profasis_plotted_series.csv', index=False)

# preparar df_prof_index para graficar (usar fecha y salario_pesos_actuales como serie)
df_prof_index = df_index_full[['fecha','salario_pesos_actuales']].copy()

# --- Plot: Profasis proyectado en pesos actuales ---
fig_p, ax_p = plt.subplots(figsize=(3840/300, 2700/300), dpi=300)

# Fondos presidenciales
for nombre, inicio, fin, color in periodos:
    ax_p.axvspan(pd.to_datetime(inicio), pd.to_datetime(fin), color=color, label=nombre)

ax_p.plot(df_prof_index["fecha"], df_prof_index["salario_pesos_actuales"], color="black", linewidth=3,
          marker='o', markersize=3, label="Salario real de bolsillo")

# Eje Y dinámico
min_v = df_prof_index["salario_pesos_actuales"].min()
max_v = df_prof_index["salario_pesos_actuales"].max()
ylim_min = np.floor(0.95 * min_v / 100000) * 100000
ylim_max = np.ceil(1.05 * max_v / 100000) * 100000
ax_p.set_ylim(ylim_min, ylim_max)
yticks_p = np.arange(ylim_min, ylim_max + 100000, 100000)
ax_p.set_yticks(yticks_p)
ax_p.yaxis.set_major_formatter(plt.FuncFormatter(millones_coma))
for y in yticks_p:
    ax_p.axhline(y=y, color='gray', linestyle='--', linewidth=0.5)

# Eje X
ax_p.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
# Use MonthLocator at January so year labels align with January data points
ax_p.xaxis.set_major_locator(mdates.MonthLocator(bymonth=1))
# Ensure xtick labels rotate and right-align
plt.sca(ax_p)
ax_p.tick_params(axis='x', rotation=45)
for lbl in ax_p.get_xticklabels():
    lbl.set_ha('right')
# Force x-axis start at January 1999 and limit to July 2026
ax_p.set_xlim(left=pd.to_datetime("1999-01-01"), right=pd.to_datetime("2026-07-01"))

last_date_p = df_prof_index["fecha"].max()
last_date_str_p = f"{MONTH_NAMES[last_date_p.month]} de {last_date_p.year}"

ax_p.set_title(f"Salario docente universitario de bolsillo ajustado por IPC\nProfesor Asistente (JTP) dedicación exclusiva ( en pesos de {last_date_str_p})", fontsize=24)
ax_p.set_xlabel("Fecha", fontsize=18)
ax_p.set_ylabel("Salario real (millones)", fontsize=18)
ax_p.legend(loc='upper left', fontsize=14)

plt.figtext(0.98, 0.01, f"Salario de un profesor asistente (JTP) con 10 años de antigüedad. Salario nominal de {last_nominal_date.strftime('%Y-%m-%d')} = ${int(nominal_last_value):,}.\nGráfico generado el {current_date}. Por Rodrigo Quiroga. Ver github.com/rquiroga7/salarios_CONICET.\nDatos históricos (pre-2020) cortesía de Matías Sanchez, AGD-UBA.",
            ha="right", fontsize=12, style='italic')

plt.tight_layout(rect=[0, 0.06, 1, 1])
plt.savefig("plots/grafico_salarios_profasis.png")
plt.close()


# --- Plot: Profasis proyectado por hora (dividir por 176) ---
HORAS_MENSUALES = 176
df_prof_index["salario_por_hora_actual"] = df_prof_index["salario_pesos_actuales"] / HORAS_MENSUALES

fig_h, ax_h = plt.subplots(figsize=(3840/300, 2700/300), dpi=300)
for nombre, inicio, fin, color in periodos:
    ax_h.axvspan(pd.to_datetime(inicio), pd.to_datetime(fin), color=color, label=nombre)

ax_h.plot(df_prof_index["fecha"], df_prof_index["salario_por_hora_actual"], color="black", linewidth=3,
          marker='o', markersize=3, label="Salario por hora")

# Y axis for per-hour: fixed range 6000-15000 with breaks every 1000
yticks_h2 = np.arange(6000, 16000, 1000)
ax_h.set_yticks(yticks_h2)

def formatter_horas(x, pos):
    return f"{int(x)}"

ax_h.yaxis.set_major_formatter(plt.FuncFormatter(formatter_horas))
for y in yticks_h2:
    ax_h.axhline(y=y, color='gray', linestyle='--', linewidth=0.5)

ax_h.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
# Use MonthLocator at January so year labels align with January data points
ax_h.xaxis.set_major_locator(mdates.MonthLocator(bymonth=1))
# Ensure xtick labels rotate and right-align
plt.sca(ax_h)
ax_h.tick_params(axis='x', rotation=45)
for lbl in ax_h.get_xticklabels():
    lbl.set_ha('right')
# Force x-axis start at January 1999 and limit to July 2026
ax_h.set_xlim(left=pd.to_datetime("1999-01-01"), right=pd.to_datetime("2026-07-01"))

ax_h.set_title(f"Salario de bolsillo ajustado por IPC\nProfesor Asistente (JTP) — por hora (pesos de {last_date_str_p})", fontsize=26)
ax_h.set_xlabel("Fecha", fontsize=18)
ax_h.set_ylabel("Pesos por hora", fontsize=18)
ax_h.legend(loc='upper left', fontsize=14)

plt.figtext(0.98, 0.01, f"Salario de un profesor asistente (JTP) con 10 años de antigüedad. Salario nominal de {last_nominal_date.strftime('%Y-%m-%d')} = ${int(nominal_last_value):,} y dividiendo por {HORAS_MENSUALES} horas/mes.\nGráfico generado el {current_date}. Por Rodrigo Quiroga. Ver github.com/rquiroga7/salarios_CONICET.\nDatos históricos (pre-2020) cortesía de Matías Sanchez, AGD-UBA.",
            ha="right", fontsize=12, style='italic')

plt.tight_layout(rect=[0, 0.06, 1, 1])
plt.savefig("plots/grafico_salarios_profasis_porhora.png")
plt.close()


# =====================
# Gráfico alternativo: proyección por hora con aumentos discretos
# Misma pendiente descendente (sep-2024 a mar-2026) + 21% en jun-26 y 3% en oct-26
# =====================

# Fit linear trend on Sep-2024 to Mar-2026
trend_start = pd.to_datetime("2024-09-01")
trend_end = pd.to_datetime("2026-03-01")
mask_trend = (df_prof_index["fecha"] >= trend_start) & (df_prof_index["fecha"] <= trend_end)
recent_trend = df_prof_index.loc[mask_trend].copy()
x_trend = mdates.date2num(recent_trend["fecha"]).astype(float)
y_trend = recent_trend["salario_por_hora_actual"].values.astype(float)
coeff_trend = np.polyfit(x_trend, y_trend, 1)
trend_fn = np.poly1d(coeff_trend)

# Projection range: from last observed date to Nov 2027
last_date_trend = df_prof_index["fecha"].max()
proj_end_trend = pd.to_datetime("2027-11-01")
months_after_trend = pd.date_range(
    start=(last_date_trend + pd.offsets.MonthBegin(1)).normalize(),
    end=proj_end_trend, freq='MS'
)
proj_dates_trend = pd.DatetimeIndex([last_date_trend]).append(months_after_trend)

# Compute trend values offset so trend starts at last actual value
trend_vals_trend = trend_fn(mdates.date2num(proj_dates_trend))
delta_trend = df_prof_index["salario_por_hora_actual"].iloc[-1] - trend_vals_trend[0]
proj_y_trend = trend_vals_trend + delta_trend

# Apply discrete bumps (additive to preserve slope): +21% in Jun-2026, +3% in Oct-2026
proj_y_bumped = proj_y_trend.copy()
jun_2026 = pd.to_datetime("2026-06-01")
oct_2026 = pd.to_datetime("2026-10-01")
jun_idx = (proj_dates_trend == jun_2026).nonzero()[0][0]
oct_idx = (proj_dates_trend == oct_2026).nonzero()[0][0]
bump_jun = proj_y_trend[jun_idx] * 0.21
bump_oct = proj_y_trend[oct_idx] * 0.03
proj_y_bumped[jun_idx:] += bump_jun
proj_y_bumped[oct_idx:] += bump_oct

# Third projection: Ley de Financiamiento Universitario
# June 2026 value = Nov 2023 real salary, same downward slope, only from Jun-2026 onward
nov_2023_val = df_prof_index.loc[df_prof_index["fecha"] == pd.to_datetime("2023-11-01"),
                                 "salario_por_hora_actual"].values[0]
slope = coeff_trend[0]  # daily slope from polyfit
jun_2026_num = mdates.date2num(jun_2026)
# LFY only from June 2026 onward
mask_lfy = proj_dates_trend >= jun_2026
proj_dates_lfy = proj_dates_trend[mask_lfy]
proj_y_lfy = np.array([
    nov_2023_val + slope * (mdates.date2num(d) - jun_2026_num)
    for d in proj_dates_lfy
])

# Create the alternative projection plot
fig_alt, ax_alt = plt.subplots(figsize=(3840/300, 2400/300), dpi=300)

# Extend Milei background to 2027-12
periodos_proy = [
    p if p[0] != "Milei" else ("Milei", "2023-12-01", "2027-12-01", "#e6ccff")
    for p in periodos
]
for nombre, inicio, fin, color in periodos_proy:
    ax_alt.axvspan(pd.to_datetime(inicio), pd.to_datetime(fin), color=color, alpha=0.6, zorder=0, label=nombre)

# Observed series
ax_alt.plot(df_prof_index["fecha"], df_prof_index["salario_por_hora_actual"], color="black", linewidth=3,
            marker='o', markersize=3, label="Salario por hora", zorder=3)

# Raw trend (no bumps) in gray dotted
ax_alt.plot(proj_dates_trend, proj_y_trend, color='gray', linestyle=':', linewidth=2,
            label='Tendencia lineal sin aumentos', zorder=2.5)

# Bumped projection (+21% jun, +3% oct) in solid gray
ax_alt.plot(proj_dates_trend, proj_y_bumped, color='green', linestyle='-', linewidth=2,
            label='Aumento ofrecido (+21% jun, +3% oct)', zorder=2.7)

# Ley de Financiamiento Universitario in blue solid (from Jun-2026 onward)
ax_alt.plot(proj_dates_lfy, proj_y_lfy, color='blue', linestyle='-', linewidth=2,
            label='Ley de Financiamiento Universitario', zorder=2.6)
# Connect last observed dot to first LFY dot (Jun-2026)
last_obs_y = df_prof_index["salario_por_hora_actual"].iloc[-1]
ax_alt.plot([proj_dates_trend[0], proj_dates_lfy[0]],
            [last_obs_y, proj_y_lfy[0]], color='blue', linestyle='-', linewidth=2, zorder=2.6)

# Y axis
all_vals_alt = np.concatenate([df_prof_index["salario_por_hora_actual"].values, proj_y_bumped, proj_y_lfy])
ymin_alt = np.nanmin(all_vals_alt)
ymax_alt = np.nanmax(all_vals_alt)
ylim_min_alt = 0
ylim_max_alt = np.ceil(1.05 * ymax_alt / 1000) * 1000
if ylim_max_alt <= 0:
    ylim_max_alt = 1000
ax_alt.set_ylim(ylim_min_alt, ylim_max_alt)
yticks_alt = np.arange(ylim_min_alt, ylim_max_alt + 1, 1000)
ax_alt.set_yticks(yticks_alt)
ax_alt.yaxis.set_major_formatter(plt.FuncFormatter(miles_formatter_dot))
for y in yticks_alt:
    ax_alt.axhline(y=y, color='gray', linestyle='--', linewidth=0.5)

# Mirror y-axis right
ax_alt_right = ax_alt.twinx()
ax_alt_right.set_ylim(ylim_min_alt, ylim_max_alt)
ax_alt_right.set_yticks(yticks_alt)
ax_alt_right.yaxis.set_major_formatter(plt.FuncFormatter(miles_formatter_dot))
ax_alt_right.tick_params(axis='y', labelsize=10)

# X axis
ax_alt.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax_alt.xaxis.set_major_locator(mdates.MonthLocator(bymonth=1))
plt.sca(ax_alt)
ax_alt.tick_params(axis='x', rotation=45)
for lbl in ax_alt.get_xticklabels():
    lbl.set_ha('right')
ax_alt.set_xlim(left=pd.to_datetime("1999-01-01"), right=pd.to_datetime("2028-01-01") + pd.offsets.MonthEnd(0))

ax_alt.set_title(f"Salario por hora — Escenario con aumentos paritarios\nProfesor Asistente (JTP) (pesos de {last_date_str_p})", fontsize=20)
ax_alt.set_xlabel("Fecha", fontsize=14)
ax_alt.set_ylabel("Pesos por hora", fontsize=14)
ax_alt.legend(loc='lower left', fontsize=10)

plt.figtext(0.98, 0.01, f"Salario de un profesor asistente (JTP) con 10 años de antigüedad. Salario nominal de {last_nominal_date.strftime('%Y-%m-%d')} = ${int(nominal_last_value):,} y dividiendo por {HORAS_MENSUALES} horas/mes.\nSe realizan tres proyecciones, lineal sin aumentos (punteada), aumentos ofrecidos (en verde, +21% jun y +3% oct), Ley de Financiamiento Universitario (azul).\nGráfico generado el {current_date}. Por Rodrigo Quiroga. Ver github.com/rquiroga7/salarios_CONICET.",
            ha="right", fontsize=11, style='italic')

plt.tight_layout(rect=[0, 0.09, 1, 1])
plt.savefig("plots/proy2.png")
plt.close()

print("Saved: plots/proy2.png")

# --- proy3: same as proy2 but x-axis restricted to 2015-01 to 2027-12 ---
fig_alt3, ax_alt3 = plt.subplots(figsize=(3840/300, 2880/300), dpi=300)

# Only show Macri, Fernández, Milei in legend for proy3
legend_proy3 = {"Macri", "Cristina Fernández", "Fernández", "Milei"}
for nombre, inicio, fin, color in periodos_proy:
    lbl = nombre if nombre in legend_proy3 else '_nolegend_'
    ax_alt3.axvspan(pd.to_datetime(inicio), pd.to_datetime(fin), color=color, alpha=0.6, zorder=0, label=lbl)

ax_alt3.plot(df_prof_index["fecha"], df_prof_index["salario_por_hora_actual"], color="black", linewidth=3,
             marker='o', markersize=3, label="Salario por hora", zorder=3)

ax_alt3.plot(proj_dates_trend, proj_y_trend, color='gray', linestyle=':', linewidth=2,
             label='Tendencia lineal sin aumentos', zorder=2.5)

ax_alt3.plot(proj_dates_trend, proj_y_bumped, color='green', linestyle='-', linewidth=2,
             label='Aumento ofrecido (+21% jun, +3% oct)', zorder=2.7)

ax_alt3.plot(proj_dates_lfy, proj_y_lfy, color='blue', linestyle='-', linewidth=2,
             label='Ley de Financiamiento Universitario', zorder=2.6)
# Connect last observed dot to first LFY dot (Jun-2026)
ax_alt3.plot([proj_dates_trend[0], proj_dates_lfy[0]],
             [last_obs_y, proj_y_lfy[0]], color='blue', linestyle='-', linewidth=2, zorder=2.6)

ax_alt3.set_ylim(4000, 15000)
yticks_alt3 = np.arange(4000, 16000, 1000)
ax_alt3.set_yticks(yticks_alt3)
ax_alt3.yaxis.set_major_formatter(plt.FuncFormatter(miles_formatter_dot))
ax_alt3.tick_params(axis='y', labelsize=14)
for y in yticks_alt3:
    ax_alt3.axhline(y=y, color='gray', linestyle='--', linewidth=0.5)

ax_alt3_right = ax_alt3.twinx()
ax_alt3_right.set_ylim(4000, 15000)
ax_alt3_right.set_yticks(yticks_alt3)
ax_alt3_right.yaxis.set_major_formatter(plt.FuncFormatter(miles_formatter_dot))
ax_alt3_right.tick_params(axis='y', labelsize=14)

ax_alt3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax_alt3.xaxis.set_major_locator(mdates.MonthLocator(bymonth=1))
plt.sca(ax_alt3)
ax_alt3.tick_params(axis='x', rotation=45, labelsize=14)
for lbl in ax_alt3.get_xticklabels():
    lbl.set_ha('right')
ax_alt3.set_xlim(left=pd.to_datetime("2015-01-01"), right=pd.to_datetime("2027-12-01") + pd.offsets.MonthEnd(0))

ax_alt3.set_title(f"Salario por hora — Escenario con aumentos paritarios\nProfesor Asistente (JTP) (pesos de {last_date_str_p})", fontsize=26)
ax_alt3.set_xlabel("Fecha", fontsize=18)
ax_alt3.set_ylabel("Pesos por hora", fontsize=18)
ax_alt3.legend(loc='lower left', fontsize=14)

plt.figtext(0.98, 0.01, f"Salario de un profesor asistente (JTP) con 10 años de antigüedad. Salario nominal de {last_nominal_date.strftime('%Y-%m-%d')} = ${int(nominal_last_value):,} y dividiendo por {HORAS_MENSUALES} horas/mes.\nSe realizan tres proyecciones, lineal sin aumentos (punteada), aumentos ofrecidos (en verde, +21% jun y +3% oct), Ley de Financiamiento Universitario (azul).\nGráfico generado el {current_date}. Por Rodrigo Quiroga. Ver github.com/rquiroga7/salarios_CONICET.",
            ha="right", fontsize=13, style='italic')

plt.tight_layout(rect=[0, 0.09, 1, 1])
plt.savefig("plots/proy3.png")
plt.close()

print("Saved: plots/proy3.png")



