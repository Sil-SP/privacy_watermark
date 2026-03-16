# Proteção de PDFs - Projetos de Engenharia e Arquitetura

Ferramenta local com interface gráfica criada para processar automaticamente arquivos em formato PDF, idealizada para lidar com projetos de arquitetura e infraestrutura (pranchas variando entre A4 a A0), visando a proteção da propriedade intelectual e garantindo a responsabilização por vazamentos (tracking confidencial). 

Todo processamento ocorre estritamente de maneira offline, dentro da máquina do usuário. Nenhuma informação é enviada à nuvem.

## Como funciona
1. A ferramenta lê todos os arquivos `.pdf` da pasta selecionada de origem.
2. É gerada, dinamicamente, uma primeira página de **Aviso Legal e Termo de Confidencialidade** (Disclaimer) em formato A4 que é inserida nativamente no princípio do PDF.
3. Todas as páginas originais subsequentes do projeto arquitetônico/elétrico recebem uma marca d'água semi-transparente apontando para o receptor confidencial selecionado, adequando dinamicamente a fonte consoante ao tamanho da folha (quer seja um A4, A3, A0 etc).
4. As cópias alteradas são salvas na subpasta `orcamentos_marcados/`, localizada obrigatoriamente dentro da raiz de origem, não sendo os originais deletados contanto. 

---

## Passo a Passo para Desenvolvimento ou Abertura Local

Antes de rodar o código-fonte, certifique-se de ter o [Python 3.8+](https://www.python.org/downloads/) configurado no PATH do seu terminal e execute:

```bash
pip install pypdf reportlab customtkinter
```

**Para Iniciar (sem compilar):**
```bash
python main.py
```

---

## Compilação Standalone via PyInstaller (.exe)

Para a distribuição desta automação entre outras máquinas Windows sem requerer que elas instalem o Python, você pode compilar utilizando o **PyInstaller**. Primeiro, garanta que seja instalado:

```bash
pip install pyinstaller
```

Em seguida, execute este exato comando na mesma pasta onde recai o arquivo em questão. A flag `--windowed` assegura que não haverá janelas de terminal ou DOS rodando ao fundo do sistema. O executável irá integrar plenamente sem rastros aparentes do console:

```bash
pyinstaller --noconfirm --onefile --windowed --name "ProtetorPDF" "main.py"
```

Uma pasta auxiliar `/dist` será concebida. Lá dentre, você resgatará o seu singelo executável `ProtetorPDF.exe`. 
