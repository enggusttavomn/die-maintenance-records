# Consulta de manutenção de estampos

**Tooling Production** é o identificador usado no histórico deste projeto.

Aplicação web para consultar fichas de manutenção de ferramentais,
acompanhar indicadores e exportar dados para Excel. A implementação reúne
uma **API Flask**, banco **MariaDB** e interface em **HTML, CSS e JavaScript**.

## Leitura rápida

| O que revisar | Arquivo ou diretório |
|---|---|
| Rotas, consultas SQL, cache e exportação | [backend/api/app.py](backend/api/app.py) |
| Telas e interação no navegador | [frontend/](frontend/) |
| Dependências da API | [backend/requirements.txt](backend/requirements.txt) |
| Configuração de conexão | [.env.example](.env.example) |
| Documentação de manutenção | [docs/HANDOVER.md](docs/HANDOVER.md) |
| Mapeamento entre API e banco | [docs/mapeamento_backend_banco.md](docs/mapeamento_backend_banco.md) |

## Estado desta versão

A API atual opera em **modo somente leitura**: os endpoints de criação,
atualização e exclusão estão bloqueados no código. Algumas telas refletem
um fluxo de edição mais amplo, mas não habilitam essas operações na API.

O código pode ser inspecionado publicamente. A execução dos endpoints de
dados depende de uma instância MariaDB e de um schema compatível com a
tabela `banco_dados`. **O dump operacional citado em versões antigas da
documentação não está incluído neste repositório.**

O arquivo [database/scripts/database.sql](database/scripts/database.sql)
é uma referência histórica com a tabela `fichas`; ele não recria, sozinho,
o schema `banco_dados` esperado pela API atual. Não é um procedimento de
instalação completo do banco.

## Funcionalidades disponíveis no código

- Consulta de fichas com filtros e cache de curta duração.
- Consulta de uma ficha pelo identificador.
- Indicadores agregados para dashboards.
- Exportação de fichas para Excel.
- Verificação de conectividade com o banco pelo endpoint de saúde.
- Telas para consulta, planejamento e impressão de fichas.

## Arquitetura

O Flask serve os arquivos de `frontend/` e os endpoints JSON. As consultas
e regras de serialização ficam em `backend/api/app.py`. A configuração
de conexão é lida de variáveis de ambiente ou do arquivo `.env` na raiz.

A seleção de perfil da interface usa estado no navegador e não representa
autenticação e autorização completas no servidor. Esta versão deve ser
tratada como material de desenvolvimento e avaliação local.

## Preparar o ambiente local

Pré-requisitos: **Python 3.10+**, Git e uma instância MariaDB local com o
schema compatível. Use apenas dados de demonstração ao preparar essa instância.

```bash
git clone https://github.com/enggusttavomn/tooling-production-gestao-de-manutencao-de-estampos.git
cd tooling-production-gestao-de-manutencao-de-estampos
python -m venv .venv
```

| Sistema | Ativar ambiente | Copiar configuração |
|---|---|---|
| Windows PowerShell | `.\.venv\Scripts\Activate.ps1` | `Copy-Item .env.example .env` |
| Linux / macOS | `source .venv/bin/activate` | `cp .env.example .env` |

```bash
python -m pip install -r backend/requirements.txt
```

Preencha `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` e `DB_PASSWORD`
com os valores da sua instância local. O template contém placeholders,
não credenciais utilizáveis. O banco precisa aceitar as consultas de
`backend/api/app.py`; a preparação do schema permanece uma pendência
para uma demonstração reproduzível do zero.

Com o banco preparado, defina o endereço local:

| Sistema | Comando |
|---|---|
| Windows PowerShell | `$env:FLASK_HOST="127.0.0.1"` |
| Linux / macOS | `export FLASK_HOST="127.0.0.1"` |

Em seguida, execute:

```bash
python backend/api/app.py
```

Abra <http://127.0.0.1:5000> e confira
<http://127.0.0.1:5000/health>. As páginas de dados e o endpoint de saúde
precisam da conexão com o banco para retornar os resultados esperados.

Os scripts em [backend/scripts/](backend/scripts/) preservam o fluxo
operacional anterior e podem exigir caminhos, ferramentas ou dumps locais
que não estão incluídos na cópia pública.

## Contrato de API

| Método | Rota | Comportamento atual |
|---|---|---|
| GET | `/api/fichas` | Lista fichas e aplica filtros |
| GET | `/api/ficha/<id>` | Consulta uma ficha |
| GET | `/api/estatisticas` | Retorna indicadores agregados |
| GET | `/api/exportar-excel` | Exporta dados em XLSX |
| GET | `/health` | Verifica conectividade com o banco |
| POST | `/api/fichas` | Bloqueado: somente leitura |
| PUT / DELETE | `/api/ficha/<id>` | Bloqueado: somente leitura |

## Verificações de desenvolvimento

```bash
python -m unittest discover -s backend/tests -v
```

Os testes usam o cliente Flask e banco simulado, sem credenciais ou dumps.
Cobrem acesso a arquivos, cache de consultas, expiração e bloqueio das escritas.
O GitHub Actions executa essa suíte a cada push e pull request.
Os testes de integração com MariaDB e exportação completa ainda dependem do
schema de demonstração pendente.

O servidor usa `127.0.0.1` por padrão e serve arquivos somente de `frontend/`.
`DEV_RELOAD=1` habilita o monitor de arquivos para desenvolvimento.
Para frontend em outra origem, defina explicitamente `CORS_ORIGINS` no `.env`.
Nenhuma origem adicional é habilitada por padrão.

## Próximos passos

- Publicar um schema de demonstração compatível, com dados sintéticos e setup validado.
- Implementar autenticação e autorização no backend antes de uma implantação.
- Separar rotas, acesso ao banco e regras de negócio.
- Ampliar os testes para integração com MariaDB e exportação.

## Contexto e autoria

Versão pessoal do projeto Tooling Production mantida por Gustavo Nascimento.
A documentação pública descreve a implementação disponível e seus limites.
