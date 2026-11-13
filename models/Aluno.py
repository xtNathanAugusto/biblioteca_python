from config.database import obter_conexao


class Aluno:

    @classmethod
    def listar(cls):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("SELECT * FROM alunos")
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def buscar_por_id(cls, id_aluno):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM alunos WHERE id_aluno = %s",
                (id_aluno,)
            )
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def criar(cls, nome, email, curso):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO alunos (nome, email, curso) VALUES (%s, %s, %s)",
                (nome, email, curso)
            )
            id_gerado = cursor.lastrowid
            conexao.commit()
            
            return {
                "id_aluno": id_gerado,
                "nome": nome,
                "email": email,
                "curso": curso
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
    def atualizar(cls, id_aluno, nome, email, curso):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor()
            cursor.execute(
                "UPDATE alunos SET nome = %s, email = %s, curso = %s "
                "WHERE id_aluno = %s",
                (nome, email, curso, id_aluno)
            )
            
            if cursor.rowcount == 0:
                return None
                
            conexao.commit()
            
            return {
                "id_aluno": id_aluno,
                "nome": nome,
                "email": email,
                "curso": curso
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
    def excluir(cls, id_aluno):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor()
            cursor.execute(
                "DELETE FROM alunos WHERE id_aluno = %s",
                (id_aluno,)
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