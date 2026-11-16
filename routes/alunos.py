from flask import Blueprint
from controllers.AlunoController import AlunoController
from services.AuthService import token_obrigatorio

alunos = Blueprint("alunos", __name__)


@alunos.get("/alunos")
@token_obrigatorio
def listar_alunos():
    return AlunoController.listar()


@alunos.get("/alunos/<int:id_aluno>")
@token_obrigatorio
def buscar_aluno(id_aluno):
    return AlunoController.buscar(id_aluno)


@alunos.post("/alunos")
@token_obrigatorio
def criar_aluno():
    return AlunoController.criar()


@alunos.put("/alunos/<int:id_aluno>")
@token_obrigatorio
def atualizar_aluno(id_aluno):
    return AlunoController.atualizar(id_aluno)


@alunos.delete("/alunos/<int:id_aluno>")
@token_obrigatorio
def excluir_aluno(id_aluno):
    return AlunoController.excluir(id_aluno)
