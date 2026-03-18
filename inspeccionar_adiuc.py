"""
Script para extraer salarios del simulador de ADIUC.
Prueba diferentes métodos para obtener los datos del simulador salarial.

URL: https://adiuc.org.ar/gremial/salario/
"""

import requests
from bs4 import BeautifulSoup
import time
import re

URL_SIMULADOR = "https://adiuc.org.ar/gremial/salario/"
URL_BASE = "https://adiuc.org.ar"


def inspeccionar_pagina():
    """Inspecciona la página del simulador para entender su estructura"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'Accept-Language': 'es-AR,es;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    })
    
    print("Descargando página del simulador...")
    response = session.get(URL_SIMULADOR)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Guardar HTML para inspección manual
        with open("datos/adiuc_simulador_raw.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("HTML guardado en: datos/adiuc_simulador_raw.html")
        
        # Buscar formularios
        forms = soup.find_all('form')
        print(f"\nFormularios encontrados: {len(forms)}")
        
        for i, form in enumerate(forms):
            print(f"\n--- Formulario {i+1} ---")
            print(f"Action: {form.get('action', 'N/A')}")
            print(f"Method: {form.get('method', 'N/A')}")
            
            inputs = form.find_all('input')
            selects = form.find_all('select')
            buttons = form.find_all('button')
            
            print(f"Inputs: {len(inputs)}")
            print(f"Selects: {len(selects)}")
            print(f"Buttons: {len(buttons)}")
            
            # Mostrar detalles de selects
            for select in selects:
                print(f"\n  Select: name={select.get('name')}, id={select.get('id')}")
                options = select.find_all('option')
                print(f"  Opciones ({len(options)}):")
                for opt in options[:10]:  # Mostrar primeras 10
                    print(f"    - {opt.get_text(strip=True)} (value={opt.get('value', '')})")
                if len(options) > 10:
                    print(f"    ... y {len(options) - 10} más")
        
        # Buscar iframes
        iframes = soup.find_all('iframe')
        if iframes:
            print(f"\nIframes encontrados: {len(iframes)}")
            for iframe in iframes:
                print(f"  - src={iframe.get('src', 'N/A')}")
        
        # Buscar scripts que puedan cargar contenido dinámicamente
        scripts = soup.find_all('script', src=True)
        if scripts:
            print(f"\nScripts externos: {len(scripts)}")
            for script in scripts[:5]:
                print(f"  - {script.get('src')}")
        
        return response.text
    
    return None


def buscar_enlace_simulador():
    """Busca el enlace directo al simulador en la página principal"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    print("\n" + "=" * 60)
    print("Buscando enlaces al simulador...")
    print("=" * 60)
    
    response = session.get(URL_SIMULADOR)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Buscar todos los enlaces
    enlaces = soup.find_all('a', href=True)
    
    simuladores = []
    for enlace in enlaces:
        texto = enlace.get_text(strip=True).lower()
        href = enlace['href']
        
        if 'simul' in texto or 'simul' in href.lower():
            simuladores.append({'texto': enlace.get_text(strip=True), 'href': href})
            print(f"Encontrado: '{enlace.get_text(strip=True)}' -> {href}")
    
    # Buscar enlaces a grillas salariales
    grillas = []
    for enlace in enlaces:
        texto = enlace.get_text(strip=True).lower()
        href = enlace['href']
        
        if 'grilla' in texto or 'grilla' in href.lower() or 'salarial' in texto:
            grillas.append({'texto': enlace.get_text(strip=True), 'href': href})
            print(f"Grilla: '{enlace.get_text(strip=True)}' -> {href}")
    
    return simuladores, grillas


def extraer_datos_grilla_salarial(url_grilla):
    """Intenta extraer datos de una grilla salarial"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    print(f"\nIntentando extraer datos de: {url_grilla}")
    
    try:
        response = session.get(url_grilla)
        response.raise_for_status()
        
        # Verificar si es PDF
        if 'application/pdf' in response.headers.get('Content-Type', ''):
            print("Es un PDF. Se necesita PyPDF2 o pdfplumber para extraer datos.")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar tablas
        tablas = soup.find_all('table')
        print(f"Tablas encontradas: {len(tablas)}")
        
        for i, tabla in enumerate(tablas):
            print(f"\n--- Tabla {i+1} ---")
            filas = tabla.find_all('tr')
            print(f"Filas: {len(filas)}")
            
            # Mostrar primeras filas
            for j, fila in enumerate(filas[:5]):
                celdas = fila.find_all(['td', 'th'])
                valores = [c.get_text(strip=True) for c in celdas]
                print(f"  Fila {j}: {valores}")
        
        return soup
        
    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("INSPECCIÓN DEL SIMULADOR ADIUC")
    print("=" * 60)
    
    # Inspeccionar página principal
    inspeccionar_pagina()
    
    # Buscar enlaces
    buscar_enlace_simulador()
    
    # Inspeccionar el iframe del simulador
    print("\n" + "=" * 60)
    print("INSPECCIONANDO IFRAME DEL SIMULADOR")
    print("=" * 60)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    try:
        response = session.get("https://simusueldo.adiuc.org.ar")
        print(f"Status simusueldo.adiuc.org.ar: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Guardar HTML
            with open("datos/simusueldo_raw.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("HTML guardado en: datos/simusueldo_raw.html")
            
            # Buscar formularios
            forms = soup.find_all('form')
            print(f"\nFormularios encontrados: {len(forms)}")
            
            for i, form in enumerate(forms):
                print(f"\n--- Formulario {i+1} ---")
                print(f"Action: {form.get('action', 'N/A')}")
                print(f"Method: {form.get('method', 'N/A')}")
                
                inputs = form.find_all('input')
                selects = form.find_all('select')
                buttons = form.find_all('button')
                
                print(f"Inputs: {len(inputs)}")
                print(f"Selects: {len(selects)}")
                print(f"Buttons: {len(buttons)}")
                
                # Mostrar detalles de inputs
                for inp in inputs:
                    inp_type = inp.get('type', 'N/A')
                    inp_name = inp.get('name', 'N/A')
                    inp_id = inp.get('id', 'N/A')
                    inp_value = inp.get('value', 'N/A')
                    print(f"  Input: type={inp_type}, name={inp_name}, id={inp_id}, value={inp_value}")
                
                # Mostrar detalles de selects
                for select in selects:
                    print(f"\n  Select: name={select.get('name')}, id={select.get('id')}")
                    options = select.find_all('option')
                    print(f"  Opciones ({len(options)}):")
                    for opt in options[:15]:  # Mostrar primeras 15
                        print(f"    - {opt.get_text(strip=True)} (value={opt.get('value', '')})")
                    if len(options) > 15:
                        print(f"    ... y {len(options) - 15} más")
            
    except Exception as e:
        print(f"Error accediendo al iframe: {e}")
    
    print("\n" + "=" * 60)
    print("Instrucciones:")
    print("=" * 60)
    print("""
1. Revisar los archivos HTML guardados en 'datos/' para entender la estructura
    
2. El simulador está en un iframe de simusueldo.adiuc.org.ar
    
3. Alternativa: Extraer datos manualmente de las grillas salariales en PDF
   - Informes del Observatorio de Salario: 
     https://adiuc.org.ar/instituto-oscar-varsavsky/observatorio-de-salario-y-presupuesto/
    
4. Completar los datos en el script 'construye_profasis_historico.py'
    """)
