# STORY-01-01: Quick Wins — Encoding, Cores, Titulos e Confirmacoes
**Epic:** EPIC-01 Sprint Zero
**Status:** Draft
**Esforco estimado:** ~7h
**Prioridade:** P1
**Debitos resolvidos:** UX-HIGH-01, UX-HIGH-02, UX-MED-01, UX-CRIT-03, UX-MED-03, SEC-01

---

## Contexto

Seis debitos criticos e altos que podem ser resolvidos de forma independente, rapida e com impacto imediato no dia a dia da Luana. Nenhum deles tem dependencias de banco ou autenticacao.

---

## Acceptance Criteria

### AC-01 — Encoding UTF-8 no layout.html (UX-HIGH-01)
- [ ] Arquivo `layout.html` salvo como UTF-8 (sem BOM)
- [ ] Titulo da aba exibe "Cobrancas — Ineprotec / Matricula EAD" sem caracteres corrompidos
- [ ] Flask retorna `Content-Type: text/html; charset=utf-8` em todas as rotas

### AC-02 — Cores de categoria corrigidas em resultado.html (UX-HIGH-02 + UX-MED-01)
- [ ] Categoria "Novos Inadimplentes" usa `table-cat-novos` (azul claro #E3F2FD) — mantida
- [ ] Categoria "Regua" usa nova classe `table-cat-regua` (verde claro #E8F5E9)
- [ ] Categoria "Acima 30 Dias" usa `table-cat-b` (vermelho claro #FFEBEE) — mantida
- [ ] Badges de categoria unificados: classes semanticas `.badge-cat-novos`, `.badge-cat-regua`, `.badge-cat-acima30` definidas em layout.html
- [ ] wizard_whatsapp.html usa as mesmas classes semanticas (nao `bg-primary` direto)

### AC-03 — Confirmacao no link Limpar Sessao (UX-CRIT-03)
- [ ] Link `/limpar` convertido em form POST com `method="post"`
- [ ] Exibe `confirm("Tem certeza? Isso apagara a consolidacao atual.")` antes de executar
- [ ] OU: modal Bootstrap similar ao de "Limpar Base" em Configuracoes
- [ ] Operacao de limpeza so ocorre apos confirmacao explicita do usuario

### AC-04 — Titulo dinamico por pagina (UX-MED-03)
- [ ] `layout.html` contem `{% block title %}Cobrancas{% endblock %}` no `<title>`
- [ ] Cada template filho define seu titulo: ex. `{% block title %}Resultado | Cobrancas{% endblock %}`
- [ ] Paginas: Inicio | Resultado | Envio de Mensagens | Base | Configuracoes

### AC-05 — Secret key via variavel de ambiente (SEC-01)
- [ ] `app.py` ln 38: `app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))`
- [ ] Arquivo `.env.example` criado com `FLASK_SECRET_KEY=gere-uma-chave-aqui`
- [ ] `.env` adicionado ao `.gitignore` (se nao estiver)
- [ ] `ABRIR CONSOLIDADOR WEB.bat` ou `app.py` carrega `.env` antes de iniciar (via `python-dotenv` ou leitura manual)
- [ ] Chave gerada uma vez e persistida no `.env` local — nao regenerada a cada restart

---

## Arquivos a Modificar

- `06_APP/templates/layout.html` — encoding + titulo block + classes CSS badge
- `06_APP/templates/resultado.html` — classes de linha + badges
- `06_APP/templates/wizard_whatsapp.html` — classes de badge
- `06_APP/app.py` — secret_key via env
- `.env.example` — novo arquivo (template)
- `.gitignore` — adicionar .env

---

## Testes Esperados

- [ ] Abrir todas as 5 paginas: titulo correto na aba do browser
- [ ] resultado.html: Novos (azul), Regua (verde), Acima 30d (vermelho) visualmente distintos
- [ ] Clicar "Limpar Sessao": dialogo de confirmacao aparece; cancelar nao limpa; confirmar limpa
- [ ] Reiniciar o servidor: sessoes existentes continuam validas (secret_key persistida no .env)

---

*STORY-01-01 — EPIC-01 Sprint Zero — MAT-INE Inadimplencia 2026*
