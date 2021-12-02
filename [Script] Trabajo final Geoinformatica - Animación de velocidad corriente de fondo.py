# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 16:39:46 2021

@author: usuario
"""
#Libreria para operar con carpetas y archivos
import os
#Libreria para trabajar con dataframes
import pandas as pd
#Libreria para trabajar con grillas
import xarray as xr
#Libreria para usar GMT en python
import pygmt
#Libreria para realizar animaciones
import cv2

#%%
#Indico la carpeta
path=r"D:\Onedrive_sebastian\OneDrive - gl.fcen.uba.ar\Doc\2.Materias y cursos\5. Geoinformatica\trabajo_final"
os.chdir(path)

#Determino la región
minlon,minlat,maxlon,maxlat=-57, -41.5, -53, -37
subset_region=[minlon, maxlon, minlat, maxlat]


#Cargo la gebco para dibujar posteriormente las curvas de nivel
gebco = pygmt.datasets.load_earth_relief(resolution="15s", region=subset_region)

#%%


#Leo el csv con los datos
model_csv = pd.read_csv("datos_velocidad_corriente_fondo_MCA.csv", sep=",")

#%%
# Crear carpeta donde guardar los gif

path_gif=path+"\\imagenes_trabajo_final\\"

try: 
    os.mkdir(path_gif) 
except OSError as error: 
    print(error)  
    
os.chdir(path_gif)

#%%


#Obtengo todas las fechas individuales
fechas=model_csv.time.unique()

#Genero un mapa por cada fecha
for i in range(0,len(fechas)):

    
    #Filtro por fechas los vectores de velocidad de uo y vo 
    
    vector_df=model_csv[model_csv["time"]==fechas[i]][["longitude", "latitude","uo","vo"]]
    
    
    #Filtro por fecha los datos de magntitud de velocidad de corriente (ws)
    model_df=model_csv[model_csv["time"]==fechas[i]][["longitude", "latitude","ws"]]
    
    
    #Para ws necesito una grilla, primero paso los datos a dataArray para que los lea PyGMT
    
    idx=pd.MultiIndex.from_arrays(arrays=[model_df.latitude,model_df.longitude],names=['Y','X'])
        
    s= pd.Series(data=model_df.ws.values, index=idx)
        
    model_data_array=xr.DataArray.from_series(s)
    
    #Grillo los datos de magnitud de ws
    
    model_sampled=pygmt.grdsample(model_data_array,spacing="0.3",interpolation="l")
    
    
    #genero figura
    fig = pygmt.Figure()
    pygmt.config(MAP_FRAME_AXES='WesN')
    
    #Grafico la magnitud de velocidad de la corriente ws
    
    pygmt.makecpt(cmap="roma", 
                  series=(0,20,0.01),
                  reverse=True
                  )
    
    fig.grdimage(
        grid=model_sampled,
        projection="M14c",
        cmap=True,
        dpi=720,
        frame=True,
        region=subset_region,
        transparency="20",
        nan_transparent=True)
    
    fig.colorbar(
        frame='+l"Velocidad (cm/s)"'
        )
    
    #Grafico los vectores de velocidad

    fig.velo(
        data=vector_df,
        #cmap=True,
        pen="1p,black",
        straight_line=True,
        frame=True,
        spec="e0.02/0.02/1",
        vector="0.3c+p1p+e+n20+a35+gblack"
    )
    
    #Curvas de nivel
        
    fig.grdcontour(
        grid=gebco,
        interval=1000,
        annotation=[1000,"f7p,Helvetica-Bold+a60+gwhite"],
        pen=["0.03c", 'black'],
        region=subset_region
    )
    
    #Recuadro superior con texto
    
    pen = "1.5p,black"
    font = "18p,Helvetica-Bold"
    fecha_ordenada=fechas[i][5:7]+"-"+fechas[i][0:4]
    fig.text(text=fecha_ordenada, x=-55, y=-37.3, fill="white",font=font,pen=pen)

    fig.text(position="TC", text="Velocidad de corriente oceánica de fondo entre 2015 y 2019", 
             offset="0/3.3c", 
             no_clip=True,
             font="15p,Helvetica-Bold"
             )
    fig.text(position="TC", text=" Datos mensuales obtenidos del modelo global 'GLORYS12V1'", 
             offset="0/2.6", 
             no_clip=True,
             font="11p,Helvetica"
             )
    fig.text(position="TC", text=" Procesados con Climate Data Operators (CDO) 2.0", 
             offset="0/2.1", 
             no_clip=True,
             font="11p,Helvetica"
             )
    
    fig.text(position="TC", text="Animación realizada con las librerias OpenCV y PyGMT en Python 3.8",
             offset="0/1.6", 
             no_clip=True,
             font="11p,Helvetica"
             )
    fig.text(position="TC", text=" Elaborado por Sebastián Principi para el curso Geoinformática Aplicada a la Cartografía Multitemática 2021  ",
             offset="0/1.1", 
             no_clip=True,
             font="11p,Helvetica"
             )
    
    
    #Escala y norte
    fig.basemap(
        rose="n0.92/0.94+w1.3c+f2",
        map_scale="n0.90/0.06+w40k+f+l"
        )
    
    #Ubicación
    with fig.inset(position="jTL+w3c+o0.2c", margin=0):
        fig.coast(
            region=subset_region,
            projection="G-54/-40/?",
            land="gray27",
            water="skyblue"
        )
        rectangle = [[subset_region[0], subset_region[2], subset_region[1], subset_region[3]]]
        fig.plot(data=rectangle, style="r+s", pen="2p,red")
    
    #Guardo las figuras
    
    fig.savefig(path_gif+str(i+1)+".png",dpi=80)
    print("**** "+ str(i+1) + "/" + str(len(fechas))+ " Listo!! ****")    

#Genero la animación

image_folder = path_gif
video_name = 'Mapa_corriente_fondo_curso_geoinformatica.avi'

images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
images = sorted(images, key=lambda x: int(os.path.splitext(x)[0]))

    
images=images[0:len(images)-1]
frame = cv2.imread(os.path.join(image_folder, images[0]))
height, width, layers = frame.shape

video = cv2.VideoWriter(video_name, 0, 5, (width,height))

for image in images:
    video.write(cv2.imread(os.path.join(image_folder, image)))

cv2.destroyAllWindows()
video.release()
