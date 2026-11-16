import sys
import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services import api_client as api


class TelaCadastroPrimeiroAcesso(tk.Toplevel):
    """Janela auxiliar para cadastrar um bibliotecário diretamente na tela de login."""

    def __init__(self, master, ao_cadastrar=None):
        super().__init__(master)
        self.ao_cadastrar = ao_cadastrar

        self.title("Cadastrar Bibliotecário")
        self.geometry("420x270")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        container = ttk.Frame(self, padding=15)
        container.pack(fill="both", expand=True)

        form = ttk.LabelFrame(container, text="Novo Bibliotecário", padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Nome:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.nome_entry = ttk.Entry(form, width=36)
        self.nome_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Email:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.email_entry = ttk.Entry(form, width=36)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Senha:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.senha_entry = ttk.Entry(form, width=36, show="*")
        self.senha_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form, text="Confirmar:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.confirmar_entry = ttk.Entry(form, width=36, show="*")
        self.confirmar_entry.grid(row=3, column=1, padx=5, pady=5)

        botoes = ttk.Frame(container)
        botoes.pack(fill="x", pady=(12, 0))

        self.btn_salvar = ttk.Button(botoes, text="Cadastrar", command=self.cadastrar)
        self.btn_salvar.pack(side="right", padx=(5, 0))

        self.btn_cancelar = ttk.Button(botoes, text="Cancelar", command=self.destroy)
        self.btn_cancelar.pack(side="right")

        self.nome_entry.focus_set()

    def cadastrar(self):
        nome = self.nome_entry.get().strip()
        email = self.email_entry.get().strip()
        senha = self.senha_entry.get().strip()
        confirmar = self.confirmar_entry.get().strip()

        if not nome or not email or not senha:
            messagebox.showwarning("Aviso", "Preencha Nome, Email e Senha!", parent=self)
            return

        if senha != confirmar:
            messagebox.showwarning("Aviso", "As senhas não coincidem!", parent=self)
            return

        self.btn_salvar.config(state="disabled")
        self.config(cursor="wait")

        def tarefa():
            try:
                api.criar("bibliotecarios", {"nome": nome, "email": email, "senha": senha})
                self.after(0, lambda: self._sucesso(email))
            except Exception as e:
                self.after(0, lambda err=str(e): messagebox.showerror("Erro", err, parent=self))
                self.after(0, self._reativar)

        threading.Thread(target=tarefa, daemon=True).start()

    def _reativar(self):
        if self.winfo_exists():
            self.btn_salvar.config(state="normal")
            self.config(cursor="")

    def _sucesso(self, email):
        messagebox.showinfo("Sucesso", "Bibliotecário cadastrado! Agora faça login.", parent=self)
        if self.ao_cadastrar:
            self.ao_cadastrar(email)
        self.destroy()


class TelaLogin(tk.Toplevel):
    def __init__(self, master=None, ao_logar=None, ao_fechar=None):
        super().__init__(master)
        self.ao_logar = ao_logar
        self.ao_fechar = ao_fechar

        self.title("Login - Sistema de Biblioteca")
        self.geometry("430x310")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._ao_fechar_janela)

        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text="Acesso do Bibliotecário",
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 4))

        ttk.Label(
            container,
            text="Informe suas credenciais para acessar o sistema",
            font=("Arial", 9)
        ).pack(pady=(0, 15))

        form = ttk.LabelFrame(container, text="Credenciais", padding=12)
        form.pack(fill="x")

        ttk.Label(form, text="Email:").grid(row=0, column=0, sticky="w", padx=5, pady=6)
        self.email_entry = ttk.Entry(form, width=36)
        self.email_entry.grid(row=0, column=1, padx=5, pady=6)

        ttk.Label(form, text="Senha:").grid(row=1, column=0, sticky="w", padx=5, pady=6)
        self.senha_entry = ttk.Entry(form, width=36, show="*")
        self.senha_entry.grid(row=1, column=1, padx=5, pady=6)

        self.mostrar_senha_var = tk.BooleanVar(value=False)
        chk_senha = ttk.Checkbutton(
            form,
            text="Mostrar senha",
            variable=self.mostrar_senha_var,
            command=self._alternar_senha
        )
        chk_senha.grid(row=2, column=1, sticky="w", padx=5, pady=(0, 4))

        botoes = ttk.Frame(container)
        botoes.pack(fill="x", pady=(14, 0))

        self.btn_entrar = ttk.Button(botoes, text="Entrar", command=self.entrar)
        self.btn_entrar.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 5))

        self.btn_cadastrar = ttk.Button(
            botoes,
            text="Novo Bibliotecário",
            command=self.abrir_cadastro
        )
        self.btn_cadastrar.pack(side="left", ipady=4)

        status_frame = ttk.Frame(container)
        status_frame.pack(side="bottom", fill="x", pady=(12, 0))

        self.lbl_status = ttk.Label(status_frame, text="", foreground="blue")
        self.lbl_status.pack(side="left")

        self.progress = ttk.Progressbar(status_frame, mode="indeterminate", length=100)

        self.email_entry.bind("<Return>", lambda _e: self.senha_entry.focus_set())
        self.senha_entry.bind("<Return>", lambda _e: self.entrar())
        self.email_entry.focus_set()

    def _alternar_senha(self):
        self.senha_entry.config(show="" if self.mostrar_senha_var.get() else "*")

    def _ao_fechar_janela(self):
        if self.ao_fechar:
            self.ao_fechar()
        else:
            self.destroy()

    def iniciar_loading(self, mensagem="Autenticando..."):
        self.lbl_status.config(text=mensagem)
        self.progress.pack(side="right")
        self.progress.start(10)
        self.config(cursor="wait")
        self.btn_entrar.config(state="disabled")
        self.btn_cadastrar.config(state="disabled")

    def parar_loading(self):
        if not self.winfo_exists():
            return
        self.lbl_status.config(text="")
        self.progress.stop()
        self.progress.pack_forget()
        self.config(cursor="")
        self.btn_entrar.config(state="normal")
        self.btn_cadastrar.config(state="normal")

    def abrir_cadastro(self):
        TelaCadastroPrimeiroAcesso(self, ao_cadastrar=self._preencher_email)

    def _preencher_email(self, email):
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, email)
        self.senha_entry.delete(0, tk.END)
        self.senha_entry.focus_set()

    def entrar(self):
        email = self.email_entry.get().strip()
        senha = self.senha_entry.get().strip()

        if not email or not senha:
            messagebox.showwarning("Aviso", "Informe email e senha!", parent=self)
            return

        self.iniciar_loading("Autenticando...")

        def tarefa():
            try:
                resposta = api.login(email, senha)
                self.after(0, lambda: self._login_sucesso(resposta))
            except Exception as e:
                self.after(0, lambda err=str(e): messagebox.showerror("Erro de Login", err, parent=self))
                self.after(0, self.parar_loading)

        threading.Thread(target=tarefa, daemon=True).start()

    def _login_sucesso(self, resposta):
        self.parar_loading()
        if self.ao_logar:
            self.ao_logar(resposta)
        self.destroy()


if __name__ == "__main__":
    import time
    import requests

    try:
        requests.get("http://127.0.0.1:5000/biblioteca/bibliotecarios", timeout=1)
    except Exception:
        from app import iniciar_api
        threading.Thread(target=iniciar_api, daemon=True).start()
        time.sleep(1)

    root = tk.Tk()
    root.withdraw()

    def on_login(resp):
        bib = resp.get("bibliotecario", {})
        messagebox.showinfo("Bem-vindo", f"Logado como: {bib.get('nome')} ({bib.get('email')})")
        root.destroy()

    TelaLogin(root, ao_logar=on_login, ao_fechar=root.destroy)
    root.mainloop()
