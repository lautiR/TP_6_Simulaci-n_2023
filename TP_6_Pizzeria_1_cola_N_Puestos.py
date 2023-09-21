import numpy as np 
import matplotlib.pyplot as plt
import scipy.stats as stats
import pandas as pd
from scipy.interpolate import interp1d
from scipy.stats import gaussian_kde


#Importar Archivo Excel
archivo_excel = "C:\\Users\lauti\\Escritorio\\Python\Python\\TP_6_Simulaci-n_2023\\Datos_FPD_v1.xlsx" 
df = pd.read_excel(archivo_excel)  
columna_excel_IA = 'IA_minutos'
columna_excel_TA = 'TA_minutos'
# Configurar el número de bins (intervalos) para el histograma
num_bins = 20

def generar_FDP(num_bins,columna_excel):  
    ## Calcular el histograma FDP
    hist, bin_edges = np.histogram(df[columna_excel], bins=num_bins, density=True)
    return hist, bin_edges

def generar_CDF(hist,bin_edges):
    cumulative_hist = np.cumsum(hist * np.diff(bin_edges))    
    return cumulative_hist

def generar_PPF_VIEJA(numero_random,media,desviacion_estandar):
    x_inversa = stats.norm.ppf(numero_random, loc=media, scale=desviacion_estandar)
    return x_inversa

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

def generar_tiempo_atencion(media,desviacion_estandar):
    num_random = np.random.rand()
    tiempo_atencion = generar_PPF_VIEJA(num_random,media,desviacion_estandar)    
    return round(tiempo_atencion,2)

def generar_intervalo_arribo(cumulative_hist,bin_edges):   
    intervalo_arribo = generar_PPF(cumulative_hist,bin_edges).item()    
    return round(intervalo_arribo,2)
 
def buscar_menor_TPS_i(lista_tiempos):
    tiempo_menor = min(lista_tiempos)
    indice = lista_tiempos.index(tiempo_menor)
    return indice, tiempo_menor    
 
def procesar_salida(tiempo_actual,vector_tiempo_proxima_salida_i,posicion_tiempo_proxima_salida_i):
    tiempo_actual = vector_tiempo_proxima_salida_i[posicion_tiempo_proxima_salida_i]
    global NS, N, HV, media_tiempo_atencion, desvio_tiempo_atencion
    NS -=1
    if(NS>=N):
        tiempo_atencion = generar_tiempo_atencion(media_tiempo_atencion,desvio_tiempo_atencion)
        vector_tiempo_proxima_salida_i[posicion_tiempo_proxima_salida_i] = tiempo_actual + tiempo_atencion
    else:
        vector_tiempo_proxima_salida_i[posicion_tiempo_proxima_salida_i] = HV
    return tiempo_actual, vector_tiempo_proxima_salida_i

def procesar_llegada(tiempo_actual,tiempo_proxima_llegada):
    tiempo_actual = tiempo_proxima_llegada
    global histograma_CDF, bin_edges
    intervalo_arribo = generar_intervalo_arribo(histograma_CDF,bin_edges)
    tiempo_proxima_llegada += intervalo_arribo
    global NS
    NS+=1
    return tiempo_actual, tiempo_proxima_llegada 

def buscar_puesto_atencion_libre(vector_tiempo_proxima_salida_i):
    global HV  
    #Busco el primer elemento que no sea HV, pero genera una lista paralela para realizar la busqueda, medio falopa
    indice = next(i for i, x in enumerate(vector_tiempo_proxima_salida_i) if x == HV)   
    return indice

def procesar_atencion_por_disponibilidad_de_puestos(tiempo_actual, posicion_tiempo_proxima_salida_i,vector_tiempo_proxima_salida_i):
    posicion_tiempo_proxima_salida_i = buscar_puesto_atencion_libre(vector_tiempo_proxima_salida_i)
    global media_tiempo_atencion, desvio_tiempo_atencion
    tiempo_atencion = generar_tiempo_atencion(media_tiempo_atencion, desvio_tiempo_atencion)
    vector_tiempo_proxima_salida_i[posicion_tiempo_proxima_salida_i] = tiempo_actual + tiempo_atencion
    #Agregar STO 
    return vector_tiempo_proxima_salida_i

#Defino Variables Globales
##mi MAIN() 
CONDICION = True
N = 5
NS = 0
NT = 0
tiempo_actual = 0
tiempo_final = 1000
HV = tiempo_final*2
iteracion = 0
tiempo_proxima_llegada = 1
vector_tiempo_proxima_salida_i = [HV,HV,HV,HV,HV]
tiempo_proxima_salida_i = 0
posicion_tiempo_proxima_salida_i = 0
media_tiempo_atencion, desvio_tiempo_atencion = 15,5
histograma_CDF, bin_edges = iniciar_FDP_and_CDF_IAs_obtener_CDF(num_bins,columna_excel_IA)

while(CONDICION):
    iteracion +=1
    posicion_tiempo_proxima_salida_i, tiempo_proxima_salida_i = buscar_menor_TPS_i(vector_tiempo_proxima_salida_i)
    if(tiempo_proxima_llegada<=tiempo_proxima_salida_i):
        NT+=1
        tiempo_actual,tiempo_proxima_llegada = procesar_llegada(tiempo_actual,tiempo_proxima_llegada)
        if(NS<=N):
            vector_tiempo_proxima_salida_i = procesar_atencion_por_disponibilidad_de_puestos(tiempo_actual,tiempo_proxima_salida_i,vector_tiempo_proxima_salida_i)
    else:
        tiempo_actual, vector_tiempo_proxima_salida_i = procesar_salida(tiempo_actual,vector_tiempo_proxima_salida_i,posicion_tiempo_proxima_salida_i)

    print(f"--> it:{iteracion},t:{format(tiempo_actual,'.2f')},TPLL: {format(tiempo_proxima_llegada, '.2f')}, i+1: {posicion_tiempo_proxima_salida_i+1}, TPS {format(tiempo_proxima_salida_i, '.2f')}, NS: {NS}, N_Ocupados: {sum(1 for e in vector_tiempo_proxima_salida_i if e != HV)} NT: {NT}")
    if(tiempo_actual>=tiempo_final):        
        if(NS==0):
            print("calculo Resultados")
            CONDICION = False
        else:
            tiempo_proxima_llegada = HV
    
        
   
## Crear GRAFICO del histograma FDP  
def graficar_histograma_FDP_2(columna_excel, num_bins):
    # Calcular el histograma de densidad
    hist, bin_edges = np.histogram(df[columna_excel], bins=num_bins, density=True)
    # Calcular los puntos medios de los bins para la representación de la FDP
    bin_width = bin_edges[1] - bin_edges[0]
    bin_centers = bin_edges[:-1] + bin_width / 2
    # Calcular la FDP (aproximada) a partir del histograma
    fdp = hist / sum(hist)
    # Configurar el título y etiquetas del gráfico
    plt.xlabel('Intervalo_Arribo [Minutos]')
    plt.ylabel('Densidad de Probabilidad')
    plt.title('Función de Densidad de Probabilidad')
    # Graficar la FDP
    plt.plot(bin_centers, fdp, color='r', label='FDP')
    # Graficar los datos en forma de histograma
    plt.hist(df[columna_excel], bins=num_bins, density=True, alpha=0.6, color='b', edgecolor='black', label='Datos')
    # Mostrar la leyenda
    plt.legend()
    # Mostrar el gráfico
    plt.show() 

def graficar_histograma_CPF(bin_edges,cumulative_hist):    
    plt.figure()
    plt.plot(bin_edges[:-1], cumulative_hist, 'r-', label='Frecuencia Acumulada')
    plt.xlabel('Intervalo Arribo [Minuntos]')
    plt.ylabel('Frecuencia Acumulada')
    plt.title('Función de Frecuencia Acumulada')
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
    
print("ACA GRAFICO")    
graficar_histograma_FDP(columna_excel_IA,num_bins)
graficar_histograma_CPF(bin_edges,histograma_CDF)
   