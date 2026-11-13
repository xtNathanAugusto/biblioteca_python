from flask import Blueprint
from controllers.LivroController import LivroController

livros = Blueprint("livros", __name__)


@livros.get("/livros")
def listar_livros():
    return LivroController.listar()


@livros.get("/livros/<int:id_livro>")
def buscar_livro(id_livro):
    return LivroController.buscar(id_livro)


@livros.post("/livros")
def criar_livro():
    return LivroController.criar()


@livros.put("/livros/<int:id_livro>")
def atualizar_livro(id_livro):
    return LivroController.atualizar(id_livro)


@livros.delete("/livros/<int:id_livro>")
def excluir_livro(id_livro):
    return LivroController.excluir(id_livro)
