#######################################################################
# DELIMITACIÓN DE CUENCAS USANDO LA LIBRERÍA                          # 
# PYSHEDS                                                             #       
#######################################################################

#Tutorial de instalación Pysheds: https://www.youtube.com/watch?v=bIrKF29oWIA&t=384s

#Importamos librerías a usar
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from pysheds.grid import Grid
import seaborn as sns
import warnings
import os
warnings.filterwarnings('ignore')

#Indicamos el directorio de trabajo:
os.chdir("C:\\Users\\Julio\\Documents\\EVENTOS\\UNSCH-Julio 2020\\Pysheds")

#Indicamos el nombre del archivo ráster
grid = Grid.from_raster('n30w100_con', data_name='dem')

#Configuramos espacio de gráfico
fig, ax = plt.subplots(figsize=(8,6))
fig.patch.set_alpha(0)

#Generamos gráfico de DEM
plt.imshow(grid.dem, extent=grid.extent, cmap='cubehelix', zorder=1)
plt.colorbar(label='Elevation (m)')
plt.grid(zorder=0)
plt.title('Digital elevation map')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.tight_layout()
plt.savefig('dem', bbox_inches='tight')

#Minnor slicing on borders to enhance colobars
elevDem=grid.dem[:-1,:-1]


#Correciones de zonas planas en DEM
#Las bajas pendientes de los cursos de agua, las áreas planas y las depresiones espurias en el DEM
#dificultan la  evaluación de la segmentación de cuencas y las capacidades de generación de la red
#de drenaje.

depressions = grid.detect_depressions('dem')
plt.imshow(depressions)
grid.fill_depressions(data='dem', out_name='dem_ndep')

flats = grid.detect_flats('dem_ndep')
plt.imshow(flats)
grid.resolve_flats('dem', out_name='dem_ndep_nflat')


#Indicamos los valores de dirección de flujo 
#(que se obtienen por defecto en algunos programas GIS)
#N    NE    E    SE    S    SW    W    NW
dirmap = (64,  128,  1,   2,    4,   8,    16,  32)

#Generamos y graficamos el ráster de dirección de flujo
grid.flowdir(data='dem_ndep_nflat', out_name='dir', dirmap=dirmap)

fig = plt.figure(figsize=(8,6))
fig.patch.set_alpha(0)

plt.imshow(grid.dir, extent=grid.extent, cmap='viridis', zorder=2)
boundaries = ([0] + sorted(list(dirmap)))
plt.colorbar(boundaries= boundaries,
             values=sorted(dirmap))
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Flow direction grid')
plt.grid(zorder=-1)
plt.tight_layout()
plt.savefig('flow_direction.png', bbox_inches='tight')


#También puede leerse un archivo ráster de dirección de flujo de otra fuente
#grid.read_raster('../data/n30w100_dir', data_name='dir')
#Con la carga reemplazaremos automáticamente el archivo de dirección de flujo
#Generado anteriormente


#Revisamos los valores en el ráster de dirección de flujo cargado
grid.dir
grid.dir.size

#Graficamos el ráster de dirección de flujo cargado
fig = plt.figure(figsize=(8,6))
fig.patch.set_alpha(0)

plt.imshow(grid.dir, extent=grid.extent, cmap='viridis', zorder=2)
boundaries = ([0] + sorted(list(dirmap)))
plt.colorbar(boundaries= boundaries,
             values=sorted(dirmap))
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Flow direction grid')
plt.grid(zorder=-1)
plt.tight_layout()

#DELIMITACIÓN DE LA CUENCA
#Especificamos la ubicación del punto de salida
x, y = -97.294167, 32.73750

#Delimitación
grid.catchment(data='dir', x=x, y=y, dirmap=dirmap, out_name='catch',
               recursionlimit=15000, xytype='label', nodata_out=0)


#Recortamos a la forma de la cuenca
grid.clip_to('catch')


# Visualización de la cuenca
catch = grid.view('catch', nodata=np.nan)

# Graficamos la cuenca
fig, ax = plt.subplots(figsize=(8,6))
fig.patch.set_alpha(0)

plt.grid('on', zorder=0)
im = ax.imshow(catch, extent=grid.extent, zorder=1, cmap='magma')
plt.colorbar(im, ax=ax, boundaries=boundaries, values=sorted(dirmap), label='Flow Direction')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Delineated Catchment')
plt.savefig('catchment.png', bbox_inches='tight')


#Si también se desea, se crea una función para adecuar todos los gráficos
def plotFigure(data, label):
    plt.figure(figsize=(12,10))
    plt.imshow(data, extent=grid.extent, cmap='terrain')
    plt.colorbar(label=label)
    plt.grid()


plotFigure(catch, 'Elevation (m)')
#Más colores para gráficos en:
#https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html

#Obtenemos y graficamos la acumulación de flujo en la cuenca
grid.accumulation(data='catch', dirmap=dirmap, out_name='acc')

fig, ax = plt.subplots(figsize=(8,6))
fig.patch.set_alpha(0)
plt.grid('on', zorder=0)
acc_img = np.where(grid.mask, grid.acc + 1, np.nan)
im = ax.imshow(acc_img, extent=grid.extent, zorder=2,
               cmap='cubehelix',
               norm=colors.LogNorm(1, grid.acc.max()))
plt.colorbar(im, ax=ax, label='Upstream Cells')
plt.title('Flow Accumulation')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.savefig('flow_accumulation.png', bbox_inches='tight')


#Obtenemos y graficamos un ráster de distancias hacia las celdas más remotas en la cuenca
grid.flow_distance(data='catch', x=x, y=y, dirmap=dirmap, out_name='dist',
                   xytype='label', nodata_out=np.nan)

fig, ax = plt.subplots(figsize=(8,6))
fig.patch.set_alpha(0)
plt.grid('on', zorder=0)
im = ax.imshow(grid.dist, extent=grid.extent, zorder=2,
               cmap='cubehelix_r')
plt.colorbar(im, ax=ax, label='Distance to outlet (cells)')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Flow Distance')
plt.savefig('flow_distance.png', bbox_inches='tight')


#Ahora obtenemos la red de drenaje de la cuenca
#Consideraremos el threshold (umbral) a 200 unidades del ráster
branches = grid.extract_river_network('catch', 'acc', threshold=200, dirmap=dirmap)

fig, ax = plt.subplots(figsize=(6.5,6.5))
plt.grid('on', zorder=0)
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('River network (>200 accumulation)')
plt.xlim(grid.bbox[0], grid.bbox[2])
plt.ylim(grid.bbox[1], grid.bbox[3])
ax.set_aspect('equal')

for branch in branches['features']:
    line = np.asarray(branch['geometry']['coordinates'])
    plt.plot(line[:, 0], line[:, 1])


#Ahora usaremos un umbral menor, a 50 unidades del ráster
branches = grid.extract_river_network('catch', 'acc', threshold=50, dirmap=dirmap)
fig, ax = plt.subplots(figsize=(6.5,6.5))

plt.grid('on', zorder=0)
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('River network (>50 accumulation)')
plt.xlim(grid.bbox[0], grid.bbox[2])
plt.ylim(grid.bbox[1], grid.bbox[3])
ax.set_aspect('equal')

for branch in branches['features']:
    line = np.asarray(branch['geometry']['coordinates'])
    plt.plot(line[:, 0], line[:, 1])

plt.savefig('river_network.png', bbox_inches='tight')


#Ahora usaremos un umbral menor, a 2 unidades del ráster
branches = grid.extract_river_network('catch', 'acc', threshold=2, dirmap=dirmap)
branches = grid.extract_river_network('catch', 'acc', threshold=2, dirmap=dirmap)
fig, ax = plt.subplots(figsize=(6.5,6.5))

plt.grid('on', zorder=0)
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('River network (>2 accumulation)')
plt.xlim(grid.bbox[0], grid.bbox[2])
plt.ylim(grid.bbox[1], grid.bbox[3])
ax.set_aspect('equal')

for branch in branches['features']:
    line = np.asarray(branch['geometry']['coordinates'])
    plt.plot(line[:, 0], line[:, 1])
