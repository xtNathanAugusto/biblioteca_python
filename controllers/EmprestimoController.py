from datetime import datetime
from flask import request, jsonify
from mysql.connector.errors import IntegrityError
from models.Emprestimo import Emprestimo


def normalizar_data(valor):
    """Aceita YYYY-MM-DD ou DD/MM/YYYY e retorna YYYY-MM-DD (ou None se vazio)."""
    if valor is None:
        return None
    texto = str(valor).strip()
    if not texto:
        return None

    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, formato).strftime("%Y-%m-%d")
        except ValueError:
            continue

    raise ValueError("Data de devolução inválida. Use o formato AAAA-MM-DD ou DD/MM/AAAA")


def validar_dados(dados):
    if not dados:
        return "Corpo da requisição vazio ou inválido"

    for campo in ("id_aluno", "id_bibliotecario", "id_livro"):
        valor = dados.get(campo)
        if valor is None or str(valor).strip() == "":
            return f"O campo '{campo}' é obrigatório"
        try:
            if int(valor) <= 0:
                return f"O campo '{campo}' deve ser um ID válido"
        except (ValueError, TypeError):
            return f"O campo '{campo}' deve ser um número inteiro"

    try:
        normalizar_data(dados.get("data_devolucao"))
    except ValueError as e:
        return str(e)

    return None


class EmprestimoController:

    @staticmethod
    def listar():
        emprestimos = Emprestimo.listar()
        return jsonify(emprestimos), 200

    @staticmethod
    def buscar(id_emprestimo):
        emprestimo = Emprestimo.buscar_por_id(id_emprestimo)
        if not emprestimo:
            return jsonify({"erro": "Empréstimo não encontrado"}), 404
        return jsonify(emprestimo), 200

    @staticmethod
    def criar():
        dados = request.get_json(silent=True)
        erro = validar_dados(dados)
        if erro:
            return jsonify({"erro": erro}), 400

        id_aluno = int(dados["id_aluno"])
        id_bibliotecario = int(dados["id_bibliotecario"])
        id_livro = int(dados["id_livro"])
        data_devolucao = normalizar_data(dados.get("data_devolucao"))

        try:
            emprestimo = Emprestimo.criar(
                id_aluno=id_aluno,
                id_bibliotecario=id_bibliotecario,
                id_livro=id_livro,
                data_devolucao=data_devolucao
            )
        except IntegrityError:
            return jsonify({
                "erro": "Aluno, Bibliotecário ou Livro informado não existe"
            }), 400

        return jsonify(emprestimo), 201

    @staticmethod
    def atualizar(id_emprestimo):
        dados = request.get_json(silent=True)
        erro = validar_dados(dados)
        if erro:
            return jsonify({"erro": erro}), 400

        id_aluno = int(dados["id_aluno"])
        id_bibliotecario = int(dados["id_bibliotecario"])
        id_livro = int(dados["id_livro"])
        data_devolucao = normalizar_data(dados.get("data_devolucao"))

        try:
            emprestimo = Emprestimo.atualizar(
                id_emprestimo=id_emprestimo,
                id_aluno=id_aluno,
                id_bibliotecario=id_bibliotecario,
                id_livro=id_livro,
                data_devolucao=data_devolucao
            )
        except IntegrityError:
            return jsonify({
                "erro": "Aluno, Bibliotecário ou Livro informado não existe"
            }), 400

        if not emprestimo:
            return jsonify({"erro": "Empréstimo não encontrado"}), 404

        return jsonify(emprestimo), 200

    @staticmethod
    def devolver(id_emprestimo):
        dados = request.get_json(silent=True) or {}
        try:
            data_devolucao = normalizar_data(dados.get("data_devolucao"))
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

        emprestimo = Emprestimo.registrar_devolucao(id_emprestimo, data_devolucao)
        if not emprestimo:
            return jsonify({"erro": "Empréstimo não encontrado"}), 404

        return jsonify(emprestimo), 200

    @staticmethod
    def excluir(id_emprestimo):
        excluido = Emprestimo.excluir(id_emprestimo)
        if not excluido:
            return jsonify({"erro": "Empréstimo não encontrado"}), 404

        return jsonify({"mensagem": "Empréstimo excluído com sucesso"}), 200
