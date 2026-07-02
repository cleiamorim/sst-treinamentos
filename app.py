# =======================================================================================
# ARQUIVO DE INFRAESTRUTURA BACK-END: app.py (API RESTful Completa)
# CONTEXTO ACADÊMICO/CORPORATIVO: CLAM SST 4.0 - Safety Analytics
# TECNOLOGIA PRINCIPAL: Python 3 com Flask & MySQL Connector Relacional
# DIDÁTICA: Padrão MVC (Model-Controller), Injeção de Dependências e Integração Omnichannel
# =======================================================================================

# 📦 IMPORTAÇÃO DE BIBLIOTECAS NATIVAS E EXTENSÕES DO ECOSSISTEMA PYTHON
import os  # Biblioteca nativa do sistema operacional. Permite ler variáveis de ambiente seguras (Environment Variables).
import re  # Módulo de Expressões Regulares (RegEx). Essencial para higienização, validação e manipulação de padrões de texto.

# Componentes do Microframework Flask para tratamento do ciclo de vida das requisições web
from flask import Flask, request, jsonify  
# Flask: Classe construtora da nossa aplicação web.
# request: Objeto global que captura os dados de entrada vindos do cliente (Headers, Body, Args).
# jsonify: Função que serializa estruturas de dados do Python (dicionários/listas) no formato JSON puro.

import mysql.connector  # Driver de conectividade oficial da Oracle para estabelecer sessões e executar transações SQL no MySQL.
from dotenv import load_dotenv  # Componente responsável por ler o arquivo confidencial '.env' e disponibilizar chaves no escopo do OS.

from twilio.rest import Client  # Cliente conector do SDK da Twilio. Abre os túneis de transmissão de pacotes para a rede de telefonia mundial.

# Componentes de segurança Cross-Origin Resource Sharing (CORS) para gerenciar permissões de requisições de domínios diferentes
from flask_cors import CORS, cross_origin  

# =======================================================================================
# ⚙️ BOOTSTRAP / INICIALIZAÇÃO DE VARIÁVEIS E COMPONENTES GLOBAIS
# =======================================================================================

# Carrega as variáveis do arquivo .env diretamente na memória volátil do ambiente operacional
load_dotenv()

# Instancia a nossa aplicação Flask passando a constante mágica __name__ para configurar o diretório raiz do servidor
app = Flask(__name__)

# Configura as políticas do CORS de forma granular:
# Define que qualquer endpoint contido na rota biunívoca '/api/*' aceitará requisições de qualquer origem ("*")
# e responderá com segurança aos métodos semânticos do protocolo HTTP: GET, POST, PUT e DELETE.
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE"]}})

# Dicionário Relacional db_config: centraliza os parâmetros de handshake da rede local do MySQL.
# Utiliza o os.getenv para puxar as credenciais protegidas, evitando o vazamento de dados sensíveis em repositórios públicos.
db_config = {
    'host': os.getenv('DB_HOST'),        # Endereço IP do servidor de banco de dados (Ex: 127.0.0.1)
    'database': os.getenv('DB_NAME'),    # Nome do catálogo lógico criado no MySQL (INF07SST)
    'user': os.getenv('DB_USER'),        # Nome do usuário administrativo do SGBD (Ex: root)
    'password': os.getenv('DB_PASS')     # Senha alfanumérica secreta do banco de dados
}

# Função de Fábrica (Factory Pattern) get_db_connection:
# Abre e retorna uma nova instância ativa de conexão com o banco de dados.
# O operador duplo asterisco (**) desempacota o dicionário db_config e passa suas chaves como parâmetros explícitos do conector.
def get_db_connection(): 
    return mysql.connector.connect(**db_config)

# =======================================================================================
# 🛠️ FUNÇÃO AUXILIAR PEDAGÓGICA: HIGIENIZAÇÃO DE STRINGS PARA O PADRÃO INTERNACIONAL E.164
# APLICABILIDADE: A Twilio exige que os números telefônicos de destino estejam formatados rigidamente sem máscaras.
# =======================================================================================
def formatar_para_twilio(telefone_raw):
    # Cláusula de Salvaguarda (Guard Clause): evita erros de execução caso o número venha nulo ou vazio
    if not telefone_raw:
        return ""
    
    # re.sub(r'\D'): Expressão regular que varre a string e substitui tudo o que NÃO for dígito (\D) por vazio ""
    # Remove de forma cirúrgica os parênteses, espaços, pontos e traços inseridos pelas máscaras do front-end
    numeros = re.sub(r'\D', '', str(telefone_raw))
    
    # Se a string higienizada contiver 11 caracteres (Padrão celular brasileiro: DDD + 9 dígitos)
    if len(numeros) == 11:
        return f"+55{numeros}" # Retorna anexando o código internacional do Brasil (+55)
        
    # Se a string já possuir 13 caracteres (usuário inseriu o código do país manualmente)
    elif len(numeros) == 13:
        return f"+{numeros}" # Adiciona unicamente o sinal de mais (+) exigido pela Twilio
        
    return numeros # Retorna o número limpo como plano de recuo (fallback)

# =======================================================================================
# 🗂️ MODELOS DE DOMÍNIO (CLASSES ENTIDADES - PADRÃO POO)
# APLICABILIDADE: Representação em orientação a objetos das tabelas relacionais do MySQL.
# =======================================================================================

class Funcionario:
    # Método Construtor: Inicializa as propriedades do objeto na memória do Python
    def __init__(self, nome, cpf, cargo, setor, email, telefone, whatsapp, id=None):
        self.id = id # O ID inicia como padrão None porque em novos registros quem gera o código é o AUTO_INCREMENT do MySQL
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
    # Representação da nossa tabela Fato (Conexão N para N entre Funcionários e Normas Regulamentadoras)
    def __init__(self, id_funcionario, id_treinamento, data_realizacao, status='Ativo', id=None):
        self.id = id
        self.id_funcionario = id_funcionario # Chave Estrangeira (FK) apontando para o trabalhador
        self.id_treinamento = id_treinamento # Chave Estrangeira (FK) apontando para o curso normativo
        self.data_realizacao = data_realizacao
        self.status = status

# =======================================================================================
# 🏢 MÓDULO 1: ENDPOINTS DA API PARA GESTÃO DE FUNCIONÁRIOS (TABELA DIMENSÃO)
# =======================================================================================

# OPERAÇÃO: CREATE (MÉTODO HTTP POST)
@app.route('/api/funcionario', methods=['POST'])
def cadastrar_funcionario():
    conn = None
    try:
        # request.get_json(): Intercepta a carga útil (payload) JSON enviada pelo JavaScript e a converte em dicionário Python
        dados = request.get_json()
        
        # Instancia a classe de modelo mapeando os dados vindos das chaves do dicionário
        func = Funcionario(dados['nome'], dados['cpf'], dados['cargo'], dados['setor'], 
                           dados['email'], dados['telefone'], dados['whatsapp'])
        
        conn = get_db_connection() # Solicita uma conexão ativa com o MySQL
        cursor = conn.cursor()     # Instancia o cursor técnico para trafegar comandos SQL na sessão
        
        # SQL Parametrizado: Prática crucial contra ataques de SQL Injection. Usamos demarcadores '%s' em vez de concatenar strings.
        sql = "INSERT INTO DimFuncionarios (nome, cpf, cargo, setor, email, telefone, whatsapp) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        
        # O cursor se encarrega de higienizar e injetar com segurança a tupla de dados nos marcadores da query
        cursor.execute(sql, (func.nome, func.cpf, func.cargo, func.setor, func.email, func.telefone, func.whatsapp))
        
        conn.commit() # Consolida e grava de forma permanente a transação no disco rígido do banco de dados
        return jsonify({"mensagem": "Funcionário cadastrado!"}), 201 # Retorna código de sucesso HTTP 201 (Created)
    except Exception as e:
        if conn: conn.rollback() # Mecanismo de segurança de transações: se a gravação der erro, desfaz tudo na memória para evitar dados corrompidos
        return jsonify({"erro": str(e)}), 500 # Retorna o erro técnico com código HTTP 500 (Internal Server Error)
    finally:
        # Bloco Finally Defensivo: Garante que a conexão de rede com o MySQL seja fechada, liberando recursos do servidor
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# OPERAÇÃO: UPDATE (MÉTODO HTTP PUT)
@app.route('/api/funcionario/<int:id>', methods=['PUT'])
def atualizar_funcionario(id): # Captura a variável tipada '<int:id>' informada diretamente no endereço da rota do navegador
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
        
        # cursor.rowcount: Retorna o número de linhas afetadas. Se for 0, o ID enviado não existe na tabela.
        if cursor.rowcount == 0: return jsonify({"mensagem": "Funcionário não encontrado."}), 404
        return jsonify({"mensagem": "Funcionário updated com sucesso!"}), 200 # Retorna código HTTP 200 (OK)
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# OPERAÇÃO: DELETE (MÉTODO HTTP DELETE)
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

# OPERAÇÃO: SEARCH / READ FILTRADO (MÉTODO HTTP GET)
@app.route('/api/funcionario/buscar', methods=['GET'])
def buscar_funcionarios():
    conn = None
    try:
        # request.args.get: Captura argumentos passados via parâmetros de Query String na URL (Ex: /buscar?nome=Clei)
        nome = request.args.get('nome')
        
        conn = get_db_connection()
        # dictionary=True: Configura o driver para retornar as tuplas do banco no formato de dicionários Python (Chave: Valor), facilitando o parse para JSON
        cursor = conn.cursor(dictionary=True)
        
        sql = "SELECT * FROM DimFuncionarios WHERE 1=1" # "WHERE 1=1" é uma técnica limpa para concatenar novos filtros SQL condicionalmente
        params = []
        
        if nome:
            sql += " AND nome LIKE %s" # Aplica o operador de busca parcial LIKE do SQL
            params.append(f"%{nome}%") # Adiciona as curingas textuais de busca por porcentagem (%)
            
        cursor.execute(sql, tuple(params))
        funcionarios = cursor.fetchall() # Coleta a lista completa de linhas correspondentes encontradas no MySQL
        return jsonify(funcionarios), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# =========================================================
# 📚 MÓDULO 2: ENDPOINTS DA API GESTÃO DE TREINAMENTOS (TABELA DIMENSÃO)
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

# =======================================================================================
# ⚖️ MÓDULO 3: ENDPOINTS DA API PARA HOMOLOGAÇÃO DE CAPACITAÇÕES (TABELA FATO)
# APLICABILIDADE: Realiza inteligência e cálculos de tempo em banco de dados relacional.
# =======================================================================================

# OPERAÇÃO: CREATE REGISTRO FATO (CALCULA A DATA DE VENCIMENTO FUTURA AUTOMATICAMENTE)
@app.route('/api/registros', methods=['POST'])
def registrar_treinamento():
    conn = None
    try:
        dados = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Subquery de Regra de Negócio: faz uma leitura prévia na DimTreinamentos para extrair quantos meses vale a norma selecionada
        cursor.execute("SELECT validade_meses FROM DimTreinamentos WHERE id_treinamento = %s", (dados['id_treinamento'],))
        treino = cursor.fetchone()
        
        if not treino:
            return jsonify({"erro": "Treinamento não encontrado"}), 404
        
        validade = treino['validade_meses'] # Captura o número inteiro de meses legal (Ex: 24 meses)
        
        # CÁLCULO RELACIONAL NATIVO:
        # Utilizamos a função matemática DATE_ADD() nativa do motor do MySQL. 
        # Ela intercepta a string da 'data_realizacao' enviada do front-end e injeta dinamicamente o intervalo de meses legal (INTERVAL %s MONTH).
        # Isso blinda o sistema fazendo o próprio banco de dados calcular e gravar a coluna 'data_vencimento' de forma ultra-precisa!
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
        return jsonify({"erro": f"Erro ao processar registro: {str(e)} "}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# OPERAÇÃO: READ TABELA FATO ENRIQUECIDA (CONSULTA COM CLAUSULAS JOIN)
@app.route('/api/registros', methods=['GET'])
def listar_registros():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # MODELAGEM DE DADOS MULTIDIMENSIONAL (JOINS):
        # Como a tabela fato FactRegistros armazena de forma performática apenas chaves numéricas (IDs), 
        # efetuamos cláusulas INNER JOIN cruzando as tabelas DimFuncionarios e DimTreinamentos na sessão.
        # Isso traz de volta os campos nominais textuais completos (F.nome e T.nome_treinamento) estruturados para o painel do Bootstrap.
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

# =======================================================================================
# 📱 MÓDULO 4 OMNICHANNEL: AUTOMAÇÃO TELECOM VIA GATEWAY TWILIO (SMS + WHATSAPP)
# APLICABILIDADE: Executa varreduras temporais analíticas buscando inconformidades críticas de segurança em campo.
# =======================================================================================
@app.route('/api/notificar-vencimentos', methods=['POST'])
def notificar_vencimentos():
    conn = None
    try:
        # Inicializa a extração dos tokens mestres de autenticação salvos no arquivo oculto de ambiente (.env)
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_PHONE_NUMBER')        # Número gerador de SMS alocado na Twilio
        whatsapp_from = os.getenv('TWILIO_WHATSAPP_NUMBER')    # ID do canal corporativo de WhatsApp Business no Sandbox
        
        # Instancia e injeta as credenciais de segurança abrindo o objeto de sessão do cliente Twilio
        client = Client(account_sid, auth_token)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # QUERY ANALYTICS PREVENTIVA:
        # Filtra as homologações fato extraindo as linhas cujo vencimento da NR esteja compreendido de forma estrita 
        # entre o dia de HOJE (CURDATE()) e os próximos 30 dias futuros (DATE_ADD(CURDATE(), INTERVAL 30 DAY)).
        sql = """
            SELECT R.*, F.nome, F.telefone, T.nome_treinamento 
            FROM FactRegistros R
            JOIN DimFuncionarios F ON R.id_funcionario = F.id_funcionario
            JOIN DimTreinamentos T ON R.id_treinamento = T.id_treinamento
            WHERE R.data_vencimento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
        """
        cursor.execute(sql)
        vencendo = cursor.fetchall() # Armazena em um array os colaboradores que exigem reciclagem iminente
        
        contador_sucesso = 0 # Inicializa o contador de entregas omnichannel com sucesso
        
        # Laço Iterador (For): Varre individualmente cada trabalhador em estado de alerta crítico retornado
        for reg in vencendo:
            # Invoca a nossa função auxiliar de higienização telefônica para remover traços e espaços da máscara
            telefone_limpo = formatar_para_twilio(reg['telefone'])
            
            # Programação Defensiva: Se o número for inválido ou strings vazias, pula o loop e vai para o próximo (impede travas na execução)
            if not telefone_limpo or len(telefone_limpo) < 10:
                print(f"Pulo: Colaborador {reg['nome']} ignorado por falta de telefone válido.")
                continue
            
            # String dinâmica interpolada contendo o texto corporativo normativo personalizado com os dados do banco
            mensagem = f"Olá {reg['nome']}, seu treinamento de {reg['nome_treinamento']} vence em breve no dia {reg['data_vencimento']}."
            
            # CANAL 1 (TRADICIONAL): Dispara pacote de texto via SMS (indispensável para indústrias, minerações ou galpões sem acesso à internet de dados)
            client.messages.create(
                body=mensagem,
                from_=from_number,
                to=telefone_limpo
            )
            
            # CANAL 2 (INSTANTÂNEO): Dispara pacote de texto via WhatsApp (foco total em engajamento instantâneo do colaborador)
            # Nota técnica: O ecossistema Twilio exige o prefixo textual fixo 'whatsapp:' antes dos números telefônicos
            client.messages.create(
                body=mensagem,
                from_=f"whatsapp:{whatsapp_from}",
                to=f"whatsapp:{telefone_limpo}"
            )
            
            # Incrementa o contador técnico a cada loop completado com sucesso
            contador_sucesso += 1
            
        # Retorna um objeto JSON informando ao front-end o relatório estatístico consolidado de mensagens entregues na operadora
        return jsonify({"mensagem": f"{contador_sucesso} notificações enviadas com sucesso via SMS e WhatsApp!"}), 200

    except Exception as e:
        # Grava os logs de erros técnicos da pilha de exceções (Traceback) no terminal do terminal do Python para fins de depuração do desenvolvedor
        print(f"Erro ao notificar: {str(e)}")
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# COMANDO BOOTSTRAPPER DO PYTHON:
# Garante que o arquivo só subirá o servidor HTTP do Flask se for executado diretamente no interpretador local (como arquivo principal)
if __name__ == '__main__':
    # Inicializa o motor do servidor web local na porta padrão 5000. 
    # O parâmetro debug=True escuta em tempo real o arquivo: se você salvar qualquer caractere, o Flask reinicia o servidor sozinho!
    app.run(debug=True)
