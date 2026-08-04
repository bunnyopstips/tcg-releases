# TCG Release Tracker

Página web com todas as datas de lançamento de TCGs (Trading Card Games), atualizada automaticamente.

**TCGs incluídos:** Pokémon, One Piece, Dragon Ball Super, Yu-Gi-Oh!, Magic: The Gathering, Disney Lorcana

**Regiões:** Europa, EUA, Japão

## Como Configurar

### 1. Criar repositório no GitHub

1. Vai ao GitHub e cria um novo repositório (ex: `tcg-releases`)
2. Faz push de todos estes ficheiros para o repositório:

```bash
cd tcg-releases
git init
git add .
git commit -m "feat: página inicial TCG Release Tracker"
git branch -M main
git remote add origin https://github.com/TEU_USERNAME/tcg-releases.git
git push -u origin main
```

### 2. Ativar GitHub Pages

1. Vai a **Settings > Pages** no teu repositório
2. Em **Source**, seleciona **GitHub Actions**
3. O deploy será feito automaticamente a cada push

### 3. As GitHub Actions já estão configuradas

- **Deploy** (`deploy.yml`): Faz deploy no GitHub Pages a cada push no `main`
- **Update Releases** (`update-releases.yml`): Corre diariamente às 8h UTC para atualizar dados

A tua página estará disponível em: `https://TEU_USERNAME.github.io/tcg-releases/`

---

## Como Adicionar um Novo TCG

Edita o ficheiro `data/releases.json` e adiciona uma nova entrada no array `tcgs`:

```json
{
  "id": "novo-tcg",
  "name": "Nome do TCG",
  "logo": "",
  "color": "#FF5733",
  "releases": [
    {
      "name": "Nome do Produto/Set",
      "type": "Booster Pack",
      "regions": {
        "japan": { "date": "2025-06-15", "note": "Opcional" },
        "usa": { "date": "2025-08-20" },
        "europe": { "date": "2025-08-20" }
      }
    }
  ]
}
```

### Campos explicados:

| Campo | Descrição |
|-------|-----------|
| `id` | Identificador único (sem espaços, minúsculas) |
| `name` | Nome completo do TCG |
| `color` | Cor hex para identificar na UI |
| `releases` | Array de produtos/sets |
| `releases[].name` | Nome do produto |
| `releases[].type` | Tipo (Expansion, Booster Pack, Core Set, etc.) |
| `releases[].regions` | Objeto com as 3 regiões |
| `regions.date` | Data no formato `YYYY-MM-DD` (ou `null` se N/A) |
| `regions.note` | Nota opcional (ex: "Data estimada") |

### Dicas:
- Se uma região não tem o produto, usa `"date": null` com `"note": "Não disponível"`
- Para datas estimadas, adiciona `"note": "Data estimada"`
- O campo `name` dentro de uma região é para nomes alternativos (ex: nome japonês)

---

## Como Adicionar um Novo Lançamento

Para adicionar um novo set/produto a um TCG existente, basta adicionar ao array `releases` desse TCG:

```json
{
  "name": "Nome do Novo Set",
  "type": "Expansion",
  "regions": {
    "japan": { "date": "2026-01-15" },
    "usa": { "date": "2026-03-20" },
    "europe": { "date": "2026-03-20" }
  }
}
```

---

## Estrutura do Projeto

```
tcg-releases/
├── index.html              # Página principal (tudo num ficheiro)
├── data/
│   └── releases.json       # Dados dos lançamentos (edita aqui!)
├── scripts/
│   └── scraper.py          # Script de scraping automático
├── .github/
│   └── workflows/
│       ├── deploy.yml      # Deploy no GitHub Pages
│       └── update-releases.yml  # Atualização automática diária
├── requirements.txt        # Dependências Python
└── README.md              # Este ficheiro
```

## Atualização Manual

Podes sempre editar `data/releases.json` diretamente no GitHub (clica no ficheiro > Edit) e fazer commit. A página atualiza automaticamente em ~1 minuto.

## Atualização Automática

O script `scripts/scraper.py` corre diariamente e tenta buscar novos dados:
- **MTG**: Usa a API do Scryfall (funciona bem)
- **Outros TCGs**: Tenta scraping dos sites oficiais (pode precisar de manutenção)

Para correr manualmente: GitHub > Actions > "Update TCG Releases" > "Run workflow"
