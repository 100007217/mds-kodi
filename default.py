import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import sys
import os
import requests
import json
from urllib.parse import quote_plus, unquote_plus, urlencode

# URL base de la API de DigiStorage
BASE_URL = "https://storage.rcs-rds.ro/api/v2"

# Obtener detalles de configuración (correo electrónico y contraseña) desde las opciones del addon
addon = xbmcaddon.Addon()
email = addon.getSetting('email')
password = addon.getSetting('password')

# Autenticación para obtener el token
def get_auth_token():
    url = f"{BASE_URL}/token"
    headers = {
        "Accept": "*/*",
        "X-Koofr-Password": password,
        "X-Koofr-Email": email
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.headers.get("X-Koofr-Token")
    else:
        xbmcgui.Dialog().ok("Error", "Failed to authenticate")
        return None

# Listar los archivos y carpetas de un directorio en DigiStorage
def list_items(token, folder_path="/"):
    url = f"{BASE_URL}/files/0/{quote_plus(folder_path)}"
    headers = {
        "Authorization": f"Token {token}",
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        items = response.json()
        for item in items:
            list_item = xbmcgui.ListItem(label=item['name'])

            # Si es un directorio, permitir navegar dentro
            if item['type'] == 'folder':
                url = f"{sys.argv[0]}?action=list&path={quote_plus(item['fullPath'])}"
                is_folder = True
            else:
                # Si es un archivo, permitir reproducirlo si es multimedia
                url = f"{sys.argv[0]}?action=play&path={quote_plus(item['fullPath'])}"
                is_folder = False

            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=list_item, isFolder=is_folder)
    else:
        xbmcgui.Dialog().ok("Error", "Failed to list items")

    xbmcplugin.endOfDirectory(int(sys.argv[1]))

# Reproducir un archivo multimedia desde DigiStorage
def play_item(token, file_path):
    url = f"{BASE_URL}/files/0/{quote_plus(file_path)}?dl=1"
    headers = {
        "Authorization": f"Token {token}"
    }
    
    # Crear un objeto ListItem para Kodi
    play_item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=play_item)

# Controlar las acciones del usuario (navegar o reproducir)
def router(paramstring):
    params = dict(arg.split('=') for arg in paramstring[1:].split('&'))
    
    token = get_auth_token()

    if not token:
        return

    if params.get('action') == 'list':
        list_items(token, unquote_plus(params['path']))
    elif params.get('action') == 'play':
        play_item(token, unquote_plus(params['path']))
    else:
        list_items(token)

# Inicializar el addon
if __name__ == '__main__':
    router(sys.argv[2])
