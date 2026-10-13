# Gerador do perfil

Na raiz do repositório, com Python 3.11 ou superior:

```sh
python .github/scripts/build_readme.py
git diff --check
```

Não há dependências de terceiros. `assets/profile.json` define o conteúdo;
`build_readme.py` monta o README; `project_cards.py` desenha as cenas dos
projetos e fornece a paleta e as primitivas; `profile_cards.py` desenha as demais
seções e as formas 3D. Edite essas fontes, pois a geração sobrescreve os SVGs
e o README. O workflow diário usa o mesmo gerador e preserva os novos cartões.

Cada seção possui quatro SVGs: desktop, celular (`-mobile`), desktop estático
(`-static`) e celular estático (`-mobile-static`). O `<picture>` seleciona a
versão compacta até 600 px e prioriza as imagens estáticas quando o visitante
prefere movimento reduzido. As animações também respeitam essa preferência
dentro do SVG. Sem animação, o primeiro quadro mantém o conteúdo visível.
Os botões também têm uma versão compacta, com ícone acima do texto, para manter
os quatro links legíveis no celular; ambas as versões são estáticas.

A paleta é estritamente em escala de cinza: valores RGB iguais em cada cor.
Fone e cubo são malhas originais projetadas em perspectiva, com iluminação,
profundidade e 60 poses por volta de seis segundos. O cubo combina uma estrutura
externa com um núcleo sombreado e uma grade que acompanha as faces. A geração
estática guarda apenas uma pose; nenhum conteúdo depende da rotação.

As cenas são ilustrações dos recursos, não telemetria em tempo real. Não usam
JavaScript, fontes remotas ou imagens externas. O ERP representa experiência
profissional e permanece sem link de repositório. Agente Pedro descreve o
aplicativo para Windows, sem atribuir a ele recursos de IA.

Para revisar, confira todas as seções em desktop e celular, com e sem
movimento reduzido: textos dentro dos limites, links corretos e animações
restritas às ilustrações. Confira também que os tons permanecem em cinza e que
os objetos 3D giram sem quadros vazios. A versão textual completa fica disponível
no final do README. O calendário mantém os dados e a data da última atualização;
o visual não cria atividade fictícia.

`--refresh` consulta o GitHub e atualiza o calendário de contribuições;
não é necessário para alterar o conteúdo ou o visual dos projetos.
