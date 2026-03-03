import pandas as pd
import numpy as np
import xlrd

def procesar_salarios(tipo):
    """
    Procesa los datos de salarios para un tipo específico (cic, beca_conicet, foncyt, profasis)
    """
    # Leer datos de salarios y estipendios
    df = pd.read_csv(f"datos/crudo_{tipo}.csv", parse_dates=["fecha"])

    # Leer datos de inflación
    ipc = pd.read_csv("datos/ipc_nuevo.csv", parse_dates=["fecha"])

    # Unir datos
    df = df.merge(ipc[["fecha", "indice"]], on="fecha", how="left")

    # Project missing IPC data using previous month's inflation rate
    # For months without IPC data, assume same monthly variation as last available month
    df = df.sort_values("fecha").reset_index(drop=True)
    for i in range(len(df)):
        if pd.isna(df.loc[i, "indice"]):
            if i >= 2 and pd.notna(df.loc[i-1, "indice"]) and pd.notna(df.loc[i-2, "indice"]):
                # Calculate monthly growth rate from previous month
                prev_growth = df.loc[i-1, "indice"] / df.loc[i-2, "indice"]
                # Apply same growth rate
                df.loc[i, "indice"] = df.loc[i-1, "indice"] * prev_growth
            elif i >= 1 and pd.notna(df.loc[i-1, "indice"]):
                # If only one previous value, just carry it forward
                df.loc[i, "indice"] = df.loc[i-1, "indice"]

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
    tipos = ["cic", "beca_conicet", "foncyt", "profasis", "art9", "resgarrahan"]
    
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