## 1. Inicialização e Configuração
```
dvc init
```

- **O que faz:** Inicializa o DVC no seu projeto. Cria a pasta oculta .dvc/ que guarda as configurações internas.
- **Quando usar:** Apenas uma vez no início do projeto (logo após ter feito o git init).
---
```
dvc remote add -d <nome_do_remote> <url_ou_caminho>
```

- **O que faz:** Ensina o DVC onde ele deve guardar os arquivos pesados (AWS S3, Google Drive, pasta local, etc.). O -d define este local como o padrão.
- **Quando usar:** Quando for configurar o seu servidor de armazenamento pela primeira vez.
Use `dvc remote add -d localstorage /tmp/dvc-storage` para definir um armazenamento local.

## 2. Versionamento de Dados (O feijão com arroz)

```
dvc add <arquivo_ou_pasta>
```

- **O que faz:** Diz ao DVC para começar a rastrear um arquivo grande (ex: dvc add data/dataset.csv). Ele move o arquivo para o cache, cria um arquivo leve de controle (dataset.csv.dvc) e adiciona o arquivo original ao .gitignore automaticamente.
- **Quando usar:** Sempre que trouxer um novo conjunto de dados bruto ou modelo final para o projeto.
---
```bash
dvc push
```

- **O que faz:** Faz o upload dos arquivos pesados que estão no seu computador para o armazenamento remoto configurado.
- **Quando usar:** Depois de fazer um dvc add ou dvc repro, antes de partilhar o seu código (como um complemento ao git push).
---

```bash
dvc pull
```

- **O que faz:** Faz o download dos arquivos pesados do armazenamento remoto para o seu computador, baseando-se nos arquivos .dvc e dvc.lock atuais.
- **Quando usar:** Quando clonar o repositório em outra máquina ou depois de fazer um git pull com atualizações dos seus colegas.
---
```bash
dvc checkout
```
**O que faz:** Sincroniza os seus dados reais (no seu disco) para que fiquem exatamente iguais à versão registada nos arquivos .dvc ou dvc.lock do commit atual.
Quando usar: Muito útil quando você troca de branch no Git (ex: git checkout branch-antiga). O Git muda o código, e o dvc checkout garante que os dados mudam para a versão correspondente àquela época.

## 3. Pipelines e Execução

```
dvc stage add -n <nome_estagio> -d <dependencias> -o <saidas> <comando>
```

- **O que faz:** É a forma via linha de comando de criar um bloco dentro do arquivo dvc.yaml. (Até a versão 2.0 do DVC, usava-se dvc run).
- **Quando usar:** Quando quiser criar uma etapa do pipeline de forma programática em vez de escrever o dvc.yaml à mão.
---

```
dvc repro
```

- **O que faz:** Lê o arquivo dvc.yaml e reproduz as etapas do pipeline. Ele é inteligente: só executa os scripts cujos dados ou código originais foram alterados.
- **Quando usar:** Sempre que alterar o código de tratamento ou tiver dados novos e quiser gerar um novo resultado (atualizando o dvc.lock).

## 4. Monitoramento e Informações

```
dvc status
```

- **O que faz:** Mostra as diferenças entre os dados atuais na sua pasta e o que está salvo nos arquivos do DVC. Diz-lhe o que mudou e precisa de ser reprocessado ou enviado.
- **Quando usar:** Sempre que estiver em dúvida se esqueceu de dar um dvc push ou rodar um dvc repro. Funciona como o git status, mas para dados.

## Fluxo Clássico em 4 passos rápidos:
1. Altera dados ou código.
2. `dvc repro` (processa e gera o novo dvc.lock).
3. `git add dvc.lock && git commit -m "atualiza dados"` (guarda a versão no Git).
4. `dvc push && git push` (envia os dados para o repositório de dados e o código para o GitHub).