# Documentação da Cube Hosting

Site Mintlify. Páginas em MDX com frontmatter; configuração em `docs.json`; rotas da API em `api-reference/openapi.json`, gerado por `scripts/gen-openapi.py` (edite o script e rode `python3 scripts/gen-openapi.py`) (as páginas de `api-reference/projects/` só apontam para ele com `openapi: "MÉTODO /rota"`).

## Regras de texto

- Texto em **pt-BR**, frases curtas, falando com "você". Rotas, campos JSON, códigos de erro, chaves do `cube.json` e endereços do painel em **inglês**.
- Só o que é verdade hoje. Recurso que ainda não existe leva `<Badge color="purple">Em breve</Badge>` ou "em breve".
- Números de planos só do catálogo (`packages/shared/src/planos.ts` do repo `cube-hosting`).
- Nunca comparar com concorrente nem citar tecnologia ou fornecedor interno (servidor, isolamento, rede de proteção, provedor de IA).
- "Cube AI" sem artigo e sem gênero ("Cube AI explica", nunca "ela").
- Ícones da biblioteca `lucide`.

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
