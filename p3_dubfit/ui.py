"""Page styling for the Dub-Fit app: embedded fonts, colours, layout, and the fit meter."""
import base64
from html import escape
from pathlib import Path
import streamlit as st

FONTS = Path(__file__).parent / "fonts"


def _face(family, file, weight, extra=""):
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:normal;font-display:swap;{extra}"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');}}")


def html(s):
    """Render raw HTML. Lines are stripped so Markdown never turns indented HTML into a code block."""
    st.markdown("".join(line.strip() for line in s.splitlines()), unsafe_allow_html=True)


def meter(slot, syllables, max_rate, label=""):
    """The fit meter: the box is the shot's time slot; the bar is the time the line needs at max comfortable pace."""
    need = syllables / max_rate if max_rate else 0
    scale = max(slot, need) * 1.12 or 1
    box, fit = 100 * slot / scale, 100 * min(need, slot) / scale
    over = 100 * max(0, need - slot) / scale
    state = "over" if need >= slot else "tight" if need > 0.85 * slot else "fit"
    note = (f"{need - slot:.1f} s too long" if need - slot >= 0.05 else "no time to spare" if state == "over"
            else f"{slot - need:.1f} s to spare")
    return (f'<div class="df-meter {state}" aria-label="{escape(label)} needs {need:.1f} of {slot:.1f} seconds">'
            f'<div class="slot" style="width:{box:.1f}%"></div><div class="bar" style="width:calc({fit:.1f}% - 8px)"></div>'
            f'<div class="spill" style="left:{box:.1f}%;width:{over:.1f}%"></div></div>'
            f'<div class="df-mnote"><span>{escape(label)}</span><span>{need:.1f} s needed of {slot:.1f} s, {note}</span></div>')


CSS = """
:root{--paper:#F4F6F7;--white:#FFFFFF;--ink:#14212B;--muted:#5E6B75;--rule:#D9E0E5;--cobalt:#2B45C9;
--fit:#1E8F62;--tight:#C98A12;--over:#CF3F3F;--sans:'Archivo','Noto Devanagari',system-ui,sans-serif}
.stApp{background:var(--paper)}
header[data-testid="stHeader"],#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stDecoration"],.stDeployButton{display:none!important}
[data-testid="stMainBlockContainer"],.block-container{max-width:1120px;padding:0 32px 64px 32px!important}
html,body,.stApp,p,li,label,input,textarea,select,button p,[data-testid="stMarkdownContainer"],[data-testid="stWidgetLabel"] p{
font-family:var(--sans)!important;color:var(--ink);font-variation-settings:"wdth" 100}
p,li{font-size:16px;line-height:1.55}
.df-wide{font-variation-settings:"wdth" 125!important}

.df-nav{display:flex;justify-content:space-between;align-items:center;padding:26px 0 22px;border-bottom:2px solid var(--ink)}
.df-mark{font-weight:800;font-size:22px;font-variation-settings:"wdth" 125;color:var(--ink);display:flex;align-items:center;gap:10px}
.df-mark svg{display:block}
.df-nav a{color:var(--ink)!important;text-decoration:none;font-size:15px;margin-left:28px}
.df-nav a:hover{color:var(--cobalt)!important;text-decoration:underline}
.df-hero{display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:center;padding:72px 0 64px;border-bottom:1px solid var(--rule)}
.df-hero h1{font-family:var(--sans)!important;font-weight:800!important;font-size:68px!important;line-height:1!important;
font-variation-settings:"wdth" 125;letter-spacing:-1.5px;margin:0 0 22px!important;padding:0!important;color:var(--ink)!important}
.df-hero p{font-size:19px;line-height:1.5;color:var(--muted);max-width:30em;margin:0}
.df-demo{background:var(--white);border:1px solid var(--rule);border-radius:6px;padding:28px 28px 22px}
.df-demo .en{font-size:15px;color:var(--muted);margin-bottom:18px}
.df-demo .en b{color:var(--ink);font-size:20px;display:block;font-weight:600;margin-top:2px}
.df-line{font-family:'Noto Devanagari',var(--sans);font-size:21px;margin:16px 0 8px}
@media(max-width:860px){.df-hero{grid-template-columns:1fr}.df-hero h1{font-size:48px!important}}
@media(max-width:600px){.df-nav>div:last-child{display:none}.df-hero{padding:40px 0 48px;gap:36px}.df-hero h1{font-size:40px!important}}
.df-mark{white-space:nowrap}

.df-meter{position:relative;height:22px;background:transparent}
.df-meter .slot{position:absolute;top:0;left:0;height:22px;border:2px solid var(--ink);border-radius:3px;box-sizing:border-box;background:repeating-linear-gradient(90deg,transparent 0 9px,#E8EDF0 9px 10px)}
.df-meter .bar{position:absolute;top:5px;left:4px;height:12px;border-radius:2px;background:var(--fit);max-width:calc(100% - 4px)}
.df-meter.tight .bar{background:var(--tight)}
.df-meter.over .bar{background:var(--over)}
.df-meter .spill{position:absolute;top:5px;height:12px;background:repeating-linear-gradient(135deg,var(--over) 0 5px,#F1B5B5 5px 9px);border-radius:0 2px 2px 0}
.df-mnote{display:flex;justify-content:space-between;gap:12px;font-size:13px;color:var(--muted);margin:6px 0 4px;font-variant-numeric:tabular-nums}

.df-h2 h2{font-family:var(--sans)!important;font-weight:800!important;font-size:36px!important;line-height:1.05!important;font-variation-settings:"wdth" 125;
letter-spacing:-.8px;margin:56px 0 8px!important;padding:0!important;color:var(--ink)!important}
.df-lede{color:var(--muted);margin:0 0 20px!important;max-width:42em}

[data-testid="stFileUploaderDropzone"]{background:var(--white);border:1.5px dashed #AEBBC4;border-radius:6px;padding:22px}
[data-testid="stBaseButton-primary"]{background:var(--cobalt)!important;border:0!important;border-radius:6px!important;padding:12px 26px!important}
[data-testid="stBaseButton-primary"] p{color:#fff!important;font-weight:600!important;font-size:16px!important}
[data-testid="stBaseButton-primary"]:hover{background:#1F35A6!important}
[data-testid="stBaseButton-secondary"]{border-radius:6px!important;border:1px solid #AEBBC4!important;background:var(--white)!important}
:focus-visible{outline:3px solid var(--cobalt)!important;outline-offset:2px}

.df-split{display:flex;height:34px;border-radius:4px;overflow:hidden;margin:8px 0 10px}
.df-split div{display:flex;align-items:center;padding-left:10px;color:#fff;font-size:14px;font-weight:600;white-space:nowrap;overflow:hidden}
.df-keys{display:flex;flex-wrap:wrap;gap:24px;font-size:15px;color:var(--ink);margin-bottom:8px}
.df-keys i{display:inline-block;width:12px;height:12px;border-radius:2px;margin-right:8px;vertical-align:-1px}
.df-sum{font-size:20px;line-height:1.5;margin:8px 0 18px!important;max-width:44em}

.df-item{display:grid;grid-template-columns:150px 1fr;gap:28px;padding:24px 0;border-top:1px solid var(--rule)}
.df-id{font-variant-numeric:tabular-nums}
.df-id b{display:block;font-size:17px;font-variation-settings:"wdth" 112}
.df-id span{display:block;color:var(--muted);font-size:14px;margin-top:2px}
.df-id .df-tag{display:inline-block!important;margin-top:10px;border-radius:3px;padding:2px 9px;font-size:13px;font-weight:600;color:#fff!important}
.df-en{font-size:17px;margin:0 0 10px}
.df-tr{font-family:'Noto Devanagari',var(--sans);font-size:18px;margin:14px 0 6px}
.df-tr small{display:block;font-family:var(--sans);color:var(--muted);font-size:13px;margin-bottom:2px}
@media(max-width:700px){.df-item{grid-template-columns:1fr;gap:8px}}

.df-steps{display:grid;grid-template-columns:repeat(4,1fr);gap:28px}
.df-steps div{border-top:2px solid var(--ink);padding-top:14px}
.df-steps b{display:block;font-size:18px;font-variation-settings:"wdth" 118;margin-bottom:6px}
.df-steps p{color:var(--muted);font-size:15px;margin:0}
@media(max-width:860px){.df-steps{grid-template-columns:1fr 1fr}}
.df-foot{margin-top:64px;padding-top:20px;border-top:1px solid var(--rule);color:var(--muted);font-size:14px}
.df-foot a{color:var(--cobalt)}
"""


def inject():
    faces = (_face("Archivo", "archivo-latin-wdth-normal.woff2", "100 900", "font-stretch:62% 125%;") +
             _face("Noto Devanagari", "noto-sans-devanagari-devanagari-400-normal.woff2", 400) +
             _face("Noto Devanagari", "noto-sans-devanagari-devanagari-600-normal.woff2", 600))
    st.markdown(f"<style>{faces}{CSS}</style>", unsafe_allow_html=True)
