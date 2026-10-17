import copy
import math
import random
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

random.seed(42)

#cargar los documentos de excel
distribucion_tiendas = pd.read_excel("datos_distribucion_tiendas.xlsx")
costos_combustibles = pd.read_excel("matriz_costos_combustible.xlsx")
datos_distancias = pd.read_excel("matriz_distancias.xlsx")

D = datos_distancias.to_numpy()
C = costos_combustibles.to_numpy()

#Separar tiendas y CDs
CDS = 10
indices_cds = list(range(0, CDS))
indices_tiendas = list(range(CDS, 100))

cds = distribucion_tiendas.iloc[indices_cds].copy()
cds["Capacidad_disponible"] = cds["Capacidad_Almacenamiento"].astype(float)
tiendas = distribucion_tiendas.iloc[indices_tiendas].copy()

#se añaden dos columnas a los datos
tiendas["demanda_semanal"] = tiendas["Capacidad_Venta"] // 4
tiendas["urgencia"] = tiendas["Capacidad_Venta"] / tiendas["Capacidad_Almacenamiento"]
urgencias = tiendas["urgencia"].to_dict()

#Agrupamiento de Tiendas a CDs
rutas = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [] }

tiendas = tiendas.sort_values("urgencia", ascending=False)


#Distribucion de las tiendas
for i, tienda in tiendas.iterrows():
    mejor_cd = -1
    distancia_minima = 9999999
    
    for j, cd in cds.iterrows():
        if cd["Capacidad_disponible"] >= tienda["demanda_semanal"] and D[i, j] < distancia_minima:
            distancia_minima = D[i, j]
            mejor_cd =  j
    rutas[mejor_cd].append(i)
    cds.loc[mejor_cd, "Capacidad_disponible"] -= tienda["demanda_semanal"] 

def funcion_de_costo(rutas):
    costo = 0
    penalizacion = 0  
    for cd, lista_tiendas in rutas.items():
        recorrido = [cd] + lista_tiendas + [cd]
        for i in range(len(recorrido)-1):
            origen = recorrido[i]
            destino = recorrido[i + 1]
            costo += C[origen, destino]            
        for posicion, tienda in enumerate(lista_tiendas, start=1):
            urgencia = urgencias[tienda]
            penalizacion += posicion * urgencia * 0.05 #0.01
            
    return costo + penalizacion
            


# Guardar el estado actual como la Mejor Solución Histórica
costo_actual = funcion_de_costo(rutas)
rutas_iniciales = copy.deepcopy(rutas)
mejor_solucion = copy.deepcopy(rutas)
mejor_costo = costo_actual

#Parametros del recocido simulado
temperatura_inicial = 0.2 * costo_actual
factor_enfriamiento = 0.99
limite_iteraciones = 1000
iteracion = 0
temperatura = temperatura_inicial

# Lista vacía para graficar la evolución del costo
historial_costos = []


while (iteracion < limite_iteraciones and temperatura > 0.001):

    for cd in rutas:        
        #intercambio de posiciones
        longitud = len(rutas[cd])
        if longitud < 2:
            continue
        
        rutas_nuevas = {k: v[:] for k, v in rutas.items()}

        inicio, fin = random.sample(range(longitud), 2)
        
        rutas_nuevas[cd][inicio], rutas_nuevas[cd][fin] = rutas_nuevas[cd][fin], rutas_nuevas[cd][inicio]
        
        costo_nuevo = funcion_de_costo(rutas_nuevas)
    
        #Evaluacion y criterio de aspiracion
        delta_costo = costo_nuevo - costo_actual
        
        if delta_costo < 0:
            rutas = rutas_nuevas
            costo_actual = costo_nuevo
        else:
            probabilidad = math.exp(-delta_costo / temperatura)
            num_aleatorio = random.random()
            if num_aleatorio < probabilidad:
            #actualizacion 
                rutas = rutas_nuevas
                costo_actual = costo_nuevo
                
        if costo_actual < mejor_costo:
            mejor_costo = costo_actual
            mejor_solucion =copy.deepcopy(rutas)
        
    historial_costos.append(costo_actual)    
    
    temperatura = temperatura * factor_enfriamiento
    
    iteracion += 1
    
# Función para evaluar las métricas logísticas reales (Distancia, Combustible y Tiempo)
def evaluar_rendimiento(diccionario_rutas, velocidad_promedio_kmh=40.0):
    distancia_total = 0.0
    costo_combustible = 0.0
    
    for cd, lista_tiendas in diccionario_rutas.items():
        recorrido = [cd] + lista_tiendas + [cd]
        for i in range(len(recorrido) - 1):
            origen = recorrido[i]
            destino = recorrido[i + 1]
            distancia_total += D[origen, destino]
            costo_combustible += C[origen, destino]
            
    tiempo_horas = distancia_total / velocidad_promedio_kmh
    return distancia_total, costo_combustible, tiempo_horas

# Comparación entre la solución inicial (referencia) y la mejor solución del Recocido Simulado
dist_ini, comb_ini, t_ini = evaluar_rendimiento(rutas_iniciales)
dist_opt, comb_opt, t_opt = evaluar_rendimiento(mejor_solucion)

def imprimir_rutas(diccionario_rutas, titulo):
    print(f"\n=== {titulo} ===")
    for cd, lista_tiendas in diccionario_rutas.items():
        recorrido_str = " -> ".join([f"CD{cd+1}"] + [f"T{t+1}" for t in lista_tiendas] + [f"CD{cd+1}"])
        print(f"CD {cd+1} ({len(lista_tiendas)} tiendas): {recorrido_str}")

def imprimir_metricas(distancia, combustible, tiempo, titulo):
    print(f"\n=== {titulo} ===")
    print(f"Distancia Total:      {distancia:.2f} km")
    print(f"Costo de Combustible: ${combustible:.2f} USD")
    print(f"Tiempo de Entrega:    {tiempo:.2f} hrs")

# Solución inicial
imprimir_metricas(dist_ini, comb_ini, t_ini, "MÉTRICAS SOLUCIÓN INICIAL")
imprimir_rutas(rutas_iniciales, "RUTAS INICIALES POR CENTRO DE DISTRIBUCIÓN")

# Solución optimizada
imprimir_metricas(dist_opt, comb_opt, t_opt, "MÉTRICAS SOLUCIÓN OPTIMIZADA")
imprimir_rutas(mejor_solucion, "RUTAS OPTIMIZADAS POR CENTRO DE DISTRIBUCIÓN")

# Comparación
print("\n=== COMPARACIÓN ===")
print(f"Distancia Total:      Inicial = {dist_ini:.2f} km  | Optimizada = {dist_opt:.2f} km  | Ahorro = {dist_ini - dist_opt:.2f} km ({(dist_ini - dist_opt)/dist_ini*100:.2f}%)")
print(f"Costo de Combustible: Inicial = ${comb_ini:.2f} USD | Optimizado = ${comb_opt:.2f} USD | Ahorro = ${comb_ini - comb_opt:.2f} USD ({(comb_ini - comb_opt)/comb_ini*100:.2f}%)")
print(f"Tiempo de Entrega:    Inicial = {t_ini:.2f} hrs  | Optimizado = {t_opt:.2f} hrs  | Ahorro = {(t_ini - t_opt)*60:.1f} min")

# Gráfica de evolución del costo (como la solicitada en las instrucciones)
plt.figure(figsize=(10, 5))
plt.plot(historial_costos, marker='o', markersize=4, linestyle='-', color='#1f77b4')
plt.title("Evolución del Costo en Recocido Simulado")
plt.xlabel("Iteración")
plt.ylabel("Costo (USD)")
plt.grid(True)
plt.show()
          
        
    
            
    