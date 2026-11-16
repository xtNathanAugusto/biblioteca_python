from flask import Blueprint
from controllers.EmprestimoController import EmprestimoController
from services.AuthService import token_obrigatorio

emprestimos = Blueprint("emprestimos", __name__)


@emprestimos.get("/emprestimos")
@emprestimos.get("/emprestimo")
@token_obrigatorio
def listar_emprestimos():
    return EmprestimoController.listar()


@emprestimos.get("/emprestimos/<int:id_emprestimo>")
@emprestimos.get("/emprestimo/<int:id_emprestimo>")
@token_obrigatorio
def buscar_emprestimo(id_emprestimo):
    return EmprestimoController.buscar(id_emprestimo)


@emprestimos.post("/emprestimos")
@emprestimos.post("/emprestimo")
@token_obrigatorio
def criar_emprestimo():
    return EmprestimoController.criar()


@emprestimos.put("/emprestimos/<int:id_emprestimo>")
@emprestimos.put("/emprestimo/<int:id_emprestimo>")
@token_obrigatorio
def atualizar_emprestimo(id_emprestimo):
    return EmprestimoController.atualizar(id_emprestimo)


@emprestimos.patch("/emprestimos/<int:id_emprestimo>/devolver")
@emprestimos.put("/emprestimos/<int:id_emprestimo>/devolver")
@emprestimos.patch("/emprestimo/<int:id_emprestimo>/devolver")
@emprestimos.put("/emprestimo/<int:id_emprestimo>/devolver")
@token_obrigatorio
def devolver_emprestimo(id_emprestimo):
    return EmprestimoController.devolver(id_emprestimo)


@emprestimos.delete("/emprestimos/<int:id_emprestimo>")
@emprestimos.delete("/emprestimo/<int:id_emprestimo>")
@token_obrigatorio
def excluir_emprestimo(id_emprestimo):
    return EmprestimoController.excluir(id_emprestimo)
