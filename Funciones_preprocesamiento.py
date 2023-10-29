# Importar librerias
import pandas as pd
import numpy as np
import datetime as dt
import re
from unidecode import unidecode

# Método constructor de la clase que preprocesa los datos de los donantes
class Preprocesamiento_Donantes:
    """Clase para el preprocesamiento de los datos"""
    # Método constructor de la clase
    def __init__(self, df: pd.DataFrame):
        """Constructor de la clase"""
        self.df = df

    # Método para validar si existen textos en las columnas de fechas
    def texto_en_fechas(self, col:str):
        """Método para validar si existen textos en las columnas de fechas
        Args:
            df (pd.DataFrame): DataFrame con los datos de los donantes
            col (str): Nombre de la columna a revisar
        Returns:
            pd.DataFrame: DataFrame con los valores convertidos en fecha"""
        
        # Obtener valores que no coincidan con una fecha
        df_error = self.df[col].str.contains(r'[Aa-zZ]', regex=True)
        # Llenar los valores faltantes con False
        df_error.fillna(False, inplace=True)
        # Los valores falsos son los correctos y se deben conservar
        df_conservar = df_error[df_error == False]
        df_conservar.replace(False, True, inplace=True)
        df_conservar = pd.DataFrame(df_conservar)
        # Filtrar el df original con los valores correctos
        self.df = self.df[self.df.index.isin(df_conservar.index)]

        return self.df, df_error[df_error == True]
    
    # Método para ajustar los nombres y tipos de las columnas
    def ajustar_nombre_y_tipo_columnas(self, col:str, n_col:str, tipo:str):
        """Método para ajustar los nombres y tipos de las columnas
        Args:
            df (pd.DataFrame): DataFrame con los datos de los donantes
            col (str): Nombre de la columna a revisar
            n_col (str): Nombre de la nueva columna
            tipo (str): Tipo de dato a convertir --> 'int', 'float', 'datetime', 'bool'
        Returns:
            pd.DataFrame: DataFrame con los valores convertidos en fecha"""
        # Cambiar tipo de columna
        self.df[col] = self.df[col].astype(tipo)
        # Renombrar columna
        self.df.rename(columns={col:n_col}, inplace=True)

        return self.df

    # Método para filtrar los donantes activos
    def filtrar_donantes_activos(self, col:str, return_inactivos: bool = False):
        """Método para filtrar los donantes activos. Ya se debe haber convertido la columna a boolean
        Args:
            df (pd.DataFrame): DataFrame con los datos de los donantes
            col (str): Nombre de la columna a revisar
            return_df (bool, optional): Si es True, retorna el DataFrame con los donantes inactivos. Defaults to False.
        Returns:
            pd.DataFrame: DataFrame con los donantes activos"""

        # Filtrar los donantes activos
        self.df = self.df[self.df[col]==True]
        df_inactivos = self.df[self.df[col]==False]

        # Retornar el DataFrame con los donantes activos
        if return_inactivos:
            return self.df, df_inactivos
        else:
            return self.df
        
    # Método para corregir las edades de los donantes
    def corregir_edades(self, return_errors: bool = False):
        """Método para corregir las edades de los donantes. En teoría solo se reciben donaciones de mayores de edad y menores de 90 años
        Args:
            df (pd.DataFrame): DataFrame con los datos de los donantes
            return_errors (bool, optional): Si es True, retorna los valores que no coincidan con una edad. Defaults to False.
        Returns:
            pd.DataFrame: DataFrame con los valores convertidos en edad"""
        # Llenar faltantes de edad
        self.df['Edad'] = np.where(self.df['Edad'].isnull(), 0, self.df['Edad'])

        # Convertir datos a entero
        self.df['Edad'] = self.df['Edad'].astype(int)

        # Remover registros menores de edad
        df_error = self.df[(self.df['Edad']<18) & (self.df['Edad']>90)]
        self.df = self.df[(self.df['Edad']>=18) & (self.df['Edad']<=90)]

        # Revisar si hay errores en la columna Edad
        if len(df_error) > 0:
            print('Hay errores en la columna Edad')
            if return_errors:
                return self.df, df_error
        else:
            print('No hay errores en la columna Edad')
            return self.df

    # Método para corregir la cantidad de hijos
    def corregir_cantidad_hijos(self, col:str, return_errors: bool = False):
        """Método para corregir la cantidad de hijos. No se debe haber corrido la función "ajustar_nombre_y_tipo_columnas" antes de correr este método
        Args:
            df (pd.DataFrame): DataFrame con los datos de los donantes
            col (str): Nombre de la columna a revisar
            return_errors (bool, optional): Si es True, retorna los valores que no coincidan con una cantidad de hijos. Defaults to False.
        Returns:
            pd.DataFrame: DataFrame con los valores convertidos en cantidad de hijos"""
        
        # Remover registros con texto en la columna Cantidad de Hijos
        df_error = self.df[self.df[col]=='mas de 10']
        self.df[col] = self.df[col].replace('mas de 10', 10)

        # Llenar faltantes de cantidad de hijos
        self.df[col] = np.where(self.df['Tiene hijos']=='No', 0, self.df[col])
        self.df.fillna(0, inplace=True)
        
        if len(df_error) > 0:
            print('Hay errores en la columna Cantidad de Hijos')
            if return_errors:
                return self.df, df_error
        else:
            print('No hay errores en la columna Cantidad de Hijos')
            return self.df
         # Método para corregir la columna Tiene Hijos
    def corregir_tiene_hijos(self):
        """Método para corregir la columna Tiene Hijos
        Args:
            df (pd.DataFrame): DataFrame con los datos de los donantes
        Returns:
            pd.DataFrame: DataFrame con los valores convertidos en boolean"""

        # Remover registros menores de edad
        self.df['CD_Tiene_Hijos'] = np.where(self.df['VL_Num_Hijos']>0, 'Si', 'No')

        # Convertir la columna Tiene Hijos a boolean
        self.df['CD_Tiene_Hijos'] = np.where(self.df['CD_Tiene_Hijos']=='Si', True, False)
        
        return self.df
        
    # Método para corregir las columnas de fechas
    def corregir_fechas(self, col:str, n_col:str, return_errors: bool=False):
        """Método para corregir las columnas de fechas
        Args:
            df (pd.DataFrame): DataFrame con los datos de los donantes
            col (str): Nombre de la columna a revisar
            n_col (str): Nombre de la nueva columna
            return_errors (bool, optional): Si es True, retorna los valores que no coincidan con una fecha. Defaults to False.
            Returns:
            pd.DataFrame: DataFrame con los valores convertidos en fecha"""
        # Obtener valores que no coincidan con una fecha
        self.df, df_error = self.texto_en_fechas(col)

        # Convertir la columna Fecha de Nacimiento a datetime
        self.df[col] = pd.to_datetime(self.df[col], errors='coerce')

        # Renombrar columna
        self.df.rename(columns={col:n_col}, inplace=True)

        # Retornar el DataFrame
        if len(df_error) > 0:
            if return_errors:
                return self.df, df_error
        else:
            return self.df
<<<<<<< HEAD
        ##Jose prueba
        
=======
        
        # Método para corregir la columna de Churn y Lapsed probability
    def corregir_prob(self, col:str):
        """Método para corregir la columna de Churn
        Args:
            df (pd.DataFrame): DataFrame con los datos de los donantes
            col (str): Nombre de la columna a revisar
        Returns:
            pd.DataFrame: DataFrame con los valores corregidos"""

        # Revisar valores mayores a 1 y dividirlos en 100
        self.df[col] = np.where(self.df[col]>1, self.df[col]/100, self.df[col])
        
        return self.df
    
    # Método para remover donantes con menos de 3 meses de captación
    def remover_donantes_menos_3_meses(self, col:str):
        """Método para remover donantes con menos de 3 meses de captación
        Args:
            df (pd.DataFrame): DataFrame con los datos de los donantes
            col (str): Nombre de la columna a revisar
        Returns:
            pd.DataFrame: DataFrame con los donantes que cumplen la condición"""

        # Obtener la fecha de hoy
        today = dt.datetime.today()

        # Obtener los donantes con menos de 3 meses de captación
        self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
        self.df = self.df[self.df[col]<(dt.datetime(today.year, today.month, today.day) - dt.timedelta(days=90))]

        # Retornar el DataFrame
        return self.df
    
    # Método para reemplazar unidades decimales
    def corregir_ciudades_o_departamentos(self, col:str, ciudad_o_departamento:str):
        """Método para corregir nombres de ciudades o departamentos
        Args:
            df (pd.DataFrame): DataFrame con los datos de las transacciones
            col (str): Nombre de la columna a revisar
            ciudad_odepartamento (str): Ciudad o Departamento, dependiendo de columna a revisar
        Returns:
            pd.DataFrame: DataFrame con los valores corregidos"""
        
        # Reemplaza filas vacías con ' '
        self.df[col] = self.df[col].fillna('')
              
        # Extrae palabras de las filas. Símbolos y números son excuídos
        regex_pattern = r'\b[A-Za-zÀ-ÿ]+\b'
        resultados = []

        for valor in self.df[col]:
            matches = re.findall(regex_pattern, str(valor), re.UNICODE)
            resultado = ' '.join(matches)
            resultados.append(resultado.title())
        
        # Reemplaza la columna con los valores extraídos
        self.df[col] = resultados

        # Reemplaza tíldes por la misma letra sin tílde
        self.df[col] = self.df[col].apply(unidecode)
>>>>>>> 97db40f11206c41c0e6be643eba903ac594e47fa
