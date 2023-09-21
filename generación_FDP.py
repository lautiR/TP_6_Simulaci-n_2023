import numpy as np 
import matplotlib.pyplot as plt
import scipy.stats as stats
import pandas as pd
from scipy.interpolate import interp1d

archivo_excel = "C:\\Users\lauti\\Escritorio\\Python\Python\\TP_6_Simulaci-n_2023\\Datos_FPD_v1.xlsx" 
df = pd.read_excel(archivo_excel)  


# Configurar el número de bins (intervalos) para el histograma
num_bins = 20

# Crear el histograma
plt.hist(df['IA_minutos'], bins=num_bins, density=True, alpha=0.6, color='b', edgecolor='black')

# Configurar etiquetas y título
plt.xlabel('Horario_Arribo')
plt.ylabel('Densidad de Probabilidad')
plt.title('Función de Densidad de Probabilidad')

# Mostrar el histograma
plt.show()

plt.hist(df['IA_minutos'], bins=20, density=True, alpha=0.6, color='b', edgecolor='black', label='Datos')

# Calcular el histograma
hist, bin_edges = np.histogram(df['IA_minutos'], bins=20, density=True)

# Calcular la función de frecuencia acumulada
cumulative_hist = np.cumsum(hist * np.diff(bin_edges))

# Crear un nuevo gráfico para la función de frecuencia acumulada
plt.figure()
plt.plot(bin_edges[:-1], cumulative_hist, 'r-', label='Frecuencia Acumulada')
plt.xlabel('Horario_Arribo')
plt.ylabel('Frecuencia Acumulada')
plt.title('Función de Frecuencia Acumulada')
plt.legend()
plt.show()

# # Crear una función interpoladora inversa
# inverse_cumulative = interp1d(cumulative_hist, bin_edges[:-1], bounds_error=False, fill_value=(bin_edges[0], bin_edges[-1]))

# # Definir una probabilidad acumulada para la que deseas encontrar el valor inverso
# probabilidad_acumulada_deseada = np.random.rand()

# # Calcular el valor inverso correspondiente a la probabilidad acumulada deseada
# valor_inverso = inverse_cumulative(probabilidad_acumulada_deseada)



horarios_arribo_generados = []
random_generados = []
combinado = []
for i in range(50):
    # Crear una función interpoladora inversa
    inverse_cumulative = interp1d(cumulative_hist, bin_edges[:-1], bounds_error=False, fill_value=(bin_edges[0], bin_edges[-1]))

    # Definir una probabilidad acumulada para la que deseas encontrar el valor inverso
    probabilidad_acumulada_deseada = round(np.random.rand(),2)
    random_generados.append(probabilidad_acumulada_deseada)  

    
    # Calcular el valor inverso correspondiente a la probabilidad acumulada deseada
    valor_inverso = inverse_cumulative(probabilidad_acumulada_deseada).item()
    horarios_arribo_generados.append(round(valor_inverso,2))

combinado = list(zip(random_generados,horarios_arribo_generados))
print(f"Valores inversos para P{combinado}")

    
