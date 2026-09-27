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

print('ok')
