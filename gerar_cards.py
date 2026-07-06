#!/usr/bin/env python3
"""
gerar_cards.py — Gera cards de divulgação de resultados dos parceiros/webdealers
seguindo a identidade visual da vero, a partir da planilha de rentabilização.

Uso:
    python gerar_cards.py caminho/para/planilha.xlsx [--saida site] [--mes Junho] [--assets assets]

A cada execução:
  1. Lê a aba "Planilha2" (bloco de dados por mês/parceiro).
  2. Valida "Média DU" (tentativas por mailing) e as "Conversão" (Produtiva e Mailing),
     corrigindo automaticamente valores fora de escala e avisando no terminal.
  3. Gera:
       site/index.html                  -> card geral (consolidado)
       site/parceiros/<slug>.html       -> um card por parceiro
  4. Os arquivos são estáticos (HTML autocontido, logos embutidos em base64),
     prontos para publicar no GitHub Pages com URL fixa por parceiro.
"""
import argparse
import re
import sys
import base64
import unicodedata
from datetime import datetime
from pathlib import Path

import pandas as pd

import templates as tpl

# --------------------------------------------------------------------------
# Identidade visual vero
# --------------------------------------------------------------------------
CORES = {
    "rosa": "#EE0056",
    "bordo": "#D20032",
    "bordo_escuro": "#920026",
    "rosa_claro": "#FF7EA0",
    "laranja": "#FF8D17",
    "amarelo": "#FFD000",
    "cinza1": "#ECF0EE",
    "cinza2": "#D3D2CF",
    "cinza3": "#9A9B9E",
    "grafite": "#5F5F5F",
}

TOLERANCIA_REL = 0.02   # 2% de tolerância antes de considerar "inconsistente"
TOLERANCIA_ABS = 0.005  # tolerância absoluta mínima para conversões (0-1)


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------
def slugify(nome: str) -> str:
    nome = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    nome = re.sub(r"[^a-zA-Z0-9]+", "-", nome).strip("-").lower()
    return nome or "parceiro"


def fmt_int(n):
    if n is None or (isinstance(n, float) and pd.isna(n)):
        return "—"
    return f"{int(round(n)):,}".replace(",", ".")


def fmt_num1(n):
    if n is None or (isinstance(n, float) and pd.isna(n)):
        return "—"
    return f"{n:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(x, casas=1):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return "—"
    s = f"{x*100:.{casas}f}"
    return s.replace(".", ",") + "%"


def fmt_pct_signed(x, casas=1):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return "—"
    s = f"{x*100:+.{casas}f}"
    return s.replace(".", ",") + "%"


def is_blank(v):
    return v is None or (isinstance(v, float) and pd.isna(v))


def to_float_or_none(v):
    if is_blank(v):
        return None
    if isinstance(v, str):
        try:
            return float(v.replace(",", "."))
        except ValueError:
            return None
    try:
        f = float(v)
        if pd.isna(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------
# Leitura e parsing da planilha
# --------------------------------------------------------------------------
def ler_blocos(caminho_xlsx, aba="Planilha2"):
    """Detecta dinamicamente cada bloco mensal (linha de cabeçalho 'Parceiro'
    seguida das linhas de parceiros, até a próxima linha em branco)."""
    df = pd.read_excel(caminho_xlsx, sheet_name=aba, header=None)

    blocos = []
    i = 0
    nrows = len(df)
    while i < nrows:
        row = df.iloc[i]
        if str(row.get(2, "")).strip() == "Parceiro":
            header_total_du = str(row.get(11, "Total DU"))
            m = re.search(r"Total\s+([\d,]+)\s*DU", header_total_du)
            dias_uteis = float(m.group(1).replace(",", ".")) if m else None

            linhas = []
            j = i + 1
            while j < nrows and not is_blank(df.iloc[j].get(1)):
                r = df.iloc[j]
                linhas.append({
                    "mes": str(r.get(1)).strip(),
                    "parceiro": str(r.get(2)).strip(),
                    "mailing": to_float_or_none(r.get(3)),
                    "tentativas": to_float_or_none(r.get(4)),
                    "media_du_bruto": to_float_or_none(r.get(5)),
                    "produtivo": to_float_or_none(r.get(6)),
                    "recusa": to_float_or_none(r.get(7)),
                    "venda": to_float_or_none(r.get(8)),
                    "conv_produtiva_bruto": to_float_or_none(r.get(9)),
                    "ativos_du": to_float_or_none(r.get(10)),
                    "total_du_bruto": to_float_or_none(r.get(11)),
                    "conv_mailing_bruto": to_float_or_none(r.get(12)),
                })
                j += 1

            if linhas:
                blocos.append({
                    "mes": linhas[0]["mes"],
                    "dias_uteis": dias_uteis,
                    "label_total_du": header_total_du,
                    "linhas": linhas,
                })
            i = j
        else:
            i += 1
    return blocos


# --------------------------------------------------------------------------
# Validação / correção automática
# --------------------------------------------------------------------------
def validar_linha(linha, contexto, avisos):
    """Valida 'Média DU' (tentativas / mailing) e as duas Conversões.
    Retorna a linha com campos '_final' corrigidos e sinaliza avisos."""
    mailing = linha["mailing"]
    tentativas = linha["tentativas"]
    produtivo = linha["produtivo"]
    venda = linha["venda"]
    ativos_du = linha["ativos_du"]
    dias_uteis = linha.get("_dias_uteis")

    # --- Média DU (tentativas por registro de mailing) ------------------
    media_calc = None
    if tentativas is not None and mailing:
        media_calc = tentativas / mailing
    media_bruto = linha["media_du_bruto"]
    if media_calc is not None:
        if media_bruto is None or media_bruto < 0 or media_bruto > 1000 or (
            media_bruto and abs(media_bruto - media_calc) / max(media_calc, 1e-9) > TOLERANCIA_REL
        ):
            if media_bruto is not None and (media_bruto < 0 or media_bruto > 1000):
                avisos.append(
                    f"[{contexto}] Média DU fora de escala ({media_bruto}); corrigido para {media_calc:.4f} "
                    f"(recalculado = tentativas / mailing)"
                )
            media_final = media_calc
        else:
            media_final = media_bruto
    else:
        media_final = None
        if media_bruto is not None and media_bruto < 0:
            avisos.append(f"[{contexto}] Média DU negativa ({media_bruto}); ajustada para 0")
            media_final = 0.0
        elif media_bruto is not None:
            media_final = media_bruto

    # --- Conversão Produtiva (venda / produtivo) -------------------------
    conv_prod_calc = None
    if produtivo:
        conv_prod_calc = venda / produtivo if venda is not None else None
    conv_prod_final = _validar_conversao(
        "Conversão Produtiva", linha["conv_produtiva_bruto"], conv_prod_calc, contexto, avisos
    )

    # --- Total DU (ativos_du * dias uteis do periodo) --------------------
    total_du_calc = None
    if ativos_du is not None and dias_uteis is not None:
        total_du_calc = ativos_du * dias_uteis
    total_du_bruto = linha["total_du_bruto"]
    if total_du_calc is not None:
        if total_du_bruto is None or total_du_bruto < 0 or (
            total_du_bruto and abs(total_du_bruto - total_du_calc) / max(total_du_calc, 1e-9) > TOLERANCIA_REL
        ):
            if total_du_bruto is not None and total_du_bruto >= 0 and total_du_bruto != 0:
                avisos.append(
                    f"[{contexto}] Total {dias_uteis:g} DU inconsistente (planilha={total_du_bruto}, "
                    f"recalculado={total_du_calc:.1f}); usando recalculado"
                )
            total_du_final = total_du_calc
        else:
            total_du_final = total_du_bruto
    else:
        total_du_final = total_du_bruto if (total_du_bruto is not None and total_du_bruto >= 0) else None

    # --- Conversão Mailing (total_du / mailing) --------------------------
    conv_mail_calc = None
    if total_du_final is not None and mailing:
        conv_mail_calc = total_du_final / mailing
    conv_mail_final = _validar_conversao(
        "Conversão Mailing", linha["conv_mailing_bruto"], conv_mail_calc, contexto, avisos
    )

    linha["media_du"] = media_final
    linha["conv_produtiva"] = conv_prod_final
    linha["total_du"] = total_du_final
    linha["conv_mailing"] = conv_mail_final
    return linha


def _validar_conversao(nome, bruto, calculado, contexto, avisos):
    if calculado is not None:
        if bruto is None:
            return calculado
        if bruto < 0 or bruto > 1.5:
            avisos.append(
                f"[{contexto}] {nome} fora de escala ({bruto}); corrigida para {calculado*100:.2f}% (recalculada)"
            )
            return calculado
        diff = abs(bruto - calculado)
        if diff > max(TOLERANCIA_ABS, TOLERANCIA_REL * calculado):
            avisos.append(
                f"[{contexto}] {nome} inconsistente (planilha={bruto*100:.2f}%, recalculada={calculado*100:.2f}%); "
                f"usando recalculada"
            )
            return calculado
        return bruto
    # sem como recalcular: só sanitiza o valor bruto
    if bruto is None:
        return None
    if bruto < 0:
        avisos.append(f"[{contexto}] {nome} negativa ({bruto}); ajustada para 0%")
        return 0.0
    if bruto > 1:
        convertida = bruto / 100
        if convertida <= 1:
            avisos.append(
                f"[{contexto}] {nome} parecia estar em formato percentual ({bruto}); "
                f"ajustada dividindo por 100 -> {convertida*100:.2f}%"
            )
            return convertida
        avisos.append(f"[{contexto}] {nome} fora de escala ({bruto}); limitada a 100%")
        return 1.0
    return bruto


def validar_blocos(blocos):
    avisos = []
    for bloco in blocos:
        for linha in bloco["linhas"]:
            linha["_dias_uteis"] = bloco["dias_uteis"]
            contexto = f"{bloco['mes']}/{linha['parceiro']}"
            validar_linha(linha, contexto, avisos)

    # checagem de qualidade: meses com dados idênticos entre si (indício de
    # planilha não atualizada / copy-paste)
    for a, b in zip(blocos, blocos[1:]):
        chaves = ["mailing", "tentativas", "produtivo", "venda", "ativos_du"]
        iguais = True
        for la, lb in zip(a["linhas"], b["linhas"]):
            if la["parceiro"] != lb["parceiro"]:
                iguais = False
                break
            for k in chaves:
                va, vb = la.get(k), lb.get(k)
                if is_blank(va) and is_blank(vb):
                    continue
                if va != vb:
                    iguais = False
                    break
            if not iguais:
                break
        if iguais and a["linhas"] and b["linhas"]:
            avisos.append(
                f"⚠ Atenção: os dados de '{a['mes']}' e '{b['mes']}' estão IDÊNTICOS para todos os parceiros. "
                f"Verifique se a planilha de '{b['mes']}' foi realmente atualizada."
            )
    return avisos


def escolher_mes(blocos, mes_arg=None):
    if mes_arg:
        for b in blocos:
            if b["mes"].lower() == mes_arg.lower():
                return b
        raise SystemExit(f"Mês '{mes_arg}' não encontrado na planilha. Meses disponíveis: "
                          f"{', '.join(b['mes'] for b in blocos)}")
    # padrão: último bloco que tenha resultado de campanha (produtivo preenchido)
    candidatos = [b for b in blocos if any(l["produtivo"] is not None for l in b["linhas"])]
    return candidatos[-1] if candidatos else blocos[-1]


# --------------------------------------------------------------------------
# Agregados para o card geral
# --------------------------------------------------------------------------
def agregados_gerais(bloco):
    linhas = bloco["linhas"]
    mailing_total = sum(l["mailing"] or 0 for l in linhas)
    produtivo_total = sum(l["produtivo"] or 0 for l in linhas)
    venda_total = sum(l["venda"] or 0 for l in linhas)
    total_du_total = sum(l["total_du"] or 0 for l in linhas)
    tentativas_total = sum(l["tentativas"] or 0 for l in linhas if l["tentativas"] is not None)
    ativos_du_total = sum(l["ativos_du"] or 0 for l in linhas if l["ativos_du"] is not None)
    conv_prod_geral = (venda_total / produtivo_total) if produtivo_total else None
    conv_mail_geral = (total_du_total / mailing_total) if mailing_total else None
    media_du_geral = (tentativas_total / mailing_total) if (mailing_total and tentativas_total) else None
    return {
        "mailing_total": mailing_total,
        "produtivo_total": produtivo_total,
        "venda_total": venda_total,
        "total_du_total": total_du_total,
        "tentativas_total": tentativas_total,
        "ativos_du_total": ativos_du_total,
        "conv_prod_geral": conv_prod_geral,
        "conv_mail_geral": conv_mail_geral,
        "media_du_geral": media_du_geral,
    }


def evolucao_ativos_du_geral(blocos_todos, bloco_atual):
    """% de evolução da SOMA de Ativos/Dia Útil de todos os parceiros do mês
    vigente em relação ao mês imediatamente anterior na planilha."""
    idx = blocos_todos.index(bloco_atual)
    if idx == 0:
        return None
    anterior = blocos_todos[idx - 1]
    soma_atual = sum(l["ativos_du"] or 0 for l in bloco_atual["linhas"] if l["ativos_du"] is not None)
    soma_anterior = sum(l["ativos_du"] or 0 for l in anterior["linhas"] if l["ativos_du"] is not None)
    if not soma_anterior:
        return None
    return (soma_atual - soma_anterior) / soma_anterior


def evolucao_ativos_du(blocos_todos, bloco_atual):
    """% de evolução de Ativos/Dia Útil do mês vigente (bloco_atual) em relação
    ao mês imediatamente anterior na planilha, por parceiro."""
    idx = blocos_todos.index(bloco_atual)
    if idx == 0:
        return {}
    anterior = blocos_todos[idx - 1]
    ativos_anterior = {l["parceiro"].strip().lower(): l["ativos_du"] for l in anterior["linhas"]}
    resultado = {}
    for l in bloco_atual["linhas"]:
        chave = l["parceiro"].strip().lower()
        atual = l["ativos_du"]
        prev = ativos_anterior.get(chave)
        if atual is not None and prev:
            resultado[chave] = (atual - prev) / prev
        else:
            resultado[chave] = None
    return resultado


def mailing_pendente_proximo_mes(blocos, bloco_atual):
    """Se existir um bloco seguinte ao mês corrente só com mailing carregado
    (campanha ainda não iniciada), devolve (mes, total_mailing)."""
    idx = blocos.index(bloco_atual)
    if idx + 1 < len(blocos):
        prox = blocos[idx + 1]
        if all(l["produtivo"] is None for l in prox["linhas"]):
            total = sum(l["mailing"] or 0 for l in prox["linhas"])
            return prox["mes"], total
    return None, None


# --------------------------------------------------------------------------
# Construção dos cards (HTML)
# --------------------------------------------------------------------------
def farol(pct, benchmark):
    """Classifica o desempenho em verde/laranja/vermelho comparando com um
    valor de referência (não temos meta fixa cadastrada, então usamos a
    média do grupo como referência)."""
    if pct is None or not benchmark:
        return "cinza"
    if pct >= benchmark:
        return "verde"
    if pct >= benchmark * 0.75:
        return "laranja"
    return "vermelho"


def build_card_geral(bloco, blocos_todos, logo_branco, logo_cor, gerado_em, parceiro_links):
    agg = agregados_gerais(bloco)
    mes = bloco["mes"]

    conv_prod_medias = [l["conv_produtiva"] for l in bloco["linhas"] if l["conv_produtiva"] is not None]
    media_grupo = sum(conv_prod_medias) / len(conv_prod_medias) if conv_prod_medias else 0

    evolucao = evolucao_ativos_du(blocos_todos, bloco)
    evolucao_geral = evolucao_ativos_du_geral(blocos_todos, bloco)
    mes_pendente, mailing_pendente = mailing_pendente_proximo_mes(blocos_todos, bloco)

    linhas_ordenadas = sorted(bloco["linhas"], key=lambda l: (l["conv_produtiva"] or 0), reverse=True)

    # --- Banner -----------------------------------------------------------
    banner = f"""
    <div class="rel-banner">
      <div class="brand">
        <img class="logo" src="{logo_branco}" alt="vero">
        <div class="titles">
          <span class="tag">Relatório comercial · Mailing parceiros</span>
          <h1>RENTABILIZAÇÃO PARCEIROS NACIONAL</h1>
          <p>Evolução mês a mês da conversão produtiva e das vendas por parceiro, com foco em resultado e consistência.</p>
        </div>
      </div>
      <div class="meta-boxes">
        <div class="meta-box"><div class="valor">{mes}</div><div class="lbl">Mês de referência</div></div>
        <div class="meta-box"><div class="valor">{fmt_pct(media_grupo)}</div><div class="lbl">Média do grupo (referência)</div></div>
      </div>
    </div>"""

    # --- Painéis por parceiro (tabela evolutiva mês a mês) -----------------
    painel_html = ""
    for l in linhas_ordenadas:
        nome = l["parceiro"].title()
        inicial = nome[0]
        cor_farol = farol(l["conv_produtiva"], media_grupo)

        linhas_tabela = ""
        for b in blocos_todos:
            linha_mes = next((x for x in b["linhas"] if x["parceiro"].strip().lower() == l["parceiro"].strip().lower()), None)
            if not linha_mes:
                continue
            if linha_mes["produtivo"] is None:
                linhas_tabela += f"""<tr class="pendente">
                  <td>{b['mes']}</td><td>{fmt_int(linha_mes['mailing'])}</td><td>—</td><td class="conv">Aguardando</td><td class="conv">—</td>
                </tr>"""
            else:
                cor_linha = farol(linha_mes["conv_produtiva"], media_grupo)
                linhas_tabela += f"""<tr>
                  <td>{b['mes']}</td><td>{fmt_int(linha_mes['mailing'])}</td><td>{fmt_int(linha_mes['venda'])}</td>
                  <td class="conv {cor_linha}">{fmt_pct(linha_mes['conv_produtiva'])}</td>
                  <td class="conv">{fmt_pct(linha_mes['conv_mailing'])}</td>
                </tr>"""

        evol = evolucao.get(l["parceiro"].strip().lower())

        painel_html += f"""
        <div class="painel">
          <div class="painel-head">
            <div class="painel-icone">{inicial}</div>
            <div class="painel-nome">{nome}</div>
            <div class="farol {cor_farol}" title="Conversão produtiva vs. média do grupo"></div>
          </div>
          <table class="evolutivo">
            <tr><th>Mês</th><th>Mailing</th><th>Vendas Total</th><th>Conversão Produtiva</th><th>Conv. Total</th></tr>
            {linhas_tabela}
          </table>
          <div class="callout">
            <div class="num">{fmt_int(l['ativos_du'])}</div>
            <div class="txt"><b>Ativos por dia útil</b>Evolução vs. mês anterior: {fmt_pct_signed(evol)}</div>
          </div>

        </div>"""

    # --- Consolidado geral do período --------------------------------------
    evol_geral_tipo = "verde" if (evolucao_geral or 0) >= 0 else "vermelho"
    consolidado = f"""
    <div class="rel-consolidado">
      <div class="rotulo">Consolidado geral<small>{mes}</small></div>
      <div class="stat-mini"><div class="num">{fmt_int(agg['mailing_total'])}</div><div class="lbl">Mailing total</div></div>
      <div class="stat-mini"><div class="num">{fmt_int(agg['produtivo_total'])}</div><div class="lbl">Contatos produtivos</div></div>
      <div class="stat-mini"><div class="num">{fmt_int(agg['venda_total'])}</div><div class="lbl">Vendas líquidas</div></div>
      <div class="stat-mini"><div class="num">{fmt_int(agg['ativos_du_total'])}</div><div class="lbl">Ativos/dia útil (soma)</div></div>
      <div class="stat-mini"><div class="num">{fmt_pct(agg['conv_prod_geral'])}</div><div class="lbl">Conversão produtiva</div></div>
      <div class="stat-mini"><div class="num">{fmt_pct(agg['conv_mail_geral'])}</div><div class="lbl">Conversão total</div></div>
    </div>"""

    # --- Conversão consolidada por parceiro --------------------------------
    itens_conv = ""
    for l in linhas_ordenadas:
        nome = l["parceiro"].title()
        itens_conv += f"""
        <div class="conv-canal-item">
          <div class="painel-icone">{nome[0]}</div>
          <div>
            <div class="num">{fmt_pct(l['conv_produtiva'])}</div>
            <div class="nome">{nome}</div>
          </div>
        </div>"""
    conv_por_parceiro = f"""
    <div class="rel-conv-canal">
      <div class="titulo">Conversão produtiva consolidada por parceiro</div>
      <div class="conv-canal-grid">{itens_conv}</div>
    </div>"""

    # --- Insights executivos (gerados a partir dos próprios dados) --------
    melhor = linhas_ordenadas[0]
    pior = linhas_ordenadas[-1]
    insights = [
        f"<span class='icone'>🏆</span><b>{melhor['parceiro'].title()}</b> lidera a conversão produtiva do período, com {fmt_pct(melhor['conv_produtiva'])} — acima da média do grupo ({fmt_pct(media_grupo)}).",
        f"<span class='icone'>⚠️</span><b>{pior['parceiro'].title()}</b> é o ponto de atenção do período, com {fmt_pct(pior['conv_produtiva'])} de conversão produtiva.",
    ]
    if mes_pendente:
        insights.append(
            f"<span class='icone'>📩</span>Mailing de <b>{mes_pendente}</b> já carregado ({fmt_int(mailing_pendente)} contatos), aguardando início da campanha."
        )
    insights.append(
        "<span class='icone'>🎯</span>Prioridade: elevar a conversão dos parceiros abaixo da média do grupo, mantendo a consistência dos que já performam acima."
    )
    insights_html = "".join(f'<div class="insight-card">{i}</div>' for i in insights)

    aviso_dados = ""
    for a, b in zip(blocos_todos, blocos_todos[1:]):
        chaves = ["mailing", "produtivo", "venda", "ativos_du"]
        iguais = all(
            all(is_blank(la.get(k)) == is_blank(lb.get(k)) and la.get(k) == lb.get(k) for k in chaves)
            for la, lb in zip(a["linhas"], b["linhas"])
        )
        if iguais and a["linhas"]:
            aviso_dados = (f" ⚠ Os dados de <b>{a['mes']}</b> e <b>{b['mes']}</b> estão idênticos na planilha original — "
                            f"confirme se a base de {b['mes']} já foi atualizada antes de divulgar.")

    footer_note = f"""
    <div class="rel-footer-note">
      <b>IMPORTANTE:</b> "Ativos por dia útil" já considera os dias úteis do período ({bloco['label_total_du']}).
      O farol (🟢🟠🔴) compara a conversão produtiva de cada parceiro com a <b>média do grupo</b> no mês,
      já que não há uma meta fixa cadastrada na planilha.{aviso_dados}
    </div>"""

    corpo = f"""
    <div class="rel-page">
      {banner}
      <div class="rel-body">
        <div class="rel-grid">{painel_html}</div>
        {consolidado}
        {conv_por_parceiro}
        <div class="rel-insights">{insights_html}</div>
      </div>
      {footer_note}
      <div class="rel-assinatura">
        <span>Gerado em {gerado_em} · vero</span>
        <img src="{logo_cor}" alt="vero" style="height:16px">
      </div>
    </div>
    <div class="links">
      {"".join(f'<a href="{href}">{nome}</a>' for nome, href in parceiro_links)}
    </div>
    """
    return tpl.render(
        titulo=f"vero · Rentabilização Parceiros Nacional — {mes}",
        descricao="Relatório consolidado de mailing, conversão produtiva e vendas dos parceiros vero.",
        corpo_html=corpo,
    )


def build_card_parceiro(linha, bloco, logo_branco, logo_cor, gerado_em, link_geral):
    mes = bloco["mes"]
    nome = linha["parceiro"].title()

    gauge = tpl.donut_svg(linha["conv_produtiva"], label_top=fmt_pct(linha["conv_produtiva"]),
                           label_bottom="Conversão Produtiva", uid=slugify(nome))

    aguardando = linha["produtivo"] is None
    aviso_html = ""
    if aguardando:
        aviso_html = """<div class="note">⏳ Campanha deste período ainda não iniciou o processamento —
        os números de conversão aparecerão aqui assim que houver contatos produtivos.</div>"""

    recusa_taxa = (linha["recusa"] / linha["produtivo"]) if (linha["produtivo"] and linha["recusa"] is not None) else None

    corpo = f"""
    <div class="card">
      <div class="header">
        <div class="top-row">
          <img class="logo" src="{logo_branco}" alt="vero">
          <span class="eyebrow">Resultados · {mes}</span>
        </div>
        <h1>Olá, {nome}!</h1>
        <p>Aqui está o resultado parcial da sua base de mailing neste período.</p>
      </div>
      <div class="hero">{gauge}</div>
      <div class="kpis">
        <div class="kpi"><div class="num">{fmt_int(linha['mailing'])}</div><div class="lbl">Total de mailing enviado</div></div>
        <div class="kpi"><div class="num">{fmt_int(linha['tentativas'])}</div><div class="lbl">Tentativas de contato</div></div>
        <div class="kpi"><div class="num">{fmt_num1(linha['media_du'])}</div><div class="lbl">Média DU (tentativas/mailing)</div></div>
        <div class="kpi"><div class="num">{fmt_int(linha['produtivo'])}</div><div class="lbl">Contatos produtivos</div></div>
        <div class="kpi"><div class="num">{fmt_int(linha['venda'])}</div><div class="lbl">Vendas realizadas</div></div>
        <div class="kpi"><div class="num">{fmt_pct(recusa_taxa)}</div><div class="lbl">Taxa de recusa</div></div>
        <div class="kpi"><div class="num">{fmt_pct(linha['conv_mailing'])}</div><div class="lbl">Conversão sobre mailing</div></div>
        <div class="kpi"><div class="num">{fmt_int(linha['ativos_du'])}</div><div class="lbl">Ativos por dia útil</div></div>
        <div class="kpi"><div class="num">{fmt_num1(linha['total_du'])}</div><div class="lbl">Projeção do mês ({bloco['label_total_du']})</div></div>
      </div>
      {aviso_html}
      <div class="footer">
        <span>Gerado em {gerado_em} · vero</span>
        <img src="{logo_cor}" alt="vero">
      </div>
    </div>
    <div class="links"><a href="{link_geral}">← Ver painel geral</a></div>
    """
    return tpl.render(
        titulo=f"vero · Resultados {nome} — {mes}",
        descricao=f"Resultado parcial de mailing e conversão produtiva de {nome} em {mes}.",
        corpo_html=corpo,
    )


# --------------------------------------------------------------------------
# CLI principal
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Gera cards de resultados dos parceiros vero.")
    ap.add_argument("planilha", nargs="?", default="dados/Rentabilização_dados.xlsx",
                     help="Caminho para o .xlsx de rentabilização (padrão: dados/Rentabilização_dados.xlsx)")
    ap.add_argument("--saida", default="site", help="Pasta de saída (padrão: site)")
    ap.add_argument("--assets", default="assets", help="Pasta com os logos vero em PNG (padrão: assets)")
    ap.add_argument("--mes", default=None, help="Mês alvo (padrão: último mês com dados de campanha)")
    args = ap.parse_args()

    caminho = Path(args.planilha)
    if not caminho.exists():
        sys.exit(f"Arquivo não encontrado: {caminho}")

    print(f"Lendo planilha: {caminho}")
    blocos = ler_blocos(caminho)
    if not blocos:
        sys.exit("Nenhum bloco de dados de parceiros encontrado na aba 'Planilha2'.")
    print(f"Meses encontrados: {[b['mes'] for b in blocos]}")

    print("\n--- Validação de 'Média DU' e 'Conversão' ---")
    avisos = validar_blocos(blocos)
    if avisos:
        for a in avisos:
            print(a)
    else:
        print("Nenhuma inconsistência encontrada. ✅")

    alvo = escolher_mes(blocos, args.mes)
    print(f"\nMês selecionado para os cards: {alvo['mes']}")

    saida = Path(args.saida)
    parceiros_dir = saida / "parceiros"
    parceiros_dir.mkdir(parents=True, exist_ok=True)

    logo_branco, logo_cor = tpl.logos_data_uri(Path(args.assets))
    gerado_em = datetime.now().strftime("%d/%m/%Y %H:%M")

    parceiro_links = []
    for l in alvo["linhas"]:
        slug = slugify(l["parceiro"])
        parceiro_links.append((l["parceiro"].title(), f"parceiros/{slug}.html"))

    for l in alvo["linhas"]:
        slug = slugify(l["parceiro"])
        html_parceiro = build_card_parceiro(l, alvo, logo_branco, logo_cor, gerado_em, link_geral="../index.html")
        (parceiros_dir / f"{slug}.html").write_text(html_parceiro, encoding="utf-8")

    html_geral = build_card_geral(alvo, blocos, logo_branco, logo_cor, gerado_em, parceiro_links)
    (saida / "index.html").write_text(html_geral, encoding="utf-8")

    print(f"\nCards gerados em: {saida}/")
    print(f"  - {saida}/index.html  (card geral)")
    for nome, href in parceiro_links:
        print(f"  - {saida}/{href}  ({nome})")


if __name__ == "__main__":
    main()
