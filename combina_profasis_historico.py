"""
Script para combinar los datos scrapeados del simulador ADIUC (2020-2023)
con los datos existentes de crudo_profasis.csv (2023-2026) para crear
una serie histórica completa.
"""

import pandas as pd
import numpy as np

# Leer datos scrapeados (2020-2026 del simulador)
scraped = pd.read_csv('datos/crudo_profasis_historico.csv', parse_dates=['fecha'])

# Leer datos existentes (2023-2026 de fuente UNC)
existing = pd.read_csv('datos/crudo_profasis.csv', parse_dates=['fecha'])

print("=== Datos scrapeados (simulador ADIUC) ===")
print(f"Período: {scraped['fecha'].min()} a {scraped['fecha'].max()}")
print(f"Registros: {len(scraped)}")

print("\n=== Datos existentes (fuente UNC) ===")
print(f"Período: {existing['fecha'].min()} a {existing['fecha'].max()}")
print(f"Registros: {len(existing)}")

# Calcular factor de conversión basado en Noviembre 2023 (mes de superposición)
nov_2023_scrap = scraped[scraped['fecha'] == '2023-11-01']['salario'].values[0]
nov_2023_exist = existing[existing['fecha'] == '2023-11-01']['salario'].values[0]
factor = nov_2023_exist / nov_2023_scrap

print(f"\n=== Factor de conversión ===")
print(f"Salario Noviembre 2023 (scrapeado): ${nov_2023_scrap:,.2f}")
print(f"Salario Noviembre 2023 (existente): ${nov_2023_exist:,.0f}")
print(f"Factor de conversión: {factor:.4f}")

# Aplicar factor de conversión a los datos scrapeados
scraped['salario_ajustado'] = (scraped['salario'] * factor).round(0).astype(int)

print("\n=== Datos scrapeados ajustados ===")
print(scraped[['fecha', 'salario', 'salario_ajustado']].head(10).to_string(index=False))

# Combinar datos: usar scrapeados hasta Octubre 2023, existentes desde Noviembre 2023
scraped_antes_oct2023 = scraped[scraped['fecha'] < '2023-11-01'][['fecha', 'salario_ajustado']].copy()
scraped_antes_oct2023.columns = ['fecha', 'salario']

# Datos existentes completos
existing_completo = existing[['fecha', 'salario']].copy()

# Combinar
combinado = pd.concat([scraped_antes_oct2023, existing_completo], ignore_index=True)
combinado = combinado.sort_values('fecha').reset_index(drop=True)

# Verificar duplicados
duplicados = combinado[combinado.duplicated(subset=['fecha'], keep=False)]
if len(duplicados) > 0:
    print(f"\n=== Duplicados encontrados ({len(duplicados)}) ===")
    print(duplicados.to_string(index=False))
    # Eliminar duplicados, mantener el último
    combinado = combinado.drop_duplicates(subset=['fecha'], keep='last').sort_values('fecha').reset_index(drop=True)

print("\n=== Serie histórica combinada ===")
print(f"Período: {combinado['fecha'].min().strftime('%Y-%m-%d')} a {combinado['fecha'].max().strftime('%Y-%m-%d')}")
print(f"Registros: {len(combinado)}")

# Guardar
combinado.to_csv('datos/crudo_profasis_historico.csv', index=False)
print(f"\nArchivo guardado: datos/crudo_profasis_historico.csv")

# Mostrar primeros y últimos registros
print("\n=== Primeros 15 registros ===")
print(combinado.head(15).to_string(index=False))

print("\n=== Últimos 15 registros ===")
print(combinado.tail(15).to_string(index=False))

# Estadísticas
print("\n=== Estadísticas ===")
print(f"Salario mínimo: ${combinado['salario'].min():,.0f} ({combinado.loc[combinado['salario'].idxmin(), 'fecha'].strftime('%Y-%m-%d')})")
print(f"Salario máximo: ${combinado['salario'].max():,.0f} ({combinado.loc[combinado['salario'].idxmax(), 'fecha'].strftime('%Y-%m-%d')})")
print(f"Salario promedio: ${combinado['salario'].mean():,.0f}")
print(f"Salario mediana: ${combinado['salario'].median():,.0f}")

# Verificar saltos grandes
combinado['variacion'] = combinado['salario'].pct_change() * 100
saltos = combinado[combinado['variacion'].abs() > 30]
if len(saltos) > 0:
    print("\n=== Saltos grandes (>30%) ===")
    for _, row in saltos.iterrows():
        print(f"{row['fecha'].strftime('%Y-%m-%d')}: {row['variacion']:+.1f}% (salario: ${row['salario']:,.0f})")
