#!/usr/bin/env python3
"""Generate monochrome, responsive GitHub README SVGs. Python 3.11+, no dependencies."""
import argparse
import datetime as dt
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.request

from profile_cards import generate as generate_profile
from project_cards import generate as generate_projects

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets'
CFG = json.loads((OUT / 'profile.json').read_text(encoding='utf-8'))


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


def readme():
    def image(name,alt,url=None,width='100%'):
        tag=f'<img src="./assets/{name}.svg" width="{width}" alt="{html.escape(alt,quote=True)}" />'
        if name.startswith('btn-'):
            tag = (f'<picture><source media="(max-width: 600px)" srcset="./assets/{name}-mobile.svg" />'
                   f'{tag}</picture>')
        else:
            tag = (f'<picture>'
                   f'<source media="(prefers-reduced-motion: reduce) and (max-width: 600px)" srcset="./assets/{name}-mobile-static.svg" />'
                   f'<source media="(prefers-reduced-motion: reduce)" srcset="./assets/{name}-static.svg" />'
                   f'<source media="(max-width: 600px)" srcset="./assets/{name}-mobile.svg" />'
                   f'{tag}</picture>')
        return f'<a href="{html.escape(url,quote=True)}">{tag}</a>' if url else tag
    pieces=['<!-- Gerado por .github/scripts/build_readme.py. Configuração: assets/profile.json. -->','<p align="center">',
            image('hero',CFG['name']+' · '+CFG['headline']+'. '+' '.join(CFG['intro']+CFG['about']),CFG['portfolio'])]
    for slug,label,url in [('portfolio','Portfólio',CFG['portfolio']),('linkedin','LinkedIn',CFG['linkedin']),('email','Email','mailto:'+CFG['email']),('github','GitHub','https://github.com/'+CFG['username'])]:
        pieces.append(image('btn-'+slug,label,url,'24%'))
    for p in CFG['projects']:pieces.append(image('proj-'+p['slug'],p['name']+' · '+' '.join(p['lines'])+' Stack: '+p['stack'],p['url']))
    pieces.extend([image('proj-erp','Retaguarda ERP · Painéis corporativos, RBAC e otimização de consultas. Laravel, React, TypeScript, SQL Server e Docker.'),
                   image('experience','SETE Tecnologia: estágio em QA / Testes. Qualisoft: estágio em Back-end / Full Stack. Engenharia de Software na UniFanor Wyden.'),
                   image('stack','React, TypeScript, JavaScript, Node.js, PHP, Laravel, Fastify, Prisma, PostgreSQL, Supabase, Postman, OpenAPI, Tailwind, Vite, Docker, Git, GitHub, Vercel. Também: SQL Server, Delphi, Framer Motion, JSON Schema e AWS.'),
                   image('quality','Engenharia de qualidade, arquitetura e resiliência: contratos de API, automação de testes, SQL, idempotência, webhooks assinados e métricas de desempenho.'),
                   image('certifications','Certificações: '+ '; '.join(a+' '+b for a,b in CFG['certifications'])),
                   image('contributions','Contribuições no GitHub de '+CFG['username']+' — calendário atualizado automaticamente.','https://github.com/'+CFG['username']+'?tab=overview'),
                   image('contact','Bora conversar? '+CFG['email']+' · '+CFG['username'],'mailto:'+CFG['email']),'</p>',
                   '', '<details>', '<summary>Perfil completo em texto</summary>', '', '### '+CFG['name'], '',
                   'Desenvolvedor Full Stack e Analista de QA, graduando em Engenharia de Software na UniFanor Wyden.', '',
                   '- **SETE Tecnologia:** estágio em QA / Testes para logística aduaneira e portuária; SQL Server, Postman e validação de APIs.',
                   '- **Qualisoft Sistemas:** estágio em Back-end / Full Stack; Laravel, React, TypeScript, consultas SQL e manutenção de sistemas Delphi.', '', '### Projetos', ''])
    for p in CFG['projects']:pieces.append(f'- **[{p["name"]}]({p["url"]}):** '+ ' '.join(p['lines'])+' '+p['stack']+'.')
    pieces.extend(['- **Retaguarda ERP:** experiência com painéis corporativos, permissões RBAC e bancos relacionais.', '',
                   '### Tecnologias e engenharia', '',
                   'React, TypeScript, JavaScript, Node.js, PHP, Laravel, Fastify, Prisma, PostgreSQL, Supabase, Postman, OpenAPI, Tailwind, Vite, Docker, Git, GitHub e Vercel.', '',
                   'Também: SQL Server, Delphi, Framer Motion, JSON Schema e AWS. Contratos de API, automação de testes, arquitetura, idempotência, webhooks assinados, métricas e resiliência.', '',
                   '### Certificações', '',
                   *['- **'+name+':** '+title for name,title in CFG['certifications']], '',
                   f'[Portfólio]({CFG["portfolio"]}) · [LinkedIn]({CFG["linkedin"]}) · [Email](mailto:{CFG["email"]})', '', '</details>', '',
                   '<sub>Visual inspirado no perfil de <a href="https://github.com/vitorcgo/vitorcgo">vitorcgo</a>; cartões e gerador personalizados. Ícones: <a href="https://simpleicons.org">Simple Icons</a>.</sub>', ''])
    (ROOT/'README.md').write_text('\n'.join(pieces),encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true', help='Atualiza as contribuições públicas do GitHub antes de gerar.')
    args = parser.parse_args()
    if args.refresh:
        refresh_calendar()
    generate_profile(CFG, ROOT, OUT)
    generate_projects(CFG['projects'], OUT)
    readme()
    print('README e cartões monocromáticos gerados em assets/.')


if __name__ == '__main__':
    main()
