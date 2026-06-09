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
    
    sql = "SELECT * FROM DimTreinamentos WHERE 1=1"
    params = []
    
    if nome:
        sql += " AND nome_treinamento LIKE %s"
        params.append(f"%{nome}%")
        
    cursor.execute(sql, tuple(params))
    treinamentos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return jsonify(treinamentos), 200