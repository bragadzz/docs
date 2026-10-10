# Documentação da Cube Hosting

Site Mintlify. Páginas em MDX com frontmatter; configuração em `docs.json`; rotas da API em `api-reference/openapi.json`, gerado por `scripts/gen-openapi.py` (edite o script e rode `python3 scripts/gen-openapi.py`) (as páginas de `api-reference/projects/` só apontam para ele com `openapi: "MÉTODO /rota"`).

## Regras de texto

- Texto em **pt-BR**, frases curtas, falando com "você". Rotas, campos JSON, códigos de erro, chaves do `cube.json` e endereços do painel em **inglês**.
- Só o que é verdade hoje. Recurso que ainda não existe leva `<Badge color="purple">Em breve</Badge>` ou "em breve".
- Números de planos só do catálogo (`packages/shared/src/planos.ts` do repo `cube-hosting`).
- Nunca comparar com concorrente nem citar tecnologia ou fornecedor interno (servidor, isolamento, rede de proteção, provedor de IA).
  - Exceção funcional (decisão do dono, 29/09/2026): a seção "Vindo de outra hospedagem" do `cube-json.mdx` lista os nomes dos arquivos de configuração que a Cube lê (`squarecloud.app`, `discloud.config`, `.shardcloud`) e as chaves de cada um, sem comparar nada.
- "Cube AI" sem artigo e sem gênero ("Cube AI explica", nunca "ela").
- Ícones da biblioteca `lucide`.

## Títulos e tutoriais

- O `title` da página que responde a uma busca é a frase que a pessoa digita ("Como hospedar um bot do Discord: passo a passo"), e o `sidebarTitle` guarda o nome curto do menu. O endereço da página nunca muda. A `description` tem até 155 caracteres e responde a busca.
- `tutorials/` tem um guia passo a passo por caso de uso (grupo **Tutoriais** do `docs.json`). Cada passo vale no produto de hoje, conferido no código do `cube-hosting`. O guia termina com o link para a landing do site (`https://cubehosting.com.br/hospedagem-…`, só a que responde 200) e entra no `llms.txt`; o `check.py` confere a navegação, o `llms.txt` e o tamanho da descrição.
- O HTML servido sai com `<html lang="en">`, fixo do fornecedor da docs. O `"language": "pt-BR"` do `docs.json` traduz a interface e faz o navegador trocar o atributo para `pt-BR` ao carregar a página. O HTML servido só muda com as páginas sob o prefixo `/pt-BR/`, o que trocaria todos os endereços: não mexer sem decisão do dono (cube-hosting#113).

## Erros e Solução de problemas

- `/errors` é a página única de códigos (decisão do dono na cube-hosting#37). Cada página de rota da Referência da API termina com a tabela **Erros comuns** (`Código | HTTP | O que fazer`, o código com link para `/errors#param-<código com hífens>`); o `check.py` confere que a rota devolve aquele código com aquele HTTP no `openapi.json`.
- `troubleshooting/` tem uma página por tema. Cada erro é um `##` com a **mensagem literal** que a Cube ou o log mostra, seguido de **O que significa**, **Por que acontece**, **Como corrigir** (passos) e um exemplo curto. Só verdade sobre a Cube.
- **O painel linka essas âncoras** ("Como resolver", `apps/app/lib/docs-links.ts` do `cube-hosting-web`, com teste que confere cada âncora na docs publicada). Mudou o texto de um título de `troubleshooting/` ou tirou uma seção? Atualize o mapa do painel no mesmo dia.

## Playground da API

`api.playground.display` fica `simple` (só o exemplo, sem botão de envio). No modo interativo, a chave `cube_…` que o cliente cola sai do navegador para o servidor do fornecedor da docs antes de chegar à Cube, e todo mundo divide o mesmo IP no limite de chaves erradas. Decisão registrada em cube-hosting#37; só volta a ser interativo com aprovação do dono.

## Conferir

```bash
npx mint dev
npx mint broken-links
python3 scripts/check.py          # repositório
python3 scripts/check.py --live   # depois do deploy: /, /llms.txt e /llms-full.txt sem o Starter Kit, os endereços da página CLI, SDKs e MCP, o MCP respondendo e o /llms-full.txt com todas as páginas do docs.json
```

O `/llms-full.txt` fica até 1 dia no cache da docs (`max-age=86400`) e publicar não o renova. Depois de publicar uma página nova, o `--live` falha na última conferência até o cache vencer: a mensagem diz quanto falta e se a versão nova já está pronta na origem.
