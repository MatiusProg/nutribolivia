import csv

def crear_plantilla_trabajo():
    """Crea plantilla optimizada para digitación manual"""
    
    campos = [
        'ID_Alimento', 'Nombre_Alimento', 'Grupo_Alimenticio',
        'Energia_kcal', 'Humedad_g', 'Proteinas_g', 'Grasas_g', 
        'Carbohidratos_g', 'FibraCruda_g', 'Ceniza_g',
        'Calcio_mg', 'Fosforo_mg', 'Hierro_mg', 'VitA_mcg',
        'Tiamina_mg', 'Riboflavina_mg', 'Niacina_mg', 'VitC_mg',
        'Estado_Validacion', 'Notas'
    ]
    
    with open('digitacion_manual.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(campos)
        
        # Ejemplos basados en tu imagen
        ejemplos = [
            ['C80', 'Toronja blanca sin membrana', 'Frutas', '44', '88.90', '0.56', '0.20', '10.03', '0.21', '0.31', '14.0', '20.0', '0.22', '0.0', '0.04', '0.06', '0.60', '36.50', 'Por validar', ''],
            ['C81', 'Tumbo', 'Frutas', '87', '83.20', '0.86', '0.53', '14.89', '6.46', '0.81', '12.0', '26.2', '0.70', '0.72', '0.03', '0.04', '0.51', '65.20', 'Por validar', ''],
            ['C82', 'Tuna variedad Amarilla', 'Frutas', '70', '82.45', '1.06', '0.16', '16.03', '6.32', '0.30', '34.0', '20.0', '0.50', '5.0', '0.03', '0.02', '0.30', '17.00', 'Por validar', '']
        ]
        
        for ejemplo in ejemplos:
            writer.writerow(ejemplo)
    
    print("✅ Plantilla creada: 'digitacion_manual.csv'")
    print("📋 Total de campos: 19")
    print("🎯 Ejemplos incluidos: 3")

# Crear la plantilla
crear_plantilla_trabajo()