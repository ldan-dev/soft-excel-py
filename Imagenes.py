import os
import requests
from bs4 import BeautifulSoup
from zipfile import ZipFile
import time

# Función para extraer la primera imagen de una página web
def extract_first_image_from_url(url):
    try:
        # Agregar un User-Agent en los encabezados
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Analizar el HTML de la página
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontrar la etiqueta de imagen con itemprop="image"
        img_tag = soup.find('img', itemprop='image')
        if img_tag and 'src' in img_tag.attrs:
            return img_tag['src']
        else:
            print(f'No se encontró imagen con itemprop="image" en {url}')
            return None
    except Exception as e:
        print(f'Error al acceder a {url}: {e}')
        return None

# Leer los enlaces desde el archivo de texto
with open('links.txt', 'r') as file:
    urls = [line.strip() for line in file.readlines()]

# Directorio donde se guardarán las imágenes
image_dir = 'images'
os.makedirs(image_dir, exist_ok=True)

# Descargar las imágenes
image_count = 498
for idx, url in enumerate(urls):
    print(f'Descargando imagen de: {url}')
    img_url = extract_first_image_from_url(url)
    
    if img_url:
        try:
            # Asegurarse de que el enlace de la imagen sea completo
            if img_url.startswith('//'):
                img_url = 'https:' + img_url  # Agregar el protocolo HTTPS
            elif not img_url.startswith('http'):
                img_url = requests.compat.urljoin(url, img_url)

            # Descargar la imagen
            response = requests.get(img_url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()  # Lanza un error si la descarga falla

            # Guardar la imagen en un archivo numerado
            image_path = os.path.join(image_dir, f'image_{image_count + 1}.jpg')
            with open(image_path, 'wb') as img_file:
                img_file.write(response.content)
            print(f'Descargada: {image_path}')
            image_count += 1
            
            # Esperar un segundo entre descargas para evitar bloqueos
            time.sleep(1)
            
        except Exception as e:
            print(f'Error al descargar la imagen {img_url}: {e}')

# Verificar si se descargaron imágenes antes de crear el archivo ZIP
if image_count > 0:
    # Crear un archivo ZIP
    zip_file_name = 'images_package.zip'
    with ZipFile(zip_file_name, 'w') as zip_file:
        for filename in os.listdir(image_dir):
            zip_file.write(os.path.join(image_dir, filename), arcname=filename)

    print(f'Imágenes guardadas en {zip_file_name}')
else:
    print('No se descargaron imágenes. El archivo ZIP no se creó.')
