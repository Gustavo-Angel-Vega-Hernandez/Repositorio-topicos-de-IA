import random
import time
from collections import deque

def Funcion_de_penalizacion (vector):
    numero_de_choques = 0
    
    #El objetivo de este bucle es comparar cada reina con todas las demas sin compararse con ella misma 
    for i in range(8):
        for j in range(i + 1, 8):
            if(abs(i - j) == abs(vector[i] - vector[j])):
                numero_de_choques += 1   
    return numero_de_choques

def Funcion_Generar_Vecinos(vecino):
    vecindario = []
    
    #Genera vecinos intercambiando cada par de posiciones i y j 
    for i in range(8):
        for j in range(i + 1, 8):
            Nuevo_Vecino = vecino.copy()
            Nuevo_Vecino[i], Nuevo_Vecino[j] = Nuevo_Vecino[j], Nuevo_Vecino[i]

            costo = Funcion_de_penalizacion(Nuevo_Vecino)
            
            #guarda el movimiento que se hizo para ingresarlo a lista tabu
            swap = tuple(sorted([Nuevo_Vecino[i], Nuevo_Vecino[j]]))
            
            vecindario.append((Nuevo_Vecino, costo, swap))    
    return vecindario
      
def Cambiar_Estado_Actual(vecindario, lista_tabu, Criterio_aspiracion):
    
    #se ordena el vecindario por costo
    vecindario.sort(key=lambda X: X[1])
    
    for candidato in vecindario:
        costo = candidato[1]
        swap = candidato[2]
        
        if (swap not in lista_tabu) or (costo < Criterio_aspiracion):
            return candidato
    return vecindario[0]   

def Dibujar_tablero(vector):
    for fila in range(8):
        linea = ""
        for columna in range(8):
            if vector[fila] == columna:
                linea += "[Q]"
            else:
                linea +="[ ]"
        print(linea)       

def main ():
    Iteracion = 0
    Iteracion_Maxima = 100
    
    #Genera un Arreglo aleatorio con valores del 0 al 7
    Estado_Actual = random.sample(range(8), 8)
    #Tendecia tabú de 5 en este caso usamos una estructura de datos Tipo FIFO con un tamaño maximo de 5 ahorrando la logica de controlar la
    #salida de la lista tabu ya que salen automaticamente 
    lista_tabu = deque(maxlen = 5)

    Mejor_Estado_Global = Estado_Actual.copy()
    
    #Se aplica la funcion de costo al primer Estadi para obtener un criterio a mejorar (Criterio de aspiracion)
    Criterio_aspiracion = Funcion_de_penalizacion(Estado_Actual)
    print(f"Estado Inicial: {Estado_Actual} con {Criterio_aspiracion} choques.")
    print()
    print("****Tablero Inicial****")
    print()
    Dibujar_tablero(Estado_Actual)

    tiempo_inicio = time.perf_counter()

    #Se definen las codiciones para que el blucle siga iterando
    #1. Que no se encuentre una solucion: El criterio de aspiracion sea mayor que cero
    #2. Que no se alcance el limite de iteraciones
    while Criterio_aspiracion > 0 and Iteracion < Iteracion_Maxima:
        
        vecindario = Funcion_Generar_Vecinos(Estado_Actual)
        
        Mejor_solucion = Cambiar_Estado_Actual(vecindario, lista_tabu, Criterio_aspiracion)
        #El resultado anterior nos da una lista que contiene lo siguiente [[solucion], costo, swap]] indice [0, 1, 2]
        Estado_Actual = Mejor_solucion[0]
        lista_tabu.append(Mejor_solucion[2])
        
        #si costo es menor al criterio de aspiracion este sera el nuevo costo de aspiracion 
        if Mejor_solucion[1] < Criterio_aspiracion:
            Criterio_aspiracion = Mejor_solucion[1]
            Mejor_Estado_Global = Mejor_solucion[0].copy()
        
        Iteracion += 1
        
    tiempo_fin = time.perf_counter()
    tiempo_ejecucion = tiempo_fin - tiempo_inicio

    print("\n--- MÉTRICAS DE RENDIMIENTO ---")
    print(f"Solución Encontrada: {Mejor_Estado_Global}")
    print(f"Choques Finales: {Criterio_aspiracion}")
    print(f"Cantidad de Movimientos: {Iteracion}")
    print(f"Tiempo de Ejecución: {tiempo_ejecucion:.6f} segundos")
    print()
    print("****Tablero Final****")
    print()
    Dibujar_tablero(Mejor_Estado_Global)
    
main()
    
    