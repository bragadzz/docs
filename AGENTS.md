# Documentação da Cube Hosting

Site Mintlify. Páginas em MDX com frontmatter; configuração em `docs.json`; rotas da API em `api-reference/openapi.json` (as páginas de `api-reference/projects/` só apontam para ele com `openapi: "MÉTODO /rota"`).

## Regras de texto

- Texto em **pt-BR**, frases curtas, falando com "você". Rotas, campos JSON, códigos de erro, chaves do `cube.json` e endereços do painel em **inglês**.
- Só o que é verdade hoje. Recurso que ainda não existe leva `<Badge color="purple">Em breve</Badge>` ou "em breve".
- Números de planos só do catálogo (`packages/shared/src/planos.ts` do repo `cube-hosting`).
- Nunca comparar com concorrente nem citar tecnologia ou fornecedor interno (servidor, isolamento, rede de proteção, provedor de IA).
- "Cube AI" sem artigo e sem gênero ("Cube AI explica", nunca "ela").
- Ícones da biblioteca `lucide`.

## Conferir

```bash
npx mint dev
npx mint broken-links
```
