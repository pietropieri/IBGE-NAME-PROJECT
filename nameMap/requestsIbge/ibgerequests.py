#
# IMPORTS
#
import plotly.express as px
import plotly as plt
import json
import requests
import numpy as np
import pandas as pd
from requestsIbge.fomatter_brasilgeoson import strip_accents
from copy import deepcopy
from requestsIbge.cachedict import CacheDict
import sys

class Ibge():
    def __init__(self) -> None:
        # get list of all Brasil UFs in IBGE system
        self.lista_estados = self.requestEstados()
        
        # map all Brasil UFs
        self.estados = self.mapEstados()

        # crate a data frame with Brasil UFs
        self.data_frame = self.createDataFrame()
        
        # name will be used
        self.name = ''

        # max frequency
        self.max_frequency = 0

        # Brasil geojson
        self.brasil_geojson = json.load(open("/home/pietro/IBGE-PROJECT/nameMap/requestsIbge/brasilgeojson.json", "r"))

        # map name image
        self.fig_name = ''

        # dict names
        self.cache = CacheDict(10)

        # list Ibge years
        self.ibge_years = [
            "1930[", "[1930,1940[", "[1940,1950[",
            "[1950,1960[", "[1960,1970[", "[1970,1980[",
            "[1980,1990[", "[1990,2000[", "[2000,2010["
        ]

        # data frame por ano
        self.data_frame_ano = self.createDataFramePerYear()

        self.fig_json = ""


    def requestEstados(self):
        # get all UFs in Brasil
        resquests_estados = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados/")

        # list all UFs        
        lista_estados = resquests_estados.json()

        # return list of Brasil UFs
        return lista_estados

    def mapEstados(self):
        # create a empty dict to map UFs by IBGE id
        estados = {'estado': [], 'nome': [], 'ibgeIds':[]}

        # map all UFs
        for i in range(len(self.lista_estados)):
            # map UFs siglas
            estados['estado'].append(self.lista_estados[i]['sigla'])

            # map UFs name
            estados['nome'].append(strip_accents(self.lista_estados[i]['nome']))

            # map UFs ids
            estados['ibgeIds'].append(self.lista_estados[i]['id'])

        return estados

    def nomePorData(self, nome):
        # get name frenquency in Brasil by years
        request_nome_basico = requests.get(f"https://servicodados.ibge.gov.br/api/v2/censos/nomes/{nome}")
        
        # list name frequency in Brasil by years
        lista_nome_basico = request_nome_basico.json()

        # create a var to compute total name frequenci in Brasil
        total = 0

        # compute name frequency
        for i in range(len(lista_nome_basico)):
            total = total + lista_nome_basico[i]['frequencia']
        return total

    def createDataFrame(self):
        # create a dataframe with states
        data_frame = pd.DataFrame.from_dict(self.estados)
        
        # create a new column with zeros
        data_frame['pessoa'] = 0

        # return data frame
        return data_frame

    def nomePorLocal(self, estado):
        # reset person column
        self.data_frame['pessoa'] = 0

        # get Ibge state id    
        estado_id = list(self.data_frame.loc[self.data_frame.nome == f'{estado}', 'ibgeIds'])[0]

        # get name frenquency in Brasil by localtion
        request_nome_local = requests.get(f"https://servicodados.ibge.gov.br/api/v2/censos/nomes/{self.name}?localidade={estado_id}")

        # total variable initialization
        total = 0  

        # get request json
        try:
            nome_local = request_nome_local.json()[0]

            # calculation of the total value of the name in that locality
            for resposta in nome_local['res']:
                total = total + resposta['frequencia']

            self.data_frame.loc[self.data_frame.ibgeIds == estado_id, 'pessoa'] = total

        except:
            # save name total frequenci in data frame
            self.data_frame.loc[self.data_frame.ibgeIds == estado_id, 'pessoa'] = total

        return None

    def setName(self, nome):
        self.name = nome
        self.nomePorTodosEstadosAno()

    def nomePorTodosEstados(self):
        # reset person column
        self.data_frame['pessoa'] = 0

        # reset max frequency value
        self.max_frequency = 0

        # get name frenquency in Brasil
        for i in self.data_frame['ibgeIds']:
            # get the name frequency by state
            request_nome_local = requests.get(f"https://servicodados.ibge.gov.br/api/v2/censos/nomes/{self.name}?localidade={i}")

            # get request json
            try:
                nome_local = request_nome_local.json()[0]

            except:
                continue

            # total variable initialization
            total = 0        
        
            # calculation of the total value of the name in that locality
            for resposta in nome_local['res']:
                total = total + resposta['frequencia']

            # save name total frequenci in data frame
            self.data_frame.loc[self.data_frame.ibgeIds == i, 'pessoa'] = total

            # get max frequency value
            if self.max_frequency < total:
                self.max_frequency = total
        
        return

    def createFig(self):
        # create map image
        self.fig_name = px.choropleth(data_frame = self.data_frame, locations='estado', geojson = self.brasil_geojson, hover_data = ['estado'], color = 'pessoa', scope = 'south america', range_color = (0,self.max_frequency))
        
        # update image layout
        self.fig_name.update_layout(height=800)
        
        return

    def createDataFramePerYear(self):
        data_frame_copy = deepcopy(self.data_frame)
        data_frame_copy = pd.concat([data_frame_copy]*len(self.ibge_years), ignore_index=True)
        inicio = 0 
        for i in range(len(self.ibge_years)):
            fim = 27 * (i+1)
            data_frame_copy.loc[inicio:fim, 'periodo'] = self.ibge_years[i]
            inicio = fim
        return data_frame_copy


    def nomePorTodosEstadosAno(self):
        # reset person column
        self.data_frame['pessoa'] = 0

        # get name frenquency in Brasil
        for i in self.data_frame['ibgeIds']:
            # get the name frequency by state
            request_nome_local = requests.get(f"https://servicodados.ibge.gov.br/api/v2/censos/nomes/{self.name}?localidade={i}")

            # get request json
            try:
                nome_local = request_nome_local.json()[0]

            except:
                continue
        
            # calculation of the total value of the name in that locality
            for resposta in nome_local['res']:

            # save name total frequenci in data frame
                self.data_frame_ano['pessoa'] = np.where((self.data_frame_ano['ibgeIds'] == i)
                & (self.data_frame_ano['periodo'] == resposta['periodo']), resposta['frequencia'], self.data_frame_ano['pessoa'])

        # get max frequency
        self.max_frequency = self.data_frame_ano['pessoa'].max()

        return

    def createFigAno(self, nome):
        # create map image
        self.fig_name = px.choropleth(data_frame = self.data_frame_ano, locations='estado', geojson = self.brasil_geojson, hover_data = ['estado'], color = 'pessoa', scope = 'south america', range_color = (0,self.max_frequency), animation_frame = 'periodo')
        
        # update image layout
        self.fig_name.update_layout(height=800)

        self.figJson(nome)
        
        return

    def figJson(self, key):
        self.fig_json = json.dumps(self.fig_name, cls=plt.utils.PlotlyJSONEncoder)
        self.cache.put(key, self.fig_json)
        return

