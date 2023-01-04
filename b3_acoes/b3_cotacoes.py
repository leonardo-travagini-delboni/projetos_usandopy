# Creditos:
print('Cotacoes B3 automatizadas diariamente')
print('Desenvolvido por Leonardo Travagini Delboni\n')

# Bibliotecas gerais para todo o programa:
import json                                                                                                                      # Operacoes com arquivo JSON
from urllib.request import urlopen                                                                                               # Operacoes com URL e JSON
import pandas as pd                                                                                                              # Biblioteca de Dataframes
from datetime import datetime                                                                                                    # Biblioteca de tempos e datas
import pdb                                                                                                                       # Biblioteca para debug pelo terminal
import logging                                                                                                                   # Biblioteca para logging
import os                                                                                                                        # Biblioteca para Sistema Operacional
import time                                                                                                                      # Biblioteca para espera de tempo explicita
import requests                                                                                                                  # Biblioteca para request de arquivo JSON
import scrapy                                                                                                                    # Biblioteca para realização de Web Scraping
import investpy as investpy                                                                                                      # 
import matplotlib.pyplot as plt                                                                                                  # Biblioteca para plotagem grafica
from redmail import EmailSender                                                                                                  # Biblioteca para envio de email pelo Gmail
from pathlib import Path                                                                                                         # Biblioteca para checagem e correcao de diretorio
import speedtest                                                                                                                 # Biblioteca para checagem de conexao internet
import argparse                                                                                                                  # Biblioteca Argparse para atribuiçao de paramteros
from redmail import gmail                                                                                                        # Biblioteca para envio de email via Gmail
import telebot                                                                                                                   # Importando a biblioteca do BOT Telegram 


# Importando dados pessoais para envio de email via Gmail:
from config import sender_email                                                                                                 
from config import receiver_email_list
from config import sender_email_password
from config import email_text
from config import assinatura

# INPUTS INICIAIS:
debug_mode = False
stock = 'BBDC4'
data_ini = '20100101'
data_fim = None
send_email = True

# Checando e corrigindo o diretorio de trabalho:
current_dir = os.getcwd()                                                                                                     # Obtendo o diretorio atual
size = int(len(current_dir))                                                                                                  # Salvando o tamanho atual do diretorio
last_dir = current_dir[size-8:size:1]                                                                                         # Obtendo os ultimos caracteres do diretorio final
if last_dir != 'b3_acoes':                                                                                                    # Condicional para correcao de diretorio
    os.chdir(current_dir + '/b3_acoes/')                                                                                      # Reescrevendo o novo diretorio

# Configurando o logging para modo debug ativado e desativado:
format_config = "%(asctime)s - %(filename)s - %(levelname)s - %(lineno)d - %(message)s"                                        # Formato de aviso de alerta logging
for handler in logging.root.handlers[:]:                                                                                       # Removendo todos os handlers anteriores
    logging.root.removeHandler(handler)                                                                                        # Corrigindo problema de falha na criacao
if debug_mode == True:                                                                                                         # Condicional para debug mode on
    pdb.set_trace()                                                                                                            # Ativador de debug pelo terminal
    logname = 'debug_mode_on.log'                                                                                              # Nomeando o arquivo log para debug on
    filename = 'debug_files/' + logname                                                                                        # Descrevendo o diretorio completo
    logging.basicConfig(level=logging.DEBUG, filename = filename, format=format_config)                                        # Configuracao de logging para debug
else:                                                                                                                          # Condicional de debug mode off
    logname = 'debug_mode_off.log'                                                                                             # Nomeando o arquivo log para debug off
    filename = 'debug_files/' + logname                                                                                        # Descrevendo o diretorio completo
    logging.basicConfig(level=logging.INFO, filename = filename, format=format_config)                                         # Configuracao de logging sem debug

# Data e hora atuais:
now = datetime.now()                                                                                                           # Extraindo o momento atual
today = now.strftime("%Y-%M-%d")                                                                                               # Extraindo a data atual como str
data_hoje = now.strftime("%Y%M%d")                                                                                             # Data de hoje no formato yyyy/mm/dd
current_time = now.strftime("%H:%M:%S")                                                                                        # Extraindo a hora atual como str

# Alertas de nova execucao de programa:
logging.info(f'--- NOVA EXECUCAO DO PROGRAMA: {current_time} DE {today} ---')                                                  # Alerta de nova execucao de programa
print(f'--- NOVA EXECUCAO DO PROGRAMA: {current_time} DE {today} ---')                                                         # Alerta de nova execucao de programa

# Creditos do desenvolvedor:
logging.info('Cotacoes B3 automatizadas diariamente. Desenvolvido por Leonardo Travagini Delboni')                             # Creditos do desenvolvedor
print('\nCotacoes B3 automatizadas diariamente.\nDesenvolvido por Leonardo Travagini Delboni\n')                               # Creditos do desenvolvedor

# Checando a internet no momento da execucao do codigo:
st = speedtest.Speedtest()                                                                                                     # Atribuindo o verificador de internet
download_speed = st.download()                                                                                                    
tries = 0
while tries < 11:
    if download_speed <= 0:
        tries += 1
        logging.warning(f'ATENCAO! NAO EXISTE CONEXAO DE INTERNET NO MOMENTO! TENTATIVA {tries} DE 10!')
        print(f'ATENCAO! NAO EXISTE CONEXAO DE INTERNET NO MOMENTO! TENTATIVA {tries} DE 10!')
        time.sleep(5)
        if tries == 10:
            logging.critical('NAO HOUVE CONEXAO COM A INTERNET EM NENHUMA TENTATIVA! ENCERRANDO O PROGRAMA!')
            print('NAO HOUVE CONEXAO COM A INTERNET EM NENHUMA TENTATIVA! ENCERRANDO O PROGRAMA!')
            exit()
    else:
        tries += 1
        logging.debug('OK! CONEXAO COM A INTERNET VERIFICADA!')
        continue
        
# Funcao que busca o dataframe das cotacoes de uma acao em um periodo de tempo:
def get_stock_prices(stock = 'PETR3',data_ini = '19000101', data_fim = None, send_email = False):
    """ Summary:
        Funcao que recebe uma acao, uma data de inicio e uma data de final, e retorna por dataframe das cotacoes atraves da API da OkaneBox.
        Tambem permite plotar o grafico desejado
    Args:
        stock (str): Sigla da acao a ser analisada na cotacao.
        data_ini (str): Data de inicio da busca, no formato AAAAMMDD.
        data_fim (str): Data de final da busca, no formato AAAAMMDD.
    Returns:
        df (dataframe): Dataframe das cotacoes para a acao no periodo estipulado seguindo a formatacao:
        ['data_pregao', 'data_abertura', 'preco_max', 'preco_min', 'preco_med', 'preco_ult', 'qtde_negocios', 'volume_negocios']
    """

    # Extraindo a ultima data disponivel da API do OKANEBOX para a acao desejada:
    url_last_data = 'https://www.okanebox.com.br/api/acoes/ultima/' + str(stock) + '/'                                          # URL para extracao da ultima data disponivel
    resp = requests.get(url_last_data)                                                                                          # Aplicando requests na URL
    resp_dict = resp.json()                                                                                                     # Retornando o arquivo JSON como um dict
    last_data = str(list(resp_dict.values())[0])                                                                                # Extraindo a ultima data como string
    last_data = last_data[0:10]                                                                                                 # Fazendo slicing na parte de interesse da string
    last_data = last_data.replace('-','')                                                                                       # Retirando os caracteres especiais

    # Obtendo a data final maxima disponivel para aplicacao na API completa:
    if data_fim == None or data_fim == 0 or data_fim == '':                                                                     # Checando a data limite da API do OKANEBOX
        data_fim = last_data                                                                         
        logging.info('COMO NAO FOI INFORMADA, CONSIDEROU-SE A DATA FINAL COMO A ULTIMA DISPONIVEL PELA API!')
        print('COMO NAO FOI INFORMADA, CONSIDEROU-SE A DATA FINAL COMO A ULTIMA DISPONIVEL PELA API!')
    elif int(data_fim) > int(last_data):
        data_fim = last_data
        print('COMO A DATA FINAL INSERIDA E MAIOR QUE A ULTIMA DISPONIVEL, CONSIDEROU-SE A ULTIMA DISPONIVEL PELA API!')
        logging.info('COMO A DATA FINAL INSERIDA E MAIOR QUE A ULTIMA DISPONIVEL, CONSIDEROU-SE A ULTIMA DISPONIVEL PELA API!')

    # Pelo API da OKANEBOX:
    url = 'https://www.okanebox.com.br/api/acoes/hist/' + str(stock) + '/' + str(data_ini) + '/' + str(data_fim) + '/'          # Declarando o URL para executar o request da API
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
    del df['aux']                                                                                                               # Deletando a coluna desnecessaria
    df['ano'] = df['data_pregao'].str[0:4:1]                                                                                    # Criando a coluna de ano da data_pregao
    df['mes'] = df['data_pregao'].str[4:6:1]                                                                                    # Criando a coluna de mes da data_pregao
    df['dia'] = df['data_pregao'].str[6:9:1]                                                                                    # Criando a coluna de dia da data_pregao
    df['data'] = pd.to_datetime(dict(year=df['ano'], month=df['mes'], day=df['dia']))                                           # Criando uma coluna de data do tipo datetime
    del df['ano'], df['mes'], df['dia']                                                                                         # Excluindo colunas desnecessarias

    # Plotando os graficos:
    try:
        df.plot(x='data', y=['preco_ult'], kind='line',figsize=(12,10))                                                         # Configurando o grafico a ser plotado
        ini = df['data'].iloc[0].strftime('%d/%m/%Y')                                                                           # Extraindo a data de inicio para legenda
        fim = df['data'].tail(1).iloc[0].strftime('%d/%m/%Y')                                                                   # Extraindo a data de fim para legenda
        titulo = f'Preco de Fechamento do Pregao da acao {stock} entre {ini} e {fim}'                                           # Setando o titulo do grafico a ser plotado
        plt.title(titulo)                                                                                                       # Introduzindo o titulo setado
        plt.xlabel(f'Data do Pregao da acao {stock}')                                                                           # Fornecendo a descricao do eixo x
        plt.ylabel('Preco de Fechamento do Pregao')                                                                             # Fornecendo a descricao do eixo y                                                
        ini2 = df['data'].iloc[0].strftime('%d-%m-%Y')                                                                          # Retirando a barra para nomear arquivo
        fim2 = df['data'].tail(1).iloc[0].strftime('%d-%m-%Y')                                                                  # Retirando a barra para nomear arquivo
        plt.savefig(f'fig_files/{stock}_{ini2}_{fim2}.png')                                                                     # Salvando o arquivo .png no diretorio desejado
        print(f'Figura de {stock} entre {ini2} e {fim2} salvo com sucesso!')                                                    # Aviso de sucesso pelo terminal
        logging.info(f'Figura de {stock} entre {ini2} e {fim2} salvo com sucesso!')                                             # Aviso de sucesso via logging
    except:
        print(f'ERRO! FIGURA DE {stock} ENTRE {ini2} e {fim2} NAO FOI SALVA COM SUCESSO!')                                      # Aviso de sucesso pelo terminal
        logging.error(f'ERRO! FIGURA DE {stock} ENTRE {ini2} e {fim2} NAO FOI SALVA COM SUCESSO!')                              # Aviso de sucesso via logging

    # Salvando o dataframe como arquivo xlsx para consulta via excel:
    try:                                                                                                                        # Caso seja possivel salvar os dados em excel
        df.to_excel(f'xlsx_files/{stock}_{ini2}_{fim2}.xlsx', sheet_name=f'{stock}_{ini2}_{fim2}')                              # Salvando o arquivo como xlsx para consulta excel
        print(f'XLSX de {stock} entre {ini2} e {fim2} salvo com sucesso!')                                                      # Aviso de sucesso pelo terminal
        logging.info(f'XLSX de {stock} entre {ini2} e {fim2} salvo com sucesso!')                                               # Aviso de sucesso via logging
    except:                                                                                                                     # Caso nao seja possivel salvar o xlsx
        print(f'ERRO! XLSX DE {stock} ENTRE {ini2} e {fim2} NAO FOI SALVO COM SUCESSO!')                                        # Aviso de sucesso pelo terminal
        logging.error(f'ERRO! XLSX DE {stock} ENTRE {ini2} e {fim2} NAO FOI SALVO COM SUCESSO!')                                # Aviso de sucesso via logging

    # Salvando o dataframe como arquivo csv para consulta via separacao por ponto e virgula:
    try:                                                                                                                        # Caso seja possivel salvar os dados em excel
        df.to_csv(f'csv_files/{stock}_{ini2}_{fim2}.csv')                                                                       # Salvando o arquivo como csv para consulta csv
        print(f'CSV de {stock} entre {ini2} e {fim2} salvo com sucesso!')                                                       # Aviso de sucesso pelo terminal
        logging.info(f'CSV de {stock} entre {ini2} e {fim2} salvo com sucesso!')                                                # Aviso de sucesso via logging
    except:                                                                                                                     # Caso nao seja possivel salvar o xlsx
        print(f'ERRO! CSV DE {stock} ENTRE {ini2} e {fim2} NAO FOI SALVO COM SUCESSO!')                                         # Aviso de sucesso pelo terminal
        logging.error(f'ERRO! CSV DE {stock} ENTRE {ini2} e {fim2} NAO FOI SALVO COM SUCESSO!')                                 # Aviso de sucesso via logging

    # Enviando e-mail com os resultados conforme desejado:
    if send_email == True:

        try:
            # Atribuindo os parametros de username e password para acessar o Gmail:
            gmail.username = sender_email                                                                                       # Importando o email de sender 
            gmail.password = sender_email_password                                                                              # Importando a senha do email de sender

            # Configuracoes para envio de email através do Gmail:
            gmail.send(                                                                                                         # Enviando atraves do Gmail
                
                # Configurando o envio de email:
                subject = f'Dados da acao {stock} desde {ini} ate {fim}',                                                       # Titulo do email
                sender = sender_email,                                                                                          # Sender email (remetente)
                receivers = receiver_email_list,                                                                                # Lista dos emails recebedores (destinatarios)
                # text = email_text,                                                                                             
                html = email_text + """{{ my_plot }}""" + assinatura,                                                           # Corpo do e-mail em html
                body_images={                                                                                                   # Imagens anexadas no corpo do e-mail
                    'my_plot': f'fig_files/{stock}_{ini2}_{fim2}.png',
                },
                attachments = {                                                                                                 # Lista dos arquivos anexados ao e-mail
                    f'{stock}_{ini2}_{fim2}.xlsx': Path(f'xlsx_files/{stock}_{ini2}_{fim2}.xlsx'),                              # Arquivo XLSX anexado ao e-mail
                    f'{stock}_{ini2}_{fim2}.csv': Path(f'csv_files/{stock}_{ini2}_{fim2}.csv'),                                 # Arquivo CSV anexado ao e-mail
                    f'fig_files/{stock}_{ini2}_{fim2}.png': Path(f'fig_files/{stock}_{ini2}_{fim2}.png'),                       # Arquivo de imagem anexado ao e-mail
                    'raw_file.html': email_text + assinatura,                                                                   # Corpo do e-mail em html anexado ao proprio e-mail
                }
            )
            print(f'Email de {stock}_{ini2}_{fim2} enviado com sucesso!')                                                       # Aviso de sucesso pelo terminal
            logging.info(f'Email de {stock}_{ini2}_{fim2} enviado com sucesso!')                                                # Aviso de sucesso via logging
        except:
            print(f'ERRO! EMAIL DE {stock}_{ini2}_{fim2} NAO FOI ENVIADO!')                                                     # Aviso de sucesso pelo terminal
            logging.info(f'Email de {stock}_{ini2}_{fim2} NAO FOI ENVIADO!')                                                    # Aviso de sucesso via logging

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

    # # Iniciando as Operacoes com o navegador:
    # driver = webdriver.Chrome(service=service, options=options)                                                                  # Inicializando o Driver conforme desejado
    # driver.maximize_window()                                                                                                     # Maximizando o navegador


    # url_b3 = 'https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/empresas-listadas.htm'                   # URL das empresas listadas na B3
    # driver.get(url_b3)                                                                                                           # Acessando a plataforma                                                                              
    # driver.maximize_window()                                                                                                     # Maximizando o navegador
    # driver.implicitly_wait(2.0)                                                                                                  # Espera temporal implicita
    # print('CHECKPOINT 1')
    # cookies_accept_xpath = '/html/body/div[2]/div[3]/div/div[1]/div/div[2]/div/button[3]'
    # driver.find_element('xpath', cookies_accept_xpath).click()
    # driver.implicitly_wait(2.0)                                                                                                  # Espera temporal implicita
    # print('CHECKPOINT 2')
    # driver.find_element(By.CSS_SELECTOR,"#accordionName > div > app-companies-home-filter-name > form > div > div:nth-child(4) > button").click()
    # time.sleep(5.0)                                                                                                  # Espera temporal implicita
    # print('CHECKPOINT 3')

    # ELEMENT:
    # <button type="submit" aria-label="Buscar Todas" class="btn btn-light btn-block mt-3">Todos</button>
    # FULL XPATH:
    # /html/body/app-root/app-companies-home/div/div/div/div/div[1]/div[2]/div/app-companies-home-filter-name/form/div/div[4]/button

    # url_fundamentus = 'https://www.fundamentus.com.br/detalhes.php?papel='

    # Retornando o dataframe e a lista de siglas
    lista_tickers = investpy.get_stocks_list("brazil")
    print('lista_tickers:\n')
    print(len(lista_tickers))

    # Executando o web scraping:
    # lista_tickers = investpy.get_stocks_list("brazil")
    # lista_tickers.sort()
    # lista_tickers_2 = []
    # maximo = len(lista_tickers)

    # for element in lista_tickers:
    #     element = str(element)
    #     element.upper()
    #     element = element.replace(' ','')
    #     lista_tickers_2.append(element)

    # contador = 0
    # for element in lista_tickers_2:
    #     contador += 1
    #     print(f'{contador}: {element}')
    # maximo_2 = len(lista_tickers_2)

    # contador = 0
    # contador_deu_bom = 0
    # contador_deu_ruim = 0
    # vetor_deu_bom = []
    # vetor_deu_ruim = []

    return lista_tickers

# Executando a funcao:
df = get_stock_prices(stock, data_ini, data_fim, send_email)
print(df)