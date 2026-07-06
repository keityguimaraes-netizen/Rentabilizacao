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


def foto_informativo_data_uri(assets_dir: Path):
    caminho = assets_dir / "foto_informativo.png"
    if not caminho.exists():
        return None
    return f"data:image/png;base64,{_b64(caminho)}"


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


def deco_header_extras(foto_uri, wave_fill):
    if not foto_uri:
        foto_html = ""
    else:
        foto_html = f'<div class="deco-photo" style="background-image:url(\'{foto_uri}\')"></div>'
    wave = f"""
    <svg class="deco-wave" viewBox="0 0 1440 60" preserveAspectRatio="none">
      <path d="M0,40 C360,5 1080,70 1440,15 L1440,60 L0,60 Z" fill="{wave_fill}"/>
    </svg>"""
    return f"""
    <div class="deco-circle orange"></div>
    <div class="deco-circle ring"></div>
    <div class="deco-circle big-bordo"></div>
    {foto_html}
    {wave}"""


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

/* ======================================================================
   Relatório — visual denso estilo "Acompanhamento Evolutivo" (referência)
   ====================================================================== */
.rel-page {{
  max-width: 1180px;
  margin: 0 auto;
  background: {CORES['cinza1']};
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 22px 50px rgba(146,0,38,0.18);
}}
.rel-banner {{
  background: linear-gradient(120deg, {CORES['rosa']} 0%, {CORES['bordo']} 55%, {CORES['bordo_escuro']} 100%);
  color: #fff;
  padding: 28px 34px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}}
.rel-banner .brand {{ display:flex; align-items:center; gap:14px; }}
.rel-banner img.logo {{ height: 30px; }}
.rel-banner .titles {{ max-width: 560px; }}
.rel-banner .tag {{
  display:inline-block;
  font-family:'Poppins',sans-serif;
  font-size:10.5px;
  font-weight:600;
  letter-spacing:.08em;
  text-transform:uppercase;
  background:rgba(255,255,255,0.18);
  padding:4px 10px;
  border-radius:999px;
  margin-bottom:10px;
}}
.rel-banner h1 {{
  font-family:'Poppins',sans-serif;
  font-weight:700;
  font-size:22px;
  letter-spacing:.01em;
  margin:0 0 6px;
  line-height:1.3;
}}
.rel-banner p {{
  margin:0;
  font-size:12.5px;
  color:rgba(255,255,255,0.88);
  line-height:1.5;
}}
.rel-banner .meta-boxes {{ display:flex; gap:12px; flex-wrap:wrap; }}
.meta-box {{
  background:#fff;
  border-radius:14px;
  padding:12px 20px;
  text-align:center;
  min-width:130px;
}}
.meta-box .valor {{
  font-family:'Poppins',sans-serif;
  font-weight:700;
  font-size:24px;
  color:{CORES['bordo_escuro']};
}}
.meta-box .lbl {{
  font-size:10px;
  color:{CORES['cinza3']};
  text-transform:uppercase;
  letter-spacing:.05em;
  margin-top:2px;
}}
.rel-body {{ padding: 26px 30px 8px; }}
.rel-grid {{
  display:grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap:18px;
  margin-bottom: 6px;
}}
.painel {{
  background:#fff;
  border-radius:16px;
  padding:16px 18px 18px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}}
.painel-head {{
  display:flex;
  align-items:center;
  gap:10px;
  margin-bottom:10px;
}}
.painel-icone {{
  width:34px; height:34px;
  border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  font-family:'Poppins',sans-serif;
  font-weight:700;
  font-size:14px;
  color:#fff;
  background:linear-gradient(135deg,{CORES['rosa']},{CORES['laranja']});
  flex-shrink:0;
}}
.painel-nome {{
  font-family:'Poppins',sans-serif;
  font-weight:700;
  font-size:14.5px;
  color:{CORES['bordo_escuro']};
  flex:1;
}}
.farol {{
  width:12px; height:12px;
  border-radius:50%;
  flex-shrink:0;
}}
.farol.verde {{ background:#1D9E75; }}
.farol.laranja {{ background:{CORES['laranja']}; }}
.farol.vermelho {{ background:#D6473C; }}
table.evolutivo {{
  width:100%;
  border-collapse: collapse;
  font-size:12px;
  margin-bottom:12px;
}}
table.evolutivo th {{
  text-align:left;
  font-family:'Poppins',sans-serif;
  font-size:9.5px;
  color:{CORES['cinza3']};
  text-transform:uppercase;
  letter-spacing:.04em;
  padding:4px 4px 6px;
  border-bottom:1px solid {CORES['cinza2']};
}}
table.evolutivo td {{
  padding:6px 4px;
  border-bottom:1px solid {CORES['cinza1']};
  color:{CORES['grafite']};
}}
table.evolutivo td.conv {{ font-weight:700; }}
table.evolutivo td.conv.verde {{ color:#1D9E75; }}
table.evolutivo td.conv.laranja {{ color:{CORES['bordo']}; }}
table.evolutivo td.conv.vermelho {{ color:#D6473C; }}
table.evolutivo tr.pendente td {{ color:{CORES['cinza3']}; font-style:italic; }}
.callout {{
  background:#FFEFF3;
  border-radius:12px;
  padding:12px 14px;
  display:flex;
  align-items:center;
  gap:12px;
}}
.callout .num {{
  font-family:'Poppins',sans-serif;
  font-weight:700;
  font-size:20px;
  color:{CORES['bordo_escuro']};
}}
.callout .txt {{ font-size:10.5px; color:{CORES['grafite']}; line-height:1.35; }}
.callout .txt b {{ display:block; font-size:9.5px; text-transform:uppercase; color:{CORES['cinza3']}; letter-spacing:.03em; }}
.icon-btn {{
  width: 30px;
  height: 30px;
  border-radius: 10px;
  background: #FFE9F0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background .15s ease;
}}
.icon-btn:hover {{ background: #FFD3E1; }}

.rel-consolidado {{
  margin: 22px 0 6px;
  background:#fff;
  border-radius:16px;
  padding:16px 22px;
  display:flex;
  flex-wrap:wrap;
  gap:18px;
  align-items:center;
  box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}}
.rel-consolidado .rotulo {{
  font-family:'Poppins',sans-serif;
  font-weight:700;
  font-size:13px;
  color:{CORES['bordo_escuro']};
  min-width:150px;
}}
.rel-consolidado .rotulo small {{
  display:block;
  font-weight:400;
  font-size:10.5px;
  color:{CORES['cinza3']};
  margin-top:2px;
}}
.stat-mini {{ text-align:center; }}
.stat-mini .num {{
  font-family:'Poppins',sans-serif;
  font-weight:700;
  font-size:18px;
  color:{CORES['bordo_escuro']};
}}
.stat-mini .lbl {{
  font-size:10px;
  color:{CORES['cinza3']};
  text-transform:uppercase;
  letter-spacing:.04em;
}}

.rel-conv-canal {{
  margin: 18px 0 6px;
  background:#fff;
  border-radius:16px;
  padding:16px 22px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}}
.rel-conv-canal .titulo {{
  font-family:'Poppins',sans-serif;
  font-weight:700;
  font-size:11.5px;
  color:{CORES['grafite']};
  text-transform:uppercase;
  letter-spacing:.04em;
  margin-bottom:12px;
}}
.conv-canal-grid {{
  display:grid;
  grid-template-columns: repeat(auto-fit, minmax(140px,1fr));
  gap:14px;
}}
.conv-canal-item {{ display:flex; align-items:center; gap:10px; }}
.conv-canal-item .painel-icone {{ width:40px; height:40px; font-size:16px; }}
.conv-canal-item .num {{
  font-family:'Poppins',sans-serif;
  font-weight:700;
  font-size:19px;
  color:{CORES['bordo_escuro']};
}}
.conv-canal-item .nome {{ font-size:10.5px; color:{CORES['cinza3']}; text-transform:uppercase; letter-spacing:.03em; }}

.rel-insights {{
  margin: 18px 0 22px;
  display:grid;
  grid-template-columns: repeat(auto-fit, minmax(220px,1fr));
  gap:14px;
}}
.insight-card {{
  background:#fff;
  border-radius:14px;
  padding:14px 16px;
  font-size:12px;
  color:{CORES['grafite']};
  line-height:1.5;
  box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}}
.insight-card .icone {{ font-size:16px; margin-bottom:6px; display:block; }}
.rel-footer-note {{
  background: {CORES['bordo_escuro']};
  color: rgba(255,255,255,0.92);
  padding: 14px 30px;
  font-size:11.5px;
  line-height:1.6;
}}
.rel-footer-note b {{ color:#fff; }}
.rel-assinatura {{
  display:flex; align-items:center; justify-content:space-between;
  padding: 12px 30px 20px;
  font-size:11px;
  color:{CORES['cinza3']};
}}
@media (max-width: 640px) {{
  .rel-banner {{ flex-direction:column; align-items:flex-start; }}
  .rel-consolidado {{ flex-direction:column; align-items:flex-start; }}
}}

/* ======================================================================
   Cabeçalho decorativo (círculos + foto + onda) — estilo "Informativo GDC"
   ====================================================================== */
.deco-header {{
  position: relative;
  overflow: hidden;
  padding-bottom: 34px !important;
}}
.rel-banner.deco-header {{
  padding-top: 44px !important;
}}
.header.deco-header {{
  padding-top: 38px !important;
}}
.deco-circle {{
  position: absolute;
  border-radius: 50%;
}}
.deco-circle.orange {{
  width: 46px; height: 46px;
  background: {CORES['laranja']};
  top: 14px; left: 18px;
  opacity: 0.9;
}}
.deco-circle.ring {{
  width: 30px; height: 30px;
  border: 2.5px solid rgba(255,255,255,0.85);
  top: 30px; left: 40px;
}}
.deco-circle.big-bordo {{
  width: 150px; height: 150px;
  background: rgba(146,0,38,0.35);
  top: -55px; right: 90px;
}}
.deco-photo {{
  position: absolute;
  top: 10px;
  right: 22px;
  width: 92px;
  height: 92px;
  border-radius: 50%;
  border: 3px solid rgba(255,255,255,0.9);
  background-size: cover;
  background-position: center;
  box-shadow: 0 6px 18px rgba(0,0,0,0.18);
}}
.deco-wave {{
  position: absolute;
  left: 0; right: 0; bottom: -1px;
  width: 100%;
  height: 34px;
  display: block;
}}
@media (max-width: 480px) {{
  .deco-photo {{ width: 64px; height: 64px; }}
  .deco-circle.big-bordo {{ display: none; }}
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
