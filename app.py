# =======================================================================================
# ARQUIVO DE INFRAESTRUTURA BACK-END: app.py (API RESTful Completa)
# CONTEXTO ACADÊMICO/CORPORATIVO: CLAM SST 4.0 - Safety Analytics
# TECNOLOGIA PRINCIPAL: Python 3 com Flask & MySQL Connector Relacional
# DIDÁTICA: Padrão MVC (Model-Controller), Injeção de Dependências e Integração Omnichannel
# =======================================================================================

# 📦 IMPORTAÇÃO DE BIBLIOTECAS NATIVAS E EXTENSÕES DO ECOSSISTEMA PYTHON

# io (Input/Output): Biblioteca nativa para manipular fluxos de bytes e dados em memória.
# Essencial para criar arquivos virtuais temporários (buffers) sem precisar salvá-los fisicamente no HD do servidor.
import io  

# os (Operating System): Permite ao Python interagir diretamente com o sistema operacional da máquina host.
# Utilizado estrategicamente aqui para ler credenciais e chaves secretas injetadas no ambiente (Segurança).
import os  

# re (Regular Expressions): Mecanismo nativo de Expressões Regulares.
# Serve para varrer strings e identificar, isolar ou extrair padrões de caracteres complexos através de máscaras textuais.
import re  

# Componentes lógicos do Microframework Flask que gerenciam o ciclo de vida das requisições e respostas HTTP
from flask import Flask, request, jsonify, send_file  
# Flask: Classe construtora primordial que inicializa e levanta o servidor web.
# request: Objeto de escopo global que intercepta e armazena os dados vindos do cliente (Headers, Body, Query Strings).
# jsonify: Função que serializa dicionários/listas nativos do Python no formato padrão JSON (JavaScript Object Notation).
# send_file: Componente que envia fluxos de arquivos binários ou páginas físicas diretas como resposta de download para o navegador.

# mysql.connector: Driver de conectividade oficial homologado pela Oracle para comunicação com o MySQL.
# É ele quem abre portas de rede, gerencia sessões de transação e traduz os comandos execute() para o SGBD.
import mysql.connector  

# pandas (pd): A biblioteca mais famosa do mundo para manipulação e análise de estruturas de dados.
# No projeto, ela atua transformando matrizes lógicas em DataFrames para gerar planilhas CSV e XLSX de forma automatizada.
import pandas as pd  

# load_dotenv: Componente que localiza e faz o parse do arquivo confidencial '.env',
# carregando as credenciais de banco e chaves de API direto na memória do ambiente do sistema operacional.
from dotenv import load_dotenv  

# Client: Classe construtora do SDK oficial da Twilio.
# É ela quem estabelece a ponte de comunicação e autenticação com os servidores de telefonia global em nuvem da Twilio.
from twilio.rest import Client  

# CORS (Cross-Origin Resource Sharing): Extensão de segurança indispensável.
# Sem o CORS, os navegadores modernos bloqueiam requisições JavaScript feitas a partir de portas diferentes (Ex: Live Server na 5500 acessando Flask na 5000).
from flask_cors import CORS

# =======================================================================================
# ⚙️ BOOTSTRAP / INICIALIZAÇÃO DE VARIÁVEIS E COMPONENTES GLOBAIS
# =======================================================================================

# Invoca a varredura do arquivo de configuração '.env' para carregar as chaves de acesso no escopo do sistema operacional
load_dotenv()

# Instancia o núcleo da aplicação Flask. O parâmetro __name__ informa ao framework o módulo atual para gerenciar escopos e arquivos estáticos.
app = Flask(__name__)

# Configura as diretrizes de CORS abertamente para ambiente de desenvolvimento local:
# Mapeia que qualquer endpoint contido no caminho '/api/*' aceitará requisições vindas de qualquer origem ("*")
# e responderá com segurança aos métodos HTTP semânticos: GET, POST, PUT e DELETE.
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE"]}})

# Dicionário Relacional db_config: Armazena os parâmetros fundamentais para o aperto de mão (handshake) com o MySQL.
# Aplica uma técnica defensiva usando os.getenv: se a chave não existir no arquivo de ambiente, o código não expõe falhas.
db_config = {
    'host': os.getenv('DB_HOST'),        # Endereço de rede do banco (Ex: 127.0.0.1 ou localhost)
    'database': os.getenv('DB_NAME'),    # Nome do catálogo/esquema relacional criado (inf07sst)
    'user': os.getenv('DB_USER'),        # Nome do usuário com privilégios administrativos (Ex: root)
    'password': os.getenv('DB_PASS')     # Senha secreta correspondente ao usuário do banco
}

# Função de Fábrica (Factory Pattern) get_db_connection:
# Centraliza a abertura de conexões. Toda rota que precisar transacionar dados chamará este bloco.
# O operador duplo asterisco (**) desempacota o dicionário 'db_config' passando chaves e valores como argumentos nomeados.
def get_db_connection(): 
    # Abre uma nova conexão limpa de rede com o MySQL a cada chamada.
    # Como não utiliza pool de conexões reutilizáveis, cada bloco de rota fica obrigado a fechar a sessão ao concluir.
    return mysql.connector.connect(**db_config)

# =======================================================================================
# 🌐 ROTAS DE APRESENTAÇÃO E ENTREGA DO SITE ESTÁTICO (WEB SERVER)
# =======================================================================================

# Rota Raiz ('/'): Intercepta o acesso principal do domínio (Ex: http://localhost:5000/)
@app.route('/')
def index():
    # Envia o arquivo físico index.html como resposta imediata, permitindo que o Flask atue também como servidor web estático.
    return send_file('index.html')

# Rota de redundância para index.html: Evita erros 404 caso o front-end tente carregar o endereço nominal explicitamente.
@app.route('/index.html')
def index_html():
    return send_file('index.html')

# =======================================================================================
# 🛠️ FUNÇÃO AUXILIAR PEDAGÓGICA: HIGIENIZAÇÃO DE STRINGS PARA O PADRÃO INTERNACIONAL E.164
# APLICABILIDADE: A Twilio exige que os números telefônicos de destino estejam formatados rigidamente sem máscaras.
# =======================================================================================
def formatar_para_twilio(telefone_raw):
    # Cláusula de Salvaguarda (Guard Clause): Aborta a execução caso a string recebida seja nula ou vazia, prevenindo erros na pilha.
    if not telefone_raw:
        return ""
    
    # re.sub(r'\D'): Localiza recursivamente tudo o que NÃO for um dígito numérico (\D) e substitui por uma string vazia "".
    # Faz a limpeza completa eliminando de forma cirúrgica parênteses, traços, pontos e espaçamentos inseridos por máscaras visuais.
    numeros = re.sub(r'\D', '', str(telefone_raw))
    
    # Se a string limpa resultar em 11 caracteres (Padrão móvel brasileiro atual com nono dígito: DDD + 9 números)
    if len(numeros) == 11:
        return f"+55{numeros}" # Retorna o número injetando o código internacional regulamentar do país (Brasil = +55)
        
    # Se a string resultante já contiver 13 caracteres (indica que o usuário digitou o código do país na entrada de dados)
    elif len(numeros) == 13:
        return f"+{numeros}" # Adiciona unicamente o caractere de mais (+), consolidando a string E.164 para a Twilio
        
    # Se o tamanho for fora do padrão esperado, devolve os dígitos limpos como plano de recuo (fallback) para análise posterior.
    return numeros 

# =======================================================================================
# 🗂️ MODELOS DE DOMÍNIO (CLASSES ENTIDADES - PADRÃO POO)
# APLICABILIDADE: Representação orientada a objetos que espelha as colunas estruturais do banco MySQL.
# =======================================================================================

class Funcionario:
    # Método Especial Construtor: Inicializa a entidade mapeando os atributos na memória interna do Python.
    def __init__(self, nome, cpf, cargo, setor, email, telefone, whatsapp, id=None):
        self.id = id # O ID inicia como None pois em inserções (POST) quem define a chave primária é o AUTO_INCREMENT do MySQL.
        self.nome = nome
        self.cpf = cpf
        self.cargo = cargo
        self.setor = setor
        self.email = email
        self.telefone = telefone
        self.whatsapp = whatsapp
        # Nota didática: Esta classe atua puramente como um Data Transfer Object (DTO). 
        # Ela encapsula as informações sem carregar lógicas internas de persistência ou conexão de banco de dados.

class Treinamento:
    def __init__(self, nome_treinamento, validade_meses, id=None):
        self.id = id
        self.nome_treinamento = nome_treinamento
        self.validade_meses = validade_meses
        # Classe de domínio representativa das Normas Regulamentadoras (Grade Curricular Técnica de Treinamentos).

class Registro:
    # Mapeamento do Core da nossa Tabela Fato: Registra o evento histórico cruzando os atores de SST.
    def __init__(self, id_funcionario, id_treinamento, data_realizacao, status='Ativo', id=None):
        self.id = id
        self.id_funcionario = id_funcionario # Atua como Chave Estrangeira (FK) referenciando DimFuncionarios
        self.id_treinamento = id_treinamento # Atua como Chave Estrangeira (FK) referenciando DimTreinamentos
        self.data_realizacao = data_realizacao
        self.status = status

# =======================================================================================
# 🏢 MÓDULO 1: CONTROLADORES LOGICOS DA API PARA GESTÃO DE FUNCIONÁRIOS (DIMENSÃO)
# =======================================================================================

# OPERAÇÃO: CREATE (MÉTODO HTTP POST MAO ÚNICA)
@app.route('/api/funcionario', methods=['POST'])
def cadastrar_funcionario():
    # Rota acionada quando o JavaScript envia um payload de dados para criar um novo trabalhador na base
    conn = None
    try:
        # request.get_json(): Intercepta o fluxo de bytes de entrada e reconverte o corpo da requisição JSON em dicionário do Python
        dados = request.get_json()
        
        # Cria a instância da classe alimentando as chaves indexadas correspondentes vindas da requisição
        func = Funcionario(dados['nome'], dados['cpf'], dados['cargo'], dados['setor'], 
                           dados['email'], dados['telefone'], dados['whatsapp'])
        
        conn = get_db_connection() # Abre canal síncrono com o MySQL
        cursor = conn.cursor()     # Cria o cursor para trafegar e executar instruções SQL
        
        # Query Parametrizada: Substitui concatenações diretas por marcadores coringa %s. Técnica padrão de segurança contra SQL Injection.
        sql = "INSERT INTO DimFuncionarios (nome, cpf, cargo, setor, email, telefone, whatsapp) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        
        # O cursor se encarrega de sanitizar e injetar com segurança a tupla de valores no lugar de cada marcador %s
        cursor.execute(sql, (func.nome, func.cpf, func.cargo, func.setor, func.email, func.telefone, func.whatsapp))
        
        conn.commit() # Transação atômica: Força o MySQL a consolidar de verdade e gravar o registro nas páginas do disco
        return jsonify({"mensagem": "Funcionário cadastrado!"}), 201 # Retorna o JSON com código HTTP 201 (Created)
    except Exception as e:
        if conn: conn.rollback() # Caso ocorra violação de restrição (Ex: CPF já existente), reverte as alterações em memória limpando a transação
        return jsonify({"erro": str(e)}), 500 # Devolve o erro para o console do front-end com código HTTP 500
    finally:
        # Cláusula de encerramento obrigatório: Evita o estouro do limite máximo de conexões simultâneas abertas no banco MySQL
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# OPERAÇÃO: UPDATE (MÉTODO HTTP PUT DIRECIONADO POR ID)
@app.route('/api/funcionario/<int:id>', methods=['PUT'])
def atualizar_funcionario(id): 
    # Recebe no argumento o ID inteiro capturado diretamente na rota do navegador para executar a alteração cirúrgica
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
        
        # cursor.rowcount: Retorna quantas linhas foram afetadas no banco. Se for 0, o ID enviado não existe na tabela.
        if cursor.rowcount == 0: return jsonify({"mensagem": "Funcionário não encontrado."}), 404
        return jsonify({"mensagem": "Funcionário updated com sucesso!"}), 200 # Retorna código HTTP 200 (OK)
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# OPERAÇÃO: DELETE (MÉTODO HTTP DELETE POR ID)
@app.route('/api/funcionario/<int:id>', methods=['DELETE'])
def excluir_funcionario(id):
    # Executa a remoção física do colaborador identificado pelo identificador numérico da URL
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

# OPERAÇÃO: READ / SEARCH FILTRADO (MÉTODO HTTP GET COM QUERY STRINGS)
@app.route('/api/funcionario/buscar', methods=['GET'])
def buscar_funcionarios():
    # Rota de leitura flexível: Serve tanto para alimentar as tabelas iniciais quanto para processar filtros de busca por nome
    conn = None
    try:
        # request.args.get: Captura argumentos passados na URL após o caractere de interrogação (Ex: /buscar?nome=Cleidson)
        nome = request.args.get('nome')
        
        conn = get_db_connection()
        # dictionary=True: Configura de forma brilhante o cursor para empacotar as linhas do MySQL como dicionários nativos.
        # Isso faz o Python gerar chaves com os nomes exatos das colunas (Ex: {'nome': 'João'}), eliminando a leitura posicional por tuplas vazias.
        cursor = conn.cursor(dictionary=True)
        
        sql = "SELECT * FROM DimFuncionarios WHERE 1=1" # Estratégia limpa: Permite acoplar novas cláusulas AND sem quebrar a sintaxe do SQL
        params = []
        
        if nome:
            sql += " AND nome LIKE %s" # Injeta o operador de correspondência parcial LIKE do SQL
            params.append(f"%{nome}%") # Concatena os caracteres curingas (%) de busca em qualquer posição do texto
            
        cursor.execute(sql, tuple(params))
        funcionarios = cursor.fetchall() # Coleta a matriz completa de dicionários correspondentes do banco
        return jsonify(funcionarios), 200 # Envia a estrutura convertida em JSON estável para o front-end
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# =========================================================
# 📚 MÓDULO 2: ENDPOINTS DA API PARA GESTÃO DA GRADE DE TREINAMENTOS (DIMENSÃO)
# =========================================================

@app.route('/api/treinamento', methods=['POST'])
def cadastrar_treinamento():
    # Cadastra novas capacitações e cargas horárias legais na dimensão de normas técnicas.
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
    # Retorna o catálogo completo de NRs disponíveis em JSON para renderizar tabelas e preencher comboboxes de seleção.
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

@app.route('/api/treinamento/buscar', methods=['GET'])
def buscar_treinamentos():
    # Filtra e pesquisa termos específicos dentro da grade de cursos técnicos de segurança cadastrados.
    nome = request.args.get('nome', '').strip()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        sql = "SELECT * FROM DimTreinamentos WHERE 1=1"
        params = []
        if nome:
            sql += " AND nome_treinamento LIKE %s"
            params.append(f"%{nome}%")

        cursor.execute(sql, tuple(params) if params else ())
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
    # Modifica as propriedades textuais ou prazos de validade regulamentares de uma norma por ID.
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
    # Remove uma norma técnica do catálogo. Nota: Chaves dependentes na fato serão tratadas pelas restrições do banco.
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
# ⚖️ MÓDULO 3: ENDPOINTS DA API PARA HOMOLOGAÇÃO DE HISTÓRICOS DE CURSOS (TABELA FATO)
# APLICABILIDADE: Núcleo inteligente do Safety Analytics. Executa a amarração relacional de chaves estrangeiras.
# =======================================================================================

# OPERAÇÃO: CREATE REGISTRO FATO (CÁLCULO AUTOMÁTICO DE VENCIMENTOS NO MYSQL)
@app.route('/api/registros', methods=['POST'])
def registrar_treinamento():
    # Rota responsável por homologar que um trabalhador X realizou o curso Y em uma data Z.
    conn = None
    try:
        dados = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Subquery de Verificação de Integridade de Regra de Negócio:
        # Busca no banco de dados a validade em meses cadastrada nativamente para o curso selecionado.
        cursor.execute("SELECT validade_meses FROM DimTreinamentos WHERE id_treinamento = %s", (dados['id_treinamento'],))
        treino = cursor.fetchone()
        
        if not treino:
            return jsonify({"erro": "Treinamento não encontrado"}), 404
        
        validade = treino['validade_meses'] # Coleta o número inteiro de vigência legal (Ex: 12 ou 24 meses)
        
        # INTELIGÊNCIA EM BANCO DE DADOS RELACIONAL:
        # Em vez de fazer cálculos complexos de tempo no Python, a query utiliza a função nativa DATE_ADD() do MySQL.
        # Ela recebe a string textual da data_realizacao e soma o intervalo de meses (INTERVAL %s MONTH) estipulado em lei,
        # gravando de forma automática, síncrona e precisa a coluna 'data_vencimento' direto na linha da tabela fato.
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

# FUNÇÃO ARQUITETURAL DE APOIO: CONSTRUTOR DINÂMICO DE QUERIES COM FILTROS AVANÇADOS
# Esta função analisa isoladamente o dicionário de argumentos vindos da tela e monta dinamicamente as cláusulas WHERE do SQL,
# retornando a string da instrução limpa e a tupla de parâmetros correspondente para execução segura.
def construir_sql_registros(args=None):
    args = args or request.args
    # Coleta e higieniza strings vazias eliminando espaços fantasmas nas pontas (.strip())
    data_inicio = (args.get('data_inicio', '') or '').strip()
    data_fim = (args.get('data_fim', '') or '').strip()
    id_treinamento = (args.get('id_treinamento', '') or '').strip()
    status_risco = (args.get('status_risco', '') or '').strip()
    nome = (args.get('nome', '') or '').strip()
    matricula = (args.get('matricula', '') or '').strip()

    # Query Base utilizando cláusulas INNER JOIN para cruzar as tabelas dimensão e trazer dados textuais ricos para a tela
    sql = """
        SELECT R.id_registro, R.id_funcionario, R.id_treinamento, F.nome AS funcionario, T.nome_treinamento,
               R.data_realizacao, R.data_vencimento, R.status
        FROM FactRegistros R
        JOIN DimFuncionarios F ON R.id_funcionario = F.id_funcionario
        JOIN DimTreinamentos T ON R.id_treinamento = T.id_treinamento
        WHERE 1=1
    """
    params = []

    # Concatenações lógicas condicionais baseadas nos filtros ativados pelo usuário no painel de relatórios do front-end
    if data_inicio:
        sql += " AND R.data_realizacao >= %s"
        params.append(data_inicio)

    if data_fim:
        sql += " AND R.data_realizacao <= %s"
        params.append(data_fim)

    if id_treinamento:
        sql += " AND R.id_treinamento = %s"
        params.append(int(id_treinamento))

    # Regras de Negócio aplicadas diretamente nas queries de data para classificar riscos
    if status_risco:
        if status_risco == 'Vencido':
            # Treinamento com flag explícita de vencido ou cuja data calculada de validade seja menor que o dia de hoje (CURDATE)
            sql += " AND (R.status = 'Vencido' OR R.data_vencimento < CURDATE())"
        elif status_risco == 'Alerta':
            # Janela de perigo crítico de auditoria: Treinamentos vencendo entre hoje e os próximos 30 dias regulamentares
            sql += " AND R.data_vencimento >= CURDATE() AND R.data_vencimento <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)"
        elif status_risco == 'EmDia':
            # Situação regular: Validade confortável superior a 30 dias futuros
            sql += " AND R.data_vencimento > DATE_ADD(CURDATE(), INTERVAL 30 DAY)"

    if nome:
        sql += " AND F.nome LIKE %s"
        params.append(f"%{nome}%")

    if matricula:
        sql += " AND F.id_funcionario = %s"
        params.append(int(matricula))

    return sql, params

# FUNÇÃO AUXILIAR DE ABASTECIMENTO DE CONSULTA INTERNA
# Executa a query estruturada pela função anterior e coleta o resultado bruto, garantindo o isolamento de tratamento de exceções.
def buscar_registros_filtrados(args=None):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        sql, params = construir_sql_registros(args)
        cursor.execute(sql, tuple(params) if params else ())
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao buscar registros: {str(e)}")
        return []
    finally:
        if cursor is not None:
            try: cursor.close()
            except Exception: pass
        if conn and conn.is_connected():
            try: conn.close()
            except Exception: pass

# FUNÇÃO INDUSTRIAL DE COMPILAÇÃO DE DADOS (CSV GENERATOR):
# Utiliza o pandas para estruturar um arquivo CSV puro com tratamento utf-8-sig (garante codificação correta para o Excel no Windows).
def gerar_csv_registros(registros):
    colunas = ["id_registro", "funcionario", "nome_treinamento", "data_realizacao", "data_vencimento", "status"]
    df = pd.DataFrame(registros or [], columns=colunas)
    buffer = io.BytesIO() # Cria um fluxo virtual binário na memória RAM da máquina
    df.to_csv(buffer, index=False, encoding='utf-8-sig') # Despeja o CSV gravando diretamente no buffer de memória
    return buffer.getvalue() # Retorna a string de bytes do arquivo pronto para download

# FUNÇÃO INDUSTRIAL DE COMPILAÇÃO DE DADOS (EXCEL GENERATOR):
# Cria uma planilha binária nativa compactada em formato OpenXML (.xlsx) em memória usando a engine openpyxl.
def gerar_xlsx_registros(registros):
    colunas = ["id_registro", "funcionario", "nome_treinamento", "data_realizacao", "data_vencimento", "status"]
    df = pd.DataFrame(registros or [], columns=colunas)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Relatório', index=False)
    return buffer.getvalue()

# OPERAÇÃO: READ DINÂMICO MULTI-FILTRADO (MÉTODO HTTP GET COMPLETO)
@app.route('/api/registros', methods=['GET'])
def listar_registros():
    # Rota que alimenta de forma flexível tanto a listagem geral quanto as buscas filtradas da aba de relatórios
    registros = buscar_registros_filtrados(request.args)
    return jsonify(registros), 200

# OPERAÇÃO: EXPURGO DE ENGENHARIA DE DADOS (MÉTODO HTTP GET DE EXPORTAÇÃO CORPORATIVA)
@app.route('/api/registros/exportar', methods=['GET'])
def exportar_registros():
    # Rota que permite ao usuário extrair relatórios complexos em formatos consolidados de mercado (CSV ou XLSX)
    formato = (request.args.get('formato', 'csv') or 'csv').lower()
    registros = buscar_registros_filtrados(request.args) # Coleta os dados respeitando os filtros de tela atuais

    if formato == 'xlsx':
        dados = gerar_xlsx_registros(registros)
        return send_file(
            io.BytesIO(dados),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='relatorio_treinamentos.xlsx'
        )

    # Fluxo de escape padrão caso não seja solicitado o formato XLSX: cospe o CSV estruturado
    dados = gerar_csv_registros(registros)
    return send_file(
        io.BytesIO(dados),
        mimetype='text/csv; charset=utf-8-sig',
        as_attachment=True,
        download_name='relatorio_treinamentos.csv'
    )

# OPERAÇÃO: UPDATE DA FATO COM RECALCULO SÍNCRONO (MÉTODO HTTP PUT)
@app.route('/api/registros/<int:id>', methods=['PUT'])
def atualizar_registro(id):
    # Rota crucial: Se o usuário edita as chaves ou a data de realização, o sistema recalcula na hora a data de vencimento correspondente
    conn = None
    try:
        dados = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Cláusula de segurança: Valida se o registro fato referenciado realmente existe antes de operar mutações
        cursor.execute("SELECT id_treinamento FROM FactRegistros WHERE id_registro = %s", (id,))
        registro_existente = cursor.fetchone()
        if not registro_existente:
            return jsonify({"mensagem": "Registro não encontrado."}), 404

        # Busca a validade regulamentar da norma atual escolhida na tela para operar a matemática do tempo
        cursor.execute("SELECT validade_meses FROM DimTreinamentos WHERE id_treinamento = %s", (dados['id_treinamento'],))
        treino = cursor.fetchone()
        if not treino:
            return jsonify({"erro": "Treinamento não encontrado"}), 404

        validade = treino['validade_meses']
        
        # Executa a query injetando o DATE_ADD() para redefinir o vencimento com base na nova data informada
        sql = """
            UPDATE FactRegistros
            SET id_funcionario = %s,
                id_treinamento = %s,
                data_realizacao = %s,
                data_vencimento = DATE_ADD(%s, INTERVAL %s MONTH)
            WHERE id_registro = %s
        """
        cursor.execute(sql, (
            dados['id_funcionario'],
            dados['id_treinamento'],
            dados['data_realizacao'],
            dados['data_realizacao'],
            validade,
            id
        ))
        conn.commit()
        return jsonify({"mensagem": "Registro updated com sucesso!"}), 200
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# OPERAÇÃO: DELETE FATO (MÉTODO HTTP DELETE NA FATO)
@app.route('/api/registros/<int:id>', methods=['DELETE'])
def deletar_registro(id):
    # Executa a revogação/exclusão de um histórico executivo de capacitação do banco pelo ID
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM FactRegistros WHERE id_registro = %s", (id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"mensagem": "Registro não encontrado."}), 404
        return jsonify({"mensagem": "Registro removido com sucesso!"}), 200
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# =======================================================================================
# 📱 MÓDULO 4 OMNICHANNEL: DISPAROS AUTOMATIZADOS DE TELECOMUNICAÇÕES (TWILIO ENGINE)
# APLICABILIDADE: Realiza análises temporais de riscos preventivos e alerta os trabalhadores por SMS e WhatsApp.
# =======================================================================================
@app.route('/api/notificar-vencimentos', methods=['POST'])
def notificar_vencimentos():
    # Rota acionada pelo painel para notificar preventivamente funcionários com treinamentos expirando nos próximos 30 dias
    conn = None
    try:
        # Extrai de forma blindada as chaves de API secretas carregadas do arquivo de configuração (.env)
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_PHONE_NUMBER')        # Número telefônico internacional emissor de SMS alocado na Twilio
        whatsapp_from = os.getenv('TWILIO_WHATSAPP_NUMBER')    # ID do canal corporativo integrado do WhatsApp Business
        
        # Instancia e injeta os tokens mestres inicializando o objeto de sessão da Twilio
        client = Client(account_sid, auth_token)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # QUERY ANALYTICS PREVENTIVA:
        # Coleta na tabela fato unicamente os registros cuja data_vencimento esteja compreendida entre 
        # a data do dia atual (CURDATE()) e os próximos 30 dias corridos futuros (DATE_ADD(CURDATE(), INTERVAL 30 DAY)).
        sql = """
            SELECT R.*, F.nome, F.telefone, T.nome_treinamento 
            FROM FactRegistros R
            JOIN DimFuncionarios F ON R.id_funcionario = F.id_funcionario
            JOIN DimTreinamentos T ON R.id_treinamento = T.id_treinamento
            WHERE R.data_vencimento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
        """
        cursor.execute(sql)
        vencendo = cursor.fetchall() # Captura a matriz com todas as inconformidades temporais críticas eminentes
        
        contador_sucesso = 0 # Inicializa acumulador estatístico para relatar a volumetria de envios concluídos
        
        # Laço de Repetição For: Itera individualmente sobre cada trabalhador irregular mapeado na query
        for reg in vencendo:
            # Invoca a nossa função auxiliar de tratamento telefônico para estruturar a string sob o padrão regulamentar E.164
            telefone_limpo = formatar_para_twilio(reg['telefone'])
            
            # Estratégia de Programação Defensiva: Se o telefone estiver incompleto ou ausente, pula o loop e vai para a próxima linha.
            # Isso impede de forma brilhante que um número digitado errado por um usuário trave a automação dos demais funcionários!
            if not telefone_limpo or len(telefone_limpo) < 10:
                print(f"Pulo: Colaborador {reg['nome']} ignorado por falta de telefone válido.")
                continue
            
            # Interpolação de string estruturando o layout da mensagem de notificação de SST personalizada com as colunas do MySQL
            mensagem = f"Olá {reg['nome']}, seu treinamento de {reg['nome_treinamento']} vence em breve no dia {reg['data_vencimento']}."
            
            # CANAL DE ENVIO 1: Dispara pacote binário via Short Message Service (SMS) corporativo. 
            # Excelente e indispensável em plantas industriais, minerações ou subsolos onde não há cobertura estável de dados móveis 4G/5G.
            client.messages.create(
                body=mensagem,
                from_=from_number,
                to=telefone_limpo
            )
            
            # CANAL DE ENVIO 2: Dispara pacote via aplicativo instantâneo WhatsApp Business.
            # Altíssimo nível de engajamento operacional. Nota: O ecossistema Twilio exige o prefixo fixo 'whatsapp:' colado nos números.
            client.messages.create(
                body=mensagem,
                from_=f"whatsapp:{whatsapp_from}",
                to=f"whatsapp:{telefone_limpo}"
            )
            
            contador_sucesso += 1 # Incrementa com sucesso o marcador a cada ciclo fechado
            
        # Devolve um dicionário serializado em JSON com status HTTP 200 relatando a volumetria de mensagens injetadas na operadora
        return jsonify({"mensagem": f"{contador_sucesso} notificações enviadas com sucesso via SMS e WhatsApp!"}), 200

    except Exception as e:
        # Grava os detalhes técnicos completos da exceção (stack trace) no console do terminal Python para fins de monitoramento técnico
        print(f"Erro ao notificar: {str(e)}")
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# INITIALIZATION CONSOLE COMMAND (BOOTSTRAPPER DO PROCESSO DA PORTA PYTHON)
# Garante que o servidor web HTTP do Flask só seja levantado na memória da máquina se o script for executado de forma principal.
if __name__ == '__main__':
    # Inicializa o motor de escuta de rede.
    # host='0.0.0.0': Abre a escuta para aceitar conexões vindas de qualquer IP da rede local, não limitando apenas ao localhost.
    # port=5000: Fixa a porta padrão de barramento de dados REST do Flask.
    # debug=True: Ativa o Hot-Reloading: Qualquer alteração salva no arquivo reescreve e reinicia o servidor web em tempo real.
    app.run(debug=True, host='0.0.0.0', port=5000)
