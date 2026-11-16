from flask import Blueprint
from controllers.LivroController import LivroController
from services.AuthService import token_obrigatorio

livros = Blueprint("livros", __name__)


@livros.get("/livros")
@token_obrigatorio
def listar_livros():
    return LivroController.listar()


@livros.get("/livros/<int:id_livro>")
@token_obrigatorio
def buscar_livro(id_livro):
    return LivroController.buscar(id_livro)


@livros.post("/livros")
@token_obrigatorio
def criar_livro():
    return LivroController.criar()


@livros.put("/livros/<int:id_livro>")
@token_obrigatorio
def atualizar_livro(id_livro):
    return LivroController.atualizar(id_livro)


@livros.delete("/livros/<int:id_livro>")
@token_obrigatorio
def excluir_livro(id_livro):
    return LivroController.excluir(id_livro)
