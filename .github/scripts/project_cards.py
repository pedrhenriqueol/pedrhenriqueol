"""Original, self-contained project scenes for GitHub's image sandbox.

No JavaScript, external fonts, images, or dependencies. Each scene has a useful
first frame; picture sources provide compact layouts and reduced-motion stills.
"""
import html
import textwrap

INK = '#f1f3f5'
MUTED = '#9a9fa8'
DIM = '#676e79'
EDGE = '#2a2e35'
MINT = '#b1e4d0'
FONT = "'DejaVu Sans Mono','Liberation Mono',Consolas,monospace"

MOTION = '''
.flow{animation:flow 5s linear infinite}
.flow-delayed{animation:flow 5s linear infinite -2.5s}
.radar{animation:radar 12s linear infinite;transform-origin:144px 113px}
.beacon{animation:beacon 4s ease-in-out infinite}
.beacon-late{animation:beacon 4s ease-in-out infinite -2s}
.test-row{animation:testRow 8s ease-in-out infinite}
.test-row.second{animation-delay:-5.3s}
.test-row.third{animation-delay:-2.6s}
.trace{animation:trace 8s linear infinite}
.orbit{animation:orbit 16s linear infinite;transform-origin:144px 116px}
.island{animation:island 6s ease-in-out infinite}
.focus{animation:focus 12s ease-in-out infinite}
.access{animation:access 6s ease-in-out infinite}
.access.second{animation-delay:-2s}
.access.third{animation-delay:-4s}
@keyframes flow{to{stroke-dashoffset:-240}}
@keyframes radar{to{transform:rotate(360deg)}}
@keyframes beacon{0%,100%{opacity:.35}50%{opacity:1}}
@keyframes testRow{0%,22%,100%{opacity:.6}30%,55%{opacity:1}}
@keyframes trace{to{stroke-dashoffset:-160}}
@keyframes orbit{to{transform:rotate(360deg)}}
@keyframes island{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
@keyframes focus{0%,100%{stroke-dashoffset:75}50%{stroke-dashoffset:12}}
@keyframes access{0%,100%{opacity:.65}35%,65%{opacity:1}}
@media(prefers-reduced-motion:reduce){
.flow,.flow-delayed,.radar,.beacon,.beacon-late,.test-row,.trace,.orbit,.island,.focus,.access{animation:none!important}
}
'''


def text(x, y, value, size=15, fill=INK, anchor='start', **attrs):
    extra = ' '.join(f'{k.rstrip("_").replace("_", "-")}="{html.escape(str(v), quote=True)}"' for k, v in attrs.items())
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" {extra}>{html.escape(value)}</text>'


def box(x, y, w, h, fill='#111419', stroke=EDGE, rx=7):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>'


def path(d, color=EDGE, width=1.5, **attrs):
    extra = ' '.join(f'{k.rstrip("_").replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def circle(x, y, r, color=EDGE, fill='none', **attrs):
    extra = ' '.join(f'{k.rstrip("_").replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{color}" {extra}/>'


def flow(d, delayed=False):
    return path(d, MINT, 2.5, stroke_dasharray='5 115', class_='flow-delayed' if delayed else 'flow')


def payment_scene():
    routes = ['M144 69V99Q144 111 132 111H74Q62 111 62 123V150',
              'M144 69V99Q144 111 156 111H214Q226 111 226 123V150']
    p = [text(18, 27, '01 / FLUXO PIX', 12, DIM), box(99, 38, 90, 34), text(144, 60, 'PIX', 15, MINT, 'middle')]
    p += [path(d) for d in routes] + [flow(routes[0]), flow(routes[1], True)]
    p += [box(108, 94, 72, 32, '#151b1b', '#435b53'), text(144, 115, 'split', 13, MINT, 'middle')]
    for x, label in [(24, 'seller A'), (188, 'seller B')]:
        p += [box(x, 150, 76, 34), text(x+38, 172, label, 12, INK, 'middle')]
    p += [circle(144, 166, 13, '#435b53'), path('M138 166L142 170L150 161', MINT),
          text(144, 208, 'idempotência · HMAC', 12, MUTED, 'middle')]
    return ''.join(p)


def port_scene():
    p = [text(18, 27, '02 / TELEMETRIA', 12, DIM)]
    for r in (27, 50, 74): p.append(circle(144, 113, r))
    p += [path('M62 113H226M144 39V187', '#20272b'),
          '<g class="radar">'+path('M144 113L192 57', MINT, 1.5)+path('M144 113L199 67', '#435b53', 5)+'</g>',
          path('M98 152V73H173L199 89H116M113 73V152M173 73V121', INK, 1.5),
          path('M103 81L113 91L103 101L113 111L103 121L113 131', DIM, 1),
          box(157, 122, 30, 22, '#19211f', '#435b53'), path('M160 128H184M160 135H184', DIM, 1),
          '<g class="beacon">'+circle(183, 139, 4, MINT, MINT)+circle(183, 139, 9, '#435b53')+'</g>',
          '<g class="beacon-late">'+circle(95, 102, 3, MINT, MINT)+'</g>',
          box(34, 154, 62, 28), text(65, 173, 'IoT', 12, INK, 'middle'),
          box(192, 154, 62, 28), text(223, 173, 'OS', 12, INK, 'middle'),
          text(144, 208, 'sinal → ordem → SLA', 12, MUTED, 'middle')]
    return ''.join(p)


def test_scene():
    p = [text(18, 27, '03 / TEST RUNNER', 12, DIM), box(20, 42, 248, 143),
          path('M20 71H268'), circle(33, 57, 2, DIM, DIM), circle(43, 57, 2, DIM, DIM), circle(53, 57, 2, DIM, DIM),
          text(252, 61, '> spectr', 11, MUTED, 'end')]
    for i, (name, value) in enumerate([('GET /health', '200'), ('schema', 'OK'), ('chaos / retry', 'OK')]):
        y = 94+i*29
        p.append(f'<g class="test-row {"second" if i == 1 else "third" if i == 2 else ""}">')
        p += [path(f'M34 {y-4}l3 3l6 -7', MINT), text(56, y, name, 13), text(250, y, value, 13, MINT, 'end'), '</g>']
    d = 'M36 170H94L102 162L112 176L121 156L133 170H252'
    p += [path(d, '#34423e'), path(d, MINT, 1.5, stroke_dasharray='36 124', class_='trace'),
          text(144, 208, 'contratos · latência · falhas', 12, MUTED, 'middle')]
    return ''.join(p)


def agent_scene():
    p = [text(18, 27, '04 / MEU DESKTOP', 12, DIM), circle(144, 116, 72, '#232b29')]
    p.append('<g class="orbit">'+circle(144, 44, 3, MINT, MINT)+circle(144, 188, 2, DIM, DIM)+'</g>')
    p += [box(34, 77, 220, 91, '#101613', '#344b41', 12), text(52, 101, 'FOCO', 11, MUTED),
          text(52, 132, '25:00', 27), text(53, 153, 'uma tarefa por vez', 10, MUTED),
          circle(220, 122, 20, '#293e34', stroke_width=3),
          circle(220, 122, 20, MINT, stroke_width=3, stroke_dasharray='126', stroke_dashoffset=75, class_='focus'),
          path('M216 115V129M223 115V129', MINT, 2)]
    p += ['<g class="island">', box(78, 46, 132, 23, '#171e1b', '#435b53', 12), circle(93, 57, 2, MINT, MINT),
          text(112, 61, 'ilha dinâmica', 9, INK), '</g>',
          text(144, 208, 'hábitos · finanças · local', 12, MUTED, 'middle')]
    return ''.join(p)


def erp_scene():
    p = [text(18, 27, '05 / ACESSO & DADOS', 12, DIM), box(28, 44, 232, 142), path('M28 72H260'),
          text(44, 63, '> retaguarda', 12, MUTED)]
    for i, (name, count) in enumerate([('admin', 5), ('equipe', 3), ('leitura', 1)]):
        y=98+i*31
        p += [text(44, y, name, 13), f'<g class="access {"second" if i == 1 else "third" if i == 2 else ""}">']
        for j in range(5): p.append(box(142+j*18, y-11, 12, 13, '#b1e4d0' if j<count else '#1c2224', 'none', 2))
        p.append('</g>')
    p += [text(144, 208, 'RBAC · consultas · painéis', 12, MUTED, 'middle')]
    return ''.join(p)


SCENES = {'paystream': payment_scene, 'portlog': port_scene, 'spectr': test_scene,
          'agente-pedro': agent_scene, 'erp': erp_scene}
DETAILS = {
    'paystream': ('PIX / SPLIT / WEBHOOKS', 'pagamentos com rastreabilidade'),
    'portlog': ('IOT / ORDENS / AUDITORIA', 'da telemetria à manutenção'),
    'spectr': ('APIS / CONTRATOS / CHAOS', 'qualidade além do caminho feliz'),
    'agente-pedro': ('TAREFAS / FOCO / FINANÇAS', 'seu dia, no seu dispositivo'),
    'erp': ('RBAC / SQL / PAINÉIS', 'experiência em sistemas corporativos'),
}


def render(project, index, mobile=False, still=False):
    width, height = (600, 600) if mobile else (1000, 344)
    slug = project['slug']
    title = f'[01.{index}] ~/{slug}'
    alt = project['name']+' · '+' '.join(project['lines'])+' Stack: '+project['stack']
    css = '' if still else MOTION
    p = [box(1, 1, width-2, height-2, '#090b0e', EDGE, 10),
         '<rect x="2" y="2" width="'+str(width-4)+'" height="'+str(height-4)+'" rx="9" fill="url(#scan)"/>',
         text(24, 30, title, 14, MUTED), text(width-24, 30, 'DESKTOP' if slug=='agente-pedro' else 'FULL STACK' if slug=='erp' else 'PROJETO', 12, DIM, 'end'),
         path(f'M1 48H{width-1}', EDGE, 1)]
    x = 32 if mobile else 342
    p += [text(x, 92 if mobile else 101, project['name'], 32, INK),
          text(x, 122 if mobile else 130, project['kind'], 16, MINT)]
    lines = textwrap.wrap(' '.join(project['lines']), width=40 if mobile else 50)
    for i, value in enumerate(lines): p.append(text(x, (164 if mobile else 171)+i*28, value, 21 if mobile else 20))
    tags = textwrap.wrap(project['stack'], width=48 if mobile else 58, break_long_words=False)
    for i, value in enumerate(tags): p.append(text(x, (254 if mobile else 247)+i*24, value, 17 if mobile else 16, MUTED))
    sx, sy = (156, 302) if mobile else (24, 68)
    p += [f'<g transform="translate({sx} {sy})">', box(0, 0, 288, 226, '#0d1014', '#232830', 8), SCENES[slug](), '</g>']
    if not mobile:
        p += [path('M324 76V282', EDGE, 1), text(342, 287, DETAILS[slug][0], 12, DIM)]
    footer = height-46
    p += [path(f'M24 {footer}H{width-24}', EDGE, 1), text(24, height-19, DETAILS[slug][1], 12 if mobile else 14, MUTED),
          text(width-24, height-19, 'experiência' if slug=='erp' else 'ver projeto ↗', 12 if mobile else 14, MINT if slug!='erp' else DIM, 'end')]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(project['name'])}</title><desc id="desc">{html.escape(alt)}</desc>
<defs><pattern id="scan" width="4" height="6" patternUnits="userSpaceOnUse"><path d="M0 0H4" stroke="#fff" stroke-opacity=".018"/></pattern></defs>
<style>text{{font-family:{FONT};font-variant-ligatures:none}}{css}</style>
{''.join(p)}</svg>'''


def generate(projects, out):
    erp = {'slug':'erp', 'name':'Retaguarda ERP', 'kind':'experiência / sistemas corporativos',
           'lines':['Painéis administrativos, permissões granulares', 'e otimização de consultas em bancos relacionais.'],
           'stack':'laravel · react · typescript · sql server · docker'}
    for index, project in enumerate([*projects, erp], 1):
        for mobile in (False, True):
            for still in (False, True):
                suffix = ('-mobile' if mobile else '')+('-static' if still else '')
                (out / f'proj-{project["slug"]}{suffix}.svg').write_text(render(project, index, mobile, still), encoding='utf-8')
