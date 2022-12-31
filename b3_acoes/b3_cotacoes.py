# Creditos:
print('Cotacoes B3 automatizadas diariamente')
print('Desenvolvido por Leonardo Travagini Delboni\n')

# Bibliotecas / Libraries:
import json                                                                                                                      # Operacoes com arquivo JSON
from urllib.request import urlopen                                                                                               # Operacoes com URL e JSON
import pandas as pd                                                                                                              # Biblioteca de Dataframes
from datetime import datetime                                                                                                    # Biblioteca de tempos e datas
import pdb                                                                                                                       # Biblioteca para debug pelo terminal
import logging                                                                                                                   # Biblioteca para logging
import os                                                                                                                        # Biblioteca para Sistema Operacional
import time                                                                                                                      # Biblioteca para espera de tempo explicita

# INPUTS INICIAIS:
debug_mode = False

# Configurando o logging para modo debug ativado e desativado:
format_config = "%(asctime)s - %(filename)s - %(levelname)s - %(lineno)d - %(message)s"                                        # Formato de aviso de alerta logging
for handler in logging.root.handlers[:]:                                                                                       # Removendo todos os handlers anteriores
    logging.root.removeHandler(handler)                                                                                        # Corrigindo problema de falha na criacao
if debug_mode == True:                                                                                                         # Condicional para debug mode on
    pdb.set_trace()                                                                                                            # Ativador de debug pelo terminal
    logname = 'debug_mode_on.log'                                                                                              # Nomeando o arquivo log para debug on
    logging.basicConfig(level=logging.DEBUG, filename = logname, format=format_config)                                         # Configuracao de logging para debug
else:                                                                                                                          # Condicional de debug mode off
    logname = 'debug_mode_off.log'                                                                                             # Nomeando o arquivo log para debug off
    logging.basicConfig(level=logging.INFO, filename = logname, format=format_config)                                          # Configuracao de logging sem debug

# Data e hora atuais:
now = datetime.now()                                                                                                           # Extraindo o momento atual
today = now.strftime("%Y-%M-%d")                                                                                               # Extraindo a data atual como str
current_time = now.strftime("%H:%M:%S")                                                                                        # Extraindo a hora atual como str

# Alertas de nova execucao de programa:
logging.info(f'--- NOVA EXECUCAO DO PROGRAMA: {current_time} DE {today} ---')                                                  # Alerta de nova execucao de programa
print(f'--- NOVA EXECUCAO DO PROGRAMA: {current_time} DE {today} ---')                                                         # Alerta de nova execucao de programa 

# Creditos do desenvolvedor:
logging.info('Cotacoes B3 automatizadas diariamente. Desenvolvido por Leonardo Travagini Delboni')                             # Creditos do desenvolvedor
print('\nCotacoes B3 automatizadas diariamente.\nDesenvolvido por Leonardo Travagini Delboni\n')                               # Creditos do desenvolvedor

# Funcao que busca o dataframe das cotacoes de uma acao em um periodo de tempo:
def get_stock_prices(stock = 'PETR3',data_ini = '20000101', data_fim = '20221130'):
    """ Summary:
        Funcao que recebe uma acao, uma data de inicio e uma data de final, 
        e retorna po dataframe das cotacoes atraves da API da OkaneBox.
    Args:
        stock (str): Sigla da acao a ser analisada na cotacao.
        data_ini (str): Data de inicio da busca, no formato AAAAMMDD.
        data_fim (str): Data de final da busca, no formato AAAAMMDD.
    Returns:
        df (dataframe): Dataframe das cotacoes para a acao no periodo estipulado seguindo a formatacao:
        ['data_pregao', 'data_abertura', 'preco_max', 'preco_min', 'preco_med', 'preco_ult', 'qtde_negocios', 'volume_negocios']
    """
    # Pelo API da OKANEBOX:
    url = 'https://www.okanebox.com.br/api/acoes/hist/' + str(stock) + '/' + str(data_ini) + '/' + str(data_fim) + '/'
    response = urlopen(url)                                                                                                     # Fazendo request da url inserida
    data_json = json.loads(response.read().decode())                                                                            # Salvando os dados como leitura
    df = pd.DataFrame(data_json)                                                                                                # Convertendo o JSON para dataframe pandas e abrindo o dicionario interno

    # Dicionario de termos da API para renomeacao das colunas
    dict_okanebox = {
        'DATPRG' : 'data_pregao', 'PREABE' : 'preco_abert', 'PREMAX' : 'preco_max', 'PREMIN' : 'preco_min',
        'PREMED' : 'preco_med', 'PREULT' : 'preco_ult', 'QUATOT' : 'qtde_negocios', 'VOLTOT' : 'volume_negocios'
        }
    
    # Iniciando a manipulacao dos dados:
    df.rename(columns=dict_okanebox, inplace=True)                                                                              # Reescrevendo as colunas do dataframe
    df['data_pregao'] = df['data_pregao'].astype(str).str.replace('-','',regex=True)                                            # Convertendo para str e removendo os hifens
    df[['data_pregao','aux']] = df['data_pregao'].str.split("T",expand=True)                                                    # Quebrando a coluna e mantendo apenas a data
    del df['aux']                                                                                                               # Deletando a coluna desnecessária

    # Retornando o dataframe final desejado:
    return df

# Funcao que busca todas as empresas listadas na B3 e retorna uma lista com todas as siglas e um dataframe detalhado de todas:
def get_all_b3_stock_companies():

    # Configurando o Selenium pelo Google Chrome:
    from selenium import webdriver                                                                                               # Biblioteca para browser
    from selenium.webdriver.common.by import By                                                                                  # Importando o comando By do Webdriver
    from selenium.webdriver.common.keys import Keys                                                                              # Importando as Keys do Webdriver
    from selenium.webdriver.chrome.service import Service                                                                        # Importando o Service para o Chrome
    from webdriver_manager.chrome import ChromeDriverManager                                                                     # Importando o Google Chrome

    # Configurando o Google Chrome:
    options = webdriver.ChromeOptions()                                                                                          # Configurando as opcoes do Google Chrome
    options.add_experimental_option('excludeSwitches', ['enable-logging'])                                                       # Desabilitando aviso de DevTools Listening
    options.add_experimental_option("detach", True)                                                                              # Mantendo o driver aberto
    service = Service(ChromeDriverManager().install())                                                                           # Configurando o Service do Google Chrome

    # Iniciando as Operacoes com o navegador:
    driver = webdriver.Chrome(service=service, options=options)                                                                  # Inicializando o Driver conforme desejado
    url_b3 = 'https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/empresas-listadas.htm'                   # URL das empresas listadas na B3
    driver.get(url_b3)                                                                                                           # Acessando a plataforma                                                                              
    driver.maximize_window()                                                                                                     # Maximizando o navegador
    driver.implicitly_wait(2.0)                                                                                                  # Espera temporal implicita
    print('CHECKPOINT 1')
    cookies_accept_xpath = '/html/body/div[2]/div[3]/div/div[1]/div/div[2]/div/button[3]'
    driver.find_element('xpath', cookies_accept_xpath).click()
    driver.implicitly_wait(2.0)                                                                                                  # Espera temporal implicita
    print('CHECKPOINT 2')
    driver.find_element(By.CSS_SELECTOR,"#accordionName > div > app-companies-home-filter-name > form > div > div:nth-child(4) > button").click()
    time.sleep(5.0)                                                                                                  # Espera temporal implicita
    print('CHECKPOINT 3')

    # ELEMENT:
    # <button type="submit" aria-label="Buscar Todas" class="btn btn-light btn-block mt-3">Todos</button>
    # FULL XPATH:
    # /html/body/app-root/app-companies-home/div/div/div/div/div[1]/div[2]/div/app-companies-home-filter-name/form/div/div[4]/button

    # Retornando o dataframe e a lista de siglas
    return True

# Executando o web scraping:
get_all_b3_stock_companies()
