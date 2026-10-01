import json
import os

BASE = "https://app.cubehosting.com.br/api"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api-reference", "openapi.json")

KEY_H = '-H "Authorization: Bearer $CUBE_API_KEY"'
NODE_HEAD = (
    "const API = '" + BASE + "';\n"
    "const headers = { Authorization: `Bearer ${process.env.CUBE_API_KEY}` };\n\n"
)
PY_HEAD = (
    'API = "' + BASE + '"\n'
    "headers = {\"Authorization\": f\"Bearer {os.environ['CUBE_API_KEY']}\"}\n\n"
)


def samples(curl, node, python, node_imports="", py_imports=("os", "requests")):
    """Imports sempre no topo, antes das constantes."""
    node_top = node_imports + "\n" if node_imports else ""
    py_top = "".join(f"import {m}\n" for m in py_imports) + "\n"
    return [
        {"lang": "bash", "label": "curl", "source": curl},
        {"lang": "javascript", "label": "Node.js", "source": node_top + NODE_HEAD + node},
        {"lang": "python", "label": "Python", "source": py_top + PY_HEAD + python},
    ]


def err(code, message, **extra):
    return {"status": "error", "code": code, "message": message, **extra}


def resp(desc, examples):
    """Resposta de erro com um ou mais exemplos (code → corpo)."""
    ex = {code: {"summary": code, "value": body} for code, body in examples}
    return {
        "description": desc,
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}, "examples": ex}},
    }


def ref(name):
    return {"$ref": f"#/components/schemas/{name}"}


PROJECT_EXAMPLE = {
    "id": "01J8Z3W6N0Q4Y7V2K5T9D1H3XA",
    "name": "Meu bot",
    "description": "Atende o servidor da loja",
    "type": "bot",
    "language": "node",
    "version": "24",
    "entry": "index.js",
    "command": "node index.js",
    "root": None,
    "systemPackages": [],
    "memoryMb": 256,
    "port": None,
    "subdomain": None,
    "url": None,
    "internalHost": "cube-t9d1h3xa",
    "status": "running",
    "error": None,
    "hasAutoRestart": True,
    "consecutiveCrashes": 0,
    "lastExit": None,
    "usage": {"memoryMb": 83, "cpuPercent": 1.2, "networkInBps": 1200, "networkOutBps": 300},
    "startedAt": "2026-09-26T18:01:05.000Z",
    "templateId": None,
    "restoredFromBackupId": None,
    "createdAt": "2026-09-26T18:00:00.000Z",
    "updatedAt": "2026-09-26T18:01:10.000Z",
}
SITE_EXAMPLE = {
    **PROJECT_EXAMPLE,
    "id": "01J8Z4B2QK7M3V9T0XW5R6N8CD",
    "internalHost": "cube-w5r6n8cd",
    "name": "Loja",
    "description": "",
    "type": "site",
    "entry": "dist/server.js",
    "command": "node dist/server.js",
    "memoryMb": 512,
    "port": 3000,
    "subdomain": "minha-loja",
    "url": "https://minha-loja.cubehost.dev",
    "usage": {"memoryMb": 141, "cpuPercent": 3.4, "networkInBps": 5200, "networkOutBps": 48000},
}
INSTALLING = {**PROJECT_EXAMPLE, "status": "installing", "usage": None, "startedAt": None}
STOPPED = {**PROJECT_EXAMPLE, "status": "stopped", "usage": None, "startedAt": None,
           "lastExit": {"code": 143, "isOutOfMemory": False, "exitedAt": "2026-09-26T19:30:00.000Z"}}

# A lista fechada dos pacotes do sistema (SYSTEM_PACKAGES do packages/shared do cube-hosting).
SYSTEM_PACKAGES = ['build-essential', 'curl', 'fonts-dejavu-core', 'fonts-liberation', 'fonts-noto-cjk', 'fonts-noto-color-emoji', 'ghostscript', 'git', 'graphviz', 'imagemagick', 'libvips-tools', 'poppler-utils', 'python3', 'sqlite3', 'tesseract-ocr', 'tesseract-ocr-por', 'unzip', 'zip']

# Erros comuns
E_KEY = ("invalid_api_key", err("invalid_api_key", 'Chave de API inválida ou revogada. Confira o cabeçalho "Authorization: Bearer <chave>" ou crie outra em Chaves de API no painel.'))
E_PERM = ("insufficient_permission", err("insufficient_permission", "Esta chave é só de leitura. Para enviar, iniciar, parar, reiniciar, mexer nas variáveis, fazer, baixar e restaurar backups, baixar e voltar versões dos envios, criar, ligar, desligar, fazer backup e ver a senha dos bancos de dados ou enviar e apagar arquivos do Blob, crie uma chave de leitura e escrita no painel."))
E_404 = ("not_found", err("not_found", "Projeto não encontrado."))
E_RATE = ("rate_limit_exceeded", err("rate_limit_exceeded", "A sua conta passou do limite da API do plano Free: 10 pedidos por minuto. Espere 42 s e tente de novo."))
E_MANY = ("too_many_requests", err("too_many_requests", "Muitas requisições seguidas. Espere alguns segundos e tente de novo."))
E_ATT = ("too_many_attempts", err("too_many_attempts", "Muitas tentativas. Tente de novo em 15 minutos."))
E_BUSY = ("project_busy", err("project_busy", "O projeto está sendo preparado ou já tem outra ação em andamento. Espere terminar."))
# Projeto de template sem a variável obrigatória dele (cube-hosting#40): não sobe.
E_MISSING_VARS = ("missing_variables", err("missing_variables", "Este projeto veio de um template e precisa de DISCORD_TOKEN para iniciar. Defina em Variáveis de ambiente e inicie de novo.", missingVariables=["DISCORD_TOKEN"]))
E_SUSP = ("account_suspended", err("account_suspended", "Sua conta está suspensa porque o Pix da renovação não foi pago, então os projetos ficam parados. Pague em Plano e cobrança: a conta volta na hora, e o que estava no ar sobe sozinho."))
E_BETA = ("beta_ending", err("beta_ending", "Seu beta terminou e a conta está voltando ao plano Free. Espere alguns minutos e tente de novo."))
# A Conta no Free perdeu a vaga do /free pela meta da semana (cube-hosting#21): nada sobe no Free.
E_FREE_LOST = ("free_slot_lost", err("free_slot_lost", "Sua vaga do Free acabou porque a meta de mensagens da semana no Discord não foi batida, então os projetos ficam parados. Os arquivos continuam guardados: assine um plano em Plano e cobrança para ligar de novo."))
E_SUSP_MANUAL = ("account_suspended_manually", err("account_suspended_manually", "Sua conta foi suspensa pela equipe da Cube: Página de phishing em loja.cubehost.dev. Os projetos ficam parados e nada sobe até a suspensão sair. Fale com o suporte no Discord para resolver."))
E_503 = ("server_unavailable", err("server_unavailable", "O servidor dos projetos não respondeu. Tente de novo em instantes."))

R401 = resp("Chave ausente, inválida ou revogada.", [E_KEY])
R403_WRITE = resp("A chave é só de leitura.", [E_PERM])
R404 = resp("O projeto não existe ou não é da sua conta.", [E_404])
R429 = resp("Limite de pedidos. Traz o cabeçalho `Retry-After`.", [E_RATE, E_ATT])
R429_HEAVY = resp("Limite de pedidos. Traz o cabeçalho `Retry-After`.", [E_RATE, E_MANY, E_ATT])
R503 = resp("O servidor dos projetos não respondeu a tempo. Nada foi alterado.", [E_503])
E_VARS = ("variables_unavailable", err("variables_unavailable", "As variáveis de ambiente do projeto não puderam ser abertas agora. Tente de novo em instantes."))
R503_VARS = resp("O servidor dos projetos não respondeu, ou as variáveis de ambiente não abriram (o projeto não sobe sem elas). Nada foi alterado.", [E_503, E_VARS])

ID_PARAM = {"$ref": "#/components/parameters/ProjectId"}

ZIP_413 = resp("O .zip passou do limite do plano (5 MB no Free, 10 MB nos pagos).", [
    ("invalid_zip", err("invalid_zip", "O zip passa do limite de 5 MB do plano Free. Tire as dependências (elas são instaladas aqui) e arquivos que o projeto não usa.", limitMb=5)),
])

paths = {}

# Templates (cube-hosting#40): a lista do GET /templates.
TOKEN_VAR = {
    "name": "DISCORD_TOKEN",
    "description": "O token do bot, do Portal de Desenvolvedores do Discord.",
    "isRequired": True,
    "helpUrl": "https://docs.cubehosting.com.br/hosting/templates#como-pegar-o-token-do-bot",
}
NO_EXTRAS = {"minimumMemoryMb": None, "minimumPlan": None, "connection": None}
TEMPLATE_EXAMPLES = [
    {"id": "discord-js-bot", "name": "Bot discord.js", "description": "Um bot de Discord em Node.js com o comando /ping, pronto para você criar os seus.", "type": "bot", "language": "node", "version": "24", "memoryMb": 256, "port": None, "variables": [TOKEN_VAR], "database": None, **NO_EXTRAS},
    {"id": "lavalink", "name": "Lavalink", "description": "O servidor de música dos seus bots, com YouTube, SoundCloud e rádios. Privado: só os projetos da sua conta conectam nele.", "type": "bot", "language": "java", "version": "21", "memoryMb": 512, "port": None, "variables": [], "database": None, "minimumMemoryMb": 512, "minimumPlan": {"id": "block", "name": "Block"}, "connection": {"port": 2333, "passwordVariable": "LAVALINK_SERVER_PASSWORD"}},
    {"id": "discord-postgres-bot", "name": "Bot com PostgreSQL", "description": "Um bot de Discord que guarda anotações num PostgreSQL da sua conta, criado junto e já ligado ao projeto.", "type": "bot", "language": "node", "version": "24", "memoryMb": 256, "port": None, "variables": [TOKEN_VAR], "database": {"engine": "postgres", "variable": "DATABASE_URL", "memoryMb": 512}, **NO_EXTRAS},
    {"id": "express-api", "name": "API Express", "description": "Uma API em Node.js com Express, no ar num endereço .cubehost.dev.", "type": "site", "language": "node", "version": "24", "memoryMb": 512, "port": 8080, "variables": [], "database": None, **NO_EXTRAS},
]
TEMPLATE_IDS = ["discord-js-bot", "discord-py-bot", "discord-music-bot", "lavalink", "discord-postgres-bot", "express-api", "fastapi-api", "static-site"]

# GET /projects
paths["/projects"] = {
    "get": {
        "operationId": "listProjects",
        "summary": "Listar projetos",
        "description": "Todos os projetos da conta, do mais novo para o mais antigo, sem paginação. O `usage` vem preenchido só nos projetos `running`.",
        "tags": ["Projetos"],
        "x-codeSamples": samples(
            f"curl {BASE}/projects \\\n  {KEY_H}",
            "const res = await fetch(`${API}/projects`, { headers });\n"
            "if (!res.ok) throw new Error((await res.json()).message);\n"
            "const { projects } = await res.json();\n"
            "for (const p of projects) console.log(p.id, p.name, p.status);",
            'r = requests.get(f"{API}/projects", headers=headers, timeout=30)\n'
            "r.raise_for_status()\n"
            'for p in r.json()["projects"]:\n'
            '    print(p["id"], p["name"], p["status"])',
        ),
        "responses": {
            "200": {
                "description": "A lista de projetos.",
                "content": {"application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["accountId", "projects"],
                        "properties": {
                            "accountId": {"type": "string", "format": "uuid", "description": "O ID público da sua conta, o mesmo de Minha conta."},
                            "projects": {"type": "array", "items": ref("Project")},
                        },
                    },
                    "example": {"accountId": "5f0c2a1e-8d4b-4c7e-9a31-2b6d0e9f7c14", "projects": [SITE_EXAMPLE, PROJECT_EXAMPLE]},
                }},
            },
            "401": R401,
            "429": R429,
        },
    },
    "post": {
        "operationId": "createProject",
        "summary": "Criar um projeto",
        "description": (
            "Envia um `.zip` e cria o projeto. A Cube extrai o código, lê a configuração e começa a instalar as dependências: "
            "a resposta chega com o projeto em `installing`. Acompanhe pelo [projeto](/api-reference/projects/get) ou pelos "
            "[logs](/api-reference/projects/logs) com `source=build`.\n\n"
            "A configuração vem do `cube.json` na raiz do `.zip`. Se o formulário trouxer `language` e `command` (ou `language` e `entry`, e o comando sai do arquivo principal; ou só `language`, no `static`, no `go`, no `elixir` e no `php`), o formulário vale "
            "e o `cube.json` é ignorado. Sem `cube.json`, vale o arquivo de configuração de outra hospedagem na raiz (`squarecloud.app`, `squarecloud.config`, "
            "`discloud.config` ou `.shardcloud`), traduzido para as mesmas chaves ([Vindo de outra hospedagem](/cube-json#vindo-de-outra-hospedagem)). "
            "Sem nada disso, um `.zip` só de HTML (o `index.html` na raiz e nenhum `package.json`, `requirements.txt`, `pyproject.toml`, `go.mod`, `composer.json`, `Gemfile`, `mix.exs` nem projeto do .NET) "
            "vira [site estático](/hosting/static-site): a Cube serve os arquivos, sem comando, versão nem build; o `go.mod` sem outro manifesto vira [Go](/hosting/go) "
            "(compilado a cada envio), o `composer.json` sem outro manifesto (o `package.json` do Vite do Laravel pode vir junto) vira um [site PHP](/hosting/php) servido pela Cube, o único projeto do .NET na raiz (`.csproj`, `.fsproj`, `.vbproj`) vira [.NET](/hosting/dotnet) com ele de `entry`, o `mix.exs` vira [Elixir](/hosting/elixir) com `mix run --no-halt` e um único `.jar` na raiz, sem manifesto, vira [Java](/hosting/java) com `java -jar`. "
            "Com o manifesto de outra linguagem só (o `Gemfile` do Ruby, a solução do .NET sem projeto na raiz), `422 missing_config` diz a linguagem e pede o comando. Um envio a cada 3 segundos por conta.\n\n"
            "Com `template` no lugar do `file`, o projeto nasce de um [template](/hosting/templates) da Cube: o código vem do template "
            "e o `cube.json` dele preenche o que o formulário não trouxer. As variáveis que ele pede vão em `variables`; sem uma "
            "obrigatória, o projeto instala e fica `stopped` mesmo com `start=true`, e `missingVariables` diz o que falta: até ela ter valor, "
            "[iniciar](/api-reference/projects/start) responde `409 missing_variables`. Sem `memoryMb`, vale a memória sugerida do template, "
            "cortada no que sobra no plano e nunca abaixo do mínimo dele. O [Lavalink](/hosting/lavalink) pede 512 MB (`403 template_not_in_plan` no Free, "
            "`422 invalid_config` abaixo disso) e a senha dele é gerada pela Cube, na variável `LAVALINK_SERVER_PASSWORD` (a que viesse em `variables` é descartada).\n\n"
            "A memória mínima depende do plano: bot **256 MB** nos planos pagos e **100 MB** no Free; site ou API **512 MB**; Java, **256 MB** em qualquer plano (no Free, `403 language_not_in_plan`). "
            "Sem `memoryMb` (no formulário e no `cube.json`), vale o mínimo do plano; abaixo dele, `422 invalid_config` com "
            "`field: \"memoryMb\"` e `minMemoryMb`. Os mínimos e quanto cabe em cada plano estão em [Listar planos](/api-reference/plans/list)."
        ),
        "tags": ["Projetos"],
        "requestBody": {
            "required": True,
            "content": {"multipart/form-data": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "file": {"type": "string", "format": "binary", "description": "O `.zip` com o código. Até 5 MB no Free e 10 MB nos planos pagos. Obrigatório, a não ser com `template`."},
                        "template": {"type": "string", "enum": TEMPLATE_IDS, "description": "Um [template](/hosting/templates) da Cube no lugar do `file` (a lista em [Listar templates](/api-reference/templates/list)). Com os dois, nada é criado."},
                        "variables": {"type": "string", "description": "Variáveis de ambiente gravadas antes da primeira subida, em JSON: `[{\"name\": \"DISCORD_TOKEN\", \"value\": \"...\"}]`. Até 50, com as regras de [Definir variáveis](/api-reference/projects/set-variables)."},
                        "start": {"type": "string", "enum": ["true", "false"], "default": "false", "description": "`true` inicia o projeto assim que a instalação terminar."},
                        "name": {"type": "string", "minLength": 1, "maxLength": 40, "description": "Nome do projeto. Vale se o `cube.json` não tiver `name`; sem nenhum, vira o nome do arquivo."},
                        "type": {"type": "string", "enum": ["bot", "site"], "description": "Mesmo significado da chave do `cube.json`."},
                        "language": {"type": "string", "enum": ["node", "python", "java", "go", "php", "ruby", "dotnet", "elixir", "static"], "description": "Com `language` e `command` (ou `language` e `entry`; ou só `language` no `static`, o [site só de HTML](/hosting/static-site), no `go`, no `elixir` e no `php`), o formulário vale e o `cube.json` é ignorado."},
                        "version": {"type": "string", "description": "`20`, `22`, `24` ou `26` (Node.js; sem ela, `24`; o `20` está fora de suporte); `3.11`, `3.12`, `3.13` ou `3.14` (Python; sem ela, `3.12`); `21` ou `25` (Java; sem ela, `21`); `1.26` ou `1.27` (Go; sem ela, `1.27`); `8.4` ou `8.5` (PHP; sem ela, `8.4`); `3.4` ou `4.0` (Ruby; sem ela, `3.4`); `10` (.NET); `1.20` (Elixir)."},
                        "command": {"type": "string", "maxLength": 500, "description": "Comando de início, numa linha só. No `go` é opcional: sem ele, roda o programa que o build gera (`/dados/bin/app`). No site `php` também: sem ele, a Cube serve o site (`cube-php-server`, com a pasta `root` ou a `public`). No `elixir` também: sem ele, `mix run --no-halt`. Sem ele, com o `entry`, o comando sai do arquivo principal (no `dotnet`, o `.dll` publicado do projeto, `dotnet /dados/publish/<projeto>.dll`, ou o `.dll` pronto, `dotnet <entry>`)."},
                        "entry": {"type": "string", "maxLength": 200, "description": "O arquivo principal, com a extensão da linguagem (como `cmd/bot/main.go`, `src/Api/Api.csproj` ou `app.dll`). No `go`, é a pasta que o build compila (sem ele, a raiz do `.zip`); no `dotnet`, o projeto que o build publica, em qualquer pasta (sem ele, o único projeto ou a solução da raiz), ou um `.dll` pronto, que roda sem build. Sem `command`, o comando sai dele. Fora do formato, `422 invalid_config` com `field: \"entry\"`."},
                        "memoryMb": {"type": "integer", "minimum": 100, "description": "Memória em MB. O mínimo é o do plano: bot 256 nos planos pagos e 100 no Free; site 512. Sem ela, vale o mínimo do plano; com `template`, a memória sugerida dele, cortada no que sobra e nunca abaixo do mínimo (no Free, o bot entra com 100)."},
                        "port": {"type": "integer", "minimum": 1024, "maximum": 65535, "description": "Só site. Padrão 8080."},
                        "subdomain": {"type": "string", "description": "Só site. Sem ele, a Cube gera um."},
                        "build": {"type": "string", "maxLength": 500, "description": "Comando de build. Ausente = automático; vazio = sem build. O site estático não tem."},
                        "root": {"type": "string", "maxLength": 200, "description": "No site `php` sem `command`: a pasta que a Cube serve (sem ela, a `public` quando existe, senão a raiz). No `static`: a pasta servida, como `dist` (`\"\"` = a raiz). Sem ela, a pasta do `index.html` mais raso do `.zip` (a raiz, ou `dist` quando ele só existe lá). Sem `..` nem pasta que começa com ponto."},
                        "systemPackages": {"type": "string", "description": "[Pacotes do sistema](/cube-json#pacotes-do-sistema), em JSON: `[\"poppler-utils\"]`. Sem ele, valem os `systemPackages` do `cube.json` (também quando o formulário traz `language` e `command`). Nome fora da lista, `422 unsupported_system_package`."},
                        "databaseId": {"type": "string", "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$", "description": "Liga o projeto a um [banco de dados](/hosting/databases) da conta: a string de conexão entra como variável de ambiente antes da primeira subida."},
                        "databaseVariable": {"type": "string", "pattern": "^[A-Za-z_][A-Za-z0-9_]{0,63}$", "description": "O nome da variável com a conexão. Sem ele, o sugerido do banco: `DATABASE_URL` (PostgreSQL e MySQL), `MONGODB_URI` ou `REDIS_URL`."},
                    },
                },
                "encoding": {"file": {"contentType": "application/zip"}},
            }},
        },
        "x-codeSamples": samples(
            f"curl {BASE}/projects \\\n  {KEY_H} \\\n  -F \"file=@meu-bot.zip\" \\\n  -F \"start=true\"",
            "const form = new FormData();\n"
            "form.set('file', await openAsBlob('meu-bot.zip'), 'meu-bot.zip');\n"
            "form.set('start', 'true');\n\n"
            "const res = await fetch(`${API}/projects`, { method: 'POST', headers, body: form });\n"
            "const { project } = await res.json();\n"
            "console.log(project.id, project.status); // installing",
            'with open("meu-bot.zip", "rb") as zip:\n'
            "    r = requests.post(\n"
            '        f"{API}/projects",\n'
            "        headers=headers,\n"
            '        files={"file": ("meu-bot.zip", zip, "application/zip")},\n'
            '        data={"start": "true"},\n'
            "        timeout=300,\n"
            "    )\n"
            "r.raise_for_status()\n"
            'print(r.json()["project"]["id"])',
            node_imports="import { openAsBlob } from 'node:fs';\n",
        ),
        "responses": {
            "201": {
                "description": "Projeto criado, instalando as dependências.",
                "content": {"application/json": {
                    "schema": {"type": "object", "required": ["project", "missingVariables"], "properties": {
                        "project": ref("Project"),
                        "missingVariables": {"type": "array", "items": {"type": "string"}, "description": "Com `template`: as variáveis obrigatórias dele que não vieram. Com alguma, o projeto instala e não inicia. Vazia sem template."},
                    }},
                    "example": {"project": {**INSTALLING, "name": "Bot discord.js", "memoryMb": 256, "templateId": "discord-js-bot"}, "missingVariables": ["DISCORD_TOKEN"]},
                }},
            },
            "400": resp("O nome em `databaseVariable` ou uma variável de `variables` não vale, ou vieram `file` e `template` juntos. Nada foi criado.", [
                ("invalid_request", err("invalid_request", "O nome PATH é reservado pela Cube. Escolha outro.", field="databaseVariable")),
                ("invalid_request", err("invalid_request", "O nome HOME é reservado pela Cube. Escolha outro.", field="variables")),
                ("invalid_request", err("invalid_request", "Envie um .zip ou escolha um template, não os dois.")),
            ]),
            "401": R401,
            "403": resp("A chave é só de leitura, ou o plano não comporta mais este projeto.", [
                E_PERM,
                ("project_limit_reached", err("project_limit_reached", "O plano Free permite até 1 bot. Exclua um projeto ou mude de plano.", limit=1)),
                ("site_not_allowed", err("site_not_allowed", "O plano Free não inclui sites. Mude para um plano pago para hospedar sites e APIs.")),
                ("site_limit_reached", err("site_limit_reached", "O plano Block permite até 2 sites. Exclua um site ou mude de plano.", limit=2)),
                ("language_not_in_plan", err("language_not_in_plan", "Um projeto Java precisa de pelo menos 256 MB de memória, e o plano Free tem 100 MB. Mude para um plano pago para hospedar Java.", minMemoryMb=256)),
                ("template_not_in_plan", err("template_not_in_plan", "O template Lavalink precisa de pelo menos 512 MB de memória e está disponível a partir do plano Block. Mude de plano em Plano e cobrança.", minMemoryMb=512)),
            ]),
            "409": resp("Conflito com o estado da conta.", [
                ("subdomain_taken", err("subdomain_taken", "Este subdomínio já é de outro site. Escolha outro.", field="subdomain")),
                ("no_capacity", err("no_capacity", "Nossos servidores estão cheios agora e não dá para liberar mais memória. Tente de novo mais tarde: estamos abrindo mais espaço.")),
                E_SUSP, E_BETA, E_FREE_LOST, E_SUSP_MANUAL,
            ]),
            "404": resp("O banco de `databaseId` não existe ou não é da sua conta, ou o `template` não existe. Nada foi criado.", [
                ("not_found", err("not_found", "Banco de dados não encontrado. Escolha um banco da sua conta ou envie sem ele.", field="databaseId")),
                ("not_found", err("not_found", "Template não encontrado. Escolha um da lista de templates.", field="template")),
            ]),
            "413": ZIP_413,
            "422": resp("O .zip ou a configuração foram recusados.", [
                ("invalid_zip", err("invalid_zip", "O arquivo não é um zip válido (corrompido, protegido por senha ou vazio). Gere o zip de novo e envie.")),
                ("unsafe_zip", err("unsafe_zip", "O zip tem atalhos (links) para outros arquivos, e eles não são aceitos. Troque os atalhos pelos arquivos de verdade e envie de novo.", reason="link")),
                ("missing_config", err("missing_config", "O zip não tem cube.json. Informe a linguagem e o comando de início do bot. Num site só de HTML, basta o index.html na raiz do .zip.")),
                ("invalid_config", err("invalid_config", 'O cube.json tem um campo que não existe: "memory". Confira se não é erro de digitação.', field="memory")),
                ("invalid_config", err("invalid_config", "A memória de um bot precisa ser de pelo menos 256 MB no plano Block.", field="memoryMb", minMemoryMb=256)),
                ("unsupported_language", err("unsupported_language", 'Por enquanto aceitamos Node.js (20, 22, 24 e 26; arquivo principal .js, .mjs, .cjs, .ts, .mts ou .cts), Python (3.11, 3.12, 3.13 e 3.14; arquivo principal .py), Java (21 e 25; arquivo principal .jar), Go (1.26 e 1.27; arquivo principal .go), PHP (8.4 e 8.5; arquivo principal .php), Ruby (3.4 e 4.0; arquivo principal .rb), .NET (10; arquivo principal .csproj, .fsproj, .vbproj ou .dll), Elixir (1.20; arquivo principal .exs) e site estático (HTML, "static").', supported={"node": ["20", "22", "24", "26"], "python": ["3.11", "3.12", "3.13", "3.14"], "java": ["21", "25"], "go": ["1.26", "1.27"], "php": ["8.4", "8.5"], "ruby": ["3.4", "4.0"], "dotnet": ["10"], "elixir": ["1.20"]})),
                ("unsupported_system_package", err("unsupported_system_package", 'O pacote "openssh-server" não está na lista dos pacotes do sistema. Aceitamos: ' + ', '.join(SYSTEM_PACKAGES[:-1]) + ' e ' + SYSTEM_PACKAGES[-1] + '.', field="systemPackages", supported=SYSTEM_PACKAGES)),
                ("insufficient_memory", err("insufficient_memory", "Este bot pede 512 MB, mas o plano Block só tem 256 MB livres. Diminua a memória no cube.json, exclua ou reduza outro projeto, ou mude de plano.", freeMemoryMb=256, requestedMemoryMb=512)),
                ("invalid_subdomain", err("invalid_subdomain", "O subdomínio precisa ter de 3 a 32 caracteres: letras minúsculas sem acento, números e hífen, começando e terminando com letra ou número e sem dois hífens seguidos.", field="subdomain")),
                ("reserved_subdomain", err("reserved_subdomain", "Este subdomínio é reservado ou usa o nome de uma marca ou órgão conhecido, e foi bloqueado para evitar golpes. Escolha outro.", field="subdomain")),
            ]),
            "429": R429_HEAVY,
            "503": R503,
        },
    },
}

paths["/projects/{id}"] = {
    "get": {
        "operationId": "getProject",
        "summary": "Ver um projeto",
        "description": "Um projeto da sua conta, com o status e o uso de agora. Um ID de outra conta responde `404`, igual a um que não existe.",
        "tags": ["Projetos"],
        "parameters": [ID_PARAM],
        "x-codeSamples": samples(
            f"curl {BASE}/projects/$PROJECT_ID \\\n  {KEY_H}",
            "const res = await fetch(`${API}/projects/${process.env.PROJECT_ID}`, { headers });\n"
            "const { project } = await res.json();\n"
            "console.log(project.status, project.usage?.memoryMb);",
            "r = requests.get(f\"{API}/projects/{os.environ['PROJECT_ID']}\", headers=headers, timeout=30)\n"
            "r.raise_for_status()\n"
            'project = r.json()["project"]\n'
            'print(project["status"], project["usage"])',
        ),
        "responses": {
            "200": {
                "description": "O projeto.",
                "content": {"application/json": {
                    "schema": {"type": "object", "required": ["project"], "properties": {"project": ref("Project")}},
                    "example": {"project": PROJECT_EXAMPLE},
                }},
            },
            "401": R401,
            "404": R404,
            "429": R429,
        },
    },
}

paths["/projects/{id}/code"] = {
    "post": {
        "operationId": "uploadProjectCode",
        "summary": "Enviar novo código",
        "description": (
            "Troca o código do projeto por um `.zip` novo. A configuração (tipo, linguagem, comando e memória) continua a mesma: "
            "um `cube.json` no `.zip` novo é ignorado. As dependências só são instaladas de novo se o `package.json`, o "
            "`package-lock.json` ou o `requirements.txt` mudou. Se o projeto estava ligado, ele volta com o código novo.\n\n"
            "O `.zip` novo substitui a pasta inteira do projeto (só as dependências instaladas ficam). Se for recusado, os arquivos "
            "de antes continuam lá. Um envio a cada 3 segundos por conta, somando com a criação de projetos."
        ),
        "tags": ["Projetos"],
        "parameters": [ID_PARAM],
        "requestBody": {
            "required": True,
            "content": {"multipart/form-data": {
                "schema": {
                    "type": "object",
                    "required": ["file"],
                    "properties": {
                        "file": {"type": "string", "format": "binary", "description": "O `.zip` com o código novo. Até 5 MB no Free e 10 MB nos planos pagos."},
                    },
                },
                "encoding": {"file": {"contentType": "application/zip"}},
            }},
        },
        "x-codeSamples": samples(
            f"curl {BASE}/projects/$PROJECT_ID/code \\\n  {KEY_H} \\\n  -F \"file=@meu-bot.zip\"",
            "const form = new FormData();\n"
            "form.set('file', await openAsBlob('meu-bot.zip'), 'meu-bot.zip');\n\n"
            "const res = await fetch(`${API}/projects/${process.env.PROJECT_ID}/code`, {\n"
            "  method: 'POST',\n  headers,\n  body: form,\n});\n"
            "const { project, isReinstallingDependencies } = await res.json();\n"
            "console.log(project.status, isReinstallingDependencies);",
            'with open("meu-bot.zip", "rb") as zip:\n'
            "    r = requests.post(\n"
            "        f\"{API}/projects/{os.environ['PROJECT_ID']}/code\",\n"
            "        headers=headers,\n"
            '        files={"file": ("meu-bot.zip", zip, "application/zip")},\n'
            "        timeout=300,\n"
            "    )\n"
            "r.raise_for_status()\n"
            "print(r.json())",
            node_imports="import { openAsBlob } from 'node:fs';\n",
        ),
        "responses": {
            "202": {
                "description": "Código recebido. O projeto passa por `installing` e volta ao estado que você deixou.",
                "content": {"application/json": {
                    "schema": ref("InstallStarted"),
                    "example": {"project": INSTALLING, "isReinstallingDependencies": False},
                }},
            },
            "401": R401,
            "403": R403_WRITE,
            "404": R404,
            "409": resp("O projeto está ocupado ou a conta não pode instalar agora.", [E_BUSY, E_SUSP, E_BETA, E_FREE_LOST, E_SUSP_MANUAL]),
            "413": ZIP_413,
            "422": resp("O .zip foi recusado. Nada mudou no projeto.", [
                ("invalid_zip", err("invalid_zip", "O arquivo não é um zip válido (corrompido, protegido por senha ou vazio). Gere o zip de novo e envie.")),
                ("unsafe_zip", err("unsafe_zip", "Descompactado, o projeto passa do limite de 500 MB. Tire os arquivos grandes que o bot não usa e envie de novo.", reason="size")),
            ]),
            "429": R429_HEAVY,
            "503": R503_VARS,
        },
    },
}

ACTIONS = {
    "start": ("startProject", "Iniciar um projeto", "Liga o projeto. Se ele já está no ar, nada muda e a resposta é `200`. Só sobe o que cabe no plano agora, somando a memória dos projetos ligados.", "running"),
    "stop": ("stopProject", "Parar um projeto", "Para o projeto: o processo recebe o sinal para encerrar e tem 10 segundos antes de ser finalizado. Desliga o reinício automático até o próximo início. Parar funciona inclusive com a conta suspensa, mas não durante o envio e a instalação (`409 project_busy`). Se já está parado, nada muda.", "stopped"),
    "restart": ("restartProject", "Reiniciar um projeto", "Para e liga de novo, zerando a contagem de quedas. Num projeto parado, com erro ou em loop, é igual a iniciar. Use depois de mudar variáveis de ambiente.", "running"),
}
for action, (op, summary, desc, st) in ACTIONS.items():
    ok_example = PROJECT_EXAMPLE if st == "running" else STOPPED
    responses = {
        "200": {
            "description": "A ação terminou. O projeto vem com o status novo.",
            "content": {"application/json": {
                "schema": {"type": "object", "required": ["project"], "properties": {"project": ref("Project")}},
                "example": {"project": ok_example},
            }},
        },
        "401": R401,
        "403": R403_WRITE,
        "404": R404,
    }
    if action == "stop":
        responses["409"] = resp("O projeto está instalando ou tem outra ação em curso.", [E_BUSY])
    else:
        responses["202"] = {
            "description": "A versão da linguagem mudou em Configurações: o projeto passa pela instalação antes de subir.",
            "content": {"application/json": {
                "schema": ref("InstallStarted"),
                "example": {"project": INSTALLING, "isReinstallingDependencies": True},
            }},
        }
        responses["409"] = resp("O projeto está ocupado, a instalação falhou, falta uma variável obrigatória do template ou a conta não pode iniciar agora.", [
            E_BUSY,
            ("install_pending", err("install_pending", "A instalação das dependências deste projeto não terminou. Envie o projeto de novo para instalar.")),
            E_MISSING_VARS,
            E_SUSP, E_BETA, E_FREE_LOST, E_SUSP_MANUAL,
        ])
        responses["403"] = resp("A chave é só de leitura, ou o plano não inclui sites.", [
            E_PERM,
            ("site_not_allowed", err("site_not_allowed", "O plano Free não inclui sites. Mude para um plano pago para colocar este site no ar.")),
        ])
        responses["422"] = resp("Ligar este projeto passa da memória do plano com os que já estão ligados.", [
            ("plan_limit_reached", err("plan_limit_reached", "Este projeto usa 512 MB, mas o plano Block só tem 256 MB livres com os projetos que estão ligados. Diminua a memória dele em Configurações ou pare outro projeto.", freeMemoryMb=256, requestedMemoryMb=512)),
        ])
    responses["429"] = R429
    responses["503"] = R503 if action == "stop" else R503_VARS
    pid = "{os.environ['PROJECT_ID']}"
    paths[f"/projects/{{id}}/{action}"] = {
        "post": {
            "operationId": op,
            "summary": summary,
            "description": desc + " A resposta chega quando a ação termina (até 30 segundos).",
            "tags": ["Controle"],
            "parameters": [ID_PARAM],
            "x-codeSamples": samples(
                f"curl -X POST {BASE}/projects/$PROJECT_ID/{action} \\\n  {KEY_H}",
                f"const res = await fetch(`${{API}}/projects/${{process.env.PROJECT_ID}}/{action}`, {{\n"
                "  method: 'POST',\n  headers,\n});\n"
                f"console.log((await res.json()).project.status); // {st}",
                "r = requests.post(\n"
                f"    f\"{{API}}/projects/{pid}/{action}\", headers=headers, timeout=60\n"
                ")\n"
                "r.raise_for_status()\n"
                'print(r.json()["project"]["status"])',
            ),
            "responses": responses,
        }
    }

SSE_EXAMPLE = (
    ": open\n\n"
    "event: line\n"
    'data: {"time":"2026-09-26T18:01:09.870Z","stream":"stdout","text":"Iniciando o bot..."}\n\n'
    "event: line\n"
    'data: {"time":"2026-09-26T18:01:10.123Z","stream":"stdout","text":"Logado como MeuBot#1234"}\n\n'
    "event: status\n"
    'data: {"status":"restarting","consecutiveCrashes":1,"error":null}\n\n'
    ": ping\n"
)

paths["/projects/{id}/logs"] = {
    "get": {
        "operationId": "streamProjectLogs",
        "summary": "Logs do projeto (ao vivo)",
        "description": (
            "Abre um stream de [Server-Sent Events](https://developer.mozilla.org/pt-BR/docs/Web/API/Server-sent_events): primeiro chegam as "
            "últimas `lines` linhas, depois as novas, ao vivo. O stream fica aberto até você fechar (com `follow=false`, termina depois das últimas linhas).\n\n"
            "- `event: line` traz uma linha do log: `time`, `stream` (`stdout`, `stderr` ou `build`) e `text` (até 4.096 caracteres).\n"
            "- `event: status` chega a cada mudança de estado do projeto, com `status`, `consecutiveCrashes` e `error` (o motivo, em `error` e `crash_loop`).\n"
            "- Um comentário `: ping` chega a cada 20 segundos para manter a conexão.\n\n"
            "O log é texto do seu app: mostre como texto, nunca como HTML. `stdout` e `stderr` podem chegar fora de ordem entre si; "
            "ordene por `time`. Uma abertura a cada 5 segundos por projeto e origem, e até 5 streams abertos por conta."
        ),
        "tags": ["Logs e métricas"],
        "parameters": [
            ID_PARAM,
            {"name": "lines", "in": "query", "description": "Quantas linhas antigas mandar antes das novas.", "schema": {"type": "integer", "minimum": 0, "maximum": 1000, "default": 200}},
            {"name": "source", "in": "query", "description": "`app`: a saída do seu app. `build`: a saída da última instalação e build.", "schema": {"type": "string", "enum": ["app", "build"], "default": "app"}},
            {"name": "follow", "in": "query", "description": "`true`: depois das últimas linhas, segue ao vivo até você fechar. `false`: manda só as últimas `lines` linhas e termina o stream.", "schema": {"type": "string", "enum": ["true", "false"], "default": "true"}},
        ],
        "x-codeSamples": samples(
            f"curl -N \"{BASE}/projects/$PROJECT_ID/logs?lines=100\" \\\n  {KEY_H}",
            "const res = await fetch(`${API}/projects/${process.env.PROJECT_ID}/logs?lines=100`, { headers });\n"
            "const decoder = new TextDecoder();\n"
            "let rest = '';\n"
            "for await (const chunk of res.body) {\n"
            "  const events = (rest + decoder.decode(chunk, { stream: true })).split('\\n\\n');\n"
            "  rest = events.pop();\n"
            "  for (const event of events) {\n"
            "    const data = event.split('\\n').find((l) => l.startsWith('data: '));\n"
            "    if (event.startsWith('event: line') && data) console.log(JSON.parse(data.slice(6)).text);\n"
            "  }\n"
            "}",
            "with requests.get(\n"
            "    f\"{API}/projects/{os.environ['PROJECT_ID']}/logs\",\n"
            '    params={"lines": 100},\n'
            "    headers=headers,\n"
            "    stream=True,\n"
            "    timeout=120,\n"
            ") as r:\n"
            "    event = None\n"
            "    for line in r.iter_lines(decode_unicode=True):\n"
            '        if line.startswith("event: "):\n'
            "            event = line[7:]\n"
            '        elif line.startswith("data: ") and event == "line":\n'
            '            print(json.loads(line[6:])["text"])',
            py_imports=("json", "os", "requests"),
        ),
        "responses": {
            "200": {
                "description": "O stream de eventos.",
                "content": {"text/event-stream": {"schema": {"type": "string"}, "example": SSE_EXAMPLE}},
            },
            "400": resp("Parâmetro fora do formato.", [("invalid_request", err("invalid_request", "Use lines de 0 a 1000, source app ou build e follow true ou false."))]),
            "401": R401,
            "404": R404,
            "429": R429_HEAVY,
            "503": R503,
        },
    },
}

paths["/projects/{id}/metrics"] = {
    "get": {
        "operationId": "getProjectMetrics",
        "summary": "Métricas do projeto",
        "description": (
            "Memória, processador e rede ao longo do tempo. `15m` traz um ponto a cada 15 segundos; `1h`, um por minuto; "
            "`24h`, médias de 5 minutos. As métricas ficam guardadas por 24 horas. Minutos em que o projeto estava parado não têm ponto. "
            "Em `24h`, a rede de cada ponto é a média dos 5 minutos inteiros (minuto parado conta 0), sem arredondar: `networkInBps × intervalSeconds` dá os bytes do bloco."
        ),
        "tags": ["Logs e métricas"],
        "parameters": [
            ID_PARAM,
            {"name": "window", "in": "query", "description": "A janela de tempo.", "schema": {"type": "string", "enum": ["15m", "1h", "24h"], "default": "1h"}},
        ],
        "x-codeSamples": samples(
            f"curl \"{BASE}/projects/$PROJECT_ID/metrics?window=24h\" \\\n  {KEY_H}",
            "const res = await fetch(`${API}/projects/${process.env.PROJECT_ID}/metrics?window=24h`, { headers });\n"
            "const { points, memoryLimitMb } = await res.json();\n"
            "const peak = points.length ? Math.max(...points.map((p) => p.memoryMb)) : 0;\n"
            "console.log(`Pico de memória: ${peak} de ${memoryLimitMb} MB`);",
            "r = requests.get(\n"
            "    f\"{API}/projects/{os.environ['PROJECT_ID']}/metrics\",\n"
            '    params={"window": "24h"},\n'
            "    headers=headers,\n"
            "    timeout=30,\n"
            ")\n"
            "r.raise_for_status()\n"
            "data = r.json()\n"
            'peak = max((p["memoryMb"] for p in data["points"]), default=0)\n'
            'print(f"Pico de memória: {peak} de {data[\'memoryLimitMb\']} MB")',
        ),
        "responses": {
            "200": {
                "description": "Os pontos da janela.",
                "content": {"application/json": {
                    "schema": ref("Metrics"),
                    "example": {
                        "window": "1h",
                        "intervalSeconds": 60,
                        "memoryLimitMb": 256,
                        "points": [
                            {"time": "2026-09-26T18:01:00.000Z", "memoryMb": 81, "cpuPercent": 1.4, "networkInBps": 1180, "networkOutBps": 290},
                            {"time": "2026-09-26T18:02:00.000Z", "memoryMb": 83, "cpuPercent": 1.2, "networkInBps": 1200, "networkOutBps": 300},
                        ],
                    },
                }},
            },
            "400": resp("Parâmetro fora do formato.", [("invalid_request", err("invalid_request", "Use window 15m, 1h ou 24h."))]),
            "401": R401,
            "404": R404,
            "429": R429,
            "503": R503,
        },
    },
}

CRASH_EXAMPLE = {
    "id": "5b0f7c9e-3d7a-4c1e-9a55-2f1c8e7d6b40",
    "exitedAt": "2026-09-29T14:02:11.000Z",
    "startedAt": "2026-09-29T13:59:58.000Z",
    "uptimeSeconds": 133,
    "exitCode": 137,
    "signal": "SIGKILL",
    "isOutOfMemory": True,
    "memoryLimitMb": 256,
    "reason": "Sem memória: passou de 256 MB",
    "outcome": "restarting",
    "consecutiveCrashes": 1,
    "restartedAt": "2026-09-29T14:02:13.000Z",
    "logStatus": "available",
}
CRASH_LOG_EXAMPLE = {
    "lines": [
        {"time": "2026-09-29T14:02:10.412Z", "stream": "stdout", "text": "Conectando com DISCORD_TOKEN=[valor de DISCORD_TOKEN]"},
        {"time": "2026-09-29T14:02:11.020Z", "stream": "stderr", "text": "FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory"},
    ],
    "isTruncated": False,
}
CRASH_ID_PARAM = {"name": "crashId", "in": "path", "required": True, "description": "O `id` da queda, da lista.", "schema": {"type": "string", "format": "uuid"}}
E_404_CRASH = ("not_found", err("not_found", "Queda não encontrada."))

paths["/projects/{id}/crashes"] = {
    "get": {
        "operationId": "listProjectCrashes",
        "summary": "Linha do tempo de quedas",
        "description": (
            "As quedas do projeto nos últimos 30 dias, a mais nova primeiro, até 50: cada vez que o processo saiu com código diferente de 0 "
            "(erro, sinal ou sem memória). Cada uma traz o motivo em pt-BR (`reason`), o código de saída e o sinal, quanto tempo ficou no ar, "
            "o que veio depois (`outcome`: o reinício automático, o loop de erro ou parado) e quando o reinício automático pôs de volta no ar. "
            "O log daquele momento vem no `GET` de uma queda. Sair com 0 ou parar pelo painel não é queda."
        ),
        "tags": ["Logs e métricas"],
        "parameters": [ID_PARAM],
        "x-codeSamples": samples(
            f"curl \"{BASE}/projects/$PROJECT_ID/crashes\" \\\n  {KEY_H}",
            "const res = await fetch(`${API}/projects/${process.env.PROJECT_ID}/crashes`, { headers });\n"
            "const { crashes } = await res.json();\n"
            "for (const c of crashes) console.log(c.exitedAt, c.reason, `${c.uptimeSeconds ?? '?'} s no ar`);",
            "r = requests.get(\n"
            "    f\"{API}/projects/{os.environ['PROJECT_ID']}/crashes\",\n"
            "    headers=headers,\n"
            "    timeout=30,\n"
            ")\n"
            "r.raise_for_status()\n"
            'for c in r.json()["crashes"]:\n'
            '    print(c["exitedAt"], c["reason"])',
        ),
        "responses": {
            "200": {
                "description": "As quedas dos últimos 30 dias.",
                "content": {"application/json": {"schema": ref("CrashList"), "example": {"crashes": [CRASH_EXAMPLE], "limit": 50, "retentionDays": 30}}},
            },
            "401": R401,
            "404": R404,
            "429": R429,
        },
    },
}

paths["/projects/{id}/crashes/{crashId}"] = {
    "get": {
        "operationId": "getProjectCrash",
        "summary": "Queda com o log do momento",
        "description": (
            "Uma queda com as últimas 200 linhas do log daquele momento (`stdout` e `stderr`, só as de antes da queda). "
            "O log desta queda é mascarado antes de ser guardado (o console ao vivo e a rota de logs seguem com o texto original): "
            "o valor de cada variável de ambiente do projeto vira `[valor de NOME]`, o de agora e o de antes de uma troca que ainda não valeu, também escapado (valores com menos de 6 caracteres não são mascarados), "
            "e tokens do Discord, chaves `sk-`, JWT, `Bearer`, senhas em URL, linhas `TOKEN=…` e chaves privadas viram `[token removido]`, `[chave removida]`, `[senha removida]` ou `[valor removido]`. "
            "Cada linha vai até 1.000 caracteres e a queda inteira até 64 mil (`isTruncated`). "
            "`log` vem `null` enquanto está sendo guardado (`logStatus: \"pending\"`, alguns segundos) ou quando não deu para ler o log daquele momento (`unavailable`)."
        ),
        "tags": ["Logs e métricas"],
        "parameters": [ID_PARAM, CRASH_ID_PARAM],
        "x-codeSamples": samples(
            f"curl \"{BASE}/projects/$PROJECT_ID/crashes/$CRASH_ID\" \\\n  {KEY_H}",
            "const res = await fetch(\n"
            "  `${API}/projects/${process.env.PROJECT_ID}/crashes/${process.env.CRASH_ID}`,\n"
            "  { headers },\n"
            ");\n"
            "const { crash } = await res.json();\n"
            "console.log(crash.reason);\n"
            "for (const line of crash.log?.lines ?? []) console.log(line.time, line.text);",
            "r = requests.get(\n"
            "    f\"{API}/projects/{os.environ['PROJECT_ID']}/crashes/{os.environ['CRASH_ID']}\",\n"
            "    headers=headers,\n"
            "    timeout=30,\n"
            ")\n"
            "r.raise_for_status()\n"
            'crash = r.json()["crash"]\n'
            'print(crash["reason"])\n'
            'for line in (crash["log"] or {}).get("lines", []):\n'
            '    print(line["time"], line["text"])',
        ),
        "responses": {
            "200": {
                "description": "A queda com o log.",
                "content": {"application/json": {"schema": {"type": "object", "required": ["crash"], "properties": {"crash": ref("CrashDetail")}}, "example": {"crash": {**CRASH_EXAMPLE, "log": CRASH_LOG_EXAMPLE}}}},
            },
            "401": R401,
            "404": resp("O projeto ou a queda não existem, ou não são da sua conta.", [E_404, E_404_CRASH]),
            "429": R429,
        },
    },
}

ANALYTICS_EXAMPLE = {
    "window": "24h",
    "intervalSeconds": 900,
    "totals": {"requests": 15201, "visits": 1479, "bytes": 279698400},
    "devices": {
        "desktop": {"requests": 8817, "visits": 680, "bytes": 185157000},
        "mobile": {"requests": 6384, "visits": 799, "bytes": 94483200},
    },
    "statusCodes": {"2xx": 13681, "3xx": 912, "4xx": 532, "5xx": 76},
    "responseTimeMs": {"p50": 38, "p95": 412},
    "points": [
        {"time": "2026-09-28T03:00:00.000Z", "requests": 120, "visits": 9},
        {"time": "2026-09-28T03:15:00.000Z", "requests": 96, "visits": 7},
    ],
    "routes": [{"path": "/", "requests": 4712}, {"path": "/produtos", "requests": 2584}],
    "countries": [{"code": "BR", "requests": 10793, "visits": 1050}, {"code": "US", "requests": 1368, "visits": 133}],
}

paths["/projects/{id}/analytics"] = {
    "get": {
        "operationId": "getProjectAnalytics",
        "summary": "Análise do site",
        "description": (
            "Requisições e visitas de um site ou API, as mesmas da aba Análise do painel: a linha do tempo, Computador e Celular, "
            "os códigos de resposta, o tempo de resposta (p50 e p95), as 20 rotas mais pedidas e os países. "
            "`24h` vem em blocos de 15 minutos, `7d` de 1 hora e `30d` de 6 horas, a partir da meia-noite de Brasília; os blocos sem acesso vêm com 0. "
            "A visita é o mesmo aparelho uma vez por dia, contada sem cookie e sem guardar o IP. Os números ficam guardados por 30 dias. "
            "Só sites e APIs: um bot responde `422 not_a_site`."
        ),
        "tags": ["Análise"],
        "parameters": [
            ID_PARAM,
            {"name": "window", "in": "query", "description": "A janela de tempo.", "schema": {"type": "string", "enum": ["24h", "7d", "30d"], "default": "24h"}},
        ],
        "x-codeSamples": samples(
            f"curl \"{BASE}/projects/$PROJECT_ID/analytics?window=7d\" \\\n  {KEY_H}",
            "const res = await fetch(`${API}/projects/${process.env.PROJECT_ID}/analytics?window=7d`, { headers });\n"
            "const { totals, countries } = await res.json();\n"
            "console.log(`${totals.requests} requisições e ${totals.visits} visitas em 7 dias`);\n"
            "console.log('País que mais acessou:', countries[0]?.code ?? 'nenhum');",
            "r = requests.get(\n"
            "    f\"{API}/projects/{os.environ['PROJECT_ID']}/analytics\",\n"
            '    params={"window": "7d"},\n'
            "    headers=headers,\n"
            "    timeout=30,\n"
            ")\n"
            "r.raise_for_status()\n"
            "data = r.json()\n"
            'print(f"{data[\'totals\'][\'requests\']} requisições e {data[\'totals\'][\'visits\']} visitas em 7 dias")',
        ),
        "responses": {
            "200": {
                "description": "O resumo da janela.",
                "content": {"application/json": {"schema": ref("Analytics"), "example": ANALYTICS_EXAMPLE}},
            },
            "400": resp("Parâmetro fora do formato.", [("invalid_request", err("invalid_request", "Use window 24h, 7d ou 30d."))]),
            "401": R401,
            "404": R404,
            "422": resp("O projeto é um bot.", [("not_a_site", err("not_a_site", "Só sites e APIs têm Análise. Bots não recebem visitas pela internet."))]),
            "429": R429,
        },
    },
}

USAGE_EXAMPLE = {
    "plan": {"id": "stack", "name": "Stack", "memoryMb": 2048, "vcpu": 2, "maxBots": 8, "maxSites": 4, "minMemoryMb": {"bot": 256, "site": 512}, "hasAutoRestart": True, "zipMaxMb": 10, "maxDatabases": 1, "blobGb": 10, "customDomainLimit": 1},
    "memory": {"reservedMb": 868, "freeMb": 1180, "inUseMb": 141},
    "projects": {"total": 3, "running": 2},
    "databases": {"total": 1, "running": 1, "reservedMb": 512},
    "blob": {"usedBytes": 48213991, "quotaBytes": 10737418240, "objectCount": 7},
    "customDomains": {"used": 0, "isAvailable": False},
}

paths["/account/usage"] = {
    "get": {
        "operationId": "getAccountUsage",
        "summary": "Uso do plano",
        "description": (
            "O plano da conta e os limites dele, a memória reservada, livre e em uso, e quantos projetos existem e estão no ar. "
            "Use `plan.zipMaxMb` para conferir o tamanho do .zip antes de enviar (a [CLI](/cli) faz isso no `cube deploy`). "
            "O uso por projeto (processador, rede e disco) fica só no painel, na página Uso."
        ),
        "tags": ["Conta"],
        "x-codeSamples": samples(
            f"curl \"{BASE}/account/usage\" \\\n  {KEY_H}",
            "const res = await fetch(`${API}/account/usage`, { headers });\n"
            "const { plan, memory } = await res.json();\n"
            "console.log(`${plan.name}: ${memory.freeMb} MB livres, .zip até ${plan.zipMaxMb} MB`);",
            "r = requests.get(f\"{API}/account/usage\", headers=headers, timeout=30)\n"
            "r.raise_for_status()\n"
            "usage = r.json()\n"
            'print(f"{usage[\'plan\'][\'name\']}: .zip até {usage[\'plan\'][\'zipMaxMb\']} MB")',
        ),
        "responses": {
            "200": {
                "description": "O uso do plano.",
                "content": {"application/json": {"schema": ref("AccountUsage"), "example": USAGE_EXAMPLE}},
            },
            "401": R401,
            "429": R429,
        },
    },
}

# Códigos de presente (cube-hosting#75): a prévia e o resgate, na conta da chave de escrita.
GIFT_PREVIEW_EXAMPLE = {
    "code": {"plan": "stack", "days": 30},
    "kind": "days_converted",
    "plan": "monolith",
    "days": 3,
    "endsAt": None,
    "returnsToPlan": None,
    "previousPaidUntil": "2026-10-20T15:00:00.000Z",
    "paidUntil": "2026-10-23T15:00:00.000Z",
    "summary": "Este código vale 3 dias do seu plano Monolith (30 dias de Stack pelo valor). O vencimento passa de 20/10/2026 para 23/10/2026.",
}
GIFT_BODY = {
    "required": True,
    "content": {"application/json": {
        "schema": {
            "type": "object",
            "required": ["code"],
            "additionalProperties": False,
            "properties": {"code": {"type": "string", "maxLength": 40, "description": "O código de presente, como `CUBE-XXXX-XXXX-XXXX` (minúsculas, espaços e hífens são aceitos)."}},
        },
        "example": {"code": "CUBE-7K2P-9QWE-4RTY"},
    }},
}
E_GIFT = [
    ("invalid_gift_code", err("invalid_gift_code", "Código inválido. Confira se digitou igual ao código de presente e tente de novo.", field="code")),
    ("invite_code_not_gift", err("invite_code_not_gift", "Este é um código de convite do beta, não de presente. Resgate em Minha conta › Perfil › Resgatar código.", field="code")),
]
E_GIFT_KEY = resp("A chave é só de leitura, ou foi criada numa equipe (o presente é da conta de quem tem o código).", [
    E_PERM,
    ("api_key_not_allowed", err("api_key_not_allowed", "Uma chave criada numa equipe não resgata código de presente: o presente é da conta de quem tem o código. Resgate pela sua conta, no painel ou com uma chave criada nela.")),
])
E_GIFT_409 = resp("A conta não pode receber este código agora.", [
    ("gift_already_active", err("gift_already_active", "Sua conta já tem um presente valendo até 23 de outubro de 2026 às 12:00. Cada conta tem um presente por vez: resgate este código depois que ele terminar.", field="code")),
    ("beta_active", err("beta_active", "Sua conta está no beta do plano Stack até 10 de outubro de 2026 às 12:00. Resgate o código de presente depois que o beta terminar.", field="code")),
    ("beta_ending", err("beta_ending", "Seu beta acabou de terminar e a conta está voltando ao plano Free. Espere alguns minutos e resgate o código de novo.", field="code")),
    ("plan_change_pending", err("plan_change_pending", "Você tem um Pix de troca de plano esperando pagamento até 29 de setembro de 2026 às 15:30. Pague o Pix ou espere ele vencer e resgate o código depois: o resgate mudaria o ciclo que ele completa.", field="code")),
    ("renewal_pending", err("renewal_pending", "A cobrança da renovação do seu plano já saiu (o ciclo vence em 20/10/2026). Pague o Pix dela em Plano e cobrança e resgate o código depois: os dias entram no ciclo novo.", field="code")),
    ("plan_without_cycle", err("plan_without_cycle", "Seu plano Tower foi liberado pela equipe da Cube e não tem vencimento, então não há onde somar os dias deste código. Só um código de um plano maior sobe a conta pelos dias dele.", field="code")),
    ("account_suspended_manually", err("account_suspended_manually", "Sua conta está suspensa pela equipe da Cube, então nenhum código de presente vale agora. Fale com o suporte no Discord para resolver.", field="code")),
    ("no_capacity", err("no_capacity", "Nossos servidores estão cheios agora e não dá para liberar mais memória. Tente de novo mais tarde: estamos abrindo mais espaço.", field="code")),
])
E_GIFT_410 = resp("O código não vale mais.", [
    ("gift_code_used", err("gift_code_used", "Este código já foi usado. Cada código de presente vale uma vez só.", field="code")),
    ("gift_code_canceled", err("gift_code_canceled", "Este código foi cancelado pela equipe da Cube. Peça um código novo a quem deu o presente.", field="code")),
    ("gift_code_expired", err("gift_code_expired", "Este código podia ser resgatado até 30/10/2026 e venceu. Peça um código novo a quem deu o presente.", field="code")),
])
GIFT_RULES = (
    "O que o código faz depende do plano da conta agora, comparado pela memória (o preço mensal só converte os dias; no anual, o preço do ano ÷ 12):\n\n"
    "- `plan_started`: no **Free**, a conta passa ao plano do código pelos dias dele (`endsAt`) e depois volta ao Free (`returnsToPlan`).\n"
    "- `days_added`: no **mesmo plano** pago, os dias entram no fim do ciclo (`paidUntil`).\n"
    "- `plan_upgraded`: num plano **maior**, sobe na hora até `endsAt`, e o vencimento do plano pago anda os mesmos dias.\n"
    "- `days_converted`: num plano **menor**, vira dias do plano de agora pelo valor: piso(dias × preço do código ÷ preço do plano), no mínimo 1.\n\n"
    "No plano liberado pela equipe, não há vencimento: só o código de um plano com mais memória vale (`plan_without_cycle` nos outros).\n\n"
    "Pede uma chave de **leitura e escrita** criada na própria conta. Até 10 tentativas a cada 15 minutos por IP e por conta. "
    "Veja [Códigos de presente](/account/gift-codes)."
)
GIFT_OUT = {
    "type": "object",
    "required": ["code", "kind", "plan", "days", "endsAt", "returnsToPlan", "previousPaidUntil", "paidUntil", "summary"],
    "properties": {
        "code": {"type": "object", "properties": {"plan": {"type": "string"}, "days": {"type": "integer"}}, "description": "O plano e os dias do código."},
        "kind": {"type": "string", "enum": ["plan_started", "days_added", "plan_upgraded", "days_converted"]},
        "plan": {"type": "string", "description": "O plano que ganha os dias: o do código (`plan_started` e `plan_upgraded`) ou o de agora."},
        "days": {"type": "integer", "description": "Os dias que entram (no `days_converted`, os dias pelo valor)."},
        "endsAt": {"type": ["string", "null"], "format": "date-time", "description": "Até quando o plano do presente vale por cima do de agora."},
        "returnsToPlan": {"type": ["string", "null"], "description": "O plano de volta depois de `endsAt`."},
        "previousPaidUntil": {"type": ["string", "null"], "format": "date-time", "description": "O vencimento do plano pago antes do resgate."},
        "paidUntil": {"type": ["string", "null"], "format": "date-time", "description": "O vencimento do plano pago depois do resgate."},
        "summary": {"type": "string", "description": "A frase em português que o painel mostra antes de confirmar."},
    },
}
paths["/account/gift-codes/preview"] = {
    "post": {
        "operationId": "previewGiftCode",
        "summary": "Prévia de código de presente",
        "description": "Diz o que o código faria na conta, **sem resgatar**. " + GIFT_RULES,
        "tags": ["Conta"],
        "requestBody": GIFT_BODY,
        "x-codeSamples": samples(
            f"curl -X POST {BASE}/account/gift-codes/preview \\\n  {KEY_H} \\\n"
            "  -H \"Content-Type: application/json\" \\\n"
            "  -d '{\"code\":\"CUBE-7K2P-9QWE-4RTY\"}'",
            "const res = await fetch(`${API}/account/gift-codes/preview`, {\n"
            "  method: 'POST',\n"
            "  headers: { ...headers, 'Content-Type': 'application/json' },\n"
            "  body: JSON.stringify({ code: process.env.GIFT_CODE }),\n"
            "});\n"
            "const { preview } = await res.json();\n"
            "console.log(preview.summary);",
            "r = requests.post(\n"
            "    f\"{API}/account/gift-codes/preview\",\n"
            "    headers=headers,\n"
            "    json={\"code\": os.environ[\"GIFT_CODE\"]},\n"
            "    timeout=30,\n"
            ")\n"
            "r.raise_for_status()\n"
            "print(r.json()[\"preview\"][\"summary\"])",
        ),
        "responses": {
            "200": {
                "description": "O que o código faria. Nada mudou na conta.",
                "content": {"application/json": {"schema": {"type": "object", "required": ["preview"], "properties": {"preview": GIFT_OUT}}, "example": {"preview": GIFT_PREVIEW_EXAMPLE}}},
            },
            "400": resp("Código fora do formato, inexistente ou de convite.", E_GIFT),
            "401": R401,
            "403": E_GIFT_KEY,
            "409": E_GIFT_409,
            "410": E_GIFT_410,
            "429": R429,
        },
    },
}
paths["/account/gift-codes/redeem"] = {
    "post": {
        "operationId": "redeemGiftCode",
        "summary": "Resgatar código de presente",
        "description": (
            "Resgata o código na conta da chave: o código vale uma vez, e a conta tem um presente por vez (o segundo recebe `gift_already_active` até o primeiro acabar). "
            "O resgate entra na Atividade da conta com o nome da chave. Os dias de presente não entram no reembolso de 7 dias. " + GIFT_RULES
        ),
        "tags": ["Conta"],
        "requestBody": GIFT_BODY,
        "x-codeSamples": samples(
            f"curl -X POST {BASE}/account/gift-codes/redeem \\\n  {KEY_H} \\\n"
            "  -H \"Content-Type: application/json\" \\\n"
            "  -d '{\"code\":\"CUBE-7K2P-9QWE-4RTY\"}'",
            "const res = await fetch(`${API}/account/gift-codes/redeem`, {\n"
            "  method: 'POST',\n"
            "  headers: { ...headers, 'Content-Type': 'application/json' },\n"
            "  body: JSON.stringify({ code: process.env.GIFT_CODE }),\n"
            "});\n"
            "const { gift, account } = await res.json();\n"
            "console.log(gift.summary, account.plan);",
            "r = requests.post(\n"
            "    f\"{API}/account/gift-codes/redeem\",\n"
            "    headers=headers,\n"
            "    json={\"code\": os.environ[\"GIFT_CODE\"]},\n"
            "    timeout=30,\n"
            ")\n"
            "r.raise_for_status()\n"
            "print(r.json()[\"gift\"][\"summary\"])",
        ),
        "responses": {
            "200": {
                "description": "Resgatado: o que o código fez e a conta com o plano de agora.",
                "content": {"application/json": {
                    "schema": {"type": "object", "required": ["gift", "account"], "properties": {
                        "gift": GIFT_OUT,
                        "account": {"type": "object", "description": "A conta depois do resgate: `plan` e `gift` (`{ endsAt, returnsToPlan }` com o plano do presente por cima)."},
                    }},
                    "example": {"gift": GIFT_PREVIEW_EXAMPLE, "account": {"id": "0f1e2d3c-aaaa-4bbb-8ccc-000000000001", "plan": "monolith", "gift": None}},
                }},
            },
            "400": resp("Código fora do formato, inexistente ou de convite.", E_GIFT),
            "401": R401,
            "403": E_GIFT_KEY,
            "409": E_GIFT_409,
            "410": E_GIFT_410,
            "429": R429,
        },
    },
}

VARS_OUT = {
    "type": "object",
    "required": ["variables"],
    "properties": {"variables": {"type": "array", "items": ref("VariableName")}},
}
paths["/projects/{id}/variables"] = {
    "get": {
        "operationId": "listProjectVariables",
        "summary": "Listar variáveis",
        "description": "Os **nomes** das variáveis de ambiente do projeto, na ordem salva. Os valores nunca voltam, nem mascarados. Pede uma chave de leitura e escrita, porque as variáveis são segredo.",
        "tags": ["Variáveis de ambiente"],
        "parameters": [ID_PARAM],
        "x-codeSamples": samples(
            f"curl {BASE}/projects/$PROJECT_ID/variables \\\n  {KEY_H}",
            "const res = await fetch(`${API}/projects/${process.env.PROJECT_ID}/variables`, { headers });\n"
            "const { variables } = await res.json();\n"
            "console.log(variables.map((v) => v.name)); // [ 'TOKEN', 'PREFIX' ]",
            "r = requests.get(\n"
            "    f\"{API}/projects/{os.environ['PROJECT_ID']}/variables\", headers=headers, timeout=30\n"
            ")\n"
            "r.raise_for_status()\n"
            'print([v["name"] for v in r.json()["variables"]])',
        ),
        "responses": {
            "200": {
                "description": "Os nomes das variáveis.",
                "content": {"application/json": {"schema": VARS_OUT, "example": {"variables": [{"name": "TOKEN"}, {"name": "PREFIX"}]}}},
            },
            "401": R401,
            "403": R403_WRITE,
            "404": R404,
            "429": R429,
            "503": resp("Não deu para abrir as variáveis agora.", [("variables_unavailable", err("variables_unavailable", "As variáveis de ambiente do projeto não puderam ser abertas agora. Tente de novo em instantes."))]),
        },
    },
    "put": {
        "operationId": "setProjectVariables",
        "summary": "Definir variáveis",
        "description": (
            "Troca a lista inteira de variáveis do projeto:\n\n"
            "- `{ \"name\", \"value\" }` grava o valor novo.\n"
            "- `{ \"name\" }` sem `value` mantém o valor que já estava guardado (erro se a variável não existia).\n"
            "- O que não vier na lista é apagado.\n\n"
            "As variáveis chegam ao processo **no próximo início**: se o projeto está no ar, `isRestartRequired` vem `true` e é só "
            "[reiniciar](/api-reference/projects/restart). Até 50 variáveis; nome com letras, números e `_`, começando com letra ou `_` "
            "(até 64 caracteres); valor numa linha só, até 4.096 caracteres; tudo somado até 32 KB. `HOME`, `PATH`, o prefixo `CUBE_` "
            "e, em sites, `PORT` são reservados."
        ),
        "tags": ["Variáveis de ambiente"],
        "parameters": [ID_PARAM],
        "requestBody": {
            "required": True,
            "content": {"application/json": {
                "schema": ref("VariablesInput"),
                "example": {"variables": [{"name": "TOKEN"}, {"name": "PREFIX"}]},
            }},
        },
        "x-codeSamples": samples(
            f"curl -X PUT {BASE}/projects/$PROJECT_ID/variables \\\n  {KEY_H} \\\n"
            "  -H \"Content-Type: application/json\" \\\n"
            "  -d '{\"variables\":[{\"name\":\"TOKEN\",\"value\":\"token-novo\"},{\"name\":\"PREFIX\"}]}'",
            "const res = await fetch(`${API}/projects/${process.env.PROJECT_ID}/variables`, {\n"
            "  method: 'PUT',\n"
            "  headers: { ...headers, 'Content-Type': 'application/json' },\n"
            "  body: JSON.stringify({\n"
            "    variables: [\n"
            "      { name: 'TOKEN', value: process.env.BOT_TOKEN },\n"
            "      { name: 'PREFIX' }, // sem value: mantém o valor guardado\n"
            "    ],\n"
            "  }),\n"
            "});\n"
            "console.log(await res.json()); // { variables: [...], isRestartRequired: true }",
            "r = requests.put(\n"
            "    f\"{API}/projects/{os.environ['PROJECT_ID']}/variables\",\n"
            "    headers=headers,\n"
            "    json={\n"
            '        "variables": [\n'
            '            {"name": "TOKEN", "value": os.environ["BOT_TOKEN"]},\n'
            '            {"name": "PREFIX"},  # sem value: mantém o valor guardado\n'
            "        ]\n"
            "    },\n"
            "    timeout=30,\n"
            ")\n"
            "print(r.json())",
        ),
        "responses": {
            "200": {
                "description": "Variáveis salvas.",
                "content": {"application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["variables", "isRestartRequired"],
                        "properties": {
                            "variables": {"type": "array", "items": ref("VariableName")},
                            "isRestartRequired": {"type": "boolean", "description": "`true` quando algo mudou e o projeto está no ar: reinicie para aplicar."},
                        },
                    },
                    "example": {"variables": [{"name": "TOKEN"}, {"name": "PREFIX"}], "isRestartRequired": True},
                }},
            },
            "400": resp("A lista está fora das regras. A mensagem diz o problema, nunca o valor.", [("invalid_request", err("invalid_request", "O nome HOME é reservado pela Cube. Escolha outro."))]),
            "401": R401,
            "403": R403_WRITE,
            "404": R404,
            "413": resp("O corpo do pedido é grande demais.", [("payload_too_large", err("payload_too_large", "O corpo da requisição é grande demais."))]),
            "415": resp("O corpo não veio como JSON. Mande o cabeçalho `Content-Type: application/json`.", [("unsupported_media_type", err("unsupported_media_type", "Envie o corpo em JSON."))]),
            "429": R429,
            "503": resp("Não deu para gravar as variáveis agora. Nada foi alterado.", [("variables_unavailable", err("variables_unavailable", "As variáveis de ambiente do projeto não puderam ser abertas agora. Tente de novo em instantes."))]),
        },
    },
}

# Backups (cube-hosting#31): listar pela chave de leitura; fazer e baixar pela de escrita (o zip traz o
# .env); restaurar, excluir e o diário só no painel.
BACKUP_ID_PARAM = {"$ref": "#/components/parameters/BackupId"}
BACKUP_EXAMPLE = {
    "id": "5b0c7a4e-2f1d-4c8e-9a36-7d2b1e0f4c11",
    "type": "manual",
    "status": "ready",
    "sizeBytes": 184320,
    "error": None,
    "createdAt": "2026-09-27T18:00:00.000Z",
    "finishedAt": "2026-09-27T18:00:04.000Z",
    "expiresAt": "2026-10-27T18:00:00.000Z",
}
E_BK_BUSY = ("backup_in_progress", err("backup_in_progress", "Este projeto já tem um backup em andamento. Espere terminar para pedir outro."))
E_BK_READY = ("backup_not_ready", err("backup_not_ready", "Este backup ainda não está pronto (ou não deu certo). Espere terminar ou use outro."))
E_BK_503 = ("backups_unavailable", err("backups_unavailable", "Os backups não estão disponíveis agora. Tente de novo em instantes."))
E_BK_404 = ("not_found", err("not_found", "Backup não encontrado."))
R404_BACKUP = resp("O projeto ou o backup não existe ou não é da sua conta.", [E_404, E_BK_404])
BK = "{os.environ['BACKUP_ID']}"
PID = "{os.environ['PROJECT_ID']}"

paths["/projects/{id}/backups"] = {
    "get": {
        "operationId": "listBackups",
        "summary": "Listar backups",
        "description": (
            "Os backups do projeto, do mais novo, com o limite do plano. Cada backup fica guardado por até 30 dias; "
            "quando um novo fica pronto e o histórico está cheio, o mais antigo sai."
        ),
        "tags": ["Backups"],
        "parameters": [ID_PARAM],
        "x-codeSamples": samples(
            f"curl {BASE}/projects/$PROJECT_ID/backups \\\n  {KEY_H}",
            "const res = await fetch(`${API}/projects/${process.env.PROJECT_ID}/backups`, { headers });\n"
            "const { backups, limit } = await res.json();\n"
            "console.log(`${backups.length} de ${limit}`, backups[0]?.status);",
            f"r = requests.get(f\"{{API}}/projects/{PID}/backups\", headers=headers, timeout=30)\n"
            "r.raise_for_status()\n"
            "data = r.json()\n"
            'print(len(data["backups"]), "de", data["limit"])',
        ),
        "responses": {
            "200": {
                "description": "Os backups e as regras do plano.",
                "content": {"application/json": {
                    "schema": ref("BackupList"),
                    "example": {"backups": [BACKUP_EXAMPLE], "limit": 3, "retentionDays": 30, "isDailyAvailable": True, "isDailyEnabled": True},
                }},
            },
            "401": R401,
            "404": R404,
            "429": R429,
        },
    },
    "post": {
        "operationId": "createBackup",
        "summary": "Fazer backup",
        "description": (
            "Pede um backup dos arquivos do projeto agora, em todos os planos. A resposta chega na hora com o backup em `pending`; "
            "ele fica `ready` em alguns segundos (acompanhe por [Listar backups](/api-reference/backups/list)). "
            "As dependências (`node_modules`, `venv`) não entram. Um backup por vez em cada projeto."
        ),
        "tags": ["Backups"],
        "parameters": [ID_PARAM],
        "x-codeSamples": samples(
            f"curl -X POST {BASE}/projects/$PROJECT_ID/backups \\\n  {KEY_H}",
            "const res = await fetch(`${API}/projects/${process.env.PROJECT_ID}/backups`, {\n"
            "  method: 'POST',\n  headers,\n});\n"
            "const { backup } = await res.json();\n"
            "console.log(backup.id, backup.status); // pending",
            f"r = requests.post(f\"{{API}}/projects/{PID}/backups\", headers=headers, timeout=30)\n"
            "r.raise_for_status()\n"
            'print(r.json()["backup"]["id"])',
        ),
        "responses": {
            "202": {
                "description": "Pedido aceito; o backup entra na fila.",
                "content": {"application/json": {
                    "schema": {"type": "object", "required": ["backup"], "properties": {"backup": ref("Backup")}},
                    "example": {"backup": {**BACKUP_EXAMPLE, "status": "pending", "sizeBytes": None, "finishedAt": None}},
                }},
            },
            "401": R401,
            "403": R403_WRITE,
            "404": R404,
            "409": resp("Já tem um backup em andamento, o projeto ainda está sendo criado, ou a conta está suspensa.", [E_BK_BUSY, E_BUSY, E_SUSP, E_BETA, E_FREE_LOST, E_SUSP_MANUAL]),
            "429": R429,
            "503": resp("O armazenamento dos backups não respondeu. Nada foi feito.", [E_BK_503]),
        },
    },
}

paths["/projects/{id}/backups/{backupId}/download"] = {
    "post": {
        "operationId": "createBackupDownloadLink",
        "summary": "Pedir o link de download",
        "description": (
            "Devolve o endereço para baixar o backup em `.zip`. O link vale **5 minutos** e só com a mesma chave (ou a mesma sessão do painel): "
            "com outra conta, responde `404`. Só backups `ready`. Pede a chave de **leitura e escrita**: o `.zip` traz todos os arquivos do projeto, "
            "inclusive o `.env`."
        ),
        "tags": ["Backups"],
        "parameters": [ID_PARAM, BACKUP_ID_PARAM],
        "x-codeSamples": samples(
            f"curl -X POST {BASE}/projects/$PROJECT_ID/backups/$BACKUP_ID/download \\\n  {KEY_H}",
            "const res = await fetch(\n"
            "  `${API}/projects/${process.env.PROJECT_ID}/backups/${process.env.BACKUP_ID}/download`,\n"
            "  { method: 'POST', headers },\n"
            ");\n"
            "const { url, expiresAt } = await res.json();\n"
            "console.log(url, expiresAt);",
            f"r = requests.post(\n    f\"{{API}}/projects/{PID}/backups/{BK}/download\",\n    headers=headers,\n    timeout=30,\n)\n"
            "r.raise_for_status()\n"
            'print(r.json()["url"])',
        ),
        "responses": {
            "200": {
                "description": "O link, relativo ao endereço da API.",
                "content": {"application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["url", "expiresAt"],
                        "properties": {
                            "url": {"type": "string", "description": "Caminho para o `GET` do download, com `expires` e `signature`. Junte ao endereço da API."},
                            "expiresAt": {"type": "string", "format": "date-time", "description": "Até quando o link vale (5 minutos)."},
                        },
                    },
                    "example": {
                        "url": "/projects/01J8Z3W6N0Q4Y7V2K5T9D1H3XA/backups/5b0c7a4e-2f1d-4c8e-9a36-7d2b1e0f4c11/download?expires=1790530000000&signature=…",
                        "expiresAt": "2026-09-27T18:05:00.000Z",
                    },
                }},
            },
            "401": R401,
            "403": R403_WRITE,
            "404": R404_BACKUP,
            "409": resp("O backup ainda não está pronto ou não deu certo.", [E_BK_READY]),
            "429": R429,
            "503": resp("O armazenamento dos backups não respondeu.", [E_BK_503]),
        },
    },
    "get": {
        "operationId": "downloadBackup",
        "summary": "Baixar o backup",
        "description": (
            "Baixa o backup em `.zip` pelo link do [Pedir o link de download](/api-reference/backups/download-link), com a mesma chave "
            "(de leitura e escrita). O nome do arquivo vem no `Content-Disposition` (`<projeto>-backup-<data>.zip`). "
            "Download que chega com menos bytes que o `Content-Length` não está inteiro: peça o link de novo."
        ),
        "tags": ["Backups"],
        "parameters": [
            ID_PARAM,
            BACKUP_ID_PARAM,
            {"name": "expires", "in": "query", "required": True, "description": "Vem no `url` do link.", "schema": {"type": "integer"}},
            {"name": "signature", "in": "query", "required": True, "description": "Vem no `url` do link.", "schema": {"type": "string"}},
        ],
        "x-codeSamples": samples(
            f"LINK=$(curl -s -X POST {BASE}/projects/$PROJECT_ID/backups/$BACKUP_ID/download \\\n  {KEY_H} | jq -r .url)\n"
            f"curl -o backup.zip \"{BASE}$LINK\" \\\n  {KEY_H}",
            "const link = await fetch(\n"
            "  `${API}/projects/${process.env.PROJECT_ID}/backups/${process.env.BACKUP_ID}/download`,\n"
            "  { method: 'POST', headers },\n"
            ").then((r) => r.json());\n"
            "const res = await fetch(API + link.url, { headers });\n"
            "await writeFile('backup.zip', Buffer.from(await res.arrayBuffer()));",
            f"link = requests.post(\n    f\"{{API}}/projects/{PID}/backups/{BK}/download\",\n    headers=headers,\n    timeout=30,\n).json()\n"
            "r = requests.get(API + link[\"url\"], headers=headers, timeout=300)\n"
            "r.raise_for_status()\n"
            "with open(\"backup.zip\", \"wb\") as f:\n"
            "    f.write(r.content)",
            node_imports="import { writeFile } from 'node:fs/promises';",
        ),
        "responses": {
            "200": {
                "description": "O `.zip` do backup.",
                "content": {"application/zip": {"schema": {"type": "string", "format": "binary"}}},
            },
            "401": R401,
            "403": resp("O link venceu (5 minutos) ou foi mexido, ou a chave é só de leitura.", [("download_expired", err("download_expired", "O link de download venceu ou não é desta Conta. Peça o download de novo pelo painel.")), E_PERM]),
            "404": R404_BACKUP,
            "409": resp("O backup ainda não está pronto ou não deu certo.", [E_BK_READY]),
            "429": R429,
            "503": resp("O armazenamento dos backups não respondeu.", [E_BK_503]),
        },
    },
}

# Restaurar um backup pela API (entrou direto no openapi.json em 3468ef5; trazido para o gerador para não se perder).
paths["/projects/{id}/backups/{backupId}/restore"] = json.loads(r'''{
  "post": {
    "operationId": "restoreBackup",
    "summary": "Restaurar um backup",
    "description": "Troca os arquivos do projeto pelos do backup, pelo mesmo caminho seguro do painel: o projeto para antes, as dependências só reinstalam se o manifesto mudou, e ele termina **parado** (você liga quando conferir). Precisa da chave de **leitura e escrita**. Só backups `ready`.",
    "parameters": [
      {
        "$ref": "#/components/parameters/ProjectId"
      },
      {
        "$ref": "#/components/parameters/BackupId"
      }
    ],
    "responses": {
      "202": {
        "description": "Arquivos trocados pelos do backup. O projeto passa por `installing` e termina **parado**: quem liga é você.",
        "content": {
          "application/json": {
            "schema": {
              "$ref": "#/components/schemas/InstallStarted"
            },
            "example": {
              "project": {
                "id": "01J8Z3W6N0Q4Y7V2K5T9D1H3XA",
                "name": "Meu bot",
                "description": "Atende o servidor da loja",
                "type": "bot",
                "language": "node",
                "version": "24",
                "entry": "index.js",
                "command": "node index.js",
                "root": null,
                "memoryMb": 256,
                "port": null,
                "subdomain": null,
                "url": null,
                "status": "installing",
                "error": null,
                "hasAutoRestart": true,
                "consecutiveCrashes": 0,
                "lastExit": null,
                "usage": null,
                "startedAt": null,
                "createdAt": "2026-09-26T18:00:00.000Z",
                "updatedAt": "2026-09-26T18:01:10.000Z"
              },
              "isReinstallingDependencies": false
            }
          }
        }
      },
      "401": {
        "description": "Chave ausente, inválida ou revogada.",
        "content": {
          "application/json": {
            "schema": {
              "$ref": "#/components/schemas/Error"
            },
            "examples": {
              "invalid_api_key": {
                "summary": "invalid_api_key",
                "value": {
                  "status": "error",
                  "code": "invalid_api_key",
                  "message": "Chave de API inválida ou revogada. Confira o cabeçalho \"Authorization: Bearer <chave>\" ou crie outra em Chaves de API no painel."
                }
              }
            }
          }
        }
      },
      "403": {
        "description": "A chave é só de leitura: restaurar pede a de leitura e escrita.",
        "content": {
          "application/json": {
            "schema": {
              "$ref": "#/components/schemas/Error"
            },
            "examples": {
              "insufficient_permission": {
                "summary": "insufficient_permission",
                "value": {
                  "status": "error",
                  "code": "insufficient_permission",
                  "message": "Esta chave é só de leitura. Crie uma chave de leitura e escrita em Chaves de API."
                }
              }
            }
          }
        }
      },
      "404": {
        "description": "O projeto ou o backup não existe ou não é da sua conta.",
        "content": {
          "application/json": {
            "schema": {
              "$ref": "#/components/schemas/Error"
            },
            "examples": {
              "not_found": {
                "summary": "not_found",
                "value": {
                  "status": "error",
                  "code": "not_found",
                  "message": "Backup não encontrado."
                }
              }
            }
          }
        }
      },
      "409": {
        "description": "O projeto está sendo preparado, o backup não está pronto, ou a conta está suspensa.",
        "content": {
          "application/json": {
            "schema": {
              "$ref": "#/components/schemas/Error"
            },
            "examples": {
              "project_busy": {
                "summary": "project_busy",
                "value": {
                  "status": "error",
                  "code": "project_busy",
                  "message": "O projeto está sendo preparado ou já tem outra ação em andamento. Espere terminar."
                }
              },
              "backup_not_ready": {
                "summary": "backup_not_ready",
                "value": {
                  "status": "error",
                  "code": "backup_not_ready",
                  "message": "Este backup ainda não está pronto (ou não deu certo). Espere terminar ou use outro."
                }
              }
            }
          }
        }
      },
      "422": {
        "description": "O backup não abriu: os arquivos ficam como estavam.",
        "content": {
          "application/json": {
            "schema": {
              "$ref": "#/components/schemas/Error"
            },
            "examples": {
              "invalid_backup": {
                "summary": "invalid_backup",
                "value": {
                  "status": "error",
                  "code": "invalid_backup",
                  "message": "O backup não abriu inteiro: nada foi restaurado."
                }
              }
            }
          }
        }
      },
      "429": {
        "description": "Limite de pedidos. Traz o cabeçalho `Retry-After`.",
        "content": {
          "application/json": {
            "schema": {
              "$ref": "#/components/schemas/Error"
            },
            "examples": {
              "rate_limit_exceeded": {
                "summary": "rate_limit_exceeded",
                "value": {
                  "status": "error",
                  "code": "rate_limit_exceeded",
                  "message": "A sua conta passou do limite da API do plano Free: 10 pedidos por minuto. Espere 42 s e tente de novo."
                }
              },
              "too_many_attempts": {
                "summary": "too_many_attempts",
                "value": {
                  "status": "error",
                  "code": "too_many_attempts",
                  "message": "Muitas tentativas. Tente de novo em 15 minutos."
                }
              }
            }
          }
        }
      },
      "503": {
        "description": "Sem resposta no meio: o projeto fica parado.",
        "content": {
          "application/json": {
            "schema": {
              "$ref": "#/components/schemas/Error"
            },
            "examples": {
              "server_unavailable": {
                "summary": "server_unavailable",
                "value": {
                  "status": "error",
                  "code": "server_unavailable",
                  "message": "Não deu para confirmar a restauração: o projeto ficou parado. Confira os arquivos antes de ligar."
                }
              }
            }
          }
        }
      },
      "507": {
        "description": "Sem espaço em disco para a troca: nada mudou.",
        "content": {
          "application/json": {
            "schema": {
              "$ref": "#/components/schemas/Error"
            },
            "examples": {
              "restore_no_space": {
                "summary": "restore_no_space",
                "value": {
                  "status": "error",
                  "code": "restore_no_space",
                  "message": "Não há espaço para restaurar este backup agora: os arquivos ficaram como estavam."
                }
              }
            }
          }
        }
      }
    },
    "tags": [
      "Backups"
    ]
  }
}''')
# Restaurar recusa como o reenvio: Conta suspensa, no fim do beta ou sem a vaga do Free (cube-hosting#21).
paths["/projects/{id}/backups/{backupId}/restore"]["post"]["responses"]["409"] = resp(
    "O projeto está sendo preparado, o backup não está pronto, ou a conta está suspensa, no fim do beta ou perdeu a vaga do Free.",
    [E_BUSY, E_BK_READY, E_SUSP, E_BETA, E_FREE_LOST, E_SUSP_MANUAL],
)

nullable = lambda t, **kw: {"type": [t, "null"], **kw}

# Bancos de dados (cube-hosting#18): listar, ver e os backups pela chave de leitura; criar, iniciar,
# parar, a conexão (com a senha) e baixar pela de escrita; excluir e restaurar só no painel.
DB_ID_PARAM = {"$ref": "#/components/parameters/DatabaseId"}
DATABASE_EXAMPLE = {
    "id": "01J9A2C4E6G8J0K2M4P6R8T0V2",
    "name": "loja-db",
    "engine": "postgres",
    "engineName": "PostgreSQL",
    "host": "loja-db",
    "port": 5432,
    "status": "running",
    "memoryMb": 512,
    "usage": {"memoryMb": 61},
    "disk": {"usedMb": 47, "limitMb": 2048},
    "externalAccess": {"isAvailable": True, "isEnabled": False, "host": "db.cubehost.dev", "certificate": None},
    "startedAt": "2026-09-28T12:26:03.000Z",
    "createdAt": "2026-09-28T12:26:00.000Z",
    "updatedAt": "2026-09-28T12:26:01.000Z",
}
DATABASE_BACKUP_EXAMPLE = {
    "id": "595bf272-a3da-4d8d-b7d5-ac70868c032d",
    "type": "daily",
    "status": "ready",
    "sizeBytes": 2732,
    "error": None,
    "createdAt": "2026-09-28T12:29:15.000Z",
    "finishedAt": "2026-09-28T12:29:17.000Z",
    "expiresAt": "2026-10-05T12:29:15.000Z",
}
E_DB_404 = ("not_found", err("not_found", "Banco de dados não encontrado."))
R404_DB = resp("O banco não existe ou não é da sua conta (a mesma resposta para os dois).", [E_DB_404])
R404_DB_BACKUP = resp("O banco ou o backup não existe ou não é da sua conta.", [E_DB_404, ("not_found", err("not_found", "Backup não encontrado."))])
E_DB_BUSY = ("database_busy", err("database_busy", "Este banco já tem uma ação em andamento. Espere terminar e tente de novo."))
E_DB_NOT_ALLOWED = ("database_not_allowed", err("database_not_allowed", "O plano Block não inclui bancos de dados. Eles vêm a partir do Stack: mude de plano em Plano e cobrança."))
E_DB_LIMIT = ("database_limit_reached", err("database_limit_reached", "O plano Stack permite até 1 banco de dados. Exclua um banco ou mude de plano.", limit=1))
E_DB_BK_503 = ("backups_unavailable", err("backups_unavailable", "Os backups não estão disponíveis agora. Tente de novo em instantes."))
E_DB_BK_READY = ("backup_not_ready", err("backup_not_ready", "Este backup ainda não está pronto (ou não deu certo). Use outro da lista."))
DB = "{os.environ['DATABASE_ID']}"
DBK = "{os.environ['BACKUP_ID']}"

paths["/databases"] = {
    "get": {
        "operationId": "listDatabases",
        "summary": "Listar bancos de dados",
        "description": (
            "Os bancos de dados da conta, do mais novo, com o status e a memória e o disco de agora, e as regras do plano: "
            "quantos bancos cabem (`limit`), a memória livre somando projetos e bancos (`freeMemoryMb`) e os tipos de banco com a memória mínima de cada um."
        ),
        "tags": ["Bancos de dados"],
        "x-codeSamples": samples(
            f"curl {BASE}/databases \\\n  {KEY_H}",
            "const res = await fetch(`${API}/databases`, { headers });\n"
            "const { databases, limit } = await res.json();\n"
            "for (const d of databases) console.log(d.name, d.engineName, d.status, `${d.host}:${d.port}`);\n"
            "console.log(`${databases.length} de ${limit}`);",
            f"r = requests.get(f\"{{API}}/databases\", headers=headers, timeout=30)\n"
            "r.raise_for_status()\n"
            "for d in r.json()[\"databases\"]:\n"
            "    print(d[\"name\"], d[\"status\"], f\"{d['host']}:{d['port']}\")",
        ),
        "responses": {
            "200": {
                "description": "Os bancos e as regras do plano.",
                "content": {"application/json": {
                    "schema": ref("DatabaseList"),
                    "example": {
                        "databases": [DATABASE_EXAMPLE],
                        "limit": 3,
                        "freeMemoryMb": 3072,
                        "diskMb": 2048,
                        "backupRetentionDays": 7,
                        "engines": [
                            {"id": "postgres", "name": "PostgreSQL", "port": 5432, "minMemoryMb": 512, "isAvailable": True},
                            {"id": "mysql", "name": "MySQL", "port": 3306, "minMemoryMb": 512, "isAvailable": True},
                            {"id": "mongodb", "name": "MongoDB", "port": 27017, "minMemoryMb": 512, "isAvailable": True},
                            {"id": "redis", "name": "Redis", "port": 6379, "minMemoryMb": 256, "isAvailable": True},
                        ],
                    },
                }},
            },
            "401": R401,
            "429": R429,
        },
    },
    "post": {
        "operationId": "createDatabase",
        "summary": "Criar um banco de dados",
        "description": (
            "Cria um PostgreSQL 17, MySQL 8.4, MongoDB 8.0 ou Redis 8 na rede da sua conta, a partir do plano Stack. "
            "O `name` é também o endereço interno que os seus projetos usam (`loja-db:5432`): de 3 a 32 caracteres, letras minúsculas, "
            "números e hífen, começando com letra, único na conta. A memória sai da mesma memória do plano que a dos projetos "
            "(mínimo de 512 MB, ou 256 MB no Redis). A senha é gerada pela Cube; veja-a em [Ver a conexão](/api-reference/databases/credentials). "
            "A resposta chega com o banco já subindo (`starting`); em alguns segundos ele fica `running`."
        ),
        "tags": ["Bancos de dados"],
        "requestBody": {
            "required": True,
            "content": {"application/json": {
                "schema": ref("DatabaseInput"),
                "example": {"engine": "postgres", "name": "loja-db", "memoryMb": 512},
            }},
        },
        "x-codeSamples": samples(
            f"curl -X POST {BASE}/databases \\\n  {KEY_H} \\\n  -H \"Content-Type: application/json\" \\\n"
            "  -d '{\"engine\": \"postgres\", \"name\": \"loja-db\", \"memoryMb\": 512}'",
            "const res = await fetch(`${API}/databases`, {\n"
            "  method: 'POST',\n"
            "  headers: { ...headers, 'Content-Type': 'application/json' },\n"
            "  body: JSON.stringify({ engine: 'postgres', name: 'loja-db', memoryMb: 512 }),\n"
            "});\n"
            "const { database } = await res.json();\n"
            "console.log(database.id, database.status); // starting",
            "r = requests.post(\n"
            "    f\"{API}/databases\",\n"
            "    headers=headers,\n"
            "    json={\"engine\": \"postgres\", \"name\": \"loja-db\", \"memoryMb\": 512},\n"
            "    timeout=300,\n"
            ")\n"
            "r.raise_for_status()\n"
            "print(r.json()[\"database\"][\"id\"])",
        ),
        "responses": {
            "201": {
                "description": "Banco criado.",
                "content": {"application/json": {
                    "schema": {"type": "object", "required": ["database"], "properties": {"database": ref("Database")}},
                    "example": {"database": {**DATABASE_EXAMPLE, "status": "starting", "usage": {"memoryMb": 18}, "disk": {"usedMb": 39, "limitMb": 2048}}},
                }},
            },
            "400": resp("O corpo, o nome ou a memória não valem.", [
                ("invalid_request", err("invalid_request", 'Envie { "engine": "postgres" | "mysql" | "redis", "name": "…", "memoryMb": 512 }.')),
                ("invalid_database_name", err("invalid_database_name", 'O nome precisa ter de 3 a 32 caracteres: letras minúsculas sem acento, números e hífen, começando com letra e sem terminar em hífen (ex.: "loja-db"). Ele é o endereço que os projetos usam para conectar.', field="name")),
                ("invalid_memory", err("invalid_memory", "O PostgreSQL precisa de pelo menos 512 MB e cabe no máximo nos 2048 MB do plano.", field="memoryMb", minMemoryMb=512)),
            ]),
            "401": R401,
            "403": resp("A chave é só de leitura, ou o plano não tem (ou não comporta mais) bancos.", [E_PERM, E_DB_NOT_ALLOWED, E_DB_LIMIT]),
            "409": resp("O tipo de banco ainda chega em breve, já existe um banco com esse nome na conta, ou a conta está suspensa.", [
                ("database_name_taken", err("database_name_taken", 'Você já tem um banco chamado "loja-db". Escolha outro nome.', field="name")),
                E_SUSP, E_BETA, E_FREE_LOST, E_SUSP_MANUAL,
            ]),
            "422": resp("A memória pedida passa do que sobra no plano, somando projetos e bancos.", [
                ("insufficient_memory", err("insufficient_memory", "O banco pede 1024 MB, mas o plano Stack só tem 512 MB livres somando projetos e bancos. Diminua a memória, reduza ou exclua um projeto, ou mude de plano.", freeMemoryMb=512, requestedMemoryMb=1024)),
            ]),
            "429": R429,
            "503": resp("O servidor dos bancos não respondeu. Nada foi criado.", [E_503]),
        },
    },
}

paths["/databases/{id}"] = {
    "get": {
        "operationId": "getDatabase",
        "summary": "Ver um banco de dados",
        "description": "Um banco de dados da conta, com o status e a memória e o disco de agora.",
        "tags": ["Bancos de dados"],
        "parameters": [DB_ID_PARAM],
        "x-codeSamples": samples(
            f"curl {BASE}/databases/$DATABASE_ID \\\n  {KEY_H}",
            "const res = await fetch(`${API}/databases/${process.env.DATABASE_ID}`, { headers });\n"
            "const { database } = await res.json();\n"
            "console.log(database.status, database.usage?.memoryMb);",
            f"r = requests.get(f\"{{API}}/databases/{DB}\", headers=headers, timeout=30)\n"
            "r.raise_for_status()\n"
            "print(r.json()[\"database\"][\"status\"])",
        ),
        "responses": {
            "200": {
                "description": "O banco.",
                "content": {"application/json": {
                    "schema": {"type": "object", "required": ["database"], "properties": {"database": ref("Database")}},
                    "example": {"database": DATABASE_EXAMPLE},
                }},
            },
            "401": R401,
            "404": R404_DB,
            "429": R429,
        },
    },
}

paths["/projects/{id}/connection"] = {
    "get": {
        "operationId": "getProjectConnection",
        "summary": "Ver a conexão",
        "description": (
            "Para o projeto de um template com conexão (o [Lavalink](/hosting/lavalink)): o **nome interno**, a porta e a **senha** que a Cube gerou "
            "(`null` se a variável dela foi apagada). Só com a chave de **leitura e escrita** (a de leitura não vê a senha, como não vê os valores das variáveis), "
            "e cada leitura entra na Atividade, sem a senha. Os dados só funcionam de dentro da conta: ponha a senha numa "
            "[variável de ambiente](/api-reference/projects/set-variables) do seu bot. Projeto de outro template, ou que deixou de ser do template, responde `404`."
        ),
        "tags": ["Variáveis de ambiente"],
        "parameters": [ID_PARAM],
        "x-codeSamples": samples(
            f"curl {BASE}/projects/$PROJECT_ID/connection \\\n  {KEY_H}",
            "const res = await fetch(`${API}/projects/${process.env.PROJECT_ID}/connection`, { headers });\n"
            "const { connection } = await res.json();\n"
            "console.log(connection.host, connection.port); // guarde a senha como segredo",
            "r = requests.get(\n"
            "    f\"{API}/projects/{os.environ['PROJECT_ID']}/connection\", headers=headers, timeout=30\n"
            ")\n"
            "r.raise_for_status()\n"
            "c = r.json()[\"connection\"]\n"
            "print(c[\"host\"], c[\"port\"])",
        ),
        "responses": {
            "200": {
                "description": "A conexão. Resposta com `Cache-Control: no-store`.",
                "content": {"application/json": {
                    "schema": {"type": "object", "required": ["connection"], "properties": {"connection": {
                        "type": "object",
                        "required": ["host", "port", "password"],
                        "properties": {
                            "host": {"type": "string", "description": "O `internalHost` do projeto."},
                            "port": {"type": "integer"},
                            "password": nullable("string", description="A senha da variável do template; `null` se ela foi apagada."),
                        },
                    }}},
                    "example": {"connection": {"host": "cube-t9d1h3xa", "port": 2333, "password": "Xk3v9QmZ-2bLr7_hP4sN8wTyC1dFgJ6a"}},
                }},
            },
            "401": R401,
            "403": R403_WRITE,
            "404": R404,
            "429": R429,
        },
    },
}

paths["/databases/{id}/credentials"] = {
    "get": {
        "operationId": "getDatabaseCredentials",
        "summary": "Ver a conexão",
        "description": (
            "O endereço interno, a porta, o usuário, a **senha** e a string de conexão pronta, com o nome de variável sugerido. "
            "Só com a chave de **leitura e escrita** (a de leitura não vê a senha, como não vê os valores das variáveis), e cada leitura entra na Atividade. "
            "A string só funciona de dentro da conta: use-a numa [variável de ambiente](/api-reference/projects/set-variables) de um projeto."
        ),
        "tags": ["Bancos de dados"],
        "parameters": [DB_ID_PARAM],
        "x-codeSamples": samples(
            f"curl {BASE}/databases/$DATABASE_ID/credentials \\\n  {KEY_H}",
            "const res = await fetch(`${API}/databases/${process.env.DATABASE_ID}/credentials`, { headers });\n"
            "const { credentials } = await res.json();\n"
            "console.log(credentials.envName); // DATABASE_URL (guarde a url como segredo)",
            f"r = requests.get(f\"{{API}}/databases/{DB}/credentials\", headers=headers, timeout=30)\n"
            "r.raise_for_status()\n"
            "c = r.json()[\"credentials\"]\n"
            "print(c[\"envName\"], c[\"host\"], c[\"port\"])",
        ),
        "responses": {
            "200": {
                "description": "A conexão. Resposta com `Cache-Control: no-store`.",
                "content": {"application/json": {
                    "schema": {"type": "object", "required": ["credentials"], "properties": {"credentials": ref("DatabaseCredentials")}},
                    "example": {"credentials": {
                        "host": "loja-db", "port": 5432, "username": "cube", "password": "q9Zk3Lr_TbW7vXe2Hn5yP-aD1sUcFo8M",
                        "database": "loja_db", "url": "postgresql://cube:q9Zk3Lr_TbW7vXe2Hn5yP-aD1sUcFo8M@loja-db:5432/loja_db", "envName": "DATABASE_URL",
                    }},
                }},
            },
            "401": R401,
            "403": R403_WRITE,
            "404": R404_DB,
            "429": R429,
        },
    },
}

def db_action(action, summary, description, samples_, extra):
    return {
        "post": {
            "operationId": f"{action}Database",
            "summary": summary,
            "description": description,
            "tags": ["Bancos de dados"],
            "parameters": [DB_ID_PARAM],
            "x-codeSamples": samples_,
            "responses": {
                "200": {
                    "description": "O banco depois da ação.",
                    "content": {"application/json": {
                        "schema": {"type": "object", "required": ["database"], "properties": {"database": ref("Database")}},
                        "example": {"database": DATABASE_EXAMPLE if action == "start" else {**DATABASE_EXAMPLE, "status": "stopped", "usage": None, "startedAt": None}},
                    }},
                },
                "401": R401,
                "404": R404_DB,
                "429": R429,
                "503": resp("O servidor dos bancos não respondeu a tempo.", [E_503]),
                **extra,
            },
        },
    }

def action_samples(action):
    return samples(
        f"curl -X POST {BASE}/databases/$DATABASE_ID/{action} \\\n  {KEY_H}",
        f"const res = await fetch(`${{API}}/databases/${{process.env.DATABASE_ID}}/{action}`, {{\n"
        "  method: 'POST',\n  headers,\n});\n"
        "const { database } = await res.json();\n"
        "console.log(database.status);",
        f"r = requests.post(f\"{{API}}/databases/{DB}/{action}\", headers=headers, timeout=120)\n"
        "r.raise_for_status()\n"
        "print(r.json()[\"database\"][\"status\"])",
    )

paths["/databases/{id}/start"] = db_action(
    "start", "Iniciar um banco",
    "Liga o banco parado. Ele só liga se couber no plano de agora: a memória dele somada aos projetos e bancos ligados, e o número de bancos ligados. "
    "Responde quando o banco já subiu; em alguns segundos ele aceita conexões (`starting` → `running`).",
    action_samples("start"),
    {
        "403": resp("A chave é só de leitura, ou o plano não comporta mais um banco ligado.", [E_PERM, E_DB_NOT_ALLOWED, E_DB_LIMIT]),
        "409": resp("O banco tem outra ação em andamento (como o backup do dia), ou a conta está suspensa.", [E_DB_BUSY, E_SUSP, E_BETA, E_FREE_LOST, E_SUSP_MANUAL]),
        "422": resp("A memória do banco não cabe no que sobra do plano com o que está ligado.", [
            ("plan_limit_reached", err("plan_limit_reached", "Este banco usa 512 MB, mas o plano Stack só tem 256 MB livres com o que está ligado. Pare um projeto ou outro banco, ou mude de plano.", freeMemoryMb=256, requestedMemoryMb=512)),
        ]),
    },
)
paths["/databases/{id}/stop"] = db_action(
    "stop", "Parar um banco",
    "Para o banco. Os dados ficam guardados e a memória continua reservada no plano. Os projetos que usam o banco perdem a conexão até você iniciar de novo; parado, ele não ganha o backup do dia.",
    action_samples("stop"),
    {
        "403": R403_WRITE,
        "409": resp("O banco tem outra ação em andamento (como o backup do dia).", [E_DB_BUSY]),
    },
)

paths["/databases/{id}/external-access"] = {
    "delete": {
        "operationId": "disableDatabaseExternalAccess",
        "summary": "Desligar o acesso externo",
        "description": (
            "Desliga o [acesso externo](/hosting/databases#acesso-externo) do banco: o certificado de cliente para de funcionar na hora, e as conexões de fora abertas com ele caem. "
            "Os projetos da conta seguem conectando pelo endereço interno. Já desligado, responde igual. "
            "Ligar e gerar um certificado é só pelo painel, gerado lá (a chave e a senha do `.p12` aparecem uma vez) ou a partir do [seu pedido (CSR)](/hosting/databases#usar-o-seu-próprio-certificado-csr)."
        ),
        "tags": ["Bancos de dados"],
        "parameters": [DB_ID_PARAM],
        "x-codeSamples": samples(
            f"curl -X DELETE {BASE}/databases/$DATABASE_ID/external-access \\\n  {KEY_H}",
            "const res = await fetch(`${API}/databases/${process.env.DATABASE_ID}/external-access`, {\n"
            "  method: 'DELETE',\n  headers,\n});\n"
            "const { database } = await res.json();\n"
            "console.log(database.externalAccess.isEnabled); // false",
            f"r = requests.delete(f\"{{API}}/databases/{DB}/external-access\", headers=headers, timeout=30)\n"
            "r.raise_for_status()\n"
            "print(r.json()[\"database\"][\"externalAccess\"][\"isEnabled\"])",
        ),
        "responses": {
            "200": {
                "description": "O banco, com o acesso externo desligado.",
                "content": {"application/json": {
                    "schema": {"type": "object", "required": ["database"], "properties": {"database": ref("Database")}},
                    "example": {"database": DATABASE_EXAMPLE},
                }},
            },
            "401": R401,
            "403": R403_WRITE,
            "404": R404_DB,
            "429": R429,
            "503": resp("O servidor dos bancos não respondeu a tempo. Tente de novo: o certificado para assim que ele responder.", [E_503]),
        },
    },
}

paths["/databases/{id}/backups"] = {
    "get": {
        "operationId": "listDatabaseBackups",
        "summary": "Listar backups do banco",
        "description": (
            "Os backups do banco, do mais novo: o diário (um por dia com o banco no ar; o que falhou sai de novo em 1 hora) e os de [Fazer backup agora](/api-reference/databases/backup-create), "
            "guardados por 7 dias e até `limit` prontos (o mais antigo sai quando um novo fica pronto). Continuam na página Backups do painel depois de excluir o banco. "
            "Restaurar é só pelo painel. `isAvailable: false` quando o armazenamento dos backups está fora (baixar responde `503`)."
        ),
        "tags": ["Bancos de dados"],
        "parameters": [DB_ID_PARAM],
        "x-codeSamples": samples(
            f"curl {BASE}/databases/$DATABASE_ID/backups \\\n  {KEY_H}",
            "const res = await fetch(`${API}/databases/${process.env.DATABASE_ID}/backups`, { headers });\n"
            "const { backups } = await res.json();\n"
            "console.log(backups[0]?.status, backups[0]?.createdAt);",
            f"r = requests.get(f\"{{API}}/databases/{DB}/backups\", headers=headers, timeout=30)\n"
            "r.raise_for_status()\n"
            "print([b[\"status\"] for b in r.json()[\"backups\"]])",
        ),
        "responses": {
            "200": {
                "description": "Os backups do banco.",
                "content": {"application/json": {
                    "schema": ref("DatabaseBackupList"),
                    "example": {"backups": [DATABASE_BACKUP_EXAMPLE], "limit": 7, "retentionDays": 7, "isAvailable": True},
                }},
            },
            "401": R401,
            "404": R404_DB,
            "429": R429,
        },
    },
}

# Fazer backup agora no banco (cube-hosting#74), como o do projeto.
paths["/databases/{id}/backups"]["post"] = {
    "operationId": "createDatabaseBackup",
    "summary": "Fazer backup do banco",
    "description": (
        "Pede um backup do banco agora, com ele no ar. A resposta chega na hora com o backup em `pending`; ele fica `ready` em alguns segundos "
        "(acompanhe por [Listar backups do banco](/api-reference/databases/backups)). Um por vez em cada banco e na conta; cada banco guarda até 7 prontos, "
        "e o mais antigo sai quando um novo fica pronto. Um backup feito nas últimas 24 horas vale como o do dia."
    ),
    "tags": ["Bancos de dados"],
    "parameters": [DB_ID_PARAM],
    "x-codeSamples": samples(
        f"curl -X POST {BASE}/databases/$DATABASE_ID/backups \\\n  {KEY_H}",
        "const res = await fetch(`${API}/databases/${process.env.DATABASE_ID}/backups`, {\n"
        "  method: 'POST',\n  headers,\n});\n"
        "const { backup } = await res.json();\n"
        "console.log(backup.id, backup.status); // pending",
        f"r = requests.post(f\"{{API}}/databases/{DB}/backups\", headers=headers, timeout=30)\n"
        "r.raise_for_status()\n"
        'print(r.json()["backup"]["id"])',
    ),
    "responses": {
        "202": {
            "description": "Pedido aceito; o backup entra na fila.",
            "content": {"application/json": {
                "schema": {"type": "object", "required": ["backup"], "properties": {"backup": ref("DatabaseBackup")}},
                "example": {"backup": {**DATABASE_BACKUP_EXAMPLE, "type": "manual", "status": "pending", "sizeBytes": None, "finishedAt": None}},
            }},
        },
        "401": R401,
        "403": R403_WRITE,
        "404": R404_DB,
        "409": resp("O banco não está no ar, já tem uma ação ou um backup em andamento, ou a conta está suspensa.", [
            ("database_not_running", err("database_not_running", "Para fazer o backup, o banco precisa estar no ar. Inicie o banco, espere ficar No ar e tente de novo.")),
            E_DB_BUSY,
            ("backup_in_progress", err("backup_in_progress", "Este banco já tem um backup na fila ou sendo feito. Espere terminar para pedir outro.")),
            E_SUSP, E_BETA, E_SUSP_MANUAL,
        ]),
        "429": R429,
        "503": resp("O armazenamento dos backups não respondeu. Nada foi feito.", [E_DB_BK_503]),
    },
}

# Backups da conta e Restaurar como novo (cube-hosting#74): excluir não apaga os backups, que ficam
# até vencer e voltam como um projeto novo, com outro ID, pelo mesmo caminho de criar.
BK_PARAM = {"$ref": "#/components/parameters/BackupId"}
paths["/account/backups"] = {
    "get": {
        "operationId": "listAccountBackups",
        "summary": "Listar os backups da conta",
        "description": (
            "Os backups de todos os projetos da conta, um item por projeto, e depois os de um projeto **apagado**, que ficam por até 30 dias "
            "para baixar pelo painel ou [restaurar como novo](/api-reference/backups/restore-as-new); somando os projetos apagados, a conta guarda os mais recentes "
            "até o número do plano (`limit`). Os bancos de dados excluídos vêm em `deletedDatabases`, com os backups dos últimos 7 dias (os 7 mais recentes da conta). "
            "Vale com a chave de leitura."
        ),
        "tags": ["Backups"],
        "x-codeSamples": samples(
            f"curl {BASE}/account/backups \\\n  {KEY_H}",
            "const res = await fetch(`${API}/account/backups`, { headers });\n"
            "const { projects } = await res.json();\n"
            "const apagados = projects.filter((p) => p.isDeleted);\n"
            "console.log(apagados.map((p) => [p.name, p.backups[0]?.id]));",
            "r = requests.get(f\"{API}/account/backups\", headers=headers, timeout=30)\n"
            "r.raise_for_status()\n"
            "for p in r.json()[\"projects\"]:\n"
            "    if p[\"isDeleted\"]:\n"
            "        print(p[\"name\"], p[\"backups\"][0][\"id\"] if p[\"backups\"] else None)",
        ),
        "responses": {
            "200": {
                "description": "Os backups da conta.",
                "content": {"application/json": {
                    "schema": ref("AccountBackups"),
                    "example": {
                        "limit": 5, "retentionDays": 30, "isDailyAvailable": True,
                        "projects": [
                            {"id": "01J8Z3W6N0Q4Y7V2K5T9D1H3XA", "name": "Meu bot", "type": "bot", "isDeleted": False, "isDailyEnabled": True, "backups": [{**BACKUP_EXAMPLE, "hasConfig": True, "hasVariables": True}]},
                            {"id": "01J8Z5C3R1T6V8X0Z2B4D6F8HK", "name": "Bot antigo", "type": "bot", "isDeleted": True, "isDailyEnabled": False, "backups": [{**BACKUP_EXAMPLE, "id": "7c1d9e2f-3a4b-4c5d-8e6f-0a1b2c3d4e5f", "hasConfig": True, "hasVariables": True}]},
                        ],
                        "deletedDatabases": [
                            {"id": "01J9A2C4E6G8J0K2M4P6R8T0V2", "name": "loja-db", "engine": "postgres", "engineName": "PostgreSQL", "memoryMb": 512, "backups": [DATABASE_BACKUP_EXAMPLE]},
                        ],
                    },
                }},
            },
            "401": R401,
            "429": R429,
        },
    },
}

paths["/account/backups/{backupId}/restore-as-new"] = {
    "post": {
        "operationId": "restoreBackupAsNew",
        "summary": "Restaurar como novo",
        "description": (
            "Cria um projeto **com outro ID** a partir de um backup `ready` da conta (o de um projeto apagado, de [Listar os backups da conta](/api-reference/backups/list-account)), "
            "pelo mesmo caminho de criar um projeto: o código do backup, a configuração que o projeto tinha no momento dele (nome, tipo, linguagem e versão, comando, "
            "arquivo principal, memória, porta, build) e as mesmas variáveis de ambiente, cifradas de novo para o projeto novo. Num site, o subdomínio de antes volta se estiver livre; "
            "se não, sai outro. A memória sobe até o mínimo do plano de agora, se estava abaixo. O projeto passa por `installing` e termina **parado**: você inicia quando conferir. "
            "Vale como um envio: precisa caber no plano, a conta não pode estar suspensa e conta no limite de 1 envio a cada 3 s. "
            "Backup de antes de a configuração ir junto (até 28/09/2026, `hasConfig: false` na lista) usa o `cube.json` do `.zip` e volta sem as variáveis; sem o `cube.json`, `missing_config`. Precisa da chave de **leitura e escrita**."
        ),
        "tags": ["Backups"],
        "parameters": [BK_PARAM],
        "x-codeSamples": samples(
            f"curl -X POST {BASE}/account/backups/$BACKUP_ID/restore-as-new \\\n  {KEY_H}",
            "const res = await fetch(`${API}/account/backups/${process.env.BACKUP_ID}/restore-as-new`, {\n"
            "  method: 'POST',\n  headers,\n});\n"
            "const { project } = await res.json();\n"
            "console.log(project.id, project.status); // installing, depois stopped",
            "r = requests.post(\n    f\"{API}/account/backups/{os.environ['BACKUP_ID']}/restore-as-new\",\n    headers=headers,\n    timeout=780,\n)\n"
            "r.raise_for_status()\n"
            "print(r.json()[\"project\"][\"id\"])",
        ),
        "responses": {
            "201": {
                "description": "Projeto novo criado a partir do backup, instalando as dependências. Ele termina **parado**.",
                "content": {"application/json": {
                    "schema": {"type": "object", "required": ["project"], "properties": {"project": ref("Project")}},
                    "example": {"project": {**INSTALLING, "id": "01J8Z6D4S2U7W9Y1A3C5E7G9JM", "internalHost": "cube-c5e7g9jm", "name": "Bot antigo", "restoredFromBackupId": "7c1d9e2f-3a4b-4c5d-8e6f-0a1b2c3d4e5f"}},
                }},
            },
            "401": R401,
            "403": resp("A chave é só de leitura, ou o plano não comporta este projeto.", [
                E_PERM,
                ("project_limit_reached", err("project_limit_reached", "O plano Free permite até 1 bot. Exclua um projeto ou mude de plano.", limit=1)),
                ("site_not_allowed", err("site_not_allowed", "O plano Free não inclui sites. Mude para um plano pago para hospedar sites e APIs.")),
                ("site_limit_reached", err("site_limit_reached", "O plano Block permite até 2 sites. Exclua um site ou mude de plano.", limit=2)),
            ]),
            "404": resp("O backup não existe ou não é da sua conta (a mesma resposta para os dois).", [E_BK_404]),
            "409": resp("O backup não está pronto, os servidores estão cheios, ou a conta está suspensa, no fim do beta ou sem a vaga do Free.", [
                E_BK_READY,
                ("no_capacity", err("no_capacity", "Nossos servidores estão cheios agora e não dá para liberar mais memória. Tente de novo mais tarde: estamos abrindo mais espaço.")),
                E_SUSP, E_BETA, E_FREE_LOST, E_SUSP_MANUAL,
            ]),
            "422": resp("O backup não abriu, não tem a configuração, ou não cabe na memória do plano. Nada foi criado.", [
                ("insufficient_memory", err("insufficient_memory", "Este bot pede 256 MB, mas o plano Block só tem 124 MB livres somando projetos e bancos de dados. Exclua ou reduza outro projeto ou banco, ou mude de plano, e restaure de novo.", freeMemoryMb=124, requestedMemoryMb=256)),
                ("missing_config", err("missing_config", "Este backup é de antes de a Cube guardar a configuração junto e não tem cube.json, então não dá para saber como iniciar o projeto. Baixe o backup e envie o .zip pelo Novo projeto, informando a linguagem e o comando de início.")),
                ("invalid_backup", err("invalid_backup", "Este backup não pôde ser aberto, e nada foi criado. Tente outro backup.")),
            ]),
            "429": R429_HEAVY,
            "503": resp("O servidor dos projetos, o armazenamento dos backups ou as variáveis não responderam. Nada foi criado.", [E_503, E_BK_503, E_VARS]),
            "507": resp("Os arquivos do backup não cabem no espaço de um projeto novo. Nada foi criado.", [
                ("restore_no_space", err("restore_no_space", "Os arquivos deste backup não cabem no espaço de um projeto novo, e nada foi criado. Baixe o backup, tire o que o projeto não usa e envie como um projeto novo.")),
            ]),
        },
    },
}

paths["/databases/{id}/backups/{backupId}/download"] = {
    "post": {
        "operationId": "createDatabaseBackupDownloadLink",
        "summary": "Pedir o link do backup do banco",
        "description": (
            "Devolve o endereço para baixar o backup do banco. O link vale **5 minutos** e só com a mesma chave (ou a mesma sessão do painel): "
            "com outra conta, responde `404`. Só backups `ready`. Pede a chave de **leitura e escrita**: o backup traz todos os dados do banco."
        ),
        "tags": ["Bancos de dados"],
        "parameters": [DB_ID_PARAM, BACKUP_ID_PARAM],
        "x-codeSamples": samples(
            f"curl -X POST {BASE}/databases/$DATABASE_ID/backups/$BACKUP_ID/download \\\n  {KEY_H}",
            "const res = await fetch(\n"
            "  `${API}/databases/${process.env.DATABASE_ID}/backups/${process.env.BACKUP_ID}/download`,\n"
            "  { method: 'POST', headers },\n"
            ");\n"
            "const { url, expiresAt } = await res.json();\n"
            "console.log(url, expiresAt);",
            f"r = requests.post(\n    f\"{{API}}/databases/{DB}/backups/{DBK}/download\",\n    headers=headers,\n    timeout=30,\n)\n"
            "r.raise_for_status()\n"
            'print(r.json()["url"])',
        ),
        "responses": {
            "200": {
                "description": "O link, relativo ao endereço da API.",
                "content": {"application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["url", "expiresAt"],
                        "properties": {
                            "url": {"type": "string", "description": "Caminho para o `GET` do download, com `expires` e `signature`. Junte ao endereço da API."},
                            "expiresAt": {"type": "string", "format": "date-time", "description": "Até quando o link vale (5 minutos)."},
                        },
                    },
                    "example": {
                        "url": "/databases/01J9A2C4E6G8J0K2M4P6R8T0V2/backups/595bf272-a3da-4d8d-b7d5-ac70868c032d/download?expires=1790530000000&signature=…",
                        "expiresAt": "2026-09-28T12:34:23.000Z",
                    },
                }},
            },
            "401": R401,
            "403": R403_WRITE,
            "404": R404_DB_BACKUP,
            "409": resp("O backup ainda não está pronto ou não deu certo.", [E_DB_BK_READY]),
            "429": R429,
            "503": resp("O armazenamento dos backups não respondeu.", [E_DB_BK_503]),
        },
    },
    "get": {
        "operationId": "downloadDatabaseBackup",
        "summary": "Baixar o backup do banco",
        "description": (
            "Baixa o backup pelo link do [Pedir o link do backup](/api-reference/databases/backup-download-link), com a mesma chave (de leitura e escrita). "
            "O formato é o da ferramenta do próprio banco, e o nome vem no `Content-Disposition` (`<banco>-backup-<data>.<extensão>`): "
            "PostgreSQL `.dump` (`pg_restore`), MySQL `.sql.gz` (gzip com o SQL do `mysqldump`), MongoDB `.archive.gz` (`mongorestore --archive --gzip`) e Redis `.rdb`. "
            "Download com menos bytes que o `Content-Length` não está inteiro: peça o link de novo."
        ),
        "tags": ["Bancos de dados"],
        "parameters": [
            DB_ID_PARAM,
            BACKUP_ID_PARAM,
            {"name": "expires", "in": "query", "required": True, "description": "Vem no `url` do link.", "schema": {"type": "integer"}},
            {"name": "signature", "in": "query", "required": True, "description": "Vem no `url` do link.", "schema": {"type": "string"}},
        ],
        "x-codeSamples": samples(
            f"LINK=$(curl -s -X POST {BASE}/databases/$DATABASE_ID/backups/$BACKUP_ID/download \\\n  {KEY_H} | jq -r .url)\n"
            f"curl -OJ \"{BASE}$LINK\" \\\n  {KEY_H}",
            "const link = await fetch(\n"
            "  `${API}/databases/${process.env.DATABASE_ID}/backups/${process.env.BACKUP_ID}/download`,\n"
            "  { method: 'POST', headers },\n"
            ").then((r) => r.json());\n"
            "const res = await fetch(API + link.url, { headers });\n"
            "await writeFile('loja-db.dump', Buffer.from(await res.arrayBuffer()));",
            f"link = requests.post(\n    f\"{{API}}/databases/{DB}/backups/{DBK}/download\",\n    headers=headers,\n    timeout=30,\n).json()\n"
            "r = requests.get(API + link[\"url\"], headers=headers, timeout=300)\n"
            "r.raise_for_status()\n"
            "with open(\"loja-db.dump\", \"wb\") as f:\n"
            "    f.write(r.content)",
            node_imports="import { writeFile } from 'node:fs/promises';",
        ),
        "responses": {
            "200": {
                "description": "O arquivo do backup.",
                "content": {"application/octet-stream": {"schema": {"type": "string", "format": "binary"}}},
            },
            "401": R401,
            "403": resp("O link venceu (5 minutos) ou foi mexido, ou a chave é só de leitura.", [("download_expired", err("download_expired", "O link de download venceu ou não é desta Conta. Peça o download de novo pelo painel.")), E_PERM]),
            "404": R404_DB_BACKUP,
            "409": resp("O backup ainda não está pronto ou não deu certo.", [E_DB_BK_READY]),
            "429": R429,
            "503": resp("O armazenamento dos backups não respondeu.", [E_DB_BK_503]),
        },
    },
}


# Versões dos envios (cube-hosting#39): o histórico pela chave de leitura; baixar e voltar pela de
# escrita (o zip é o código enviado, às vezes com o .env).
DEPLOYMENT_ID_PARAM = {"$ref": "#/components/parameters/DeploymentId"}
DEPLOYMENT_EXAMPLE = {
    "id": "3f2b8c1e-6a4d-4e7b-9c2a-1d5e8f0a7b36",
    "source": "code_upload",
    "fileName": "bot.zip",
    "sizeBytes": 48230,
    "apiKeyName": "GitHub Actions",
    "hasReinstalledDependencies": False,
    "result": "ok",
    "isRestorable": True,
    "isCurrent": True,
    "restoredFrom": None,
    "startedAt": "2026-09-28T12:00:00.000Z",
    "finishedAt": "2026-09-28T12:00:14.000Z",
    "activatedAt": "2026-09-28T12:00:00.000Z",
}
E_DP_404 = ("not_found", err("not_found", "Versão não encontrada."))
E_DP_GONE = ("deployment_not_available", err("deployment_not_available", "Esta versão não está guardada. Só as versões dos últimos 30 dias, até o limite do seu plano, podem ser baixadas ou restauradas."))
E_DP_503 = ("deployments_unavailable", err("deployments_unavailable", "As versões guardadas não estão disponíveis agora. Tente de novo em instantes."))
R404_DEPLOYMENT = resp("O projeto ou a versão não existe ou não é da sua conta.", [E_404, E_DP_404])
DP = "{os.environ['DEPLOYMENT_ID']}"

paths["/projects/{id}/deployments"] = {
    "get": {
        "operationId": "listDeployments",
        "summary": "Histórico de envios",
        "description": (
            "Os 20 últimos envios do projeto e as versões ainda guardadas, do mais novo, com o resultado da instalação: cada `.zip` enviado (pelo painel, pela CLI ou pela API), "
            "cada Aplicar mudanças, troca de versão da linguagem, backup restaurado e volta para uma versão. "
            "Cada `.zip` fica guardado como **versão** para baixar ou voltar para ele (`isRestorable`): o plano define quantas ficam (`versionLimit`), por até 30 dias, "
            "e ficam as usadas por último (`activatedAt`: o envio ou a volta mais recente para ela). `isCurrent` marca o que está no projeto agora: depois de voltar, é a versão da volta."
        ),
        "tags": ["Versões dos envios"],
        "parameters": [ID_PARAM],
        "x-codeSamples": samples(
            f"curl {BASE}/projects/$PROJECT_ID/deployments \\\n  {KEY_H}",
            "const res = await fetch(`${API}/projects/${process.env.PROJECT_ID}/deployments`, { headers });\n"
            "const { deployments } = await res.json();\n"
            "// A versão que estava no projeto antes da atual: guardada, não é a atual, usada por último.\n"
            "const previous = deployments\n"
            "  .filter((d) => d.isRestorable && !d.isCurrent)\n"
            "  .sort((a, b) => b.activatedAt.localeCompare(a.activatedAt))[0];\n"
            "console.log(previous?.id, previous?.fileName);",
            f"r = requests.get(f\"{{API}}/projects/{PID}/deployments\", headers=headers, timeout=30)\n"
            "r.raise_for_status()\n"
            "for d in r.json()[\"deployments\"]:\n"
            "    print(d[\"id\"], d[\"source\"], d[\"result\"], d[\"isRestorable\"])",
        ),
        "responses": {
            "200": {
                "description": "O histórico e as regras do plano.",
                "content": {"application/json": {
                    "schema": ref("DeploymentList"),
                    "example": {"deployments": [DEPLOYMENT_EXAMPLE], "versionLimit": 3, "retentionDays": 30},
                }},
            },
            "401": R401,
            "404": R404,
            "429": R429,
        },
    },
}

paths["/projects/{id}/deployments/{deploymentId}/download"] = {
    "post": {
        "operationId": "createDeploymentDownloadLink",
        "summary": "Pedir o link da versão",
        "description": (
            "Devolve o endereço para baixar o `.zip` daquela versão, do jeito que foi enviado. O link vale **5 minutos** e só com a mesma chave "
            "(ou a mesma sessão do painel): com outra conta, responde `404`. Só versões com `isRestorable`. Pede a chave de **leitura e escrita**: "
            "o `.zip` é o seu código, às vezes com o `.env`."
        ),
        "tags": ["Versões dos envios"],
        "parameters": [ID_PARAM, DEPLOYMENT_ID_PARAM],
        "x-codeSamples": samples(
            f"curl -X POST {BASE}/projects/$PROJECT_ID/deployments/$DEPLOYMENT_ID/download \\\n  {KEY_H}",
            "const res = await fetch(\n"
            "  `${API}/projects/${process.env.PROJECT_ID}/deployments/${process.env.DEPLOYMENT_ID}/download`,\n"
            "  { method: 'POST', headers },\n"
            ");\n"
            "const { url, expiresAt } = await res.json();\n"
            "console.log(url, expiresAt);",
            f"r = requests.post(\n    f\"{{API}}/projects/{PID}/deployments/{DP}/download\",\n    headers=headers,\n    timeout=30,\n)\n"
            "r.raise_for_status()\n"
            'print(r.json()["url"])',
        ),
        "responses": {
            "200": {
                "description": "O link, relativo ao endereço da API.",
                "content": {"application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["url", "expiresAt"],
                        "properties": {
                            "url": {"type": "string", "description": "Caminho para o `GET` do download, com `expires` e `signature`. Junte ao endereço da API."},
                            "expiresAt": {"type": "string", "format": "date-time", "description": "Até quando o link vale (5 minutos)."},
                        },
                    },
                    "example": {
                        "url": "/projects/01J8Z3W6N0Q4Y7V2K5T9D1H3XA/deployments/3f2b8c1e-6a4d-4e7b-9c2a-1d5e8f0a7b36/download?expires=1790530000000&signature=…",
                        "expiresAt": "2026-09-28T12:05:00.000Z",
                    },
                }},
            },
            "401": R401,
            "403": R403_WRITE,
            "404": R404_DEPLOYMENT,
            "409": resp("A versão não está mais guardada (passou do limite do plano ou dos 30 dias, ou foi excluída), ou a linha não guarda arquivos.", [E_DP_GONE]),
            "429": R429,
            "503": resp("O armazenamento das versões não respondeu.", [E_DP_503]),
        },
    },
    "get": {
        "operationId": "downloadDeployment",
        "summary": "Baixar a versão",
        "description": (
            "Baixa o `.zip` da versão pelo link do [Pedir o link da versão](/api-reference/deployments/download-link), com a mesma chave "
            "(de leitura e escrita). O nome do arquivo vem no `Content-Disposition` (`<projeto>-versao-<data>.zip`). "
            "Download que chega com menos bytes que o `Content-Length` não está inteiro: peça o link de novo."
        ),
        "tags": ["Versões dos envios"],
        "parameters": [
            ID_PARAM,
            DEPLOYMENT_ID_PARAM,
            {"name": "expires", "in": "query", "required": True, "description": "Vem no `url` do link.", "schema": {"type": "integer"}},
            {"name": "signature", "in": "query", "required": True, "description": "Vem no `url` do link.", "schema": {"type": "string"}},
        ],
        "x-codeSamples": samples(
            f"LINK=$(curl -s -X POST {BASE}/projects/$PROJECT_ID/deployments/$DEPLOYMENT_ID/download \\\n  {KEY_H} | jq -r .url)\n"
            f"curl -o versao.zip \"{BASE}$LINK\" \\\n  {KEY_H}",
            "const link = await fetch(\n"
            "  `${API}/projects/${process.env.PROJECT_ID}/deployments/${process.env.DEPLOYMENT_ID}/download`,\n"
            "  { method: 'POST', headers },\n"
            ").then((r) => r.json());\n"
            "const res = await fetch(API + link.url, { headers });\n"
            "await writeFile('versao.zip', Buffer.from(await res.arrayBuffer()));",
            f"link = requests.post(\n    f\"{{API}}/projects/{PID}/deployments/{DP}/download\",\n    headers=headers,\n    timeout=30,\n).json()\n"
            "r = requests.get(API + link[\"url\"], headers=headers, timeout=300)\n"
            "r.raise_for_status()\n"
            "with open(\"versao.zip\", \"wb\") as f:\n"
            "    f.write(r.content)",
            node_imports="import { writeFile } from 'node:fs/promises';",
        ),
        "responses": {
            "200": {
                "description": "O `.zip` da versão: igual ao enviado ou, na `file_editor`, os arquivos do Aplicar mudanças.",
                "content": {"application/zip": {"schema": {"type": "string", "format": "binary"}}},
            },
            "401": R401,
            "403": resp("O link venceu (5 minutos) ou foi mexido, ou a chave é só de leitura.", [("download_expired", err("download_expired", "O link de download venceu ou não é desta Conta. Peça o download de novo pelo painel.")), E_PERM]),
            "404": R404_DEPLOYMENT,
            "409": resp("A versão não está mais guardada.", [E_DP_GONE]),
            "429": R429,
            "503": resp("O armazenamento das versões não respondeu.", [E_DP_503]),
        },
    },
}

paths["/projects/{id}/deployments/{deploymentId}/rollback"] = {
    "post": {
        "operationId": "rollbackDeployment",
        "summary": "Voltar para a versão",
        "description": (
            "Troca os arquivos do projeto pelos daquela versão (o `.zip` enviado ou, na `file_editor`, os arquivos do Aplicar mudanças), pelo mesmo caminho de [Enviar novo código](/api-reference/projects/upload-code): "
            "o projeto **para antes**, os arquivos são trocados, as dependências só são instaladas de novo se o `package.json` ou o `requirements.txt` mudou, "
            "e a configuração (comando, memória, variáveis) continua a de agora. O projeto termina **parado**, a não ser com `shouldStart: true`, "
            "que liga depois da instalação (se ele couber no plano, como o [Iniciar](/api-reference/projects/start)). "
            "A resposta chega quando os arquivos já foram trocados, com o projeto em `installing`; acompanhe pelos logs de instalação. "
            "Guia em [Versões e voltar atrás](/hosting/versions)."
        ),
        "tags": ["Versões dos envios"],
        "parameters": [ID_PARAM, DEPLOYMENT_ID_PARAM],
        "requestBody": {
            "required": False,
            "content": {"application/json": {
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "shouldStart": {"type": "boolean", "default": False, "description": "`true` liga o projeto quando a instalação terminar. Sem ele, o projeto fica parado até você iniciar."},
                    },
                },
                "example": {"shouldStart": True},
            }},
        },
        "x-codeSamples": samples(
            f"curl -X POST {BASE}/projects/$PROJECT_ID/deployments/$DEPLOYMENT_ID/rollback \\\n  {KEY_H} \\\n"
            "  -H 'Content-Type: application/json' \\\n  -d '{\"shouldStart\": true}'",
            "const res = await fetch(\n"
            "  `${API}/projects/${process.env.PROJECT_ID}/deployments/${process.env.DEPLOYMENT_ID}/rollback`,\n"
            "  {\n    method: 'POST',\n    headers: { ...headers, 'Content-Type': 'application/json' },\n"
            "    body: JSON.stringify({ shouldStart: true }),\n  },\n);\n"
            "const { project, isReinstallingDependencies } = await res.json();\n"
            "console.log(project.status, isReinstallingDependencies); // installing",
            f"r = requests.post(\n    f\"{{API}}/projects/{PID}/deployments/{DP}/rollback\",\n    headers=headers,\n"
            "    json={\"shouldStart\": True},\n    timeout=300,\n)\n"
            "r.raise_for_status()\n"
            'print(r.json()["project"]["status"])',
        ),
        "responses": {
            "202": {
                "description": "Os arquivos voltaram aos da versão, e a instalação começou.",
                "content": {"application/json": {
                    "schema": ref("InstallStarted"),
                    "example": {"project": INSTALLING, "isReinstallingDependencies": False},
                }},
            },
            "400": resp("O corpo está fora do formato.", [("invalid_request", err("invalid_request", 'Envie { "shouldStart": true } para iniciar depois, ou false (o padrão).'))]),
            "401": R401,
            "403": resp("A chave é só de leitura, ou (com `shouldStart`) o plano não inclui sites.", [E_PERM, ("site_not_allowed", err("site_not_allowed", "O plano Free não inclui sites. Mude para um plano pago para colocar este site no ar."))]),
            "404": R404_DEPLOYMENT,
            "413": resp("A versão de um `.zip` foi guardada num plano maior e passa do limite do `.zip` do plano de agora (a `file_editor` não tem esse limite). Nada mudou.", [("invalid_zip", err("invalid_zip", "Esta versão passa do limite de 5 MB do .zip no plano Free. Baixe a versão, tire o que o projeto não usa e envie o .zip de novo.", limitMb=5))]),
            "409": resp("A versão não está mais guardada, o projeto está instalando ou com outra ação, falta (com `shouldStart`) uma variável obrigatória do template, ou a conta está suspensa. Nada mudou.", [E_DP_GONE, E_BUSY, E_MISSING_VARS, E_SUSP, E_BETA, E_FREE_LOST, E_SUSP_MANUAL]),
            "422": resp("O `.zip` foi recusado na troca, a versão do Aplicar mudanças não abriu, ou (com `shouldStart`) o projeto não cabe no plano ligado. Os arquivos e o projeto ficaram como estavam.", [
                ("unsafe_zip", err("unsafe_zip", "Descompactado, o projeto passa do limite de 500 MB. Tire os arquivos grandes que o bot não usa e envie de novo.", reason="size")),
                ("invalid_backup", err("invalid_backup", "Esta versão não pôde ser aberta, e os arquivos e o projeto ficaram como estavam. Tente outra versão.")),
                ("plan_limit_reached", err("plan_limit_reached", "Este projeto usa 512 MB, mas o plano Block só tem 256 MB livres com os projetos que estão ligados. Diminua a memória dele em Configurações ou pare outro projeto.", freeMemoryMb=256, requestedMemoryMb=512)),
            ]),
            "429": R429_HEAVY,
            "507": resp("A versão do Aplicar mudanças, os arquivos de agora e os restaurados não cabem juntos no espaço do projeto. Os arquivos e o projeto ficaram como estavam.", [("restore_no_space", err("restore_no_space", "Não há espaço no projeto para voltar para esta versão: a versão, os arquivos de agora e os restaurados precisam caber juntos. Os arquivos e o projeto ficaram como estavam. Apague arquivos grandes que o projeto não usa e tente de novo."))]),
            "503": resp("O armazenamento das versões não respondeu (nada mudou), ou o servidor dos projetos não respondeu no meio da troca: aí o projeto fica parado e a mensagem diz isso.", [E_DP_503, ("server_unavailable", err("server_unavailable", "O servidor dos projetos não respondeu no meio da troca de versão. O projeto ficou parado: confira os arquivos antes de iniciar ou tente de novo em instantes."))]),
        },
    },
}

# Avisos por e-mail (cube-hosting#33): a chave lê as preferências; mudar é só no painel.
paths["/projects/{id}/alerts"] = {
    "get": {
        "operationId": "getAlerts",
        "summary": "Ver os avisos",
        "description": (
            "Quais avisos por e-mail estão ligados no projeto: queda, loop de erro e memória alta, e se "
            "eles também saem por mensagem direta no Discord (`isDiscordEnabled`, só com o Discord "
            "vinculado à conta: `isDiscordLinked`). "
            "Os avisos existem nos planos pagos; no Free, `isAvailable` é `false` e todos vêm `false`. "
            "Ligar e desligar é pelo painel, em Configurações › Avisos. Guia em [Avisos por e-mail](/hosting/alerts)."
        ),
        "tags": ["Avisos"],
        "parameters": [ID_PARAM],
        "x-codeSamples": samples(
            f"curl {BASE}/projects/$PROJECT_ID/alerts \\\n  {KEY_H}",
            "const res = await fetch(`${API}/projects/${process.env.PROJECT_ID}/alerts`, { headers });\n"
            "const alerts = await res.json();\n"
            "console.log(alerts.isCrashEnabled, alerts.isCrashLoopEnabled, alerts.isHighMemoryEnabled);",
            f"r = requests.get(f\"{{API}}/projects/{PID}/alerts\", headers=headers, timeout=30)\n"
            "r.raise_for_status()\n"
            "print(r.json())",
        ),
        "responses": {
            "200": {
                "description": "Os avisos do projeto.",
                "content": {"application/json": {
                    "schema": ref("AlertSettings"),
                    "example": {"isAvailable": True, "isCrashEnabled": True, "isCrashLoopEnabled": True, "isHighMemoryEnabled": False, "isDiscordEnabled": True, "isDiscordLinked": True},
                }},
            },
            "401": R401,
            "404": R404,
            "429": R429,
        },
    },
}

# Blob (cube-hosting#17): listar, ver e o link temporário com a chave de leitura; pedir o envio,
# confirmar, tornar público ou privado e apagar com a de escrita. A chave Só Blob faz tudo isso e
# nada fora do Blob.
BLOB_ID_PARAM = {"$ref": "#/components/parameters/BlobObjectId"}
BLOB_OBJECT_EXAMPLE = {
    "id": "01JA3F7K2M9P4R6T8V0X1Z3B5D",
    "path": "img/logo.png",
    "sizeBytes": 23456,
    "contentType": "image/png",
    "status": "ready",
    "visibility": "public",
    "publicUrl": "https://cdn.cubehost.dev/q7Rf2kLm9xA1/logo.png",
    "expiresAt": None,
    "cacheMaxAgeSeconds": None,
    "isDownloadForced": False,
    "createdAt": "2026-09-28T13:10:02.000Z",
}
BLOB_USAGE_EXAMPLE = {
    "usedBytes": 48213991,
    "quotaBytes": 5368709120,
    "objectCount": 7,
    "maxObjectBytes": 1073741824,
    "multipartThresholdBytes": 16777216,
    "isAvailable": True,
}
E_BLOB_EXT = ("extension_not_allowed", err(
    "extension_not_allowed",
    "A regra da pasta backups só aceita arquivos .zip, .tar.gz. Envie para outra pasta ou troque a regra na aba Regras de pasta do Blob.",
    folder="backups", allowedExtensions=["zip", "tar.gz"],
))
E_BLOB_RULE_SIZE = ("folder_file_too_large", err(
    "folder_file_too_large",
    "Este arquivo tem 80 MB, e a regra da pasta backups/diarios aceita até 50 MB por arquivo. Diminua o arquivo, envie para outra pasta ou troque a regra na aba Regras de pasta do Blob.",
    folder="backups/diarios", maxBytes=52428800,
))
E_BLOB_EXISTS = ("object_exists", err(
    "object_exists",
    "Já existe um arquivo chamado img/logo.png no Blob. Para trocar, envie de novo substituindo o que existe (shouldOverwrite); para manter os dois, use o sufixo de segurança no nome (shouldAddRandomSuffix).",
))
E_BLOB_EXPIRED = ("upload_expired", err("upload_expired", "Este envio em partes passou das 24 horas e foi cancelado. Envie o arquivo de novo."))
E_BLOB_NOT_MULTIPART = ("not_multipart", err("not_multipart", "Este arquivo não está sendo enviado em partes. Confira o id ou peça o envio com isMultipart: true."))
BLOB_RULE_EXAMPLE = {
    "folder": "backups/diarios",
    "defaultVisibility": "private",
    "defaultExpirationDays": 30,
    "cacheMaxAgeSeconds": None,
    "maxFileSizeBytes": 52428800,
    "allowedExtensions": ["zip", "tar.gz"],
    "deleteAfterDays": 7,
    "deletionStartsAt": "2026-10-01T13:10:02.000Z",
    "updatedAt": "2026-09-30T13:10:02.000Z",
}
E_BLOB_404 = ("not_found", err("not_found", "Arquivo não encontrado no Blob."))
R404_BLOB = resp("O arquivo não existe ou não é da sua conta (a mesma resposta para os dois).", [E_BLOB_404])
E_BLOB_503 = ("blob_unavailable", err("blob_unavailable", "O Blob não está disponível agora. Tente de novo em instantes."))
R503_BLOB = resp("O armazenamento do Blob não respondeu. Nada mudou.", [E_BLOB_503])
E_BLOB_QUOTA = ("blob_quota_exceeded", err(
    "blob_quota_exceeded",
    "Este arquivo (200 MB) não cabe no Blob do plano Block: 4,9 GB de 5 GB já estão ocupados. Apague arquivos que não usa ou mude para um plano maior.",
    usedBytes=5261334937, quotaBytes=5368709120, sizeBytes=209715200,
))
BLOB_ID = "{os.environ['BLOB_ID']}"

paths["/blob/objects"] = {
    "get": {
        "operationId": "listBlobObjects",
        "summary": "Listar arquivos do Blob",
        "description": (
            "Os arquivos do Blob da conta, na ordem do nome, e o uso da cota do plano. `prefix` filtra pelo começo do nome "
            "(uma pasta é o começo com `/`: `img/`); com `delimiter=/`, o que fica dentro de uma subpasta vem junto em `folders`. "
            "`search` procura o texto no nome inteiro, sem diferenciar maiúsculas (e ignora o `delimiter`). "
            "Com mais itens que o `limit`, `nextCursor` vem preenchido: mande de volta em `cursor` para a próxima página. "
            "Só aparece o que já foi confirmado (`complete`). Guia em [Blob](/hosting/blob)."
        ),
        "tags": ["Blob"],
        "parameters": [
            {"name": "prefix", "in": "query", "description": "O começo do nome (ex.: `img/`).", "schema": {"type": "string", "maxLength": 1024}},
            {"name": "delimiter", "in": "query", "description": "Só `/`: junta as subpastas em `folders`.", "schema": {"type": "string", "enum": ["/"]}},
            {"name": "search", "in": "query", "description": "Texto que o nome precisa conter.", "schema": {"type": "string", "maxLength": 200}},
            {"name": "cursor", "in": "query", "description": "O `nextCursor` da página anterior.", "schema": {"type": "string"}},
            {"name": "limit", "in": "query", "description": "Itens por página, de 1 a 1000.", "schema": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 100}},
        ],
        "x-codeSamples": samples(
            f"curl \"{BASE}/blob/objects?delimiter=/&prefix=img/\" \\\n  {KEY_H}",
            "const res = await fetch(`${API}/blob/objects?delimiter=/&prefix=img/`, { headers });\n"
            "const { objects, folders, usage } = await res.json();\n"
            "for (const f of folders) console.log(f.prefix, f.objectCount);\n"
            "for (const o of objects) console.log(o.path, o.sizeBytes);\n"
            "console.log(`${usage.usedBytes} de ${usage.quotaBytes} bytes`);",
            "r = requests.get(\n"
            "    f\"{API}/blob/objects\",\n"
            "    headers=headers,\n"
            "    params={\"delimiter\": \"/\", \"prefix\": \"img/\"},\n"
            "    timeout=30,\n"
            ")\n"
            "r.raise_for_status()\n"
            "for o in r.json()[\"objects\"]:\n"
            "    print(o[\"path\"], o[\"sizeBytes\"])",
        ),
        "responses": {
            "200": {
                "description": "Os arquivos, as subpastas e o uso da cota.",
                "content": {"application/json": {
                    "schema": ref("BlobList"),
                    "example": {
                        "objects": [BLOB_OBJECT_EXAMPLE],
                        "folders": [{"prefix": "img/icones/", "objectCount": 3, "sizeBytes": 12288}],
                        "nextCursor": None,
                        "usage": BLOB_USAGE_EXAMPLE,
                    },
                }},
            },
            "400": resp("Um parâmetro saiu do formato.", [("invalid_request", err("invalid_request", 'Use prefix, delimiter "/", search, cursor e limit de 1 a 1000.'))]),
            "401": R401,
            "429": R429,
        },
    },
    "post": {
        "operationId": "createBlobUpload",
        "summary": "Pedir o envio de um arquivo",
        "description": (
            "Primeiro passo do envio: diga o nome (`path`, com pastas por `/`), o tamanho exato em bytes e o tipo, e a resposta traz um link de "
            "**15 minutos** para mandar o arquivo direto ao armazenamento com `PUT`, sem passar pelo servidor dos projetos "
            "(`upload.type: \"single\"`). O link só aceita **esse tamanho e esse tipo**: mande o `Content-Type` de `upload.headers` e o corpo com o arquivo "
            "(o `Content-Length` sai sozinho). **Não mande a chave de API no `PUT`**. Depois, chame "
            "[Confirmar o envio](/api-reference/blob/complete). Com `isMultipart: true`, o envio vai **em partes** de 16 MB que continuam de onde pararam "
            "por até 24 horas (`upload.type: \"multipart\"`, com `partSizeBytes` e `partCount`): peça as URLs em [Pedir as URLs das partes](/api-reference/blob/parts-create). "
            "A cota do plano é conferida aqui (somando os envios em andamento: 15 minutos no envio simples e 24 horas no em partes) e de novo na confirmação. "
            "Um arquivo que chega pelo link e não é confirmado em 10 minutos é removido. Mesmo nome de um arquivo que já existe: o novo entra no lugar quando "
            "for confirmado, com um link novo; com `shouldOverwrite: false`, a resposta é `409 object_exists` e nada muda. `shouldAddRandomSuffix` põe "
            "8 letras e números aleatórios antes da extensão (o `path` da resposta é o final). "
            "Cada arquivo vai até o **teto do plano** (`maxObjectBytes` da lista: 1/5 da cota, até 4 GB); o arquivo sobe do jeito que você mandar. "
            "A **regra da pasta** (a de caminho mais longo, em [Regras de pasta](/api-reference/blob/folder-rules-get)) vale aqui: extensão fora da lista → `422 extension_not_allowed`, "
            "acima do tamanho dela → `413 folder_file_too_large`; sem `visibility` ou `expiresAt`, valem os padrões dela. "
            "Com `visibility: \"public\"`, o arquivo pronto ganha o `publicUrl`, um link fixo que não vence; sem ele (e sem regra), fica privado. "
            "`expiresAt` apaga o arquivo na data (`null`: nunca vence) e `isDownloadForced` faz o link sempre baixar. O Free não tem Blob."
        ),
        "tags": ["Blob"],
        "requestBody": {
            "required": True,
            "content": {"application/json": {
                "schema": ref("BlobUploadInput"),
                "example": {"path": "img/logo.png", "sizeBytes": 23456, "contentType": "image/png", "visibility": "public"},
            }},
        },
        "x-codeSamples": samples(
            f"SIZE=$(wc -c < logo.png | tr -d ' ')\n"
            f"UP=$(curl -s -X POST {BASE}/blob/objects \\\n  {KEY_H} \\\n  -H \"Content-Type: application/json\" \\\n"
            "  -d \"{\\\"path\\\": \\\"img/logo.png\\\", \\\"sizeBytes\\\": $SIZE, \\\"contentType\\\": \\\"image/png\\\"}\")\n"
            "# O arquivo vai direto no link, sem a chave de API.\n"
            "curl -X PUT \"$(echo \"$UP\" | jq -r .upload.url)\" -H \"Content-Type: image/png\" --data-binary @logo.png\n"
            f"curl -X POST {BASE}/blob/objects/$(echo \"$UP\" | jq -r .object.id)/complete \\\n  {KEY_H}",
            "const file = await readFile('logo.png');\n"
            "const res = await fetch(`${API}/blob/objects`, {\n"
            "  method: 'POST',\n"
            "  headers: { ...headers, 'Content-Type': 'application/json' },\n"
            "  body: JSON.stringify({ path: 'img/logo.png', sizeBytes: file.length, contentType: 'image/png' }),\n"
            "});\n"
            "const { object, upload } = await res.json();\n"
            "// Direto no link, sem a chave de API.\n"
            "await fetch(upload.url, { method: 'PUT', headers: upload.headers, body: file });\n"
            "await fetch(`${API}/blob/objects/${object.id}/complete`, { method: 'POST', headers });",
            "size = os.path.getsize(\"logo.png\")\n"
            "r = requests.post(\n"
            "    f\"{API}/blob/objects\",\n"
            "    headers=headers,\n"
            "    json={\"path\": \"img/logo.png\", \"sizeBytes\": size, \"contentType\": \"image/png\"},\n"
            "    timeout=30,\n"
            ")\n"
            "r.raise_for_status()\n"
            "up = r.json()\n"
            "# Direto no link, sem a chave de API.\n"
            "with open(\"logo.png\", \"rb\") as f:\n"
            "    requests.put(up[\"upload\"][\"url\"], data=f, headers=up[\"upload\"][\"headers\"], timeout=3600).raise_for_status()\n"
            "requests.post(f\"{API}/blob/objects/{up['object']['id']}/complete\", headers=headers, timeout=30).raise_for_status()",
            node_imports="import { readFile } from 'node:fs/promises';",
        ),
        "responses": {
            "201": {
                "description": "O envio foi reservado: mande o arquivo no link e confirme.",
                "content": {"application/json": {
                    "schema": ref("BlobUpload"),
                    "example": {
                        "object": {**BLOB_OBJECT_EXAMPLE, "status": "pending"},
                        "upload": {
                            "type": "single",
                            "url": "https://…/accounts/…/blob/01JA3F7K2M9P4R6T8V0X1Z3B5D?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Expires=900&X-Amz-SignedHeaders=content-length%3Bcontent-type%3Bhost&X-Amz-Signature=…",
                            "method": "PUT",
                            "headers": {"content-type": "image/png"},
                            "expiresAt": "2026-09-28T13:25:02.000Z",
                        },
                    },
                }},
            },
            "400": resp("O corpo, o nome ou o tipo não valem.", [
                ("invalid_request", err("invalid_request", "Mande path, sizeBytes (inteiro, em bytes) e, se quiser, contentType.")),
                ("invalid_path", err("invalid_path", 'Nome de arquivo inválido. Use até 1024 bytes, pastas separadas por "/", sem começar ou terminar com "/" e sem "..".')),
            ]),
            "401": R401,
            "403": resp("A chave é só de leitura, ou o plano não tem Blob (Free).", [E_PERM, ("blob_not_in_plan", err("blob_not_in_plan", "O Blob é dos planos pagos. Assine um plano em Plano e cobrança para enviar arquivos."))]),
            "409": resp("A conta chegou a 100.000 arquivos, já existe um arquivo com o nome (com `shouldOverwrite: false`), ou a conta está suspensa.", [
                ("blob_object_limit_reached", err("blob_object_limit_reached", "O Blob da conta chegou a 100.000 arquivos. Apague os que não usa ou junte arquivos pequenos num .zip.")),
                E_BLOB_EXISTS, E_SUSP, E_BETA, E_FREE_LOST, E_SUSP_MANUAL,
            ]),
            "413": resp("O arquivo passa do teto do plano ou do tamanho da regra da pasta, ou não cabe na cota do plano.", [
                ("file_too_large", err("file_too_large", "Este arquivo tem 1,5 GB e passa do limite do Blob no plano Block: cada arquivo pode ter até 1 GB. Divida o arquivo em partes menores ou mude para um plano maior e envie de novo.", maxBytes=1073741824)),
                E_BLOB_RULE_SIZE,
                E_BLOB_QUOTA,
            ]),
            "422": resp("A regra da pasta não aceita a extensão do arquivo.", [E_BLOB_EXT]),
            "429": R429,
            "503": R503_BLOB,
        },
    },
}

paths["/blob/objects/{id}"] = {
    "get": {
        "operationId": "getBlobObject",
        "summary": "Ver um arquivo do Blob",
        "description": "O nome, o tamanho, o tipo, a visibilidade e a data de um arquivo, com o `publicUrl` quando ele é público. `status` é `pending` enquanto o envio não foi confirmado.",
        "tags": ["Blob"],
        "parameters": [BLOB_ID_PARAM],
        "x-codeSamples": samples(
            f"curl {BASE}/blob/objects/$BLOB_ID \\\n  {KEY_H}",
            "const res = await fetch(`${API}/blob/objects/${process.env.BLOB_ID}`, { headers });\n"
            "const { object } = await res.json();\n"
            "console.log(object.path, object.sizeBytes, object.status);",
            f"r = requests.get(f\"{{API}}/blob/objects/{BLOB_ID}\", headers=headers, timeout=30)\n"
            "r.raise_for_status()\n"
            "print(r.json()[\"object\"])",
        ),
        "responses": {
            "200": {
                "description": "O arquivo.",
                "content": {"application/json": {
                    "schema": {"type": "object", "required": ["object"], "properties": {"object": ref("BlobObject")}},
                    "example": {"object": BLOB_OBJECT_EXAMPLE},
                }},
            },
            "401": R401,
            "404": R404_BLOB,
            "429": R429,
        },
    },
    "patch": {
        "operationId": "updateBlobObject",
        "summary": "Tornar público ou privado",
        "description": (
            "Público: o arquivo ganha o `publicUrl`, `https://cdn.cubehost.dev/<id>/<nome>`, um link fixo que **não vence** e abre sem chave "
            "(imagem abre no navegador; o resto baixa). Privado: o link público para **na hora**, antes da resposta, e o arquivo só sai por "
            "[link temporário](/api-reference/blob/download-url). Tornar público de novo volta o mesmo link. Entra na Atividade da conta."
        ),
        "tags": ["Blob"],
        "parameters": [BLOB_ID_PARAM],
        "requestBody": {
            "required": True,
            "content": {"application/json": {
                "schema": {
                    "type": "object",
                    "required": ["visibility"],
                    "additionalProperties": False,
                    "properties": {"visibility": {"type": "string", "enum": ["public", "private"]}},
                },
                "example": {"visibility": "public"},
            }},
        },
        "x-codeSamples": samples(
            f"curl -X PATCH {BASE}/blob/objects/$BLOB_ID \\\n  {KEY_H} \\\n  -H \"Content-Type: application/json\" \\\n  -d '{{\"visibility\": \"public\"}}'",
            "const res = await fetch(`${API}/blob/objects/${process.env.BLOB_ID}`, {\n"
            "  method: 'PATCH',\n"
            "  headers: { ...headers, 'Content-Type': 'application/json' },\n"
            "  body: JSON.stringify({ visibility: 'public' }),\n"
            "});\n"
            "const { object } = await res.json();\n"
            "console.log(object.publicUrl);",
            f"r = requests.patch(f\"{{API}}/blob/objects/{BLOB_ID}\", headers=headers, json={{\"visibility\": \"public\"}}, timeout=30)\n"
            "r.raise_for_status()\n"
            "print(r.json()[\"object\"][\"publicUrl\"])",
        ),
        "responses": {
            "200": {
                "description": "O arquivo, com a visibilidade nova.",
                "content": {"application/json": {
                    "schema": {"type": "object", "required": ["object"], "properties": {"object": ref("BlobObject")}},
                    "example": {"object": BLOB_OBJECT_EXAMPLE},
                }},
            },
            "400": resp("`visibility` fora de `public` e `private`.", [("invalid_request", err("invalid_request", 'Mande visibility: "public" ou "private".'))]),
            "401": R401,
            "403": R403_WRITE,
            "404": R404_BLOB,
            "429": R429,
            "503": resp("O armazenamento não respondeu: nada mudou. Tente de novo.", [E_BLOB_503]),
        },
    },
    "delete": {
        "operationId": "deleteBlobObject",
        "summary": "Apagar um arquivo do Blob",
        "description": (
            "Apaga o arquivo do armazenamento e da lista, e o espaço volta para a cota. O link público e os temporários que já saíram param de funcionar na hora. "
            "Num envio que não terminou (`pending`), cancela. Enquanto o link de envio do arquivo vale (15 minutos desde o pedido), o tamanho dele segue reservado na cota: o link não se desfaz, e o que for mandado por ele depois de apagar é removido. Não tem volta."
        ),
        "tags": ["Blob"],
        "parameters": [BLOB_ID_PARAM],
        "x-codeSamples": samples(
            f"curl -X DELETE {BASE}/blob/objects/$BLOB_ID \\\n  {KEY_H}",
            "const res = await fetch(`${API}/blob/objects/${process.env.BLOB_ID}`, { method: 'DELETE', headers });\n"
            "console.log(res.status); // 204",
            f"r = requests.delete(f\"{{API}}/blob/objects/{BLOB_ID}\", headers=headers, timeout=30)\n"
            "r.raise_for_status()",
        ),
        "responses": {
            "204": {"description": "Apagado."},
            "401": R401,
            "403": R403_WRITE,
            "404": R404_BLOB,
            "429": R429,
            "503": resp("O armazenamento não respondeu: o arquivo continua lá. Tente de novo.", [E_BLOB_503]),
        },
    },
}

paths["/blob/objects/{id}/complete"] = {
    "post": {
        "operationId": "completeBlobUpload",
        "summary": "Confirmar o envio",
        "description": (
            "Segundo passo do envio, depois do `PUT` no link de [Pedir o envio](/api-reference/blob/create): a Cube confere que o arquivo chegou inteiro "
            "e confere a cota de novo, agora com o que chegou de verdade. Passou da cota (outro envio entrou antes), o arquivo sai e a resposta é `413`. "
            "Confirmado, ele aparece na lista (`status: ready`) e, se já havia um arquivo com o mesmo nome, o antigo sai. Confirmar de novo devolve o mesmo. "
            "No envio em partes, a Cube junta as partes só com todas do tamanho certo; senão, `409 upload_incomplete` traz `missingParts`, as que faltam."
        ),
        "tags": ["Blob"],
        "parameters": [BLOB_ID_PARAM],
        "x-codeSamples": samples(
            f"curl -X POST {BASE}/blob/objects/$BLOB_ID/complete \\\n  {KEY_H}",
            "const res = await fetch(`${API}/blob/objects/${process.env.BLOB_ID}/complete`, { method: 'POST', headers });\n"
            "const { object } = await res.json();\n"
            "console.log(object.status); // ready",
            f"r = requests.post(f\"{{API}}/blob/objects/{BLOB_ID}/complete\", headers=headers, timeout=30)\n"
            "r.raise_for_status()\n"
            "print(r.json()[\"object\"][\"status\"])",
        ),
        "responses": {
            "200": {
                "description": "O arquivo, pronto.",
                "content": {"application/json": {
                    "schema": {"type": "object", "required": ["object"], "properties": {"object": ref("BlobObject")}},
                    "example": {"object": BLOB_OBJECT_EXAMPLE},
                }},
            },
            "401": R401,
            "403": R403_WRITE,
            "404": R404_BLOB,
            "409": resp("O arquivo ainda não chegou inteiro pelo link (no envio em partes, com as que faltam), ou o envio em partes passou das 24 horas.", [
                ("upload_incomplete", err("upload_incomplete", "O arquivo ainda não chegou inteiro. Termine o envio pela URL (PUT) e confirme de novo; se a URL venceu, peça outra.")),
                ("upload_incomplete_parts", err("upload_incomplete", "Faltam 1 de 3 partes (a primeira é a 2). Mande as que faltam e confirme de novo.", missingParts=[2])),
                E_BLOB_EXPIRED,
            ]),
            "413": resp("Com o que já está guardado, o arquivo passa da cota: ele sai.", [E_BLOB_QUOTA]),
            "429": R429,
            "503": R503_BLOB,
        },
    },
}

paths["/blob/objects/{id}/download-url"] = {
    "post": {
        "operationId": "createBlobDownloadUrl",
        "summary": "Pedir o link temporário",
        "description": (
            "Um link curto para abrir ou baixar o arquivo, público ou privado, sem a chave: "
            "`https://cdn.cubehost.dev/s/<token>/<nome>`. Vale **5 minutos** (ou o `expiresInSeconds`, de 60 a 3600) e só abre esse arquivo. "
            "Depois do prazo, ou com qualquer parte do token mudada, ele é recusado (`403`); com outro nome no fim, `404`. "
            "Imagem (PNG, JPEG, GIF, WebP, AVIF, BMP) abre no navegador; o resto sai como anexo, com o nome do arquivo, e `?download=1` no fim "
            "baixa sempre. HTML, SVG, XML e JavaScript saem como binário (`application/octet-stream`), com `X-Content-Type-Options: nosniff`. "
            "Cada link entra na Atividade da conta. Com a conta [suspensa pela equipe](/security#suspensão-pela-equipe), o link temporário "
            "sai só pelo painel, com 5 minutos, e a chave de API recebe `409 account_suspended_manually`."
        ),
        "tags": ["Blob"],
        "parameters": [BLOB_ID_PARAM],
        "requestBody": {
            "required": False,
            "content": {"application/json": {
                "schema": {"type": "object", "properties": {"expiresInSeconds": {"type": "integer", "minimum": 60, "maximum": 3600, "default": 300, "description": "Quanto o link vale, em segundos."}}},
                "example": {"expiresInSeconds": 600},
            }},
        },
        "x-codeSamples": samples(
            f"URL=$(curl -s -X POST {BASE}/blob/objects/$BLOB_ID/download-url \\\n  {KEY_H} | jq -r .url)\n"
            "curl -o logo.png \"$URL\"",
            "const res = await fetch(`${API}/blob/objects/${process.env.BLOB_ID}/download-url`, { method: 'POST', headers });\n"
            "const { url } = await res.json();\n"
            "const file = await fetch(url);\n"
            "await writeFile('logo.png', Buffer.from(await file.arrayBuffer()));",
            f"link = requests.post(f\"{{API}}/blob/objects/{BLOB_ID}/download-url\", headers=headers, timeout=30).json()\n"
            "r = requests.get(link[\"url\"], timeout=300)\n"
            "r.raise_for_status()\n"
            "with open(\"logo.png\", \"wb\") as f:\n"
            "    f.write(r.content)",
            node_imports="import { writeFile } from 'node:fs/promises';",
        ),
        "responses": {
            "200": {
                "description": "O link e até quando ele vale.",
                "content": {"application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["url", "expiresAt"],
                        "properties": {
                            "url": {"type": "string", "format": "uri", "description": "O link completo (`https://cdn.cubehost.dev/s/…/<nome>`): abra ou baixe com um `GET`, sem a chave de API."},
                            "expiresAt": {"type": "string", "format": "date-time"},
                        },
                    },
                    "example": {
                        "url": "https://cdn.cubehost.dev/s/q7Rf2kLm9xA1.tm3a9k.9ig4z3Rd7w4dd7wb/logo.png",
                        "expiresAt": "2026-09-28T13:15:02.000Z",
                    },
                }},
            },
            "400": resp("`expiresInSeconds` fora de 60 a 3600.", [("invalid_request", err("invalid_request", "expiresInSeconds vai de 60 a 3600 segundos."))]),
            "401": R401,
            "404": R404_BLOB,
            "409": resp(
                "A conta foi suspensa pela equipe da Cube: enquanto a suspensão durar, o link temporário sai só pelo painel.",
                [("account_suspended_manually", err("account_suspended_manually", "Esta conta foi suspensa pela equipe da Cube: Página de phishing no Blob. Enquanto a suspensão durar, o link temporário do Blob sai só pelo painel e vale 5 minutos. Fale com o suporte no Discord para resolver."))],
            ),
            "429": R429,
            "503": R503_BLOB,
        },
    },
}

# Envio em partes do Blob (cube-hosting#97): as URLs de cada parte e as que já chegaram.
PARTS_EXAMPLE = {
    "parts": [{"partNumber": 1, "sizeBytes": 16777216}, {"partNumber": 3, "sizeBytes": 8388608}],
    "partSizeBytes": 16777216,
    "partCount": 3,
    "expiresAt": "2026-10-01T13:10:02.000Z",
}
paths["/blob/objects/{id}/parts"] = {
    "get": {
        "operationId": "listBlobUploadParts",
        "summary": "Ver as partes que chegaram",
        "description": (
            "No envio em partes (`isMultipart: true` em [Pedir o envio](/api-reference/blob/create)), as partes que já chegaram ao armazenamento "
            "com o tamanho certo. Para continuar um envio que caiu (a conexão, ou o script que parou), mande só as que não estão aqui e confirme. "
            "O envio vale 24 horas desde o pedido (`expiresAt`)."
        ),
        "tags": ["Blob"],
        "parameters": [BLOB_ID_PARAM],
        "x-codeSamples": samples(
            f"curl {BASE}/blob/objects/$BLOB_ID/parts \\\n  {KEY_H}",
            "const res = await fetch(`${API}/blob/objects/${process.env.BLOB_ID}/parts`, { headers });\n"
            "const { parts, partCount } = await res.json();\n"
            "const done = new Set(parts.map((p) => p.partNumber));\n"
            "const missing = Array.from({ length: partCount }, (_, i) => i + 1).filter((n) => !done.has(n));\n"
            "console.log(missing);",
            f"r = requests.get(f\"{{API}}/blob/objects/{BLOB_ID}/parts\", headers=headers, timeout=30)\n"
            "r.raise_for_status()\n"
            "body = r.json()\n"
            "done = {p[\"partNumber\"] for p in body[\"parts\"]}\n"
            "print([n for n in range(1, body[\"partCount\"] + 1) if n not in done])",
        ),
        "responses": {
            "200": {
                "description": "As partes que chegaram.",
                "content": {"application/json": {"schema": ref("BlobParts"), "example": PARTS_EXAMPLE}},
            },
            "401": R401,
            "403": R403_WRITE,
            "404": R404_BLOB,
            "409": resp("O arquivo não está sendo enviado em partes, ou o envio passou das 24 horas.", [E_BLOB_NOT_MULTIPART, E_BLOB_EXPIRED]),
            "429": R429,
            "503": R503_BLOB,
        },
    },
    "post": {
        "operationId": "createBlobUploadPartUrls",
        "summary": "Pedir as URLs das partes",
        "description": (
            "As URLs para mandar cada parte direto ao armazenamento com `PUT` (sem a chave de API), de 1 a 100 por pedido. "
            "Cada URL vale 1 hora e só aceita o tamanho da parte (`sizeBytes`): todas têm `partSizeBytes`, menos a última, com o resto. "
            "Mandar a mesma parte de novo troca a anterior: é assim que a parte que caiu no meio vai outra vez. "
            "Com todas enviadas, chame [Confirmar o envio](/api-reference/blob/complete)."
        ),
        "tags": ["Blob"],
        "parameters": [BLOB_ID_PARAM],
        "requestBody": {
            "required": True,
            "content": {"application/json": {
                "schema": {"type": "object", "required": ["partNumbers"], "properties": {"partNumbers": {"type": "array", "minItems": 1, "maxItems": 100, "items": {"type": "integer", "minimum": 1}, "description": "Os números das partes, de 1 a `partCount`."}}},
                "example": {"partNumbers": [1, 2, 3]},
            }},
        },
        "x-codeSamples": samples(
            f"URLS=$(curl -s -X POST {BASE}/blob/objects/$BLOB_ID/parts \\\n  {KEY_H} \\\n  -H \"Content-Type: application/json\" \\\n"
            "  -d '{\"partNumbers\": [1]}')\n"
            "# A parte 1 são os primeiros 16 MB do arquivo, sem a chave de API.\n"
            "head -c 16777216 aula.mp4 | curl -X PUT \"$(echo \"$URLS\" | jq -r '.parts[0].url')\" --data-binary @-",
            "const PART = 16 * 1024 * 1024;\n"
            "const file = await readFile('aula.mp4');\n"
            "const res = await fetch(`${API}/blob/objects/${process.env.BLOB_ID}/parts`, {\n"
            "  method: 'POST',\n"
            "  headers: { ...headers, 'Content-Type': 'application/json' },\n"
            "  body: JSON.stringify({ partNumbers: [1, 2, 3] }),\n"
            "});\n"
            "const { parts } = await res.json();\n"
            "for (const p of parts) {\n"
            "  const start = (p.partNumber - 1) * PART;\n"
            "  await fetch(p.url, { method: 'PUT', body: file.subarray(start, start + p.sizeBytes) });\n"
            "}\n"
            "await fetch(`${API}/blob/objects/${process.env.BLOB_ID}/complete`, { method: 'POST', headers });",
            "PART = 16 * 1024 * 1024\n"
            f"r = requests.post(f\"{{API}}/blob/objects/{BLOB_ID}/parts\", headers=headers, json={{\"partNumbers\": [1, 2, 3]}}, timeout=30)\n"
            "r.raise_for_status()\n"
            "with open(\"aula.mp4\", \"rb\") as f:\n"
            "    for p in r.json()[\"parts\"]:\n"
            "        f.seek((p[\"partNumber\"] - 1) * PART)\n"
            "        requests.put(p[\"url\"], data=f.read(p[\"sizeBytes\"]), timeout=3600).raise_for_status()\n"
            f"requests.post(f\"{{API}}/blob/objects/{BLOB_ID}/complete\", headers=headers, timeout=30).raise_for_status()",
            node_imports="import { readFile } from 'node:fs/promises';",
        ),
        "responses": {
            "200": {
                "description": "As URLs das partes pedidas.",
                "content": {"application/json": {
                    "schema": ref("BlobPartUrls"),
                    "example": {
                        "parts": [{"partNumber": 1, "sizeBytes": 16777216, "url": "https://…/accounts/…/blob/01JA3F7K2M9P4R6T8V0X1Z3B5D?partNumber=1&uploadId=…&X-Amz-Expires=3600&X-Amz-SignedHeaders=content-length%3Bhost&X-Amz-Signature=…"}],
                        "expiresAt": "2026-09-30T14:10:02.000Z",
                    },
                }},
            },
            "400": resp("`partNumbers` fora do formato ou com uma parte que o envio não tem.", [("invalid_request", err("invalid_request", "Mande partNumbers: de 1 a 100 números de parte, cada um de 1 a 3."))]),
            "401": R401,
            "403": R403_WRITE,
            "404": R404_BLOB,
            "409": resp("O arquivo não está sendo enviado em partes, ou o envio passou das 24 horas.", [E_BLOB_NOT_MULTIPART, E_BLOB_EXPIRED]),
            "429": R429,
            "503": R503_BLOB,
        },
    },
}

# Regras de pasta do Blob (cube-hosting#97): ler com a chave de leitura; salvar a lista inteira com a
# de escrita (a Só Blob não mexe nelas: uma regra apaga arquivos).
paths["/blob/folder-rules"] = {
    "get": {
        "operationId": "listBlobFolderRules",
        "summary": "Ver as regras de pasta",
        "description": (
            "As regras de pasta do Blob da conta e quantas o plano tem (`limit`: 1 por GB da cota, até 50). Cada regra vale para a pasta e as subpastas "
            "dela; com duas na mesma pasta, vale a de caminho mais longo, inteira. Guia em [Blob](/hosting/blob#regras-de-pasta)."
        ),
        "tags": ["Blob"],
        "x-codeSamples": samples(
            f"curl {BASE}/blob/folder-rules \\\n  {KEY_H}",
            "const res = await fetch(`${API}/blob/folder-rules`, { headers });\n"
            "const { rules, limit } = await res.json();\n"
            "console.log(`${rules.length} de ${limit} regras`);",
            "r = requests.get(f\"{API}/blob/folder-rules\", headers=headers, timeout=30)\n"
            "r.raise_for_status()\n"
            "print(r.json()[\"rules\"])",
        ),
        "responses": {
            "200": {
                "description": "As regras e o limite do plano.",
                "content": {"application/json": {"schema": ref("BlobFolderRules"), "example": {"rules": [BLOB_RULE_EXAMPLE], "limit": 5}}},
            },
            "401": R401,
            "403": resp("A chave é Só Blob (ela não lê nem mexe nas regras).", [E_PERM]),
            "429": R429,
        },
    },
    "put": {
        "operationId": "saveBlobFolderRules",
        "summary": "Salvar as regras de pasta",
        "description": (
            "Troca a lista inteira de regras da conta (lista vazia apaga todas). Visibilidade, expiração, cache, tamanho e extensões valem nos **envios** "
            "para a pasta; a expiração e o cache ficam gravados em cada arquivo. **Apagar com mais de N dias** (`deleteAfterDays`) vale também para os "
            "arquivos que já estão na pasta e só começa **24 horas depois de salvar** (`deletionStartsAt`): salvar de novo com o mesmo N mantém a data, e "
            "trocar o N recomeça as 24 horas. Arquivo apagado não volta. A pasta vem sem `/` nas pontas e as extensões em minúsculas, sem o ponto."
        ),
        "tags": ["Blob"],
        "requestBody": {
            "required": True,
            "content": {"application/json": {
                "schema": {"type": "object", "required": ["rules"], "properties": {"rules": {"type": "array", "maxItems": 50, "items": ref("BlobFolderRuleInput")}}},
                "example": {"rules": [{"folder": "backups/diarios", "allowedExtensions": ["zip"], "deleteAfterDays": 7}]},
            }},
        },
        "x-codeSamples": samples(
            f"curl -X PUT {BASE}/blob/folder-rules \\\n  {KEY_H} \\\n  -H \"Content-Type: application/json\" \\\n"
            "  -d '{\"rules\": [{\"folder\": \"backups/diarios\", \"allowedExtensions\": [\"zip\"], \"deleteAfterDays\": 7}]}'",
            "const res = await fetch(`${API}/blob/folder-rules`, {\n"
            "  method: 'PUT',\n"
            "  headers: { ...headers, 'Content-Type': 'application/json' },\n"
            "  body: JSON.stringify({ rules: [{ folder: 'backups/diarios', allowedExtensions: ['zip'], deleteAfterDays: 7 }] }),\n"
            "});\n"
            "const { rules } = await res.json();\n"
            "console.log(rules[0].deletionStartsAt);",
            "r = requests.put(\n"
            "    f\"{API}/blob/folder-rules\",\n"
            "    headers=headers,\n"
            "    json={\"rules\": [{\"folder\": \"backups/diarios\", \"allowedExtensions\": [\"zip\"], \"deleteAfterDays\": 7}]},\n"
            "    timeout=30,\n"
            ")\n"
            "r.raise_for_status()\n"
            "print(r.json()[\"rules\"])",
        ),
        "responses": {
            "200": {
                "description": "As regras salvas e o limite do plano.",
                "content": {"application/json": {"schema": ref("BlobFolderRules"), "example": {"rules": [BLOB_RULE_EXAMPLE], "limit": 5}}},
            },
            "400": resp("O corpo saiu do formato, ou uma regra tem a pasta ou uma extensão torta, ou há duas para a mesma pasta. Nada mudou.", [
                ("invalid_request", err("invalid_request", "Mande rules: a lista de regras, cada uma com folder e, se quiser, defaultVisibility, defaultExpirationDays, cacheMaxAgeSeconds, maxFileSizeBytes, allowedExtensions e deleteAfterDays.")),
                ("invalid_folder_rule", err("invalid_folder_rule", "Duas regras para a pasta backups/diarios. Junte as duas numa só e salve de novo.")),
            ]),
            "401": R401,
            "403": resp("A chave é só de leitura ou Só Blob, ou o plano não tem Blob (Free).", [E_PERM, ("blob_not_in_plan", err("blob_not_in_plan", "O Blob é dos planos pagos. Assine um plano em Plano e cobrança para enviar arquivos."))]),
            "409": resp("Mais regras que o plano tem. Nada mudou.", [("folder_rule_limit_reached", err("folder_rule_limit_reached", "O plano Block tem até 5 regras de pasta. Junte ou remova 1 e salve de novo, ou mude para um plano maior.", limit=5))]),
            "429": R429,
        },
    },
}

# Domínio próprio (cube-hosting#13, #47): listar com a chave de leitura; adicionar, redirecionar,
# verificar e remover com a de escrita.
DOMAIN_ID_PARAM = {"$ref": "#/components/parameters/DomainId"}
DOMAIN_EXAMPLE = {
    "id": "01JA9K3M5P7R9T1V3X5Z7B9D1F",
    "projectId": SITE_EXAMPLE["id"],
    "hostname": "loja.com.br",
    "redirectTo": None,
    "status": "active",
    "error": None,
    "records": [
        {"type": "CNAME", "name": "loja.com.br", "value": "domains.cubehost.dev", "isOk": True},
        {"type": "TXT", "name": "_cube-verify.loja.com.br", "value": "cube-verify=4a4163549b3f77ae5fbfff6fa7480999", "isOk": True},
    ],
    "verifiedAt": "2026-09-28T15:11:01.597Z",
    "checkedAt": "2026-09-28T15:21:02.114Z",
    "createdAt": "2026-09-28T15:09:40.000Z",
    "project": {"id": SITE_EXAMPLE["id"], "name": "Loja"},
}
WWW_EXAMPLE = {
    **DOMAIN_EXAMPLE,
    "id": "01JA9K3M5P7R9T1V3X5Z7B9D1G",
    "hostname": "www.loja.com.br",
    "redirectTo": "loja.com.br",
    "status": "pending",
    "records": [
        {"type": "CNAME", "name": "www.loja.com.br", "value": "domains.cubehost.dev", "isOk": False},
        {"type": "TXT", "name": "_cube-verify.loja.com.br", "value": "cube-verify=4a4163549b3f77ae5fbfff6fa7480999", "isOk": True},
    ],
}
DOMAIN_LIST_EXAMPLE = {"domains": [DOMAIN_EXAMPLE, WWW_EXAMPLE], "used": 1, "limit": 1, "target": "domains.cubehost.dev", "isAvailable": True}
DOMAIN_ACCOUNT_LIST_EXAMPLE = {**DOMAIN_LIST_EXAMPLE, "limit": 4}
E_DOMAIN_404 = ("not_found", err("not_found", "Domínio não encontrado."))
R404_DOMAIN = resp("O projeto ou o domínio não existe ou não é da sua conta.", [E_404, E_DOMAIN_404])
E_DOMAIN_OFF = ("custom_domains_unavailable", err("custom_domains_unavailable", "O domínio próprio está fora do ar agora. Tente de novo mais tarde."))
E_DOMAIN_PLAN = ("custom_domain_not_allowed", err("custom_domain_not_allowed", "O plano Free não tem sites, então não tem domínio próprio. Ele vem em todo plano pago, 1 por site."))
E_DOMAIN_TAKEN = ("domain_taken", err("domain_taken", "Este domínio já é de outra conta. Se ele é seu, fale com o suporte."))
E_REDIRECT = ("invalid_redirect", err("invalid_redirect", "O redirecionamento precisa ir para outro domínio deste site que abre o site direto (sem redirecionar de novo)."))
DOMAIN_ONE = lambda desc, example: {
    "description": desc,
    "content": {"application/json": {
        "schema": {"type": "object", "required": ["domain"], "properties": {"domain": ref("Domain")}},
        "example": {"domain": example},
    }},
}

paths["/templates"] = {
    "get": {
        "operationId": "listTemplates",
        "summary": "Listar templates",
        "description": "Os [templates](/hosting/templates) da Cube, com o que cada um pede. Público: não precisa de chave.",
        "tags": ["Templates"],
        "security": [],
        "x-codeSamples": samples(
            f"curl {BASE}/templates",
            "const res = await fetch(`${API}/templates`);\n"
            "const { templates } = await res.json();\n"
            "for (const t of templates) console.log(t.id, t.memoryMb, t.variables.map((v) => v.name));",
            'r = requests.get(f"{API}/templates", timeout=30)\n'
            "r.raise_for_status()\n"
            'for t in r.json()["templates"]:\n'
            '    print(t["id"], t["memoryMb"], [v["name"] for v in t["variables"]])',
        ),
        "responses": {
            "200": {
                "description": "A lista de templates.",
                "content": {"application/json": {
                    "schema": {"type": "object", "required": ["templates"], "properties": {"templates": {"type": "array", "items": ref("Template")}}},
                    "example": {"templates": TEMPLATE_EXAMPLES},
                }},
            },
            "500": resp("Erro do nosso lado. Tente de novo em instantes.", [
                ("internal_error", err("internal_error", "Erro inesperado. Tente de novo em instantes.")),
            ]),
        },
    },
}

# GET /plans: o catálogo público, com quanto cabe em cada plano (decisão do dono, 28/09/2026), os
# 17 tamanhos do Empresas e o isAvailable (cube-hosting#76).
ENTERPRISE_SIZES = [32, 48, 64, 96, 128, 160, 192, 224, 256, 288, 320, 384, 448, 512, 640, 768, 1024]
PLAN_EXAMPLES = [
    {"id": "free", "name": "Free", "memoryMb": 100, "vcpu": 0.25, "blobGb": 0, "databases": 0, "hasCustomDomain": False, "priceCents": 0, "annualPriceCents": 0, "isForSale": True, "isAvailable": True, "apiRateLimit": {"perMinute": 10, "perDay": 5000}, "backupLimit": 1, "hasDailyBackup": False, "deploymentVersionLimit": 2, "customDomainLimit": 0, "teamMemberLimit": 0, "minMemoryMb": {"bot": 100, "site": 512}, "maxBots": 1, "maxSites": 0},
    {"id": "block", "name": "Block", "memoryMb": 1024, "vcpu": 1, "blobGb": 5, "databases": 0, "hasCustomDomain": True, "priceCents": 599, "annualPriceCents": 5750, "isForSale": True, "isAvailable": True, "apiRateLimit": {"perMinute": 30, "perDay": 43200}, "backupLimit": 3, "hasDailyBackup": True, "deploymentVersionLimit": 3, "customDomainLimit": 1, "teamMemberLimit": 0, "minMemoryMb": {"bot": 256, "site": 512}, "maxBots": 4, "maxSites": 2},
    {"id": "tower", "name": "Tower", "memoryMb": 4096, "vcpu": 3, "blobGb": 25, "databases": 3, "hasCustomDomain": True, "priceCents": 2399, "annualPriceCents": 23030, "isForSale": True, "isAvailable": True, "apiRateLimit": {"perMinute": 120, "perDay": 172800}, "backupLimit": 7, "hasDailyBackup": True, "deploymentVersionLimit": 7, "customDomainLimit": 1, "teamMemberLimit": 3, "minMemoryMb": {"bot": 256, "site": 512}, "maxBots": 16, "maxSites": 8},
    {"id": "monolith", "name": "Monolith", "memoryMb": 16384, "vcpu": 6, "blobGb": 100, "databases": 12, "hasCustomDomain": True, "priceCents": 9499, "annualPriceCents": 91190, "isForSale": True, "isAvailable": True, "apiRateLimit": {"perMinute": 240, "perDay": 345600}, "backupLimit": 14, "hasDailyBackup": True, "deploymentVersionLimit": 14, "customDomainLimit": 1, "teamMemberLimit": 15, "minMemoryMb": {"bot": 256, "site": 512}, "maxBots": 64, "maxSites": 32},
    {"id": "enterprise-32", "name": "Empresas 32", "memoryMb": 32768, "vcpu": 8, "blobGb": 200, "databases": 64, "hasCustomDomain": True, "priceCents": 18990, "annualPriceCents": 182304, "isForSale": True, "isAvailable": True, "apiRateLimit": {"perMinute": 300, "perDay": 432000}, "backupLimit": 14, "hasDailyBackup": True, "deploymentVersionLimit": 14, "customDomainLimit": 1, "teamMemberLimit": 20, "minMemoryMb": {"bot": 256, "site": 512}, "maxBots": 128, "maxSites": 64},
]

paths["/plans"] = {
    "get": {
        "operationId": "listPlans",
        "summary": "Listar planos",
        "description": (
            "Os planos da Cube, do Free ao Empresas: memória, processador, preço mensal e anual e os limites de cada um. "
            "O **Empresas** vem em 17 tamanhos (`enterprise-32` a `enterprise-1024`, a memória em GB), depois do Monolith; não há "
            "plano sob medida. `isAvailable` diz se o plano pode ser contratado agora: o Monolith e o Empresas estão sempre à venda, e "
            "`false` = os nossos servidores estão cheios de verdade agora (\"Indisponível no momento\"), e o checkout recusa sem gerar Pix; libera sozinho. "
            "`minMemoryMb` é a memória mínima de cada tipo no plano (bot 256 MB nos pagos e 100 MB no Free; site 512 MB), e "
            "`maxBots` e `maxSites` dizem quantos cabem, cada um com esse mínimo. Público: não precisa de chave. Guia em [Planos e memória](/account/plans)."
        ),
        "tags": ["Conta"],
        "security": [],
        "x-codeSamples": samples(
            f"curl {BASE}/plans",
            "const res = await fetch(`${API}/plans`);\n"
            "const plans = await res.json();\n"
            "for (const p of plans) console.log(p.name, p.maxBots, p.maxSites, p.minMemoryMb.bot);",
            'r = requests.get(f"{API}/plans", timeout=30)\n'
            "r.raise_for_status()\n"
            "for p in r.json():\n"
            '    print(p["name"], p["maxBots"], p["maxSites"], p["minMemoryMb"]["bot"])',
        ),
        "responses": {
            "200": {
                "description": "A lista de planos, do menor para o maior.",
                "content": {"application/json": {
                    "schema": {"type": "array", "items": ref("Plan")},
                    "example": PLAN_EXAMPLES,
                }},
            },
            "500": resp("Erro do nosso lado. Tente de novo em instantes.", [
                ("internal_error", err("internal_error", "Erro inesperado. Tente de novo em instantes.")),
            ]),
        },
    },
}

paths["/domains"] = {
    "get": {
        "operationId": "listDomains",
        "summary": "Listar domínios da conta",
        "description": (
            "Os domínios próprios de todos os sites da conta, cada um com o site (`project`), o status e os registros DNS para criar. "
            "Cada site tem 1 domínio (o `www` do mesmo nome vai junto e não conta): `used` = quantos sites têm domínio, "
            "`limit` = 1 por site que o plano comporta (0 no Free, que não tem site). Guia em [Endereço e domínios](/hosting/domains)."
        ),
        "tags": ["Domínios"],
        "x-codeSamples": samples(
            f"curl {BASE}/domains \\\n  {KEY_H}",
            "const res = await fetch(`${API}/domains`, { headers });\n"
            "const { domains } = await res.json();\n"
            "for (const d of domains) console.log(d.hostname, d.status, d.project.name);",
            'r = requests.get(f"{API}/domains", headers=headers, timeout=30)\n'
            "r.raise_for_status()\n"
            'for d in r.json()["domains"]:\n'
            '    print(d["hostname"], d["status"], d["project"]["name"])',
        ),
        "responses": {
            "200": {
                "description": "Os domínios da conta.",
                "content": {"application/json": {"schema": ref("DomainList"), "example": DOMAIN_ACCOUNT_LIST_EXAMPLE}},
            },
            "401": R401,
            "429": R429,
        },
    },
}

paths["/projects/{id}/domains"] = {
    "get": {
        "operationId": "listProjectDomains",
        "summary": "Listar domínios do site",
        "description": (
            "Os domínios próprios do site, com o status (`pending` verificando, `active`, `error`) e, em `records`, os dois registros para criar "
            "no DNS do domínio: o **CNAME** para `domains.cubehost.dev` e o **TXT** que prova a posse. A Cube confere sozinha a cada minuto. "
            "O site tem 1 domínio, com o `www` junto: `used` é 0 ou 1 e `limit` é 1 (0 num bot ou no Free)."
        ),
        "tags": ["Domínios"],
        "parameters": [ID_PARAM],
        "x-codeSamples": samples(
            f"curl {BASE}/projects/$PROJECT_ID/domains \\\n  {KEY_H}",
            "const res = await fetch(`${API}/projects/${process.env.PROJECT_ID}/domains`, { headers });\n"
            "const { domains } = await res.json();\n"
            "for (const d of domains) for (const r of d.records) console.log(d.hostname, r.type, r.name, r.value, r.isOk);",
            f"r = requests.get(f\"{{API}}/projects/{{os.environ['PROJECT_ID']}}/domains\", headers=headers, timeout=30)\n"
            "r.raise_for_status()\n"
            'for d in r.json()["domains"]:\n'
            '    for rec in d["records"]:\n'
            '        print(d["hostname"], rec["type"], rec["name"], rec["value"], rec["isOk"])',
        ),
        "responses": {
            "200": {
                "description": "Os domínios do site.",
                "content": {"application/json": {"schema": ref("DomainList"), "example": DOMAIN_LIST_EXAMPLE}},
            },
            "401": R401,
            "404": R404,
            "429": R429,
        },
    },
    "post": {
        "operationId": "createDomain",
        "summary": "Adicionar domínio",
        "description": (
            "Adiciona o domínio do site, em todo plano pago: 1 por site, com o `www` do mesmo nome junto (ele não conta como outro). "
            "Outro nome num site que já tem o dele dá `plan_limit_reached`. Responde com o domínio `pending` e os registros para criar no DNS dele. "
            "Com `redirectTo` (outro domínio do mesmo site que abre o site direto), quem abrir este vai para o outro: é o jeito de pôr o `www` "
            "levando à raiz, ou o contrário. O `www` e a raiz usam o mesmo TXT. Só o domínio verificado abre o site, e um domínio verificado é de uma conta só."
        ),
        "tags": ["Domínios"],
        "parameters": [ID_PARAM],
        "requestBody": {
            "required": True,
            "content": {"application/json": {
                "schema": ref("DomainInput"),
                "examples": {
                    "raiz": {"summary": "A raiz", "value": {"hostname": "loja.com.br"}},
                    "www": {"summary": "O www levando à raiz", "value": {"hostname": "www.loja.com.br", "redirectTo": "loja.com.br"}},
                },
            }},
        },
        "x-codeSamples": samples(
            f"curl -X POST {BASE}/projects/$PROJECT_ID/domains \\\n  {KEY_H} \\\n  -H \"Content-Type: application/json\" \\\n"
            "  -d '{\"hostname\": \"loja.com.br\"}'",
            "const res = await fetch(`${API}/projects/${process.env.PROJECT_ID}/domains`, {\n"
            "  method: 'POST',\n"
            "  headers: { ...headers, 'Content-Type': 'application/json' },\n"
            "  body: JSON.stringify({ hostname: 'loja.com.br' }),\n"
            "});\n"
            "const { domain } = await res.json();\n"
            "for (const r of domain.records) console.log(r.type, r.name, r.value);",
            f"r = requests.post(\n    f\"{{API}}/projects/{{os.environ['PROJECT_ID']}}/domains\",\n"
            "    headers=headers,\n"
            "    json={\"hostname\": \"loja.com.br\"},\n"
            "    timeout=30,\n)\n"
            "r.raise_for_status()\n"
            'for rec in r.json()["domain"]["records"]:\n'
            '    print(rec["type"], rec["name"], rec["value"])',
        ),
        "responses": {
            "201": DOMAIN_ONE("O domínio, verificando.", {**DOMAIN_EXAMPLE, "status": "pending", "verifiedAt": None, "records": [{**r, "isOk": False} for r in DOMAIN_EXAMPLE["records"]]}),
            "400": resp("Domínio fora do formato: só o nome, sem `https://`, barra, porta nem curinga.", [("invalid_domain", err("invalid_domain", "Digite só o domínio, como loja.com.br ou www.loja.com.br, sem https:// nem barra."))]),
            "401": R401,
            "403": resp("A chave é só de leitura, ou o plano não tem site (Free).", [E_PERM, E_DOMAIN_PLAN]),
            "404": R404,
            "409": resp("O domínio já está em outro site da conta ou outra conta já provou a posse.", [E_DOMAIN_TAKEN]),
            "422": resp("Bot, endereço da Cube, o site já tem o domínio dele ou redirecionamento inválido.", [
                ("not_a_site", err("not_a_site", "Só sites e APIs recebem domínio próprio. Bots não recebem visitas pela internet.")),
                ("reserved_domain", err("reserved_domain", "Endereços em cubehost.dev e do painel não podem ser domínio próprio. Para mudar o endereço em cubehost.dev, troque o subdomínio padrão.")),
                ("plan_limit_reached", err("plan_limit_reached", "Cada site tem 1 domínio próprio (o www vai junto). Remova o atual para usar outro.", limit=1)),
                E_REDIRECT,
            ]),
            "429": R429,
            "503": resp("O domínio próprio está fora do ar agora.", [E_DOMAIN_OFF]),
        },
    },
}

paths["/projects/{id}/domains/{domainId}"] = {
    "patch": {
        "operationId": "updateDomain",
        "summary": "Trocar para onde o domínio vai",
        "description": (
            "`redirectTo` com outro domínio do site faz este redirecionar para ele (`308`, com o caminho); `null` faz este abrir o site direto. "
            "Para inverter o `www` (a raiz passa a levar ao `www`), mande `redirectTo: \"www.loja.com.br\"` na raiz: o `www`, que redirecionava para ela, "
            "passa a abrir o site no mesmo pedido, e quem apontava para a raiz passa a apontar para o `www` (nunca uma cadeia)."
        ),
        "tags": ["Domínios"],
        "parameters": [ID_PARAM, DOMAIN_ID_PARAM],
        "requestBody": {
            "required": True,
            "content": {"application/json": {"schema": ref("DomainUpdateInput"), "example": {"redirectTo": "www.loja.com.br"}}},
        },
        "x-codeSamples": samples(
            f"curl -X PATCH {BASE}/projects/$PROJECT_ID/domains/$DOMAIN_ID \\\n  {KEY_H} \\\n  -H \"Content-Type: application/json\" \\\n"
            "  -d '{\"redirectTo\": \"www.loja.com.br\"}'",
            "const url = `${API}/projects/${process.env.PROJECT_ID}/domains/${process.env.DOMAIN_ID}`;\n"
            "const res = await fetch(url, {\n"
            "  method: 'PATCH',\n"
            "  headers: { ...headers, 'Content-Type': 'application/json' },\n"
            "  body: JSON.stringify({ redirectTo: 'www.loja.com.br' }),\n"
            "});\n"
            "console.log((await res.json()).domain.redirectTo);",
            "url = f\"{API}/projects/{os.environ['PROJECT_ID']}/domains/{os.environ['DOMAIN_ID']}\"\n"
            "r = requests.patch(url, headers=headers, json={\"redirectTo\": \"www.loja.com.br\"}, timeout=30)\n"
            "r.raise_for_status()\n"
            'print(r.json()["domain"]["redirectTo"])',
        ),
        "responses": {
            "200": DOMAIN_ONE("O domínio, com o redirecionamento novo.", {**DOMAIN_EXAMPLE, "redirectTo": "www.loja.com.br"}),
            "401": R401,
            "403": R403_WRITE,
            "404": R404_DOMAIN,
            "422": resp("O alvo não é outro domínio do site que abre o site direto.", [E_REDIRECT]),
            "429": R429,
        },
    },
    "delete": {
        "operationId": "deleteDomain",
        "summary": "Remover domínio",
        "description": (
            "O domínio para de abrir o site na hora. Quem redirecionava para ele passa a abrir o site direto. "
            "Os registros continuam no DNS do domínio: apague lá se não for usar."
        ),
        "tags": ["Domínios"],
        "parameters": [ID_PARAM, DOMAIN_ID_PARAM],
        "x-codeSamples": samples(
            f"curl -X DELETE {BASE}/projects/$PROJECT_ID/domains/$DOMAIN_ID \\\n  {KEY_H}",
            "const url = `${API}/projects/${process.env.PROJECT_ID}/domains/${process.env.DOMAIN_ID}`;\n"
            "const res = await fetch(url, { method: 'DELETE', headers });\n"
            "console.log(res.status); // 204",
            "url = f\"{API}/projects/{os.environ['PROJECT_ID']}/domains/{os.environ['DOMAIN_ID']}\"\n"
            "r = requests.delete(url, headers=headers, timeout=30)\n"
            "r.raise_for_status()",
        ),
        "responses": {
            "204": {"description": "Removido."},
            "401": R401,
            "403": R403_WRITE,
            "404": R404_DOMAIN,
            "429": R429,
        },
    },
}

paths["/projects/{id}/domains/{domainId}/verify"] = {
    "post": {
        "operationId": "verifyDomain",
        "summary": "Verificar domínio agora",
        "description": (
            "Confere os registros na hora (a Cube já confere sozinha a cada minuto). Achou o TXT com o valor certo, o domínio fica verificado e passa a abrir o site; "
            "com o CNAME também chegando à Cube, fica `active`. Sem o TXT em 7 dias, a conferência sozinha para (`verification_expired`), e este pedido volta a procurar. Com `certificate_failed`, ele pede o certificado HTTPS de novo, do zero, e o domínio volta a `pending`. "
            "Um pedido a cada 3 segundos por conta."
        ),
        "tags": ["Domínios"],
        "parameters": [ID_PARAM, DOMAIN_ID_PARAM],
        "x-codeSamples": samples(
            f"curl -X POST {BASE}/projects/$PROJECT_ID/domains/$DOMAIN_ID/verify \\\n  {KEY_H}",
            "const url = `${API}/projects/${process.env.PROJECT_ID}/domains/${process.env.DOMAIN_ID}/verify`;\n"
            "const res = await fetch(url, { method: 'POST', headers });\n"
            "const { domain } = await res.json();\n"
            "console.log(domain.status, domain.records.map((r) => `${r.type}: ${r.isOk}`));",
            "url = f\"{API}/projects/{os.environ['PROJECT_ID']}/domains/{os.environ['DOMAIN_ID']}/verify\"\n"
            "r = requests.post(url, headers=headers, timeout=30)\n"
            "r.raise_for_status()\n"
            'print(r.json()["domain"]["status"])',
        ),
        "responses": {
            "200": DOMAIN_ONE("O domínio, conferido agora.", DOMAIN_EXAMPLE),
            "401": R401,
            "403": R403_WRITE,
            "404": R404_DOMAIN,
            "429": resp("Conferências seguidas demais. Traz o cabeçalho `Retry-After`.", [E_RATE, E_MANY]),
        },
    },
}

components = {
    "securitySchemes": {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "description": "Chave de API da Cube (`cube_…`), criada no painel em **Chaves de API**. Mande como `Authorization: Bearer cube_…`.",
        }
    },
    "parameters": {
        "ProjectId": {
            "name": "id",
            "in": "path",
            "required": True,
            "description": "O ID do projeto (26 caracteres). Aparece no painel, no topo do projeto, e em `GET /projects`.",
            "schema": {"type": "string", "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$", "example": "01J8Z3W6N0Q4Y7V2K5T9D1H3XA"},
        },
        "DeploymentId": {
            "name": "deploymentId",
            "in": "path",
            "required": True,
            "description": "O ID da versão (UUID), do [Histórico de envios](/api-reference/deployments/list).",
            "schema": {"type": "string", "format": "uuid", "example": "3f2b8c1e-6a4d-4e7b-9c2a-1d5e8f0a7b36"},
        },
        "DatabaseId": {
            "name": "id",
            "in": "path",
            "required": True,
            "description": "O ID do banco de dados (26 caracteres), de [Listar bancos de dados](/api-reference/databases/list).",
            "schema": {"type": "string", "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$", "example": "01J9A2C4E6G8J0K2M4P6R8T0V2"},
        },
        "DomainId": {
            "name": "domainId",
            "in": "path",
            "required": True,
            "description": "O ID do domínio (26 caracteres), de [Listar domínios do site](/api-reference/domains/list).",
            "schema": {"type": "string", "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$", "example": "01JA9K3M5P7R9T1V3X5Z7B9D1F"},
        },
        "BlobObjectId": {
            "name": "id",
            "in": "path",
            "required": True,
            "description": "O ID do arquivo do Blob (26 caracteres), de [Listar arquivos do Blob](/api-reference/blob/list).",
            "schema": {"type": "string", "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$", "example": "01JA3F7K2M9P4R6T8V0X1Z3B5D"},
        },
        "BackupId": {
            "name": "backupId",
            "in": "path",
            "required": True,
            "description": "O ID do backup (UUID), de [Listar backups](/api-reference/backups/list).",
            "schema": {"type": "string", "format": "uuid", "example": "5b0c7a4e-2f1d-4c8e-9a36-7d2b1e0f4c11"},
        },
    },
    "schemas": {
        "Project": {
            "type": "object",
            "description": "Um projeto: um bot ou um site.",
            "required": ["id", "name", "description", "type", "language", "version", "entry", "command", "root", "systemPackages", "memoryMb", "port", "subdomain", "url", "internalHost", "status", "error", "hasAutoRestart", "consecutiveCrashes", "lastExit", "usage", "startedAt", "templateId", "restoredFromBackupId", "createdAt", "updatedAt"],
            "properties": {
                "id": {"type": "string", "description": "ID do projeto, 26 caracteres."},
                "name": {"type": "string", "maxLength": 40, "description": "Nome do projeto."},
                "description": {"type": "string", "maxLength": 200, "description": "Descrição do painel. `\"\"` quando não tem."},
                "type": {"type": "string", "enum": ["bot", "site"]},
                "language": {"type": "string", "enum": ["node", "python", "java", "go", "php", "ruby", "dotnet", "elixir", "static"], "description": "`java` roda um `.jar` pronto ([Hospedar Java](/hosting/java)), `go` é compilado a cada envio ([Hospedar Go](/hosting/go)), `php` e `ruby` instalam o `composer.json` e o `Gemfile` ([Hospedar PHP](/hosting/php), [Hospedar Ruby](/hosting/ruby)), `dotnet` publica o projeto a cada envio ([Hospedar .NET](/hosting/dotnet)), `elixir` compila o projeto do `mix.exs` a cada envio ([Hospedar Elixir](/hosting/elixir)) e `static` é o [site só de HTML](/hosting/static-site), servido pela Cube."},
                "version": {"type": "string", "description": "`20`, `22`, `24` ou `26` (Node.js); `3.11`, `3.12`, `3.13` ou `3.14` (Python); `21` ou `25` (Java); `1.26` ou `1.27` (Go); `8.4` ou `8.5` (PHP); `3.4` ou `4.0` (Ruby); `10` (.NET); `1.20` (Elixir); `\"\"` no `static`."},
                "entry": nullable("string", description="Arquivo principal: o arquivo que o comando roda, relativo à raiz do projeto (como `index.js`, `src/index.ts`, `src/bot.py`, `bot.jar`, `bot.php`, `bot.rb`, `Bot.csproj`, `app.dll` ou `mix.exs`). Vem do `command` quando ele é só `node <arquivo>`, `tsx <arquivo>` (TypeScript direto), `python <arquivo>`, `java -jar <arquivo>`, `php <arquivo>`, `ruby <arquivo>`, `dotnet <arquivo>.dll` ou `mix run --no-halt <arquivo>`, e muda em Configurações › Geral. No `go`, é o main cuja pasta o build compila (`null` = a raiz); no `dotnet`, o projeto que o build publica ou o `.dll` pronto. `null` com um comando próprio, como `npm start`."),
                "command": {"type": "string", "description": "Comando de início, o que de fato roda. Quando é `node <entry>`, `tsx <entry>`, `python <entry>` ou `java -jar <entry>` (ou, no `go`, `/dados/bin/app`, o programa do build; no site `php`, `cube-php-server`, o servidor da Cube; no `dotnet`, `dotnet /dados/publish/<projeto do entry>.dll` ou, no `.dll` pronto, `dotnet <entry>`; no `elixir`, `mix run --no-halt`), o painel mostra o campo vazio (vazio = roda o arquivo principal). `\"\"` no `static`."},
                "root": nullable("string", description="Só `static`: a pasta servida, relativa à raiz do projeto (`\"\"` = a raiz). `null` nas outras linguagens."),
                "systemPackages": {"type": "array", "items": {"type": "string", "enum": SYSTEM_PACKAGES}, "description": "Os [pacotes do sistema](/cube-json#pacotes-do-sistema) do projeto, na ordem da lista. `[]` sem nenhum (e sempre no `static`). Mudam em Configurações › Geral e valem no próximo início."},
                "memoryMb": {"type": "integer", "description": "Memória reservada, em MB. É também o teto do processo."},
                "port": nullable("integer", description="Só site: a porta em que o app escuta (também na variável `PORT`). `null` em bot."),
                "subdomain": nullable("string", description="Só site: o nome em `nome.cubehost.dev`. `null` em bot."),
                "url": nullable("string", format="uri", description="Só site: o endereço público com HTTPS. `null` em bot."),
                "internalHost": {"type": "string", "pattern": "^cube-[0-9a-z]{8}$", "description": "O **nome interno**: `cube-` e os 8 últimos caracteres do `id`, em minúsculas, fixo. Os outros projetos **da sua conta** chegam neste por ele, em qualquer porta em que ele escute, com ele no ar (como `http://cube-t9d1h3xa:2333` para o [Lavalink](/hosting/lavalink)). Outra conta não resolve o nome nem chega no projeto; não é um endereço público."},
                "status": ref("ProjectStatus"),
                "error": {"oneOf": [ref("ProjectError"), {"type": "null"}], "description": "O motivo, quando `status` é `error` ou `crash_loop`."},
                "hasAutoRestart": {"type": "boolean", "description": "`true` nos planos pagos: o projeto volta sozinho se cair."},
                "consecutiveCrashes": {"type": "integer", "description": "Quedas seguidas desde a última vez que rodou 60 segundos sem cair. Com 5, o projeto vai para `crash_loop`."},
                "lastExit": {"oneOf": [ref("LastExit"), {"type": "null"}], "description": "A última vez que o processo terminou."},
                "usage": {"oneOf": [ref("Usage"), {"type": "null"}], "description": "O uso de agora. Só com `status` `running`."},
                "startedAt": nullable("string", format="date-time", description="Quando o processo subiu (o \"tempo no ar\" do painel). Só com `running`."),
                "templateId": nullable("string", description="O [template](/hosting/templates) de onde o projeto nasceu, como `discord-js-bot`. `null` num `.zip` ou pelo GitHub, e volta a `null` quando o código é trocado por outro `.zip` ou pelo GitHub. Enquanto está preenchido, o projeto só inicia com as variáveis obrigatórias do template (`missing_variables`)."),
                "restoredFromBackupId": nullable("string", format="uuid", description="O backup de onde o projeto nasceu pelo [Restaurar como novo](/api-reference/backups/restore-as-new). `null` nos outros."),
                "createdAt": {"type": "string", "format": "date-time"},
                "updatedAt": {"type": "string", "format": "date-time"},
            },
        },
        "Plan": {
            "type": "object",
            "description": "Um plano da Cube: do Free ao Monolith e os 17 tamanhos do Empresas.",
            "required": ["id", "name", "memoryMb", "vcpu", "blobGb", "databases", "hasCustomDomain", "priceCents", "annualPriceCents", "isForSale", "isAvailable", "apiRateLimit", "backupLimit", "hasDailyBackup", "deploymentVersionLimit", "customDomainLimit", "teamMemberLimit", "minMemoryMb", "maxBots", "maxSites"],
            "properties": {
                "id": {"type": "string", "enum": ["free", "block", "stack", "tower", "fortress", "monolith", *[f"enterprise-{gb}" for gb in ENTERPRISE_SIZES]]},
                "name": {"type": "string"},
                "memoryMb": {"type": "integer", "description": "A memória do plano, dividida entre projetos e bancos."},
                "vcpu": {"type": "number"},
                "blobGb": {"type": "integer", "description": "A cota do [Blob](/hosting/blob) em GB."},
                "databases": {"type": "integer", "description": "Quantos [bancos de dados](/hosting/databases) cabem (0 no Free e no Block)."},
                "hasCustomDomain": {"type": "boolean"},
                "priceCents": {"type": "integer", "description": "Preço do mês em centavos (0 no Free)."},
                "annualPriceCents": {"type": "integer", "description": "Preço de 12 meses num Pix só, com 20% de desconto."},
                "isForSale": {"type": "boolean", "description": "Está à venda pelo painel."},
                "isAvailable": {"type": "boolean", "description": "Pode ser contratado agora: à venda e com espaço nos nossos servidores (o Monolith e o Empresas, sempre). `false` = \"Indisponível no momento\", só com os servidores cheios de verdade; libera sozinho quando abre espaço."},
                "apiRateLimit": {"type": "object", "required": ["perMinute", "perDay"], "properties": {"perMinute": {"type": "integer"}, "perDay": {"type": "integer"}}, "description": "O limite de pedidos da API."},
                "backupLimit": {"type": "integer", "description": "Backups guardados por projeto."},
                "hasDailyBackup": {"type": "boolean"},
                "deploymentVersionLimit": {"type": "integer", "description": "Versões dos envios guardadas por projeto."},
                "customDomainLimit": {"type": "integer", "description": "Domínios próprios por site (0 no Free, que não tem site)."},
                "teamMemberLimit": {"type": "integer", "description": "Membros da [equipe](/account/teams) além do dono, somando os convites pendentes: Tower 3, Fortress 7, Monolith 15, Empresas 32 a 1024 de 20 a 100. `0` = o plano não tem equipe (Free, Block e Stack)."},
                "minMemoryMb": {"type": "object", "required": ["bot", "site"], "properties": {"bot": {"type": "integer"}, "site": {"type": "integer"}}, "description": "A memória mínima de cada tipo: bot 256 nos pagos e 100 no Free; site 512."},
                "maxBots": {"type": "integer", "description": "Quantos bots cabem, cada um com o mínimo: Free 1, Block 4, Stack 8, Tower 16, Fortress 32, Monolith 64, Empresas 32 a 1024 de 128 a 4.096."},
                "maxSites": {"type": "integer", "description": "Quantos sites e APIs cabem: 0 no Free, 2 no Block, e o dobro a cada plano."},
            },
        },
        "Template": {
            "type": "object",
            "description": "Um template da Cube: um projeto pronto, com o código completo.",
            "required": ["id", "name", "description", "type", "language", "version", "memoryMb", "port", "variables", "database", "minimumMemoryMb", "minimumPlan", "connection"],
            "properties": {
                "id": {"type": "string", "enum": TEMPLATE_IDS, "description": "O que vai no campo `template` de [Criar um projeto](/api-reference/projects/create)."},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "type": {"type": "string", "enum": ["bot", "site"]},
                "language": {"type": "string", "enum": ["node", "python", "java"]},
                "version": {"type": "string"},
                "memoryMb": {"type": "integer", "description": "A memória sugerida, em MB (nos bots, 256: o mínimo dos planos pagos). No Free, ela cai para o que cabe no plano. Mande outra em `memoryMb` se quiser, a partir do mínimo do plano."},
                "port": nullable("integer", description="Só site: a porta do app. `null` em bot."),
                "variables": {"type": "array", "items": {
                    "type": "object",
                    "required": ["name", "description", "isRequired", "helpUrl"],
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "isRequired": {"type": "boolean", "description": "Sem ela, o projeto instala e não inicia."},
                        "helpUrl": nullable("string", format="uri", description="Onde ver como pegar o valor."),
                    },
                }},
                "database": {"oneOf": [{
                    "type": "object",
                    "required": ["engine", "variable", "memoryMb"],
                    "properties": {
                        "engine": {"type": "string", "enum": ["postgres", "mysql", "redis"]},
                        "variable": {"type": "string", "description": "A variável que recebe a conexão (`databaseId` no envio)."},
                        "memoryMb": {"type": "integer", "description": "A memória sugerida do banco."},
                    },
                }, {"type": "null"}], "description": "O banco que o painel cria junto. Pela API, [crie o banco](/api-reference/databases/create) e mande o `databaseId`."},
                "minimumMemoryMb": nullable("integer", description="O mínimo próprio do template, acima do do tipo e da linguagem (o Lavalink: 512). Vale ao criar e ao mudar a memória. `null` sem um próprio."),
                "minimumPlan": {"oneOf": [{
                    "type": "object",
                    "required": ["id", "name"],
                    "properties": {"id": {"type": "string"}, "name": {"type": "string"}},
                }, {"type": "null"}], "description": "O menor plano em que o template cabe (o Lavalink: a partir do Block). Num plano menor, `403 template_not_in_plan`."},
                "connection": {"oneOf": [{
                    "type": "object",
                    "required": ["port", "passwordVariable"],
                    "properties": {
                        "port": {"type": "integer", "description": "A porta em que o serviço escuta, dentro da conta."},
                        "passwordVariable": {"type": "string", "description": "A variável com a senha, que a Cube gera ao criar."},
                    },
                }, {"type": "null"}], "description": "O projeto é um serviço privado da conta (o [Lavalink](/hosting/lavalink)): os outros projetos conectam pelo `internalHost`, nesta porta, com a senha de [Ver a conexão](/api-reference/projects/connection)."},
            },
        },
        "ProjectStatus": {
            "type": "string",
            "enum": ["creating", "installing", "running", "stopped", "restarting", "crash_loop", "error"],
            "description": "`creating` (Enviando), `installing` (Instalando), `running` (No ar), `stopped` (Parado), `restarting` (Reiniciando), `crash_loop` (Em loop de erro), `error` (Com erro).",
        },
        "ProjectError": {
            "type": "object",
            "required": ["code", "message"],
            "properties": {
                "code": {"type": "string", "enum": ["install_failed", "install_timeout", "install_out_of_memory", "install_interrupted", "start_failed", "system_packages_failed", "process_exited", "crash_loop"], "description": "Veja [Estados de erro do projeto](/errors#estados-de-erro-do-projeto)."},
                "message": {"type": "string", "description": "Explicação em português."},
            },
        },
        "LastExit": {
            "type": "object",
            "required": ["code", "isOutOfMemory", "exitedAt"],
            "properties": {
                "code": {"type": "integer", "description": "O código de saída do processo."},
                "isOutOfMemory": {"type": "boolean", "description": "`true` se o processo passou da memória do projeto."},
                "exitedAt": {"type": "string", "format": "date-time"},
            },
        },
        "Usage": {
            "type": "object",
            "required": ["memoryMb", "cpuPercent", "networkInBps", "networkOutBps"],
            "properties": {
                "memoryMb": {"type": "integer", "description": "Memória em uso, em MB."},
                "cpuPercent": {"type": "number", "description": "Uso de processador. 100 = um núcleo inteiro."},
                "networkInBps": {"type": "integer", "description": "Rede recebida, em bytes por segundo."},
                "networkOutBps": {"type": "integer", "description": "Rede enviada, em bytes por segundo."},
            },
        },
        "InstallStarted": {
            "type": "object",
            "required": ["project", "isReinstallingDependencies"],
            "properties": {
                "project": ref("Project"),
                "isReinstallingDependencies": {"type": "boolean", "description": "`true` quando as dependências vão ser instaladas de novo; `false` quando só o build (se houver) roda."},
            },
        },
        "Metrics": {
            "type": "object",
            "required": ["window", "intervalSeconds", "memoryLimitMb", "points"],
            "properties": {
                "window": {"type": "string", "enum": ["15m", "1h", "24h"]},
                "intervalSeconds": {"type": "integer", "description": "Segundos entre um ponto e outro: 15, 60 ou 300."},
                "memoryLimitMb": {"type": "integer", "description": "A memória reservada do projeto."},
                "points": {"type": "array", "items": ref("MetricPoint")},
            },
        },
        "Crash": {
            "type": "object",
            "required": ["id", "exitedAt", "startedAt", "uptimeSeconds", "exitCode", "signal", "isOutOfMemory", "memoryLimitMb", "reason", "outcome", "consecutiveCrashes", "restartedAt", "logStatus"],
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "exitedAt": {"type": "string", "format": "date-time", "description": "Quando o processo saiu."},
                "startedAt": {"type": ["string", "null"], "format": "date-time", "description": "Quando aquela vida do processo tinha subido."},
                "uptimeSeconds": {"type": ["integer", "null"], "description": "Tempo no ar antes de cair."},
                "exitCode": {"type": "integer", "description": "O código de saída (diferente de 0)."},
                "signal": {"type": ["string", "null"], "description": "Acima de 128, o sinal que encerrou o processo: `SIGKILL` no 137, `SIGSEGV` no 139, `SIGTERM` no 143."},
                "isOutOfMemory": {"type": "boolean", "description": "Passou da memória reservada do projeto."},
                "memoryLimitMb": {"type": "integer", "description": "A memória que o projeto tinha quando caiu (memória nova só vale depois de reiniciar)."},
                "reason": {"type": "string", "description": "O motivo em pt-BR: `Sem memória: passou de 512 MB`, `Encerrado pelo sinal SIGSEGV (código 139)` ou `Saiu com erro (código 1)`."},
                "outcome": {"type": "string", "enum": ["restarting", "crash_loop", "stopped"], "description": "`restarting`: o reinício automático. `crash_loop`: a 5ª queda seguida, o projeto parou. `stopped`: sem reinício automático (Free)."},
                "consecutiveCrashes": {"type": "integer", "description": "Quedas seguidas, contando esta."},
                "restartedAt": {"type": ["string", "null"], "format": "date-time", "description": "Quando o reinício automático pôs o projeto de volta no ar."},
                "logStatus": {"type": "string", "enum": ["available", "pending", "unavailable"], "description": "Se o log daquele momento está guardado, sendo guardado ou não deu para ler."},
            },
        },
        "CrashList": {
            "type": "object",
            "required": ["crashes", "limit", "retentionDays"],
            "properties": {
                "crashes": {"type": "array", "items": ref("Crash")},
                "limit": {"type": "integer", "description": "Quantas quedas ficam guardadas por projeto (50)."},
                "retentionDays": {"type": "integer", "description": "Por quantos dias (30)."},
            },
        },
        "CrashDetail": {
            "allOf": [
                ref("Crash"),
                {
                    "type": "object",
                    "required": ["log"],
                    "properties": {
                        "log": {
                            "type": ["object", "null"],
                            "required": ["lines", "isTruncated"],
                            "properties": {
                                "lines": {"type": "array", "items": {"type": "object", "required": ["time", "stream", "text"], "properties": {"time": {"type": "string", "format": "date-time"}, "stream": {"type": "string", "enum": ["stdout", "stderr"]}, "text": {"type": "string"}}}},
                                "isTruncated": {"type": "boolean", "description": "Alguma linha ou as mais antigas foram cortadas pelo tamanho."},
                            },
                        },
                    },
                },
            ],
        },
        "Analytics": {
            "type": "object",
            "required": ["window", "intervalSeconds", "totals", "devices", "statusCodes", "responseTimeMs", "points", "routes", "countries"],
            "properties": {
                "window": {"type": "string", "enum": ["24h", "7d", "30d"]},
                "intervalSeconds": {"type": "integer", "description": "Segundos de cada bloco da linha do tempo: 900, 3600 ou 21600."},
                "totals": ref("Traffic"),
                "devices": {
                    "type": "object",
                    "required": ["desktop", "mobile"],
                    "description": "Computador e celular, pelo User-Agent (robôs e `curl` contam como computador).",
                    "properties": {"desktop": ref("Traffic"), "mobile": ref("Traffic")},
                },
                "statusCodes": {
                    "type": "object",
                    "required": ["2xx", "3xx", "4xx", "5xx"],
                    "description": "Quantas respostas de cada classe. As páginas da Cube de site parado ou sem resposta contam como 503.",
                    "properties": {k: {"type": "integer"} for k in ["2xx", "3xx", "4xx", "5xx"]},
                },
                "responseTimeMs": {
                    "type": "object",
                    "required": ["p50", "p95"],
                    "description": "Do pedido chegar até o site mandar os cabeçalhos. `null` sem medida no período.",
                    "properties": {"p50": nullable("integer"), "p95": nullable("integer")},
                },
                "points": {"type": "array", "items": ref("AnalyticsPoint"), "description": "Todos os blocos da janela, do mais velho ao de agora."},
                "routes": {
                    "type": "array",
                    "description": "As 20 rotas mais pedidas: o caminho sem a query (`/login?token=x` conta como `/login`). As outras entram só em `totals`.",
                    "items": {"type": "object", "required": ["path", "requests"], "properties": {"path": {"type": "string"}, "requests": {"type": "integer"}}},
                },
                "countries": {
                    "type": "array",
                    "description": "Todos os países do período, do que mais pediu ao que menos. `code` é o ISO 3166 de 2 letras; `XX` quando o país não é conhecido.",
                    "items": {"type": "object", "required": ["code", "requests", "visits"], "properties": {"code": {"type": "string"}, "requests": {"type": "integer"}, "visits": {"type": "integer"}}},
                },
            },
        },
        "Traffic": {
            "type": "object",
            "required": ["requests", "visits", "bytes"],
            "properties": {
                "requests": {"type": "integer", "description": "Respostas do site no período."},
                "visits": {"type": "integer", "description": "Aparelhos diferentes por dia (IP + navegador), sem cookie e sem guardar o IP."},
                "bytes": {"type": "integer", "description": "O que saiu para os visitantes (cabeçalhos e corpo)."},
            },
        },
        "AnalyticsPoint": {
            "type": "object",
            "required": ["time", "requests", "visits"],
            "properties": {
                "time": {"type": "string", "format": "date-time", "description": "O começo do bloco."},
                "requests": {"type": "integer"},
                "visits": {"type": "integer"},
            },
        },
        "MetricPoint": {
            "type": "object",
            "required": ["time", "memoryMb", "cpuPercent", "networkInBps", "networkOutBps"],
            "properties": {
                "time": {"type": "string", "format": "date-time"},
                "memoryMb": {"type": "integer"},
                "cpuPercent": {"type": "number", "description": "100 = um núcleo inteiro."},
                "networkInBps": {"type": "number", "description": "Bytes por segundo recebidos. Inteiro em `15m` e `1h`; em `24h` pode ter uma casa decimal (a média dos 5 minutos)."},
                "networkOutBps": {"type": "number", "description": "Bytes por segundo enviados. Inteiro em `15m` e `1h`; em `24h` pode ter uma casa decimal (a média dos 5 minutos)."},
            },
        },
        "Backup": {
            "type": "object",
            "description": "Uma cópia dos arquivos do projeto (sem as dependências).",
            "required": ["id", "type", "status", "sizeBytes", "error", "createdAt", "finishedAt", "expiresAt"],
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "type": {"type": "string", "enum": ["manual", "daily", "before_suspension", "before_deletion"], "description": "`manual` (Fazer backup agora ou a API), `daily` (o automático dos planos pagos), `before_suspension` (a cópia feita quando a conta é suspensa), `before_deletion` (a cópia antes de apagar um projeto parado)."},
                "status": {"type": "string", "enum": ["pending", "creating", "ready", "failed"], "description": "`pending` (na fila), `creating` (sendo feito), `ready` (pronto para baixar e restaurar), `failed` (não deu certo; o motivo vem em `error`)."},
                "sizeBytes": nullable("integer", description="Tamanho do `.zip`, em bytes. `null` até ficar pronto."),
                "error": {"oneOf": [ref("BackupError"), {"type": "null"}], "description": "O motivo, quando `status` é `failed`."},
                "createdAt": {"type": "string", "format": "date-time"},
                "finishedAt": nullable("string", format="date-time"),
                "expiresAt": {"type": "string", "format": "date-time", "description": "Até quando o backup fica guardado (30 dias). Pode sair antes, quando o histórico passa do limite do plano."},
            },
        },
        "BackupError": {
            "type": "object",
            "required": ["code", "message"],
            "properties": {
                "code": {"type": "string", "enum": ["too_large", "empty", "backup_failed"], "description": "`too_large`: o projeto passa de 500 MB ou de 20.000 arquivos sem as dependências. `empty`: não há arquivo para guardar. `backup_failed`: falha do nosso lado; tente de novo."},
                "message": {"type": "string", "description": "Explicação em português."},
            },
        },
        "Deployment": {
            "type": "object",
            "description": "Um envio: um `.zip`, um push ou um Implantar agora do [deploy pelo GitHub](/github), um Aplicar mudanças, uma troca de versão da linguagem, um backup restaurado ou uma volta para uma versão.",
            "required": ["id", "source", "fileName", "commit", "sizeBytes", "apiKeyName", "hasReinstalledDependencies", "result", "isRestorable", "isCurrent", "restoredFrom", "startedAt", "finishedAt", "activatedAt"],
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "source": {"type": "string", "enum": ["initial_upload", "code_upload", "file_editor", "version_change", "entry_change", "backup_restore", "rollback", "github_push", "github_manual", "dependencies_reinstall"], "description": "`initial_upload` (o `.zip` que criou o projeto, ou o primeiro commit dele pelo GitHub), `code_upload` (um `.zip` novo), `file_editor` (Aplicar mudanças no painel; os arquivos daquele momento ficam guardados como versão), `version_change` (troca da versão da linguagem), `entry_change` (troca do arquivo principal de um projeto Go, que compila de novo no próximo início), `backup_restore` (backup restaurado), `rollback` (volta para uma versão), `github_push` (um push na branch escolhida), `github_manual` (o Implantar agora do painel) e `dependencies_reinstall` (o Reinstalar dependências da aba Arquivos)."},
                "fileName": nullable("string", description="O nome do `.zip`, quando houver."),
                "commit": {
                    "oneOf": [
                        {"type": "object", "required": ["sha", "message", "author"], "properties": {"sha": {"type": "string", "description": "O commit inteiro (40 caracteres)."}, "message": {"type": "string", "description": "A mensagem do commit (até 500 caracteres)."}, "author": nullable("string", description="Quem fez o commit.")}},
                        {"type": "null"},
                    ],
                    "description": "No [deploy pelo GitHub](/github): o commit que foi ao ar (ou que parou antes). `null` nos outros envios.",
                },
                "sizeBytes": nullable("integer", description="O tamanho do `.zip` guardado, em bytes. `null` quando a linha não guarda arquivos."),
                "apiKeyName": nullable("string", description="O nome da chave de API que enviou. `null` quando foi pelo painel."),
                "hasReinstalledDependencies": {"type": "boolean", "description": "`true` quando as dependências foram instaladas de novo; `false` quando o manifesto não mudou."},
                "result": nullable("string", description="`null` enquanto instala, `ok` quando terminou bem, ou o código do erro do projeto (`install_failed`, `start_failed`…). No deploy pelo GitHub, o envio que parou antes da instalação vem já fechado com o motivo (`repository_too_large`, `repository_not_found`, `unsafe_zip`, `github_unavailable`, `project_busy`…) e nada mudou no projeto."),
                "isRestorable": {"type": "boolean", "description": "`true` quando a versão ainda está guardada e dentro do limite do seu plano de agora: dá para baixar e voltar para ela. Na `file_editor`, fica `true` alguns segundos depois de aplicar."},
                "isCurrent": {"type": "boolean", "description": "`true` no que está no projeto agora: a última troca dos arquivos. Depois de voltar para uma versão, é a versão da volta (não a linha `rollback`); depois de Aplicar mudanças ou de restaurar um backup, é essa linha. A troca da versão da linguagem, a troca do arquivo principal do Go e o envio pelo GitHub que parou antes da instalação não contam."},
                "restoredFrom": {
                    "oneOf": [
                        {"type": "object", "required": ["id", "startedAt"], "properties": {"id": {"type": "string", "format": "uuid"}, "startedAt": {"type": "string", "format": "date-time"}}},
                        {"type": "null"},
                    ],
                    "description": "Numa volta (`rollback`): a versão para a qual o projeto voltou.",
                },
                "startedAt": {"type": "string", "format": "date-time"},
                "finishedAt": nullable("string", format="date-time"),
                "activatedAt": nullable("string", format="date-time", description="Quando foi posta no projeto pela última vez: o envio, ou a volta mais recente para ela. O limite do plano guarda as de `activatedAt` mais recente. `null` no envio pelo GitHub que parou antes da instalação (nada mudou no projeto)."),
            },
        },
        "DeploymentList": {
            "type": "object",
            "required": ["deployments", "versionLimit", "retentionDays"],
            "properties": {
                "deployments": {"type": "array", "items": ref("Deployment"), "description": "Os 20 últimos e as versões ainda guardadas, do mais novo para o mais antigo."},
                "versionLimit": {"type": "integer", "description": "Quantas versões (`.zip` enviados) o plano guarda por projeto, as usadas por último: Free 2 (a de agora e a anterior), Block 3, Stack 5, Tower 7, Fortress 10, Monolith 14."},
                "retentionDays": {"type": "integer", "description": "Por quantos dias no máximo uma versão fica guardada."},
            },
        },
        "AlertSettings": {
            "type": "object",
            "required": ["isAvailable", "isCrashEnabled", "isCrashLoopEnabled", "isHighMemoryEnabled", "isDiscordEnabled", "isDiscordLinked"],
            "properties": {
                "isAvailable": {"type": "boolean", "description": "`true` nos planos pagos, que têm os avisos por e-mail."},
                "isCrashEnabled": {"type": "boolean", "description": "E-mail quando o processo cai e o reinício automático sobe de novo (quedas seguidas vêm somadas)."},
                "isCrashLoopEnabled": {"type": "boolean", "description": "E-mail quando o projeto entra em `crash_loop`: 5 quedas seguidas, e ele fica parado até você iniciar."},
                "isHighMemoryEnabled": {"type": "boolean", "description": "E-mail quando o projeto passa 5 minutos seguidos com 90% ou mais da memória."},
                "isDiscordEnabled": {"type": "boolean", "description": "Os mesmos avisos também por mensagem direta do bot da Cube no Discord, junto do e-mail. Guia em [Avisos por e-mail e Discord](/hosting/alerts#discord)."},
                "isDiscordLinked": {"type": "boolean", "description": "A conta tem um Discord vinculado; sem ele, o Discord não liga."},
            },
        },
        "AccountBackups": {
            "type": "object",
            "description": "Os backups de todos os projetos da conta, também os de um projeto apagado, e os dos bancos excluídos.",
            "required": ["limit", "retentionDays", "isDailyAvailable", "projects", "deletedDatabases"],
            "properties": {
                "limit": {"type": "integer", "description": "Quantos backups manuais e automáticos o plano guarda por projeto."},
                "retentionDays": {"type": "integer", "description": "Por quantos dias no máximo um backup fica guardado (30)."},
                "isDailyAvailable": {"type": "boolean", "description": "`true` nos planos pagos, que têm o backup automático diário."},
                "projects": {
                    "type": "array",
                    "description": "Um item por projeto da conta (com ou sem backup) e, depois, um por projeto apagado que ainda tem backup.",
                    "items": {
                        "type": "object",
                        "required": ["id", "name", "type", "isDeleted", "isDailyEnabled", "backups"],
                        "properties": {
                            "id": {"type": "string", "description": "ID do projeto (o de antes, se ele foi apagado)."},
                            "name": {"type": "string"},
                            "type": nullable("string", enum=["bot", "site", None], description="O tipo do projeto (o subdomínio só volta no site). Do projeto apagado, o do backup mais novo que guardou a configuração; `null` quando nenhum guardou."),
                            "isDeleted": {"type": "boolean", "description": "`true` no projeto apagado: os backups dele ficam por até 30 dias e voltam pelo [Restaurar como novo](/api-reference/backups/restore-as-new)."},
                            "isDailyEnabled": {"type": "boolean"},
                            "backups": {
                                "type": "array",
                                "description": "Do mais novo para o mais antigo.",
                                "items": {
                                    "allOf": [
                                        ref("Backup"),
                                        {
                                            "type": "object",
                                            "required": ["hasConfig", "hasVariables"],
                                            "properties": {
                                                "hasConfig": {"type": "boolean", "description": "O backup guardou a configuração do projeto. `false` só nos de antes de 28/09/2026: voltam pelo `cube.json` do `.zip`, sem as variáveis."},
                                                "hasVariables": {"type": "boolean", "description": "O backup guardou alguma variável de ambiente, que volta no Restaurar como novo."},
                                            },
                                        },
                                    ],
                                },
                            },
                        },
                    },
                },
                "deletedDatabases": {
                    "type": "array",
                    "description": "Um item por banco de dados excluído que ainda tem backup (7 dias; somando os bancos excluídos, a conta guarda os 7 mais recentes). Restaurar como um banco novo é só pelo painel.",
                    "items": {
                        "type": "object",
                        "required": ["id", "name", "engine", "engineName", "memoryMb", "backups"],
                        "properties": {
                            "id": {"type": "string", "description": "ID do banco excluído."},
                            "name": {"type": "string"},
                            "engine": {"type": "string", "enum": ["postgres", "mysql", "mongodb", "redis"]},
                            "engineName": {"type": "string"},
                            "memoryMb": {"type": "integer"},
                            "backups": {"type": "array", "items": ref("DatabaseBackup")},
                        },
                    },
                },
            },
        },
        "BackupList": {
            "type": "object",
            "required": ["backups", "limit", "retentionDays", "isDailyAvailable", "isDailyEnabled"],
            "properties": {
                "backups": {"type": "array", "items": ref("Backup"), "description": "Do mais novo para o mais antigo."},
                "limit": {"type": "integer", "description": "Quantos backups manuais e automáticos o plano guarda por projeto (Free 1, Block 3, Stack 5, Tower 7, Fortress 10, Monolith 14)."},
                "retentionDays": {"type": "integer", "description": "Por quantos dias no máximo um backup fica guardado."},
                "isDailyAvailable": {"type": "boolean", "description": "`true` nos planos pagos, que têm o backup automático diário."},
                "isDailyEnabled": {"type": "boolean", "description": "Se o backup automático deste projeto está ligado (liga e desliga no painel)."},
            },
        },
        "Domain": {
            "type": "object",
            "description": "Um domínio próprio de um site.",
            "required": ["id", "projectId", "hostname", "redirectTo", "status", "error", "records", "verifiedAt", "checkedAt", "createdAt", "project"],
            "properties": {
                "id": {"type": "string", "description": "ID do domínio (26 caracteres)."},
                "projectId": {"type": "string", "description": "O site que o domínio abre."},
                "hostname": {"type": "string", "description": "O domínio, em minúsculas (acento em punycode: `café.com.br` → `xn--caf-dma.com.br`)."},
                "redirectTo": nullable("string", description="Outro domínio do site para onde este redireciona (`308`, com o caminho); `null` = abre o site."),
                "status": {"type": "string", "enum": ["pending", "active", "error"], "description": "`pending`: falta o TXT ou o CNAME (verificando). `active`: verificado e chegando à Cube. `error`: veja `error`."},
                "error": {
                    "oneOf": [
                        {
                            "type": "object",
                            "required": ["code", "message"],
                            "properties": {
                                "code": {"type": "string", "enum": ["verification_expired", "domain_taken", "certificate_failed", "plan_not_allowed"]},
                                "message": {"type": "string"},
                            },
                        },
                        {"type": "null"},
                    ],
                    "description": "`verification_expired`: sem o TXT em 7 dias. `domain_taken`: outra conta provou a posse antes. `certificate_failed`: o HTTPS não saiu. `plan_not_allowed`: a conta está no Free, que não tem site.",
                },
                "records": {"type": "array", "items": ref("DomainRecord"), "description": "Os dois registros para criar no DNS do domínio."},
                "verifiedAt": nullable("string", format="date-time", description="Quando a posse foi provada; `null` até achar o TXT."),
                "checkedAt": nullable("string", format="date-time", description="A última conferência."),
                "createdAt": {"type": "string", "format": "date-time"},
                "project": {
                    "type": "object",
                    "required": ["id", "name"],
                    "properties": {"id": {"type": "string"}, "name": {"type": "string"}},
                },
            },
        },
        "DomainRecord": {
            "type": "object",
            "required": ["type", "name", "value", "isOk"],
            "properties": {
                "type": {"type": "string", "enum": ["CNAME", "TXT"]},
                "name": {"type": "string", "description": "O nome do registro. O TXT fica em `_cube-verify.<domínio sem o www>`: o `www` e a raiz usam o mesmo."},
                "value": {"type": "string", "description": "O valor: `domains.cubehost.dev` no CNAME; `cube-verify=<token>` no TXT."},
                "isOk": {"type": "boolean", "description": "Se a Cube já achou o registro certo."},
            },
        },
        "DomainList": {
            "type": "object",
            "required": ["domains", "used", "limit", "target", "isAvailable"],
            "properties": {
                "domains": {"type": "array", "items": ref("Domain")},
                "used": {"type": "integer", "description": "Quantos sites têm domínio (o `www` vai junto e não conta). No site: 0 ou 1."},
                "limit": {"type": "integer", "description": "No site: 1 (0 num bot ou no Free). Na conta: 1 por site que o plano comporta (0 no Free, que não tem site)."},
                "target": {"type": "string", "description": "O alvo do CNAME (`domains.cubehost.dev`)."},
                "isAvailable": {"type": "boolean", "description": "`false` quando o domínio próprio está fora do ar."},
            },
        },
        "DomainInput": {
            "type": "object",
            "required": ["hostname"],
            "additionalProperties": False,
            "properties": {
                "hostname": {"type": "string", "description": "Só o domínio (`loja.com.br`, `www.loja.com.br`), sem `https://`, barra nem porta."},
                "redirectTo": nullable("string", description="Opcional: outro domínio do mesmo site, que abre o site direto, para onde este redireciona."),
            },
        },
        "DomainUpdateInput": {
            "type": "object",
            "required": ["redirectTo"],
            "additionalProperties": False,
            "properties": {
                "redirectTo": nullable("string", description="Outro domínio do site para redirecionar, ou `null` para abrir o site direto."),
            },
        },
        "BlobObject": {
            "type": "object",
            "required": ["id", "path", "sizeBytes", "contentType", "status", "visibility", "publicUrl", "expiresAt", "cacheMaxAgeSeconds", "isDownloadForced", "createdAt"],
            "properties": {
                "id": {"type": "string", "description": "ID do arquivo (26 caracteres)."},
                "path": {"type": "string", "description": "O nome, com pastas por `/` (`img/logo.png`)."},
                "sizeBytes": {"type": "integer"},
                "contentType": {"type": "string", "description": "O tipo mandado no envio (`application/octet-stream` sem ele)."},
                "status": {"type": "string", "enum": ["pending", "ready"], "description": "`pending` até a confirmação do envio."},
                "visibility": {"type": "string", "enum": ["public", "private"], "description": "`public`: abre pelo `publicUrl`, sem vencer. `private` (o padrão): só por link temporário."},
                "publicUrl": nullable("string", description="O link fixo (`https://cdn.cubehost.dev/<id>/<nome>`) do arquivo pronto e público; `null` no privado e no envio em andamento."),
                "expiresAt": nullable("string", description="Quando o arquivo sai do Blob e os links dele param de abrir; `null`: nunca vence."),
                "cacheMaxAgeSeconds": nullable("integer", description="O cache do link público que a regra da pasta deu no envio; `null`: o navegador confere a cada uso."),
                "isDownloadForced": {"type": "boolean", "description": "O link sempre baixa como anexo, até a imagem."},
                "createdAt": {"type": "string", "format": "date-time", "description": "Quando o envio foi confirmado."},
            },
        },
        "BlobList": {
            "type": "object",
            "required": ["objects", "folders", "nextCursor", "usage"],
            "properties": {
                "objects": {"type": "array", "items": ref("BlobObject")},
                "folders": {
                    "type": "array",
                    "description": "Com `delimiter=/`: as subpastas da pasta pedida.",
                    "items": {
                        "type": "object",
                        "required": ["prefix", "objectCount", "sizeBytes"],
                        "properties": {
                            "prefix": {"type": "string", "description": "O prefixo da pasta, com `/` no fim (`img/icones/`)."},
                            "objectCount": {"type": "integer"},
                            "sizeBytes": {"type": "integer"},
                        },
                    },
                },
                "nextCursor": nullable("string", description="Para a próxima página, em `cursor`; `null` na última."),
                "usage": ref("BlobUsage"),
            },
        },
        "BlobUsage": {
            "type": "object",
            "required": ["usedBytes", "quotaBytes", "objectCount", "maxObjectBytes", "multipartThresholdBytes", "isAvailable"],
            "properties": {
                "usedBytes": {"type": "integer", "description": "O que já está guardado (envios confirmados)."},
                "quotaBytes": {"type": "integer", "description": "A cota do plano (1 GB = 1024³ bytes): Block 5 GB, Stack 10, Tower 25, Fortress 50, Monolith 100; 0 no Free."},
                "objectCount": {"type": "integer"},
                "maxObjectBytes": {"type": "integer", "description": "O maior arquivo aceito no plano: 1/5 da cota, até 4 GB (Block 1 GB, Stack 2 GB, do Tower em diante 4 GB)."},
                "multipartThresholdBytes": {"type": "integer", "description": "Acima disto (16 MB), o painel manda em partes; pela API, o envio em partes é com `isMultipart`."},
                "isAvailable": {"type": "boolean", "description": "`false` quando o armazenamento não está disponível: a lista funciona, enviar e baixar não."},
            },
        },
        "BlobUploadInput": {
            "type": "object",
            "required": ["path", "sizeBytes"],
            "properties": {
                "path": {"type": "string", "description": "O nome, com pastas por `/`: até 1024 bytes, sem `/` no começo ou no fim, sem pasta vazia, `.` ou `..`, sem `\\`."},
                "sizeBytes": {"type": "integer", "minimum": 0, "maximum": 4294967296, "description": "O tamanho exato do arquivo, até o teto do plano (`maxObjectBytes`): o link só aceita esse tamanho."},
                "contentType": {"type": "string", "description": "O tipo (`image/png`), sem parâmetros; padrão `application/octet-stream`. O link só aceita esse tipo."},
                "visibility": {"type": "string", "enum": ["public", "private"], "description": "`public` dá ao arquivo pronto um link fixo que não vence (`publicUrl`). Sem ele, vale a visibilidade padrão da regra da pasta e, sem regra, `private`."},
                "expiresAt": nullable("string", description="Quando o arquivo vence (ISO, de 1 minuto a 10 anos). `null`: nunca vence. Sem o campo, vale a expiração padrão da regra da pasta."),
                "isDownloadForced": {"type": "boolean", "default": False, "description": "O link sempre baixa como anexo, até a imagem."},
                "shouldOverwrite": {"type": "boolean", "default": True, "description": "`false`: com um arquivo de mesmo nome, responde `409 object_exists` e nada muda."},
                "shouldAddRandomSuffix": {"type": "boolean", "default": False, "description": "Põe 8 letras e números aleatórios antes da extensão (`logo-k3j9x2qa.png`)."},
                "isMultipart": {"type": "boolean", "default": False, "description": "Envio em partes de 16 MB, que pode continuar por 24 horas (pelo menos 1 byte)."},
            },
        },
        "BlobUpload": {
            "type": "object",
            "required": ["object", "upload"],
            "properties": {
                "object": ref("BlobObject"),
                "upload": {
                    "type": "object",
                    "required": ["type", "expiresAt"],
                    "properties": {
                        "type": {"type": "string", "enum": ["single", "multipart"], "description": "`single`: um `PUT` no `url`. `multipart`: as partes, pelas [URLs das partes](/api-reference/blob/parts-create)."},
                        "url": {"type": "string", "format": "uri", "description": "Só no `single`: o link do envio, direto no armazenamento (sem a chave de API)."},
                        "method": {"type": "string", "enum": ["PUT"], "description": "Só no `single`."},
                        "headers": {"type": "object", "additionalProperties": {"type": "string"}, "description": "Só no `single`: os cabeçalhos que o `PUT` precisa mandar (o `content-type`)."},
                        "partSizeBytes": {"type": "integer", "description": "Só no `multipart`: o tamanho de cada parte (16 MB), menos a última."},
                        "partCount": {"type": "integer", "description": "Só no `multipart`: quantas partes o arquivo tem."},
                        "expiresAt": {"type": "string", "format": "date-time", "description": "Até quando o `PUT` pode começar (15 minutos), ou até quando o envio em partes vale (24 horas)."},
                    },
                },
            },
        },
        "BlobParts": {
            "type": "object",
            "required": ["parts", "partSizeBytes", "partCount", "expiresAt"],
            "properties": {
                "parts": {"type": "array", "description": "As partes que chegaram com o tamanho certo.", "items": {"type": "object", "required": ["partNumber", "sizeBytes"], "properties": {"partNumber": {"type": "integer"}, "sizeBytes": {"type": "integer"}}}},
                "partSizeBytes": {"type": "integer"},
                "partCount": {"type": "integer"},
                "expiresAt": {"type": "string", "format": "date-time", "description": "Até quando o envio vale (24 horas desde o pedido)."},
            },
        },
        "BlobPartUrls": {
            "type": "object",
            "required": ["parts", "expiresAt"],
            "properties": {
                "parts": {"type": "array", "items": {"type": "object", "required": ["partNumber", "sizeBytes", "url"], "properties": {
                    "partNumber": {"type": "integer"},
                    "sizeBytes": {"type": "integer", "description": "O tamanho exato da parte: a URL só aceita esse."},
                    "url": {"type": "string", "format": "uri", "description": "A URL do `PUT` da parte, direto no armazenamento (sem a chave de API)."},
                }}},
                "expiresAt": {"type": "string", "format": "date-time", "description": "Até quando as URLs valem (1 hora, ou o que falta das 24 horas)."},
            },
        },
        "BlobFolderRuleInput": {
            "type": "object",
            "required": ["folder"],
            "properties": {
                "folder": {"type": "string", "description": "A pasta (`backups/diarios`), sem `/` nas pontas; a regra vale também para as subpastas."},
                "defaultVisibility": nullable("string", description="`public` ou `private`: a visibilidade dos envios que não dizem a deles."),
                "defaultExpirationDays": nullable("integer", description="De 1 a 3650: em quantos dias vencem os envios que não dizem o `expiresAt`."),
                "cacheMaxAgeSeconds": nullable("integer", description="De 60 a 31536000: o cache do link público dos arquivos enviados. Com ele, quem já abriu fica com a cópia até vencer, mesmo se o arquivo ficar privado ou for apagado."),
                "maxFileSizeBytes": nullable("integer", description="O maior arquivo aceito na pasta (até 4 GB)."),
                "allowedExtensions": {"type": "array", "maxItems": 50, "items": {"type": "string"}, "description": "As extensões aceitas (`png`, `tar.gz`); vazia aceita qualquer uma."},
                "deleteAfterDays": nullable("integer", description="De 1 a 3650: apaga os arquivos da pasta com mais desses dias, inclusive os que já estão lá, a partir de 24 horas depois de salvar."),
            },
        },
        "BlobFolderRule": {
            "allOf": [
                ref("BlobFolderRuleInput"),
                {"type": "object", "required": ["deletionStartsAt", "updatedAt"], "properties": {
                    "deletionStartsAt": nullable("string", description="Quando o `deleteAfterDays` começa a apagar (24 horas depois de salvo); `null` sem ele."),
                    "updatedAt": {"type": "string", "format": "date-time"},
                }},
            ],
        },
        "BlobFolderRules": {
            "type": "object",
            "required": ["rules", "limit"],
            "properties": {
                "rules": {"type": "array", "items": ref("BlobFolderRule")},
                "limit": {"type": "integer", "description": "Quantas regras o plano tem: 1 por GB da cota, até 50 (Block 5, Stack 10, Tower 25); 0 no Free."},
            },
        },
        "AccountUsage": {
            "type": "object",
            "required": ["plan", "memory", "projects", "databases", "blob"],
            "properties": {
                "plan": {
                    "type": "object",
                    "required": ["id", "name", "memoryMb", "vcpu", "maxBots", "maxSites", "hasAutoRestart", "zipMaxMb"],
                    "properties": {
                        "id": {"type": "string", "description": "`free`, `block`, `stack`, `tower`, `fortress`, `monolith` ou um tamanho do Empresas (`enterprise-32` a `enterprise-1024`)."},
                        "name": {"type": "string"},
                        "memoryMb": {"type": "integer", "description": "Memória do plano, dividida entre os projetos."},
                        "vcpu": {"type": "number"},
                        "maxBots": {"type": "integer", "description": "Quantos projetos cabem no plano, cada um com o mínimo do bot: 1 no Free, 4 no Block, e o dobro a cada plano."},
                        "maxSites": {"type": "integer", "description": "Quantos sites e APIs cabem no plano (0 no Free)."},
                        "minMemoryMb": {"type": "object", "required": ["bot", "site"], "properties": {"bot": {"type": "integer"}, "site": {"type": "integer"}}, "description": "A memória mínima de cada tipo no plano: bot 256 nos pagos e 100 no Free; site 512. Vale para criar e para mudar a memória."},
                        "hasAutoRestart": {"type": "boolean", "description": "Se o projeto que cai volta sozinho (planos pagos)."},
                        "zipMaxMb": {"type": "integer", "description": "Tamanho máximo do .zip: 5 no Free, 10 nos pagos."},
                        "maxDatabases": {"type": "integer", "description": "Quantos [bancos de dados](/hosting/databases) cabem no plano (0 no Free e no Block)."},
                        "blobGb": {"type": "integer", "description": "A cota do [Blob](/hosting/blob) em GB (0 no Free)."},
                        "customDomainLimit": {"type": "integer", "description": "Quantos [domínios próprios](/hosting/domains) cada site tem: 1, com o `www` junto (0 no Free, que não tem site)."},
                    },
                },
                "memory": {
                    "type": "object",
                    "required": ["reservedMb", "freeMb", "inUseMb"],
                    "properties": {
                        "reservedMb": {"type": "integer", "description": "Soma da memória de todos os projetos e bancos de dados, ligados ou não."},
                        "freeMb": {"type": "integer", "description": "O que sobra do plano para projetos novos ou maiores."},
                        "inUseMb": {"type": "integer", "description": "Memória em uso agora pelos projetos no ar."},
                    },
                },
                "projects": {
                    "type": "object",
                    "required": ["total", "running"],
                    "properties": {"total": {"type": "integer"}, "running": {"type": "integer"}},
                },
                "databases": {
                    "type": "object",
                    "required": ["total", "running", "reservedMb"],
                    "description": "Os [bancos de dados](/hosting/databases) da conta.",
                    "properties": {
                        "total": {"type": "integer"},
                        "running": {"type": "integer", "description": "Os que você quer no ar (parados não contam)."},
                        "reservedMb": {"type": "integer", "description": "A memória dos bancos, que já está somada em `memory.reservedMb`."},
                    },
                },
                "blob": {
                    "type": "object",
                    "required": ["usedBytes", "quotaBytes", "objectCount"],
                    "description": "O [Blob](/hosting/blob) da conta: só os envios confirmados contam como usado.",
                    "properties": {
                        "usedBytes": {"type": "integer"},
                        "quotaBytes": {"type": "integer", "description": "0 no Free."},
                        "objectCount": {"type": "integer"},
                    },
                },
                "customDomains": {
                    "type": "object",
                    "required": ["used", "isAvailable"],
                    "description": "Os [domínios próprios](/hosting/domains) da conta.",
                    "properties": {
                        "used": {"type": "integer", "description": "Quantos sites da conta têm domínio, verificado ou não (o `www` não conta)."},
                        "isAvailable": {"type": "boolean", "description": "`false` quando o domínio próprio está fora do ar."},
                    },
                },
            },
        },
        "VariableName": {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string", "description": "O nome da variável. O valor nunca volta."}},
        },
        "VariablesInput": {
            "type": "object",
            "required": ["variables"],
            "properties": {
                "variables": {
                    "type": "array",
                    "maxItems": 50,
                    "items": {
                        "type": "object",
                        "required": ["name"],
                        "properties": {
                            "name": {"type": "string", "pattern": "^[A-Za-z_][A-Za-z0-9_]{0,63}$", "description": "Nome da variável."},
                            "value": {"type": "string", "maxLength": 4096, "description": "Valor novo, numa linha só. Sem ele, o valor guardado é mantido."},
                        },
                    },
                }
            },
        },
        "Database": {
            "type": "object",
            "description": "Um banco de dados da conta: PostgreSQL, MySQL, MongoDB ou Redis.",
            "required": ["id", "name", "engine", "engineName", "host", "port", "status", "memoryMb", "usage", "disk", "externalAccess", "startedAt", "createdAt", "updatedAt"],
            "properties": {
                "id": {"type": "string", "description": "ID do banco, 26 caracteres."},
                "name": {"type": "string", "pattern": "^[a-z][a-z0-9-]{1,30}[a-z0-9]$", "description": "Nome do banco, que é também o endereço interno."},
                "engine": {"type": "string", "enum": ["postgres", "mysql", "mongodb", "redis"]},
                "engineName": {"type": "string", "description": "`PostgreSQL`, `MySQL`, `MongoDB` ou `Redis`."},
                "host": {"type": "string", "description": "O endereço que os projetos da conta usam (igual ao `name`). Só vale de dentro da conta."},
                "port": {"type": "integer", "description": "5432 (PostgreSQL), 3306 (MySQL), 27017 (MongoDB) ou 6379 (Redis)."},
                "status": {"type": "string", "enum": ["creating", "starting", "running", "restarting", "restoring", "stopped", "error"], "description": "`starting`: subiu e ainda não aceita conexões. `restoring`: um backup está sendo restaurado. `error`: deveria estar no ar e não está (a Cube tenta subir de novo a cada 30 s)."},
                "memoryMb": {"type": "integer", "description": "Memória reservada no plano."},
                "usage": {"oneOf": [{"type": "object", "required": ["memoryMb"], "properties": {"memoryMb": {"type": "integer"}}}, {"type": "null"}], "description": "A memória em uso agora. `null` parado ou quando não dá para saber."},
                "disk": {"type": "object", "required": ["usedMb", "limitMb"], "properties": {"usedMb": nullable("integer", description="Espaço usado. `null` quando não dá para saber agora."), "limitMb": {"type": "integer", "description": "Espaço do banco (2048)."}}},
                "externalAccess": {
                    "type": "object",
                    "description": "O [acesso externo](/hosting/databases#acesso-externo): conectar de fora da Cube com o certificado de cliente do banco.",
                    "required": ["isAvailable", "isEnabled", "host", "certificate"],
                    "properties": {
                        "isAvailable": {"type": "boolean", "description": "`false` = o acesso externo ainda não está liberado."},
                        "isEnabled": {"type": "boolean", "description": "Tem um certificado valendo: quem tiver ele e a senha conecta de fora. Vencido, fica `false` e o `certificate` continua com as datas: gere outro no painel."},
                        "host": {"type": "string", "description": "`db.cubehost.dev`, ou `mysql.cubehost.dev` no MySQL."},
                        "certificate": {"oneOf": [{"type": "object", "required": ["createdAt", "expiresAt"], "properties": {"createdAt": {"type": "string", "format": "date-time"}, "expiresAt": {"type": "string", "format": "date-time", "description": "Depois disso o certificado para; gere outro no painel."}}}, {"type": "null"}], "description": "`null` com o acesso desligado. Vencido, continua aqui (com `isEnabled: false`) até você gerar outro ou desligar."},
                    },
                },
                "startedAt": nullable("string", format="date-time", description="Desde quando está no ar."),
                "createdAt": {"type": "string", "format": "date-time"},
                "updatedAt": {"type": "string", "format": "date-time"},
            },
        },
        "DatabaseInput": {
            "type": "object",
            "required": ["engine", "name", "memoryMb"],
            "additionalProperties": False,
            "properties": {
                "engine": {"type": "string", "enum": ["postgres", "mysql", "mongodb", "redis"]},
                "name": {"type": "string", "pattern": "^[a-z][a-z0-9-]{1,30}[a-z0-9]$", "description": "De 3 a 32 caracteres: minúsculas, números e hífen, começando com letra e sem terminar em hífen. Não pode ser `localhost` nem começar com `cube`. Único na conta."},
                "memoryMb": {"type": "integer", "minimum": 256, "description": "Mínimo de 512 MB (256 MB no Redis), até a memória do plano."},
            },
        },
        "DatabaseList": {
            "type": "object",
            "required": ["databases", "limit", "freeMemoryMb", "diskMb", "backupRetentionDays", "engines"],
            "properties": {
                "databases": {"type": "array", "items": ref("Database"), "description": "Do mais novo para o mais antigo."},
                "limit": {"type": "integer", "description": "Quantos bancos o plano permite (0 no Free e no Block, Stack 1, Tower 3, Fortress 6, Monolith 12, Empresas 32 a 1024 de 64 a 2.048)."},
                "freeMemoryMb": {"type": "integer", "description": "A memória do plano que sobra, somando projetos e bancos."},
                "diskMb": {"type": "integer", "description": "Espaço de cada banco, em MB."},
                "backupRetentionDays": {"type": "integer", "description": "Por quantos dias o backup diário fica guardado (7)."},
                "engines": {"type": "array", "items": {"type": "object", "required": ["id", "name", "port", "minMemoryMb", "isAvailable"], "properties": {"id": {"type": "string"}, "name": {"type": "string"}, "port": {"type": "integer"}, "minMemoryMb": {"type": "integer"}, "isAvailable": {"type": "boolean", "description": "`false` = chega em breve: ainda não dá para criar (hoje, todos estão liberados)."}}}},
            },
        },
        "DatabaseCredentials": {
            "type": "object",
            "required": ["host", "port", "username", "password", "database", "url", "envName"],
            "properties": {
                "host": {"type": "string"},
                "port": {"type": "integer"},
                "username": {"type": "string", "description": "`cube` (`default` no Redis)."},
                "password": {"type": "string", "description": "Gerada pela Cube (192 bits). Trate como segredo."},
                "database": nullable("string", description="O banco dentro do servidor: o nome com `_` no lugar de `-`. `null` no Redis."),
                "url": {"type": "string", "description": "A string de conexão pronta: `postgresql://…`, `mysql://…`, `mongodb://…?authSource=admin` ou `redis://…`."},
                "envName": {"type": "string", "description": "O nome de variável sugerido: `DATABASE_URL`, `MONGODB_URI` ou `REDIS_URL`."},
            },
        },
        "DatabaseBackup": {
            "type": "object",
            "required": ["id", "type", "status", "sizeBytes", "error", "createdAt", "finishedAt", "expiresAt"],
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "type": {"type": "string", "enum": ["manual", "daily"], "description": "`manual` (Fazer backup agora, no painel ou pela API) ou `daily` (o automático)."},
                "status": {"type": "string", "enum": ["pending", "creating", "ready", "failed"]},
                "sizeBytes": nullable("integer", description="Tamanho do backup, em bytes. `null` até ficar pronto."),
                "error": {"oneOf": [{"type": "object", "required": ["code", "message"], "properties": {"code": {"type": "string", "enum": ["backup_failed"]}, "message": {"type": "string"}}}, {"type": "null"}], "description": "Quando `failed`: o backup não saiu (o automático tenta de novo em 1 hora)."},
                "createdAt": {"type": "string", "format": "date-time"},
                "finishedAt": nullable("string", format="date-time"),
                "expiresAt": {"type": "string", "format": "date-time", "description": "Até quando fica guardado (7 dias)."},
            },
        },
        "DatabaseBackupList": {
            "type": "object",
            "required": ["backups", "limit", "retentionDays", "isAvailable"],
            "properties": {
                "backups": {"type": "array", "items": ref("DatabaseBackup"), "description": "Do mais novo para o mais antigo."},
                "limit": {"type": "integer", "description": "Quantos backups prontos o banco guarda (7): quando um novo fica pronto, o mais antigo sai."},
                "retentionDays": {"type": "integer"},
                "isAvailable": {"type": "boolean", "description": "`false` quando o armazenamento dos backups está fora."},
            },
        },
        "Error": {
            "type": "object",
            "required": ["status", "code", "message"],
            "properties": {
                "status": {"type": "string", "const": "error"},
                "code": {"type": "string", "description": "Código fixo em inglês. Veja [Códigos de erro](/errors)."},
                "message": {"type": "string", "description": "Texto em português para mostrar a uma pessoa."},
            },
            "additionalProperties": True,
        },
    },
}

spec = {
    "openapi": "3.1.0",
    "info": {
        "title": "API da Cube Hosting",
        "version": "1.0.0",
        "description": "Hospede bots de Discord, sites e APIs em Node.js e Python: envie o .zip, inicie, pare, reinicie, leia logs e métricas, veja a análise das visitas dos sites, cuide das variáveis de ambiente, faça e baixe backups, volte para uma versão anterior, crie bancos de dados (PostgreSQL, MySQL, MongoDB e Redis), guarde arquivos privados no Blob, use um domínio seu nos sites e veja o uso do plano. Para agentes de IA, o servidor MCP da conta (`POST https://app.cubehosting.com.br/api/mcp`, JSON-RPC, com a mesma chave) está em https://docs.cubehosting.com.br/account-mcp.",
        "contact": {"name": "Cube Hosting", "url": "https://discord.gg/pv6D9tUsDV"},
    },
    "servers": [{"url": BASE}],
    "security": [{"bearerAuth": []}],
    "tags": [
        {"name": "Projetos"},
        {"name": "Controle"},
        {"name": "Logs e métricas"},
        {"name": "Análise"},
        {"name": "Variáveis de ambiente"},
        {"name": "Backups"},
        {"name": "Versões dos envios"},
        {"name": "Bancos de dados"},
        {"name": "Blob"},
        {"name": "Domínios"},
        {"name": "Templates"},
        {"name": "Avisos"},
        {"name": "Conta"},
    ],
    "paths": paths,
    "components": components,
}

with open(OUT, "w") as f:
    json.dump(spec, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("ok", len(paths))
