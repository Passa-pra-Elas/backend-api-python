from fastapi import FastAPI
import requests
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Union, Any

# Cria a aplicação FastAPI.
# O título e a versão são importantes para a documentação automática da API.
app = FastAPI(title='API de Coordenadas', version='1.0')

# Define as origens permitidas (domínios) que podem fazer requisições à sua API.
# Isso é essencial para segurança e para evitar problemas de CORS em navegadores.
# O "*" é usado em ambientes de desenvolvimento para permitir todas as origens.
origins: List[str] = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "*"
]

# Adiciona o middleware CORS à aplicação.
# O middleware é um "intermediário" que processa as requisições antes que elas cheguem às rotas.
# Ele configura os cabeçalhos HTTP necessários para que os navegadores permitam as requisições de outras origens.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP (GET, POST, PUT, DELETE, etc.).
    allow_headers=["*"],  # Permite todos os cabeçalhos na requisição.
)

# Endereço IP do servidor de dados.
# Este é o ponto de acesso para buscar os dados de coordenadas em um servidor externo,
# provavelmente um Orion Context Broker.
url: str = '20.81.234.239'

# Dicionário global para armazenar os limites do perímetro.
# Este perímetro é definido pelo usuário via um endpoint POST.
# Os valores 'up', 'down', 'left' e 'right' são os limites de latitude e longitude.
perimeter_data: Dict[str, Dict[str, Union[float, None]]] = {
    'y': {  # 'y' representa a latitude
        'up': None,
        'down': None
    },
    'x': {  # 'x' representa a longitude
        'left': None,
        'right': None
    }
}

def hemisferios(coord: List[str]) -> Dict[str, str]:
    """
    Determina o hemisfério de uma coordenada.

    Esta função recebe uma lista contendo a latitude e a longitude como strings.
    Ela converte os valores para números flutuantes e usa o sinal
    (positivo/negativo) para determinar o hemisfério de cada coordenada.
    Valores positivos de latitude são Norte, negativos são Sul.
    Valores positivos de longitude são Leste, negativos são Oeste.
    """
    if float(coord[0]) > 0:
        hemisferio_lat = "Norte"
    else:
        hemisferio_lat = "Sul"

    if float(coord[1]) > 0:
        hemisferio_lon = "Leste"
    else:
        hemisferio_lon = "Oeste"

    return {'y': hemisferio_lat, 'x': hemisferio_lon}

@app.get('/coord/hemisferios')
def hemisferios_get() -> Dict[str, str]:
    """
    Busca a coordenada atual e retorna o hemisfério.

    Este endpoint faz uma requisição HTTP GET para um servidor externo (Orion Context Broker)
    para obter a coordenada atual. A resposta JSON é processada para extrair a coordenada,
    e a função `hemisferios` é chamada para determinar e retornar o hemisfério.
    """
    request = requests.get(f'http://{url}:1026/v2/entities/urn:ngsi-ld:Gps:001/attrs/coord', headers={'fiware-service': 'smart', 'fiware-servicepath': '/', 'accept': 'application/json'})
    response: List[str] = request.json()['value'].split(' ')
    return hemisferios(response)

@app.get('/coord/lat')
def lat_get() -> Dict[str, str]:
    """
    Busca e retorna apenas a latitude atual.

    Similar a outros endpoints, este faz uma requisição ao servidor externo para
    obter a coordenada completa, mas retorna apenas a primeira parte da string,
    que corresponde à latitude.
    """
    request = requests.get(f'http://{url}:1026/v2/entities/urn:ngsi-ld:Gps:001/attrs/coord', headers={'fiware-service': 'smart', 'fiware-servicepath': '/', 'accept': 'application/json'})
    response: str = request.json()['value'].split(' ')[0]
    return {'y': response}

@app.get('/coord/long')
def long_get() -> Dict[str, str]:
    """
    Busca e retorna apenas a longitude atual.

    Este endpoint busca a coordenada completa e extrai a segunda parte da string,
    que corresponde à longitude, para retornar ao cliente.
    """
    request = requests.get(f'http://{url}:1026/v2/entities/urn:ngsi-ld:Gps:001/attrs/coord', headers={'fiware-service': 'smart', 'fiware-servicepath': '/', 'accept': 'application/json'})
    response: str = request.json()['value'].split(' ')[1]
    return {'x': response}

@app.get('/coord/latlong')
def lat_long_get() -> Dict[str, str]:
    """
    Busca e retorna a latitude e a longitude atuais.

    Este endpoint é usado para obter a coordenada completa em um formato
    estruturado de dicionário, com 'y' para latitude e 'x' para longitude.
    """
    request = requests.get(f'http://{url}:1026/v2/entities/urn:ngsi-ld:Gps:001/attrs/coord', headers={'fiware-service': 'smart', 'fiware-servicepath': '/', 'accept': 'application/json'})
    response: List[str] = request.json()['value'].split(' ')
    return {'y': response[0], 'x': response[1]}

@app.get('/coord/latlong/historic')
def lat_long_historic() -> Dict[str, List[Dict[str, str]]]:
    """
    Busca e retorna as últimas 10 coordenadas históricas.

    Faz uma requisição para um serviço de dados históricos (provavelmente o QuantumLeap,
    que armazena dados de contexto do FIWARE). A resposta, que contém as últimas 10
    coordenadas, é iterada e formatada em uma lista de dicionários para facilitar o uso.
    """
    request = requests.get(f'http://{url}:8666/STH/v1/contextEntities/type/Gps/id/urn:ngsi-ld:Gps:001/attributes/coord?lastN=10', headers={'fiware-service': 'smart', 'fiware-servicepath': '/'})
    response: List[Dict[str, Any]] = request.json()['contextResponses'][0]['contextElement']['attributes'][0]['values']

    hist: List[Dict[str, str]] = []
    # Itera sobre cada item do histórico para formatá-lo.
    for i in response:
        value_arr: List[str] = i['attrValue'].split(' ')
        list_yx: Dict[str, str] = {
            'y': value_arr[0],
            'x': value_arr[1]
        }
        hist.append(list_yx)

    return {'historico': hist}

# Classe Pydantic para validar os dados do perímetro.
# FastAPI usa Pydantic para garantir que os dados recebidos via POST estejam no formato correto.
class Perimeter(BaseModel):
    """
    Define o formato do perímetro para o endpoint POST.

    Garante que a requisição POST tenha as chaves 'y' e 'x', e que cada uma
    contenha 'up', 'down', 'left' e 'right' com valores do tipo string.
    """
    y: Dict[str, str]
    x: Dict[str, str]

@app.post('/coord/define')
def lockin_perimeter(perimeter: Perimeter) -> Dict[str, Union[str, Dict[str, Dict[str, str]]]]:
    """
    Define e armazena os limites do perímetro.

    Este é o endpoint responsável por configurar a área de interesse.
    Ele recebe um objeto JSON, que o Pydantic valida, e armazena
    esses valores na variável global `perimeter_data` para uso em endpoints futuros.
    """
    global perimeter_data
    # .model_dump() é o método recomendado para converter modelos Pydantic em dicionários.
    perimeter_data = perimeter.model_dump()
    return {'status': 'Atualizado!', 'perimetro_data': perimeter_data}

@app.get('/coord/lat/100')
def lat_100_get() -> Dict[str, Union[str, float]]:
    """
    Calcula e retorna a latitude em uma escala de -100 a 100.

    Esta rota pega a latitude atual e a mapeia para uma nova escala. A fórmula
    utiliza o intervalo total do perímetro definido e a posição atual para
    calcular uma nova posição percentual, que é então ajustada para a escala [-100, 100].
    Se o perímetro não estiver definido, retorna uma mensagem de erro.
    """
    request = requests.get(f'http://{url}:1026/v2/entities/urn:ngsi-ld:Gps:001/attrs/coord', headers={'fiware-service': 'smart', 'fiware-servicepath': '/', 'accept': 'application/json'})
    response: str = request.json()['value'].split(' ')[0]

    if perimeter_data['y']['up'] is None or perimeter_data['y']['down'] is None:
        return {'y': 'Atualize primeiro o perimeter antes de mandar'}

    # Cálculo de interpolação linear para mapear o valor.
    intervalo_total: float = float(perimeter_data['y']['up']) - float(perimeter_data['y']['down'])
    intervalo_parcial: float = float(response) - float(perimeter_data['y']['down'])
    resultado: float = (-100) + ((intervalo_parcial * 200) / intervalo_total)

    return {'y': resultado}

@app.get('/coord/long/100')
def long_100_get() -> Dict[str, Union[str, float]]:
    """
    Calcula e retorna a longitude em uma escala de -100 a 100.

    Funciona exatamente como o endpoint `/lat/100`, mas aplica a lógica de
    mapeamento para a longitude, usando os limites definidos para o eixo 'x'.
    """
    request = requests.get(f'http://{url}:1026/v2/entities/urn:ngsi-ld:Gps:001/attrs/coord', headers={'fiware-service': 'smart', 'fiware-servicepath': '/', 'accept': 'application/json'})
    response: str = request.json()['value'].split(' ')[1]

    if perimeter_data['x']['left'] is None or perimeter_data['x']['right'] is None:
        return {'x': 'Atualize primeiro o perimeter antes de mandar'}

    # Cálculo de interpolação linear para mapear o valor.
    intervalo_total: float = float(perimeter_data['x']['left']) - float(perimeter_data['x']['right'])
    intervalo_parcial: float = float(response) - float(perimeter_data['x']['right'])
    resultado: float = (-100) + ((intervalo_parcial * 200) / intervalo_total)

    return {'x': resultado}

@app.get('/coord/latlong/100')
def lat_long_100_get() -> Dict[str, Union[str, float]]:
    """
    Calcula e retorna a latitude e a longitude na escala de -100 a 100.

    Combina a lógica dos endpoints `/lat/100` e `/long/100` para retornar
    ambos os valores escalados em uma única resposta.
    """
    request = requests.get(f'http://{url}:1026/v2/entities/urn:ngsi-ld:Gps:001/attrs/coord', headers={'fiware-service': 'smart', 'fiware-servicepath': '/', 'accept': 'application/json'})
    response: List[str] = request.json()['value'].split(' ')

    if perimeter_data['y']['up'] is None or perimeter_data['y']['down'] is None or perimeter_data['x']['left'] is None or perimeter_data['x']['right'] is None:
        return {'y': 'Atualize primeiro o perimeter antes de mandar', 'x': 'Atualize primeiro o perimeter antes de mandar'}

    # Cálculo da latitude escalada.
    intervalo_totaly: float = float(perimeter_data['y']['up']) - float(perimeter_data['y']['down'])
    intervalo_parcialy: float = float(response[0]) - float(perimeter_data['y']['down'])
    resultadoy: float = (-100) + ((intervalo_parcialy * 200) / intervalo_totaly)

    # Cálculo da longitude escalada.
    intervalo_totalx: float = float(perimeter_data['x']['left']) - float(perimeter_data['x']['right'])
    intervalo_parcialx: float = float(response[1]) - float(perimeter_data['x']['right'])
    resultadox: float = (-100) + ((intervalo_parcialx * 200) / intervalo_totalx)

    return {'y': resultadoy, 'x': resultadox}

@app.get('/coord/latlong/100/historic')
def lat_long_100_historic() -> Dict[str, Union[List[Dict[str, float]], str]]:
    """
    Busca as últimas 10 coordenadas históricas e as retorna em uma escala de -100 a 100.

    Esta rota é a versão histórica do endpoint `/latlong/100`. Ela busca um
    histórico de coordenadas e aplica o mesmo cálculo de escala a cada ponto
    histórico, retornando uma lista de coordenadas já transformadas.
    """
    request = requests.get(f'http://{url}:8666/STH/v1/contextEntities/type/Gps/id/urn:ngsi-ld:Gps:001/attributes/coord?lastN=10', headers={'fiware-service': 'smart', 'fiware-servicepath': '/'})
    response: List[Dict[str, Any]] = request.json()['contextResponses'][0]['contextElement']['attributes'][0]['values']
    
    if perimeter_data['y']['up'] is None or perimeter_data['y']['down'] is None or perimeter_data['x']['left'] is None or perimeter_data['x']['right'] is None:
        return {'historico': 'Atualize primeiro o perimeter antes de mandar'}
    
    hist: List[Dict[str, float]] = []
    # Itera sobre os dados históricos para aplicar o cálculo de escala em cada ponto.
    for i in response:
        value_arr: List[str] = i['attrValue'].split(' ')

        # Cálculo da latitude escalada.
        intervalo_totaly: float = float(perimeter_data['y']['up']) - float(perimeter_data['y']['down'])
        intervalo_parcialy: float = float(value_arr[0]) - float(perimeter_data['y']['down'])
        resultadoy: float = (-100) + ((intervalo_parcialy * 200) / intervalo_totaly)

        # Cálculo da longitude escalada.
        intervalo_totalx: float = float(perimeter_data['x']['left']) - float(perimeter_data['x']['right'])
        intervalo_parcialx: float = float(value_arr[1]) - float(perimeter_data['x']['right'])
        resultadox: float = (-100) + ((intervalo_parcialx * 200) / intervalo_totalx)

        list_yx: Dict[str, float] = {
            'y': resultadoy,
            'x': resultadox
        }
        hist.append(list_yx)

    return {'historico': hist}