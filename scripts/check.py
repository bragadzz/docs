#!/usr/bin/env python3
"""Conferências da docs: `python3 scripts/check.py` confere o repositório; com `--live`, também o site no ar."""
import json
import sys
import urllib.request

SITE = 'https://docs.cubehosting.com.br'

docs = json.load(open('docs.json'))
# O playground interativo manda a chave do cliente pelo servidor do fornecedor da docs, fora da Cube.
assert docs['api']['playground']['display'] == 'simple', 'api.playground.display precisa ser "simple"'
assert open('llms.txt').readline().strip() == '# Cube Hosting', 'llms.txt precisa começar com "# Cube Hosting"'

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
    # E o MCP da documentação precisa responder a um cliente MCP de verdade (initialize).
    inicio = {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {
        'protocolVersion': '2025-06-18', 'capabilities': {}, 'clientInfo': {'name': 'cube-docs-check', 'version': '1'}}}
    req = urllib.request.Request(SITE + '/mcp', data=json.dumps(inicio).encode(), headers={
        'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream', 'User-Agent': 'cube-docs-check'})
    assert '"serverInfo"' in urllib.request.urlopen(req, timeout=30).read().decode(), '/mcp não respondeu ao initialize'

print('ok')
