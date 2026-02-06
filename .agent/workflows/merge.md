---
description: Executa o merge das traduções (partes copy.json) para o JSON principal
---

# Workflow: Merge de Traduções

Execute o script de merge que realiza as seguintes etapas:

1. **Renomeia**: arquivos `*copy.json` → `*_pt.json`
2. **Merge**: junta todas as partes de cada tema em um arquivo `*_merged.json`
3. **Backup**: move arquivos processados para `bkp/`
4. **Regenera**: atualiza o `shin_college_data.json` com todos os temas merged

// turbo
## Comando de Execução

```sh
cd /Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data && python3 merge_translations.py
```

## Após o Merge

Verifique o resultado:

```sh
ls -la temasSeparados/*_merged.json | wc -l
```
