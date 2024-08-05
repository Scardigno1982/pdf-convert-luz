import os
import numpy as np
from shutil import move
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from sklearn.metrics.pairwise import cosine_similarity

# Cargar el modelo preentrenado VGG16
base_model = VGG16(weights='imagenet')
model = Model(inputs=base_model.input, outputs=base_model.get_layer('fc1').output)

def extract_features(img_path):
    try:
        img = image.load_img(img_path, target_size=(224, 224))
        img_data = image.img_to_array(img)
        img_data = np.expand_dims(img_data, axis=0)
        img_data = preprocess_input(img_data)
        features = model.predict(img_data)
        return features.flatten()
    except Exception as e:
        print(f"Error al procesar la imagen {img_path}: {e}")
        return None

def process_images_in_directory(directory):
    image_features = {}
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    
    for root, _, files in os.walk(directory):
        for img_name in files:
            if img_name.lower().endswith(valid_extensions):
                img_path = os.path.join(root, img_name)
                features = extract_features(img_path)
                if features is not None:
                    image_features[img_path] = features
    
    return image_features

def move_duplicates_to_similares(image_pairs, log_file):
    similar_dir = os.path.join(image_dir, 'similares')
    os.makedirs(similar_dir, exist_ok=True)
    moved_count = 0
    
    with open(log_file, 'a') as f:
        f.write("\nImágenes movidas a la carpeta 'similares':\n")
        for pair in image_pairs:
            original_image = pair[0]
            duplicates = pair[1:]
            for img_path in duplicates:
                img_name = os.path.basename(img_path)
                new_path = os.path.join(similar_dir, img_name)
                try:
                    move(img_path, new_path)
                    f.write(f"{img_path} => {new_path}\n")
                    moved_count += 1
                except FileNotFoundError:
                    print(f"No se pudo encontrar el archivo {img_path}")
                    f.write(f"No se pudo encontrar el archivo {img_path}\n")
                except Exception as e:
                    print(f"Error al mover el archivo {img_path}: {e}")
                    f.write(f"Error al mover el archivo {img_path}: {e}\n")
        
        f.write(f"\nCantidad de imágenes duplicadas movidas: {moved_count}\n")

# Directorio principal de imágenes
image_dir = r'C:\Users\sergi\Proyectos\imagenes-similares-python\originals'

# Procesar todas las imágenes en el directorio principal y sus subdirectorios
image_features = process_images_in_directory(image_dir)

# Verificar si se extrajeron características
if not image_features:
    print("No se pudieron extraer características de ninguna imagen.")
else:
    # Comparar características y detectar imágenes similares
    img_paths = list(image_features.keys())
    features_matrix = np.array(list(image_features.values()))
    similarity_matrix = cosine_similarity(features_matrix)

    # Umbral para considerar imágenes como similares
    threshold = 0.9

    # Detectar y contar imágenes similares
    image_pairs = []
    for i in range(len(img_paths)):
        pair = [img_paths[i]]
        for j in range(i + 1, len(img_paths)):
            if similarity_matrix[i, j] > threshold:
                pair.append(img_paths[j])
        if len(pair) > 1:  # Solo agregar grupos con más de una imagen
            image_pairs.append(pair)

    # Crear un log con la cantidad de imágenes duplicadas movidas
    log_file = 'image_similarity_log.txt'
    with open(log_file, 'w') as f:
        f.write("Imágenes duplicadas encontradas:\n")
        for pair in image_pairs:
            f.write(f"{', '.join(pair)}\n")
        f.write(f"\nCantidad de imágenes duplicadas encontradas: {len(image_pairs)}\n")

    # Mover imágenes duplicadas a la carpeta 'similares'
    move_duplicates_to_similares(image_pairs, log_file)

    print(f"Proceso completo. Verifica el archivo de log: {log_file}")
