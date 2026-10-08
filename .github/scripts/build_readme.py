#!/usr/bin/env python3
"""Generate self-contained GitHub README SVGs. Python 3.11+, no dependencies."""
import argparse
import datetime as dt
import html
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import random
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets'
CFG = json.loads((ROOT / 'assets' / 'profile.json').read_text(encoding='utf-8'))
WHITE, MUTED, ACCENT, BORDER = '#f5f5f5', '#999999', '#dddddd', '#292929'
FONT = "'DejaVu Sans Mono', 'Liberation Mono', Consolas, monospace"

# These animations live inside the SVG images, which GitHub displays directly.
# All effects have a visible static first frame and respect reduced motion.
ANIMATION_CSS = '''
.cursor{animation:blink 1.1s steps(1,end) infinite}
.rain-column{animation:fall 12s linear infinite}
.frame{animation:frameCycle 8s steps(1,end) infinite}
.typing-reveal{animation:typing 1.8s steps(40,end) 1}
.packet-a{animation:packetA 2.8s ease-in-out infinite}
.packet-b{animation:packetB 2.8s ease-in-out infinite .35s}
.signal{animation:signal 3.6s ease-in-out infinite}
.request-dot{animation:requestDot 3.8s linear infinite}
.heartbeat{animation:heartbeat 4s ease-in-out infinite}
.calendar-sweep{animation:calendarSweep 12s linear infinite}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}
@keyframes fall{from{transform:translateY(0)}to{transform:translateY(630px)}}
@keyframes frameCycle{0%{opacity:1}2.5%,100%{opacity:0}}
@keyframes typing{from{width:0}to{width:650px}}
@keyframes packetA{0%{transform:translate(0,0);opacity:0}15%{opacity:1}45%{transform:translate(0,42px)}75%{transform:translate(-46px,78px);opacity:1}100%{transform:translate(-46px,96px);opacity:0}}
@keyframes packetB{0%{transform:translate(0,0);opacity:0}15%{opacity:1}45%{transform:translate(0,42px)}75%{transform:translate(46px,78px);opacity:1}100%{transform:translate(46px,96px);opacity:0}}
@keyframes signal{0%,100%{opacity:.18}50%{opacity:.8}}
@keyframes requestDot{0%{transform:translateX(0);opacity:0}10%{opacity:1}80%{transform:translateX(136px);opacity:1}100%{transform:translateX(136px);opacity:0}}
@keyframes heartbeat{0%,100%{opacity:.25}50%{opacity:1}}
@keyframes calendarSweep{from{transform:translateX(0)}to{transform:translateX(865px)}}
@media(prefers-reduced-motion:reduce){
 .cursor,.rain-column,.frame,.typing-reveal,.packet-a,.packet-b,.signal,.request-dot,.heartbeat,.calendar-sweep{animation:none!important}
 .frame{opacity:0!important}.frame.first{opacity:1!important}
 .calendar-sweep,.packet-a,.packet-b,.request-dot{opacity:0!important}
}
'''


def text(x, y, value, size=20, fill=WHITE, **attrs):
    attributes = ' '.join(f'{("xml:space" if k == "xml_space" else k.replace("_", "-"))}="{html.escape(str(v), quote=True)}"' for k, v in attrs.items())
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" {attributes}>{html.escape(str(value))}</text>'


def line(x1, y1, x2, y2, stroke=BORDER):
    return f'<path d="M{x1} {y1}H{x2}" stroke="{stroke}"/>' if y1 == y2 else f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{stroke}"/>'


def rect(x, y, w, h, fill, rx=0, stroke='none'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>'


def card(filename, height, title, parts, status='', matrix=False):
    title_xml = text(30, 31, title, 15, ACCENT)
    if status:
        title_xml += text(968, 31, status, 15, MUTED, text_anchor='end')
    rain = ''
    if matrix:
        rng = random.Random(41)
        for col in range(18):
            chars = ''.join(rng.choice('01ABCDEF') for _ in range(35))
            column = []
            for row, char in enumerate(chars):
                for duplicate in (-630, 0):
                    column.append(text(30+col*55, 68+row*18+duplicate, char, 12, '#ffffff', opacity='.055'))
            duration = 13 + (col % 5) * 2
            rain += f'<g class="rain-column" style="animation-duration:{duration}s;animation-delay:-{col*1.37:.2f}s">{"".join(column)}</g>'
        rain = f'<g class="rain" clip-path="url(#content-area)">{rain}</g>'
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape('Cartão do perfil de '+CFG['name'])}</desc>
<defs><pattern id="scan" width="4" height="7" patternUnits="userSpaceOnUse"><path d="M0 0H4" stroke="#fff" stroke-opacity=".025"/></pattern>
<clipPath id="content-area"><rect x="2" y="51" width="996" height="{height-53}"/></clipPath>
<clipPath id="typing-clip"><rect class="typing-reveal" x="48" y="258" width="650" height="40"/></clipPath></defs>
<style>text{{font-family:{FONT};font-variant-ligatures:none}}{ANIMATION_CSS}</style>
{rect(1,1,998,height-2,'#080808',8,BORDER)}{rain}{rect(1,1,998,height-2,'url(#scan)',8)}
{title_xml}{line(1,50,999,50)}{''.join(parts)}</svg>'''
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / (filename+'.svg')).write_text(svg, encoding='utf-8')


def ascii_lines(x, y, values, size=20, fill=MUTED, spacing=24):
    return ''.join(text(x, y+i*spacing, v, size, fill, xml_space='preserve') for i,v in enumerate(values))


def pixel_name():
    alphabet = {
        'P':['11110','10001','10001','11110','10000','10000','10000'],
        'E':['11111','10000','10000','11110','10000','10000','11111'],
        'D':['11110','10001','10001','10001','10001','10001','11110'],
        'R':['11110','10001','10001','11110','10100','10010','10001'],
        'O':['01110','10001','10001','10001','10001','10001','01110']}
    parts=[]
    for i,c in enumerate('PEDRO'):
        for row,bits in enumerate(alphabet[c]):
            for col,bit in enumerate(bits):
                if bit == '1':parts.append(rect(48+i*84+col*14,92+row*14,12,12,WHITE))
    return ''.join(parts)


def rotate_vector(point, angle, tilt=0.0):
    x,y,z = point
    c,s = math.cos(angle),math.sin(angle)
    x,z = c*x+s*z,-s*x+c*z
    c,s = math.cos(tilt),math.sin(tilt)
    return x,c*y-s*z,s*y+c*z


def render_cloud(points, angle, columns=40, rows=25, scale=11.0, center_y=0.0, tilt=0.0):
    cells = [[' ']*columns for _ in range(rows)]
    depth = [[float('inf')]*columns for _ in range(rows)]
    ramp = '.,:;=+*#%@'
    light = (-.35,.55,-.76)
    for position,normal in points:
        x,y,z = rotate_vector((position[0],position[1]-center_y,position[2]),angle,tilt)
        nx,ny,nz = rotate_vector(normal,angle,tilt)
        perspective = 4.8/(4.8+z)
        col = round(columns/2+x*scale*perspective)
        row = round(rows/2-y*scale*.66*perspective)
        if 0<=col<columns and 0<=row<rows and z<depth[row][col]:
            brightness = .22+.78*max(0,nx*light[0]+ny*light[1]+nz*light[2])
            cells[row][col] = ramp[min(len(ramp)-1,round(brightness*(len(ramp)-1)))]
            depth[row][col] = z
    return [''.join(row).rstrip() for row in cells]


def headphones_model():
    points=[]
    # A curved headband and two rounded ear cups; all geometry is original.
    for i in range(101):
        theta=math.pi*i/100
        for j in range(12):
            phi=2*math.pi*j/12
            radial=(math.cos(theta),math.sin(theta),0)
            normal=(radial[0]*math.cos(phi),radial[1]*math.cos(phi),math.sin(phi))
            point=(.98*math.cos(theta)+.06*normal[0],1.13*math.sin(theta)+.06*normal[1],.06*normal[2])
            points.append((point,normal))
    for side in (-1,1):
        for i in range(23):
            latitude=math.pi*i/22
            for j in range(48):
                longitude=2*math.pi*j/48
                normal=(math.cos(latitude),math.sin(latitude)*math.cos(longitude),math.sin(latitude)*math.sin(longitude))
                point=(side*.98+.16*normal[0],-.20+.36*normal[1],.27*normal[2])
                points.append((point,normal))
    return points


def cube_model():
    points=[]
    for axis in range(3):
        for side in (-1,1):
            normal=[0,0,0];normal[axis]=side
            other=[i for i in range(3) if i!=axis]
            for i in range(27):
                for j in range(27):
                    point=[0,0,0];point[axis]=side*.8
                    point[other[0]]=-.8+1.6*i/26;point[other[1]]=-.8+1.6*j/26
                    points.append((point,normal))
    return points


def animated_cloud(kind,x,y,font_size=10,spacing=9,scale=11):
    points=headphones_model() if kind=='headphones' else cube_model()
    groups=[]
    for frame in range(40):
        angle=2*math.pi*frame/40
        rows=render_cloud(points,angle,scale=scale,center_y=.28 if kind=='headphones' else 0,tilt=-.08 if kind=='headphones' else -.48)
        body=ascii_lines(x,y,rows,font_size,'#d8d8d8',spacing)
        groups.append(f'<g class="frame{" first" if frame==0 else ""}" opacity="{1 if frame==0 else 0}" style="animation-delay:{frame*.2:.1f}s">{body}</g>')
    return '<g class="ascii-object">'+''.join(groups)+'</g>'


def hero():
    typed=f'<g clip-path="url(#typing-clip)">{text(48,286,"> "+CFG["headline"],23,ACCENT)}</g>'
    parts=[pixel_name(),text(48,237,'H E N R I Q U E',28),typed,
           text(48,331,CFG['intro'][0],21),text(48,359,CFG['intro'][1],21),line(48,388,952,388),
           text(48,419,'$ cat sobre.txt',16,ACCENT)]
    for i,s in enumerate(CFG['about']):parts.append(text(48,452+28*i,s,20))
    parts.append(animated_cloud('headphones',664,84,font_size=11,spacing=9,scale=12))
    parts.append(f'<g class="cursor">{rect(600,269,11,20,WHITE)}</g>')
    card('hero',538,'~/pedrhenriqueol',parts,'full stack / QA',True)


def buttons():
    for slug,label,symbol in [('portfolio','portfólio','↗'),('linkedin','linkedin','in'),('email','email','@'),('github','github','<>')]:
        body=rect(1,1,238,60,'#080808',8,BORDER)+text(24,39,symbol,23,ACCENT)+text(66,37,label,18)+text(218,37,'↗',17,MUTED,text_anchor='end')
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="240" height="62" viewBox="0 0 240 62"><title>{label}</title><g font-family="{FONT}">{body}</g></svg>'
        (OUT/('btn-'+slug+'.svg')).write_text(svg,encoding='utf-8')


def projects():
    for i,p in enumerate(CFG['projects']):
        parts=[ascii_lines(47,86,p['diagram'],19,spacing=21),text(342,100,p['name'],34),text(342,128,p['kind'],15,ACCENT)]
        for j,s in enumerate(p['lines']):parts.append(text(342,166+j*28,s,20))
        parts.append(text(342,232,p['stack'],16,MUTED))
        if p['slug']=='paystream':
            parts.extend([f'<g class="packet-a">{rect(168,91,5,5,WHITE)}</g>',f'<g class="packet-b">{rect(168,91,5,5,WHITE)}</g>'])
        elif p['slug']=='portlog':
            parts.append(f'<g class="signal">{rect(45,180,198,56,"none",2,"#777777")}</g>')
        elif p['slug']=='spectr':
            parts.append(f'<g class="request-dot">{rect(78,229,7,3,WHITE)}</g>')
        card('proj-'+p['slug'],258,f'[01.{i+1}] ~/{p["slug"]}',parts,'abrir repositório ↗')
    parts=[ascii_lines(47,91,['  ┌───────────┐','  │    ERP    │','  ├───────────┤','  │ RBAC      │','  │ MULTI     │','  │ TENANT    │','  └───────────┘'],19,spacing=21),
           text(342,100,'Retaguarda ERP',34),text(342,128,'experiência / sistemas corporativos',15,ACCENT),
           text(342,166,'Painéis administrativos, permissões granulares',20),
           text(342,194,'e otimização de consultas em bancos relacionais.',20),
           text(342,232,'laravel · react · typescript · sql server · docker',16,MUTED)]
    parts.append(f'<g class="heartbeat">{rect(231,168,6,6,WHITE)}</g>')
    card('proj-erp',258,'[01.4] ~/retaguarda-erp',parts,'experiência profissional')


def experience():
    parts=[text(38,96,'01',30,ACCENT),text(109,90,'SETE Tecnologia',26),text(109,119,'QA / Testes · estágio',18,MUTED),
           text(109,155,'Logística aduaneira e portuária, SQL Server e Postman.',20),line(38,182,962,182),
           text(38,231,'02',30,ACCENT),text(109,225,'Qualisoft Sistemas',26),text(109,254,'Back-end / Full Stack · estágio',18,MUTED),
           text(109,290,'ERPs com Laravel, React e TypeScript; manutenção Delphi.',20),line(38,317,962,317),
           text(38,358,'$ formação',16,ACCENT),text(220,358,'Engenharia de Software · UniFanor Wyden',20)]
    card('experience',393,'[02] ~/experiência',parts,'desenvolvimento + qualidade')


def icon(slug,x,y,size=38):
    source=ROOT/'assets'/'icons'/(slug+'.svg')
    if not source.exists():return text(x,y+28,slug[:2].upper(),24)
    root=ET.fromstring(source.read_text(encoding='utf-8'))
    paths=''.join(ET.tostring(e,encoding='unicode') for e in root if e.tag.endswith('path'))
    return f'<g transform="translate({x} {y}) scale({size/24})" fill="{WHITE}">{paths}</g>'


def stack():
    rows=[('aplicações',[('react','React'),('typescript','TypeScript'),('javascript','JavaScript'),('nodedotjs','Node.js'),('php','PHP'),('laravel','Laravel')]),
          ('dados & APIs',[('fastify','Fastify'),('prisma','Prisma'),('postgresql','PostgreSQL'),('supabase','Supabase'),('postman','Postman'),('openapiinitiative','OpenAPI')]),
          ('entrega & interface',[('tailwindcss','Tailwind'),('vite','Vite'),('docker','Docker'),('git','Git'),('github','GitHub'),('vercel','Vercel')])]
    parts=[]
    for row,(label,entries) in enumerate(rows):
        y=80+row*111;parts.append(text(38,y,label,15,ACCENT))
        for col,(slug,name) in enumerate(entries):
            cx=95+col*161;parts.append(icon(slug,cx-19,y+17));parts.append(text(cx,y+81,name,15,MUTED,text_anchor='middle'))
    parts.extend([line(38,398,962,398),text(38,432,'também: SQL Server · Delphi · Framer Motion · JSON Schema · AWS',17,MUTED)])
    card('stack',465,'[03] $ ls ~/stack',parts,'18 ferramentas + fundamentos')


def quality():
    parts=[]
    groups=[('01 / qualidade',['Contratos JSON Schema / OpenAPI','Testes e automação de APIs','Asserções com Postman / Runner']),
            ('02 / arquitetura',['Node.js e PHP / Laravel','React, TypeScript e Tailwind','Consultas SQL e sistemas legados']),
            ('03 / resiliência',['Idempotência e HMAC-SHA256','Injeção de latência e falhas','Métricas de desempenho e SLA'])]
    for i,(title,items) in enumerate(groups):
        y=95+i*111;parts.append(text(38,y,title,21,ACCENT))
        for j,s in enumerate(items):parts.append(text(375,y-2+j*27,'> '+s,20))
        if i<2:parts.append(line(38,y+74,962,y+74))
    card('quality',398,'[04] ~/engenharia',parts,'implementar · validar · medir')


def certifications():
    parts=[]
    for i,(name,title) in enumerate(CFG['certifications']):
        y=92+i*49;parts.append(text(38,y,name,18,ACCENT));parts.append(text(207,y,title,20))
    card('certifications',276,'[05] ~/certificações',parts,'aprendizado contínuo')


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__();self.days={};self.ids={};self.tip=None;self.buffer=''

    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='td' and a.get('data-date'):
            date=a['data-date'];self.days[date]={'date':date,'level':int(a['data-level']),'count':0};self.ids[a['id']]=date
        if tag=='tool-tip' and a.get('for') in self.ids:self.tip=self.ids[a['for']];self.buffer=''

    def handle_data(self, data):
        if self.tip:self.buffer+=data

    def handle_endtag(self, tag):
        if tag=='tool-tip' and self.tip:
            match=re.search(r'([\d,]+) contributions?',self.buffer)
            self.days[self.tip]['count']=int(match.group(1).replace(',','')) if match else 0
            self.tip=None


def request(url):
    req=urllib.request.Request(url,headers={'User-Agent':'profile-readme-generator','Accept':'*/*'})
    with urllib.request.urlopen(req,timeout=40) as response:return response.read().decode('utf-8')


def refresh_calendar():
    user=CFG['username']
    profile=json.loads(request(f'https://api.github.com/users/{user}'))
    parser=CalendarParser();parser.feed(request(f'https://github.com/users/{user}/contributions'))
    days=sorted(parser.days.values(),key=lambda d:d['date'])
    if len(days)<350 or any(d['level']>0 and d['count']==0 for d in days):
        raise RuntimeError('Calendário incompleto: mantendo a versão anterior. Confira o HTML do GitHub.')
    result={'username':user,'updated':dt.datetime.now(dt.timezone.utc).date().isoformat(),
            'followers':profile['followers'],'repositories':profile['public_repos'],
            'total':sum(d['count'] for d in days),'days':days}
    (ROOT/'assets'/'contributions.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def contributions():
    snap=json.loads((ROOT/'assets'/'contributions.json').read_text(encoding='utf-8'))
    days=snap['days'];best=run=0
    for d in days:
        run=run+1 if d['count'] else 0;best=max(best,run)
    recent=days[:-1] if days[-1]['count']==0 else days
    current=0
    for d in reversed(recent):
        if not d['count']:break
        current+=1
    parts=[text(38,92,f'{snap["total"]:,}'.replace(',','.')+' contribuições no último ano',22),
           text(38,124,f'sequência atual: {current} dias · maior sequência: {best} dias',17,MUTED)]
    start=dt.date.fromisoformat(days[0]['date']);start-=dt.timedelta(days=(start.weekday()+1)%7)
    levels=['·',':','+','#','@'];colors=['#333333','#666666','#999999',ACCENT,WHITE];month=None
    months=['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez']
    for d in days:
        date=dt.date.fromisoformat(d['date']);delta=(date-start).days;col,row=divmod(delta,7)
        x,y=96+col*16,174+row*19
        if row==0 and date.month!=month:
            parts.append(text(x,152,months[date.month-1],13,MUTED));month=date.month
        level=d['level'];glyph=text(x,y,levels[level],17,colors[level])
        parts.append(f'<g><title>{date.isoformat()}: {d["count"]} contribuições</title>{glyph}</g>')
    for row,label in [(1,'seg'),(3,'qua'),(5,'sex')]:parts.append(text(38,174+row*19,label,13,MUTED))
    parts.append(f'<g clip-path="url(#calendar-area)"><g class="calendar-sweep">{rect(75,157,20,132,"#ffffff")}</g></g>')
    parts[-1]='<defs><clipPath id="calendar-area"><rect x="88" y="156" width="866" height="133"/></clipPath></defs>'+parts[-1].replace('<g class="calendar-sweep">','<g class="calendar-sweep" opacity=".045">')
    parts.extend([text(38,324,'atualizado em '+dt.date.fromisoformat(snap['updated']).strftime('%d/%m/%Y'),14,MUTED),
                  text(963,324,'menos  · : + # @  mais',14,MUTED,text_anchor='end')])
    card('contributions',352,'[06] ~/contribuições',parts,f'{snap["followers"]} seguidores · {snap["repositories"]} repositórios públicos')


def contact():
    parts=[animated_cloud('cube',48,81,font_size=11,spacing=8,scale=11),
           text(400,112,'bora conversar?',36),text(400,155,'Projetos, desenvolvimento ou qualidade.',20),
           text(400,200,'> '+CFG['email'],20,ACCENT),text(400,235,'> '+CFG['username'],20),
           f'<g class="cursor">{rect(619,219,12,20,ACCENT)}</g>']
    card('contact',294,'[07] ~/contato',parts,'-- EOF --',True)


def readme():
    def image(name,alt,url=None):
        tag=f'<img src="./assets/{name}.svg" width="100%" alt="{html.escape(alt,quote=True)}" />'
        return f'<a href="{html.escape(url,quote=True)}">{tag}</a>' if url else tag
    pieces=['<!-- Gerado por .github/scripts/build_readme.py. Configuração: assets/profile.json. -->','<p align="center">',
            image('hero',CFG['name']+' · '+CFG['headline']+'. '+' '.join(CFG['intro']+CFG['about']),CFG['portfolio'])]
    for slug,label,url in [('portfolio','Portfólio',CFG['portfolio']),('linkedin','LinkedIn',CFG['linkedin']),('email','Email','mailto:'+CFG['email']),('github','GitHub','https://github.com/'+CFG['username'])]:
        pieces.append(f'<a href="{url}"><img src="./assets/btn-{slug}.svg" width="24%" alt="{label}" /></a>')
    for p in CFG['projects']:pieces.append(image('proj-'+p['slug'],p['name']+' · '+' '.join(p['lines'])+' Stack: '+p['stack'],p['url']))
    pieces.extend([image('proj-erp','Retaguarda ERP · Painéis corporativos, RBAC e otimização de consultas. Laravel, React, TypeScript, SQL Server e Docker.'),
                   image('experience','SETE Tecnologia: estágio em QA / Testes. Qualisoft: estágio em Back-end / Full Stack. Engenharia de Software na UniFanor Wyden.'),
                   image('stack','React, TypeScript, JavaScript, Node.js, PHP, Laravel, Fastify, Prisma, PostgreSQL, Supabase, Postman, OpenAPI, Tailwind, Vite, Docker, Git, GitHub, Vercel. Também: SQL Server, Delphi, Framer Motion, JSON Schema e AWS.'),
                   image('quality','Engenharia de qualidade, arquitetura e resiliência: contratos de API, automação de testes, SQL, idempotência, webhooks assinados e métricas de desempenho.'),
                   image('certifications','Certificações: '+ '; '.join(a+' '+b for a,b in CFG['certifications'])),
                   image('contributions','Contribuições no GitHub de '+CFG['username']+' — calendário atualizado automaticamente.','https://github.com/'+CFG['username']+'?tab=overview'),
                   image('contact','Bora conversar? '+CFG['email']+' · '+CFG['username'],'mailto:'+CFG['email']),'</p>',
                   '', '<details>', '<summary>Perfil e projetos em texto</summary>', '', '### '+CFG['name'], '',
                   'Desenvolvedor Full Stack e Analista de QA, graduando em Engenharia de Software na UniFanor Wyden.', '',
                   '- **SETE Tecnologia:** estágio em QA / Testes para logística aduaneira e portuária; SQL Server, Postman e validação de APIs.',
                   '- **Qualisoft Sistemas:** estágio em Back-end / Full Stack; Laravel, React, TypeScript, consultas SQL e manutenção de sistemas Delphi.', '', '### Projetos', ''])
    for p in CFG['projects']:pieces.append(f'- **[{p["name"]}]({p["url"]}):** '+ ' '.join(p['lines'])+' '+p['stack']+'.')
    pieces.extend(['- **Retaguarda ERP:** experiência com painéis corporativos, permissões RBAC e bancos relacionais.', '',
                   f'[Portfólio]({CFG["portfolio"]}) · [LinkedIn]({CFG["linkedin"]}) · [Email](mailto:{CFG["email"]})', '', '</details>', '',
                   '<sub>Visual inspirado no perfil de <a href="https://github.com/vitorcgo/vitorcgo">vitorcgo</a>; cartões e gerador personalizados. Ícones: <a href="https://simpleicons.org">Simple Icons</a>.</sub>', ''])
    (ROOT/'README.md').write_text('\n'.join(pieces),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--refresh',action='store_true',help='Atualiza as contribuições públicas do GitHub antes de gerar.');args=parser.parse_args()
    if args.refresh:refresh_calendar()
    hero();buttons();projects();experience();stack();quality();certifications();contributions();contact();readme()
    print('README e cartões monocromáticos gerados em assets/.')


if __name__=='__main__':main()
