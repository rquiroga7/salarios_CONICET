"""
Script para extraer el histórico de salarios del Profesor Asistente D.E.
desde el simulador salarial de ADIUC: https://simusueldo.adiuc.org.ar

Extrae el "Neto a Cobrar" para cada mes desde 2020 hasta la fecha.
Nota: El simulador solo tiene datos desde 2020.
"""

import pandas as pd
import time
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# Configuración
URL_SIMULADOR = "https://simusueldo.adiuc.org.ar"
CARGO_PROFASIS = "16"  # Profesor Asistente D.E.
ANIO_INICIO = 2020  # El simulador solo tiene datos desde 2020
MES_FIN = datetime.now().month
ANIO_FIN = datetime.now().year


def obtener_session():
    """Crea una sesión requests con headers apropiados"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'Accept-Language': 'es-AR,es;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'https://adiuc.org.ar/gremial/salario/',
        'Origin': 'https://simusueldo.adiuc.org.ar',
    })
    return session


def obtener_token_csrf(session):
    """Obtiene el token CSRF del formulario"""
    response = session.get(URL_SIMULADOR)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    form = soup.find('form')
    
    if form:
        token_input = form.find('input', {'name': 'csrfmiddlewaretoken'})
        if token_input:
            return token_input.get('value'), response.cookies
    return None, response.cookies


def extraer_neto_cobrar_html(html_content):
    """Extrae el valor de 'Neto a Cobrar' del HTML del resultado"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Buscar específicamente la sección "Neto a Cobrar"
        # El simulador muestra una tarjeta con class="net-summary-card"
        net_card = soup.find('div', class_='net-summary-card')
        
        if net_card:
            # Buscar el valor dentro de la tarjeta
            summary_items = net_card.find_all('div', class_='summary-item')
            
            for item in summary_items:
                label = item.find('span', class_='s-label')
                value_elem = item.find('span', class_='s-value')
                
                if label and value_elem:
                    label_text = label.get_text(strip=True).lower()
                    
                    if 'neto a cobrar' in label_text:
                        value_text = value_elem.get_text(strip=True)
                        # Extraer número del formato "$ 366761,73" o "479427,10"
                        # Usar regex simple que captura todos los dígitos antes de la coma
                        match = re.search(r'([0-9]+(?:,[0-9]{2})?)', value_text)
                        if match:
                            numero_str = match.group(1)
                            numero_str = numero_str.replace('.', '').replace(',', '.')
                            return float(numero_str)
        
        # Fallback: buscar en toda la página el texto "Neto a Cobrar"
        for elem in soup.find_all(string=re.compile(r'[Nn]eto.*[Cc]obrar', re.IGNORECASE)):
            padre = elem.find_parent(['td', 'th', 'div', 'span', 'tr'])
            if padre:
                # Buscar el valor en el mismo elemento o hermanos
                value_elem = padre.find('span', class_='s-value') or padre.find_next_sibling(['td', 'div', 'span'])
                if value_elem:
                    texto = value_elem.get_text(strip=True)
                    match = re.search(r'([0-9]+(?:,[0-9]{2})?)', texto)
                    if match:
                        numero_str = match.group(1)
                        numero_str = numero_str.replace('.', '').replace(',', '.')
                        return float(numero_str)
        
        return None
        
    except Exception as e:
        print(f"Error extrayendo neto cobrar: {e}")
        return None


def simular_salario_request(session, mes, anio, csrf_token):
    """
    Simula el salario para un mes, año y cargo específicos.
    Retorna el Neto a Cobrar.
    """
    try:
        # Construir el payload
        payload = {
            'csrfmiddlewaretoken': csrf_token,
            'mes': str(mes),
            'anio': str(anio),
            'antiguedad': '0',  # Sin antigüedad
            'univcargo-TOTAL_FORMS': '1',
            'univcargo-INITIAL_FORMS': '0',
            'univcargo-MIN_NUM_FORMS': '0',
            'univcargo-MAX_NUM_FORMS': '5',
            'univcargo-0-cargo': CARGO_PROFASIS,  # Profesor Asistente D.E.
            'univcargo-0-horas': '40',  # Dedicación Exclusiva = 40 horas
            'preunivcargo-TOTAL_FORMS': '0',
            'preunivcargo-INITIAL_FORMS': '0',
            'preunivcargo-MIN_NUM_FORMS': '0',
            'preunivcargo-MAX_NUM_FORMS': '5',
            'doctorado': False,
            'master': False,
            'especialista': False,
            'afiliado': False,
        }
        
        # Enviar formulario
        response = session.post(
            URL_SIMULADOR,
            data=payload,
            headers={'Referer': URL_SIMULADOR}
        )
        response.raise_for_status()
        
        # Guardar HTML para depuración
        with open(f"datos/simulacion_{anio}_{mes:02d}.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        # Extraer Neto a Cobrar
        neto = extraer_neto_cobrar_html(response.text)
        
        return neto
        
    except Exception as e:
        print(f"Error en simulación {mes}/{anio}: {e}")
        return None


def scrape_historico():
    """Scrapea todo el histórico de salarios"""
    session = obtener_session()
    resultados = []
    
    try:
        print(f"Iniciando scrapeo desde {ANIO_INICIO} hasta {ANIO_FIN}/{MES_FIN}")
        print(f"Cargo: Profesor Asistente D.E. (codigo={CARGO_PROFASIS})")
        print(f"URL: {URL_SIMULADOR}")
        print("-" * 60)
        
        # Obtener token CSRF inicial
        csrf_token, cookies = obtener_token_csrf(session)
        session.cookies.update(cookies)
        
        if not csrf_token:
            print("Error: No se pudo obtener el token CSRF")
            return None
        
        print(f"Token CSRF obtenido: {csrf_token[:20]}...")
        
        # Iterar por todos los meses y años
        anio = ANIO_INICIO
        mes = 1  # Enero
        
        while True:
            fecha_str = f"{anio}-{mes:02d}-01"
            print(f"Procesando: {fecha_str}...", end=" ")
            
            neto = simular_salario_request(session, mes, anio, csrf_token)
            
            if neto is not None:
                resultados.append({"fecha": fecha_str, "salario": neto})
                print(f"${neto:,.0f}")
            else:
                print("No encontrado")
            
            # Actualizar token CSRF (puede cambiar)
            csrf_token, cookies = obtener_token_csrf(session)
            session.cookies.update(cookies)
            
            # Avanzar al siguiente mes
            mes += 1
            if mes > 12:
                mes = 1
                anio += 1
            
            # Verificar si llegamos al final
            if anio > ANIO_FIN or (anio == ANIO_FIN and mes > MES_FIN):
                break
            
            # Pequeña pausa para no sobrecargar el servidor
            time.sleep(1)
        
        # Crear DataFrame y guardar
        df = pd.DataFrame(resultados)
        
        # Guardar CSV
        archivo_salida = "datos/crudo_profasis_historico.csv"
        df.to_csv(archivo_salida, index=False)
        print("-" * 60)
        print(f"Datos guardados en: {archivo_salida}")
        print(f"Total de registros: {len(resultados)}")
        print(df.to_string(index=False))
        
        return df
        
    finally:
        session.close()


if __name__ == "__main__":
    scrape_historico()
