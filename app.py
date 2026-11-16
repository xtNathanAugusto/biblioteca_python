import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from flask import Flask

from routes.alunos import alunos
from routes.bibliotecarios import bibliotecarios
from routes.livros import livros
from routes.emprestimos import emprestimos

from views.tela_alunos import TelaAlunos
from views.tela_livros import TelaLivros
from views.tela_bibliotecarios import TelaBibliotecarios
from views.tela_emprestimos import TelaEmprestimos
from views.tela_login import TelaLogin
from services import api_client as api

app = Flask(__name__)
PREFIXO = "/biblioteca"

app.register_blueprint(alunos, url_prefix=PREFIXO)
app.register_blueprint(bibliotecarios, url_prefix=PREFIXO)
app.register_blueprint(livros, url_prefix=PREFIXO)
app.register_blueprint(emprestimos, url_prefix=PREFIXO)


def iniciar_api():
    """Executa a API Flask em segundo plano."""
    # use_reloader=False é obrigatório para não conflitar com a thread do Tkinter
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Biblioteca")
        self.geometry("500x520")
        self.resizable(False, False)

        self.tela_alunos = None
        self.tela_livros = None
        self.tela_bibliotecarios = None
        self.tela_emprestimos = None
        self.tela_login = None

        container = ttk.Frame(self, padding=25)
        container.pack(fill="both", expand=True)

        lbl_titulo = ttk.Label(
            container,
            text="Sistema de Gerenciamento",
            font=("Arial", 16, "bold")
        )
        lbl_titulo.pack(pady=(5, 2))

        lbl_subtitulo = ttk.Label(
            container,
            text="Biblioteca Universitária",
            font=("Arial", 11)
        )
        lbl_subtitulo.pack(pady=(0, 8))

        self.lbl_usuario = ttk.Label(
            container,
            text="",
            font=("Arial", 9, "italic"),
            foreground="#1f538d"
        )
        self.lbl_usuario.pack(pady=(0, 15))

        menu_frame = ttk.LabelFrame(container, text="Selecione um Módulo", padding=15)
        menu_frame.pack(fill="x", padx=10, pady=5)

        btn_alunos = ttk.Button(
            menu_frame,
            text="📚 Gerenciar Alunos",
            command=self.abrir_tela_alunos
        )
        btn_alunos.pack(fill="x", pady=6, ipady=4)

        btn_livros = ttk.Button(
            menu_frame,
            text="📖 Gerenciar Livros",
            command=self.abrir_tela_livros
        )
        btn_livros.pack(fill="x", pady=6, ipady=4)

        btn_bibliotecarios = ttk.Button(
            menu_frame,
            text="👤 Gerenciar Bibliotecários",
            command=self.abrir_tela_bibliotecarios
        )
        btn_bibliotecarios.pack(fill="x", pady=6, ipady=4)

        btn_emprestimos = ttk.Button(
            menu_frame,
            text="📋 Gerenciar Empréstimos",
            command=self.abrir_tela_emprestimos
        )
        btn_emprestimos.pack(fill="x", pady=6, ipady=4)

        btn_logout = ttk.Button(
            container,
            text="🚪 Sair (Trocar Bibliotecário)",
            command=self.fazer_logout
        )
        btn_logout.pack(fill="x", padx=10, pady=(12, 0), ipady=3)

        status_frame = ttk.Frame(container)
        status_frame.pack(side="bottom", fill="x", pady=(15, 0))

        lbl_api_status = ttk.Label(
            status_frame,
            text="● API REST conectada (http://127.0.0.1:5000/biblioteca)",
            font=("Arial", 8),
            foreground="green"
        )
        lbl_api_status.pack(side="left")

        self.withdraw()
        self.after(150, self.abrir_tela_login)

    def abrir_tela_login(self):
        if self.tela_login is None or not self.tela_login.winfo_exists():
            self.tela_login = TelaLogin(
                self,
                ao_logar=self._ao_logar,
                ao_fechar=self.destroy
            )
        else:
            self.tela_login.lift()
            self.tela_login.focus_force()

    def _ao_logar(self, resposta):
        bibliotecario = (resposta or {}).get("bibliotecario") or {}
        nome = bibliotecario.get("nome", "Bibliotecário")
        email = bibliotecario.get("email", "")
        texto = f"Logado como: {nome} ({email})" if email else f"Logado como: {nome}"
        self.lbl_usuario.config(text=texto)
        self.deiconify()
        self.lift()
        self.focus_force()

    def fazer_logout(self):
        for janela in (
            self.tela_alunos,
            self.tela_livros,
            self.tela_bibliotecarios,
            self.tela_emprestimos,
        ):
            if janela is not None and janela.winfo_exists():
                janela.destroy()

        api.logout()
        self.lbl_usuario.config(text="")
        self.withdraw()
        self.abrir_tela_login()

    def abrir_tela_alunos(self):
        if self.tela_alunos is None or not self.tela_alunos.winfo_exists():
            self.tela_alunos = TelaAlunos(self)
        else:
            self.tela_alunos.lift()
            self.tela_alunos.focus_force()

    def abrir_tela_livros(self):
        if self.tela_livros is None or not self.tela_livros.winfo_exists():
            self.tela_livros = TelaLivros(self)
        else:
            self.tela_livros.lift()
            self.tela_livros.focus_force()

    def abrir_tela_bibliotecarios(self):
        if self.tela_bibliotecarios is None or not self.tela_bibliotecarios.winfo_exists():
            self.tela_bibliotecarios = TelaBibliotecarios(self)
        else:
            self.tela_bibliotecarios.lift()
            self.tela_bibliotecarios.focus_force()

    def abrir_tela_emprestimos(self):
        if self.tela_emprestimos is None or not self.tela_emprestimos.winfo_exists():
            self.tela_emprestimos = TelaEmprestimos(self)
        else:
            self.tela_emprestimos.lift()
            self.tela_emprestimos.focus_force()


if __name__ == "__main__":
    thread_servidor = threading.Thread(target=iniciar_api, daemon=True)
    thread_servidor.start()

    app_desktop = App()
    app_desktop.mainloop()
