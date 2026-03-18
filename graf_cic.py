import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from adjustText import adjust_text

# Format y-axis labels for axc: show values in millions with a decimal comma (e.g. 1.2M -> 1,2M)
def millones_coma(x, pos):
    s = f"{x/1e6:,.1f}M"
    # swap thousand separator and decimal point: '1,234.5' -> '1.234,5'
    return s.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')

# Add generation date to first two plots
current_date = pd.Timestamp.now().strftime("%d/%m/%Y")
footnote_text = f"Inflación según INDEC (IPC). Se estima IPC constante para el último mes si no hay dato disponible.\nSerie reconstruida en base a actas paritarias de UPCN. Gráfico generado el {current_date}."


# Leer el archivo CSV
df = pd.read_csv("datos/cic.csv", parse_dates=["fecha"])

# Crear figura
fig, ax = plt.subplots(figsize=(3840/300, 2700/300), dpi=300)

# Definir períodos presidenciales
periodos = [
    ("Macri", "2015-12-01", "2019-11-30", "#fff3b0"),     # amarillo pálido
    ("Fernández", "2019-12-01", "2023-11-30", "#cce5ff"), # celeste pálido
    ("Milei", "2023-12-01", df["fecha"].max(), "#e6ccff") # violeta pálido
]

# Dibujar fondos de colores por período
for nombre, inicio, fin, color in periodos:
    ax.axvspan(pd.to_datetime(inicio), pd.to_datetime(fin), color=color, label=nombre)

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

# Formatear eje de fechas
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.YearLocator())
plt.xticks(rotation=45)
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

plt.figtext(0.5, 0.01, footnote_text,
            ha="center", fontsize=14, style='italic')

# Ajustar diseño y guardar
plt.tight_layout(rect=[0, 0.06, 1, 1])  # Increased bottom margin
plt.savefig("plots/grafico_salarios_CIC.png")
plt.close()


# =====================
# Gráfico Beca Doctoral CONICET (similar style to CIC)
# =====================

# Leer el archivo CSV de CONICET
df_con = pd.read_csv("datos/beca_conicet.csv", parse_dates=["fecha"]) 

# Crear figura
figc, axc = plt.subplots(figsize=(3840/300, 2700/300), dpi=300)

# Dibujar fondos de colores por período (reusa 'periodos')
for nombre, inicio, fin, color in periodos:
    axc.axvspan(pd.to_datetime(inicio), pd.to_datetime(fin), color=color, label=nombre)


# Dibujar línea con puntos
axc.plot(df_con["fecha"], df_con["salario_real"], color="black", linewidth=2,
         marker='o', markersize=3, label="Salario")

# Eje Y: dinámico según datos
min_m = df_con["salario_real"].min() / 1e6
max_m = df_con["salario_real"].max() / 1e6

step_m = 0.1   # 0.1 millones = 100k
ymin_axis_m = np.floor(min_m / step_m) * step_m
ymax_axis_m = np.ceil(max_m / step_m) * step_m

# asegurar que no sean iguales
if ymin_axis_m == ymax_axis_m:
    ymin_axis_m -= step_m
    ymax_axis_m += step_m

# aplicar en pesos
axc.set_ylim(ymin_axis_m * 1e6, ymax_axis_m * 1e6)
ticks_m = np.arange(ymin_axis_m, ymax_axis_m + 1e-9, step_m)
yticks_c = ticks_m * 1e6
axc.set_yticks(yticks_c)



axc.yaxis.set_major_formatter(plt.FuncFormatter(millones_coma))

# Líneas horizontales en cada tick
for y in yticks_c:
    axc.axhline(y=y, color='gray', linestyle='--', linewidth=0.5)

# Formatear eje de fechas
axc.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
axc.xaxis.set_major_locator(mdates.YearLocator())
plt.sca(axc)
plt.xticks(rotation=45)

# Get the last date from the data
last_date_c = df_con["fecha"].max()
last_date_str_c = f"{MONTH_NAMES[last_date_c.month]} de {last_date_c.year}"

# Update title with dynamic date reference
axc.set_title(f"Beca Doctoral CONICET\n(ajustado por inflación, en pesos de {last_date_str_c})", fontsize=28)
axc.set_xlabel("Fecha", fontsize=20)
axc.set_ylabel("Salario real (millones de pesos)", fontsize=20)
axc.legend(fontsize=20)

# Footnote specific to CONICET
footnote_con = f"Inflación según INDEC (IPC). Se estima IPC constante para el último mes si no hay dato disponible.\nSerie reconstruida en base a publicaciones periódicas de CONICET y actas paritarias de UPCN. Gráfico generado el {current_date}."
plt.figtext(0.5, 0.01, footnote_con,
            ha="center", fontsize=14, style='italic')

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
        footnote = f"Inflación según INDEC (IPC). Se estima IPC constante para el último mes si no hay dato disponible.\nSerie reconstruida en base a actas paritarias de UPCN. Gráfico generado el {current_date}"
    else:
        footnote = f"{footnote}. Gráfico generado el {current_date}."
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
    "Profesor Asistente Dedicación Exclusiva",
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
# Gráfico: Salario por hora Profasis (172 horas mensuales) - Serie histórica desde 2020
# =====================

# Leer datos profasis (desde 2020)
df_prof_crudo = pd.read_csv("datos/crudo_profasis.csv", parse_dates=["fecha"])

# Leer índice IPC para ajuste por inflación
df_ipc = pd.read_csv("datos/ipc_nuevo.csv", parse_dates=["fecha"])

# Calcular salario por hora usando 172 horas mensuales
HORAS_MENSUALES = 172
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
footnote_prof = f"Inflación según INDEC (IPC). Se estima IPC constante para el último mes si no hay dato disponible.\nSerie salarial reconstruida en base a recibos de sueldo de UNC y simulador de ADIUC.\nCorresponde a Profesor Asistente con 10 años de antigüedad.\nEl cálculo ya incluye el aumento del 6.85% anunciado por el gobierno de Milei el martes 17 de marzo. Gráfico generado el {current_date}"
plt.figtext(0.5, 0.01, footnote_prof, ha="center", fontsize=11, style='italic')

# Save plot
plt.tight_layout(rect=[0, 0.08, 1, 1])
plt.savefig("plots/grafico_salario_por_hora_profasis.png")
plt.close()




