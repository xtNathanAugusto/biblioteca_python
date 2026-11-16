from datetime import date, datetime
from config.database import obter_conexao


def _formatar_registro(registro):
    if not registro:
        return registro
    if isinstance(registro.get("data"), (datetime, date)):
        registro["data"] = registro["data"].strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(registro.get("data_devolucao"), (datetime, date)):
        registro["data_devolucao"] = registro["data_devolucao"].strftime("%Y-%m-%d")
    return registro


class Emprestimo:

    @classmethod
    def listar(cls):
        conexao = obter_conexao()
        cursor = None

        try:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    e.id_emprestimo,
                    e.data,
                    e.id_aluno,
                    a.nome AS nome_aluno,
                    e.id_bibliotecario,
                    b.nome AS nome_bibliotecario,
                    e.id_livro,
                    l.titulo AS titulo_livro,
                    e.data_devolucao
                FROM emprestimo e
                INNER JOIN alunos a ON e.id_aluno = a.id_aluno
                INNER JOIN bibliotecarios b ON e.id_bibliotecario = b.id_bibliotecario
                INNER JOIN livros l ON e.id_livro = l.id_livro
                ORDER BY e.id_emprestimo DESC
                """
            )
            registros = cursor.fetchall()
            return [_formatar_registro(r) for r in registros]
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def buscar_por_id(cls, id_emprestimo):
        conexao = obter_conexao()
        cursor = None

        try:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    e.id_emprestimo,
                    e.data,
                    e.id_aluno,
                    a.nome AS nome_aluno,
                    e.id_bibliotecario,
                    b.nome AS nome_bibliotecario,
                    e.id_livro,
                    l.titulo AS titulo_livro,
                    e.data_devolucao
                FROM emprestimo e
                INNER JOIN alunos a ON e.id_aluno = a.id_aluno
                INNER JOIN bibliotecarios b ON e.id_bibliotecario = b.id_bibliotecario
                INNER JOIN livros l ON e.id_livro = l.id_livro
                WHERE e.id_emprestimo = %s
                """,
                (id_emprestimo,)
            )
            return _formatar_registro(cursor.fetchone())
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def criar(cls, id_aluno, id_bibliotecario, id_livro, data_devolucao=None):
        conexao = obter_conexao()
        cursor = None

        try:
            cursor = conexao.cursor()
            cursor.execute(
                """
                INSERT INTO emprestimo (id_aluno, id_bibliotecario, id_livro, data_devolucao)
                VALUES (%s, %s, %s, %s)
                """,
                (id_aluno, id_bibliotecario, id_livro, data_devolucao)
            )
            id_gerado = cursor.lastrowid
            conexao.commit()

            return {
                "id_emprestimo": id_gerado,
                "id_aluno": id_aluno,
                "id_bibliotecario": id_bibliotecario,
                "id_livro": id_livro,
                "data_devolucao": data_devolucao
            }
        except Exception:
            if conexao:
                conexao.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def atualizar(cls, id_emprestimo, id_aluno, id_bibliotecario, id_livro, data_devolucao=None):
        conexao = obter_conexao()
        cursor = None

        try:
            cursor = conexao.cursor()
            cursor.execute(
                """
                UPDATE emprestimo
                SET id_aluno = %s, id_bibliotecario = %s, id_livro = %s, data_devolucao = %s
                WHERE id_emprestimo = %s
                """,
                (id_aluno, id_bibliotecario, id_livro, data_devolucao, id_emprestimo)
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    "SELECT id_emprestimo FROM emprestimo WHERE id_emprestimo = %s",
                    (id_emprestimo,)
                )
                if not cursor.fetchone():
                    return None

            conexao.commit()

            return {
                "id_emprestimo": id_emprestimo,
                "id_aluno": id_aluno,
                "id_bibliotecario": id_bibliotecario,
                "id_livro": id_livro,
                "data_devolucao": data_devolucao
            }
        except Exception:
            if conexao:
                conexao.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def registrar_devolucao(cls, id_emprestimo, data_devolucao=None):
        if not data_devolucao:
            data_devolucao = date.today().strftime("%Y-%m-%d")

        conexao = obter_conexao()
        cursor = None

        try:
            cursor = conexao.cursor()
            cursor.execute(
                "UPDATE emprestimo SET data_devolucao = %s WHERE id_emprestimo = %s",
                (data_devolucao, id_emprestimo)
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    "SELECT id_emprestimo FROM emprestimo WHERE id_emprestimo = %s",
                    (id_emprestimo,)
                )
                if not cursor.fetchone():
                    return None

            conexao.commit()
            return {
                "id_emprestimo": id_emprestimo,
                "data_devolucao": data_devolucao
            }
        except Exception:
            if conexao:
                conexao.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def excluir(cls, id_emprestimo):
        conexao = obter_conexao()
        cursor = None

        try:
            cursor = conexao.cursor()
            cursor.execute(
                "DELETE FROM emprestimo WHERE id_emprestimo = %s",
                (id_emprestimo,)
            )
            afetados = cursor.rowcount
            conexao.commit()
            return afetados > 0
        except Exception:
            if conexao:
                conexao.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    # Alias para compatibilidade
    deletar = excluir
