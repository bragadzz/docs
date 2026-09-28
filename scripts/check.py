#!/usr/bin/env python3
"""Conferências da docs: `python3 scripts/check.py` confere o repositório; com `--live`, também o site no ar."""
import glob
import json
import re
import sys
import time
import urllib.error
import urllib.request

SITE = 'https://docs.cubehosting.com.br'

docs = json.load(open('docs.json'))
# O playground interativo manda a chave do cliente pelo servidor do fornecedor da docs, fora da Cube.
assert docs['api']['playground']['display'] == 'simple', 'api.playground.display precisa ser "simple"'
assert open('llms.txt').readline().strip() == '# Cube Hosting', 'llms.txt precisa começar com "# Cube Hosting"'


def pages(node):
    """Todas as páginas da navegação do docs.json."""
    if isinstance(node, list):
        for item in node:
            yield from pages(item)
    elif isinstance(node, dict):
        for key, value in node.items():
            if key == 'pages':
                for page in value:
                    yield from [page] if isinstance(page, str) else pages(page)
            elif isinstance(value, (list, dict)):
                yield from pages(value)


def missing_pages(llms_full):
    """Páginas do docs.json sem a linha "Source: <endereço>" no llms-full.txt."""
    sources = {line.removeprefix(f'Source: {SITE}/') for line in llms_full.splitlines() if line.startswith('Source: ')}
    return sorted(set(pages(docs['navigation'])) - sources)


def route_errors(openapi, method, path):
    """{code: {status}} que a rota devolve no openapi.json (os exemplos de cada resposta de erro)."""
    found = {}
    for status, response in openapi['paths'][path][method.lower()]['responses'].items():
        if '$ref' in response:
            response = openapi['components']['responses'][response['$ref'].split('/')[-1]]
        for code in response.get('content', {}).get('application/json', {}).get('examples', {}):
            found.setdefault(code, set()).add(status)
    return found


# "Erros comuns" de cada rota (cube-hosting#37): todo código da tabela a rota devolve de verdade,
# com o mesmo HTTP, e o link leva à âncora dele em /errors.
openapi = json.load(open('api-reference/openapi.json'))
documented = set(re.findall(r'<ResponseField name="([a-z_]+)"', open('errors.mdx').read()))
for page in sorted(glob.glob('api-reference/*/*.mdx')):
    text = open(page).read()
    method, path = re.search(r'^openapi: "(\w+) ([^"]+)"', text, re.M).groups()
    assert '## Erros comuns' in text, f'{page} sem a tabela "Erros comuns"'
    errors = route_errors(openapi, method, path)
    rows = re.findall(r'^\| \[`([a-z_]+)`\]\(/errors#param-([a-z-]+)\) \| ([^|]+) \|', text, re.M)
    assert rows, f'{page}: tabela "Erros comuns" vazia'
    for code, anchor, http in rows:
        assert anchor == code.replace('_', '-'), f'{page}: {code} aponta para #param-{anchor}'
        assert code in documented, f'{page}: {code} não está em errors.mdx'
        assert code in errors, f'{page}: {method} {path} não devolve {code} no openapi.json'
        statuses = set(re.findall(r'\d{3}', http))
        assert statuses == errors[code], f'{page}: {code} com HTTP {http.strip()}, o openapi.json diz {sorted(errors[code])}'

PAGES = set(pages(docs['navigation']))
assert {'index', 'tools', 'cli', 'github-actions', 'hosting/backups', 'errors'} <= PAGES, 'a navegação do docs.json não foi lida inteira'
assert missing_pages(f'Source: {SITE}/tools') == sorted(PAGES - {'tools'})

if '--live' in sys.argv:
    def get(path):
        req = urllib.request.Request(SITE + path, headers={'User-Agent': 'cube-docs-check'})
        return urllib.request.urlopen(req, timeout=30).read().decode()

    # Sem parâmetro na URL: é o que o cache entrega para quem chega.
    assert get('/llms.txt').splitlines()[0] == '# Cube Hosting', '/llms.txt no ar ainda não é o da Cube'
    for path in ('/', '/llms-full.txt'):
        assert 'Starter Kit' not in get(path), f'{path} no ar ainda mostra o Starter Kit'

    # A página Ferramentas do painel (cube-hosting#58) lista estes endereços: todos precisam abrir.
    for path in ('/api-reference/openapi.json', '/quickstart.md', '/tools'):
        get(path)
    # A CLI (cube-hosting#42) instala pelo npm, e o .tgz do site segue como alternativa sem o registro.
    req = urllib.request.Request('https://registry.npmjs.org/@cubehosting%2fcli', headers={'User-Agent': 'cube-docs-check'})
    assert json.load(urllib.request.urlopen(req, timeout=30))['dist-tags']['latest'], '@cubehosting/cli fora do npm'
    for tgz in ('https://cubehosting.com.br/cli/latest.tgz', 'https://cubehosting.com.br/cli/cube-cli-0.1.0.tgz',
                'https://cubehosting.com.br/cli/cube-cli-0.1.1.tgz', 'https://cubehosting.com.br/cli/cube-cli-0.1.2.tgz',
                'https://cubehosting.com.br/cli/cube-cli-0.2.0.tgz', 'https://cubehosting.com.br/cli/cube-cli-0.2.1.tgz',
                'https://cubehosting.com.br/cli/cube-cli-0.2.2.tgz'):
        req = urllib.request.Request(tgz, headers={'User-Agent': 'cube-docs-check'})
        assert urllib.request.urlopen(req, timeout=30).read(2) == b'\x1f\x8b', f'{tgz} não é um .tgz'
    for path in ('/cli', '/github-actions', '/api-reference/account/usage', '/account-mcp', '/hosting/blob'):
        get(path)
    # O MCP da conta (cube-hosting#45), que a página account-mcp ensina a conectar: sem chave é 401
    # invalid_api_key (nunca a página do painel), e o GET, sem stream do servidor, é 405.
    conta = 'https://app.cubehosting.com.br/api/mcp'
    for method, body, status in (('POST', b'{}', 401), ('GET', None, 405)):
        req = urllib.request.Request(conta, data=body, method=method, headers={
            'Content-Type': 'application/json', 'User-Agent': 'cube-docs-check'})
        try:
            urllib.request.urlopen(req, timeout=30)
            raise SystemExit(f'{method} {conta} respondeu 200 sem chave')
        except urllib.error.HTTPError as e:
            assert e.code == status, f'{method} {conta} respondeu {e.code}, esperado {status}'
            if status == 401:
                assert json.load(e)['code'] == 'invalid_api_key', f'{conta} sem chave não deu invalid_api_key'
    # E o MCP da documentação precisa responder a um cliente MCP de verdade (initialize).
    inicio = {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {
        'protocolVersion': '2025-06-18', 'capabilities': {}, 'clientInfo': {'name': 'cube-docs-check', 'version': '1'}}}
    req = urllib.request.Request(SITE + '/mcp', data=json.dumps(inicio).encode(), headers={
        'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream', 'User-Agent': 'cube-docs-check'})
    assert '"serverInfo"' in urllib.request.urlopen(req, timeout=30).read().decode(), '/mcp não respondeu ao initialize'

    # Por último: o /llms-full.txt que o agente recebe (sem parâmetro) precisa ter todas as páginas. Ele fica
    # até 1 dia no cache da docs e publicar não o renova, então só o 200 não prova que está em dia.
    req = urllib.request.Request(SITE + '/llms-full.txt', headers={'User-Agent': 'cube-docs-check'})
    with urllib.request.urlopen(req, timeout=30) as res:
        age, served = int(res.headers.get('Age') or 0), res.read().decode()
    missing = missing_pages(served)
    if missing:
        at_origin = missing_pages(get(f'/llms-full.txt?rev={time.time_ns()}'))
        where = ('a origem também está sem elas: a docs não gerou o arquivo' if at_origin else
                 f'a origem já tem todas; o cache vence em até {max(0, 86400 - age) // 3600} h')
        raise SystemExit(f'/llms-full.txt no ar ainda sem {", ".join(missing)} ({where})')

print('ok')
