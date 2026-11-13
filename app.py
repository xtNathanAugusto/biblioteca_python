import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from flask import Flask

from routes.alunos import alunos
from routes.bibliotecarios import bibliotecarios
from routes.livros import livros

from views.tela_alunos import TelaAlunos
from views.tela_livros import TelaLivros

# -------------------------------------------------------------
# Configuração da API Flask
# -------------------------------------------------------------
app = Flask(__name__)
PREFIXO = "/biblioteca"

app.register_blueprint(alunos, url_prefix=PREFIXO)
app.register_blueprint(bibliotecarios, url_prefix=PREFIXO)
app.register_blueprint(livros, url_prefix=PREFIXO)


def iniciar_api():
    """Executa a API Flask em segundo plano."""
    # use_reloader=False é obrigatório para não conflitar com a thread do Tkinter
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


# -------------------------------------------------------------
# Interface Gráfica Principal (Menu do Sistema)
# -------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Biblioteca")
        self.geometry("500x380")
        self.resizable(False, False)

        # Referências das janelas filhas para evitar aberturas duplicadas
        self.tela_alunos = None
        self.tela_livros = None

        # Container Central
        container = ttk.Frame(self, padding=25)
        container.pack(fill="both", expand=True)

        # Título e Subtítulo
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
        lbl_subtitulo.pack(pady=(0, 25))

        # Quadro de Ações (Menu)
        menu_frame = ttk.LabelFrame(container, text="Selecione um Módulo", padding=15)
        menu_frame.pack(fill="x", padx=10, pady=5)

        btn_alunos = ttk.Button(
            menu_frame,
            text="📚 Gerenciar Alunos",
            command=self.abrir_tela_alunos
        )
        btn_alunos.pack(fill="x", pady=8, ipady=4)

        btn_livros = ttk.Button(
            menu_frame,
            text="📖 Gerenciar Livros",
            command=self.abrir_tela_livros
        )
        btn_livros.pack(fill="x", pady=8, ipady=4)

        # Rodapé / Status da API
        status_frame = ttk.Frame(container)
        status_frame.pack(side="bottom", fill="x", pady=(20, 0))

        lbl_api_status = ttk.Label(
            status_frame,
            text="● API REST conectada (http://127.0.0.1:5000/biblioteca)",
            font=("Arial", 8),
            foreground="green"
        )
        lbl_api_status.pack(side="left")

    def abrir_tela_alunos(self):
        # Se a janela não existir ou tiver sido fechada, cria uma nova
        if self.tela_alunos is None or not self.tela_alunos.winfo_exists():
            self.tela_alunos = TelaAlunos(self)
        else:
            self.tela_alunos.lift()
            self.tela_alunos.focus_force()

    def abrir_tela_livros(self):
        # Se a janela não existir ou tiver sido fechada, cria uma nova
        if self.tela_livros is None or not self.tela_livros.winfo_exists():
            self.tela_livros = TelaLivros(self)
        else:
            self.tela_livros.lift()
            self.tela_livros.focus_force()


# -------------------------------------------------------------
# Ponto de Entrada da Aplicação
# -------------------------------------------------------------
if __name__ == "__main__":
    # 1. Inicia o servidor Flask em uma thread daemon em segundo plano
    thread_servidor = threading.Thread(target=iniciar_api, daemon=True)
    thread_servidor.start()

    # 2. Inicia o aplicativo desktop Tkinter na thread principal
    app_desktop = App()
    app_desktop.mainloop()
