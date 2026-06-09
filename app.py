from flask import Flask, request, jsonify
import mysql.connector
#Importa a biblioteca para conectar ao MySQL. mysql.connector é um conector oficial do MySQL para Python, que permite que você se conecte a um banco de dados MySQL e execute consultas SQL.

# No terminal, instale o Flask e o mysql-connector-python usando pip:
# pip install Flask mysql-connector-python. esse comando instala as bibliotecas necessárias para criar a API com Flask e para conectar ao banco de dados MySQL usando mysql.connector. O Flask é um microframework leve para criar APIs web, enquanto o mysql-connector-python é a biblioteca oficial do MySQL para Python, que facilita a conexão e a execução de consultas SQL em um banco de dados MySQL.

# Importando as bibliotecas necessárias para criar a API e lidar com o banco de dados
#flask é o microframework para criar a API, request para pegar os dados enviados pelo cliente, jsonify para retornar respostas em formato JSON
#request e jsonify são funções do Flask para lidar com requisições e respostas HTTP, respectivamente.

app = Flask(__name__) 

# Criando a aplicação Flask, que é o núcleo da nossa API. O nome __name__ é uma convenção do Python que indica o nome do módulo atual, e é usado para configurar a aplicação corretamente.

# Configuração do Banco de Dados - Centralizada para evitar erros, facilitar manutenção e garantir segurança (evitando SQL Injection)

db_config = {
    'host': 'localhost',
    # O endereço do servidor MySQL (pode ser 'localhost' se estiver rodando localmente) ou o IP do servidor onde o MySQL está hospedado.
    'database': 'INF07SST',
    # O nome do banco de dados que você criou para armazenar as tabelas DimFuncionarios, DimTreinamentos e FactRegistros. o Schema do banco de dados é o nome do banco onde as tabelas estão criadas.
    'user': 'root', 
    # O nome de usuário do MySQL (geralmente 'root' para instalações locais, mas pode ser diferente dependendo da configuração do seu MySQL).
    'password': '115088' 
    # Coloque sua senha aqui, se você tiver configurado uma senha para o usuário do MySQL. Se estiver usando uma instalação local sem senha, deixe em branco.
}

def get_db_connection(): 
    # Função para obter uma conexão com o banco de dados usando as configurações definidas acima. 
    #Função auxiliar para abrir conexão sempre que necessário.
    return mysql.connector.connect(**db_config)
    #A função get_db_connection() é uma função auxiliar que cria e retorna uma nova conexão com o banco de dados MySQL usando as configurações definidas em db_config. O uso de **db_config permite passar os parâmetros do dicionário como argumentos nomeados para a função mysql.connector.connect(), facilitando a manutenção e evitando erros de digitação ao criar conexões em diferentes partes do código.

# =========================================================
# CLASSES (MODELOS) - A definição dos nossos objetos
# =========================================================

# Definindo a planta baixa (Classe) para Funcionários
class Funcionario:
    # __init__ é o construtor: ele "constrói" o objeto quando o chamamos
    # self refere-se ao objeto que estamos criando naquele momento
    # id=None é um valor padrão: se não passarmos um ID, ele assume None (útil para novos registros que ainda não têm ID)
    def __init__(self, nome, cpf, cargo, setor, id=None):
        self.id = id # Armazena o ID (None para novos, um número para existentes)
        self.nome = nome # Atribui o nome passado na criação ao atributo do objeto
        self.cpf = cpf # Atribui o CPF
        self.cargo = cargo # Atribui o cargo
        self.setor = setor # Atribui o setor

# Definindo a planta baixa para Treinamentos
class Treinamento:
    def __init__(self, nome_treinamento, validade_meses, id=None):
        self.id = id
        self.nome_treinamento = nome_treinamento
        self.validade_meses = validade_meses

# Definindo a planta baixa para os Registros (a tabela Fato)
class Registro:
    # status='Ativo' é um valor padrão: se não dissermos nada, ele assume 'Ativo'
    def __init__(self, id_funcionario, id_treinamento, data_realizacao, status='Ativo', id=None):
        self.id = id
        self.id_funcionario = id_funcionario # Guarda quem fez (chave estrangeira)
        self.id_treinamento = id_treinamento # Guarda o que fez (chave estrangeira)
        self.data_realizacao = data_realizacao # Guarda quando fez
        self.status = status # Guarda o estado atual (ex: ativo ou vencido)

# =========================================================
# 1. ROTAS PARA FUNCIONÁRIOS (CRUD)
# =========================================================
# CRUD significa Create (Criar), Read (Ler), Update (Atualizar) e Delete (Excluir). Essas são as operações básicas para gerenciar dados em um sistema. Aqui, vamos implementar as rotas para criar e excluir funcionários. As rotas para ler e atualizar podem ser adicionadas posteriormente seguindo a mesma lógica.
# route é um decorador do Flask que define a URL e o método HTTP para a função que segue. No caso, estamos definindo uma rota para criar um funcionário usando o método POST, e outra para excluir um funcionário usando o método DELETE. O <int:id> na rota de exclusão indica que esperamos um número inteiro como parte da URL, que será usado para identificar qual funcionário excluir.
#REST ful API: cada rota corresponde a uma operação específica (ex: POST para criar, DELETE para excluir), e os dados são enviados e recebidos em formato JSON, que é um formato leve e fácil de usar para comunicação entre cliente e servidor.
#metodo POST é usado para criar novos recursos (neste caso, um novo funcionário), enquanto o método DELETE é usado para remover recursos existentes (neste caso, um funcionário específico identificado por seu ID).
#Metodo Delete: é usado para excluir um recurso específico. No exemplo, a rota '/api/funcionario/<int:id>' espera um ID de funcionário na URL, e quando essa rota é acessada com o método DELETE, o funcionário correspondente a esse ID será removido do banco de dados.
#metodo get é usado para ler ou recuperar informações. No exemplo, a rota '/api/registros' com o método GET é usada para listar todos os registros de treinamentos realizados, retornando os dados em formato JSON para o cliente.

# =========================================================
# ROTA DE ADIÇÃO DE FUNCIONÁRIO (CREATE)
# =========================================================

@app.route('/api/funcionario', methods=['POST']) 
# Define uma rota para criar um novo funcionário. Quando um cliente enviar uma requisição POST para '/api/funcionario', a função cadastrar_funcionario() será executada.
def cadastrar_funcionario():
    dados = request.get_json() 
    # Pega os dados enviados pelo cliente em formato JSON e os converte para um dicionário Python. Esperamos que o cliente envie um JSON com as chaves 'nome', 'cpf', 'cargo' e 'setor'.
    func = Funcionario(dados['nome'], dados['cpf'], dados['cargo'], dados['setor']) 
    # Cria um objeto Funcionario usando os dados recebidos. Isso é útil para organizar os dados e facilitar a manipulação antes de salvar no banco de dados. #Criamos um objeto Funcionario usando os dados recebidos do cliente. Isso nos permite trabalhar com um objeto estruturado em vez de um dicionário solto, o que pode facilitar a manutenção e a clareza do código. o usuario envia o json que é recebido na classe Funcionario, e seguida o request.get_json() converte o JSON em um dicionário Python, e a variavel func recebe o discionário convertido para um objeto Funcionario, onde os atributos do objeto são preenchidos com os valores correspondentes do dicionário.
    
    conn = get_db_connection()
    # Estabelece uma conexão com o banco de dados usando a função get_db_connection() que definimos anteriormente. Isso nos permite executar consultas SQL para inserir os dados do novo funcionário.
    cursor = conn.cursor() 
    # a variavel cursor é usada para executar comandos SQL no banco de dados. Ela é criada a partir da conexão estabelecida e é responsável por enviar as consultas e receber os resultados. conn.cursor() recebe a conexão com o banco de dados e retorna um objeto cursor que pode ser usado para executar comandos SQL. O cursor é essencial para interagir com o banco de dados, permitindo que você execute consultas, insira dados, atualize registros e muito mais. 
    #.cursor() é um método da conexão que cria um cursor, que é um objeto usado para executar comandos SQL e gerenciar os resultados. O cursor é essencial para interagir com o banco de dados, permitindo que você execute consultas, insira dados, atualize registros e muito mais.
    
    sql = "INSERT INTO DimFuncionarios (nome, cpf, cargo, setor) VALUES (%s, %s, %s, %s)"
    # a variavel sql armazena entre "" o comando SQL porque SQL e Python são linguagens diferentes, e o comando SQL precisa ser passado como uma string para que o metodo execute() do cursor possa interpretá-lo corretamente. O comando SQL é uma string que representa a consulta que queremos executar no banco de dados. Neste caso, estamos usando um comando INSERT para adicionar um novo registro à tabela DimFuncionarios, e os %s são placeholders para os valores que serão inseridos, o que ajuda a evitar SQL Injection.
    # Define a consulta SQL para inserir um novo funcionário na tabela DimFuncionarios. Os %s são placeholders para os valores que serão inseridos, e ajudam a evitar SQL Injection.
    #placeholders (%s) são usados para evitar SQL Injection, que é uma técnica maliciosa onde um atacante pode inserir código SQL malicioso em vez de dados normais. Usar placeholders e passar os valores separadamente garante que o banco de dados trate os valores como dados, e não como parte da consulta SQL.
    cursor.execute(sql, (func.nome, func.cpf, func.cargo, func.setor)) 
    # Executa a consulta SQL usando o cursor, passando os valores do objeto Funcionario como parâmetros. Isso insere um novo registro na tabela DimFuncionarios com os dados fornecidos.
    conn.commit()
    #commit() é um método da conexão que salva as alterações feitas no banco de dados. Depois de executar uma consulta de inserção, atualização ou exclusão, é necessário chamar commit() para garantir que as mudanças sejam persistidas no banco de dados. Se você não chamar commit(), as alterações não serão salvas e podem ser perdidas se a conexão for fechada.
    cursor.close()
    #cursor.close() é um método que fecha o cursor após o uso. É uma boa prática fechar o cursor para liberar os recursos associados a ele. Depois de executar a consulta e fazer o commit, fechamos o cursor para garantir que não haja conexões ou recursos desnecessários abertos.
    conn.close()
    #conn.close() é um método que fecha a conexão com o banco de dados. É importante fechar a conexão após terminar de usá-la para liberar os recursos do banco de dados e evitar conexões abertas desnecessárias, o que pode levar a problemas de desempenho ou esgotamento de conexões.

    return jsonify({"mensagem": "Funcionário cadastrado!"}), 201 
# Retorna uma resposta JSON indicando que o funcionário foi cadastrado com sucesso, junto com o status HTTP 201 (Created) para indicar que um novo recurso foi criado.

# =========================================================
# ROTA DE EXCLUSÃO DE FUNCIONÁRIO (DELETE)
# =========================================================

@app.route('/api/funcionario/<int:id>', methods=['DELETE']) 
# Define uma rota para excluir um funcionário específico. O <int:id> indica que esperamos um número inteiro como parte da URL, que será usado para identificar qual funcionário excluir. Quando uma requisição DELETE for enviada para essa rota, a função excluir_funcionario() será executada.
def excluir_funcionario(id): 
    # A função recebe o ID do funcionário a ser excluído como parâmetro, que é extraído da URL. O Flask automaticamente converte o valor da URL para um inteiro devido ao <int:id> na definição da rota.
    conn = get_db_connection()
    # Estabelece uma conexão com o banco de dados para executar a consulta de exclusão.
    cursor = conn.cursor()
    # Executa a consulta SQL para excluir o funcionário com o ID fornecido. O %s é um placeholder para o ID, e o valor é passado como uma tupla (id,) para evitar SQL Injection.
    cursor.execute("DELETE FROM DimFuncionarios WHERE id_funcionario = %s", (id,))
    # A consulta SQL "DELETE FROM DimFuncionarios WHERE id_funcionario = %s" é usada para excluir um registro da tabela DimFuncionarios onde o id_funcionario corresponde ao valor fornecido. O %s é um placeholder que será substituído pelo valor do ID passado como parâmetro, e a tupla (id,) garante que o valor seja tratado corretamente como um parâmetro, evitando SQL Injection. O comando deletara a linha da tabela DimFuncionarios onde o id_funcionario for igual ao valor do ID fornecido na URL.
    conn.commit()
    #commit() é chamado para salvar as alterações no banco de dados após a execução da consulta de exclusão. Isso garante que o funcionário seja realmente removido do banco de dados.
    cursor.close()
    #cursor.close() é chamado para fechar o cursor após a execução da consulta. Isso é uma boa prática para liberar os recursos associados ao cursor.
    conn.close()
    #conn.close() é chamado para fechar a conexão com o banco de dados após a execução da consulta. Isso é importante para liberar os recursos do banco de dados e evitar conexões abertas desnecessárias, o que pode levar a problemas de desempenho ou esgotamento de conexões.
    return jsonify({"mensagem": "Funcionário excluído!"})
    # Retorna uma resposta JSON indicando que o funcionário foi excluído com sucesso. O status HTTP padrão para uma exclusão bem-sucedida é 200 (OK), então não é necessário especificar um status diferente aqui.
    
# =========================================================
# ROTA DE EDIÇÃO/ATUALIZAÇÃO DE FUNCIONÁRIO (UPDATE)
# =========================================================
# PUT é o método HTTP recomendado para atualizações, pois é idempotente (ou seja, fazer a mesma requisição várias vezes terá o mesmo efeito que fazer uma vez). Isso é importante para garantir que as atualizações sejam previsíveis e consistentes. O método POST, por outro lado, é geralmente usado para criar novos recursos e não é idempotente, o que pode levar a resultados inesperados se usado para atualizações.
    
@app.route('/api/funcionario/<int:id>', methods=['PUT'])
# Definimos o método PUT, que é o padrão da indústria para realizar atualizações (Update) de recursos existentes.
def atualizar_funcionario(id):
    # Recebemos os novos dados enviados pelo front-end no corpo da requisição (JSON).
    dados = request.get_json()
    # O ID do funcionário a ser atualizado é recebido como parte da URL, e os novos dados (nome, cpf, cargo, setor) são recebidos no corpo da requisição em formato JSON. O Flask converte esse JSON em um dicionário Python usando request.get_json(), permitindo que acessemos os valores usando as chaves correspondentes.
    # O request.get_json() ira pegar os dados enviados pelo cliente em formato JSON e os converterá para um dicionário Python. Esperamos que o cliente envie um JSON com as chaves 'nome', 'cpf', 'cargo' e 'setor', que serão usadas para atualizar os dados do funcionário no banco de dados.
    

    func = Funcionario(dados['nome'], dados['cpf'], dados['cargo'], dados['setor'])
    # Criamos uma instância da classe Funcionario com os dados recebidos. 
    # Isso serve como uma validação: se o front-end esquecer algum campo, podemos identificar aqui. Além disso, ter um objeto Funcionario facilita a manipulação dos dados e torna o código mais organizado. O objeto func agora contém os novos dados que queremos atualizar para o funcionário identificado pelo ID na URL.
    
    
    conn = get_db_connection()
    # Estabelecemos a conexão com o banco de dados. Isso é necessário para executar a consulta SQL que irá atualizar os dados do funcionário.
    # A função get_db_connection() é chamada para criar uma nova conexão com o banco de dados usando as configurações definidas anteriormente. Isso nos permite executar consultas SQL para atualizar os dados do funcionário.
    #     
    cursor = conn.cursor()
    # Criamos um cursor para executar as consultas SQL no banco de dados. O cursor é um objeto que nos permite enviar comandos SQL e receber resultados do banco de dados.
    
    # Comando SQL UPDATE: responsável por alterar os dados na tabela.
    # Atenção: O WHERE id_funcionario = %s é obrigatório. Sem ele, o MySQL alteraria todos os funcionários da tabela!
    sql = """
        UPDATE DimFuncionarios 
        SET nome = %s, cpf = %s, cargo = %s, setor = %s 
        WHERE id_funcionario = %s
    """
    # a variavel esta armazenando entre aspas triplas (""") uma string que representa a consulta SQL para atualizar os dados de um funcionário na tabela DimFuncionarios. A consulta usa placeholders (%s) para os valores que serão atualizados, e o WHERE id_funcionario = %s garante que apenas o funcionário com o ID específico seja atualizado. É crucial incluir a cláusula WHERE para evitar atualizar todos os registros da tabela acidentalmente.
    
    # Executamos o comando passando os novos dados e, por último, o ID do funcionário que queremos editar.
    cursor.execute(sql, (func.nome, func.cpf, func.cargo, func.setor, id))
    # O método cursor.execute() é usado para executar a consulta SQL definida na variável sql. Os valores para os placeholders (%s) são passados como uma tupla, onde os primeiros quatro valores correspondem aos novos dados do funcionário (nome, cpf, cargo, setor) e o último valor é o ID do funcionário que queremos atualizar. Isso garante que apenas o funcionário com o ID especificado seja atualizado com os novos dados fornecidos.
    
    # Salvamos as alterações no banco de dados.
    conn.commit()
    # O método conn.commit() é chamado para salvar as alterações feitas no banco de dados após a execução da consulta de atualização. Isso garante que os novos dados do funcionário sejam persistidos no banco de dados.
    
    # Fechamos o cursor e a conexão para liberar os recursos do banco.
    cursor.close()
    # O método cursor.close() é chamado para fechar o cursor após a execução da consulta. Isso é uma boa prática para liberar os recursos associados ao cursor.
    conn.close()
    # O método conn.close() é chamado para fechar a conexão com o banco de dados após a execução da consulta. Isso é importante para liberar os recursos do banco de dados e evitar conexões abertas desnecessárias, o que pode levar a problemas de desempenho ou esgotamento de conexões.
    
    # Retornamos uma confirmação de que a atualização foi realizada com sucesso.
    return jsonify({"mensagem": "Funcionário atualizado com sucesso!"}), 200
    # Retorna uma resposta JSON indicando que o funcionário foi atualizado com sucesso, junto com o status HTTP 200 (OK) para indicar que a operação foi bem-sucedida.

### ROTA DE BUSCA DE FUNCIONÁRIOS COM FILTROS (READ)

@app.route('/api/funcionario/buscar', methods=['GET'])
# Rota para buscar funcionários com filtros. O cliente envia parâmetros na URL, ex: /api/funcionario/buscar?nome=Clei
def buscar_funcionarios(): # Pegamos os parâmetros de busca enviados pelo cliente na URL (ex: ?nome=Clei&cargo=Analista)
    
    nome = request.args.get('nome') 
    # Pegamos o parâmetro 'nome' da URL, se o cliente enviou. Se não enviou, nome será None.
    #request.args é um objeto do Flask que contém os parâmetros de consulta enviados na URL. O método get('nome') é usado para obter o valor do parâmetro 'nome' da URL. Se o cliente enviou um parâmetro 'nome' (ex: /api/funcionario/buscar?nome=Clei), então nome receberá o valor correspondente (neste caso, "Cleidson"). Se o cliente não enviou o parâmetro 'nome', então nome será None, indicando que não há filtro de nome para a busca.

    cargo = request.args.get('cargo') 
    # Pegamos o parâmetro 'cargo' da URL, se o cliente enviou. Se não enviou, cargo será None.
    
    conn = get_db_connection() 
    # Estabelecemos a conexão com o banco de dados para executar a consulta de busca.

    cursor = conn.cursor(dictionary=True) 
    # O parâmetro dictionary=True faz com que o cursor retorne os resultados como dicionários, onde as chaves são os nomes das colunas. Isso facilita a conversão para JSON posteriormente.
    
    # Truque didático: WHERE 1=1. 
    # Isso é sempre verdade, permitindo que a gente adicione "AND" na frente sem erro de sintaxe.
    
    sql = "SELECT * FROM DimFuncionarios WHERE 1=1"
    # A variável sql armazena a consulta SQL para selecionar os funcionários da tabela DimFuncionarios. O truque WHERE 1=1 é usado para facilitar a construção dinâmica da consulta, permitindo que adicionemos cláusulas AND sem nos preocupar com a sintaxe. Isso é útil quando queremos aplicar filtros opcionais com base nos parâmetros enviados pelo cliente.

    params = []
    # A lista params será usada para armazenar os valores dos filtros que serão aplicados na consulta SQL. Conforme verificamos quais parâmetros foram enviados pelo cliente (nome, cargo), adicionaremos os filtros correspondentes à consulta SQL e os valores à lista params. No final, passaremos essa lista como parâmetros para a execução da consulta, garantindo que os valores sejam tratados corretamente e evitando SQL Injection.
    
    # Se o usuário enviou um nome, adicionamos o filtro
    if nome:
        sql += " AND nome LIKE %s"
        params.append(f"%{nome}%") 
        # %s nos dois lados permite busca parcial (ex: "Cleidson" acha "Cleidson")
        # O operador LIKE é usado para realizar buscas parciais em strings. Ao usar % antes e depois do valor do nome (f"%{nome}%"), estamos dizendo ao banco de dados para procurar por qualquer registro onde a coluna nome contenha a string fornecida, independentemente de onde ela apareça no nome completo. Por exemplo, se o cliente enviar "Cleidson", a consulta encontrará registros como "Cleidson", "Cleiton", "Cleiston", etc., porque todos esses nomes contêm a substring "Cleidson". Isso torna a busca mais flexível e amigável para o usuário.
        
    # Se o usuário enviou um cargo, adicionamos o filtro
    if cargo:
        sql += " AND cargo = %s"
        params.append(cargo)
        # O operador = é usado para realizar uma busca exata. Ao usar cargo = %s, estamos dizendo ao banco de dados para procurar por registros onde a coluna cargo seja exatamente igual ao valor fornecido. Por exemplo, se o cliente enviar "Analista", a consulta encontrará apenas os registros onde o cargo seja exatamente "Analista". Isso é útil quando queremos uma correspondência precisa para um campo específico.
        
    cursor.execute(sql, tuple(params))
    # O método cursor.execute() é usado para executar a consulta SQL definida na variável sql, passando os valores dos filtros como parâmetros. A função tuple(params) converte a lista params em uma tupla, que é o formato esperado pelo método execute() para os parâmetros da consulta. Isso garante que os valores sejam tratados corretamente e evita SQL Injection. A consulta será executada com os filtros aplicados com base nos parâmetros enviados pelo cliente.
    funcionarios = cursor.fetchall()
    # O método cursor.fetchall() é usado para recuperar todos os resultados da consulta SQL executada. Ele retorna uma lista de dicionários (devido ao dictionary=True) onde cada dicionário representa um registro da tabela DimFuncionarios, com as chaves correspondendo aos nomes das colunas e os valores correspondendo aos dados de cada funcionário que corresponde aos filtros aplicados.
    
    cursor.close()
    # Fechamos o cursor e a conexão para liberar os recursos do banco.
    conn.close()
    #cursor.close() é chamado para fechar o cursor após a execução da consulta. Isso é uma boa prática para liberar os recursos associados ao cursor. conn.close() é chamado para fechar a conexão com o banco de dados após a execução da consulta. Isso é importante para liberar os recursos do banco de dados e evitar conexões abertas desnecessárias, o que pode levar a problemas de desempenho ou esgotamento de conexões.
    return jsonify(funcionarios), 200
    # Retorna a lista de funcionários encontrados em formato JSON, junto com o status HTTP 200 (OK) para indicar que a operação foi bem-sucedida.

# =========================================================
# 2. ROTAS PARA TREINAMENTOS (CRUD) 
# =========================================================

### ROTA DE CADASTRO DE TREINAMENTO (CREATE)

@app.route('/api/treinamento', methods=['POST'])
# Rota para CADASTRAR um novo treinamento.
def cadastrar_treinamento():
    dados = request.get_json()
    # Criamos o objeto Treinamento (a "planta baixa") usando os dados do JSON.
    treino = Treinamento(dados['nome_treinamento'], dados['validade_meses'])
    # O request.get_json() pega os dados enviados pelo cliente em formato JSON e os converte para um dicionário Python. Esperamos que o cliente envie um JSON com as chaves 'nome_treinamento' e 'validade_meses', que serão usadas para criar um novo objeto Treinamento. O objeto treino agora contém os dados do novo treinamento que queremos cadastrar no banco de dados.
    
    conn = get_db_connection()
    # Estabelecemos a conexão com o banco de dados para executar a consulta de inserção do novo treinamento.
    cursor = conn.cursor()
    # Criamos um cursor para executar as consultas SQL no banco de dados. O cursor é um objeto que nos permite enviar comandos SQL e receber resultados do banco de dados.
    sql = "INSERT INTO DimTreinamentos (nome_treinamento, validade_meses) VALUES (%s, %s)"
    # A variável sql armazena a consulta SQL para inserir um novo treinamento na tabela DimTreinamentos. Os %s são placeholders para os valores que serão inseridos, e ajudam a evitar SQL Injection.
    cursor.execute(sql, (treino.nome_treinamento, treino.validade_meses))
    # O método cursor.execute() é usado para executar a consulta SQL definida na variável sql. Os valores para os placeholders (%s) são passados como uma tupla, onde o primeiro valor corresponde ao nome do treinamento e o segundo valor corresponde à validade em meses. Isso insere um novo registro na tabela DimTreinamentos com os dados fornecidos.
    conn.commit()
    # O método conn.commit() é chamado para salvar as alterações feitas no banco de dados após a execução da consulta de inserção. Isso garante que o novo treinamento seja persistido no banco de dados.
    cursor.close()
    # O método cursor.close() é chamado para fechar o cursor após a execução da consulta. Isso é uma boa prática para liberar os recursos associados ao cursor.
    conn.close()
    # O método conn.close() é chamado para fechar a conexão com o banco de dados após a execução da consulta. Isso é importante para liberar os recursos do banco de dados e evitar conexões abertas desnecessárias, o que pode levar a problemas de desempenho ou esgotamento de conexões.
    return jsonify({"mensagem": "Treinamento cadastrado com sucesso!"}), 201
    # Retorna uma resposta JSON indicando que o treinamento foi cadastrado com sucesso, junto com o status HTTP 201 (Created) para indicar que um novo recurso foi criado.

### ROTA DE LISTAGEM DE TREINAMENTOS (READ)

@app.route('/api/treinamento', methods=['GET'])
# Rota para LISTAR todos os treinamentos existentes.

def listar_treinamentos():
    conn = get_db_connection()
    # Estabelecemos a conexão com o banco de dados para executar a consulta de seleção dos treinamentos.

    cursor = conn.cursor(dictionary=True) 
    # O parâmetro dictionary=True faz com que o cursor retorne os resultados como dicionários, onde as chaves são os nomes das colunas. Isso facilita a conversão para JSON posteriormente.
    cursor.execute("SELECT * FROM DimTreinamentos")
    # Executamos a consulta SQL para selecionar todos os registros da tabela DimTreinamentos. O resultado será uma lista de dicionários, onde cada dicionário representa um treinamento com suas respectivas colunas como chaves.
    treinamentos = cursor.fetchall()
    # O método cursor.fetchall() é usado para recuperar todos os resultados da consulta SQL executada. Ele retorna uma lista de dicionários (devido ao dictionary=True) onde cada dicionário representa um registro da tabela DimTreinamentos, com as chaves correspondendo aos nomes das colunas e os valores correspondendo aos dados de cada treinamento.
    cursor.close()
    conn.close()
    return jsonify(treinamentos), 200

### ROTA DE ATUALIZAÇÃO DE TREINAMENTO (UPDATE)

@app.route('/api/treinamento/<int:id>', methods=['PUT'])
# Rota para EDITAR um treinamento existente identificado pelo ID.
def atualizar_treinamento(id):
    # Recebemos os novos dados do treinamento no corpo da requisição (JSON).
    dados = request.get_json()
    # Criamos um objeto Treinamento com os novos dados. Isso ajuda a organizar as informações e facilita a manipulação antes de atualizar no banco de dados. O objeto treino agora contém os novos dados do treinamento que queremos atualizar para o treinamento identificado pelo ID na URL.
    treino = Treinamento(dados['nome_treinamento'], dados['validade_meses'])
    # O request.get_json() pega os dados enviados pelo cliente em formato JSON e os converte para um dicionário Python. Esperamos que o cliente envie um JSON com as chaves 'nome_treinamento' e 'validade_meses', que serão usadas para criar um novo objeto Treinamento. O objeto treino agora contém os novos dados do treinamento que queremos atualizar para o treinamento identificado pelo ID na URL.
    
    conn = get_db_connection()
    # Estabelecemos a conexão com o banco de dados para executar a consulta de atualização do treinamento.
    cursor = conn.cursor()
    # Comando SQL UPDATE: responsável por alterar os dados na tabela. O SET define os novos valores, e o WHERE id_treinamento = %s garante que apenas o treinamento com o ID específico seja atualizado. Sem o WHERE, todos os treinamentos seriam alterados acidentalmente!
    # O WHERE é fundamental: garante que alteramos apenas o treinamento que estamos editando.
    sql = """
        UPDATE DimTreinamentos 
        SET nome_treinamento = %s, validade_meses = %s 
        WHERE id_treinamento = %s
    """
    # A variável sql armazena a consulta SQL para atualizar os dados de um treinamento na tabela DimTreinamentos. A consulta usa placeholders (%s) para os valores que serão atualizados, e o WHERE id_treinamento = %s garante que apenas o treinamento com o ID específico seja atualizado. É crucial incluir a cláusula WHERE para evitar atualizar todos os registros da tabela acidentalmente.

    cursor.execute(sql, (treino.nome_treinamento, treino.validade_meses, id))
    # O método cursor.execute() é usado para executar a consulta SQL definida na variável sql. Os valores para os placeholders (%s) são passados como uma tupla, onde os primeiros dois valores correspondem aos novos dados do treinamento (nome_treinamento e validade_meses) e o último valor é o ID do treinamento que queremos atualizar. Isso garante que apenas o treinamento com o ID especificado seja atualizado com os novos dados fornecidos.
    conn.commit()
    # O método conn.commit() é chamado para salvar as alterações feitas no banco de dados após a execução da consulta de atualização. Isso garante que os novos dados do treinamento sejam persistidos no banco de dados.
    cursor.close()
    # O método cursor.close() é chamado para fechar o cursor após a execução da consulta. Isso é uma boa prática para liberar os recursos associados ao cursor.
    conn.close()
    # O método conn.close() é chamado para fechar a conexão com o banco de dados após a execução da consulta. Isso é importante para liberar os recursos do banco de dados e evitar conexões abertas desnecessárias, o que pode levar a problemas de desempenho ou esgotamento de conexões.
    return jsonify({"mensagem": "Treinamento atualizado com sucesso!"}), 200
    # Retorna uma resposta JSON indicando que o treinamento foi atualizado com sucesso, junto com o status HTTP 200 (OK) para indicar que a operação foi bem-sucedida.

### ROTA DE EXCLUSÃO DE TREINAMENTO (DELETE)

@app.route('/api/treinamento/<int:id>', methods=['DELETE'])
# Rota para EXCLUIR um treinamento específico.
def excluir_treinamento(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # DELETE remove a linha inteira. O WHERE garante que não apagamos o catálogo todo!
    cursor.execute("DELETE FROM DimTreinamentos WHERE id_treinamento = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensagem": "Treinamento excluído com sucesso!"}), 200

### ROTA DE BUSCA DE TREINAMENTOS COM FILTROS (READ)

@app.route('/api/treinamento/buscar', methods=['GET'])
# Rota para buscar treinamentos filtrando por nome.
def buscar_treinamentos():
    nome = request.args.get('nome_treinamento')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    sql = "SELECT * FROM DimTreinamentos WHERE 1=1" # O truque do WHERE 1=1 permite adicionar filtros opcionais com AND sem se preocupar com a sintaxe. o truque WHERE 1=1 é usado para facilitar a construção dinâmica da consulta SQL, permitindo que adicionemos cláusulas AND sem nos preocupar com a sintaxe. Isso é útil quando queremos aplicar filtros opcionais com base nos parâmetros enviados pelo cliente. Por exemplo, se o cliente enviar um parâmetro de nome para filtrar os treinamentos, podemos simplesmente adicionar "AND nome_treinamento LIKE %s" à consulta sem precisar verificar se é o primeiro filtro ou não.  
    params = []
    
    if nome:
        sql += " AND nome_treinamento LIKE %s"
        params.append(f"%{nome}%")
        
    cursor.execute(sql, tuple(params))
    treinamentos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return jsonify(treinamentos), 200

# =========================================================
# 3. ROTAS PARA REGISTROS (FATO)
# =========================================================

@app.route('/api/registro', methods=['POST'])
# Rota para CADASTRAR um novo registro de treinamento.
def registrar_treinamento():
    dados = request.get_json()
    # Criamos o objeto Registro usando os IDs que vêm do front-end.
    reg = Registro(dados['id_funcionario'], dados['id_treinamento'], dados['data_realizacao'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    # Inserimos os dados na tabela Fato.
    sql = "INSERT INTO FactRegistros (id_funcionario, id_treinamento, data_realizacao) VALUES (%s, %s, %s)"
    cursor.execute(sql, (reg.id_funcionario, reg.id_treinamento, reg.data_realizacao))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensagem": "Registro de treinamento criado!"}), 201

@app.route('/api/registros', methods=['GET'])
# Rota para LISTAR todos os registros, já trazendo os Nomes dos funcionários e treinamentos (JOIN).
def listar_registros():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # O JOIN é como uma "ponte": ele pega o ID que está no FactRegistros 
    # e busca o nome correspondente na tabela de Dimensão.
    sql = """
        SELECT R.id_registro, F.nome AS funcionario, T.nome_treinamento, R.data_realizacao, R.status
        FROM FactRegistros R
        JOIN DimFuncionarios F ON R.id_funcionario = F.id_funcionario
        JOIN DimTreinamentos T ON R.id_treinamento = T.id_treinamento
    """
    cursor.execute(sql)
    registros = cursor.fetchall()
    
    cursor.close()
    conn.close()
    # Retorna uma lista legível, onde o front-end já recebe o nome e não apenas um número.
    return jsonify(registros), 200

@app.route('/api/registro/<int:id>', methods=['PUT'])
# Rota para ATUALIZAR um registro (ex: mudar o status para 'Concluído' ou alterar data).
def atualizar_registro(id):
    dados = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
        UPDATE FactRegistros 
        SET id_funcionario = %s, id_treinamento = %s, data_realizacao = %s, status = %s 
        WHERE id_registro = %s
    """
    cursor.execute(sql, (dados['id_funcionario'], dados['id_treinamento'], dados['data_realizacao'], dados['status'], id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensagem": "Registro atualizado!"}), 200

@app.route('/api/registro/<int:id>', methods=['DELETE'])
# Rota para EXCLUIR um registro.
def excluir_registro(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM FactRegistros WHERE id_registro = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensagem": "Registro excluído!"}), 200



if __name__ == '__main__': 
    # Isso garante que o servidor Flask só será iniciado se este arquivo for executado diretamente, e não quando for importado como um módulo em outro lugar.
    app.run(debug=True)
    # Inicia o servidor Flask em modo de depuração (debug=True), o que é útil durante o desenvolvimento, pois fornece mensagens de erro detalhadas e recarrega automaticamente o servidor quando o código é alterado.