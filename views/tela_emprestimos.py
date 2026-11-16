import sys
import os
import threading
from datetime import date, datetime
import tkinter as tk
from tkinter import messagebox, ttk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services import api_client as api


class TelaEmprestimos(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)

        self.title("Gerenciamento de Empréstimos")
        self.geometry("860x620")
        self.resizable(False, False)
        self.emprestimo_id = None

        self.mapa_alunos = {}
        self.mapa_bibliotecarios = {}
        self.mapa_livros = {}
        self.registros_emprestimos = {}

        form = ttk.LabelFrame(self, text="Dados do Empréstimo", padding=10)
        form.pack(padx=10, pady=10, fill="x")

        ttk.Label(form, text="Aluno:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.aluno_cb = ttk.Combobox(form, width=52, state="readonly")
        self.aluno_cb.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form, text="Bibliotecário:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.bibliotecario_cb = ttk.Combobox(form, width=52, state="readonly")
        self.bibliotecario_cb.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form, text="Livro:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.livro_cb = ttk.Combobox(form, width=52, state="readonly")
        self.livro_cb.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form, text="Data Devolução (DD/MM/AAAA):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.devolucao_entry = ttk.Entry(form, width=25)
        self.devolucao_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.devolucao_entry.bind("<KeyRelease>", self._mascara_data)

        botoes = ttk.Frame(self)
        botoes.pack(fill="x", padx=10, pady=5)

        self.btn_cadastrar = ttk.Button(botoes, text="Cadastrar", command=self.inserir)
        self.btn_cadastrar.pack(side="left", padx=5)

        self.btn_atualizar = ttk.Button(botoes, text="Atualizar", command=self.atualizar)
        self.btn_atualizar.pack(side="left", padx=5)

        self.btn_devolver = ttk.Button(botoes, text="Devolver Hoje", command=self.devolver)
        self.btn_devolver.pack(side="left", padx=5)

        self.btn_excluir = ttk.Button(botoes, text="Excluir", command=self.deletar)
        self.btn_excluir.pack(side="left", padx=5)

        self.btn_limpar = ttk.Button(botoes, text="Limpar", command=self.limpar)
        self.btn_limpar.pack(side="left", padx=5)

        self.btn_recarregar = ttk.Button(botoes, text="Recarregar", command=self.carregar_tudo)
        self.btn_recarregar.pack(side="left", padx=5)

        self.botoes = [
            self.btn_cadastrar,
            self.btn_atualizar,
            self.btn_devolver,
            self.btn_excluir,
            self.btn_limpar,
            self.btn_recarregar
        ]

        status_frame = ttk.Frame(self)
        status_frame.pack(side="bottom", fill="x", padx=10, pady=5)

        self.lbl_status = ttk.Label(status_frame, text="", foreground="blue")
        self.lbl_status.pack(side="left")

        self.progress = ttk.Progressbar(status_frame, mode="indeterminate", length=120)

        tabela_frame = ttk.LabelFrame(self, text="Lista de Empréstimos", padding=10)
        tabela_frame.pack(padx=10, pady=5, fill="both", expand=True)

        colunas = ("id", "aluno", "bibliotecario", "livro", "data", "data_devolucao")
        self.tree = ttk.Treeview(tabela_frame, columns=colunas, show="headings", selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.heading("aluno", text="Aluno")
        self.tree.heading("bibliotecario", text="Bibliotecário")
        self.tree.heading("livro", text="Livro")
        self.tree.heading("data", text="Data Empréstimo")
        self.tree.heading("data_devolucao", text="Data Devolução")

        self.tree.column("id", width=45, anchor="center")
        self.tree.column("aluno", width=170)
        self.tree.column("bibliotecario", width=160)
        self.tree.column("livro", width=190)
        self.tree.column("data", width=130, anchor="center")
        self.tree.column("data_devolucao", width=110, anchor="center")

        scrollbar = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.ao_selecionar)

        self.carregar_tudo()

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
        self.emprestimo_id = None
        self.aluno_cb.set("")
        self.bibliotecario_cb.set("")
        self.livro_cb.set("")
        self.devolucao_entry.delete(0, tk.END)
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def _mascara_data(self, event):
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab"):
            return
        digitos = "".join(c for c in self.devolucao_entry.get() if c.isdigit())[:8]
        novo = ""
        if len(digitos) > 4:
            novo = f"{digitos[:2]}/{digitos[2:4]}/{digitos[4:]}"
        elif len(digitos) > 2:
            novo = f"{digitos[:2]}/{digitos[2:]}"
        else:
            novo = digitos
        if novo != self.devolucao_entry.get():
            self.devolucao_entry.delete(0, tk.END)
            self.devolucao_entry.insert(0, novo)

    @staticmethod
    def _formatar_data_br(valor):
        if not valor:
            return ""
        texto = str(valor).strip()
        for fmt_entrada, fmt_saida in (
            ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M"),
            ("%Y-%m-%d", "%d/%m/%Y"),
            ("%d/%m/%Y", "%d/%m/%Y"),
        ):
            try:
                return datetime.strptime(texto, fmt_entrada).strftime(fmt_saida)
            except ValueError:
                continue
        return texto

    @staticmethod
    def _converter_data_para_banco(valor):
        texto = (valor or "").strip()
        if not texto:
            return None
        try:
            return datetime.strptime(texto, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("Data de devolução inválida! Use o formato DD/MM/AAAA.")

    def _selecionar_combo_por_id(self, combobox, mapa, id_alvo):
        for chave, valor_id in mapa.items():
            if valor_id == id_alvo:
                combobox.set(chave)
                return
        combobox.set("")

    def ao_selecionar(self, event):
        selecionado = self.tree.selection()
        if selecionado:
            item = self.tree.item(selecionado[0])
            valores = item["values"]
            if valores:
                self.emprestimo_id = valores[0]
                registro = self.registros_emprestimos.get(self.emprestimo_id)
                if registro:
                    self._selecionar_combo_por_id(
                        self.aluno_cb, self.mapa_alunos, registro.get("id_aluno")
                    )
                    self._selecionar_combo_por_id(
                        self.bibliotecario_cb, self.mapa_bibliotecarios, registro.get("id_bibliotecario")
                    )
                    self._selecionar_combo_por_id(
                        self.livro_cb, self.mapa_livros, registro.get("id_livro")
                    )
                    self.devolucao_entry.delete(0, tk.END)
                    if registro.get("data_devolucao"):
                        self.devolucao_entry.insert(0, self._formatar_data_br(registro.get("data_devolucao")))

    def carregar_tudo(self):
        self.iniciar_loading("Carregando dados da API...")

        def tarefa():
            try:
                alunos = api.listar("alunos") or []
                bibliotecarios = api.listar("bibliotecarios") or []
                livros = api.listar("livros") or []
                emprestimos = api.listar("emprestimos") or []
                self.after(
                    0,
                    self._atualizar_interface,
                    alunos,
                    bibliotecarios,
                    livros,
                    emprestimos
                )
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro", str(e)))
            finally:
                self.after(0, self.parar_loading)

        threading.Thread(target=tarefa, daemon=True).start()

    def listar(self):
        self.carregar_tudo()

    def _atualizar_interface(self, alunos, bibliotecarios, livros, emprestimos):
        self.mapa_alunos = {
            f"{a['id_aluno']} - {a['nome']}": a["id_aluno"] for a in alunos
        }
        self.aluno_cb["values"] = list(self.mapa_alunos.keys())

        self.mapa_bibliotecarios = {
            f"{b['id_bibliotecario']} - {b['nome']}": b["id_bibliotecario"] for b in bibliotecarios
        }
        self.bibliotecario_cb["values"] = list(self.mapa_bibliotecarios.keys())

        usuario_logado = api.obter_usuario_logado()
        if not self.emprestimo_id and usuario_logado:
            self._selecionar_combo_por_id(
                self.bibliotecario_cb,
                self.mapa_bibliotecarios,
                usuario_logado.get("id_bibliotecario")
            )

        self.mapa_livros = {
            f"{l['id_livro']} - {l['titulo']}": l["id_livro"] for l in livros
        }
        self.livro_cb["values"] = list(self.mapa_livros.keys())

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.registros_emprestimos = {}
        for emp in emprestimos:
            id_emp = emp.get("id_emprestimo")
            self.registros_emprestimos[id_emp] = emp
            self.tree.insert("", tk.END, values=(
                id_emp,
                f"{emp.get('id_aluno')} - {emp.get('nome_aluno', '')}",
                f"{emp.get('id_bibliotecario')} - {emp.get('nome_bibliotecario', '')}",
                f"{emp.get('id_livro')} - {emp.get('titulo_livro', '')}",
                self._formatar_data_br(emp.get("data")),
                self._formatar_data_br(emp.get("data_devolucao")) or "Pendente"
            ))

    def _obter_dados_formulario(self):
        aluno_chave = self.aluno_cb.get()
        bib_chave = self.bibliotecario_cb.get()
        livro_chave = self.livro_cb.get()
        data_devolucao = self.devolucao_entry.get().strip()

        id_aluno = self.mapa_alunos.get(aluno_chave)
        id_bibliotecario = self.mapa_bibliotecarios.get(bib_chave)
        id_livro = self.mapa_livros.get(livro_chave)

        if not id_aluno or not id_bibliotecario or not id_livro:
            messagebox.showwarning("Aviso", "Selecione Aluno, Bibliotecário e Livro!")
            return None

        try:
            data_banco = self._converter_data_para_banco(data_devolucao)
        except ValueError as e:
            messagebox.showwarning("Aviso", str(e))
            return None

        return {
            "id_aluno": id_aluno,
            "id_bibliotecario": id_bibliotecario,
            "id_livro": id_livro,
            "data_devolucao": data_banco
        }

    def inserir(self):
        dados = self._obter_dados_formulario()
        if not dados:
            return

        self.iniciar_loading("Cadastrando empréstimo...")

        def tarefa():
            try:
                api.criar("emprestimos", dados)
                self.after(0, lambda: messagebox.showinfo("Sucesso", "Empréstimo registrado com sucesso!"))
                self.after(0, self.limpar)
                self.after(0, self.carregar_tudo)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro", str(e)))
            finally:
                self.after(0, self.parar_loading)

        threading.Thread(target=tarefa, daemon=True).start()

    def atualizar(self):
        if not self.emprestimo_id:
            messagebox.showwarning("Aviso", "Selecione um empréstimo da lista para atualizar!")
            return

        dados = self._obter_dados_formulario()
        if not dados:
            return

        self.iniciar_loading("Atualizando empréstimo...")

        def tarefa():
            try:
                api.atualizar("emprestimos", self.emprestimo_id, dados)
                self.after(0, lambda: messagebox.showinfo("Sucesso", "Empréstimo atualizado com sucesso!"))
                self.after(0, self.limpar)
                self.after(0, self.carregar_tudo)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro", str(e)))
            finally:
                self.after(0, self.parar_loading)

        threading.Thread(target=tarefa, daemon=True).start()

    def devolver(self):
        if not self.emprestimo_id:
            messagebox.showwarning("Aviso", "Selecione um empréstimo da lista para registrar a devolução!")
            return

        hoje_br = date.today().strftime("%d/%m/%Y")
        hoje_banco = date.today().strftime("%Y-%m-%d")
        self.devolucao_entry.delete(0, tk.END)
        self.devolucao_entry.insert(0, hoje_br)

        self.iniciar_loading("Registrando devolução...")

        def tarefa():
            try:
                api.request("PUT", f"/emprestimos/{self.emprestimo_id}/devolver", json={"data_devolucao": hoje_banco})
                self.after(0, lambda: messagebox.showinfo("Sucesso", "Devolução registrada com sucesso!"))
                self.after(0, self.limpar)
                self.after(0, self.carregar_tudo)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro", str(e)))
            finally:
                self.after(0, self.parar_loading)

        threading.Thread(target=tarefa, daemon=True).start()

    def deletar(self):
        if not self.emprestimo_id:
            messagebox.showwarning("Aviso", "Selecione um empréstimo da lista para excluir!")
            return

        if not messagebox.askyesno("Confirmação", "Deseja realmente excluir este empréstimo?"):
            return

        self.iniciar_loading("Excluindo empréstimo...")

        def tarefa():
            try:
                api.deletar("emprestimos", self.emprestimo_id)
                self.after(0, lambda: messagebox.showinfo("Sucesso", "Empréstimo excluído com sucesso!"))
                self.after(0, self.limpar)
                self.after(0, self.carregar_tudo)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro", str(e)))
            finally:
                self.after(0, self.parar_loading)

        threading.Thread(target=tarefa, daemon=True).start()


if __name__ == "__main__":
    import time
    import requests

    try:
        requests.get("http://127.0.0.1:5000/biblioteca/emprestimos", timeout=1)
    except Exception:
        from app import iniciar_api
        threading.Thread(target=iniciar_api, daemon=True).start()
        time.sleep(1)

    root = tk.Tk()
    root.withdraw()
    tela = TelaEmprestimos(root)
    tela.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
