import sys
import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services import api_client as api


class TelaBibliotecarios(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)

        self.title("Cadastro de Bibliotecários")
        self.geometry("700x560")
        self.resizable(False, False)
        self.bibliotecario_id = None

        form = ttk.LabelFrame(self, text="Dados do Bibliotecário", padding=10)
        form.pack(padx=10, pady=10, fill="x")

        ttk.Label(form, text="Nome:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.nome_entry = ttk.Entry(form, width=50)
        self.nome_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form, text="Email:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.email_entry = ttk.Entry(form, width=50)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form, text="Senha:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.senha_entry = ttk.Entry(form, width=50, show="*")
        self.senha_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        botoes = ttk.Frame(self)
        botoes.pack(fill="x", padx=10, pady=5)

        self.btn_cadastrar = ttk.Button(botoes, text="Cadastrar", command=self.inserir)
        self.btn_cadastrar.pack(side="left", padx=5)

        self.btn_atualizar = ttk.Button(botoes, text="Atualizar", command=self.atualizar)
        self.btn_atualizar.pack(side="left", padx=5)

        self.btn_excluir = ttk.Button(botoes, text="Excluir", command=self.deletar)
        self.btn_excluir.pack(side="left", padx=5)

        self.btn_limpar = ttk.Button(botoes, text="Limpar", command=self.limpar)
        self.btn_limpar.pack(side="left", padx=5)

        self.btn_recarregar = ttk.Button(botoes, text="Recarregar", command=self.listar)
        self.btn_recarregar.pack(side="left", padx=5)

        self.botoes = [
            self.btn_cadastrar,
            self.btn_atualizar,
            self.btn_excluir,
            self.btn_limpar,
            self.btn_recarregar
        ]

        status_frame = ttk.Frame(self)
        status_frame.pack(side="bottom", fill="x", padx=10, pady=5)

        self.lbl_status = ttk.Label(status_frame, text="", foreground="blue")
        self.lbl_status.pack(side="left")

        self.progress = ttk.Progressbar(status_frame, mode="indeterminate", length=120)

        tabela_frame = ttk.LabelFrame(self, text="Lista de Bibliotecários", padding=10)
        tabela_frame.pack(padx=10, pady=5, fill="both", expand=True)

        colunas = ("id", "nome", "email")
        self.tree = ttk.Treeview(tabela_frame, columns=colunas, show="headings", selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("email", text="Email")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nome", width=280)
        self.tree.column("email", width=300)

        scrollbar = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.ao_selecionar)

        self.listar()

    def iniciar_loading(self, mensagem="Carregando..."):
        self.lbl_status.config(text=mensagem)
        self.progress.pack(side="right")
        self.progress.start(10)
        self.config(cursor="wait")
        for b in self.botoes:
            b.config(state="disabled")

    def parar_loading(self):
        self.lbl_status.config(text="")
        self.progress.stop()
        self.progress.pack_forget()
        self.config(cursor="")
        for b in self.botoes:
            b.config(state="normal")

    def limpar(self):
        self.bibliotecario_id = None
        self.nome_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.senha_entry.delete(0, tk.END)
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def ao_selecionar(self, event):
        selecionado = self.tree.selection()
        if selecionado:
            item = self.tree.item(selecionado[0])
            valores = item["values"]
            if valores:
                self.bibliotecario_id = valores[0]
                self.nome_entry.delete(0, tk.END)
                self.nome_entry.insert(0, valores[1])
                self.email_entry.delete(0, tk.END)
                self.email_entry.insert(0, valores[2])
                self.senha_entry.delete(0, tk.END)

    def listar(self):
        self.iniciar_loading("Carregando bibliotecários...")

        def tarefa():
            try:
                bibliotecarios = api.listar("bibliotecarios")
                self.after(0, self._atualizar_tabela, bibliotecarios)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro", str(e)))
            finally:
                self.after(0, self.parar_loading)

        threading.Thread(target=tarefa, daemon=True).start()

    def _atualizar_tabela(self, bibliotecarios):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if bibliotecarios:
            for bib in bibliotecarios:
                self.tree.insert("", tk.END, values=(
                    bib.get("id_bibliotecario"),
                    bib.get("nome"),
                    bib.get("email")
                ))

    def inserir(self):
        nome = self.nome_entry.get().strip()
        email = self.email_entry.get().strip()
        senha = self.senha_entry.get().strip()

        if not nome or not email or not senha:
            messagebox.showwarning("Aviso", "Preencha Nome, Email e Senha!")
            return

        self.iniciar_loading("Cadastrando bibliotecário...")

        def tarefa():
            try:
                api.criar("bibliotecarios", {"nome": nome, "email": email, "senha": senha})
                self.after(0, lambda: messagebox.showinfo("Sucesso", "Bibliotecário cadastrado com sucesso!"))
                self.after(0, self.limpar)
                self.after(0, self.listar)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro", str(e)))
            finally:
                self.after(0, self.parar_loading)

        threading.Thread(target=tarefa, daemon=True).start()

    def atualizar(self):
        if not self.bibliotecario_id:
            messagebox.showwarning("Aviso", "Selecione um bibliotecário da lista para atualizar!")
            return

        nome = self.nome_entry.get().strip()
        email = self.email_entry.get().strip()
        senha = self.senha_entry.get().strip()

        if not nome or not email:
            messagebox.showwarning("Aviso", "Os campos 'Nome' e 'Email' são obrigatórios!")
            return

        dados = {"nome": nome, "email": email}
        if senha:
            dados["senha"] = senha

        self.iniciar_loading("Atualizando bibliotecário...")

        def tarefa():
            try:
                api.atualizar("bibliotecarios", self.bibliotecario_id, dados)
                self.after(0, lambda: messagebox.showinfo("Sucesso", "Bibliotecário atualizado com sucesso!"))
                self.after(0, self.limpar)
                self.after(0, self.listar)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro", str(e)))
            finally:
                self.after(0, self.parar_loading)

        threading.Thread(target=tarefa, daemon=True).start()

    def deletar(self):
        if not self.bibliotecario_id:
            messagebox.showwarning("Aviso", "Selecione um bibliotecário da lista para excluir!")
            return

        if not messagebox.askyesno("Confirmação", "Deseja realmente excluir este bibliotecário?"):
            return

        self.iniciar_loading("Excluindo bibliotecário...")

        def tarefa():
            try:
                api.deletar("bibliotecarios", self.bibliotecario_id)
                self.after(0, lambda: messagebox.showinfo("Sucesso", "Bibliotecário excluído com sucesso!"))
                self.after(0, self.limpar)
                self.after(0, self.listar)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro", str(e)))
            finally:
                self.after(0, self.parar_loading)

        threading.Thread(target=tarefa, daemon=True).start()


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
    tela = TelaBibliotecarios(root)
    tela.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
