import os
import re  # Adicionado para limpar caracteres especiais do telefone
from flask import Flask, request, jsonify
import mysql.connector
from dotenv import load_dotenv
from twilio.rest import Client  # Import fixado no topo

# Carrega as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configuração do Banco de Dados
db_config = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS')
}

def get_db_connection(): 
    return mysql.connector.connect(**db_config)

# Função Auxiliar para garantir o padrão E.164 exigido pela Twilio
def formatar_para_twilio(telefone_raw):
    if not telefone_raw:
        return ""
    # Remove espaços, parênteses e traços, mantendo apenas dígitos
    numeros = re.sub(r'\D', '', str(telefone_raw))
    # Se tiver 11 dígitos (DDD + 9 dígitos), assume Brasil e insere o +55
    if len(numeros) == 11:
        return f"+55{numeros}"
    # Se já possuir o código do país (13 dígitos), adiciona apenas o sinal de +
    elif len(numeros) == 13:
        return f"+{numeros}"
    return numeros

# =========================================================
# CLASSES (MODELOS)
# =========================================================
class Funcionario:
    def __init__(self, nome, cpf, cargo, setor, email, telefone, whatsapp, id=None):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.cargo = cargo
        self.setor = setor
        self.email = email
        self.telefone = telefone
        self.whatsapp = whatsapp

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
# 1. ROTAS PARA FUNCIONÁRIOS (Atualizadas com Contatos)
# =========================================================

@app.route('/api/funcionario', methods=['POST'])
def cadastrar_funcionario():
    conn = None
    try:
        dados = request.get_json()
        func = Funcionario(dados['nome'], dados['cpf'], dados['cargo'], dados['setor'], 
                           dados['email'], dados['telefone'], dados['whatsapp'])
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO DimFuncionarios (nome, cpf, cargo, setor, email, telefone, whatsapp) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (func.nome, func.cpf, func.cargo, func.setor, func.email, func.telefone, func.whatsapp))
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
        func = Funcionario(dados['nome'], dados['cpf'], dados['cargo'], dados['setor'], 
                           dados['email'], dados['telefone'], dados['whatsapp'])
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """UPDATE DimFuncionarios 
                 SET nome = %s, cpf = %s, cargo = %s, setor = %s, email = %s, telefone = %s, whatsapp = %s 
                 WHERE id_funcionario = %s"""
        cursor.execute(sql, (func.nome, func.cpf, func.cargo, func.setor, func.email, func.telefone, func.whatsapp, id))
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM DimFuncionarios WHERE 1=1"
        params = []
        if nome:
            sql += " AND nome LIKE %s"
            params.append(f"%{nome}%")
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

# =========================================================
# 3. ROTAS PARA REGISTROS (FATO)
# =========================================================

@app.route('/api/registros', methods=['POST'])
def registrar_treinamento():
    conn = None
    try:
        dados = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT validade_meses FROM DimTreinamentos WHERE id_treinamento = %s", (dados['id_treinamento'],))
        treino = cursor.fetchone()
        
        if not treino:
            return jsonify({"erro": "Treinamento não encontrado"}), 404
        
        validade = treino['validade_meses']
        
        sql = """
            INSERT INTO FactRegistros 
            (id_funcionario, id_treinamento, data_realizacao, data_vencimento) 
            VALUES (%s, %s, %s, DATE_ADD(%s, INTERVAL %s MONTH))
        """
        
        cursor.execute(sql, (
            dados['id_funcionario'], 
            dados['id_treinamento'], 
            dados['data_realizacao'], 
            dados['data_realizacao'], 
            validade
        ))
        
        conn.commit()
        return jsonify({"mensagem": "Registro criado com data de vencimento calculada!"}), 201
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"erro": f"Erro ao processar registro: {str(e)}"}), 500
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
            SELECT R.id_registro, F.nome AS funcionario, T.nome_treinamento, R.data_realizacao, R.data_vencimento, R.status
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

# =========================================================
# #### API DISPAROS DE AVISO (SMS + WHATSAPP INTEGRADOS)
# =========================================================

@app.route('/api/notificar-vencimentos', methods=['POST'])
def notificar_vencimentos():
    conn = None
    try:
        # Carrega as credenciais seguras do arquivo .env
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        client = Client(account_sid, auth_token)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Query para buscar registros que vencem nos próximos 30 dias
        sql = """
            SELECT R.*, F.nome, F.telefone, T.nome_treinamento 
            FROM FactRegistros R
            JOIN DimFuncionarios F ON R.id_funcionario = F.id_funcionario
            JOIN DimTreinamentos T ON R.id_treinamento = T.id_treinamento
            WHERE R.data_vencimento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
        """
        cursor.execute(sql)
        vencendo = cursor.fetchall()
        
        contador_sucesso = 0
        for reg in vencendo:
            # Sanitiza o número do banco de dados antes do envio
            telefone_limpo = formatar_para_twilio(reg['telefone'])
            
            # Validação defensiva básica para evitar strings vazias ou nulas
            if not telefone_limpo or len(telefone_limpo) < 10:
                print(f"Pulo: Colaborador {reg['nome']} ignorado por falta de telefone válido.")
                continue
            
            # Personaliza a mensagem corporativa
            mensagem = f"Olá {reg['nome']}, seu treinamento de {reg['nome_treinamento']} vence em breve no dia {reg['data_vencimento']}."
            
            # 1. Disparo de canal tradicional via SMS
            client.messages.create(
                body=mensagem,
                from_=from_number,
                to=telefone_limpo
            )
            
            # 2. Disparo de canal instantâneo via WhatsApp
        whatsapp_from = os.getenv('TWILIO_WHATSAPP_NUMBER')
        client.messages.create(
             body=mensagem,
             from_=f"whatsapp:{whatsapp_from}",
             to=f"whatsapp:{telefone_limpo}"
           )
            
        return jsonify({"mensagem": f"{contador_sucesso} notificações enviadas com sucesso via SMS e WhatsApp!"}), 200

    except Exception as e:
        # Registra a exceção no console para fins de depuração
        print(f"Erro ao notificar: {str(e)}")
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)


