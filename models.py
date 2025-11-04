from pydantic import BaseModel
from typing import Optional

# DTO (Data Transfer Object) é um padrão de projeto usado para transferir dados
# entre diferentes camadas de uma aplicação, como entre o cliente (navegador)
# e o servidor (nossa API). Em vez de expor a estrutura interna do banco de dados,
# criamos esses modelos Pydantic para definir exatamente quais dados nossa API
# espera receber e quais dados ela irá enviar.

class X_template(BaseModel):
    """
    Define a estrutura para as coordenadas do eixo X (longitude).
    
    Este modelo é reutilizado em outros DTOs para garantir uma estrutura
    consistente para os limites de longitude.
    """
    left: float = None
    right: float = None

class Y_template(BaseModel):
    """
    Define a estrutura para as coordenadas do eixo Y (latitude).
    
    Assim como o X_template, este modelo é reutilizado para padronizar
    a estrutura dos limites de latitude.
    """
    up: float = None
    down : float = None

class CreatePerimeterDTO(BaseModel):
    """
    DTO para a criação de um novo perímetro.
    
    Define os campos obrigatórios que o cliente deve enviar ao criar um
    perímetro. A API usará este modelo para validar se a requisição
    contém um nome e os objetos 'x' e 'y' com a estrutura correta.
    """
    name: str
    x: X_template
    y: Y_template

class UpdatePerimeterDTO(BaseModel):
    """
    DTO para a atualização de um perímetro existente.
    
    Exige o 'id' do perímetro a ser atualizado. Todos os outros campos
    são marcados como 'Optional', o que significa que o cliente pode
    enviar apenas os campos que deseja alterar, permitindo atualizações parciais.
    """
    id: str
    name: Optional[str] = None
    x: Optional[X_template] = None
    y: Optional[Y_template] = None

class ChoosePerimeterDTO(BaseModel):
    """
    DTO para selecionar ou deletar um perímetro.
    
    Este é um modelo simples usado em operações que precisam apenas
    identificar um perímetro específico pelo seu 'id', como selecioná-lo
    para ser o perímetro ativo ou para excluí-lo do banco de dados.
    """
    id: str