import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime


def miles_formatter_dot(x, pos):
    try:
        return f"{int(x):,}".replace(',', '.')
    except Exception:
        return f"{x}"


def millones_coma(x, pos):
    s = f"{x/1e6:,.1f}M"
    return s.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')


def main():
    infile = "plots/profasis_plotted_series.csv"
    outpng = "plots/grafico_salarios_profasis_porhora_proy.png"

    df = pd.read_csv(infile, parse_dates=["fecha"]) 
    df = df.sort_values("fecha")
    df["salario_por_hora_actual"] = df["salario_real_ipc"] / 176
    df = df.dropna(subset=["salario_por_hora_actual"])

    # Fit a linear trend on the most recent 36 months (or all if fewer)
    n_months = 36
    recent = df.tail(min(n_months, len(df)))
    x = mdates.date2num(recent["fecha"]).astype(float)
    y = recent["salario_por_hora_actual"].values.astype(float)
    coeff = np.polyfit(x, y, 1)
    trend = np.poly1d(coeff)

    # Projection range: start from the last observed point and project monthly up to Nov 2027
    last_date = df["fecha"].max()
    last_actual = df["salario_por_hora_actual"].iloc[-1]
    proj_end = pd.to_datetime("2027-11-01")

    # Build projection dates: include the last actual date as the first projected point,
    # then monthly points after that up to proj_end
    months_after = pd.date_range(start=(last_date + pd.offsets.MonthBegin(1)).normalize(),
                                 end=proj_end, freq='MS')
    if len(months_after) == 0:
        proj_dates = pd.DatetimeIndex([last_date])
    else:
        proj_dates = pd.DatetimeIndex([last_date]).append(months_after)

    # Compute trend values and align the trend so it starts at the last actual value
    trend_vals = trend(mdates.date2num(proj_dates))
    # offset so trend at last_date equals the observed last_actual
    delta = last_actual - trend_vals[0]
    proj_y = trend_vals + delta

    # Presidential periods (background shades)
    periodos = [
        ("Menem", "1989-07-01", "1999-11-30", "#d9d9d9"),
        ("De la Rúa", "1999-12-01", "2001-12-20", "#ffccdf"),
        ("Duhalde", "2002-01-02", "2003-05-24", "#d6f5d6"),
        ("Néstor Kirchner", "2003-05-25", "2007-12-09", "#d9eefc"),
        ("Cristina Fernández", "2007-12-10", "2015-12-09", "#bfe6ff"),
        ("Macri", "2015-12-10", "2019-12-09", "#fff3b0"),
        ("Fernández", "2019-12-10", "2023-11-30", "#cce5ff"),
        # extend Milei through the projection end so background covers the projection
        ("Milei", "2023-12-01", proj_end, "#e6ccff"),
    ]

    # Create figure (reduced height to allow extra footnote line)
    fig, ax = plt.subplots(figsize=(3840/300, 2400/300), dpi=300)

    # Draw background spans first (low zorder) and add labels for legend
    for nombre, inicio, fin, color in periodos:
        ax.axvspan(pd.to_datetime(inicio), pd.to_datetime(fin), color=color, alpha=0.6, zorder=0, label=nombre)

    # Plot observed series
    ax.plot(df["fecha"], df["salario_por_hora_actual"], color="black", linewidth=3,
            marker='o', markersize=3, label="Salario por hora", zorder=3)

    if len(proj_dates) > 0:
        ax.plot(proj_dates, proj_y, color='red', linestyle='--', linewidth=3,
                label='Proyección lineal hasta Nov 2027')
        ax.axvspan(proj_dates[0], proj_dates[-1], color='#ffe6e6', alpha=0.25)

    # Y axis: include data and projection and add padding, ticks every 1000
    all_vals = df["salario_por_hora_actual"].values
    if proj_y.size > 0:
        all_vals = np.concatenate([all_vals, proj_y])
    ymin = np.nanmin(all_vals)
    ymax = np.nanmax(all_vals)
    # Force y-axis to start at zero
    ylim_min = 0
    ylim_max = np.ceil(1.05 * ymax / 1000) * 1000
    if ylim_max <= 0:
        ylim_max = 1000
    ax.set_ylim(ylim_min, ylim_max)
    yticks_h2 = np.arange(ylim_min, ylim_max + 1, 1000)
    ax.set_yticks(yticks_h2)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(miles_formatter_dot))
    for y in yticks_h2:
        ax.axhline(y=y, color='gray', linestyle='--', linewidth=0.5)

    # Mirror y-axis labels on the right side
    ax_right = ax.twinx()
    ax_right.set_ylim(ylim_min, ylim_max)
    ax_right.set_yticks(yticks_h2)
    ax_right.yaxis.set_major_formatter(plt.FuncFormatter(miles_formatter_dot))
    ax_right.tick_params(axis='y', labelsize=10)

    # X axis formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=1))
    plt.sca(ax)
    ax.tick_params(axis='x', rotation=45)
    for lbl in ax.get_xticklabels():
        lbl.set_ha('right')

    # Show axis a bit beyond the projection: extend up to January 2028
    ax.set_xlim(left=pd.to_datetime("1999-01-01"), right=pd.to_datetime("2028-01-01") + pd.offsets.MonthEnd(0))

    # Title and labels: use the last observed month (before projection) for the 'pesos de' label
    MONTH_NAMES = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
        5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
        9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    last_observed = last_date
    last_label = f"{MONTH_NAMES[last_observed.month]} de {last_observed.year}"
    ax.set_title(f"Salario docente universitario de bolsillo ajustado por IPC\nProfesor Asistente (JTP) — por hora (pesos de {last_label})", fontsize=20)
    ax.set_xlabel("Fecha", fontsize=14)
    ax.set_ylabel("Pesos por hora", fontsize=14)
    # Move legend to bottom-left and allow it to show the presidential periods
    ax.legend(loc='lower left', fontsize=10)

    # Footnote similar to graf_cic.py
    current_date = pd.Timestamp.now().strftime("%d/%m/%Y")
    footnote_text = (
        "Inflación según INDEC (IPC). Se estima IPC constante para el último mes si no hay dato disponible.\n"
        "Serie salarial reconstruida en base a recibos de sueldo de UNC y simulador de ADIUC.\n"
        "Corresponde a un cargo de Profesor Asistente (JTP) con 10 años de antigüedad.\n"
        f"Gráfico generado el {current_date}. Por Rodrigo Quiroga. Ver github.com/rquiroga7/salarios_CONICET"
    )
    plt.figtext(0.98, 0.01, footnote_text, ha='right', fontsize=11, style='italic')

    plt.tight_layout(rect=[0, 0.09, 1, 1])
    plt.savefig(outpng)
    plt.close()

    print(f"Saved: {outpng}")

    # ------------------
    # CIC plot with linear projection to Nov 2027
    # ------------------
    df_cic = pd.read_csv("datos/cic.csv", parse_dates=["fecha"]) 
    df_cic = df_cic.sort_values("fecha")
    last_date_c = df_cic["fecha"].max()
    last_val_c = df_cic.loc[df_cic["fecha"] == last_date_c, "salario_real"].values[0]

    # Fit linear trend on recent 12 months (last year) of the CIC series
    recent_c = df_cic.tail(min(12, len(df_cic)))
    xc = mdates.date2num(recent_c["fecha"]).astype(float)
    yc = recent_c["salario_real"].values.astype(float)
    coeff_c = np.polyfit(xc, yc, 1)
    trend_c = np.poly1d(coeff_c)

    proj_end_c = pd.to_datetime("2027-11-01")
    months_after_c = pd.date_range(start=(last_date_c + pd.offsets.MonthBegin(1)).normalize(), end=proj_end_c, freq='MS')
    if len(months_after_c) == 0:
        proj_dates_c = pd.DatetimeIndex([last_date_c])
    else:
        proj_dates_c = pd.DatetimeIndex([last_date_c]).append(months_after_c)

    trend_vals_c = trend_c(mdates.date2num(proj_dates_c))
    delta_c = last_val_c - trend_vals_c[0]
    proj_y_c = trend_vals_c + delta_c

    # Plot CIC with background periods
    figc, axc = plt.subplots(figsize=(3840/300, 2700/300), dpi=300)
    # Add only the three recent presidencies to the legend for clarity
    legend_periods = {"Macri", "Fernández", "Milei"}
    for nombre, inicio, fin, color in periodos:
        # only show spans that at least touch 2015 onwards (as in graf_cic)
        if nombre in legend_periods:
            axc.axvspan(pd.to_datetime(inicio), pd.to_datetime(fin), color=color, alpha=0.6, zorder=0, label=nombre)
        else:
            axc.axvspan(pd.to_datetime(inicio), pd.to_datetime(fin), color=color, alpha=0.6, zorder=0)

    axc.plot(df_cic["fecha"], df_cic["salario_real"], color="black", linewidth=2,
             marker='o', markersize=3, label="Salario")
    if len(proj_dates_c) > 0:
        axc.plot(proj_dates_c, proj_y_c, color='red', linestyle='--', linewidth=2, label='Proyección lineal hasta Nov 2027')

    # y axis formatting similar to graf_cic but include projection values so projection is visible
    min_value = df_cic["salario_real"].min()
    max_value = df_cic["salario_real"].max()
    if proj_y_c.size > 0:
        min_value = min(min_value, float(np.min(proj_y_c)))
        max_value = max(max_value, float(np.max(proj_y_c)))
    ylim_min = np.floor(0.95 * min_value / 100000) * 100000
    ylim_max = np.ceil(1.05 * max_value / 100000) * 100000
    axc.set_ylim(ylim_min, ylim_max)
    yticks = np.arange(ylim_min, ylim_max + 100000, 100000)
    axc.set_yticks(yticks)
    axc.yaxis.set_major_formatter(plt.FuncFormatter(millones_coma))
    for y in yticks:
        axc.axhline(y=y, color='gray', linestyle='--', linewidth=0.5)

    axc.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    start_year = 2016
    end_year = 2028
    ticks = [pd.to_datetime(f"{y}-01-01") for y in range(start_year, end_year+1)]
    axc.set_xticks(ticks)
    axc.tick_params(axis='x', rotation=45)
    for lbl in axc.get_xticklabels():
        lbl.set_ha('right')

    axc.set_xlim(left=pd.to_datetime("2016-01-01"), right=pd.to_datetime("2028-01-01") + pd.offsets.MonthEnd(0))

    MONTH_NAMES = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
        5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
        9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    last_date_str_c = f"{MONTH_NAMES[last_date_c.month]} de {last_date_c.year}"
    axc.set_title(f"Salario de bolsillo ajustado por IPC\nInvestigador asistente CONICET (pesos de {last_date_str_c})", fontsize=24)
    axc.set_xlabel("Fecha", fontsize=16)
    axc.set_ylabel("Salario real (millones)", fontsize=16)
    # Match legend style/location from profasis projection plot (increase fontsize)
    axc.legend(loc='lower left', fontsize=12)

    # Add right-side secondary y-axis mirroring the left axis
    axc_right = axc.twinx()
    axc_right.set_ylim(ylim_min, ylim_max)
    axc_right.set_yticks(yticks)
    axc_right.yaxis.set_major_formatter(plt.FuncFormatter(millones_coma))
    axc_right.tick_params(axis='y', labelsize=12)

    plt.figtext(0.98, 0.01, f"Inflación según INDEC (IPC). Se estima IPC constante para el último mes si no hay dato disponible.\nSerie reconstruida en base a actas paritarias de UPCN. Gráfico generado el {pd.Timestamp.now().strftime('%d/%m/%Y')}.\nPor Rodrigo Quiroga. Ver github.com/rquiroga7/salarios_CONICET", ha="right", fontsize=12, style='italic')

    plt.tight_layout(rect=[0, 0.06, 1, 1])
    plt.savefig("plots/grafico_salarios_CIC_proy.png")
    plt.close()

    print("Saved: plots/grafico_salarios_CIC_proy.png")

    # ------------------
    # Beca Doctoral plot using CIC-style formatting, projected to Nov 2027
    # ------------------
    df_beca = pd.read_csv("datos/beca_conicet.csv", parse_dates=["fecha"]) 
    df_beca = df_beca.sort_values("fecha")
    last_date_b = df_beca["fecha"].max()
    last_val_b = df_beca.loc[df_beca["fecha"] == last_date_b, "salario_real"].values[0]

    # Fit linear trend on recent 9 months
    recent_b = df_beca.tail(min(9, len(df_beca)))
    xb = mdates.date2num(recent_b["fecha"]).astype(float)
    yb = recent_b["salario_real"].values.astype(float)
    coeff_b = np.polyfit(xb, yb, 1)
    trend_b = np.poly1d(coeff_b)

    proj_end_b = pd.to_datetime("2027-11-01")
    months_after_b = pd.date_range(start=(last_date_b + pd.offsets.MonthBegin(1)).normalize(), end=proj_end_b, freq='MS')
    if len(months_after_b) == 0:
        proj_dates_b = pd.DatetimeIndex([last_date_b])
    else:
        proj_dates_b = pd.DatetimeIndex([last_date_b]).append(months_after_b)

    trend_vals_b = trend_b(mdates.date2num(proj_dates_b))
    delta_b = last_val_b - trend_vals_b[0]
    proj_y_b = trend_vals_b + delta_b

    # Plot Beca Doctoral
    figb, axb = plt.subplots(figsize=(3840/300, 2700/300), dpi=300)
    # Label only recent presidencies in the legend for clarity
    legend_periods = {"Macri", "Fernández", "Milei"}
    for nombre, inicio, fin, color in periodos:
        if nombre in legend_periods:
            axb.axvspan(pd.to_datetime(inicio), pd.to_datetime(fin), color=color, alpha=0.6, zorder=0, label=nombre)
        else:
            axb.axvspan(pd.to_datetime(inicio), pd.to_datetime(fin), color=color, alpha=0.6, zorder=0)

    axb.plot(df_beca["fecha"], df_beca["salario_real"], color="black", linewidth=2,
             marker='o', markersize=3, label="Beca Doctoral")
    if len(proj_dates_b) > 0:
        axb.plot(proj_dates_b, proj_y_b, color='red', linestyle='--', linewidth=2, label='Proyección lineal hasta Nov 2027')

    # y axis include projection
    min_value_b = df_beca["salario_real"].min()
    max_value_b = df_beca["salario_real"].max()
    if proj_y_b.size > 0:
        min_value_b = min(min_value_b, float(np.min(proj_y_b)))
        max_value_b = max(max_value_b, float(np.max(proj_y_b)))
    ylim_min_b = np.floor(0.95 * min_value_b / 100000) * 100000
    ylim_max_b = np.ceil(1.05 * max_value_b / 100000) * 100000
    axb.set_ylim(ylim_min_b, ylim_max_b)
    yticks_b = np.arange(ylim_min_b, ylim_max_b + 100000, 100000)
    axb.set_yticks(yticks_b)
    axb.yaxis.set_major_formatter(plt.FuncFormatter(millones_coma))
    for y in yticks_b:
        axb.axhline(y=y, color='gray', linestyle='--', linewidth=0.5)

    # Mirror right axis
    axb_right = axb.twinx()
    axb_right.set_ylim(ylim_min_b, ylim_max_b)
    axb_right.set_yticks(yticks_b)
    axb_right.yaxis.set_major_formatter(plt.FuncFormatter(millones_coma))
    left_labels_b = axb.yaxis.get_ticklabels()
    if len(left_labels_b) > 0:
        left_fp_b = left_labels_b[0].get_fontproperties()
        for lbl in axb_right.yaxis.get_ticklabels():
            lbl.set_fontproperties(left_fp_b)
    else:
        axb_right.tick_params(axis='y', labelsize=12)

    axb.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    start_y = 2016
    end_y = 2028
    ticks_b = [pd.to_datetime(f"{y}-01-01") for y in range(start_y, end_y+1)]
    axb.set_xticks(ticks_b)
    axb.tick_params(axis='x', rotation=45)
    for lbl in axb.get_xticklabels():
        lbl.set_ha('right')

    axb.set_xlim(left=pd.to_datetime("2016-01-01"), right=pd.to_datetime("2028-01-01") + pd.offsets.MonthEnd(0))

    last_date_b_str = f"{MONTH_NAMES[last_date_b.month]} de {last_date_b.year}"
    axb.set_title(f"Beca Doctoral CONICET\n(ajustado por inflación, en pesos de {last_date_b_str})", fontsize=24)
    axb.set_xlabel("Fecha", fontsize=16)
    axb.set_ylabel("Salario real (millones)", fontsize=16)
    axb.legend(loc='lower left', fontsize=12)

    plt.figtext(0.98, 0.01, f"Inflación según INDEC (IPC). Se estima IPC constante para el último mes si no hay dato disponible.\nSerie reconstruida en base a publicaciones periódicas de CONICET. Gráfico generado el {pd.Timestamp.now().strftime('%d/%m/%Y')}.\nPor Rodrigo Quiroga. Ver github.com/rquiroga7/salarios_CONICET", ha="right", fontsize=12, style='italic')

    plt.tight_layout(rect=[0, 0.06, 1, 1])
    plt.savefig("plots/grafico_salarios_beca_doctoral_proy.png")
    plt.close()

    print("Saved: plots/grafico_salarios_beca_doctoral_proy.png")

if __name__ == '__main__':
    main()
