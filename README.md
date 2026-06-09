# Configuração do Amazon S3 como Remote Storage no DVC

Este guia fornece o passo a passo completo para configurar um bucket do Amazon S3 como armazenamento remoto para o **Data Version Control (DVC)**. O fluxo cobre desde a criação de recursos na AWS até a autenticação no macOS e inicialização do plugin no DVC.

---

## Pré-requisitos
* Repositório Git inicializado (`git init`)
* DVC instalado no projeto (`dvc init`)

---

## Passo 1: Configuração no Console da AWS

### 1.1. Criação da Conta e do Bucket S3
1. Acesse o console da [AWS (Amazon Web Services)](https://aws.amazon.com/) e faça login.
2. No painel de serviços, busque por **S3**.
3. Clique em **Criar bucket** (Create bucket).
4. Insira um nome globalmente exclusivo para o seu bucket (ex: `meu-projeto-dvc-storage`).
5. Escolha a região AWS mais próxima (ex: `sa-east-1` - São Paulo) e mantenha as demais configurações padrão.
6. Clique em **Criar bucket** no final da página.

### 1.2. Criação do Usuário IAM e Permissões
Para que o DVC se conecte com segurança, criamos um usuário programático no IAM (Identity and Access Management):
1. No console da AWS, busque por **IAM**.
2. No menu lateral esquerdo, clique em **Usuários** (Users) e depois em **Criar usuário** (Create user).
3. Defina um nome para o usuário (ex: `usuario-dvc-projeto`).
4. Na tela de permissões, selecione **Anexar políticas diretamente** (Attach policies directly).
5. Busque por `AmazonS3FullAccess` (ou crie uma política personalizada limitando o acesso apenas ao seu bucket específico) e marque a caixa de seleção.
6. Avance e clique em **Criar usuário**.

### 1.3. Geração de Credenciais de Acesso
1. Na lista de usuários do IAM, clique no usuário que você acabou de criar.
2. Vá até a aba **Credenciais de segurança** (Security credentials).
3. Desça até a seção **Chaves de acesso** (Access keys) e clique em **Criar chave de acesso** (Create access key).
4. Escolha a opção **Interface da Linha de Comando (CLI)**, marque o aviso de conformidade e avance.
5. O console exibirá duas chaves importantes:
   * **Access Key ID (ID da chave de acesso)**
   * **Secret Access Key (Chave de acesso secreta)**
6. **IMPORTANTE:** Baixe o arquivo `.csv` ou copie as chaves para um local seguro. A chave secreta não será exibida novamente.

---

## Passo 2: Instalação e Configuração da AWS CLI (macOS)

Com as credenciais geradas, precisamos configurar a interface de linha de comando da AWS no seu sistema operacional.

### 2.1. Instalação via Terminal
Utilize o Homebrew para instalar a AWS CLI no macOS:
```bash
brew install awscli

aws --version
```

### 2.2. Método de Autenticação via Variáveis de Ambiente
Em vez de salvar as credenciais em um arquivo global fixo, exportaremos as chaves diretamente no terminal como variáveis de ambiente temporárias ou na configuração do seu terminal (.zshrc ou .bash_profile):

```bash
export AWS_ACCESS_KEY_ID="SEU_ACCESS_KEY_ID_AQUI"
export AWS_SECRET_ACCESS_KEY="SUA_SECRET_ACCESS_KEY_AQUI"
export AWS_DEFAULT_REGION="sa-east-1" # Região escolhida na criação do bucket
```

## Passo 3: Preparação e Configuração do DVC
### 3.1. Instalação do Plugin dvc-s3
O DVC precisa de uma extensão separada para se comunicar com o protocolo do Amazon S3. No ambiente virtual do seu projeto, execute:
```Bash
pip install dvc-s3
```

### 3.2. Configurando o Storage Remoto no DVC
Agora, associe o bucket criado ao repositório DVC do seu projeto local:

```bash
# 1. Adiciona o remote apontando para a URI do S3
dvc remote add -d meu-s3-remote s3://nome-do-seu-bucket

# 2. Salva a alteração da estrutura do DVC no repositório Git
git add .dvc/config
git commit -m "Configura Amazon S3 como remote storage padrão"
```

### 3.3. Testando o Pipeline e Sincronização
Para garantir que tudo está funcionando perfeitamente, adicione um arquivo pesado de teste e envie para a nuvem:
```bash
# Rastreia um arquivo de dados ou modelo
dvc add data/dados.csv

# Envia o arquivo físico para o bucket S3 da Amazon
dvc push
```

# Configuração do Google Drive como Remote Storage no DVC

Este guia fornece o passo a passo completo para configurar uma pasta do **Google Drive (GDrive)** como armazenamento remoto para o **Data Version Control (DVC)**. Devido às políticas recentes de segurança do Google, a melhor prática recomendada é utilizar um projeto personalizado no Google Cloud Platform (GCP) para evitar limites de taxa e erros de autenticação.

---

## Pré-requisitos
* Repositório Git inicializado (`git init`)
* DVC instalado no projeto (`dvc init`)
* Uma conta Google (Gmail ou Google Workspace)

---

## Passo 1: Configuração no Google Cloud Platform (GCP)

Para que o DVC acesse o seu Google Drive de forma segura e automatizada, precisamos criar um "aplicativo" dentro do console de desenvolvedor do Google.

### 1.1. Criação do Projeto e Ativação da API
1. Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2. Faça login com a sua conta Google.
3. No topo da página, clique no seletor de projetos e selecione **Novo Projeto** (New Project). Defina um nome (ex: `DVC Storage Projeto`) e clique em **Criar**.
4. Certifique-se de que o novo projeto está selecionado.
5. No menu lateral esquerdo, vá em **APIs e Serviços > Biblioteca** (APIs & Services > Library).
6. Pesquise por **Google Drive API**, clique sobre ela e depois clique no botão **Ativar** (Enable).

### 1.2. Configuração da Tela de Consentimento OAuth (Evitando a Publicação)
Como o nosso aplicativo será de uso pessoal/interno, não precisamos passar pelo processo burocrático de homologação e publicação do Google. Podemos mantê-lo em modo de "Teste", desde que configuremos nosso e-mail como autorizado.

1. No menu lateral esquerdo, vá em **APIs e Serviços > Tela de consentimento OAuth** (OAuth consent screen).
2. Selecione o tipo de usuário como **Externo** (External) e clique em **Criar**.
3. Preencha as informações obrigatórias básicas:
   * **Nome do aplicativo:** `Meu DVC Storage`
   * **E-mail de suporte ao usuário:** Seu próprio e-mail.
   * **Dados de contato do desenvolvedor:** Seu próprio e-mail.
4. Clique em **Salvar e Continuar** nas próximas telas até chegar na seção **Usuários de teste** (Test users).
5. **PASSO CRUCIAL:** Na seção de Usuários de Teste, clique em **Add Users** (Adicionar usuários) e insira exatamente o e-mail da conta Google que você usará para acessar o Drive. Se esquecer este passo, você receberá o *Erro 403: access_denied*.
6. Salve e conclua o fluxo.

### 1.3. Criação das Credenciais de Acesso
1. No menu lateral, clique em **Credenciais** (Credentials).
2. No topo da tela, clique em **+ Criar Credenciais** (+ Create Credentials) e escolha a opção **ID do cliente OAuth** (OAuth client ID).
3. No campo *Tipo de aplicativo* (Application type), selecione **App para computador** (Desktop app).
4. Dê um nome descritivo (ex: `DVC CLI Token`) e clique em **Criar**.
5. O console exibirá duas chaves fundamentais. Copie e guarde-as:
   * **ID do cliente** (Client ID)
   * **Chave secreta do cliente** (Client Secret)

---

## Passo 2: Configuração no Google Drive

1. Acesse o seu Google Drive convencional pelo navegador.
2. Crie uma pasta vazia onde o DVC armazenará os arquivos (ex: `dvc_remote_storage`).
3. Entre na pasta criada e olhe para a barra de endereços (URL) do seu navegador. Ela será parecida com isto:
   `https://drive.google.com/drive/folders/1P5eQTvb5-T85wj4bomUXG3f8yqOjy-ta`
4. Copie **apenas a sequência de caracteres que fica no final da URL** (após o `folders/`). Esse código é o **ID da sua pasta** (no exemplo acima, seria `1P5eQTvb5-T85wj4bomUXG3f8yqOjy-ta`).

---

## Passo 3: Preparação e Configuração do DVC

### 3.1. Instalação do Driver `dvc-gdrive`
Por padrão, o DVC não vem com os módulos de nuvem instalados. No terminal do seu projeto (e com o ambiente virtual ativado), execute o comando para instalar a extensão do Google Drive:

```bash
pip install "dvc-gdrive"
```
### 3.2. Configurando o Storage Remoto no DVC

```bash
# 1. Adiciona o remote com a URL contendo o ID da sua pasta do Drive
dvc remote add -d meu-gdrive gdrive://SEU_ID_DA_PASTA_AQUI

# 2. Configura o Client ID personalizado gerado no GCP
dvc remote modify meu-gdrive gdrive_client_id "SEU_ID_DO_CLIENTE_AQUI"

# 3. Configura a Chave Secreta personalizada gerada no GCP
dvc remote modify meu-gdrive gdrive_client_secret "SUA_CHAVE_SECRETA_AQUI"

# 4. Salva as definições de estrutura no Git
git add .dvc/config
git commit -m "Configura Google Drive personalizado como remote storage"
```

## Problemas de autentificação

Caso a aplicação esteja em teste, após 7 dias, o token OAuth vai expirar e um erro como o seguinte pode ser visto
ao se executar alguma ação do DVC que exige a integração com a api do Google Drive.
```bash
ERROR: unexpected error - Failed to authenticate GDrive: Access token refresh failed: invalid_grant: Bad Request   
```
Duas formas de contornar:
1. Acesso o painel do Google Cloud e publicar o app;
2. Excluir o default.json que contém o token inválido e executar novamente o login via web.
O local do arquivo pode variar a depender do SO:
   - **Linux**: `~/.cache/pydrive2fs/://googleusercontent.com`
   - **macOS**: `~/Library/Caches/pydrive2fs/://googleusercontent.com`
   - **Windows**: `%LOCALAPPDATA%\pydrive2fs\apps.googleusercontent.com\default.json`