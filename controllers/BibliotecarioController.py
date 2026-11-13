from flask import request, jsonify
from mysql.connector.errors import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from services.AuthService import gerar_token
from models.Bibliotecario import Bibliotecario


def validar_dados(dados):
    if not dados:
        return "Corpo da requisição vazio ou inválido"

    for campo in ("nome", "email", "senha"):
        valor = dados.get(campo)
        if not valor or not str(valor).strip():
            return f"O campo '{campo}' é obrigatório"

    return None


class BibliotecarioController:
    @staticmethod
    def listar():
        bibliotecarios = Bibliotecario.listar()
        return jsonify(bibliotecarios), 200

    @staticmethod
    def buscar(id_bibliotecario):
        bibliotecario = Bibliotecario.buscar_por_id(id_bibliotecario)
        if not bibliotecario:
            return jsonify({"erro": "Bibliotecário não encontrado"}), 404
        return jsonify(bibliotecario), 200

    @staticmethod
    def criar():
        dados = request.get_json(silent=True)
        erro = validar_dados(dados)
        if erro:
            return jsonify({"erro": erro}), 400

        senha_hash = generate_password_hash(dados["senha"].strip())

        try:
            bibliotecario = Bibliotecario.criar(
                dados["nome"].strip(),
                dados["email"].strip(),
                senha_hash
            )
        except IntegrityError:
            return jsonify({"erro": "Email já cadastrado"}), 409

        return jsonify(bibliotecario), 201

    @staticmethod
    def atualizar(id_bibliotecario):
        dados = request.get_json(silent=True)
        
        if not dados or not dados.get("nome") or not dados.get("email"):
            return jsonify({"erro": "Nome e Email são obrigatórios"}), 400

        try:
            bibliotecario = Bibliotecario.atualizar(
                id_bibliotecario,
                dados["nome"].strip(),
                dados["email"].strip()
            )
        except IntegrityError:
            return jsonify({"erro": "Email já cadastrado"}), 409

        if not bibliotecario:
            return jsonify({"erro": "Bibliotecário não encontrado"}), 404

        return jsonify(bibliotecario), 200

    @staticmethod
    def excluir(id_bibliotecario):
        try:
            excluido = Bibliotecario.excluir(id_bibliotecario)
        except IntegrityError:
            return jsonify({
                "erro": "Não é possível excluir: O Bibliotecário possui registros vinculados"
            }), 409

        if not excluido:
            return jsonify({"erro": "Bibliotecário não encontrado"}), 404

        return jsonify({"mensagem": "Bibliotecário excluído com sucesso"}), 200

    @staticmethod
    def login():
        dados = request.get_json(silent=True)
        if not dados or not dados.get("email") or not dados.get("senha"):
            return jsonify({"erro": "Email e Senha são obrigatórios"}), 400

        bibliotecario = Bibliotecario.buscar_por_email(dados["email"].strip())

        if not bibliotecario or not check_password_hash(bibliotecario["senha"], dados["senha"].strip()):
            return jsonify({"erro": "Email ou Senha inválidos!"}), 401

        bibliotecario.pop("senha", None)

        token = gerar_token(bibliotecario["id_bibliotecario"], bibliotecario["email"])
        return jsonify({
            "token": token,
            "bibliotecario": bibliotecario
        }), 200