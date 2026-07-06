"""Templates HTML/SVG para os cards vero (card geral + cards por parceiro)."""
import base64
import math
from pathlib import Path

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


def _b64(path: Path) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode()


def logos_data_uri(assets_dir: Path):
    branco = f"data:image/png;base64,{_b64(assets_dir / 'vero_logo_branco.png')}"
    colorido = f"data:image/png;base64,{_b64(assets_dir / 'vero_logo.png')}"
    return branco, colorido


def donut_svg(pct, size=176, stroke=16, label_top="", label_bottom="Conversão Produtiva", uid="g1"):
    pct = 0 if pct is None else max(0, min(pct, 1))
    r = (size - stroke) / 2
    c = 2 * math.pi * r
    dash = c * pct
    cx = cy = size / 2
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" class="gauge">
      <defs>
        <linearGradient id="grad-{uid}" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="{CORES['laranja']}"/>
          <stop offset="100%" stop-color="{CORES['amarelo']}"/>
        </linearGradient>
      </defs>
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{CORES['cinza2']}" stroke-width="{stroke}"/>
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#grad-{uid})" stroke-width="{stroke}"
              stroke-linecap="round" stroke-dasharray="{dash:.2f} {c:.2f}"
              transform="rotate(-90 {cx} {cy})"/>
      <text x="{cx}" y="{cy - 6}" text-anchor="middle" class="gauge-num">{label_top}</text>
      <text x="{cx}" y="{cy + 22}" text-anchor="middle" class="gauge-sub">{label_bottom}</text>
    </svg>
    """


def mini_bar(pct, cor=CORES["rosa"]):
    pct = 0 if pct is None else max(0, min(pct, 1))
    largura = max(pct * 100, 2)
    return f"""
    <div class="bar-track">
      <div class="bar-fill" style="width:{largura:.1f}%; background:linear-gradient(90deg,{CORES['rosa']},{cor})"></div>
    </div>
    """


BADGE_TIPOS = {
    "verde":   {"bg": "#E1F5EE", "fg": "#0F6E56"},
    "laranja": {"bg": "#FFF3E0", "fg": "#B45309"},
    "vermelho":{"bg": "#FDEBEA", "fg": "#B3261E"},
    "rosa":    {"bg": "#FFE9F0", "fg": CORES["bordo_escuro"]},
    "cinza":   {"bg": CORES["cinza1"], "fg": CORES["grafite"]},
}


def badge(valor, label, tipo="cinza"):
    cores = BADGE_TIPOS.get(tipo, BADGE_TIPOS["cinza"])
    return f"""
    <div class="badge" style="background:{cores['bg']}">
      <div class="badge-num" style="color:{cores['fg']}">{valor}</div>
      <div class="badge-lbl">{label}</div>
    </div>"""


def barra_com_marcador(pct, marcador_pct, cor_barra=None):
    """Barra horizontal 0-130% com um marcador vertical numa posição de
    referência (ex: média do grupo). A barra pode ultrapassar o marcador."""
    escala = 1.3  # a barra representa de 0% a 130%
    pct_visivel = max(0, min(pct if pct is not None else 0, escala))
    largura = min(pct_visivel / escala * 100, 100)
    marcador_pos = min(max((marcador_pct or 0) / escala, 0), 1) * 100
    cor_barra = cor_barra or CORES["rosa"]
    return f"""
    <div class="barra-wrap">
      <div class="barra-track">
        <div class="barra-fill" style="width:{largura:.1f}%; background:linear-gradient(90deg,{CORES['rosa']},{cor_barra})"></div>
        <div class="barra-marcador" style="left:{marcador_pos:.1f}%"></div>
      </div>
    </div>"""


BASE_CSS = f"""
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  font-family: 'Inter', -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  background: {CORES['cinza1']};
  color: {CORES['grafite']};
  padding: 32px 12px;
}}
.card {{
  max-width: 440px;
  margin: 0 auto;
  background: #fff;
  border-radius: 22px;
  overflow: hidden;
  box-shadow: 0 18px 40px rgba(146, 0, 38, 0.16);
}}
.header {{
  background: linear-gradient(135deg, {CORES['rosa']} 0%, {CORES['bordo']} 55%, {CORES['bordo_escuro']} 100%);
  padding: 22px 24px 26px;
  color: #fff;
  position: relative;
}}
.header .top-row {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}}
.header img.logo {{ height: 26px; display:block; }}
.eyebrow {{
  font-family: 'Poppins', sans-serif;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .06em;
  background: rgba(255,255,255,0.18);
  padding: 6px 12px;
  border-radius: 999px;
  text-transform: uppercase;
}}
.header h1 {{
  font-family: 'Poppins', sans-serif;
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 4px;
  line-height: 1.25;
}}
.header p {{
  margin: 0;
  font-size: 13.5px;
  color: rgba(255,255,255,0.88);
  line-height: 1.5;
}}
.hero {{
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 28px 24px 8px;
}}
.gauge-num {{
  font-family: 'Poppins', sans-serif;
  font-size: 30px;
  font-weight: 700;
  fill: {CORES['bordo_escuro']};
}}
.gauge-sub {{
  font-family: 'Inter', sans-serif;
  font-size: 11.5px;
  fill: {CORES['cinza3']};
  text-transform: uppercase;
  letter-spacing: .04em;
}}
.kpis {{
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
  padding: 12px 24px 6px;
}}
.kpi {{
  background: {CORES['cinza1']};
  border-radius: 14px;
  padding: 14px 14px;
}}
.kpi .num {{
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  font-size: 19px;
  color: {CORES['bordo_escuro']};
}}
.kpi .lbl {{
  font-size: 11px;
  color: {CORES['grafite']};
  margin-top: 2px;
  line-height: 1.35;
}}
.section-title {{
  font-family: 'Poppins', sans-serif;
  font-size: 13px;
  font-weight: 600;
  color: {CORES['grafite']};
  text-transform: uppercase;
  letter-spacing: .04em;
  padding: 18px 24px 6px;
}}
.partner-row {{
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 24px;
}}
.partner-row .name {{
  width: 128px;
  flex-shrink: 0;
  font-size: 12.5px;
  font-weight: 600;
  color: {CORES['grafite']};
}}
.bar-track {{
  flex: 1;
  background: {CORES['cinza2']};
  border-radius: 999px;
  height: 10px;
  overflow: hidden;
}}
.bar-fill {{
  height: 100%;
  border-radius: 999px;
}}
.partner-row .pct {{
  width: 52px;
  text-align: right;
  font-size: 12.5px;
  font-weight: 700;
  color: {CORES['bordo_escuro']};
}}
.note {{
  margin: 14px 24px 4px;
  background: #FFF7EA;
  border: 1px solid {CORES['amarelo']}55;
  border-radius: 12px;
  padding: 10px 14px;
  font-size: 12px;
  color: {CORES['grafite']};
  line-height: 1.5;
}}
.footer {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  margin-top: 10px;
  background: {CORES['grafite']};
  color: rgba(255,255,255,0.85);
  font-size: 11px;
}}
.footer img {{ height: 16px; opacity: .95; }}
.links {{
  max-width: 440px;
  margin: 18px auto 0;
  text-align: center;
}}
.links a {{
  display: inline-block;
  margin: 4px 6px;
  font-size: 12.5px;
  color: {CORES['bordo_escuro']};
  text-decoration: none;
  border: 1px solid {CORES['cinza2']};
  padding: 6px 12px;
  border-radius: 999px;
}}
.links a:hover {{ background: {CORES['cinza1']}; }}
@media (max-width: 380px) {{
  .kpis {{ grid-template-columns: 1fr 1fr; }}
}}

/* --- Ranking / desempenho por parceiro --- */
.rank-card {{
  max-width: 640px;
  margin: 0 auto;
  background: #fff;
  border-radius: 22px;
  overflow: hidden;
  box-shadow: 0 18px 40px rgba(146, 0, 38, 0.14);
}}
.rank-header {{
  padding: 20px 26px;
  background: linear-gradient(135deg, {CORES['rosa']} 0%, {CORES['bordo']} 60%, {CORES['bordo_escuro']} 100%);
  color: #fff;
}}
.rank-header-top {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}}
.rank-header img.logo {{ height: 24px; display: block; }}
.rank-header .title-group h1 {{
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  font-size: 20px;
  margin: 0 0 4px;
}}
.rank-header .title-group p {{
  margin: 0;
  font-size: 12px;
  color: rgba(255,255,255,0.85);
}}
.rank-header .eyebrow {{
  font-family: 'Poppins', sans-serif;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .05em;
  background: rgba(255,255,255,0.18);
  padding: 6px 12px;
  border-radius: 999px;
  text-transform: uppercase;
}}
.legenda {{
  padding: 10px 26px;
  font-size: 11px;
  color: {CORES['cinza3']};
  background: {CORES['cinza1']};
  border-bottom: 1px solid {CORES['cinza2']};
}}
.parceiro-block {{
  margin: 18px 20px;
  background: #fff;
  border: 1px solid {CORES['cinza2']};
  border-radius: 16px;
  padding: 18px 20px 16px;
}}
.parceiro-top {{
  display: flex;
  align-items: flex-start;
  gap: 14px;
}}
.rank-num {{
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 2px solid {CORES['rosa']};
  color: {CORES['bordo_escuro']};
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
}}
.parceiro-nome-linha {{
  flex: 1;
  min-width: 0;
}}
.parceiro-nome-linha .nome {{
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  font-size: 15px;
  color: {CORES['bordo_escuro']};
  letter-spacing: .01em;
}}
.parceiro-nome-linha .contexto {{
  font-size: 11.5px;
  color: {CORES['cinza3']};
  margin-top: 2px;
}}
.parceiro-headline {{
  text-align: right;
  flex-shrink: 0;
}}
.parceiro-headline .num {{
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  font-size: 20px;
  color: {CORES['bordo_escuro']};
  line-height: 1.1;
}}
.parceiro-headline .lbl {{
  font-size: 10px;
  color: {CORES['cinza3']};
  text-transform: uppercase;
  letter-spacing: .04em;
}}
.barra-wrap {{ margin: 12px 0 4px; }}
.barra-track {{
  position: relative;
  height: 12px;
  background: {CORES['cinza2']};
  border-radius: 999px;
  overflow: visible;
}}
.barra-fill {{
  position: absolute;
  left: 0; top: 0; bottom: 0;
  border-radius: 999px;
}}
.barra-marcador {{
  position: absolute;
  top: -3px;
  bottom: -3px;
  width: 2px;
  background: {CORES['grafite']};
}}
.pills-grid {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-top: 14px;
}}
.badge {{
  border-radius: 10px;
  padding: 8px 6px;
  text-align: center;
}}
.badge-num {{
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  font-size: 13.5px;
}}
.badge-lbl {{
  font-size: 9px;
  color: {CORES['grafite']};
  text-transform: uppercase;
  letter-spacing: .02em;
  margin-top: 1px;
  line-height: 1.2;
}}
.parceiro-block.consolidado {{
  border: 2px solid {CORES['bordo']};
  background: linear-gradient(180deg, #FFF5F8 0%, #ffffff 65%);
}}
.rank-num.total {{
  border-color: {CORES['bordo']};
  background: {CORES['bordo']};
  color: #fff;
  font-size: 15px;
}}
.section-divider {{
  margin: 20px 20px 0;
  font-family: 'Poppins', sans-serif;
  font-size: 11px;
  font-weight: 600;
  color: {CORES['cinza3']};
  text-transform: uppercase;
  letter-spacing: .06em;
  border-top: 1px dashed {CORES['cinza2']};
  padding-top: 14px;
}}
@media (max-width: 480px) {{
  .pills-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
"""

HTML_SHELL = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descricao}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
{corpo}
</body>
</html>
"""


def render(titulo, descricao, corpo_html, css=BASE_CSS):
    return HTML_SHELL.format(titulo=titulo, descricao=descricao, corpo=corpo_html, css=css)
