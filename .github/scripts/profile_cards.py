"""Monochrome profile panels and original projected 3D objects.

Geometry is generated locally and animated as SVG frames inside GitHub images.
Only the standard library is used; all content remains visible without motion.
"""
import datetime as dt
import html
import json
import math
from functools import lru_cache
import textwrap
import xml.etree.ElementTree as ET

from project_cards import INK, MUTED, DIM, EDGE, ACCENT, FONT, box, text, path, circle

FRAME_COUNT = 60
DURATION = 6
MOTION = f'''
.model-frame{{animation:modelFrame {DURATION}s steps(1,end) infinite}}
.sweep{{animation:sweep 10s linear infinite}}
.pulse{{animation:pulse 5s ease-in-out infinite}}
.pulse.second{{animation-delay:-2.5s}}
.dash{{animation:dash 8s linear infinite}}
@keyframes modelFrame{{0%{{opacity:1}}{100/FRAME_COUNT:.5f}%,100%{{opacity:0}}}}
@keyframes sweep{{0%{{transform:translateX(-40px)}}100%{{transform:translateX(1000px)}}}}
@keyframes pulse{{0%,100%{{opacity:.65}}50%{{opacity:1}}}}
@keyframes dash{{to{{stroke-dashoffset:-120}}}}
@media(prefers-reduced-motion:reduce){{
.model-frame,.sweep,.pulse,.dash{{animation:none!important}}
.model-frame{{opacity:0!important}}.model-frame.first{{opacity:1!important}}
.sweep{{opacity:0!important}}
}}
'''


def shade(value):
    value = max(0, min(255, round(value)))
    return '#'+f'{value:02x}'*3


def rotate(p, angle, tilt=-.22):
    x,y,z=p
    x,z=x*math.cos(angle)+z*math.sin(angle),-x*math.sin(angle)+z*math.cos(angle)
    return x,y*math.cos(tilt)-z*math.sin(tilt),y*math.sin(tilt)+z*math.cos(tilt)


def project(p, scale=72):
    x,y,z=p
    perspective=5/(5+z)
    return 150+x*scale*perspective,132-y*scale*perspective


def points_path(points, close=True):
    return 'M'+'L'.join(f'{x:.1f},{y:.1f}' for x,y in points)+('Z' if close else '')


def face(vertices, normal, material=1):
    return vertices, normal, material


@lru_cache(maxsize=1)
def headphone_mesh():
    faces=[]
    # A curved solid band with front/back walls, plus cylindrical ear shells.
    for i in range(24):
        a,b=math.pi*i/24,math.pi*(i+1)/24
        def v(t,r,z): return (r*math.cos(t),1.18*r*math.sin(t),z)
        for z,n in [(-.075,(0,0,-1)),(.075,(0,0,1))]:
            faces.append(face([v(a,.94,z),v(a,1.04,z),v(b,1.04,z),v(b,.94,z)],n,.85))
        for r,sign in [(.94,-1),(1.04,1)]:
            mid=(a+b)/2
            faces.append(face([v(a,r,-.075),v(a,r,.075),v(b,r,.075),v(b,r,-.075)],(sign*math.cos(mid),sign*math.sin(mid),0),1))
    for side in (-1,1):
        for x,n,material in [(side*.88,(-side,0,0),.42),(side*1.14,(side,0,0),1)]:
            ring=[(x,-.22+.40*math.cos(t*2*math.pi/20),.27*math.sin(t*2*math.pi/20)) for t in range(20)]
            faces.append(face(ring,n,material))
            # Recessed centers and vent slots make the cups read as hardware,
            # including when the rotation presents just one outer ear shell.
            direction=n[0]
            rim_x=x+direction*.004
            inner=[(rim_x,-.22+.34*math.cos(t*2*math.pi/20),.225*math.sin(t*2*math.pi/20)) for t in range(20)]
            faces.append(face(inner,n,material*.52))
            if direction==side:
                for slot in range(-2,3):
                    z=slot*.051
                    sx=rim_x+direction*.004
                    faces.append(face([(sx,-.40,z-.005),(sx,-.04,z-.005),(sx,-.04,z+.005),(sx,-.40,z+.005)],n,.15))
        for i in range(20):
            a,b=2*math.pi*i/20,2*math.pi*(i+1)/20
            v=lambda x,t:(x,-.22+.40*math.cos(t),.27*math.sin(t))
            faces.append(face([v(side*.88,a),v(side*1.14,a),v(side*1.14,b),v(side*.88,b)],(0,math.cos((a+b)/2),math.sin((a+b)/2)),.7))
    return faces


def headphones(angle):
    faces=[]
    for vertices,normal,material in headphone_mesh():
        rotated=[rotate((x,y-.28,z),angle,-.12) for x,y,z in vertices]
        nx,ny,nz=rotate(normal,angle,-.12)
        # Keep rear surfaces occluded by sorting before projecting.
        value=(48+155*max(0,-nx*.38+ny*.48-nz*.78))*material
        faces.append((sum(v[2] for v in rotated)/len(rotated),
                      f'<path d="{points_path([project(v,78) for v in rotated])}" fill="{shade(value)}" stroke="{shade(value+24)}" stroke-width=".45" stroke-linejoin="round"/>'))
    return ''.join(item[1] for item in sorted(faces,reverse=True))


def cube_vertices(size):
    return [(x*size,y*size,z*size) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]


def cube(angle):
    p=[]
    outer=[rotate(v,angle,-.48) for v in cube_vertices(.97)]
    # Dashed rear edges, solid front edges, and a separately shaded inner core.
    edges=[(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    for a,b in edges:
        depth=(outer[a][2]+outer[b][2])/2
        p.append(path(points_path([project(outer[a],65),project(outer[b],65)],False), shade(90 if depth>0 else 195),1,stroke_dasharray='3 4' if depth>0 else 'none'))
    inner=[rotate(v,angle+.12,-.48) for v in cube_vertices(.61)]
    faces=[]
    for ids,n in [([0,1,2,3],(0,0,-1)),([4,5,6,7],(0,0,1)),([0,3,7,4],(-1,0,0)),([1,2,6,5],(1,0,0)),([3,2,6,7],(0,1,0)),([0,1,5,4],(0,-1,0))]:
        nx,ny,nz=rotate(n,angle+.12,-.48)
        points=[inner[i] for i in ids]
        value=34+100*max(0,-nx*.4+ny*.55-nz*.74)
        body=f'<path d="{points_path([project(v,65) for v in points])}" fill="{shade(value)}" stroke="{shade(value+65)}" stroke-width=".7"/>'
        # A surface lattice follows each face in perspective.
        a,b,c,d=points
        for j in range(1,5):
            t=j/5
            lerp=lambda u,v:tuple(u[k]+(v[k]-u[k])*t for k in range(3))
            for u,v in [(lerp(a,b),lerp(d,c)),(lerp(a,d),lerp(b,c))]:
                body+=path(points_path([project(u,65),project(v,65)],False),shade(value+33),.5)
        faces.append((sum(v[2] for v in points)/4,body))
    p += [item[1] for item in sorted(faces,reverse=True)]
    for v in outer:
        x,y=project(v,65)
        p.append(circle(round(x,1),round(y,1),1.8,INK,INK))
    return ''.join(p)


@lru_cache(maxsize=4)
def object_scene(kind, still):
    p=[box(0,0,300,274,'#101010',EDGE,10),text(18,25,'FORM / 01' if kind=='headphones' else 'FORM / 02',11,DIM),
       text(282,25,'3D',11,DIM,'end')]
    # A quiet reference grid, ground plane, and orbital framing.
    for x in range(30,300,30): p.append(path(f'M{x} 44V226','#191919',.6))
    for y in range(46,227,30): p.append(path(f'M20 {y}H280','#191919',.6))
    p += ['<ellipse cx="150" cy="221" rx="78" ry="12" fill="url(#shadow)"/>',
          '<ellipse cx="150" cy="140" rx="119" ry="93" fill="none" stroke="#292929" stroke-dasharray="2 7"/>']
    renderer=headphones if kind=='headphones' else cube
    for i in range(1 if still else FRAME_COUNT):
        angle=.48+2*math.pi*i/FRAME_COUNT
        attr='' if still else f' class="model-frame{" first" if i==0 else ""}" opacity="{1 if i==0 else 0}" style="animation-delay:{i*DURATION/FRAME_COUNT:.1f}s"'
        p.append(f'<g{attr}>{renderer(angle)}</g>')
    p += [path('M20 238H280',EDGE,1),text(150,258,'som · código · concentração' if kind=='headphones' else 'ideia → código → entrega',11,MUTED,'middle')]
    return ''.join(p)


def panel(width,height,title,status,parts,still,desc):
    css='' if still else MOTION
    header=[box(1,1,width-2,height-2,'#0b0b0b',EDGE,10),
            f'<rect x="2" y="2" width="{width-4}" height="{height-4}" rx="9" fill="url(#scan)"/>',
            text(24,30,title,14,MUTED),text(width-24,30,status,11,DIM,'end'),path(f'M1 48H{width-1}',EDGE,1)]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(desc)}</desc>
<defs><pattern id="scan" width="4" height="6" patternUnits="userSpaceOnUse"><path d="M0 0H4" stroke="#fff" stroke-opacity=".018"/></pattern>
<radialGradient id="shadow"><stop stop-color="#000" stop-opacity=".85"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient></defs>
<style>text{{font-family:{FONT};font-variant-ligatures:none}}{css}</style>
{''.join(header+parts)}</svg>'''


def wrapped(x,y,value,width,size=20,fill=INK,step=28):
    return [text(x,y+i*step,line,size,fill) for i,line in enumerate(textwrap.wrap(value,width=width,break_long_words=False))]


def footer(width,height,left,right=''):
    return [path(f'M24 {height-46}H{width-24}',EDGE,1),text(24,height-19,left,12,MUTED),text(width-24,height-19,right,12,DIM,'end')]


def pixel_name(x,y):
    alphabet={'P':['11110','10001','10001','11110','10000','10000','10000'],
              'E':['11111','10000','10000','11110','10000','10000','11111'],
              'D':['11110','10001','10001','10001','10001','10001','11110'],
              'R':['11110','10001','10001','11110','10100','10010','10001'],
              'O':['01110','10001','10001','10001','10001','10001','01110']}
    p=[]
    for i,c in enumerate('PEDRO'):
        for row,bits in enumerate(alphabet[c]):
            for col,bit in enumerate(bits):
                if bit=='1':p.append(box(x+i*84+col*14,y+row*14,11,11,INK,'none',1))
    return ''.join(p)


def hero(cfg,root,mobile,still):
    w,h=(600,890) if mobile else (1000,588)
    x=32 if mobile else 38
    p=[text(x,83,'DESENVOLVIMENTO / FULL STACK / QA',14,MUTED),pixel_name(x,106),
       text(x,234,'H E N R I Q U E',26),*wrapped(x,278,'> '+cfg['headline'],37 if mobile else 40,22,ACCENT)]
    y=356 if mobile else 370
    for s in cfg['intro']:
        rows=wrapped(x,y,s,41 if mobile else 64,20)
        p+=rows;y+=len(rows)*28
    if mobile:
        p += [f'<g transform="translate(150 452)">{object_scene("headphones",still)}</g>',path('M32 749H568',EDGE,1)]
        # Keep full biography in a separate panel on compact screens.
        p+=wrapped(32,787,'Full stack + qualidade. Engenharia de Software na UniFanor Wyden.',42,19,MUTED)
    else:
        p += [f'<g transform="translate(656 94)">{object_scene("headphones",still)}</g>',path('M38 443H962',EDGE,1),text(38,476,'$ cat sobre.txt',14,MUTED)]
        for i,s in enumerate(cfg['about']):p.append(text(38,510+i*27,s,18))
    return panel(w,h,'~/'+cfg['username'],'FULL STACK / QA',p,still,'Perfil de '+cfg['name']+'. '+' '.join(cfg['intro']+cfg['about']))


def experience(cfg,root,mobile,still):
    w,h=(600,716) if mobile else (1000,564)
    p=[text(32,95,'Experiência que conecta código e qualidade.',21 if mobile else 25)]
    entries=[('01','SETE Tecnologia','QA / Testes · estágio','Logística aduaneira e portuária, SQL Server, Postman e validação de APIs.'),
             ('02','Qualisoft Sistemas','Back-end / Full Stack · estágio','ERPs com Laravel, React e TypeScript; consultas SQL e manutenção de sistemas Delphi.')]
    for i,(index,name,role,desc) in enumerate(entries):
        y=(157+i*197) if mobile else (157+i*153)
        p += [f'<g class="pulse {"second" if i else ""}">{circle(48,y-7,15,MUTED)}</g>',text(48,y-2,index,11,MUTED,'middle'),text(80,y,name,26),text(80,y+30,role,17,MUTED)]
        p += wrapped(80,y+70,desc,36 if mobile else 68,19)
        if i==0:p.append(path(f'M48 {y+14}V{y+(175 if mobile else 131)}',EDGE,1))
    fy=566 if mobile else 457
    p += [path(f'M32 {fy-30}H{w-32}',EDGE,1),text(32,fy,'FORMAÇÃO',13,DIM)]
    p += wrapped(32,fy+35,'Engenharia de Software · UniFanor Wyden',40 if mobile else 70,21)
    p += footer(w,h,'desenvolvimento + qualidade','[02]')
    return panel(w,h,'[02] ~/experiência','TRAJETÓRIA',p,still,'SETE Tecnologia: QA. Qualisoft: back-end e full stack. Engenharia de Software na UniFanor Wyden.')


def icon(root,slug,x,y,size=32):
    source=root/'assets'/'icons'/(slug+'.svg')
    node=ET.fromstring(source.read_text(encoding='utf-8'))
    paths=''.join(ET.tostring(e,encoding='unicode') for e in node if e.tag.endswith('path'))
    return f'<g transform="translate({x} {y}) scale({size/24})" fill="{INK}">{paths}</g>'


def stack(cfg,root,mobile,still):
    w,h=(600,936) if mobile else (1000,572)
    groups=[('01 / aplicações',[('react','React'),('typescript','TypeScript'),('javascript','JavaScript'),('nodedotjs','Node.js'),('php','PHP'),('laravel','Laravel')]),
            ('02 / dados & APIs',[('fastify','Fastify'),('prisma','Prisma'),('postgresql','PostgreSQL'),('supabase','Supabase'),('postman','Postman'),('openapiinitiative','OpenAPI')]),
            ('03 / entrega & interface',[('tailwindcss','Tailwind'),('vite','Vite'),('docker','Docker'),('git','Git'),('github','GitHub'),('vercel','Vercel')])]
    p=[]
    for i,(label,items) in enumerate(groups):
        y=88+i*(254 if mobile else 133)
        p.append(text(32,y,label,16,MUTED))
        for j,(slug,label) in enumerate(items):
            col,row=(j%3,j//3) if mobile else (j,0)
            x=32+col*(183 if mobile else 157);cy=y+22+row*94
            p += [box(x,cy,170 if mobile else 147,80,'#111111',EDGE,7),icon(root,slug,x+12,cy+14),text(x+12,cy+65,label,14)]
    end=850 if mobile else 492
    p.append(path(f'M32 {end-28}H{w-32}',EDGE,1))
    p+=wrapped(32,end,'também: SQL Server · Delphi · Framer Motion · JSON Schema · AWS',47 if mobile else 80,17,MUTED,24)
    p+=footer(w,h,'18 ferramentas + fundamentos','[03]')
    return panel(w,h,'[03] ~/stack','FERRAMENTAS',p,still,'Tecnologias de aplicações, dados, APIs, entrega e interface.')


def quality(cfg,root,mobile,still):
    w,h=(600,800) if mobile else (1000,462)
    p=[text(32,94,'Implementar. Validar. Medir.',26)]
    groups=[('01','Qualidade',['Contratos JSON Schema / OpenAPI','Testes e automação de APIs','Asserções com Postman / Runner']),
            ('02','Arquitetura',['Node.js e PHP / Laravel','React, TypeScript e Tailwind','Consultas SQL e sistemas legados']),
            ('03','Resiliência',['Idempotência e HMAC-SHA256','Injeção de latência e falhas','Métricas de desempenho e SLA'])]
    for i,(index,label,items) in enumerate(groups):
        y=127+(i*204 if mobile else 0);x=32 if mobile else 32+i*317
        p += [box(x,y,536 if mobile else 301,184 if mobile else 240,'#111111',EDGE,8),text(x+20,y+32,index+' / '+label,20)]
        for j,item in enumerate(items):
            p += wrapped(x+20,y+73+j*(35 if mobile else 49),item,39 if mobile else 23,18 if mobile else 16,MUTED,23)
        # A small moving trace, with text and all assertions independent of it.
        track=f'M{x+20} {y+(163 if mobile else 217)}H{x+(516 if mobile else 281)}'
        p += [path(track,EDGE,1),path(track,ACCENT,1.5,stroke_dasharray='12 108',class_='dash')]
    p += footer(w,h,'engenharia em cada entrega','[04]')
    return panel(w,h,'[04] ~/engenharia','QUALIDADE / ARQUITETURA',p,still,'Qualidade, arquitetura e resiliência. Contratos, automação, consultas SQL, idempotência, HMAC e métricas.')


def certifications(cfg,root,mobile,still):
    w,h=(600,635) if mobile else (1000,398)
    p=[text(32,94,'Aprendizado contínuo.',27)]
    for i,(name,title) in enumerate(cfg['certifications']):
        col,row=(0,i) if mobile else (i%2,i//2)
        x=32+col*475;y=123+row*(111 if mobile else 108)
        p += [box(x,y,536 if mobile else 461,96,'#111111',EDGE,8),circle(x+30,y+31,12,EDGE),path(f'M{x+24} {y+30}l4 4l8 -8',ACCENT,1.5),text(x+54,y+37,name,18)]
        p += wrapped(x+20,y+69,title,39 if mobile else 35,17,MUTED,21)
    p += footer(w,h,'segurança · cloud · desenvolvimento','[05]')
    return panel(w,h,'[05] ~/certificações','APRENDIZADO',p,still,'Certificações: '+ '; '.join(' '.join(v) for v in cfg['certifications']))


def contributions(cfg,root,mobile,still):
    snap=json.loads((root/'assets'/'contributions.json').read_text(encoding='utf-8'))
    days=snap['days'];best=run=0
    for day in days:
        run=run+1 if day['count'] else 0;best=max(best,run)
    recent=days[:-1] if days[-1]['count']==0 else days
    current=0
    for day in reversed(recent):
        if not day['count']:break
        current+=1
    w,h=(600,752) if mobile else (1000,460)
    p=[text(32,97,'Constância, um commit de cada vez.',23 if mobile else 27)]
    metrics=[(str(snap['total']),'contribuições / ano'),(str(current)+' dias','sequência atual'),(str(best)+' dias','maior sequência')]
    for i,(value,label) in enumerate(metrics):
        x=32+i*(184 if mobile else 316)
        p += [box(x,123,170 if mobile else 302,87,'#111111',EDGE,7),text(x+16,162,value,27),text(x+16,189,label,11 if mobile else 14,MUTED)]
    start=dt.date.fromisoformat(days[0]['date']);start-=dt.timedelta(days=(start.weekday()+1)%7)
    weeks=max((dt.date.fromisoformat(d['date'])-start).days//7 for d in days)+1
    colors=['#202020','#494949','#737373','#a9a9a9','#eeeeee']
    for d in days:
        date=dt.date.fromisoformat(d['date']);col,row=divmod((date-start).days,7)
        if mobile:
            block,local=divmod(col,27);x=39+local*19;y=268+block*211+row*20;size=13
        else:x=48+col*17;y=265+row*17;size=11
        p += [f'<g><title>{date.isoformat()}: {d["count"]} contribuições</title>{box(x,y,size,size,colors[d["level"]],"none",2)}</g>']
    if mobile:
        for i in range(2):
            label_start=start+dt.timedelta(weeks=i*27)
            label_end=min(dt.date.fromisoformat(days[-1]['date']),start+dt.timedelta(weeks=min((i+1)*27,weeks),days=-1))
            p.append(text(39,247+i*211,f'{label_start:%m/%Y} — {label_end:%m/%Y}',14,MUTED))
        ly=641
    else:
        for col in range(0,weeks,8):
            p.append(text(48+col*17,245,(start+dt.timedelta(weeks=col)).strftime('%m/%Y'),12,MUTED))
        ly=408
    p += [text(32,ly,'menos',12,DIM)]
    for i,color in enumerate(colors):p.append(box(84+i*18,ly-11,11,11,color,'none',2))
    p.append(text(180,ly,'mais',12,DIM))
    if not still:
        p += [f'<defs><clipPath id="calendar-area"><rect x="32" y="255" width="{w-64}" height="{344 if mobile else 127}"/></clipPath></defs>',
              '<g clip-path="url(#calendar-area)"><g class="sweep" opacity=".05">'+box(0,255,28,344 if mobile else 127,INK,'none',0)+'</g></g>']
    if mobile:p.append(text(32,678,f'{snap["followers"]} seguidores · {snap["repositories"]} repositórios públicos',15,MUTED))
    p += footer(w,h,'atualizado em '+dt.date.fromisoformat(snap['updated']).strftime('%d/%m/%Y'),'[06]')
    status='ATIVIDADE' if mobile else f'{snap["followers"]} seguidores / {snap["repositories"]} repositórios'
    return panel(w,h,'[06] ~/contribuições',status,p,still,f'{snap["total"]} contribuições. Calendário de '+cfg['username']+' atualizado em '+snap['updated'])


def contact(cfg,root,mobile,still):
    w,h=(600,672) if mobile else (1000,414)
    x,y=(32,101) if mobile else (380,130)
    p=[text(x,y,'bora conversar?',34),*wrapped(x,y+43,'Projetos, desenvolvimento ou qualidade.',39 if mobile else 44,20,MUTED)]
    p += [box(x,y+94,536 if mobile else 583,46,'#161616',EDGE,7),text(x+16,y+124,'> '+cfg['email'],19),text(x,y+172,'@ '+cfg['username'],17,MUTED)]
    if mobile:p.append(f'<g transform="translate(150 321)">{object_scene("cube",still)}</g>')
    else:p.append(f'<g transform="translate(32 82)">{object_scene("cube",still)}</g>')
    p += footer(w,h,'vamos construir a próxima ideia','EMAIL ↗')
    return panel(w,h,'[07] ~/contato','PRÓXIMA CONVERSA',p,still,'Bora conversar? '+cfg['email']+' · '+cfg['username'])


def buttons(out):
    for slug,label,symbol in [('portfolio','portfólio','↗'),('linkedin','linkedin','in'),('email','email','@'),('github','github','<>')]:
        svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="240" height="70" viewBox="0 0 240 70" role="img" aria-labelledby="title"><title id="title">{label}</title><style>text{{font-family:{FONT}}}</style>{box(1,1,238,68,'#111111',EDGE,8)}{text(20,43,symbol,22,ACCENT)}{text(61,42,label,18)}{text(218,42,'↗',16,DIM,'end')}</svg>'''
        (out/f'btn-{slug}.svg').write_text(svg,encoding='utf-8')
        compact=f'''<svg xmlns="http://www.w3.org/2000/svg" width="120" height="100" viewBox="0 0 120 100" role="img" aria-labelledby="title"><title id="title">{label}</title><style>text{{font-family:{FONT}}}</style>{box(1,1,118,98,'#111111',EDGE,8)}{text(60,41,symbol,27,ACCENT,'middle')}{text(60,79,label,17,INK,'middle')}</svg>'''
        (out/f'btn-{slug}-mobile.svg').write_text(compact,encoding='utf-8')


def generate(cfg,root,out):
    out.mkdir(parents=True,exist_ok=True)
    for name,renderer in [('hero',hero),('experience',experience),('stack',stack),('quality',quality),('certifications',certifications),('contributions',contributions),('contact',contact)]:
        for mobile in (False,True):
            for still in (False,True):
                suffix=('-mobile' if mobile else '')+('-static' if still else '')
                (out/f'{name}{suffix}.svg').write_text(renderer(cfg,root,mobile,still),encoding='utf-8')
    buttons(out)
