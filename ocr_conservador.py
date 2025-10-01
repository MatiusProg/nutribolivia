from google.cloud import vision
import io
import os
import csv
from PIL import Image, ImageEnhance

class ExtraccionConservadora:
    def __init__(self, credentials_path):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        self.client = vision.ImageAnnotatorClient()
    
    def mejorar_imagen(self, ruta_imagen):
        """MEJORA LA IMAGEN PARA MEJOR OCR"""
        try:
            img = Image.open(ruta_imagen)
            if img.mode != 'L':
                img = img.convert('L')
            
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(3.0)
            
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(3.0)
            
            ruta_mejorada = ruta_imagen.replace('.jpg', '_MEJORADA.jpg')
            img.save(ruta_mejorada, dpi=(300, 300))
            return ruta_mejorada
        except:
            return ruta_imagen
    
    def extraer_texto_estructurado(self, image_path):
        """EXTRAE TEXTO Y SU POSICIÓN PARA ENTENDER LA ESTRUCTURA"""
        image_path_opt = self.mejorar_imagen(image_path)
        
        with io.open(image_path_opt, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        response = self.client.document_text_detection(image=image)
        
        if not response.text_annotations:
            return ""
        
        # Extraer texto con información de posición
        elementos = []
        for text in response.text_annotations[1:]:  # Saltar el primero que es todo el texto
            vertices = [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
            x_pos = sum(v[0] for v in vertices) / 4  # Posición X promedio
            y_pos = sum(v[1] for v in vertices) / 4  # Posición Y promedio
            
            elementos.append({
                'text': text.description,
                'x': x_pos,
                'y': y_pos
            })
        
        return elementos
    
    def organizar_por_filas(self, elementos):
        """ORGANIZA ELEMENTOS POR FILAS BASADO EN POSICIÓN Y"""
        # Ordenar por posición Y (filas)
        elementos.sort(key=lambda e: e['y'])
        
        filas = []
        fila_actual = []
        umbral_y = 20  # Margen para considerar misma fila
        
        for i, elemento in enumerate(elementos):
            if not fila_actual:
                fila_actual.append(elemento)
            else:
                # Verificar si está en la misma fila
                diff_y = abs(elemento['y'] - fila_actual[0]['y'])
                if diff_y < umbral_y:
                    fila_actual.append(elemento)
                else:
                    # Nueva fila
                    fila_actual.sort(key=lambda e: e['x'])  # Ordenar por X dentro de la fila
                    filas.append(fila_actual)
                    fila_actual = [elemento]
        
        if fila_actual:
            fila_actual.sort(key=lambda e: e['x'])
            filas.append(fila_actual)
        
        return filas
    
    def procesar_conservador(self, image_path):
        """PROCESO CONSERVADOR: EXTRAE Y ORGANIZA, PERO NO INTERPRETA"""
        print("🔍 Extrayendo texto con información estructural...")
        
        elementos = self.extraer_texto_estructurado(image_path)
        if not elementos:
            print("❌ No se pudieron extraer elementos")
            return
        
        filas = self.organizar_por_filas(elementos)
        
        # Guardar análisis estructural
        with open('analisis_estructural.txt', 'w', encoding='utf-8') as f:
            f.write("ANÁLISIS ESTRUCTURAL DE LA TABLA\n")
            f.write("=" * 50 + "\n")
            
            for i, fila in enumerate(filas):
                f.write(f"\nFILA {i+1}:\n")
                textos_fila = [elem['text'] for elem in fila]
                f.write(" | ".join(textos_fila) + "\n")
        
        print("✅ Análisis estructural guardado en: analisis_estructural.txt")
        
        # Crear CSV con datos crudos organizados
        with open('datos_crudos_organizados.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Fila', 'Columna', 'Texto', 'PosX', 'PosY'])
            
            for i, fila in enumerate(filas):
                for j, elemento in enumerate(fila):
                    writer.writerow([i+1, j+1, elemento['text'], elemento['x'], elemento['y']])
        
        print("💾 Datos crudos organizados en: datos_crudos_organizados.csv")
        
        return filas

# USO DEL SCRIPT CONSERVADOR
if __name__ == "__main__":
    CREDENTIALS_PATH = "D:\\Marcos\\silicon-vista-448115-f6-409aecd9dfad.json"
    IMAGEN_PRUEBA = r"D:\Marcos\nutricion-UNIVALLE\imagenes_ocr\imagenEjemplo.jpeg"
    
    extractor = ExtraccionConservadora(CREDENTIALS_PATH)
    resultado = extractor.procesar_conservador(IMAGEN_PRUEBA)
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Revisa 'analisis_estructural.txt' para ver cómo se organizó el texto")
    print("2. Revisa 'datos_crudos_organizados.csv' para ver la estructura por coordenadas")
    print("3. Con esta información, podemos crear un parser MÁS preciso")