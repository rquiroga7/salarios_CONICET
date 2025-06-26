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
    try:
        urllib.request.urlretrieve(url, data_dir / filename)
        with open("version_IPC.txt", "w") as f:
            f.write(filename)
        return True
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
        download_ipc_file(current_file, data_dir)
    
    # Leer IPC actual
    if current_path.exists():
        try:
            ipc = read_ipc_from_xls(current_path)
        except Exception as e:
            print(f"Error parsing filename {current_file}: {e}")
            return None

    # Estimar último mes si es necesario
    if (ipc["fecha"].max() != df["fecha"].max()) and \
       (ipc["fecha"].max() + pd.Timedelta(days=31) >= df["fecha"].max()):
        print("Falta dato de IPC para el último mes. Estimando último mes de IPC...")
        ultimo_indice = ipc["indice"].iloc[-1] * (ipc["indice"].iloc[-1] / ipc["indice"].iloc[-2])
        ipc = pd.concat([ipc, pd.DataFrame({
            "fecha": [df["fecha"].max()],
            "indice": [ultimo_indice]
        })], ignore_index=True)
    elif ipc["fecha"].max() + pd.Timedelta(days=31) < df["fecha"].max():
        print("Faltan datos de IPC para más de un mes. Actualizando archivo desde INDEC...")
        if download_ipc_file(next_file, data_dir):
            ipc = read_ipc_from_xls(data_dir / next_file)
        else:
            return None

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