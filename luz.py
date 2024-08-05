import PyPDF2
import json
import os
from pymongo import MongoClient

# Función para extraer texto del PDF usando PyPDF2
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n"  # Añadir un salto de línea para separar las páginas
    except Exception as e:
        print(f"Error al extraer texto del PDF {pdf_path}: {e}")
    return text

# Función para cargar el registro de archivos procesados
def load_processed_files(log_path):
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as log_file:
            return json.load(log_file)
    return []

# Función para actualizar el registro de archivos procesados
def update_processed_files(log_path, processed_files):
    with open(log_path, 'w', encoding='utf-8') as log_file:
        json.dump(processed_files, log_file, ensure_ascii=False, indent=4)

# Conexión a MongoDB
try:
    client = MongoClient('mongodb://192.168.3.99:27017/')
    db = client['luz']
    collection = db['luz']
    print("Conexión a MongoDB exitosa.")
except Exception as e:
    print(f"Error al conectar a MongoDB: {e}")

# Ruta del archivo de registro
log_path = 'procesados.json'

# Cargar el registro de archivos procesados
processed_files = load_processed_files(log_path)
print(f"Archivos procesados previamente: {processed_files}")

# Directorio de archivos PDF
pdf_directory = 'C:/Users/sergi/Downloads'

# Procesar archivos PDF
for filename in os.listdir(pdf_directory):
    if filename.lower().endswith('.pdf'):
        if filename not in processed_files:
            pdf_path = os.path.join(pdf_directory, filename)
            print(f"Procesando archivo: {pdf_path}")

            # Extraer texto del PDF
            pdf_text = extract_text_from_pdf(pdf_path)
            print(f"Texto extraído del archivo {filename}:\n{pdf_text[:100]}...")  # Mostrar los primeros 100 caracteres

            # Dividir el texto en líneas y numerarlas
            lines = pdf_text.split('\n')
            numbered_lines = [{"line_number": i + 1, "text": line.strip()} for i, line in enumerate(lines) if line.strip()]
            print(f"Número de líneas extraídas: {len(numbered_lines)}")

            # Verificar si se extrajo contenido
            if numbered_lines:  # Verifica si hay líneas extraídas
                # Guardar las líneas numeradas en la colección de MongoDB
                data_to_save = {
                    "filename": filename,
                    "lines": numbered_lines
                }
                try:
                    result = collection.insert_one(data_to_save)
                    print(f"Datos extraídos y guardados en MongoDB para el archivo {filename}, ID del documento: {result.inserted_id}")
                except Exception as e:
                    print(f"Error al guardar los datos en MongoDB: {e}")

                # Actualizar el registro de archivos procesados
                processed_files.append(filename)
                update_processed_files(log_path, processed_files)
                print(f"Registro de archivos procesados actualizado.")

            else:
                print(f"No se extrajo contenido del archivo {pdf_path}.")
        else:
            print(f"Archivo {filename} ya procesado.")
    else:
        print(f"Archivo {filename} no es un PDF.")
