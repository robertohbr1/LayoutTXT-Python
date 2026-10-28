# LayoutTXT (Python)

Recriação em Python 3 (Tkinter) do projeto original em Visual Basic 6 (`C:\Guardar\LayoutTXT`).

## Como executar

```powershell
python -m layouttxt
```

## Como executar os testes

```powershell
python -m pytest
```

## Estrutura do projeto

- `layouttxt/domain/` — Regras de negócio puras (leitura de CSV de layout, identificação de tipos de linha, cálculo/validação de CPF/CNPJ, geração de valores, interpretação de tipos `IN`/`ECPF/CNPJ`/`ECEP`/`N`/`D`, busca com escopo, sequenciamento, substituição em lote, exclusão/criação de linhas e blocos de coluna).
- `layouttxt/infra/` — Leitura/gravação ANSI (`cp1252`) com preservação de bytes e backup `.Bak`, persistência de preferências em JSON (`%APPDATA%\LayoutTXT\settings.json`) e carregamento de `Nomes.txt`.
- `layouttxt/ui/` — Interface gráfica Tkinter fiel ao `frmPrincipal.frm` e `frmSequenciar.frm` (abas Arquivo, Edita, Lista, Ferramentas, Substitui e Linhas, editor monoespaçado com sublinhado em vermelho do campo atual, modo Insere/Sobrescreve e barra de status de 13 painéis).
- `layouts/` — Arquivos `.csv` de layout copiados do projeto original.
- `exemplos/` — Arquivos de teste copiados de `Arquivos Para Teste`.
- `tests/` — Suíte de testes unitários e de interface (`pytest`).
