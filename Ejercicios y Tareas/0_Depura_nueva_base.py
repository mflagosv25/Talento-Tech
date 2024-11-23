# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 16:16:53 2024

@author: mflagosv
"""

import pandas as pd
import re

# Definir el directorio de trabajo
import os
os.chdir("C:/OneDrive/OneDrive DNP/OneDrive - Departamento Nacional de Planeacion/Clic Participativo/Cientificos de datos/Revisión 2024/Formato_actualizacion_R")

# Leer el archivo Excel
formato_act = pd.read_excel("Instancias.xlsx")

# Filtrar filas donde 'Es_IRPC' es "Si"
formato_act = formato_act[formato_act['Es_IRPC'] == "Si"]

# Crear la columna 'Norma' concatenando otras columnas
formato_act['Norma'] = formato_act['Año'].astype(str) + " " + formato_act['Tipo'] + " " + formato_act['Numero'].astype(str) + " " + formato_act['Objeto']

# Seleccionar las columnas deseadas
columnas = ["Instancia", "Instancia_ID", "Año", "Tipo", "Numero", "Epigrafe", "Norma", "Objeto", 
            "Sector_administrativo", "Sector_poblacional", "Portalweb", "Estado", "Secretarias", 
            "tipo_secretaria", "Actores", "Alcances", "Funciones", "Categoria"]
formato_act = formato_act[columnas]

# Convertir texto a minúsculas y eliminar acentos
formato_act = formato_act.applymap(lambda x: str(x).lower() if isinstance(x, str) else x)

# Modificar columna 'Norma' para tener un formato específico
formato_act['Norma'] = formato_act['Tipo'] + " " + formato_act['Numero'].astype(str) + " de " + formato_act['Año'].astype(str) + " - " + formato_act['Objeto']

# Rellenar valores nulos en columnas específicas
formato_act['Secretarias'].fillna("Sin secretaria", inplace=True)
formato_act['tipo_secretaria'].fillna("Sin secretaria", inplace=True)
formato_act['Instancia_ID'] = formato_act['Instancia_ID'].str.upper()

# Aplicar formato de mayúsculas a columnas específicas
for col in ["Instancia", "Año", "Epigrafe", "Norma", "Objeto", "Sector_administrativo", "Sector_poblacional", 
            "Portalweb", "Estado", "Secretarias", "tipo_secretaria", "Actores", "Alcances", "Funciones", "Categoria"]:
    formato_act[col] = formato_act[col].str.capitalize()

# ------------------ Funciones ---------------------

# Filtrar las columnas necesarias y separar por el símbolo '-'
funciones = formato_act[["Instancia", "Instancia_ID", "Funciones"]].copy()
funciones['Funciones'] = funciones['Funciones'].str.split('-')
funciones = funciones.explode('Funciones')
funciones['Funciones'] = funciones['Funciones'].str.strip()
funciones.dropna(subset=['Funciones'], inplace=True)

# ------------------- Actores ----------------------

actores = formato_act[["Instancia", "Instancia_ID", "Actores"]].copy()
actores['Actores'] = actores['Actores'].str.lower()

# Reemplazar enumeraciones por ';' en la columna 'Actores'
for i in range(len(actores)):
    if ';' not in actores.at[i, 'Actores']:
        actores.at[i, 'Actores'] = re.sub(r'\b\d+\.', ';', actores.at[i, 'Actores'])
        actores.at[i, 'Actores'] = re.sub(r'\b(?:i{1,3}|iv|v{1,3}|ix|x{1,3})\.', ';', actores.at[i, 'Actores'])
        actores.at[i, 'Actores'] = re.sub(r'\b[a-z]\)', ';', actores.at[i, 'Actores'])
        actores.at[i, 'Actores'] = re.sub(r'\b[a-z]\.', ';', actores.at[i, 'Actores'])
        actores.at[i, 'Actores'] = re.sub(r'\b\d+\.\d+\b', ';', actores.at[i, 'Actores'])

# Limpiar y separar actores en filas individuales
actores['Actores'] = actores['Actores'].str.replace(';;', ';')
actores = actores.assign(Actores=actores['Actores'].str.split(';')).explode('Actores')
actores['Actores'] = actores['Actores'].str.strip()
actores = actores[~actores['Actores'].isna() & ~actores['Actores'].str.match(r'^[[:punct:][:space:]]*$')]

# Remover enumeraciones de 'Actores'
actores['Actores'] = actores['Actores'].str.replace(r'\d+\.\s*', '', regex=True)
actores['Actores'] = actores['Actores'].str.replace(r'\b[a-z]\)', '', regex=True)
actores['Actores'] = actores['Actores'].str.replace(r'\b[a-z]\.', ';', regex=True)
actores['Actores'] = actores['Actores'].str.replace(r'\b\d+\.\d+\.', '', regex=True)
actores['Actores'] = actores['Actores'].str.replace(r'\b(?:i{1,3}|iv|v{1,3}|ix|x{1,3})\.', '', regex=True)

# ----------------- Secretarias ----------------------

secretarias = formato_act[["Instancia", "Instancia_ID", "tipo_secretaria", "Secretarias"]].copy()
secretarias = secretarias.assign(Secretarias=secretarias['Secretarias'].str.split(',')).explode('Secretarias')
secretarias['Secretarias'] = secretarias['Secretarias'].str.strip()
secretarias['Secretarias'].fillna("Sin secretaria", inplace=True)
secretarias['tipo_secretaria'].fillna("Sin secretaria", inplace=True)

# ----------------- Guardar ----------------------

funciones.to_excel("funciones.xlsx", index=False)
actores.to_excel("actores.xlsx", index=False)
secretarias.to_excel("secretarias.xlsx", index=False)
formato_act.to_excel("Instancias.xlsx", index=False)
