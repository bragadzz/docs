# Documentação da Cube Hosting

Código da documentação pública em [docs.cubehosting.com.br](https://docs.cubehosting.com.br), feita com [Mintlify](https://mintlify.com).

## Rodar local

```bash
npx mint dev
```

Abre em `http://localhost:3000`. Antes de subir, confira os links:

```bash
npx mint broken-links
```

## Publicar

A branch `main` publica sozinha no ar. Trabalhe noutra branch e só junte na `main` quando o conteúdo valer para o que está em produção.

## Onde fica cada coisa

| O quê | Onde |
| --- | --- |
| Configuração (abas, cores, logo, navbar) | `docs.json` |
| Guias | `index.mdx`, `quickstart.mdx`, `cube-json.mdx`, `tutorials/` (passo a passo por caso de uso), `hosting/`, `account/`, `cube-ai.mdx`, `security.mdx` |
| Referência da API | `api-reference/openapi.json` (fonte das rotas, gerado por `python3 scripts/gen-openapi.py`: edite o script, não o JSON) e as páginas em `api-reference/projects/` |
| Erros | `errors.mdx` |
| Resumo para IAs | `llms.txt` |
| Estilo extra | `style.css` |
