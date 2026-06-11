import os
from flask import Flask, request, jsonify
import mysql.connector
from dotenv import load_dotenv # Importa a função para carregar o .env

# Carrega as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configuração do Banco de Dados usando variáveis de ambiente
db_config = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS')
}


def get_db_connection(): 
    return mysql.connector.connect(**db_config)

# =========================================================
# CLASSES (MODELOS)
# =========================================================
class Funcionario:
    def __init__(self, nome, cpf, cargo, setor, id=None):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.cargo = cargo
        self.setor = setor

class Treinamento:
    def __init__(self, nome_treinamento, validade_meses, id=None):
        self.id = id
        self.nome_treinamento = nome_treinamento
        self.validade_meses = validade_meses

class Registro:
    def __init__(self, id_funcionario, id_treinamento, data_realizacao, status='Ativo', id=None):
        self.id = id
        self.id_funcionario = id_funcionario
        self.id_treinamento = id_treinamento
        self.data_realizacao = data_realizacao
        self.status = status

# =========================================================
# 1. ROTAS PARA FUNCIONÁRIOS
# =========================================================

@app.route('/api/funcionario', methods=['POST'])
def cadastrar_funcionario():
    conn = None
    try:
        dados = request.get_json()
        func = Funcionario(dados['nome'], dados['cpf'], dados['cargo'], dados['setor'])
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO DimFuncionarios (nome, cpf, cargo, setor) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (func.nome, func.cpf, func.cargo, func.setor))
        conn.commit()
        return jsonify({"mensagem": "Funcionário cadastrado!"}), 201
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/funcionario/<int:id>', methods=['PUT'])
def atualizar_funcionario(id):
    conn = None
    try:
        dados = request.get_json()
        func = Funcionario(dados['nome'], dados['cpf'], dados['cargo'], dados['setor'])
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "UPDATE DimFuncionarios SET nome = %s, cpf = %s, cargo = %s, setor = %s WHERE id_funcionario = %s"
        cursor.execute(sql, (func.nome, func.cpf, func.cargo, func.setor, id))
        conn.commit()
        if cursor.rowcount == 0: return jsonify({"mensagem": "Funcionário não encontrado."}), 404
        return jsonify({"mensagem": "Funcionário atualizado!"}), 200
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/funcionario/<int:id>', methods=['DELETE'])
def excluir_funcionario(id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM DimFuncionarios WHERE id_funcionario = %s", (id,))
        conn.commit()
        if cursor.rowcount == 0: return jsonify({"mensagem": "Funcionário não encontrado."}), 404
        return jsonify({"mensagem": "Funcionário excluído!"}), 200
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/funcionario/buscar', methods=['GET'])
def buscar_funcionarios():
    conn = None
    try:
        nome = request.args.get('nome')
        cargo = request.args.get('cargo')
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM DimFuncionarios WHERE 1=1"
        params = []
        if nome:
            sql += " AND nome LIKE %s"
            params.append(f"%{nome}%")
        if cargo:
            sql += " AND cargo = %s"
            params.append(cargo)
        cursor.execute(sql, tuple(params))
        funcionarios = cursor.fetchall()
        return jsonify(funcionarios), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# =========================================================
# 2. ROTAS PARA TREINAMENTOS
# =========================================================

@app.route('/api/treinamento', methods=['POST'])
def cadastrar_treinamento():
    conn = None
    try:
        dados = request.get_json()
        treino = Treinamento(dados['nome_treinamento'], dados['validade_meses'])
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO DimTreinamentos (nome_treinamento, validade_meses) VALUES (%s, %s)"
        cursor.execute(sql, (treino.nome_treinamento, treino.validade_meses))
        conn.commit()
        return jsonify({"mensagem": "Treinamento cadastrado!"}), 201
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/treinamento', methods=['GET'])
def listar_treinamentos():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM DimTreinamentos")
        treinamentos = cursor.fetchall()
        return jsonify(treinamentos), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/treinamento/<int:id>', methods=['PUT'])
def atualizar_treinamento(id):
    conn = None
    try:
        dados = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "UPDATE DimTreinamentos SET nome_treinamento = %s, validade_meses = %s WHERE id_treinamento = %s"
        cursor.execute(sql, (dados['nome_treinamento'], dados['validade_meses'], id))
        conn.commit()
        if cursor.rowcount == 0: return jsonify({"mensagem": "Treinamento não encontrado."}), 404
        return jsonify({"mensagem": "Treinamento atualizado!"}), 200
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/treinamento/<int:id>', methods=['DELETE'])
def excluir_treinamento(id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM DimTreinamentos WHERE id_treinamento = %s", (id,))
        conn.commit()
        if cursor.rowcount == 0: return jsonify({"mensagem": "Treinamento não encontrado."}), 404
        return jsonify({"mensagem": "Treinamento excluído!"}), 200
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/treinamento/buscar', methods=['GET'])
def buscar_treinamentos():
    conn = None
    try:
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
        return jsonify(treinamentos), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# =========================================================
# 3. ROTAS PARA REGISTROS (FATO)
# =========================================================

@app.route('/api/registros', methods=['POST'])
def registrar_treinamento():
    conn = None
    try:
        dados = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO FactRegistros (id_funcionario, id_treinamento, data_realizacao) VALUES (%s, %s, %s)"
        cursor.execute(sql, (dados['id_funcionario'], dados['id_treinamento'], dados['data_realizacao']))
        conn.commit()
        return jsonify({"mensagem": "Registro criado!"}), 201
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/registros', methods=['GET'])
def listar_registros():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT R.id_registro, F.nome AS funcionario, T.nome_treinamento, R.data_realizacao, R.status
            FROM FactRegistros R
            JOIN DimFuncionarios F ON R.id_funcionario = F.id_funcionario
            JOIN DimTreinamentos T ON R.id_treinamento = T.id_treinamento
        """
        cursor.execute(sql)
        registros = cursor.fetchall()
        return jsonify(registros), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/registros/<int:id>', methods=['PUT'])
def atualizar_registro(id):
    conn = None
    try:
        dados = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "UPDATE FactRegistros SET id_funcionario = %s, id_treinamento = %s, data_realizacao = %s, status = %s WHERE id_registro = %s"
        cursor.execute(sql, (dados['id_funcionario'], dados['id_treinamento'], dados['data_realizacao'], dados['status'], id))
        conn.commit()
        if cursor.rowcount == 0: return jsonify({"mensagem": "Registro não encontrado."}), 404
        return jsonify({"mensagem": "Registro atualizado!"}), 200
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/registros/<int:id>', methods=['DELETE'])
def excluir_registro(id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM FactRegistros WHERE id_registro = %s", (id,))
        conn.commit()
        if cursor.rowcount == 0: return jsonify({"mensagem": "Registro não encontrado."}), 404
        return jsonify({"mensagem": "Registro excluído!"}), 200
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)