# Gerador do perfil

Na raiz do repositório, com Python 3.11 ou superior:

```sh
python .github/scripts/build_readme.py
git diff --check
```

Não há dependências de terceiros. `assets/profile.json` define o conteúdo;
`build_readme.py` monta o README e as demais seções; `project_cards.py` desenha
as cenas dos projetos. Edite essas fontes, pois a geração sobrescreve os SVGs
e o README. O workflow diário usa o mesmo gerador e preserva os novos cartões.

Cada projeto possui quatro SVGs: desktop, celular (`-mobile`), desktop estático
(`-static`) e celular estático (`-mobile-static`). O `<picture>` seleciona a
versão compacta até 600 px e prioriza as imagens estáticas quando o visitante
prefere movimento reduzido. As animações também respeitam essa preferência
dentro do SVG. Sem animação, o primeiro quadro mantém o conteúdo visível.

As cenas são ilustrações dos recursos, não telemetria em tempo real. Não usam
JavaScript, fontes remotas ou imagens externas. O ERP representa experiência
profissional e permanece sem link de repositório. Agente Pedro descreve o
aplicativo para Windows, sem atribuir a ele recursos de IA.

Para revisar, confira todos os cartões em desktop e celular, com e sem
movimento reduzido: textos dentro dos limites, links corretos e animações
restritas às ilustrações. A versão textual fica disponível no final do README.

`--refresh` consulta o GitHub e atualiza o calendário de contribuições;
não é necessário para alterar o conteúdo ou o visual dos projetos.
