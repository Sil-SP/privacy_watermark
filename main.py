import os
import sys
import io
import math
import textwrap
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color

# Configuração global da aparência
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def get_base_path():
    """Retorna o diretório base correto, seja executando o script ou o .exe compilado."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent

class PDFProtectorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Proteção de PDFs - Projetos de Engenharia e Arquitetura")
        self.geometry("650x600")
        self.minsize(600, 550)

        # Configuração do layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        # Variáveis
        self.folder_path = ctk.StringVar()
        self.var_cedente = ctk.StringVar()
        self.var_projeto = ctk.StringVar()
        self.var_receptor = ctk.StringVar()

        # UI Elements
        self.create_widgets()

    def create_widgets(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self, corner_radius=10)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1)

        # Título
        lbl_title = ctk.CTkLabel(main_frame, text="Configuração de Processamento", font=ctk.CTkFont(size=20, weight="bold"))
        lbl_title.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10))

        # 1. Pasta de Origem
        lbl_folder = ctk.CTkLabel(main_frame, text="Pasta de Origem:")
        lbl_folder.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        ent_folder = ctk.CTkEntry(main_frame, textvariable=self.folder_path, state="disabled")
        ent_folder.grid(row=1, column=1, padx=(0, 10), pady=10, sticky="ew")
        
        btn_folder = ctk.CTkButton(main_frame, text="Selecionar", command=self.select_folder, width=100)
        btn_folder.grid(row=1, column=2, padx=(0, 20), pady=10)

        # 2. Cedente(s)
        lbl_cedente = ctk.CTkLabel(main_frame, text="Nome(s) do(s) Cedente(s):")
        lbl_cedente.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        self.ent_cedente = ctk.CTkEntry(main_frame, textvariable=self.var_cedente, placeholder_text="Ex: João da Silva")
        self.ent_cedente.grid(row=2, column=1, columnspan=2, padx=(0, 20), pady=10, sticky="ew")

        # 3. Descrição do Projeto
        lbl_projeto = ctk.CTkLabel(main_frame, text="Descrição do Projeto:")
        lbl_projeto.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        
        self.ent_projeto = ctk.CTkEntry(main_frame, textvariable=self.var_projeto, placeholder_text="Ex: Residência X, Local Y")
        self.ent_projeto.grid(row=3, column=1, columnspan=2, padx=(0, 20), pady=10, sticky="ew")

        # 4. Receptor / Fornecedor
        lbl_receptor = ctk.CTkLabel(main_frame, text="Nome do Receptor:")
        lbl_receptor.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        
        self.ent_receptor = ctk.CTkEntry(main_frame, textvariable=self.var_receptor, placeholder_text="Ex: Empresa Fornecedora LTDA")
        self.ent_receptor.grid(row=4, column=1, columnspan=2, padx=(0, 20), pady=10, sticky="ew")

        # Botão Processar
        self.btn_process = ctk.CTkButton(self, text="PROCESSAR PDFs", font=ctk.CTkFont(size=16, weight="bold"), height=40, command=self.start_processing)
        self.btn_process.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Área de Log
        self.log_textbox = ctk.CTkTextbox(self, height=150)
        self.log_textbox.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        instrucoes = (
            "▶ INSTRUÇÕES BÁSICAS:\n"
            "1. Selecione a pasta onde se encontram os PDFs originais do projeto.\n"
            "2. Preencha todos os campos do formulário para garantir a responsabilização.\n"
            "3. Clique em PROCESSAR PDFs.\n\n"
            "Repositório / Documentação Oficial:\n"
            "https://github.com/Sil-SP/privacy_watermark"
        )
        self.log_textbox.insert("0.0", instrucoes)
        self.log_textbox.configure(state="disabled")

    def select_folder(self):
        folder_selected = filedialog.askdirectory(title="Selecione a Pasta com os PDFs")
        if folder_selected:
            # Usar path absoluto para evitar que o PyInstaller perca o caminho
            self.folder_path.set(str(Path(folder_selected).resolve()))

    def log(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")
        self.update_idletasks()

    def start_processing(self):
        if not self.folder_path.get():
            messagebox.showwarning("Aviso", "Selecione a pasta de origem primeiro!")
            return
            
        # Verifica se os campos não estão vazios ou contêm apenas espaços
        if not self.var_cedente.get().strip() or not self.var_projeto.get().strip() or not self.var_receptor.get().strip():
            messagebox.showwarning("Aviso", "Preencha todos os campos do formulário (Cedente, Projeto e Receptor) obrigatoriamente!")
            return

        # Desabilita o botão para evitar múltiplos cliques
        self.btn_process.configure(state="disabled")
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        
        self.log("Iniciando processamento...")

        # Inicia em background para manter a UI responsiva
        thread = threading.Thread(target=self.process_pdfs)
        thread.start()

    def create_disclaimer_page(self):
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=A4)
        width, height = A4
        
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 80, "TERMO DE CONFIDENCIALIDADE E SIGILO")

        c.setFont("Helvetica", 12)
        y = height - 130
        
        info_lines = [
            f"Cedente(s): {self.var_cedente.get()}",
            f"Projeto: {self.var_projeto.get()}",
            f"Receptor autorizado: {self.var_receptor.get()}"
        ]
        
        # Usa o textwrap para não deixar o texto da interface vazar as margens da página A4
        for full_line in info_lines:
            wrapped_lines = textwrap.wrap(full_line, width=70) # Limite de 70 caracteres por linha para fonte 12
            for line in wrapped_lines:
                c.drawString(50, y, line)
                y -= 20 # Espaçamento entre linhas do mesmo item
            y -= 10 # Espaçamento extra antes de pular para o próximo item principal

        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "AVISO LEGAL:")
        y -= 25

        c.setFont("Helvetica", 11)
        aviso = (
            "O conteúdo das páginas a seguir possui propriedade intelectual protegida e dados sensíveis de infraestrutura. "
            "A abertura, leitura ou armazenamento deste documento implica na aceitação tácita de sigilo absoluto. Este material "
            "deve ser usado exclusivamente para formulação de orçamento. É expressamente proibida a reprodução, compartilhamento "
            "com terceiros não autorizados ou uso de imagens em redes sociais e portfólios. Caso não concorde com estes termos, "
            "exclua este arquivo e todas as suas cópias imediatamente."
        )
        
        # Quebra de linha manual para texto fluir na página A4
        lines = textwrap.wrap(aviso, width=80)
        for line in lines:
            c.drawString(50, y, line)
            y -= 18

        c.save()
        packet.seek(0)
        reader = PdfReader(packet)
        return reader.pages[0]

    def create_watermark(self, width, height, rotation, text):
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(width, height))
        
        # Cor cinza com 15% de opacidade
        c.setFillColor(Color(0.5, 0.5, 0.5, alpha=0.15))
        
        # Resolve dimensões visuais considerando se a página tem rotação de 90 ou 270 graus
        is_rotated = (rotation % 180) != 0
        w_vis = height if is_rotated else width
        h_vis = width if is_rotated else height
        
        # Calcula tamanho da fonte baseado na diagonal da folha visual para escalar dinamicamente
        diag = math.sqrt(w_vis**2 + h_vis**2)
        text_length = max(len(text), 1)
        font_size = (0.8 * diag) / (text_length * 0.5)
        # Limita o tamanho da fonte para não ficar nem gigantesca nem minúscula
        font_size = min(max(font_size, 10), 150) 

        c.setFont("Helvetica-Bold", font_size)
        
        # Ângulo de rotação da diagonal visual
        angle = math.degrees(math.atan2(h_vis, w_vis))
        
        c.translate(width / 2, height / 2)
        
        # Desfazer a rotação do leitor no sentido horário girando o canvas no sentido anti-horário
        c.rotate(rotation)
        
        # Aplicar o ângulo desejado para o texto
        c.rotate(angle)
        
        # Centraliza o texto verticalmente também aplicando um offset usando parte do tamanho da fonte
        c.drawCentredString(0, -font_size / 4, text)
        
        c.save()
        packet.seek(0)
        reader = PdfReader(packet)
        return reader.pages[0]

    def process_pdfs(self):
        origin = Path(self.folder_path.get())
        
        # Sanitiza o nome do receptor para criar uma pasta válida no sistema (remove caracteres proibidos do Windows)
        nome_receptor = self.var_receptor.get().strip()
        safe_folder_name = "".join(c for c in nome_receptor if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not safe_folder_name:
            safe_folder_name = "orcamentos_marcados"
            
        output_dir = origin / safe_folder_name
        
        try:
            output_dir.mkdir(exist_ok=True)
            self.log(f"Pasta de saída verificada: {output_dir.name}")
        except Exception as e:
            self.log(f"Erro ao acessar/criar pasta de saída: {e}")
            self.btn_process.configure(state="normal")
            return

        pdf_files = list(origin.glob("*.pdf"))
        
        if not pdf_files:
            self.log("Nenhum arquivo PDF encontrado na pasta selecionada.")
            self.btn_process.configure(state="normal")
            return

        watermark_text = f"CONFIDENCIAL - Uso exclusivo: {self.var_receptor.get()}"
        
        success_count = 0
        error_count = 0

        for pdf_path in pdf_files:
            self.log(f"Processando: {pdf_path.name}")
            try:
                # Cada arquivo ganha uma nova instância de disclaimer_page para garantir integridade via PyPDF
                disclaimer_page = self.create_disclaimer_page()

                reader = PdfReader(str(pdf_path))
                writer = PdfWriter()
                
                # Inserindo página de rosto na primeira posição (index 0 / página 1)
                writer.add_page(disclaimer_page)
                
                # Iterando originais e aplicando a marca d'água em cada página independentemente do tamanho
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    
                    # Usa dimensão do mediabox original e aplica abs em predição de PDFs com mediabox negativos por peculiaridades da exportação
                    box = page.mediabox
                    width = abs(float(box.right - box.left))
                    height = abs(float(box.top - box.bottom))
                    
                    # Obter a rotação da página para corrigir PDFs girados nativamente
                    rotation = page.rotation if hasattr(page, 'rotation') and isinstance(page.rotation, int) else 0
                    
                    # Cria a marca d'água dinamicamente de acordo com o tamanho local daquela prancha
                    wm_page = self.create_watermark(width, height, rotation, watermark_text)
                    page.merge_page(wm_page)
                    
                    writer.add_page(page)

                # Salva o resultado sem comprometer o arquivo original
                out_filepath = output_dir / pdf_path.name
                with open(out_filepath, "wb") as f_out:
                    writer.write(f_out)
                    
                self.log(f"  -> Concluído com sucesso!")
                success_count += 1
                
            except Exception as e:
                self.log(f"  -> Erro ao processar {pdf_path.name}: {e}")
                error_count += 1

        self.log("-" * 40)
        self.log(f"Processamento concluído.")
        self.log(f"Sucesso: {success_count} | Erros: {error_count}")
        self.log(f"Arquivos salvos separadamente e com sucesso em: {output_dir}")
        self.btn_process.configure(state="normal")


if __name__ == "__main__":
    app = PDFProtectorApp()
    app.mainloop()
