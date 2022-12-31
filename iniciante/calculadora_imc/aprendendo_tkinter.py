# Bibliotecas / Libraries:
import requests                                                                                                                  #
import json                                                                                                                      # Operacoes com arquivo JSON
from urllib.request import urlopen                                                                                               # Operacoes com URL e JSON
from tkinter import *                                                                                                            #
import pandas as pd                                                                                                              # Biblioteca de Dataframes

# INPUTS INICIAIS:
stock = 'PETR4'
data_ini = '20190709'
data_fim = '20200709'

def get_stock_prices(stock = 'PETR4',data_ini = '20200101', data_fim = '20221130'):


    # Pelo API da OKANEBOX:
    url = 'https://www.okanebox.com.br/api/acoes/hist/' + str(stock) + '/' + str(data_ini) + '/' + str(data_fim) + '/'
    response = urlopen(url)                                                                                                     # Fazendo request da url inserida
    data_json = json.loads(response.read().decode())                                                                            # Salvando os dados como leitura
    df = pd.DataFrame(data_json)                                                                                                # Convertendo o JSON para dataframe pandas e abrindo o dicionario interno

    # Dicionario de termos da API:
    dict_okanebox = {
        'DATPRG' : 'data_pregao',
        'PREABE' : 'data_abertura',
        'PREMAX' : 'preco_max',
        'PREMIN' : 'preco_min',
        'PREMED' : 'preco_med',
        'PREULT' : 'preco_ult',
        'QUATOT' : 'qtde_negocios',
        'VOLTOT' : 'volume_negocios'
    }
    
    # Reescrevendo as colunas do dataframe:
    df.rename(columns=dict_okanebox, inplace=True)

    print(df)
    print('\nPara checar no navegador:')
    print(url)

# Executando a funcao:
# get_stock_prices(stock, data_ini, data_fim)

