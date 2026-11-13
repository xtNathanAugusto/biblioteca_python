from flask import request, jsonify
from mysql.connector.errors import IntegrityError
from models.Livro import Livro


def validar_dados(dados):
    if not dados:
        return "Corpo da requisição vazio ou inválido"

    for campo in ("titulo", "autor"):
        valor = dados.get(campo)
        if not valor or not str(valor).strip():
            return f"O campo '{campo}' é obrigatório"

    exemplares = dados.get("exemplares", 1)
    if exemplares is not None:
        try:
            num = int(exemplares)
            if num < 0:
                return "O campo 'exemplares' deve ser maior ou igual a zero"
        except (ValueError, TypeError):
            return "O campo 'exemplares' deve ser um número inteiro"

    return None


class LivroController:

    @staticmethod
    def listar():
        livros = Livro.listar()
        return jsonify(livros), 200

    @staticmethod
    def buscar(id_livro):
        livro = Livro.buscar_por_id(id_livro)
        if not livro:
            return jsonify({"erro": "Livro não encontrado"}), 404
        return jsonify(livro), 200

    @staticmethod
    def criar():
        dados = request.get_json(silent=True)
        erro = validar_dados(dados)
        if erro:
            return jsonify({"erro": erro}), 400

        titulo = dados["titulo"].strip()
        autor = dados["autor"].strip()
        editora = dados.get("editora")
        if editora is not None:
            editora = str(editora).strip()
        exemplares = int(dados.get("exemplares", 1))

        livro = Livro.criar(
            titulo=titulo,
            autor=autor,
            editora=editora,
            exemplares=exemplares
        )

        return jsonify(livro), 201

    @staticmethod
    def atualizar(id_livro):
        dados = request.get_json(silent=True)
        erro = validar_dados(dados)
        if erro:
            return jsonify({"erro": erro}), 400

        titulo = dados["titulo"].strip()
        autor = dados["autor"].strip()
        editora = dados.get("editora")
        if editora is not None:
            editora = str(editora).strip()
        exemplares = int(dados.get("exemplares", 1))

        livro = Livro.atualizar(
            id_livro=id_livro,
            titulo=titulo,
            autor=autor,
            editora=editora,
            exemplares=exemplares
        )

        if not livro:
            return jsonify({"erro": "Livro não encontrado"}), 404

        return jsonify(livro), 200

    @staticmethod
    def excluir(id_livro):
        try:
            excluido = Livro.excluir(id_livro)
        except IntegrityError:
            return jsonify({
                "erro": "Não é possível excluir: O livro possui empréstimos registrados"
            }), 409

        if not excluido:
            return jsonify({"erro": "Livro não encontrado"}), 404

        return jsonify({"mensagem": "Livro excluído com sucesso"}), 200
