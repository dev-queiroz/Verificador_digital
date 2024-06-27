from pyfingerprint.pyfingerprint import PyFingerprint
import sqlite3

class Academia:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.criar_tabela_clientes()

    def criar_tabela_clientes(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
                                id INTEGER PRIMARY KEY,
                                nome TEXT,
                                fingerprint BLOB)''')
        self.conn.commit()

    def cadastrar_cliente(self, nome_cliente, fingerprint):
        self.cursor.execute("INSERT INTO clientes (nome, fingerprint) VALUES (?, ?)", (nome_cliente, fingerprint))
        self.conn.commit()

    def obter_fingerprints(self):
        self.cursor.execute("SELECT id, fingerprint FROM clientes")
        rows = self.cursor.fetchall()
        return rows

    def fechar_conexao(self):
        self.conn.close()

# Configurações
db_file = "academia.db"
com_port = '/dev/ttyUSB0'  # Porta COM do leitor de impressões digitais

# Inicialização do leitor de impressões digitais
try:
    fingerprint = PyFingerprint(com_port, 57600, 0xFFFFFFFF, 0x00000000)
    if not fingerprint.verifyPassword():
        raise ValueError('Erro ao inicializar o leitor de impressões digitais!')
except Exception as e:
    print('Erro: ' + str(e))
    exit(1)

def registrar_fingerprint():
    print('Por favor, coloque seu dedo no leitor...')
    while not fingerprint.readImage():
        pass
    fingerprint.convertImage(0x01)
    return fingerprint.downloadCharacteristics()

def comparar_fingerprints(fingerprint1, fingerprint2):
    # Comparação de impressões digitais utilizando a biblioteca PyFingerprint
    return fingerprint1 == fingerprint2

# Exemplo de uso
academia = Academia(db_file)

# Cadastro de clientes
while True:
    nome_cliente = input("Digite o nome do cliente (ou 'sair' para terminar): ")
    if nome_cliente.lower() == 'sair':
        break
    fingerprint_data = registrar_fingerprint()
    academia.cadastrar_cliente(nome_cliente, fingerprint_data)
    print("Cliente cadastrado com sucesso!")

# Verificação de identidade
print('Por favor, coloque seu dedo no leitor...')
while not fingerprint.readImage():
    pass
fingerprint.convertImage(0x01)
fingerprint_data = fingerprint.downloadCharacteristics()

for id_cliente, fingerprint_bd in academia.obter_fingerprints():
    if comparar_fingerprints(fingerprint_data, fingerprint_bd):
        print("Bem-vindo(a), cliente de ID {}!".format(id_cliente))
        break
else:
    print("Acesso negado. Cliente não reconhecido.")

academia.fechar_conexao()
