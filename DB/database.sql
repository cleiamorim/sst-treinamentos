DROP DATABASE IF EXISTS INF07SST;
CREATE DATABASE INF07SST;
USE INF07SST;

CREATE TABLE DimFuncionarios (
    id_funcionario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    cargo VARCHAR(50),
    setor VARCHAR(50)
);

CREATE TABLE DimTreinamentos (
    id_treinamento INT AUTO_INCREMENT PRIMARY KEY,
    nome_treinamento VARCHAR(100) NOT NULL,
    validade_meses INT NOT NULL
);

CREATE TABLE FactRegistros (
    id_registro INT AUTO_INCREMENT PRIMARY KEY,
    id_funcionario INT NOT NULL,
    id_treinamento INT NOT NULL,
    data_realizacao DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Ativo',
    FOREIGN KEY (id_funcionario) REFERENCES DimFuncionarios(id_funcionario) ON DELETE CASCADE,
    FOREIGN KEY (id_treinamento) REFERENCES DimTreinamentos(id_treinamento) ON DELETE CASCADE
);