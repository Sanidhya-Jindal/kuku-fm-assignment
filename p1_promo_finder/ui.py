"""Page styling for the Promo Finder app: embedded fonts, colours and layout."""
import base64
from pathlib import Path
import streamlit as st

FONTS = Path(__file__).parent / "fonts"


def _face(family, file, weight):
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:normal;font-display:swap;"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');}}")


def html(s):
    """Render raw HTML. Lines are stripped so Markdown never turns indented HTML into a code block."""
    st.markdown("".join(line.strip() for line in s.splitlines()), unsafe_allow_html=True)


CSS = """
:root{--plum:#2A1225;--mist:#F5F2F6;--paper:#FFFFFF;--ink:#221A24;--muted:#6E6472;--rule:#E3DCE5;
--hook:#CC2E64;--cliff:#12867F;--display:'Big Shoulders',Impact,sans-serif;--body:'Schibsted',system-ui,sans-serif}
.stApp{background:var(--mist)}
header[data-testid="stHeader"],#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stDecoration"],.stDeployButton{display:none!important}
[data-testid="stMainBlockContainer"],.block-container{max-width:1120px;padding:0 32px 64px 32px!important}
html,body,.stApp,p,li,label,input,textarea,select,button p,[data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"] p{font-family:var(--body)!important;color:var(--ink)}
p,li{font-size:16px;line-height:1.55}

/* top bar + hero: full-bleed plum band */
.pf-band{background:var(--plum);width:100vw;margin-left:calc(50% - 50vw);margin-top:-1rem;padding:0 calc(50vw - 528px)}
@media(max-width:1120px){.pf-band{padding:0 32px}}
.pf-nav{display:flex;justify-content:space-between;align-items:center;padding:22px 0;border-bottom:1px solid rgba(255,255,255,.12)}
.pf-mark{font-family:var(--display);font-weight:800;font-size:26px;letter-spacing:.5px;color:#fff}
.pf-mark span{display:inline-block;width:9px;height:20px;background:var(--hook);margin-right:9px;vertical-align:-2px;border-radius:2px}
.pf-nav a{color:#E9DDE8!important;text-decoration:none;font-size:15px;margin-left:28px}
.pf-nav a:hover{color:#fff!important;text-decoration:underline}
.pf-hero{display:grid;grid-template-columns:1.35fr .65fr;gap:56px;align-items:center;padding:64px 0 72px}
.pf-hero h1{font-family:var(--display)!important;font-weight:800!important;font-size:88px!important;line-height:.92!important;color:#fff!important;margin:0 0 24px!important;padding:0!important;letter-spacing:-.5px}
.pf-hero p{color:#E3D3E0;font-size:19px;line-height:1.5;max-width:34em;margin:0}
.pf-legend{display:flex;gap:28px;margin-top:28px;color:#E3D3E0;font-size:15px}
.pf-legend i{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:8px;vertical-align:-1px}
.pf-phone{justify-self:end}
@media(max-width:820px){.pf-hero{grid-template-columns:1fr}.pf-hero h1{font-size:64px!important}.pf-phone{justify-self:start}}
@media(max-width:600px){.pf-nav>div:last-child{display:none}.pf-hero{padding:40px 0 48px}.pf-hero h1{font-size:52px!important}.pf-phone{display:none}}
.pf-mark{white-space:nowrap}

/* sections */
.pf-h2 h2{font-family:var(--display)!important;font-weight:700!important;font-size:44px!important;line-height:1!important;margin:56px 0 8px!important;padding:0!important;color:var(--plum)!important;letter-spacing:0!important}
.pf-lede{color:var(--muted);margin:0 0 20px;max-width:40em}

/* widgets */
[data-testid="stFileUploaderDropzone"]{background:var(--paper);border:1.5px dashed #CDBFD0;border-radius:14px;padding:22px}
[data-testid="stRadio"] label p{font-size:15px}
[data-testid="stBaseButton-primary"],.stButton button[kind="primary"]{background:var(--hook)!important;border:0!important;border-radius:10px!important;
padding:12px 26px!important;font-weight:600!important;color:#fff!important}
[data-testid="stBaseButton-primary"] p{color:#fff!important;font-size:16px!important}
[data-testid="stBaseButton-primary"]:hover{background:#B02455!important}
[data-testid="stBaseButton-secondary"]{border-radius:10px!important;border:1px solid #CDBFD0!important;background:var(--paper)!important}
[data-testid="stTextInput"] input{border-radius:8px}
:focus-visible{outline:3px solid var(--hook)!important;outline-offset:2px}

/* results */
.pf-summary{font-size:20px;line-height:1.5;margin:8px 0 28px;max-width:44em}
.pf-summary b{color:var(--plum)}
.pf-row{display:grid;grid-template-columns:92px 1fr;gap:24px;padding:28px 0;border-top:1px solid var(--rule)}
.pf-rank{font-family:var(--display);font-weight:800;font-size:72px;line-height:.8;color:var(--plum)}
.pf-row h3{font-family:var(--body)!important;font-size:21px!important;font-weight:700!important;margin:0 0 4px!important;padding:0!important;color:var(--ink)!important}
.pf-meta{color:var(--muted);font-size:15px;margin-bottom:14px}
.pf-tl{position:relative;height:30px;margin:6px 0 4px}
.pf-tl .ep{position:absolute;top:13px;left:0;right:0;height:4px;background:#E6DEE8;border-radius:2px}
.pf-tl .cut{position:absolute;top:7px;height:16px;background:var(--plum);border-radius:4px;opacity:.92}
.pf-tl .h,.pf-tl .c{position:absolute;top:0;width:4px;height:30px;border-radius:2px}
.pf-tl .h{background:var(--hook)}.pf-tl .c{background:var(--cliff)}
.pf-scale{display:flex;justify-content:space-between;color:var(--muted);font-size:13px;margin-bottom:16px}
.pf-pair{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.pf-q{border-left:4px solid var(--hook);padding:2px 0 2px 14px}
.pf-q.c{border-color:var(--cliff)}
.pf-q small{display:block;color:var(--muted);font-size:13px;margin-bottom:3px}
.pf-q div{font-size:16px;line-height:1.45}
.pf-why{margin:18px 0 0!important;font-size:16px}
.pf-chip{display:inline-block;background:#F3E6EC;color:#8A1E44;border-radius:999px;padding:3px 12px;font-size:13px;margin:10px 8px 0 0}
@media(max-width:700px){.pf-pair{grid-template-columns:1fr}.pf-row{grid-template-columns:56px 1fr}.pf-rank{font-size:48px}}

.pf-steps{display:grid;grid-template-columns:repeat(4,1fr);gap:28px;margin-top:8px}
.pf-steps div{border-top:3px solid var(--plum);padding-top:14px}
.pf-steps b{font-family:var(--display);font-size:24px;display:block;margin-bottom:6px;color:var(--plum)}
.pf-steps p{color:var(--muted);font-size:15px;margin:0}
@media(max-width:820px){.pf-steps{grid-template-columns:1fr 1fr}}
.pf-foot{margin-top:64px;padding-top:20px;border-top:1px solid var(--rule);color:var(--muted);font-size:14px}
.pf-foot a{color:var(--plum)}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
"""


def inject():
    faces = "".join([_face("Big Shoulders", "big-shoulders-display-latin-700-normal.woff2", 700),
                     _face("Big Shoulders", "big-shoulders-display-latin-800-normal.woff2", 800)] +
                    [_face("Schibsted", f"schibsted-grotesk-latin-{w}-normal.woff2", w) for w in (400, 500, 600, 700)])
    st.markdown(f"<style>{faces}{CSS}</style>", unsafe_allow_html=True)
