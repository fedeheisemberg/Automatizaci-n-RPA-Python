from pytube import Youtube
import pandas as pd
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

#Variables excel

file_path='enlaces_videos/enlaces.xlsx'
sheet_name='Hoja1'
column_name='Videos'

#Credenciales de google drive
directorio_crendenciales=''
id_folder=''

#Iniciar sesión en drive

def login():
    GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = directorio_crendenciales
    gauth=GoogleAuth()
    gauth.LocalCredentialsFile(directorio_crendenciales)

    if gauth.credentials is None:
        gauth.LocalWebserverAuth(port_numbers=[8092])
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    
    gauth.SaveCredentialesFile(directorio_crendenciales)
    credenciales=GoogleDrive(gauth)
    return credenciales

def main():
    #Leer los links del excel
    df=pd.read_excel(file_path,sheet_name=sheet_name)
    column_data=df[column_name]
    videos=column_data.values

    #Descargar videos de youtube y subirlo a drive

    for link_video in videos:
        #Descarga
        yt=Youtube(link_video)
        video=yt.streams.get_highest_resolution()
        video.download('./YT')

        #Subir
        subir_archivo(f'./YT/{video.title}.mp4',id_folder)

if __name__=='__main__':
    main()
