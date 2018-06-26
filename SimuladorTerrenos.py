from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import random
import matplotlib.tri as mtri
import numpy as np
from scipy.spatial import Delaunay
import math


def lectura_fichero(fichero):
    numbers_float = []

    with open(fichero) as f:
        COLUMNAS = int(next(f).split()[1])
        FILAS = int(next(f).split()[1])
        next(f)
        next(f)
        ESPACIADO = int(next(f).split()[1])
        next(f)
        for line in f:
            numbers_str = line.split()
            if(len(numbers_str)==1):
                break
            numbers_float.append([float(x) for x in numbers_str])

    """alturas son todas las filas del fichero seguidas"""
    alturas = [y for x in numbers_float for y in x]
    return alturas,FILAS,COLUMNAS,ESPACIADO


def plot_terreno(fichero,poly,color):
    npoly,vueltas = 0,0
    if(poly == 'lowpoly'):
        npoly = 500
        vueltas = 10
    elif(poly == 'highpoly'):
        npoly = 20000
        vueltas = 100
    else:
        npoly = 5000
        vueltas = 100
    alturas, filas, columnas, espaciado = lectura_fichero(fichero)[0],lectura_fichero(fichero)[1],lectura_fichero(fichero)[2],lectura_fichero(fichero)[3]     
    altura_punto_invisible = 0
    if(espaciado == 5):
        altura_punto_invisible = 2500
    elif(espaciado == 25):
        altura_punto_invisible = 2000
    elif(espaciado == 200):
        altura_punto_invisible = 10000
    x,kx = [0]*columnas,0
    y,ky = [0]*filas,0    
    for xi in range(columnas):
        x[xi]=kx
        kx+=espaciado
    for yi in range(filas):
        y[yi]=ky
        ky+=espaciado
        
    """
    x es una lista [0,..,ColumnaMax*espaciado,0,..,ColumnaMax*espaciado,..]
    con saltos entre números de tamaño = (espaciado) y nº de columnas = (columnas*filas)
    """
    
    x_original = x*filas

    """
    y es una lista [0,..,0,espaciado,..,espaciado,..,FilaMax*espaciado,..,FilaMax*espaciado]
    """
    
    y_original=sorted(y*columnas)


    """alturas son todas las alturas en fila en una misma lista"""
    z_original = alturas
    
    """matriz con todas las alturas para poder consultar"""
    matriz_alturas = np.reshape(z_original,(filas,columnas))
    
    acortar = acortar_terreno(x_original,y_original,z_original,npoly)

    x,y,z = acortar[0],acortar[1],acortar[2]
    
    """paso a array numpy para triangular"""
    x,y,z = np.array(x),np.array(y),np.array(z)
    #print(y_original)
    
    """veces que se miran triangulos aleatorios"""
    for h in range(vueltas):
        triang = Delaunay(np.array([x,y]).T,False,True)
        terreno = actualizar_terreno(triang,x,y,z,500,matriz_alturas,filas,columnas,espaciado,200)
        x,y,z=terreno[0],terreno[1],terreno[2]
    triang = Delaunay(np.array([x,y]).T,False,True)
    
    """pintar"""
    fig = plt.figure(figsize=plt.figaspect(0.3))
    ax = fig.add_subplot(111,projection='3d')
    
    #z=np.zeros(len(x))
    #ISLA: vmin = -700 queda bien
    ax.plot_trisurf(x, y, z, triangles=triang.simplices, cmap=color, vmin = -700)

    #ax.plot_trisurf(y, x, z)
    #ax.plot_wireframe(x, y, z)
    ax.scatter(1, 1, altura_punto_invisible, c='whitesmoke')
    plt.show()
    print(len(x),len(y),len(z))


"""

triangularTerreno: triangula y después coge triángulos aleatorios calcula su centro y 
comprueba si la altura se aleja mucho (la compara con Epsilon)
nRandom es el número de triángulos a mirar
epsilon es el valor para comprobar si añades el punto

"""

def actualizar_terreno(triang,x,y,z,nRandom,matriz_alturas,filas,columnas,espaciado,epsilon):
    """El True es para poder añadir puntos"""

    simpl = triang.simplices
    triangulos_editar = []
    
    for i in range(nRandom):
        triangulos_editar.append(random.randint(0,x.size-1))
       
    for j in range(len(triangulos_editar)):
        """miro uno a uno los triángulos, calculo baricentro y miro en la matriz de alturas a cual corresponde"""
        tri_actual = simpl[triangulos_editar[j]]
        
        puntos_triangulo = [triang.points[tri_actual[0]],triang.points[tri_actual[1]],triang.points[tri_actual[2]]]
        baricentro = (puntos_triangulo[0]+puntos_triangulo[1]+puntos_triangulo[2])/3
        
        """la matriz de alturas no tiene en cuenta el espaciado"""
        altura_baricentro_en_matriz_alturas = encontrar_altura(int(baricentro[1]/espaciado),int(baricentro[0]/espaciado),matriz_alturas)
        altura_coplanar_baricentro = (encontrar_altura(puntos_triangulo[0][1]/espaciado,puntos_triangulo[0][0]/espaciado,matriz_alturas)+encontrar_altura(puntos_triangulo[1][1]/espaciado,puntos_triangulo[1][0]/espaciado,matriz_alturas)+encontrar_altura(puntos_triangulo[2][1]/espaciado,puntos_triangulo[2][0]/espaciado,matriz_alturas))/3
        b1 = np.append(baricentro,altura_coplanar_baricentro)
        b2 = np.append(baricentro,altura_baricentro_en_matriz_alturas)   
        
        distancia = math.sqrt(abs(b1[0]**2-b2[0]**2)+abs(b1[1]**2-b2[1]**2)+abs(b1[2]**2-b2[2]**2))
        
        """si el baricentro es reseñable lo añado
        si no, cojo un punto aleatorio del triángulo y miro si su vecinos son casi coplanarios para eliminarlo
        COMPROBAR"""
        if(distancia>200):
            x = np.append(x,b2[0])
            y = np.append(y,b2[1])
            z = np.append(z,b2[2])
     
        else:
            """cojo el índice de un punto aleatorio del triángulo actual"""
            ind_punto_coplanario = tri_actual[random.randint(0,2)]
            indice_vecinos = find_neighbors(ind_punto_coplanario,triang)
            if(len(indice_vecinos) < 3):
                continue
            else:
                A,B,C = triang.points[indice_vecinos[0]],triang.points[indice_vecinos[1]],triang.points[indice_vecinos[2]]
                punto_central = triang.points[ind_punto_coplanario]
                alturaA,alturaB,alturaC,alturaD = encontrar_altura(A[1]/espaciado,A[0]/espaciado,matriz_alturas),encontrar_altura(B[1]/espaciado,B[0]/espaciado,matriz_alturas),encontrar_altura(C[1]/espaciado,C[0]/espaciado,matriz_alturas),encontrar_altura(punto_central[1]/espaciado,punto_central[0]/espaciado,matriz_alturas)
                A,B,C,punto_central = np.append(A,alturaA),np.append(B,alturaB),np.append(C,alturaC),np.append(punto_central,alturaD)
                altura_tetraedro = calcular_altura(A,B,C,punto_central)
                """COMPROBAR"""
                if(altura_tetraedro < 20):
                    xyz = borrar_punto_de_listas(punto_central,x,y,z)
                    x,y,z = xyz[0],xyz[1],xyz[2]           
    return x,y,z


def acortar_terreno(x,y,z,n):
    """
    acortar_terreno coge sólo un número pequeño de puntos para pintar el terreno
    x,y,z las de nube de puntos y n el número de puntos que quiero
    """
    puntos=[]
    x2,y2,z2 = [],[],[]
    for i in range(n):
        puntos.append(random.randint(0,len(x)-1))
    puntos = sorted(puntos)
    """cada z[n] corresponde exactamente a un x[n] y un y[n]"""
    for j in range(n):
        x2.append(x[puntos[j]])
        y2.append(y[puntos[j]])
        z2.append(z[puntos[j]])
    return x2,y2,z2

    
def encontrar_altura(x,y,matriz_alturas):
    """Busca la altura correspondiente en la matriz de alturas global"""
    return matriz_alturas[int(x)][int(y)]

def calcular_altura(A,B,C,punto_central):
    """Calcula la altura de un poliedro"""
    v = calcular_volumen(A,B,C,punto_central)
    area_base = calcular_area(A,B,C)
    if(area_base == 0):
        return 99999
    return 6*v/area_base

def calcular_area(A,B,C):
    """Calcula el área de un poligono"""    
    return math.fabs(((B[0]-A[0])*(C[1]-A[1])-(C[0]-A[0])*(B[1]-A[1]))/2)
    
def calcular_volumen(A,B,C,punto_central):
    """Calcula el volumen de un poliedro mediante un determinante"""
    a = np.array([[1,1,1,1],[A[0],B[0],C[0],punto_central[0]],[A[1],B[1],C[1],punto_central[1]],[A[2],B[2],C[2],punto_central[2]]])
    #a = np.array([[1,1,1,1],[A[0],B[0],C[0],punto_central[0]],[A[1],B[1],C[1],punto_central[1]],[A[0]**2+A[1]**2,B[0]**2+B[1]**2, C[0]**2+C[1]**2,punto_central[0]**2+punto_central[1]**2]])
    return math.fabs(np.linalg.det(a)/6)

def encontrar_punto_en_listas(punto,x,y,z):
    """Busca el punto en las listas globales xyz"""
    pos = -1
    for i in range(len(x)):
        if(x[i] == punto[0] and y[i] == punto[1] and z[i] == punto[2]):
            pos = i
            break
    return pos
            
def borrar_punto_de_listas(punto,x,y,z):
    """Borra el punto de las listas globales xyz"""
    pos = encontrar_punto_en_listas(punto,x,y,z)
    if(pos != -1):
        x,y,z = np.delete(x,pos),np.delete(y,pos),np.delete(z,pos)
    return x,y,z

"""stackoverflow: https://stackoverflow.com/questions/12374781/how-to-find-all-neighbors-of-a-given-point-in-a-delaunay-triangulation-using-sci"""
def find_neighbors(pindex, triang):
    """Fan del vertice"""
    return triang.vertex_neighbor_vertices[1][triang.vertex_neighbor_vertices[0][pindex]:triang.vertex_neighbor_vertices[0][pindex+1]]


"""
plot_terreno("fichero", 'lowpoly' o 'highpoly' o '_____' = caso neutral,color)
colores por ejemplo = 'magma', 'terrain', 'gist_earth', 'gist_ncar', 'gnuplot', 'gnuplot2', 'nipy_spectral', 'CMRmap' 
"""

plot_terreno("D:\\ronda5.asc",'lowpoly','magma')
