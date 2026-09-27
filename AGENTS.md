# Documentação da Cube Hosting

Site Mintlify. Páginas em MDX com frontmatter; configuração em `docs.json`; rotas da API em `api-reference/openapi.json`, gerado por `scripts/gen-openapi.py` (edite o script e rode `python3 scripts/gen-openapi.py`) (as páginas de `api-reference/projects/` só apontam para ele com `openapi: "MÉTODO /rota"`).

## Regras de texto

- Texto em **pt-BR**, frases curtas, falando com "você". Rotas, campos JSON, códigos de erro, chaves do `cube.json` e endereços do painel em **inglês**.
- Só o que é verdade hoje. Recurso que ainda não existe leva `<Badge color="purple">Em breve</Badge>` ou "em breve".
- Números de planos só do catálogo (`packages/shared/src/planos.ts` do repo `cube-hosting`).
- Nunca comparar com concorrente nem citar tecnologia ou fornecedor interno (servidor, isolamento, rede de proteção, provedor de IA).
- "Cube AI" sem artigo e sem gênero ("Cube AI explica", nunca "ela").
- Ícones da biblioteca `lucide`.

## Playground da API

`api.playground.display` fica `simple` (só o exemplo, sem botão de envio). No modo interativo, a chave `cube_…` que o cliente cola sai do navegador para o servidor do fornecedor da docs antes de chegar à Cube, e todo mundo divide o mesmo IP no limite de chaves erradas. Decisão registrada em cube-hosting#37; só volta a ser interativo com aprovação do dono.

## Conferir

```bash
npx mint dev
npx mint broken-links
python3 scripts/check.py          # repositório
python3 scripts/check.py --live   # depois do deploy: /, /llms.txt e /llms-full.txt sem o Starter Kit
```
