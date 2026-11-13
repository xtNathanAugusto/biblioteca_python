import sys
import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services import api_client as api


class TelaLivros(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)

        self.title("Cadastro de Livros")
        self.geometry("750x600")
        self.resizable(False, False)
        self.livro_id = None

        # Formulário de Livro
        form = ttk.LabelFrame(self, text="Dados do Livro", padding=10)
        form.pack(padx=10, pady=10, fill="x")

        ttk.Label(form, text="Título:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.titulo_entry = ttk.Entry(form, width=50)
        self.titulo_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form, text="Autor:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.autor_entry = ttk.Entry(form, width=50)
        self.autor_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form, text="Editora:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.editora_entry = ttk.Entry(form, width=50)
        self.editora_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form, text="Exemplares:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.exemplares_entry = ttk.Entry(form, width=20)
        self.exemplares_entry.insert(0, "1")
        self.exemplares_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

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

        # Tabela (Treeview) de Livros
        tabela_frame = ttk.LabelFrame(self, text="Lista de Livros", padding=10)
        tabela_frame.pack(padx=10, pady=5, fill="both", expand=True)

        colunas = ("id", "titulo", "autor", "editora", "exemplares")
        self.tree = ttk.Treeview(tabela_frame, columns=colunas, show="headings", selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.heading("titulo", text="Título")
        self.tree.heading("autor", text="Autor")
        self.tree.heading("editora", text="Editora")
        self.tree.heading("exemplares", text="Exemplares")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("titulo", width=220)
        self.tree.column("autor", width=180)
        self.tree.column("editora", width=140)
        self.tree.column("exemplares", width=80, anchor="center")

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
        self.livro_id = None
        self.titulo_entry.delete(0, tk.END)
        self.autor_entry.delete(0, tk.END)
        self.editora_entry.delete(0, tk.END)
        self.exemplares_entry.delete(0, tk.END)
        self.exemplares_entry.insert(0, "1")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def ao_selecionar(self, event):
        selecionado = self.tree.selection()
        if selecionado:
            item = self.tree.item(selecionado[0])
            valores = item["values"]
            if valores:
                self.livro_id = valores[0]
                self.titulo_entry.delete(0, tk.END)
                self.titulo_entry.insert(0, valores[1])
                self.autor_entry.delete(0, tk.END)
                self.autor_entry.insert(0, valores[2])
                self.editora_entry.delete(0, tk.END)
                self.editora_entry.insert(0, valores[3] if valores[3] != "None" else "")
                self.exemplares_entry.delete(0, tk.END)
                self.exemplares_entry.insert(0, valores[4])

    def listar(self):
        self.iniciar_loading("Carregando livros...")

        def tarefa():
            try:
                livros = api.listar("livros")
                self.after(0, self._atualizar_tabela, livros)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro", str(e)))
            finally:
                self.after(0, self.parar_loading)

        threading.Thread(target=tarefa, daemon=True).start()

    def _atualizar_tabela(self, livros):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if livros:
            for livro in livros:
                self.tree.insert("", tk.END, values=(
                    livro.get("id_livro"),
                    livro.get("titulo"),
                    livro.get("autor"),
                    livro.get("editora") or "",
                    livro.get("exemplares", 1)
                ))

    def inserir(self):
        titulo = self.titulo_entry.get().strip()
        autor = self.autor_entry.get().strip()
        editora = self.editora_entry.get().strip()
        exemplares = self.exemplares_entry.get().strip()

        if not titulo or not autor:
            messagebox.showwarning("Aviso", "Os campos 'Título' e 'Autor' são obrigatórios!")
            return

        try:
            exemplares_int = int(exemplares) if exemplares else 1
        except ValueError:
            messagebox.showwarning("Aviso", "O campo 'Exemplares' deve ser um número inteiro!")
            return

        self.iniciar_loading("Cadastrando livro...")

        def tarefa():
            try:
                api.criar("livros", {
                    "titulo": titulo,
                    "autor": autor,
                    "editora": editora or None,
                    "exemplares": exemplares_int
                })
                self.after(0, lambda: messagebox.showinfo("Sucesso", "Livro cadastrado com sucesso!"))
                self.after(0, self.limpar)
                self.after(0, self.listar)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro", str(e)))
            finally:
                self.after(0, self.parar_loading)

        threading.Thread(target=tarefa, daemon=True).start()

    def atualizar(self):
        if not self.livro_id:
            messagebox.showwarning("Aviso", "Selecione um livro da lista para atualizar!")
            return

        titulo = self.titulo_entry.get().strip()
        autor = self.autor_entry.get().strip()
        editora = self.editora_entry.get().strip()
        exemplares = self.exemplares_entry.get().strip()

        if not titulo or not autor:
            messagebox.showwarning("Aviso", "Os campos 'Título' e 'Autor' são obrigatórios!")
            return

        try:
            exemplares_int = int(exemplares) if exemplares else 1
        except ValueError:
            messagebox.showwarning("Aviso", "O campo 'Exemplares' deve ser um número inteiro!")
            return

        self.iniciar_loading("Atualizando livro...")

        def tarefa():
            try:
                api.atualizar("livros", self.livro_id, {
                    "titulo": titulo,
                    "autor": autor,
                    "editora": editora or None,
                    "exemplares": exemplares_int
                })
                self.after(0, lambda: messagebox.showinfo("Sucesso", "Livro atualizado com sucesso!"))
                self.after(0, self.limpar)
                self.after(0, self.listar)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro", str(e)))
            finally:
                self.after(0, self.parar_loading)

        threading.Thread(target=tarefa, daemon=True).start()

    def deletar(self):
        if not self.livro_id:
            messagebox.showwarning("Aviso", "Selecione um livro da lista para excluir!")
            return

        if not messagebox.askyesno("Confirmação", "Deseja realmente excluir este livro?"):
            return

        self.iniciar_loading("Excluindo livro...")

        def tarefa():
            try:
                api.deletar("livros", self.livro_id)
                self.after(0, lambda: messagebox.showinfo("Sucesso", "Livro excluído com sucesso!"))
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

    # Verifica se a API Flask já está ativa; se não estiver, inicia automaticamente em segundo plano
    try:
        requests.get("http://127.0.0.1:5000/biblioteca/livros", timeout=1)
    except Exception:
        from app import iniciar_api
        threading.Thread(target=iniciar_api, daemon=True).start()
        time.sleep(1)

    root = tk.Tk()
    root.withdraw()
    tela = TelaLivros(root)
    tela.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
