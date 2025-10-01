from google.cloud import vision
import io
import os

def prueba_ocr_simple(image_path):
    """Prueba mínima de OCR con una imagen"""
    try:
        # El cliente usará automáticamente la variable de entorno
        client = vision.ImageAnnotatorClient()
        
        # Cargar imagen
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        
        # Llamar a la API
        response = client.text_detection(image=image)
        texts = response.text_annotations
        
        if response.error.message:
            print(f"❌ Error de la API: {response.error.message}")
            return
        
        if texts:
            print("✅ ¡OCR FUNCIONA! Texto detectado:")
            print("=" * 50)
            print(texts[0].description)
            
            # Guardar en archivo para revisar
            with open('prueba_exitosa.txt', 'w', encoding='utf-8') as f:
                f.write(texts[0].description)
            print("📄 Texto guardado en 'prueba_exitosa.txt'")
        else:
            print("❌ No se detectó texto en la imagen")
            
    except Exception as e:
        print(f"❌ Error general: {e}")

# EJECUTAR PRUEBA
if __name__ == "__main__":
    # CAMBIA ESTA RUTA por la ruta a UNA imagen de prueba
    imagen_prueba = r"D:\Marcos\nutricion-UNIVALLE\imagenes_ocr\imagenEjemplo.jpeg"
    prueba_ocr_simple(imagen_prueba)