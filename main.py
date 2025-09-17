from fastapi import FastAPI
import requests
from pydantic import BaseModel


app = FastAPI(title='API de Coordenadas', version='1.0')
url = '20.81.234.239'
perimeter_data = {
    'y': {
        'up': None,
        'down': None
    },
    'x': {
        'left': None,
        'right': None
    }
}

def hemisferios(coord: list[str, str]) -> dict:
    """
    Serve para retornar em que hemisfério do mapa está localizado.
    """
    if float(coord[0]) > 0:
        hemisferio_lat = "Norte"
    else:
        hemisferio_lat = "Sul"

    if float(coord[1]) > 0:
        hemisferio_lon = "Leste"
    else:
        hemisferio_lon = "Oeste"

    return {'y': hemisferio_lat,'x': hemisferio_lon}


@app.get('/coord/hemisferios')
def hemisferios_get() -> dict:
    request = requests.get(f'http://{url}:1026/v2/entities/urn:ngsi-ld:Gps:001/attrs/coord', headers={'fiware-service': 'smart', 'fiware-servicepath': '/', 'accept': 'application/json'})
    response = request.json()['value'].split(' ')
    return hemisferios(response)

@app.get('/coord/lat')
def lat_get() -> dict:
    request = requests.get(f'http://{url}:1026/v2/entities/urn:ngsi-ld:Gps:001/attrs/coord', headers={'fiware-service': 'smart', 'fiware-servicepath': '/', 'accept': 'application/json'})
    response = request.json()['value'].split(' ')[0]
    return {'y': response}

@app.get('/coord/long')
def long_get() -> dict:
    request = requests.get(f'http://{url}:1026/v2/entities/urn:ngsi-ld:Gps:001/attrs/coord', headers={'fiware-service': 'smart', 'fiware-servicepath': '/', 'accept': 'application/json'})
    response = request.json()['value'].split(' ')[1]
    return {'x': response}

@app.get('/coord/latlong')
def lat_long_get() -> dict:
    request = requests.get(f'http://{url}:1026/v2/entities/urn:ngsi-ld:Gps:001/attrs/coord', headers={'fiware-service': 'smart', 'fiware-servicepath': '/', 'accept': 'application/json'})
    response = request.json()['value'].split(' ')
    return {'y': response[0], 'x': response[1]}

@app.get('/coord/latlong/historic')
def lat_long_historic() -> dict:
    request = requests.get(f'http://{url}:8666/STH/v1/contextEntities/type/Gps/id/urn:ngsi-ld:Gps:001/attributes/coord?lastN=10', headers={'fiware-service': 'smart', 'fiware-servicepath': '/'})
    response = request.json()['contextResponses'][0]['contextElement']['attributes'][0]['values']

    hist = []
    for i in response:
        value_arr = i['attrValue'].split(' ')
        list_yx = {
            'y': value_arr[0],
            'x': value_arr[1]
        }
        hist.append(list_yx)

    return {'historico': hist}

class Perimeter(BaseModel):
    y: dict = {
        'up': str,
        'down': str
    }
    x: dict = {
        'left': str,
        'right': str
    }

@app.post('/coord/define')
def lockin_perimeter(perimeter: Perimeter) -> dict:
    global perimeter_data
    perimeter_data = perimeter.__dict__
    return {'status': 'Atualizado!', 'perimetro_data': perimeter_data}

@app.get('/coord/lat/100')
def lat_100_get() -> dict:
    request = requests.get(f'http://{url}:1026/v2/entities/urn:ngsi-ld:Gps:001/attrs/coord', headers={'fiware-service': 'smart', 'fiware-servicepath': '/', 'accept': 'application/json'})
    response = request.json()['value'].split(' ')[0]

    if perimeter_data['y']['up'] == None or perimeter_data['y']['down'] == None:
        return {'y': 'Atualize primeiro o perimeter antes de mandar'}

    intervalo_total = float(perimeter_data['y']['up']) - float(perimeter_data['y']['down'])
    intervalo_parcial = float(response) - float(perimeter_data['y']['down'])

    resultado = (-100) + ((intervalo_parcial * 200)/intervalo_total)

    return {'y': resultado}

@app.get('/coord/long/100')
def long_100_get() -> dict:
    request = requests.get(f'http://{url}:1026/v2/entities/urn:ngsi-ld:Gps:001/attrs/coord', headers={'fiware-service': 'smart', 'fiware-servicepath': '/', 'accept': 'application/json'})
    response = request.json()['value'].split(' ')[1]

    if perimeter_data['x']['left'] == None or perimeter_data['x']['right'] == None:
        return {'x': 'Atualize primeiro o perimeter antes de mandar'}

    intervalo_total = float(perimeter_data['x']['left']) - float(perimeter_data['x']['right'])
    intervalo_parcial = float(response) - float(perimeter_data['x']['right'])

    resultado = (-100) + ((intervalo_parcial * 200)/intervalo_total)

    return {'x': resultado}

@app.get('/coord/latlong/100')
def lat_long_100_get() -> dict:
    request = requests.get(f'http://{url}:1026/v2/entities/urn:ngsi-ld:Gps:001/attrs/coord', headers={'fiware-service': 'smart', 'fiware-servicepath': '/', 'accept': 'application/json'})
    response = request.json()['value'].split(' ')

    if perimeter_data['y']['up'] == None or perimeter_data['y']['down'] == None or perimeter_data['x']['left'] == None or perimeter_data['x']['right'] == None:
        return {'y': 'Atualize primeiro o perimeter antes de mandar', 'x': 'Atualize primeiro o perimeter antes de mandar'}

    intervalo_totaly = float(perimeter_data['y']['up']) - float(perimeter_data['y']['down'])
    intervalo_parcialy = float(response[0]) - float(perimeter_data['y']['down'])

    resultadoy = (-100) + ((intervalo_parcialy * 200)/intervalo_totaly)

    intervalo_totalx = float(perimeter_data['x']['left']) - float(perimeter_data['x']['right'])
    intervalo_parcialx = float(response[1]) - float(perimeter_data['x']['right'])

    resultadox = (-100) + ((intervalo_parcialx * 200)/intervalo_totalx)

    return {'y': resultadoy, 'x': resultadox}

@app.get('/coord/latlong/100/historic')
def lat_long_100_historic() -> dict:
    request = requests.get(f'http://{url}:8666/STH/v1/contextEntities/type/Gps/id/urn:ngsi-ld:Gps:001/attributes/coord?lastN=10', headers={'fiware-service': 'smart', 'fiware-servicepath': '/'})
    response = request.json()['contextResponses'][0]['contextElement']['attributes'][0]['values']
    if perimeter_data['y']['up'] == None or perimeter_data['y']['down'] == None or perimeter_data['x']['left'] == None or perimeter_data['x']['right'] == None:
        return {'y': 'Atualize primeiro o perimeter antes de mandar', 'x': 'Atualize primeiro o perimeter antes de mandar'}
    
    hist = []
    for i in response:
        value_arr = i['attrValue'].split(' ')

        intervalo_totaly = float(perimeter_data['y']['up']) - float(perimeter_data['y']['down'])
        intervalo_parcialy = float(value_arr[0]) - float(perimeter_data['y']['down'])

        resultadoy = (-100) + ((intervalo_parcialy * 200)/intervalo_totaly)

        intervalo_totalx = float(perimeter_data['x']['left']) - float(perimeter_data['x']['right'])
        intervalo_parcialx = float(value_arr[1]) - float(perimeter_data['x']['right'])

        resultadox = (-100) + ((intervalo_parcialx * 200)/intervalo_totalx)

        list_yx = {
            'y': resultadoy,
            'x': resultadox
        }
        hist.append(list_yx)

    return {'historico': hist}