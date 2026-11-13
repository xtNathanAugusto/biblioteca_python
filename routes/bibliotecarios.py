from flask import Blueprint
from controllers.BibliotecarioController import BibliotecarioController

bibliotecarios = Blueprint("bibliotecarios", __name__)


@bibliotecarios.get("/bibliotecarios")
def listar_bibliotecarios():
    return BibliotecarioController.listar()


@bibliotecarios.get("/bibliotecarios/<int:id_bibliotecarios>")
def buscar_bibliotecario(id_bibliotecarios):
    return BibliotecarioController.buscar(id_bibliotecarios)


@bibliotecarios.post("/bibliotecarios")
def criar_bibliotecario():
    return BibliotecarioController.criar()


@bibliotecarios.put("/bibliotecarios/<int:id_bibliotecarios>")
def atualizar_bibliotecario(id_bibliotecarios):
    return BibliotecarioController.atualizar(id_bibliotecarios)


@bibliotecarios.delete("/bibliotecarios/<int:id_bibliotecarios>")
def excluir_bibliotecario(id_bibliotecarios):
    return BibliotecarioController.excluir(id_bibliotecarios)


@bibliotecarios.post("/bibliotecarios/login")
def login_bibliotecario():
    return BibliotecarioController.login()
