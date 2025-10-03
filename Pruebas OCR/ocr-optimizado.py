from google.cloud import vision
import io
import re
import pandas as pd
from PIL import Image, ImageEnhance, ImageFilter
import os

class OCRNutriBoliviaOptimizado:
    def __init__(self, credentials_path):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        self.client = vision.ImageAnnotatorClient()
    
    def mejorar_imagen(self, ruta_imagen):
        """MEJORA LA CALIDAD DE IMAGEN ANTES DEL OCR"""
        try:
            img = Image.open(ruta_imagen)
            
            # Convertir a escala de grises (mejor para texto)
            if img.mode != 'L':
                img = img.convert('L')
            
            # Mejorar contraste
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.5)  # Más contraste
            
            # Mejorar nitidez
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(3.0)
            
            # Mejorar brillo
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.1)
            
            # Guardar imagen mejorada
            ruta_mejorada = ruta_imagen.replace('.jpg', '_OPTIMIZADA.jpg')
            img.save(ruta_mejorada, dpi=(300, 300))
            print(f"✅ Imagen optimizada guardada: {ruta_mejorada}")
            return ruta_mejorada
            
        except Exception as e:
            print(f"⚠️ No se pudo optimizar imagen: {e}")
            return ruta_imagen
    
    def ocr_optimizado(self, image_path):
        """OCR ESPECIALIZADO PARA TABLAS NUTRICIONALES"""
        # Primero mejorar la imagen
        image_path_opt = self.mejorar_imagen(image_path)
        
        with io.open(image_path_opt, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        
        # CONFIGURACIÓN AVANZADA para documentos
        image_context = vision.ImageContext(
            language_hints=["es"],  # Idioma español
        )
        
        # Usar document_text_detection (mejor para tablas)
        response = self.client.document_text_detection(
            image=image, 
            image_context=image_context
        )
        
        if response.error.message:
            print(f"❌ Error API: {response.error.message}")
            return ""
        
        return response.full_text_annotation.text if response.text_annotations else ""
    
    def parser_inteligente_tabla4(self, texto_ocr):
        """PARSER INTELIGENTE ESPECÍFICO PARA TABLA 4"""
        lineas = texto_ocr.split('\n')
        registros = []
        registro_actual = {}
        
        print("🔍 Analizando estructura del texto OCR...")
        
        for i, linea in enumerate(lineas):
            linea = linea.strip()
            if not linea:
                continue
            
            # 1. DETECTAR CÓDIGO (C60, E1, D2, etc.)
            codigo_match = re.match(r'^[A-Z]\d+$', linea)
            if codigo_match:
                if registro_actual and 'ID_Alimento' in registro_actual:
                    registros.append(registro_actual)
                registro_actual = {'ID_Alimento': linea}
                print(f"  📍 Encontrado código: {linea}")
                continue
            
            # 2. DETECTAR NOMBRE DE ALIMENTO (después del código)
            if (registro_actual and 
                'ID_Alimento' in registro_actual and 
                'Nombre_Alimento' not in registro_actual and
                len(linea) > 2 and
                not re.match(r'^\d', linea) and  # No empieza con número
                not re.search(r'\d\.\d', linea)):  # No contiene números con punto
                
                # Filtrar líneas que son claramente valores numéricos
                if not any(palabra in linea.lower() for palabra in ['kcal', 'g', 'mg', 'μg']):
                    registro_actual['Nombre_Alimento'] = linea
                    print(f"  🍎 Nombre detectado: {linea}")
                    continue
            
            # 3. EXTRAER VALORES NUMÉRICOS (la parte más importante)
            if registro_actual and 'ID_Alimento' in registro_actual:
                # Buscar secuencias de números (mejorado)
                numeros = re.findall(r'-?\d+[,.]?\d*', linea.replace(',', '.'))
                
                if len(numeros) >= 5:  # Si hay varios números, probablemente sean valores nutricionales
                    print(f"  🔢 Línea con valores: {linea}")
                    print(f"     Números detectados: {numeros}")
                    
                    # ASIGNACIÓN INTELIGENTE basada en posición
                    try:
                        if 'Energia_kcal' not in registro_actual and len(numeros) > 0:
                            registro_actual['Energia_kcal'] = float(numeros[0])
                        
                        if 'Humedad_g' not in registro_actual and len(numeros) > 1:
                            registro_actual['Humedad_g'] = float(numeros[1])
                            
                        if 'Proteinas_g' not in registro_actual and len(numeros) > 2:
                            registro_actual['Proteinas_g'] = float(numeros[2])
                            
                        # Continuar con otros campos...
                        
                    except ValueError as e:
                        print(f"     ⚠️ Error convirtiendo números: {e}")
        
        # Añadir último registro
        if registro_actual and 'ID_Alimento' in registro_actual:
            registros.append(registro_actual)
            
        print(f"✅ Parser completado. Registros encontrados: {len(registros)}")
        return registros
    
    def procesar_imagen_completa(self, image_path):
        """PROCESO COMPLETO PARA UNA IMAGEN"""
        print(f"\n🚀 PROCESANDO: {os.path.basename(image_path)}")
        print("=" * 50)
        
        # Paso 1: OCR optimizado
        texto_ocr = self.ocr_optimizado(image_path)
        
        if not texto_ocr:
            print("❌ No se pudo extraer texto")
            return []
        
        # Guardar OCR crudo para análisis
        nombre_base = os.path.splitext(os.path.basename(image_path))[0]
        with open(f'ocr_crudo_{nombre_base}.txt', 'w', encoding='utf-8') as f:
            f.write(texto_ocr)
        print(f"📄 OCR crudo guardado: ocr_crudo_{nombre_base}.txt")
        
        # Paso 2: Parser inteligente
        registros = self.parser_inteligente_tabla4(texto_ocr)
        
        # Paso 3: Mostrar resultados
        for i, registro in enumerate(registros):
            print(f"\n📋 Registro {i+1}:")
            for key, value in registro.items():
                print(f"   {key}: {value}")
        
        return registros

# USO DEL SCRIPT OPTIMIZADO
if __name__ == "__main__":
    # CONFIGURAR ESTAS RUTAS
    CREDENTIALS_PATH = "D:\\Marcos\\silicon-vista-448115-f6-409aecd9dfad.json"
    IMAGEN_PRUEBA = r"D:\Marcos\nutricion-UNIVALLE\imagenes_ocr\imagenEjemplo2.jpeg"
    
    # Crear procesador
    procesador = OCRNutriBoliviaOptimizado(CREDENTIALS_PATH)
    
    # Procesar imagen
    resultados = procesador.procesar_imagen_completa(IMAGEN_PRUEBA)
    
    # Guardar resultados en CSV
    if resultados:
        df = pd.DataFrame(resultados)
        df.to_csv('resultados_optimizados.csv', index=False, encoding='utf-8')
        print(f"\n🎉 ¡PROCESO COMPLETADO!")
        print(f"📊 Resultados guardados en: resultados_optimizados.csv")
        print(f"📝 Total de alimentos digitalizados: {len(resultados)}")