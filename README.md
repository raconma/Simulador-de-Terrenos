# Simulador-de-Terrenos
Trabajo de fin de grado 2017-2018. <br />   
Para correr el programa hay que hacer uso del mandato plot_terreno
plot_terreno tiene tres argumentos (fichero,poly,color)
      fichero: el nombre del fichero entre comillas dobles, debe estar en la misma carpeta que el código,
               si está en otra carpeta se debe especificar el path completo.
               Estos ficheros deben descargarse de http://centrodedescargas.cnig.es/CentroDescargas/index.jsp en la parte de
               modelos digitales de terreno. Son archivos con extensión .asc , el programa acepta pasos de malla de 5m, 25m y 200m.
      poly: indica el número de triángulos de la simulación. Las tres opciones de menor a mayor 'lowpoly', '' ó 'highpoly'.
      color: colormaps del terreno, especificados en la documentación de matplotlib (https://matplotlib.org/users/colormaps.html).


Ejemplo de uso: plot_terreno("7picos.asc",'','magma') //// plot_terreno("D:\\naranjobulnes200",'lowpoly','CMRmap')     
