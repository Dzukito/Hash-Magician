import argparse
import hashlib
import os
import csv
import PySimpleGUI as sg

# Definir el diseño de la interfaz gráfica
layout = [
    [sg.Text('Seleccionar carpeta objetivo:'), sg.Input(key='-FOLDER-', readonly=True), sg.FolderBrowse()],
    [sg.Text('Seleccionar algoritmos hash a utilizar:')],
    [sg.Checkbox('MD5', default=True, key='-MD5-'), sg.Checkbox('SHA1', default=True, key='-SHA1-'), sg.Checkbox('SHA256', default=True, key='-SHA256-')],
    [sg.Button('Iniciar'), sg.Button('Cancelar')]
]

# Crear la ventana
window = sg.Window('Calcular Hashes de Archivos', layout)

# Loop principal para eventos de la interfaz gráfica
while True:
    event, values = window.read()
    
    # Si el usuario cierra la ventana o hace clic en 'Cancelar'
    if event == sg.WINDOW_CLOSED or event == 'Cancelar':
        break
    
    # Si el usuario hace clic en 'Iniciar'
    if event == 'Iniciar':
        folder_path = values['-FOLDER-']
        
        # Seleccionar los algoritmos hash a utilizar
        algoritmos_seleccionados = []
        if values['-MD5-']:
            algoritmos_seleccionados.append('md5')
        if values['-SHA1-']:
            algoritmos_seleccionados.append('sha1')
        if values['-SHA256-']:
            algoritmos_seleccionados.append('sha256')
        
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
                        sha256_value = hashlib.sha256(content).hexdigest()
                        sha1_value = hashlib.sha1(content).hexdigest()
                        hash_list.append({'filename': file_name, 'md5':md5_value, 'sha256':sha256_value, 'sha1': sha1_value})
                else:
                    calcular_hashes(file_path, os.listdir(file_path), hash_list)
            return hash_list

        hashes = calcular_hashes(folder_path, os.listdir(folder_path), hash_list)
        
        # Mostrar los hashes en una tabla
        output = ">>--------------- Hashes ---------------------<<\n"
        output += '{:<30}{:<10}{:<40}{:<64}\n'.format('Archivo', 'MD5', 'SHA-1', 'SHA-256')
        for unHash in hashes:
            output += '{:<30}{:<10}{:<40}{:<64}\n'.format(unHash['filename'], unHash['md5'], unHash['sha1'], unHash['sha256'])

    	    # Escribir los hashes en un archivo CSV
    headings = ['Archivo', 'MD5', 'SHA-1', 'SHA-256']
    with open('hashes.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headings)
        for item in hashes:
            writer.writerow([item[h.lower()] for h in headings])
    
    # Mostrar el resultado de los hashes en una ventana de mensaje
    sg.popup_scrolled(output, title='Hashes', size=(100, 30))
    

    
window.close()
