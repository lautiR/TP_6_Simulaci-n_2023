import numpy as np 
import matplotlib.pyplot as plt
import scipy.stats as stats





#Defino bloques funcionales
def generar_FDP(limite_inferior, limite_superior, tamanio_muestra,media,desviacion_estandar):    
    muestras = np.linspace(limite_inferior, limite_superior, tamanio_muestra)
    pdf = stats.norm.pdf(muestras, loc=media, scale=desviacion_estandar)
    return pdf

def generar_CDF(limite_inferior,limite_superior,media,desviacion_estandar):
    cdf = stats.norm.cdf(limite_superior, loc=media, scale=desviacion_estandar) - stats.norm.cdf(limite_inferior, loc=media, scale=desviacion_estandar)
    return cdf

def generar_PPF(numero_random,media,desviacion_estandar):
    x_inversa = stats.norm.ppf(numero_random, loc=media, scale=desviacion_estandar)
    return x_inversa

#TODO  
def generar_tiempo_atencion(media,desviacion_estandar):
    num_random = np.random.rand()
    tiempo_atencion = generar_PPF(num_random,media,desviacion_estandar)    
    return round(tiempo_atencion,2)

#TODO definir minutos / horas / ETC 
def generar_intervalo_arribo(media,desviacion_estandar):
    num_random = np.random.rand()
    intervalo_arribo = generar_PPF(num_random,media,desviacion_estandar)    
    return round(intervalo_arribo,2)
 
def buscar_menor_TPS_i(lista_tiempos):
    tiempo_menor = min(lista_tiempos)
    indice = lista_tiempos.index(tiempo_menor)
    return indice, tiempo_menor    

#TODO  
def procesar_salida(tiempo_actual,vector_tiempo_proxima_salida_i,posicion_tiempo_proxima_salida_i):
    tiempo_actual = vector_tiempo_proxima_salida_i[posicion_tiempo_proxima_salida_i]
    global NS, N, media_tiempo_atencion, desvio_tiempo_atencion
    NS -=1
    if(NS>=N):
        tiempo_atencion = generar_tiempo_atencion(media_tiempo_atencion,desvio_tiempo_atencion)
        vector_tiempo_proxima_salida_i[posicion_tiempo_proxima_salida_i] = tiempo_actual + tiempo_atencion
    return tiempo_actual, vector_tiempo_proxima_salida_i
#TODO  
def procesar_llegada(tiempo_actual,tiempo_proxima_llegada):
    tiempo_actual = tiempo_proxima_llegada
    global media_arribo_pedidos, desvio_arribo_pedidos 
    intervalo_arribo = generar_intervalo_arribo(media_arribo_pedidos,desvio_arribo_pedidos)
    tiempo_proxima_llegada += intervalo_arribo
    global NS
    NS+=1
    return tiempo_actual, tiempo_proxima_llegada 

def buscar_puesto_atencion_libre(vector_tiempo_proxima_salida_i):
    global HV  
    #Busco el primer elemento que no sea HV, pero genera una lista paralela para realizar la busqueda, medio falopa
    indice = next(i for i, x in enumerate(vector_tiempo_proxima_salida_i) if x == HV)   
    return indice 
  

#TODO
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
tiempo_final = 100
HV = tiempo_final*2
iteracion = 0
tiempo_proxima_llegada = 1
vector_tiempo_proxima_salida_i = [HV,HV,HV,HV,HV]
tiempo_proxima_salida_i = 0
posicion_tiempo_proxima_salida_i = 0
media_arribo_pedidos, desvio_arribo_pedidos = 10,2
media_tiempo_atencion, desvio_tiempo_atencion = 15,5


while(CONDICION):
    iteracion +=1
    posicion_tiempo_proxima_salida_i, tiempo_proxima_salida_i = buscar_menor_TPS_i(vector_tiempo_proxima_salida_i)
    if(tiempo_proxima_llegada<=tiempo_proxima_salida_i):
        NT+=1
        tiempo_actual, tiempo_proxima_llegada = procesar_llegada(tiempo_actual,tiempo_proxima_llegada)
        if(NS<=N):
            vector_tiempo_proxima_salida_i = procesar_atencion_por_disponibilidad_de_puestos(tiempo_actual,tiempo_proxima_salida_i,vector_tiempo_proxima_salida_i)
    else:
        tiempo_actual, vector_tiempo_proxima_salida_i = procesar_salida(tiempo_actual,tiempo_proxima_salida_i,posicion_tiempo_proxima_salida_i)

    print(f"------> it:{iteracion},t:{format(tiempo_actual,'.2f')},TPLL: {format(tiempo_proxima_llegada, '.2f')}, i: {posicion_tiempo_proxima_salida_i}, TPS {format(tiempo_proxima_salida_i, '.2f')}, NT: {NT}")
    if(tiempo_actual>=tiempo_final):        
        if(NS==0):
            print("calculo Resultados")
            CONDICION = False
        else:
            tiempo_proxima_llegada = HV
    
        
   

