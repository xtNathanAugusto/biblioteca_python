CREATE DATABASE IF NOT EXISTS biblioteca
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE biblioteca;

CREATE TABLE alunos (
    id_aluno INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    curso VARCHAR(100) NOT NULL,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bibliotecarios (
    id_bibliotecario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE livros (
    id_livro INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    editora VARCHAR(100),
    autor VARCHAR(100) NOT NULL,
    exemplares INT NOT NULL DEFAULT 1,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE emprestimo (
    id_emprestimo INT AUTO_INCREMENT PRIMARY KEY,
    data DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_aluno INT NOT NULL,
    id_bibliotecario INT NOT NULL,
    id_livro INT NOT NULL,
    data_devolucao DATE NULL,
    CONSTRAINT fk_emprestimo_aluno
        FOREIGN KEY (id_aluno) REFERENCES alunos(id_aluno),
    CONSTRAINT fk_emprestimo_bibliotecario
        FOREIGN KEY (id_bibliotecario) REFERENCES bibliotecarios(id_bibliotecario),
    CONSTRAINT fk_emprestimo_livro
        FOREIGN KEY (id_livro) REFERENCES livros(id_livro)
);