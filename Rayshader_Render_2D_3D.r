#####################################################################################
# GENERACIÓN DE MAPAS CON TEXTURA 2D Y 3D CON LA LIBRERÍA RAYSHADER                 #
#####################################################################################

#Rayshader se puede usar para dos propósitos: crear mapas sombreados y gráficos de visualización de datos en 3D. 

# Instalando la última versión desde Github:

#install.packages("devtools")
devtools::install_github("tylermorganwall/rayshader")
install.packages("processx")
install.packages("rayshader")

library(rayshader)
library(raster)
library(processx)

#Comenzar con un archivo de ejemplo:
loadzip = tempfile() 

download.file("https://tylermw.com/data/dem_01.tif.zip", loadzip)
localtif = raster::raster(unzip(loadzip, "dem_01.tif"))
unlink(loadzip)

#Convertimos los valores de cada ráster a una matriz extensa:
elmat = raster_to_matrix(localtif)

#Usaremos una textura incluida en la librería rayshader:
elmat %>%
  sphere_shade(texture = "desert") %>%
  plot_map()


#Usaremos el comando sphere_shade para cambiar la incidencia de los rayos solares:
elmat %>%
  sphere_shade(sunangle = 45, texture = "desert") %>%
  plot_map()


#Agregaremos una capa de superficie de agua usando detect water y add_water:
elmat %>%
  sphere_shade(texture = "desert") %>%
  add_water(detect_water(elmat), color = "desert") %>%
  plot_map()


#Ya que se cambió la indicencia de los rayos solares, ahora se agregará al cuerpo de agua:
elmat %>%
  sphere_shade(texture = "desert") %>%
  add_water(detect_water(elmat), color = "desert") %>%
  add_shadow(ray_shade(elmat), 0.5) %>%
  plot_map()


#And here we add an ambient occlusion shadow layer, which models 
#lighting from atmospheric scattering:

elmat %>%
  sphere_shade(texture = "desert") %>%
  add_water(detect_water(elmat), color = "desert") %>%
  add_shadow(ray_shade(elmat), 0.5) %>%
  add_shadow(ambient_shade(elmat), 0) %>%
  plot_map()


# Oclusión ambiental: Capa de sombra que regulará iluminación a partir de la dispersión atmosférica
elmat %>%
  sphere_shade(texture = "desert") %>%
  add_water(detect_water(elmat), color = "desert") %>%
  add_shadow(ray_shade(elmat), 0.5) %>%
  add_shadow(ambient_shade(elmat), 0) %>%
  plot_map()

#Rayshader también admite mapeo 3D al pasar un mapa de textura, ya sea externo o uno producido por rayshader 
#con la función plot_3d:
elmat %>%
  sphere_shade(texture = "desert") %>%
  add_water(detect_water(elmat), color = "desert") %>%
  add_shadow(ray_shade(elmat, zscale = 3), 0.5) %>%
  add_shadow(ambient_shade(elmat), 0) %>%
  plot_3d(elmat, zscale = 10, fov = 0, theta = 135, zoom = 0.75, phi = 45, windowsize = c(1000, 800))
Sys.sleep(0.2)
render_snapshot()


##Puede agregar una barra de escala, así como una brújula usando funciones render_scalebar y render_compass
render_camera(fov = 0, theta = 60, zoom = 0.75, phi = 45)
render_scalebar(limits=c(0, 5, 10),label_unit = "km",position = "W", y=50,
                scale_length = c(0.33,1))
render_compass(position = "E")
render_snapshot(clear=TRUE)

#También puede renderizar utilizando el trazador incorporado cuya fuente es la librería "rayrender", 
#Simplemente reemplace render_snapshot con render_highquality. 
#Cuando se llama a render_highquality, no es necesario calcular previamente las sombras con ninguna de 
#las funciones "_shade", por lo que si las tenemos, las removemos:
elmat %>%
  sphere_shade(texture = "desert") %>%
  add_water(detect_water(elmat), color = "desert") %>%
  plot_3d(elmat, zscale = 10, fov = 0, theta = 60, zoom = 0.75, phi = 45, windowsize = c(1000, 800))

render_scalebar(limits=c(0, 5, 10),label_unit = "km",position = "W", y=50,
                scale_length = c(0.33,1))

render_compass(position = "E")
Sys.sleep(0.2)
render_highquality(samples=200, scale_text_size = 24,clear=TRUE)
