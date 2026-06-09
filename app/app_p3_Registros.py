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

