from config.database import obter_conexao


class Livro:

    @classmethod
    def listar(cls):
        conexao = obter_conexao()
        cursor = None

        try:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("SELECT * FROM livros")
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def buscar_por_id(cls, id_livro):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM livros WHERE id_livro = %s",
                (id_livro,)
            )
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def criar(cls, titulo, autor, editora=None, exemplares=1):
        conexao = obter_conexao()
        cursor = None

        try:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO livros (titulo, autor, editora, exemplares) VALUES (%s, %s, %s, %s)",
                (titulo, autor, editora, exemplares)
            )
            id_gerado = cursor.lastrowid
            conexao.commit()

            return {
                "id_livro": id_gerado,
                "titulo": titulo,
                "autor": autor,
                "editora": editora,
                "exemplares": exemplares
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
    def atualizar(cls, id_livro, titulo, autor, editora=None, exemplares=1):
        conexao = obter_conexao()
        cursor = None

        try:
            cursor = conexao.cursor()
            cursor.execute(
                "UPDATE livros SET titulo = %s, autor = %s, editora = %s, exemplares = %s WHERE id_livro = %s",
                (titulo, autor, editora, exemplares, id_livro)
            )

            if cursor.rowcount == 0:
                return None

            conexao.commit()

            return {
                "id_livro": id_livro,
                "titulo": titulo,
                "autor": autor,
                "editora": editora,
                "exemplares": exemplares
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
    def excluir(cls, id_livro):
        conexao = obter_conexao()
        cursor = None

        try:
            cursor = conexao.cursor()
            cursor.execute(
                "DELETE FROM livros WHERE id_livro = %s",
                (id_livro,)
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


    # Alias para compatibilidade
    deletar = excluir