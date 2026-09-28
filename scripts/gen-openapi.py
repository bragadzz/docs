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
    "memoryMb": 256,
    "port": None,
    "subdomain": None,
    "url": None,
    "status": "running",
    "error": None,
    "hasAutoRestart": True,
    "consecutiveCrashes": 0,
    "lastExit": None,
    "usage": {"memoryMb": 83, "cpuPercent": 1.2, "networkInBps": 1200, "networkOutBps": 300},
    "startedAt": "2026-09-26T18:01:05.000Z",
    "createdAt": "2026-09-26T18:00:00.000Z",
    "updatedAt": "2026-09-26T18:01:10.000Z",
}
SITE_EXAMPLE = {
    **PROJECT_EXAMPLE,
    "id": "01J8Z4B2QK7M3V9T0XW5R6N8CD",
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

# Erros comuns
E_KEY = ("invalid_api_key", err("invalid_api_key", 'Chave de API inválida ou revogada. Confira o cabeçalho "Authorization: Bearer <chave>" ou crie outra em Chaves de API no painel.'))
E_PERM = ("insufficient_permission", err("insufficient_permission", "Esta chave é só de leitura. Para enviar, iniciar, parar, reiniciar ou mexer nas variáveis, crie uma chave de leitura e escrita no painel."))
E_404 = ("not_found", err("not_found", "Projeto não encontrado."))
E_RATE = ("rate_limit_exceeded", err("rate_limit_exceeded", "A sua conta passou do limite da API do plano Free: 10 pedidos por minuto. Espere 42 s e tente de novo."))
E_MANY = ("too_many_requests", err("too_many_requests", "Muitas requisições seguidas. Espere alguns segundos e tente de novo."))
E_ATT = ("too_many_attempts", err("too_many_attempts", "Muitas tentativas. Tente de novo em 15 minutos."))
E_BUSY = ("project_busy", err("project_busy", "O projeto está sendo preparado ou já tem outra ação em andamento. Espere terminar."))
E_SUSP = ("account_suspended", err("account_suspended", "Sua conta está suspensa porque o Pix da renovação não foi pago, então os projetos ficam parados. Pague em Plano e cobrança: a conta volta na hora, e o que estava no ar sobe sozinho."))
E_BETA = ("beta_ending", err("beta_ending", "Seu beta terminou e a conta está voltando ao plano Free. Espere alguns minutos e tente de novo."))
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
            "A configuração vem do `cube.json` na raiz do `.zip`. Se o formulário trouxer `language` e `command`, o formulário vale "
            "e o `cube.json` é ignorado. Um envio a cada 3 segundos por conta."
        ),
        "tags": ["Projetos"],
        "requestBody": {
            "required": True,
            "content": {"multipart/form-data": {
                "schema": {
                    "type": "object",
                    "required": ["file"],
                    "properties": {
                        "file": {"type": "string", "format": "binary", "description": "O `.zip` com o código. Até 5 MB no Free e 10 MB nos planos pagos."},
                        "start": {"type": "string", "enum": ["true", "false"], "default": "false", "description": "`true` inicia o projeto assim que a instalação terminar."},
                        "name": {"type": "string", "minLength": 1, "maxLength": 40, "description": "Nome do projeto. Vale se o `cube.json` não tiver `name`; sem nenhum, vira o nome do arquivo."},
                        "type": {"type": "string", "enum": ["bot", "site"], "description": "Mesmo significado da chave do `cube.json`."},
                        "language": {"type": "string", "enum": ["node", "python"], "description": "Com `language` e `command`, o formulário vale e o `cube.json` é ignorado."},
                        "version": {"type": "string", "description": "`20`, `22` ou `24` (Node.js); `3.11` ou `3.12` (Python)."},
                        "command": {"type": "string", "maxLength": 500, "description": "Comando de início, numa linha só."},
                        "memoryMb": {"type": "integer", "minimum": 100, "description": "Memória em MB. Mínimo 100 (bot) ou 512 (site)."},
                        "port": {"type": "integer", "minimum": 1024, "maximum": 65535, "description": "Só site. Padrão 8080."},
                        "subdomain": {"type": "string", "description": "Só site. Sem ele, a Cube gera um."},
                        "build": {"type": "string", "maxLength": 500, "description": "Comando de build. Ausente = automático; vazio = sem build."},
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
                    "schema": {"type": "object", "required": ["project"], "properties": {"project": ref("Project")}},
                    "example": {"project": INSTALLING},
                }},
            },
            "401": R401,
            "403": resp("A chave é só de leitura, ou o plano não comporta mais este projeto.", [
                E_PERM,
                ("project_limit_reached", err("project_limit_reached", "O plano Free permite até 1 bot. Exclua um projeto ou mude de plano.", limit=1)),
                ("site_not_allowed", err("site_not_allowed", "O plano Free não inclui sites. Mude para um plano pago para hospedar sites e APIs.")),
                ("site_limit_reached", err("site_limit_reached", "O plano Block permite até 2 sites. Exclua um site ou mude de plano.", limit=2)),
            ]),
            "409": resp("Conflito com o estado da conta.", [
                ("subdomain_taken", err("subdomain_taken", "Este subdomínio já é de outro site. Escolha outro.", field="subdomain")),
                ("no_capacity", err("no_capacity", "Nossos servidores estão cheios agora e não dá para liberar mais memória. Tente de novo mais tarde: estamos abrindo mais espaço.")),
                E_SUSP, E_BETA,
            ]),
            "413": ZIP_413,
            "422": resp("O .zip ou a configuração foram recusados.", [
                ("invalid_zip", err("invalid_zip", "O arquivo não é um zip válido (corrompido, protegido por senha ou vazio). Gere o zip de novo e envie.")),
                ("unsafe_zip", err("unsafe_zip", "O zip tem atalhos (links) para outros arquivos, e eles não são aceitos. Troque os atalhos pelos arquivos de verdade e envie de novo.", reason="link")),
                ("missing_config", err("missing_config", "O zip não tem cube.json. Informe a linguagem e o comando de início do bot.")),
                ("invalid_config", err("invalid_config", 'O cube.json tem um campo que não existe: "memory". Confira se não é erro de digitação.', field="memory")),
                ("unsupported_language", err("unsupported_language", "Por enquanto aceitamos Node.js (versões 20, 22 e 24) e Python (3.11 e 3.12).", supported={"node": ["20", "22", "24"], "python": ["3.11", "3.12"]})),
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
            "409": resp("O projeto está ocupado ou a conta não pode instalar agora.", [E_BUSY, E_SUSP, E_BETA]),
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
        responses["409"] = resp("O projeto está ocupado, a instalação falhou ou a conta não pode iniciar agora.", [
            E_BUSY,
            ("install_pending", err("install_pending", "A instalação das dependências deste projeto não terminou. Envie o projeto de novo para instalar.")),
            E_SUSP, E_BETA,
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
            "últimas `lines` linhas, depois as novas, ao vivo. O stream fica aberto até você fechar.\n\n"
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
            "400": resp("Parâmetro fora do formato.", [("invalid_request", err("invalid_request", "Use lines de 0 a 1000 e source app ou build."))]),
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

# Backups (cube-hosting#31): listar, fazer e baixar pela chave; restaurar, excluir e o diário só no painel.
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
            "409": resp("Já tem um backup em andamento, o projeto ainda está sendo criado, ou a conta está suspensa.", [E_BK_BUSY, E_BUSY, E_SUSP, E_BETA]),
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
            "com outra conta, responde `404`. Só backups `ready`."
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
            "Baixa o backup em `.zip` pelo link do [Pedir o link de download](/api-reference/backups/download-link), com a mesma chave. "
            "O nome do arquivo vem no `Content-Disposition` (`<projeto>-backup-<data>.zip`)."
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
            "403": resp("O link venceu (5 minutos) ou foi mexido.", [("download_expired", err("download_expired", "O link de download venceu ou não é desta Conta. Peça o download de novo pelo painel."))]),
            "404": R404_BACKUP,
            "409": resp("O backup ainda não está pronto ou não deu certo.", [E_BK_READY]),
            "429": R429,
            "503": resp("O armazenamento dos backups não respondeu.", [E_BK_503]),
        },
    },
}

nullable = lambda t, **kw: {"type": [t, "null"], **kw}

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
            "required": ["id", "name", "description", "type", "language", "version", "entry", "command", "memoryMb", "port", "subdomain", "url", "status", "error", "hasAutoRestart", "consecutiveCrashes", "lastExit", "usage", "startedAt", "createdAt", "updatedAt"],
            "properties": {
                "id": {"type": "string", "description": "ID do projeto, 26 caracteres."},
                "name": {"type": "string", "maxLength": 40, "description": "Nome do projeto."},
                "description": {"type": "string", "maxLength": 200, "description": "Descrição do painel. `\"\"` quando não tem."},
                "type": {"type": "string", "enum": ["bot", "site"]},
                "language": {"type": "string", "enum": ["node", "python"]},
                "version": {"type": "string", "description": "`20`, `22` ou `24` (Node.js); `3.11` ou `3.12` (Python)."},
                "entry": nullable("string", description="Arquivo principal: o arquivo que o comando roda, relativo à raiz do projeto (como `index.js` ou `src/bot.py`). Vem do `command` quando ele é só `node <arquivo>` ou `python <arquivo>`, e muda em Configurações › Geral. `null` com um comando próprio, como `npm start`."),
                "command": {"type": "string", "description": "Comando de início, o que de fato roda. Quando é `node <entry>` ou `python <entry>`, o painel mostra o campo vazio (vazio = roda o arquivo principal)."},
                "memoryMb": {"type": "integer", "description": "Memória reservada, em MB. É também o teto do processo."},
                "port": nullable("integer", description="Só site: a porta em que o app escuta (também na variável `PORT`). `null` em bot."),
                "subdomain": nullable("string", description="Só site: o nome em `nome.cubehost.dev`. `null` em bot."),
                "url": nullable("string", format="uri", description="Só site: o endereço público com HTTPS. `null` em bot."),
                "status": ref("ProjectStatus"),
                "error": {"oneOf": [ref("ProjectError"), {"type": "null"}], "description": "O motivo, quando `status` é `error` ou `crash_loop`."},
                "hasAutoRestart": {"type": "boolean", "description": "`true` nos planos pagos: o projeto volta sozinho se cair."},
                "consecutiveCrashes": {"type": "integer", "description": "Quedas seguidas desde a última vez que rodou 60 segundos sem cair. Com 5, o projeto vai para `crash_loop`."},
                "lastExit": {"oneOf": [ref("LastExit"), {"type": "null"}], "description": "A última vez que o processo terminou."},
                "usage": {"oneOf": [ref("Usage"), {"type": "null"}], "description": "O uso de agora. Só com `status` `running`."},
                "startedAt": nullable("string", format="date-time", description="Quando o processo subiu (o \"tempo no ar\" do painel). Só com `running`."),
                "createdAt": {"type": "string", "format": "date-time"},
                "updatedAt": {"type": "string", "format": "date-time"},
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
                "code": {"type": "string", "enum": ["install_failed", "install_timeout", "install_out_of_memory", "install_interrupted", "start_failed", "process_exited", "crash_loop"], "description": "Veja [Estados de erro do projeto](/errors#estados-de-erro-do-projeto)."},
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
        "description": "Hospede bots de Discord, sites e APIs em Node.js e Python: envie o .zip, inicie, pare, reinicie, leia logs e métricas, cuide das variáveis de ambiente e faça e baixe backups.",
        "contact": {"name": "Cube Hosting", "url": "https://discord.gg/pv6D9tUsDV"},
    },
    "servers": [{"url": BASE}],
    "security": [{"bearerAuth": []}],
    "tags": [
        {"name": "Projetos"},
        {"name": "Controle"},
        {"name": "Logs e métricas"},
        {"name": "Variáveis de ambiente"},
        {"name": "Backups"},
    ],
    "paths": paths,
    "components": components,
}

with open(OUT, "w") as f:
    json.dump(spec, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("ok", len(paths))
