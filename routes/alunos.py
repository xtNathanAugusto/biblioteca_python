from flask import Blueprint
from controllers.AlunoController import AlunoController

alunos = Blueprint("alunos", __name__)


@alunos.get("/alunos")
def listar_alunos():
    return AlunoController.listar()


@alunos.get("/alunos/<int:id_aluno>")
def buscar_aluno(id_aluno):
    return AlunoController.buscar(id_aluno)


@alunos.post("/alunos")
def criar_aluno():
    return AlunoController.criar()


@alunos.put("/alunos/<int:id_aluno>")
def atualizar_aluno(id_aluno):
    return AlunoController.atualizar(id_aluno)


@alunos.delete("/alunos/<int:id_aluno>")
def excluir_aluno(id_aluno):
    return AlunoController.excluir(id_aluno)
