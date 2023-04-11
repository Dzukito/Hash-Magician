
import subprocess
import argparse
import hashlib
import os
import csv
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PySimpleGUI"])

# Verificar si los paquetes están instalados y, en caso contrario, instalarlos
try:
    __import__("PySimpleGUI")
except ImportError:
    install("PySimpleGUI")
import PySimpleGUI as sg




# Definir el diseño de la interfaz gráfica
icono="mago.ico"
sg.set_global_icon(icono)
layout = [
    [sg.Text('Seleccionar carpeta objetivo:'), sg.Input(key='-FOLDER-', readonly=True), sg.FolderBrowse()],
    [sg.Text('Seleccionar algoritmos hash a utilizar:')],
    [sg.Checkbox('MD5', default=True, key='-MD5-'), sg.Checkbox('SHA1', default=True, key='-SHA1-'), sg.Checkbox('SHA256', default=True, key='-SHA256-')],
    [sg.Checkbox('Mayúsculas', default=False, key='-UPPER-')],
    [sg.Button('Iniciar'), sg.Button('Cancelar')]
]

# Crear la ventana
window = sg.Window('Hash-Magician', layout)

# Loop principal para eventos de la interfaz gráfica
while True:
    event, values = window.read()
    
    # Si el usuario cierra la ventana o hace clic en 'Cancelar'
    if event == sg.WINDOW_CLOSED or event == 'Cancelar':
        break
    
    # Si el usuario hace clic en 'Iniciar', ademas corrobora que haya elegido una carpeta
    if event == 'Iniciar':
        folder_path = values['-FOLDER-']
        if folder_path=="" :
          sg.popup('No se ha seleccionado una carpeta. Por favor, seleccione una carpeta y vuelva a intentarlo.',title="Error")
          continue
  
        
        # Seleccionar los algoritmos hash a utilizar
        algoritmos_seleccionados = []
        if values['-MD5-']:
            algoritmos_seleccionados.append('md5')
        if values['-SHA1-']:
            algoritmos_seleccionados.append('sha1')
        if values['-SHA256-']:
            algoritmos_seleccionados.append('sha256')
        if not algoritmos_seleccionados:
            sg.popup('No se ha seleccionado ningun algoritmo. Por favor, seleccione una tipo de algoritmo y vuelva a intentarlo.',title="Error")
            continue
        
        # Configurar los argumentos
        parser = argparse.ArgumentParser(description='Obtener el hash de todos los archivos en una carpeta')
        parser.add_argument('-p', '--path', type=str, default=folder_path, help='Carpeta objetivo (por defecto: carpeta seleccionada)')
        parser.add_argument('-a', '--algoritmo', nargs='+', default=algoritmos_seleccionados, choices=['sha1', 'sha256', 'md5'], help='Algoritmo(s) hash a utilizar (por defecto: seleccionados)')
        args = parser.parse_args()

        # Calcular los hashes de los archivos
        hash_list = []
        def calcular_hashes(folder_path, file_list, hash_list):
            for file_name in file_list:
                file_path = os.path.join(folder_path, file_name)

                if os.path.isfile(file_path):
                    with open(file_path, 'rb') as file_current:
                        content = file_current.read()
           
                        md5_value = hashlib.md5(content).hexdigest()
                        sha1_value = hashlib.sha1(content).hexdigest()
                        sha256_value = hashlib.sha256(content).hexdigest()
                        if values['-UPPER-']:
                            md5_value = md5_value.upper()
                            sha1_value = sha1_value.upper()
                            sha256_value = sha256_value.upper()
                        hash_list.append({'filename': file_name, 'md5':md5_value, 'sha256':sha256_value, 'sha1': sha1_value})
                else:
                    calcular_hashes(file_path, os.listdir(file_path), hash_list)
            return hash_list

        hashes = calcular_hashes(folder_path, os.listdir(folder_path), hash_list)
        
        #Output
        # Crear la lista de nombres de campo a partir de los algoritmos seleccionados
        fieldnames = ['filename']
        if 'md5' in algoritmos_seleccionados:
            fieldnames.append('md5')
        if 'sha1' in algoritmos_seleccionados:
            fieldnames.append('sha1')
        if 'sha256' in algoritmos_seleccionados:
            fieldnames.append('sha256')

        # Escribir las filas en el archivo CSV solo con los valores correspondientes a los algoritmos seleccionados
        output_path = os.path.join(folder_path, 'hashes.csv').replace("\\", "/")
        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for fileWithHashes in hashes:
                row = {'filename': fileWithHashes['filename']}
                if 'md5' in algoritmos_seleccionados:
                    row['md5'] = fileWithHashes['md5']
                if 'sha1' in algoritmos_seleccionados:
                    row['sha1'] = fileWithHashes['sha1']
                if 'sha256' in algoritmos_seleccionados:
                    row['sha256'] = fileWithHashes['sha256']
                writer.writerow(row)

                
        sg.popup(f'Se ha creado el archivo CSV en: {output_path}',title="Ejecucion completada")
        
        

    
window.close()
