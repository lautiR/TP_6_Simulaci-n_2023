import numpy as np 
import matplotlib.pyplot as plt
import scipy.stats as stats
import pandas as pd
from scipy.interpolate import interp1d
from scipy.stats import gaussian_kde

#TODO ****************
# 1) Convertir la FDP de T.A. (distribución normal) a una Equiprobable (entre 15 y 30 min, ponele)  * DONE
# 2) Analizar la 2da Variable de Control, tomarla como "tiempo de corte" y poder particulzarizar para cada elemento
# en el sistema, conocer su tiempo de permanecia (por ej, si tardó 30 min o más en salir del sistema ). Además, cálcular resultado
# 3) Utilizar el Excel normalizado con los Datos Posta en vez del excel de prueba subido al repo. 
#*********************

#Importar Archivo Excel
#archivo_excel = ".\\Datos_FPD_v1.xlsx" 
archivo_excel = ".\\pizza_orders.xlsx" 
df = pd.read_excel(archivo_excel)  
columna_excel_IA = 'IA'
# Configurar el número de bins (intervalos) para el histograma
num_bins = 90

def generar_FDP(num_bins,columna_excel):  
    ## Calcular el histograma FDP
    hist, bin_edges = np.histogram(df[columna_excel], bins=num_bins, density=True)
    return hist, bin_edges

def generar_CDF(hist,bin_edges):
    cumulative_hist = np.cumsum(hist * np.diff(bin_edges))    
    return cumulative_hist

def generar_PPF(cumulative_hist,bin_edges):
    # # Crear una función interpoladora inversa relacionada con la ACUMULADA
    inverse_cumulative = interp1d(cumulative_hist, bin_edges[:-1], bounds_error=False, fill_value=(bin_edges[0], bin_edges[-1]))
    # # Definir una probabilidad acumulada para la que deseas encontrar el valor inverso (GENERO DE FORMA RANDOM)
    probabilidad_acumulada_deseada = np.random.rand()
    # # Calcular el valor inverso correspondiente a la probabilidad acumulada deseada
    valor_inverso = inverse_cumulative(probabilidad_acumulada_deseada)
    return valor_inverso

def iniciar_FDP_and_CDF_IAs_obtener_CDF(num_bins,columna_excel):
    hist, bin_edges = generar_FDP(num_bins,columna_excel)
    cumulative_hist = generar_CDF(hist,bin_edges)
    return cumulative_hist, bin_edges

def generar_tiempo_atencion():    
    tiempo_atencion = 10 + (5* np.random.rand())
    #print(f"--> TA:{format(tiempo_atencion,'.2f')}")
    return round(tiempo_atencion,2)

def generar_intervalo_arribo(cumulative_hist,bin_edges):   
    intervalo_arribo = generar_PPF(cumulative_hist,bin_edges).item()    
    return round(intervalo_arribo,2)
 
def buscar_menor_TPS_i(lista_tiempos):
    tiempo_menor = min(lista_tiempos)
    indice = lista_tiempos.index(tiempo_menor)
    return indice, tiempo_menor    
 
def procesar_salida(tiempo_actual,vector_tiempo_proxima_salida_i,posicion_tiempo_proxima_salida_i,vector_inicio_tiempo_ocioso_i):
    tiempo_actual = vector_tiempo_proxima_salida_i[posicion_tiempo_proxima_salida_i]
    global NS, N_PUESTOS, HV
    NS -=1
    if(NS>=N_PUESTOS):
        tiempo_atencion = generar_tiempo_atencion()
        vector_tiempo_proxima_salida_i[posicion_tiempo_proxima_salida_i] = tiempo_actual + tiempo_atencion
    else:
        vector_tiempo_proxima_salida_i[posicion_tiempo_proxima_salida_i] = HV
        vector_inicio_tiempo_ocioso_i[posicion_tiempo_proxima_salida_i] = tiempo_actual
    return tiempo_actual, vector_tiempo_proxima_salida_i, vector_inicio_tiempo_ocioso_i

def procesar_llegada(tiempo_actual,tiempo_proxima_llegada):
    tiempo_actual = tiempo_proxima_llegada
    global histograma_CDF_IA, bin_edges_IA
    intervalo_arribo = generar_intervalo_arribo(histograma_CDF_IA,bin_edges_IA)
    tiempo_proxima_llegada += intervalo_arribo
    global NS, NT
    NS+=1
    NT+=1
    return tiempo_actual, tiempo_proxima_llegada 

def buscar_puesto_atencion_libre(vector_tiempo_proxima_salida_i):
    global HV  
    #Busco el primer elemento que no sea HV, pero genera una lista paralela para realizar la busqueda, medio falopa
    indice = next(i for i, x in enumerate(vector_tiempo_proxima_salida_i) if x == HV)   
    return indice

def procesar_atencion_por_disponibilidad_de_puestos(tiempo_actual, posicion_tiempo_proxima_salida_i,vector_tiempo_proxima_salida_i,vector_sumatoria_tiempo_ocioso_i,vector_inicio_tiempo_ocioso_i):
    posicion_tiempo_proxima_salida_i = buscar_puesto_atencion_libre(vector_tiempo_proxima_salida_i)    
    tiempo_atencion = generar_tiempo_atencion()
    vector_tiempo_proxima_salida_i[posicion_tiempo_proxima_salida_i] = tiempo_actual + tiempo_atencion
    vector_sumatoria_tiempo_ocioso_i[posicion_tiempo_proxima_salida_i] += (tiempo_actual - vector_inicio_tiempo_ocioso_i[posicion_tiempo_proxima_salida_i])
    #Agregar STO 
    return vector_tiempo_proxima_salida_i,vector_sumatoria_tiempo_ocioso_i

def calcular_y_mostrar_PTO_i(vector_sumatoria_tiempo_ocioso_i,tiempo_actual):
    tamanio = len(vector_sumatoria_tiempo_ocioso_i)
    vector_PTO_i = [0 for _ in range(tamanio)]
    for i in range(tamanio):
        vector_PTO_i[i] = (vector_sumatoria_tiempo_ocioso_i[i]/tiempo_actual)*100
        print(f"Puesto i:{i}, PTO: {format(vector_PTO_i[i],'.2f')}%")
    
def calcular_y_mostar_PPA():
    print(f"Pedidos Totales: {NT}, Promociones Activadas: {ACTIVACIONES}, PPA: {format(ACTIVACIONES/NT*100,'.2f')}%")

#Defino Variables Globales
##mi MAIN() 
CONDICION = True
#//**VARIABLES DE CONTROL//
N_PUESTOS = 3 #Puestos Atención 
N_CORTE_PROMO = 12 #Cantidad de elementos MAX en el sistema, a partir de los cuales, que me generarían un retraso
#//VARIABLES DE CONTROL**// 
NS = 0 #Elementos en el sistema en el tiempo actual
NT = 0 #Elementos totales que ingresaron al sistema
ACTIVACIONES = 0
tiempo_actual = 0
tiempo_final = 100000
HV = tiempo_final*100
iteracion = 0
tiempo_proxima_llegada = 0
vector_tiempo_proxima_salida_i = [HV for _ in range(N_PUESTOS)] #Inicializo puestos atención libres "HV"
vector_inicio_tiempo_ocioso_i = [0 for _ in range(N_PUESTOS)]
vector_sumatoria_tiempo_ocioso_i = [0 for _ in range(N_PUESTOS)]
histograma_CDF_IA, bin_edges_IA = iniciar_FDP_and_CDF_IAs_obtener_CDF(num_bins,columna_excel_IA)
tiempo_permanencia_elemento = 0

while(CONDICION):
    iteracion +=1
    posicion_tiempo_proxima_salida_i, tiempo_proxima_salida_i = buscar_menor_TPS_i(vector_tiempo_proxima_salida_i)
    if(tiempo_proxima_llegada<=tiempo_proxima_salida_i):              
        tiempo_actual,tiempo_proxima_llegada = procesar_llegada(tiempo_actual,tiempo_proxima_llegada)
        if(NS>=N_CORTE_PROMO): #No es metodología, solo para Resultados
            ACTIVACIONES+=1
        if(NS<=N_PUESTOS):
            vector_tiempo_proxima_salida_i,vector_sumatoria_tiempo_ocioso_i = procesar_atencion_por_disponibilidad_de_puestos(tiempo_actual,tiempo_proxima_salida_i,vector_tiempo_proxima_salida_i,vector_sumatoria_tiempo_ocioso_i, vector_inicio_tiempo_ocioso_i)
    else:
        tiempo_actual, vector_tiempo_proxima_salida_i, vector_inicio_tiempo_ocioso_i = procesar_salida(tiempo_actual,vector_tiempo_proxima_salida_i,posicion_tiempo_proxima_salida_i,vector_inicio_tiempo_ocioso_i)

    print(f"--> it:{iteracion},t:{format(tiempo_actual,'.2f')},TPLL: {format(tiempo_proxima_llegada, '.2f')}, i: {posicion_tiempo_proxima_salida_i}, TPS_i: {format(tiempo_proxima_salida_i, '.2f')}, NS: {NS}, N_Ocupados: {sum(1 for e in vector_tiempo_proxima_salida_i if e != HV)} NT: {NT}, ITO_i: {format(vector_inicio_tiempo_ocioso_i[posicion_tiempo_proxima_salida_i],'.2f')}, STO_i: {format(vector_sumatoria_tiempo_ocioso_i[posicion_tiempo_proxima_salida_i],'.2f')}")
    if(tiempo_actual>=tiempo_final):        
        if(NS==0):
            print("Cálculo de Resultados:")
            calcular_y_mostrar_PTO_i(vector_sumatoria_tiempo_ocioso_i,tiempo_actual)
            calcular_y_mostar_PPA()  #Porcentaje_Promos_Activadas: Porcentaje de los pedidos que debieron activar la promo                   
            CONDICION = False
        else:
            tiempo_proxima_llegada = HV
            
    

## GRAFICOS FDP y CPF         
def graficar_histograma_CPF(bin_edges,cumulative_hist):    
    plt.figure()
    plt.plot(bin_edges[:-1], cumulative_hist, 'r-', label='Frecuencia Acumulada')
    plt.xlabel('Intervalo Arribo [Minutos]')
    plt.ylabel('Probabilidad Acumulada')
    plt.title('Función de Distribución Acumulada')
    plt.legend()
    plt.show()
    
def graficar_histograma_FDP(columna_excel, num_bins):
    # Obtener los datos de la columna
    data = df[columna_excel]
    # Calcular el histograma de densidad
    hist, bin_edges = np.histogram(data, bins=num_bins, density=True)
    # Calcular la FDP a partir del histograma
    bin_width = bin_edges[1] - bin_edges[0]
    # bin_centers = bin_edges[:-1] + bin_width / 2
    # fdp = hist / sum(hist)
    # Calcular una estimación suavizada de la FDP usando una distribución de kernel
    kde = gaussian_kde(data)
    x_vals = np.linspace(min(data), max(data), 1000)
    fdp_suavizada = kde(x_vals)
    # Configurar el título y etiquetas del gráfico
    plt.xlabel('Intervalo_Arribo [Minutos]')
    plt.ylabel('Densidad de Probabilidad')
    plt.title('Función de Densidad de Probabilidad')
    # Graficar la FDP suavizada
    plt.plot(x_vals, fdp_suavizada, color='r', label='FDP')
    # Graficar los datos en forma de histograma
    plt.hist(data, bins=num_bins, density=True, alpha=0.6, color='b', edgecolor='black', label='Datos')
    # Mostrar la leyenda
    plt.legend()
    # Mostrar el gráfico
    plt.show()
    
print("ACÁ GRAFÍCO")    
graficar_histograma_FDP(columna_excel_IA,num_bins)
graficar_histograma_CPF(bin_edges_IA,histograma_CDF_IA)
   