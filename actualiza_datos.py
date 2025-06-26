import pandas as pd
import numpy as np
import xlrd 

def procesar_salarios(tipo):
    """
    Procesa los datos de salarios para un tipo específico (cic, conicet, foncyt, profasis)
    """
    # Leer datos de salarios y estipendios
    df = pd.read_csv(f"datos/crudo_{tipo}.csv", parse_dates=["fecha"])
    
    # Leer datos de inflación
    ipc = pd.read_csv("datos/ipc_crudo.csv", parse_dates=["fecha"])

    # Procesar IPC desde Excel
    workbook = xlrd.open_workbook("datos/sh_ipc_06_25.xls")
    sheet = workbook.sheet_by_name("Índices IPC Cobertura Nacional")
    
    ipc_values = []
    for col in range(2, sheet.ncols):
        value = sheet.cell_value(9, col)
        if value:
            ipc_values.append(value)

    # Crear DataFrame de IPC
    ipc_dates = pd.date_range(start="2017-01-01", periods=len(ipc_values), freq='MS')
    ultimo_indice = ipc["indice"].iloc[-1]
    ipc_values = [x * ultimo_indice/100 for x in ipc_values]
    ipc2 = pd.DataFrame({"fecha": ipc_dates, "indice": ipc_values})
    ipc = pd.concat([ipc, ipc2], ignore_index=True)

    # Estimar último mes si falta
    if ipc["fecha"].iloc[-1] != df["fecha"].iloc[-1]:
        ultimo_indice = ipc["indice"].iloc[-1] * (ipc["indice"].iloc[-1] / ipc["indice"].iloc[-2])
        ipc = pd.concat([ipc, pd.DataFrame({
            "fecha": [df["fecha"].iloc[-1]], 
            "indice": [ultimo_indice]
        })], ignore_index=True)

    # Unir datos
    df = df.merge(ipc[["fecha", "indice"]], on="fecha", how="left")
    
    # Calcular ajustes
    fecha_inicio = pd.to_datetime("2023-11-01")
    salario_base = df.loc[df["fecha"] == fecha_inicio, "salario"].iloc[0]
    indice_base = df.loc[df["fecha"] == fecha_inicio, "indice"].iloc[0]
    
    df["ajustado"] = np.where(
        df["fecha"] < fecha_inicio,
        df["salario"],
        salario_base * (df["indice"] / indice_base)
    )
    
    df["salario_indice"] = df["salario"] / df["salario"].iloc[0]
    df["nominal"] = df["salario"]
    df["salario_real_indice"] = df["salario_indice"] / df["indice"]
    df["salario_real"] = (df["salario"].iloc[-1] * 
                         df["salario_real_indice"] / 
                         df["salario_real_indice"].iloc[-1])

    return df

def actualizar_datos():
    """
    Procesa todos los tipos de salarios y guarda los resultados
    """
    tipos = ["cic", "conicet", "foncyt", "profasis"]
    
    for tipo in tipos:
        try:
            df = procesar_salarios(tipo)
            
            # Guardar datos procesados
            df[["fecha", "salario_real"]].to_csv(f"datos/{tipo}.csv", index=False)
            df[df["fecha"] >= "2023-11-01"][["fecha", "nominal", "ajustado"]].to_csv(
                f"datos/{tipo}_ajustado.csv", index=False)
            
            print(f"Procesamiento exitoso para {tipo}")
            
        except Exception as e:
            print(f"Error procesando {tipo}: {e}")

if __name__ == "__main__":
    actualizar_datos()