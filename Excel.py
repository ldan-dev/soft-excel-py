import pandas as pd
import re
from openpyxl import Workbook
import requests
import time

# Lista extendida de palabras clave
keywords = {
    "screw": ["screw", "bolt", "fastener", "stud", "pin", "machine screw", "cap screw"],
    "nut": ["nut", "locknut", "cap nut", "hex nut", "wing nut", "jam nut"],
    "washer": ["washer", "spacer", "flat washer", "lock washer", "seal washer"],
    "wheel": ["wheel", "caster", "pulley", "roller", "drive wheel", "idler wheel"],
    "bearing": ["bearing", "ball bearing", "roller bearing", "bushing", "race", "thrust bearing"],
    "box": ["box", "case", "container", "housing", "enclosure"],
    "bushing": ["bushing", "sleeve", "liner", "grommet", "spacer", "shock bushing"],
    "motor": ["motor", "servo", "actuator", "dc motor", "stepper motor", "gear motor"],
    "gear": ["gear", "gearbox", "gearwheel", "pinion", "spur gear", "bevel gear"],
    "arm": ["arm", "joint", "linkage", "lever", "actuator arm", "bracket"],
    "sensor": ["sensor", "accelerometer", "gyroscope", "encoder", "range sensor", "lidar"],
    "battery": ["battery", "cell", "power pack", "rechargeable", "battery pack"],
    "circuit": ["circuit", "pcb", "board", "controller", "esc", "switch", "connector"],
    "clamp": ["clamp", "bracket", "fastener", "clip", "holder", "mount"],
    "adapter": ["adapter", "fitting", "coupler", "converter", "socket", "attachment"],
    "hydraulic": ["hydraulic", "pneumatic", "fluid", "pressure", "cylinder", "hydraulic line"],
    "connector": ["connector", "plug", "jack", "coupling", "junction", "adapter"],
    "joint": ["joint", "hinge", "pivot", "link", "connection", "articulation"],
    "hose": ["hose", "pipe", "tubing", "conduit", "flexible hose", "hose pipe"],
    "piping": ["piping", "tube", "pipeline", "conduit", "plumbing", "channel"],
    "filter": ["filter", "strainer", "screen", "filtration", "separator", "filter element"],
    "magnetic": ["magnetic", "magnet", "attractor", "magnetic field", "magnetized", "magnetic separator"],
    "valve": ["valve", "control valve", "check valve", "relief valve", "solenoid valve"],
    "fitting": ["fitting", "coupler", "adapter", "connector", "joint", "socket"],
    "flow": ["flow", "flow meter", "flow sensor", "stream", "flux", "flow control"],
    "seal": ["seal", "gasket", "o-ring", "packing", "sealant", "sealing"],
    "regulator": ["regulator", "pressure regulator", "flow regulator", "controller", "control valve"],
    "pin": ["pin", "pasador", "dowel", "retaining pin", "locking pin"],
    "plug": ["plug", "enchufe", "connector", "socket", "power plug"],
    "hinge": ["hinge", "pivot", "articulation", "bracket", "door hinge"],
    "clip": ["clip", "retainer", "holder", "opresor", "fastener"],
    "nozzle": ["nozzle", "boquilla", "spout", "spray nozzle", "tip"],
    "cap": ["cap", "tapon", "cover", "lid", "end cap"]
}

def check_keywords(name):
    for component, synonyms in keywords.items():
        for synonym in synonyms:
            if re.search(rf"\b{synonym}\b", str(name), re.IGNORECASE):
                return True
    return False

def check_link(url, retries=3, delay=2):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    for _ in range(retries):
        try:
            response = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Error al verificar el enlace {url}: {e}")
            time.sleep(delay)  # Esperar un poco antes de intentar nuevamente
    return False

def process_excel(file_path):
    sheets = pd.read_excel(file_path, sheet_name=None, header=None)

    result = []

    for sheet_name, df in sheets.items():
        if len(df.columns) == 6:
            df.columns = ["codigo", "ref_name", "category", "name", "cantidad", "link"]
        else:
            raise ValueError("The number of columns in the DataFrame does not match the expected number.")

        for _, row in df.iterrows():
            name = row["name"]
            cantidad = row["cantidad"]
            link = row["link"]

            # Verificar coincidencias en el nombre con las palabras clave
            if check_keywords(name):
                print(f"Procesando Link: {link}")
                
                # Comprobar si el enlace está disponible
                if check_link(link):
                    # Ajustar cantidad según las reglas dadas
                    if cantidad > 100:
                        cantidad = cantidad // 4
                    elif cantidad > 20:
                        cantidad = cantidad // 2

                    result.append({
                        "codigo": row["codigo"],
                        "nombre": name,
                        "cantidad": cantidad,
                        "link": link,
                        "image": "Imagen no disponible"  
                    })
                else:
                    print(f"Enlace no válido: {link}")

    # Crear un archivo Excel de salida
    output_wb = Workbook()
    output_ws = output_wb.active
    output_ws.title = "Resultados"

    # Agregar encabezados de columnas
    output_ws.append(["Código", "Nombre", "Cantidad", "Link", "Imagen"])

    # Escribir los resultados en el archivo Excel
    for item in result:
        output_ws.append([item["codigo"], item["nombre"], item["cantidad"], item["link"], item["image"]])

    output_file = "Lista_Alix.xlsx"
    output_wb.save(output_file)
    return output_file

# Ejemplo de uso
output_file = process_excel('Lista.xlsx')
print(f"Archivo de salida generado: {output_file}")
