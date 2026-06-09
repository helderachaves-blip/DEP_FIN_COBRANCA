# 📚 Guia de Boas Práticas para Commits no Git

Este guia rápido reúne as melhores práticas de mercado para escrever mensagens de commit claras, organizadas e profissionais, ajudando na manutenção do projeto e no histórico de alterações.

---

## 🎯 O Padrão: Conventional Commits

O padrão **Conventional Commits** utiliza prefixos no título da mensagem para identificar instantaneamente a intenção da alteração.

### Estrutura básica:
```text
tipo(escopo opcional): breve descrição em letras minúsculas
```

---

## 🏷️ Tipos de Commits Comuns

Use estes prefixos dependendo do que foi feito:

| Prefixo | Significado | Exemplo de Uso |
| :--- | :--- | :--- |
| **`feat`** | Nova funcionalidade (Feature) | `feat: adiciona botao de gerar relatorio xlsx` |
| **`fix`** | Correção de bug (Bug fix) | `fix: resolve falha na leitura do cpf com digito zero` |
| **`docs`** | Alteração em documentações (Docs) | `docs: adiciona manual de boas praticas do git` |
| **`style`** | Estética, espaçamento, CSS, formatação | `style: ajusta alinhamento dos cards na home` |
| **`refactor`**| Melhoria no código sem alterar o resultado | `refactor: otimiza query de busca de alunos` |
| **`chore`** | Atualizações, configs, pacotes (`.gitignore`, etc) | `chore: adiciona dependencias no requirements.txt` |
| **`test`** | Criação ou ajuste de testes automatizados | `test: adiciona teste unitario para login` |

---

## 📝 Commits Detalhados (Título + Descrição)

Para commits maiores que alteram múltiplos componentes, use um **Título Curto** seguido de uma **Lista Detalhada**:

### Exemplo de Mensagem:
```text
feat(app): integra sistema com envio de whatsapp

- Adiciona suporte a API oficial do WhatsApp Business
- Cria modal de configuracao de credenciais no frontend
- Salva status do envio de forma persistente no banco de dados
```

### Como fazer:
*   **No GitHub Desktop:** Digite o título curto no campo **Summary** e a lista detalhada no campo **Description**.
*   **No Terminal:** Utilize múltiplos parâmetros `-m`:
    ```bash
    git commit -m "feat(app): integra sistema com envio de whatsapp" -m "- Adiciona suporte a API oficial" -m "- Cria modal de configuracao no frontend"
    ```

---

## 🏆 As 3 Regras de Ouro

1. **Foque no "Porquê" e no "O quê" (Não no "Como"):** O código alterado já mostra *como* você fez. O commit deve explicar a motivação e o impacto da alteração.
2. **Seja Breve no Título:** A primeira linha do commit (título) deve ter preferencialmente **menos de 50 caracteres**.
3. **Use Verbos na 3ª Pessoa do Singular (ou Imperativo):** Mantenha o padrão gramatical (ex: `adiciona`, `corrige`, `atualiza` em vez de "adicionei" ou "corrigido").

---
**Status:** Ativo  
**Última atualização:** Junho / 2026
