import pandas as pd
import numpy as np
import xlrd 
import urllib.request
import os
from pathlib import Path

def read_ipc_from_xls(filename, start_date="2017-01-01"):
    """
    Lee valores de IPC desde archivo XLS y retorna DataFrame
    """
    # Leer archivo XLS
    workbook = xlrd.open_workbook(filename)
    sheet = workbook.sheet_by_name("Índices IPC Cobertura Nacional")
    
    # Extraer valores
    ipc_values = []
    for col in range(2, sheet.ncols):
        value = sheet.cell_value(9, col)
        if value:
            ipc_values.append(value)
    
    # Crear fechas y DataFrame
    ipc_dates = pd.date_range(start=start_date, periods=len(ipc_values), freq='MS')
    
    ipc = pd.read_csv("datos/ipc_crudo.csv", parse_dates=["fecha"])
    ultimo_indice = ipc["indice"].iloc[-1]
    ipc_values = [x * ultimo_indice/100 for x in ipc_values]
    ipc2 = pd.DataFrame({"fecha": ipc_dates, "indice": ipc_values})
    ipc = pd.concat([ipc, ipc2], ignore_index=True)

    return ipc

def parse_ipc_filename(filename):
    """
    Parse IPC filename to extract month and year
    """
    # Remove .xls extension and split
    parts = filename.replace('.xls', '').split('_')
    month = int(parts[2])  # Get month number
    year = int(parts[3])   # Get year number
    return month, year

def download_ipc_file(filename, data_dir):
    """
    Downloads IPC file from INDEC website
    """
    url = f"https://www.indec.gob.ar/ftp/cuadros/economia/{filename}"
    temp_path = data_dir / filename
    try:
        urllib.request.urlretrieve(url, temp_path)
        # Verify it's a valid Excel file
        try:
            xlrd.open_workbook(temp_path)
            return True
        except Exception as e:
            # Not a valid Excel file, remove it
            if temp_path.exists():
                temp_path.unlink()
            print(f"Downloaded file is not valid: {e}")
            return False
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False

def update_ipc_data(df):
    """
    Actualiza datos de IPC si es necesario
    """
    data_dir = Path("datos")
    data_dir.mkdir(exist_ok=True)
    
    # Determinar archivo actual
    try:
        with open("version_IPC.txt", "r") as f:
            current_file = f.read().strip()
            current_path = data_dir / current_file
    except FileNotFoundError:
        raise FileNotFoundError("No se encontró el archivo version_IPC.txt. Por favor, asegúrate de que el archivo existe y contiene el nombre del último archivo IPC.")
    
    # Descargar archivo si no existe
    if not current_path.exists():
        print(f"Archivo {current_file} no encontrado. Descargando del sitio de INDEC...")
        if not download_ipc_file(current_file, data_dir):
            print(f"No se pudo descargar {current_file}")
            return None
    
    # Leer IPC actual
    try:
        ipc = read_ipc_from_xls(current_path)
    except Exception as e:
        print(f"Error leyendo archivo {current_file}: {e}")
        return None

    # Intentar descargar archivo más reciente
    try:
        current_month, current_year = parse_ipc_filename(current_file)
        # Calcular próximo mes
        next_month = current_month + 1
        next_year = current_year
        if next_month > 12:
            next_month = 1
            next_year += 1
        
        next_file = f"sh_ipc_{next_month:02d}_{next_year % 100:02d}.xls"
        print(f"Verificando si existe archivo más reciente: {next_file}...")
        
        if download_ipc_file(next_file, data_dir):
            print(f"Archivo {next_file} descargado exitosamente. Actualizando datos...")
            ipc = read_ipc_from_xls(data_dir / next_file)
            # Update version file only if new file is valid
            with open("version_IPC.txt", "w") as f:
                f.write(next_file)
        else:
            print(f"Archivo {next_file} no disponible. Usando {current_file}...")
    except Exception as e:
        print(f"Error al intentar descargar archivo más reciente: {e}")

    # Estimar meses faltantes si es necesario
    while ipc["fecha"].max() < df["fecha"].max():
        print(f"Falta dato de IPC para {(ipc['fecha'].max() + pd.DateOffset(months=1)).strftime('%Y-%m')}. Estimando...")
        ultimo_indice = ipc["indice"].iloc[-1] * (ipc["indice"].iloc[-1] / ipc["indice"].iloc[-2])
        siguiente_fecha = ipc["fecha"].max() + pd.DateOffset(months=1)
        ipc = pd.concat([ipc, pd.DataFrame({
            "fecha": [siguiente_fecha],
            "indice": [ultimo_indice]
        })], ignore_index=True)

    # Guardar datos actualizados
    ipc.to_csv(data_dir / "ipc_nuevo.csv", index=False)
    return ipc

def main():
    """
    Función principal
    """
    try:
        df = pd.read_csv("datos/crudo_cic.csv", parse_dates=["fecha"])
        ipc = update_ipc_data(df)
        if ipc is not None:
            print("Actualización de IPC completada exitosamente")
    except Exception as e:
        print(f"Error en el proceso: {e}")

if __name__ == "__main__":
    main()