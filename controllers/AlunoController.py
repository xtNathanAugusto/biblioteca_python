from flask import request, jsonify
from mysql.connector.errors import IntegrityError
from models.Aluno import Aluno


def validar_dados(dados):

    if not dados:
        return "Corpo da requisição vazio ou inválido"

    for campo in ("nome", "email", "curso"):
        valor = dados.get(campo)
        if not valor or not str(valor).strip():
            return f"O campo '{campo}' é obrigatório"
    
    return None


class AlunoController:
    @staticmethod
    def listar():
        alunos = Aluno.listar()
        return jsonify(alunos), 200

    @staticmethod
    def buscar(id_aluno):
        aluno = Aluno.buscar_por_id(id_aluno)
        if not aluno:
            return jsonify({"erro": "Aluno não encontrado"}), 404
        return jsonify(aluno), 200

    @staticmethod
    def criar():
        dados = request.get_json(silent=True)
        erro = validar_dados(dados)
        if erro:
            return jsonify({"erro": erro}), 400

        try:
            aluno = Aluno.criar(
                dados["nome"].strip(),
                dados["email"].strip(),
                dados["curso"].strip()
            )
        except IntegrityError:
            return jsonify({"erro": "Email já cadastrado"}), 409

        return jsonify(aluno), 201

    @staticmethod
    def atualizar(id_aluno):
        dados = request.get_json(silent=True)
        erro = validar_dados(dados)
        if erro:
            return jsonify({"erro": erro}), 400

        try:
            aluno = Aluno.atualizar(
                id_aluno,
                dados["nome"].strip(),
                dados["email"].strip(),
                dados["curso"].strip()
            )
        except IntegrityError:
            return jsonify({"erro": "Email já cadastrado"}), 409

        if not aluno:
            return jsonify({"erro": "Aluno não encontrado"}), 404

        return jsonify(aluno), 200

    @staticmethod
    def excluir(id_aluno):
        try:
            excluido = Aluno.excluir(id_aluno)
        except IntegrityError:

            return jsonify({
                "erro": "Não é possível excluir: O aluno possui empréstimos registrados"
            }), 409

        if not excluido:
            return jsonify({"erro": "Aluno não encontrado"}), 404

        return jsonify({"mensagem": "Aluno excluído com sucesso"}), 200