import json
import os
import uuid
def verify_database():
    """
    Verifica se o arquivo 'database.json' existe no diretório atual.

    Se o arquivo não for encontrado, esta função o criará
    com uma lista JSON vazia ('[]') como conteúdo padrão.
    Isso é crucial para evitar erros de 'FileNotFound' ou 'JSONDecodeError'
    nas outras funções que tentam ler o arquivo.
    """
    if not os.path.exists("./database.json"):
        with open("database.json", "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)

def read_matchcoord_database() -> list:
    """
    Lê todo o conteúdo do arquivo 'database.json'.

    Abre o arquivo no modo 'r' (read - leitura) e carrega
    seu conteúdo JSON para uma estrutura de dados Python (uma lista de dicionários).

    Retorna:
        list: Uma lista de dicionários, onde cada dicionário representa
              um registro de coordenada. Retorna lista vazia se o
              arquivo estiver vazio.
    """
    with open("database.json", 'r', encoding='utf-8') as f:
        return json.load(f)
    
def create_matchcoord_database(name:str, xleft: float, xright: float, yup: float, ydown: float) -> int:
    """
    Adiciona um novo registro de coordenada ao 'database.json'.

    Esta função primeiro lê todos os dados existentes, depois
    adiciona ('append') um novo dicionário a essa lista.
    O novo dicionário contém os dados fornecidos e um 'id'
    único gerado com 'uuid.uuid4()'.
    Finalmente, ela sobrescreve o 'database.json' com a lista atualizada.

    Args:
        name (str): O nome descritivo para este conjunto de coordenadas.
        xleft (float): Limite da coordenada X esquerda.
        xright (float): Limite da coordenada X direita.
        yup (float): Limite da coordenada Y superior.
        ydown (float): Limite da coordenada Y inferior.

    Returns:
        int: Retorna 1 para indicar sucesso na operação.
    """
    data = read_matchcoord_database()
    data.append({
        'id': str(uuid.uuid4()),
        'name': name,
        'y': {
            'up': yup,
            'down': ydown
        },
        'x': {
            'left': xleft,
            'right': xright
        }
    })
    with open("database.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    return 1

def delete_matchcoord_database(id: str) -> int:
    """
    Remove um registro de coordenada do 'database.json' usando o 'id'.

    A função lê todos os dados, itera pela lista para encontrar
    o índice (posição) do item que corresponde ao 'id' fornecido.
    Se o 'id' for encontrado, o item é removido da lista ('data.pop(index)')
    e o arquivo é reescrito.

    Args:
        id (str): O UUID do registro a ser deletado.

    Returns:
        int: Retorna 1 se a exclusão for bem-sucedida,
             ou -1 se o 'id' não for encontrado.
    """
    data = read_matchcoord_database()
    index= None
    for i in range(len(data)):
        if data[i]["id"] == id:
            index = i
            break
    if index == None:
        return -1
    else:
        data.pop(index)
        with open("database.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        return 1
    
def update_matchcoord_database(id: str, name: str = None, xleft: float = None, xright: float = None, yup: float = None, ydown: float = None) -> int:
    """
    Atualiza um registro de coordenada existente, permitindo alterações parciais.

    Busca o item pelo 'id'. Se um novo valor (ex: 'name') for fornecido,
    ele é usado. Se o novo valor for 'None' (o padrão), o valor antigo
    que já estava no registro é mantido.

    Args:
        id (str): O UUID do registro a ser atualizado.
        name (Optional[str]): O novo nome (ou None para não alterar).
        xleft (Optional[float]): O novo xleft (ou None para não alterar).
        xright (Optional[float]): O novo xright (ou None para não alterar).
        yup (Optional[float]): O novo yup (ou None para não alterar).
        ydown (Optional[float]): O novo ydown (ou None para não alterar).

    Returns:
        int: Retorna 1 se a atualização for bem-sucedida,
             ou -1 se o 'id' não for encontrado.
    """
    data = read_matchcoord_database()
    index= None
    for i in range(len(data)):
        if data[i]["id"] == id:
            index = i
            break
    if index == None:
        return -1
    else:
        new_name   = data[i]["name"]   if name == None   else name
        new_xleft  = data[i]["x"]["left"]  if xleft == None  else xleft
        new_xright = data[i]["x"]["right"] if xright == None else xright
        new_yup    = data[i]["y"]["up"]    if yup == None    else yup
        new_ydown  = data[i]["y"]["down"]  if ydown == None  else ydown
        data[i]["name"]       = new_name
        data[i]["y"]["up"]    = new_yup
        data[i]["y"]["down"]  = new_ydown
        data[i]["x"]["left"]  = new_xleft
        data[i]["x"]["right"] = new_xright
        with open("database.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        return 1
