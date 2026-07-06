# Cards de Resultados — Parceiros vero

Script reutilizável que lê a planilha de rentabilização, valida os números e gera:

- **Card geral**: visão consolidada de todos os parceiros/webdealers
- **Cards individuais**: um card por parceiro, com os números só daquele parceiro

Os cards seguem a identidade visual da vero (cores + logo) e são páginas HTML
autocontidas (sem dependências externas além das fontes), prontas para publicar
no GitHub Pages com **link fixo** por parceiro.

## Estrutura do projeto

```
vero-cards/
├── gerar_cards.py           # script principal (rode este arquivo)
├── templates.py             # layout/HTML/SVG dos cards (cores e estilo vero)
├── requirements.txt
├── dados/                   # coloque aqui a planilha do dia (.xlsx)
├── assets/                  # logos vero em PNG (coloridos e branco)
├── site/                    # SAÍDA gerada — index.html + parceiros/*.html
└── .github/workflows/deploy.yml   # publica o site/ automaticamente no GitHub Pages
```

## 1. Uso local (rodar todo dia com uma planilha nova)

```bash
pip install -r requirements.txt

# coloque a planilha nova em dados/ (ou aponte o caminho direto)
python gerar_cards.py dados/Rentabilização_dados.xlsx
```

Isso vai:

1. Imprimir no terminal os meses encontrados na aba `Planilha2`.
2. **Validar automaticamente** as colunas "Média DU" (tentativas por mailing)
   e as duas "Conversão" (Produtiva e Mailing): se algum valor estiver fora de
   escala (negativo, maior que 100% sem justificativa, batendo `#DIV/0!` etc.),
   o script recalcula a partir dos dados brutos e **avisa no terminal** o que
   foi corrigido e por quê.
3. Escolher automaticamente o mês mais recente que já tenha resultado de
   campanha (produtivo/venda preenchidos). Para forçar um mês específico:
   ```bash
   python gerar_cards.py dados/Rentabilização_dados.xlsx --mes Junho
   ```
4. Gerar os arquivos em `site/`:
   - `site/index.html` — **card geral**: agora no formato de **relatório comercial**
     (inspirado no painel "Acompanhamento Evolutivo" que vocês usam), com:
     - banner com o logo vero e duas caixas de destaque (mês de referência e
       média de conversão do grupo);
     - um **painel por parceiro** com farol 🟢🟠🔴 (verde = acima da média do
       grupo, laranja = perto, vermelho = abaixo), uma **tabela evolutiva
       mês a mês** (Mailing, Vendas, Conversão) usando os meses disponíveis na
       planilha, e uma caixa de destaque com "Ativos por dia útil" +
       evolução % vs. mês anterior;
     - bloco **consolidado geral do período** (soma dos 3 parceiros);
     - bloco de **conversão consolidada por parceiro** (ícones + %);
     - **insights executivos** gerados automaticamente a partir dos próprios
       dados (melhor parceiro, ponto de atenção, mailing pendente, prioridade);
     - rodapé com nota explicando os critérios do farol e qualquer alerta de
       qualidade de dados (ex.: meses idênticos).
   - `site/parceiros/tmkt.html`, `site/parceiros/midia-simples.html`,
     `site/parceiros/webdealer-logmais.html` — cards individuais, um por
     parceiro, focados só naquele parceiro.

Abra `site/index.html` no navegador para conferir antes de publicar.

> **Adaptações em relação ao painel de referência**: como a nossa planilha
> tem dados por **mês** (não por dia), a "evolução diária" virou uma
> **evolução mensal** (Maio/Junho/Julho); e como não existe uma **meta fixa**
> cadastrada, o farol usa a **média de conversão do grupo no mês** como
> referência em vez de um percentual de meta.

> **Nota sobre a Evolução Ativos DU**: como nos dados de exemplo "Maio" e
> "Junho" estão idênticos (ver aviso do terminal e do rodapé do relatório), a
> evolução aparece como +0,0% — isso é esperado até a planilha de Junho ser
> realmente atualizada com números próprios. Quando não existe mês anterior
> na planilha ou faltam dados de Ativos DU, o campo mostra "—" em vez de
> inventar um número.

> Observação encontrada nos dados de exemplo: os números de "Maio" e "Junho"
> na planilha enviada estão **idênticos** para os três parceiros. O script avisa
> isso no terminal — vale confirmar se a aba foi realmente atualizada com os
> dados reais de Junho antes de divulgar.

## 2. Publicar no GitHub Pages (link fixo para compartilhar)

Como o ambiente onde este script foi gerado não tem acesso à internet, você
mesmo precisa criar o repositório no GitHub (uma vez só). Depois disso, o
workflow incluso (`.github/workflows/deploy.yml`) publica automaticamente toda
vez que você atualizar a planilha — sem precisar rodar nada manualmente.

### Passo a passo (uma vez)

1. Crie um repositório novo no GitHub (pode ser privado), por exemplo
   `vero-cards-parceiros`.
2. Dentro desta pasta (`vero-cards/`), rode:
   ```bash
   git init
   git add .
   git commit -m "Cards de resultados dos parceiros"
   git branch -M main
   git remote add origin https://github.com/SEU-USUARIO/vero-cards-parceiros.git
   git push -u origin main
   ```
3. No GitHub, vá em **Settings → Pages** e em "Build and deployment" escolha
   **Source: GitHub Actions** (não "Deploy from a branch").
4. Pronto. O workflow já roda automaticamente no primeiro push (aba **Actions**
   do repositório mostra o progresso, leva cerca de 1 minuto).

Seus links fixos ficam em:

```
https://SEU-USUARIO.github.io/vero-cards-parceiros/                       -> card geral
https://SEU-USUARIO.github.io/vero-cards-parceiros/parceiros/tmkt.html
https://SEU-USUARIO.github.io/vero-cards-parceiros/parceiros/midia-simples.html
https://SEU-USUARIO.github.io/vero-cards-parceiros/parceiros/webdealer-logmais.html
```

Esses caminhos **não mudam** de um dia para o outro (o slug vem do nome do
parceiro), então você pode mandar o mesmo link para cada webdealer todo mês —
o conteúdo é atualizado, o endereço continua o mesmo.

### Rotina diária/mensal depois disso

Só troque o arquivo em `dados/` (pode manter o mesmo nome ou trocar) e suba:

```bash
cp /caminho/para/nova_planilha.xlsx dados/Rentabilização_dados.xlsx
git add dados/
git commit -m "Atualiza dados do mês"
git push
```

O GitHub Actions já roda `gerar_cards.py` sozinho (com validação e avisos
visíveis na aba Actions do repositório) e publica o `site/` atualizado nos
mesmos links. Se preferir, dá pra rodar `python gerar_cards.py ...` localmente
antes também, só para conferir os avisos de validação no seu terminal.

Se quiser gerar para um mês específico via Actions (em vez do automático),
use **Actions → Gerar cards e publicar no GitHub Pages → Run workflow** e
preencha o campo "mes".

## 3. Personalizar

- **Cores/identidade**: editar o dicionário `CORES` em `templates.py`.
- **Logos**: trocar os arquivos em `assets/vero_logo.png` (colorido) e
  `assets/vero_logo_branco.png` (branco), mantendo os mesmos nomes.
- **Textos dos cards**: editar `build_card_geral` e `build_card_parceiro` em
  `gerar_cards.py`.
- **Tolerância da validação**: constantes `TOLERANCIA_REL` / `TOLERANCIA_ABS`
  no topo de `gerar_cards.py`.
