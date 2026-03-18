"""
Script para construir la serie histórica de salarios del Profesor Asistente D.E.
desde diciembre 2015 hasta la fecha actual.

Este script combina:
1. Datos scrapeados del simulador de ADIUC (si están disponibles)
2. Datos ingresados manualmente desde informes del Observatorio de Salario

Los datos se guardan en datos/crudo_profasis_historico.csv
"""

import pandas as pd
from datetime import datetime
import os

# ============================================
# DATOS HISTÓRICOS - PROFASOR ASISTENTE D.E.
# ============================================
# Fuente: ADIUC - Observatorio de Salario y Presupuesto
# https://adiuc.org.ar/instituto-oscar-varsavsky/observatorio-de-salario-y-presupuesto/
#
# Para completar esta sección, consultar los informes PDF:
# - INFORME DE PARITARIA 2022 (MARZO 2022 | FEBRERO 2023)
# - PARITARIA 2022 Y AVANCE 2023 (MARZO 2022-JUNIO 2023)
# - PARITARIA 2023 (ACTUALIZACIÓN NOVIEMBRE)
# - EVOLUCIÓN DEL SALARIO DOCENTE 2024
#
# El salario a ingresar es el "Neto a Cobrar" para Profesor Asistente D.E.
# ============================================

datos_manuales = {
    # 2015 - Año base
    "2015-12-01": None,  # Completar con dato de informe
    
    # 2016
    "2016-01-01": None,
    "2016-02-01": None,
    "2016-03-01": None,
    "2016-04-01": None,
    "2016-05-01": None,
    "2016-06-01": None,
    "2016-07-01": None,
    "2016-08-01": None,
    "2016-09-01": None,
    "2016-10-01": None,
    "2016-11-01": None,
    "2016-12-01": None,
    
    # 2017
    "2017-01-01": None,
    "2017-02-01": None,
    "2017-03-01": None,
    "2017-04-01": None,
    "2017-05-01": None,
    "2017-06-01": None,
    "2017-07-01": None,
    "2017-08-01": None,
    "2017-09-01": None,
    "2017-10-01": None,
    "2017-11-01": None,
    "2017-12-01": None,
    
    # 2018
    "2018-01-01": None,
    "2018-02-01": None,
    "2018-03-01": None,
    "2018-04-01": None,
    "2018-05-01": None,
    "2018-06-01": None,
    "2018-07-01": None,
    "2018-08-01": None,
    "2018-09-01": None,
    "2018-10-01": None,
    "2018-11-01": None,
    "2018-12-01": None,
    
    # 2019
    "2019-01-01": None,
    "2019-02-01": None,
    "2019-03-01": None,
    "2019-04-01": None,
    "2019-05-01": None,
    "2019-06-01": None,
    "2019-07-01": None,
    "2019-08-01": None,
    "2019-09-01": None,
    "2019-10-01": None,
    "2019-11-01": None,
    "2019-12-01": None,
    
    # 2020
    "2020-01-01": None,
    "2020-02-01": None,
    "2020-03-01": None,
    "2020-04-01": None,
    "2020-05-01": None,
    "2020-06-01": None,
    "2020-07-01": None,
    "2020-08-01": None,
    "2020-09-01": None,
    "2020-10-01": None,
    "2020-11-01": None,
    "2020-12-01": None,
    
    # 2021
    "2021-01-01": None,
    "2021-02-01": None,
    "2021-03-01": None,
    "2021-04-01": None,
    "2021-05-01": None,
    "2021-06-01": None,
    "2021-07-01": None,
    "2021-08-01": None,
    "2021-09-01": None,
    "2021-10-01": None,
    "2021-11-01": None,
    "2021-12-01": None,
    
    # 2022
    "2022-01-01": None,
    "2022-02-01": None,
    "2022-03-01": None,
    "2022-04-01": None,
    "2022-05-01": None,
    "2022-06-01": None,
    "2022-07-01": None,
    "2022-08-01": None,
    "2022-09-01": None,
    "2022-10-01": None,
    "2022-11-01": None,
    "2022-12-01": None,
    
    # 2023
    "2023-01-01": None,
    "2023-02-01": None,
    "2023-03-01": None,
    "2023-04-01": None,
    "2023-05-01": None,
    "2023-06-01": None,
    "2023-07-01": None,
    "2023-08-01": None,
    "2023-09-01": None,
    "2023-10-01": None,
    # Noviembre 2023 en adelante ya tenemos datos
}

# Datos existentes desde crudo_profasis.csv (Noviembre 2023 en adelante)
datos_existentes = {
    "2023-11-01": 449442,
    "2023-12-01": 474161,
    "2024-01-01": 474161,
    "2024-02-01": 550027,
    "2024-03-01": 616030,
    "2024-04-01": 665313,
    "2024-05-01": 725191,
    "2024-06-01": 754198,
    "2024-07-01": 810763,
    "2024-08-01": 826979,
    "2024-09-01": 851788,
    "2024-10-01": 909709,
    "2024-11-01": 927904,
    "2024-12-01": 937183,
    "2025-01-01": 951240,
    "2025-02-01": 962655,
    "2025-03-01": 975170,
    "2025-04-01": 987847,
    "2025-05-01": 1000689,
    "2025-06-01": 1013698,
    "2025-07-01": 1026876,
    "2025-08-01": 1040225,
    "2025-09-01": 1052708,
    "2025-10-01": 1064288,
    "2025-11-01": 1075995,
    "2025-12-01": 1097515,
    "2026-01-01": 1124953,
    "2026-02-01": 1149702,
    "2026-03-01": 1172696,
}


def construir_serie_historica():
    """Construye la serie histórica combinando datos manuales y existentes"""
    
    # Combinar datos
    todos_datos = {**datos_manuales, **datos_existentes}
    
    # Filtrar None y crear DataFrame
    datos_validos = {k: v for k, v in todos_datos.items() if v is not None}
    
    df = pd.DataFrame([
        {"fecha": k, "salario": v}
        for k, v in datos_validos.items()
    ])
    
    # Ordenar por fecha
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha").reset_index(drop=True)
    
    # Formatear fecha
    df["fecha"] = df["fecha"].dt.strftime("%Y-%m-%d")
    
    # Guardar CSV
    archivo_salida = "datos/crudo_profasis_historico.csv"
    df.to_csv(archivo_salida, index=False)
    
    print("=" * 60)
    print("SERIE HISTÓRICA - PROFESOR ASISTENTE D.E.")
    print("=" * 60)
    print(f"Período: {df['fecha'].iloc[0]} a {df['fecha'].iloc[-1]}")
    print(f"Total de registros: {len(df)}")
    print(f"Archivo guardado: {archivo_salida}")
    print("=" * 60)
    print("\nÚltimos 10 registros:")
    print(df.tail(10).to_string(index=False))
    print("\nPrimeros 10 registros:")
    print(df.head(10).to_string(index=False))
    
    # Verificar datos faltantes
    datos_faltantes = sum(1 for v in datos_manuales.values() if v is None)
    if datos_faltantes > 0:
        print(f"\n⚠️ Hay {datos_faltantes} datos faltantes por completar (2015-2023)")
        print("Complete los valores en el diccionario 'datos_manuales' en este script.")
    
    return df


def verificar_datos():
    """Verifica la consistencia de los datos"""
    df = pd.read_csv("datos/crudo_profasis_historico.csv", parse_dates=["fecha"])
    
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE DATOS")
    print("=" * 60)
    
    # Estadísticas básicas
    print(f"\nEstadísticas del salario:")
    print(f"  Mínimo: ${df['salario'].min():,.0f}")
    print(f"  Máximo: ${df['salario'].max():,.0f}")
    print(f"  Promedio: ${df['salario'].mean():,.0f}")
    print(f"  Mediana: ${df['salario'].median():,.0f}")
    
    # Verificar saltos grandes
    df["variacion"] = df["salario"].pct_change() * 100
    saltos_grandes = df[df["variacion"].abs() > 50]
    if len(saltos_grandes) > 0:
        print(f"\n⚠️ Saltos grandes detectados (>50%):")
        for _, row in saltos_grandes.iterrows():
            print(f"  {row['fecha'].strftime('%Y-%m-%d')}: {row['variacion']:+.1f}%")
    
    # Verificar meses consecutivos
    fechas = pd.to_datetime(df["fecha"])
    meses_faltantes = []
    for i in range(1, len(fechas)):
        diff = (fechas.iloc[i] - fechas.iloc[i-1]).days / 30
        if diff > 1.5:  # Más de 1.5 meses
            meses_faltantes.append({
                "desde": fechas.iloc[i-1].strftime("%Y-%m-%d"),
                "hasta": fechas.iloc[i].strftime("%Y-%m-%d"),
                "meses_aprox": diff
            })
    
    if meses_faltantes:
        print(f"\n⚠️ Huecos en la serie:")
        for hueco in meses_faltantes:
            print(f"  {hueco['desde']} a {hueco['hasta']} (~{hueco['meses_aprox']:.1f} meses)")
    else:
        print("\n✓ No se detectaron huecos en la serie")
    
    return df


if __name__ == "__main__":
    # Construir serie histórica
    df = construir_serie_historica()
    
    # Verificar datos
    verificar_datos()
