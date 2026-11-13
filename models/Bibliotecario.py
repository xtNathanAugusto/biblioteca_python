from config.database import obter_conexao


class Bibliotecario:

    @classmethod
    def listar(cls):
        conexao = obter_conexao()
        cursor = None

        try:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("SELECT * FROM bibliotecarios")
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def buscar_por_id(cls, id_bibliotecario):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM bibliotecarios WHERE id_bibliotecario = %s",
                (id_bibliotecario,)
            )
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def buscar_por_email(cls, email):
        conexao = obter_conexao()
        cursor = None

        try:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM bibliotecarios WHERE email = %s",
                (email,)
            )
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def criar(cls, nome, email, senha_hash):
        conexao = obter_conexao()
        cursor = None

        try:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO bibliotecarios (nome, email, senha) VALUES (%s, %s, %s)",
                (nome, email, senha_hash)
            )
            id_gerado = cursor.lastrowid
            conexao.commit()

            return {
                "id_bibliotecario": id_gerado,
                "nome": nome,
                "email": email
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
    def atualizar(cls, id_bibliotecario, nome, email):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor()
            cursor.execute(
                "UPDATE bibliotecarios SET nome = %s, email = %s WHERE id_bibliotecario = %s",
                (nome, email, id_bibliotecario)
            )

            if cursor.rowcount == 0:
                return None

            conexao.commit()

            return {
                "id_bibliotecario": id_bibliotecario,
                "nome": nome,
                "email": email,
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
    def excluir(cls, id_bibliotecario):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor()
            cursor.execute(
                "DELETE FROM bibliotecarios WHERE id_bibliotecario = %s",
                (id_bibliotecario,)
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