import csv
import re
import os
from google.cloud import vision
import io

class DigitalizacionPractica:
    def __init__(self, credentials_path):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        self.client = vision.ImageAnnotatorClient()
    
    def extraer_datos_crudos(self, image_path):
        """Extrae datos crudos organizados por alimentos"""
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        response = self.client.document_text_detection(image=image)
        
        if not response.text_annotations:
            return []
        
        texto_completo = response.text_annotations[0].description
        return self.organizar_por_alimentos(texto_completo)
    
    def organizar_por_alimentos(self, texto_ocr):
        """Organiza el texto por alimentos detectados"""
        lineas = texto_ocr.split('\n')
        alimentos = []
        alimento_actual = {"lineas": []}
        
        for linea in lineas:
            linea = linea.strip()
            if not linea:
                continue
            
            # Detectar si es un nuevo alimento por código (C80, E1, D2, etc.)
            if re.match(r'^[A-Z]\d+', linea):
                if alimento_actual["lineas"]:  # Si ya tenemos un alimento, guardarlo
                    alimentos.append(alimento_actual)
                alimento_actual = {"lineas": [linea]}  # Nuevo alimento
            else:
                alimento_actual["lineas"].append(linea)
        
        # Añadir el último alimento
        if alimento_actual["lineas"]:
            alimentos.append(alimento_actual)
        
        return alimentos
    
    def extraer_id_nombre(self, lineas):
        """Intenta extraer ID y nombre de las primeras líneas"""
        if not lineas:
            return "DESCONOCIDO", "DESCONOCIDO"
        
        primera_linea = lineas[0]
        
        # Buscar patrón de código (C80, E1, etc.)
        match_codigo = re.match(r'^([A-Z]\d+)\s+(.+)', primera_linea)
        if match_codigo:
            return match_codigo.group(1), match_codigo.group(2)
        
        # Si no encuentra patrón, usar la primera línea como nombre
        return "DESCONOCIDO", primera_linea
    
    def extraer_valores_nutricionales(self, lineas):
        """Intenta extraer valores numéricos de las líneas"""
        todos_numeros = []
        for linea in lineas:
            # Buscar números (enteros y decimales)
            numeros = re.findall(r'-?\d+[,.]?\d*', linea.replace(',', '.'))
            todos_numeros.extend(numeros)
        
        # Devolver los primeros números encontrados (podrían ser energía, proteínas, etc.)
        return todos_numeros[:8]  # Primeros 8 valores
    
    def generar_archivo_validacion(self, alimentos, output_file):
        """Genera CSV para validación manual"""
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Encabezados
            writer.writerow([
                'ID_Detectado', 'Nombre_Detectado', 
                'Valores_Nutricionales', 'Datos_Completos',
                'ID_Corregido', 'Nombre_Corregido', 
                'Energia_kcal', 'Proteinas_g', 'Grasas_g', 'Carbohidratos_g',
                'Notas', 'Grupo_Alimenticio'
            ])
            
            for alimento in alimentos:
                lineas = alimento["lineas"]
                id_detectado, nombre_detectado = self.extraer_id_nombre(lineas)
                valores = self.extraer_valores_nutricionales(lineas)
                datos_completos = " | ".join(lineas)
                
                # Preparar valores nutricionales como string para revisión
                valores_str = " | ".join(valores) if valores else "NO_DETECTADO"
                
                writer.writerow([
                    id_detectado, nombre_detectado,
                    valores_str, datos_completos,
                    '', '', '', '', '', '', '', ''  # Columnas vacías para llenar manualmente
                ])
        
        print(f"✅ Archivo de validación generado: {output_file}")
        print(f"📝 Total de alimentos detectados: {len(alimentos)}")

# EJECUCIÓN INMEDIATA
if __name__ == "__main__":
    CREDENTIALS_PATH = "D:\\Marcos\\silicon-vista-448115-f6-409aecd9dfad.json"
    IMAGEN_PRUEBA = r"D:\Marcos\nutricion-UNIVALLE\imagenes_ocr\imagenEjemplo2.jpeg"
    
    print("🚀 INICIANDO EXTRACCIÓN PRÁCTICA...")
    digitalizador = DigitalizacionPractica(CREDENTIALS_PATH)
    
    print("📄 Extrayendo datos de la imagen...")
    alimentos = digitalizador.extraer_datos_crudos(IMAGEN_PRUEBA)
    
    print("💾 Generando archivo de validación...")
    digitalizador.generar_archivo_validacion(alimentos, 'validacion_manual.csv')
    
    print("\n🎯 ¡LISTO PARA VALIDACIÓN MANUAL!")
    print("==========================================")
    print("1. Abre 'validacion_manual.csv' en Excel o Google Sheets")
    print("2. Revisa y corrige las columnas 'ID_Corregido', 'Nombre_Corregido'")
    print("3. Llena los valores nutricionales en las columnas correspondientes")
    print("4. Guarda el archivo corregido")
    print("5. Luego lo importamos a Airtable")
    print(f"📊 Alimentos listos para validar: {len(alimentos)}")