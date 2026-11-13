import sys
import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services import api_client as api


class TelaAlunos(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)

        self.title("Cadastro de Alunos")
        self.geometry("700x560")
        self.resizable(False, False)
        self.aluno_id = None

        # Formulário de Aluno
        form = ttk.LabelFrame(self, text="Dados de Aluno", padding=10)
        form.pack(padx=10, pady=10, fill="x")

        ttk.Label(form, text="Nome:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.nome_entry = ttk.Entry(form, width=50)
        self.nome_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form, text="Email:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.email_entry = ttk.Entry(form, width=50)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form, text="Curso:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.curso_entry = ttk.Entry(form, width=50)
        self.curso_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Botões de Ação
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

        # Barra de status / loading
        status_frame = ttk.Frame(self)
        status_frame.pack(side="bottom", fill="x", padx=10, pady=5)

        self.lbl_status = ttk.Label(status_frame, text="", foreground="blue")
        self.lbl_status.pack(side="left")

        self.progress = ttk.Progressbar(status_frame, mode="indeterminate", length=120)

        # Tabela (Treeview) de Alunos
        tabela_frame = ttk.LabelFrame(self, text="Lista de Alunos", padding=10)
        tabela_frame.pack(padx=10, pady=5, fill="both", expand=True)

        colunas = ("id", "nome", "email", "curso")
        self.tree = ttk.Treeview(tabela_frame, columns=colunas, show="headings", selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("email", text="Email")
        self.tree.heading("curso", text="Curso")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nome", width=200)
        self.tree.column("email", width=220)
        self.tree.column("curso", width=180)

        scrollbar = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.ao_selecionar)

        # Carregar lista inicial
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
        self.aluno_id = None
        self.nome_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.curso_entry.delete(0, tk.END)
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def ao_selecionar(self, event):
        selecionado = self.tree.selection()
        if selecionado:
            item = self.tree.item(selecionado[0])
            valores = item["values"]
            if valores:
                self.aluno_id = valores[0]
                self.nome_entry.delete(0, tk.END)
                self.nome_entry.insert(0, valores[1])
                self.email_entry.delete(0, tk.END)
                self.email_entry.insert(0, valores[2])
                self.curso_entry.delete(0, tk.END)
                self.curso_entry.insert(0, valores[3])

    def listar(self):
        self.iniciar_loading("Carregando alunos...")

        def tarefa():
            try:
                alunos = api.listar("alunos")
                self.after(0, self._atualizar_tabela, alunos)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro", str(e)))
            finally:
                self.after(0, self.parar_loading)

        threading.Thread(target=tarefa, daemon=True).start()

    def _atualizar_tabela(self, alunos):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if alunos:
            for aluno in alunos:
                self.tree.insert("", tk.END, values=(
                    aluno.get("id_aluno"),
                    aluno.get("nome"),
                    aluno.get("email"),
                    aluno.get("curso")
                ))

    def inserir(self):
        nome = self.nome_entry.get().strip()
        email = self.email_entry.get().strip()
        curso = self.curso_entry.get().strip()

        if not nome or not email or not curso:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return

        self.iniciar_loading("Cadastrando aluno...")

        def tarefa():
            try:
                api.criar("alunos", {"nome": nome, "email": email, "curso": curso})
                self.after(0, lambda: messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso!"))
                self.after(0, self.limpar)
                self.after(0, self.listar)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro", str(e)))
            finally:
                self.after(0, self.parar_loading)

        threading.Thread(target=tarefa, daemon=True).start()

    def atualizar(self):
        if not self.aluno_id:
            messagebox.showwarning("Aviso", "Selecione um aluno da lista para atualizar!")
            return

        nome = self.nome_entry.get().strip()
        email = self.email_entry.get().strip()
        curso = self.curso_entry.get().strip()

        if not nome or not email or not curso:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return

        self.iniciar_loading("Atualizando aluno...")

        def tarefa():
            try:
                api.atualizar("alunos", self.aluno_id, {"nome": nome, "email": email, "curso": curso})
                self.after(0, lambda: messagebox.showinfo("Sucesso", "Aluno atualizado com sucesso!"))
                self.after(0, self.limpar)
                self.after(0, self.listar)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro", str(e)))
            finally:
                self.after(0, self.parar_loading)

        threading.Thread(target=tarefa, daemon=True).start()

    def deletar(self):
        if not self.aluno_id:
            messagebox.showwarning("Aviso", "Selecione um aluno da lista para excluir!")
            return

        if not messagebox.askyesno("Confirmação", "Deseja realmente excluir este aluno?"):
            return

        self.iniciar_loading("Excluindo aluno...")

        def tarefa():
            try:
                api.deletar("alunos", self.aluno_id)
                self.after(0, lambda: messagebox.showinfo("Sucesso", "Aluno excluído com sucesso!"))
                self.after(0, self.limpar)
                self.after(0, self.listar)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro", str(e)))
            finally:
                self.after(0, self.parar_loading)

        threading.Thread(target=tarefa, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    tela = TelaAlunos(root)
    tela.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
