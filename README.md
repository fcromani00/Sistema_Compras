# 🛒 Sistema de Registro de Compras

Sistema profissional para registro de compras usando **Streamlit** e **Google Sheets** como banco de dados.

## 📋 Funcionalidades

- ✅ Cadastro de produtos com imagem (URL)
- ✅ Registro de compras com carrinho visual
- ✅ Múltiplos métodos de pagamento (Pix, Crédito, Débito, Dinheiro, etc.)
- ✅ Histórico de compras com filtros avançados (data, mês, ano)
- ✅ Exportação para Excel
- ✅ Dashboard com métricas
- ✅ Dados salvos automaticamente no Google Sheets
- ✅ Pronto para deploy no Streamlit Community Cloud

---

## 🚀 Desenvolvimento Local

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Conta de Serviço Google

#### Passo 1: Criar Projeto no Google Cloud

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Clique em **"Criar Projeto"** (ou selecione um existente)
3. Dê um nome ao projeto (ex: "Sistema de Compras")
4. Clique em **"Criar"**

#### Passo 2: Ativar APIs Necessárias

1. No menu lateral, vá em **"APIs e Serviços"** → **"Biblioteca"**
2. Pesquise e ative:
   - **Google Sheets API**
   - **Google Drive API**

#### Passo 3: Criar Conta de Serviço

1. Vá em **"APIs e Serviços"** → **"Credenciais"**
2. Clique em **"+ Criar Credenciais"** → **"Conta de serviço"**
3. Preencha o nome (ex: `sheets-service`)
4. Clique em **"Criar e Continuar"** → **"Concluído"**

#### Passo 4: Gerar Chave JSON

1. Na lista de contas de serviço, clique no email da conta criada
2. Vá na aba **"Chaves"**
3. Clique em **"Adicionar Chave"** → **"Criar nova chave"** → **JSON**
4. O arquivo será baixado automaticamente

#### Passo 5: Configurar Credenciais

**Opção A - Arquivo credentials.json (mais simples):**
- Renomeie o arquivo baixado para `credentials.json`
- Coloque na pasta raiz do projeto

**Opção B - Arquivo secrets.toml (recomendado):**
- Abra `.streamlit/secrets.toml`
- Copie os valores do seu `credentials.json` para os campos correspondentes

#### Passo 6: Compartilhar Planilha

1. Crie uma planilha no Google Sheets (ou deixe o sistema criar)
2. Copie o `client_email` do seu credentials.json
3. Compartilhe a planilha com esse email (permissão de **Editor**)

### 3. Executar localmente

```bash
streamlit run app.py
```

---

## ☁️ Deploy no Streamlit Community Cloud

### Passo 1: Preparar Repositório GitHub

1. Crie um repositório no GitHub
2. Faça upload dos arquivos:
   - `app.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `README.md`
   - `.gitignore`

⚠️ **NÃO faça upload de:**
- `credentials.json`
- `.streamlit/secrets.toml`

### Passo 2: Deploy no Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io/)
2. Clique em **"New app"**
3. Conecte seu repositório GitHub
4. Selecione:
   - **Repository:** seu-usuario/seu-repositorio
   - **Branch:** main
   - **Main file path:** app.py

### Passo 3: Configurar Secrets

1. Antes de fazer deploy, clique em **"Advanced settings"**
2. Na seção **"Secrets"**, cole o conteúdo abaixo (com seus valores):

```toml
[gcp_service_account]
type = "service_account"
project_id = "seu-project-id"
private_key_id = "sua-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nSUA_CHAVE_AQUI\n-----END PRIVATE KEY-----\n"
client_email = "seu-email@seu-projeto.iam.gserviceaccount.com"
client_id = "seu-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/seu-email%40seu-projeto.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

3. Clique em **"Deploy!"**

### Passo 4: Compartilhar Planilha

Após o deploy, compartilhe sua planilha Google Sheets com o `client_email` da conta de serviço.

---

## 📁 Estrutura do Projeto

```
Sistema-Compras/
├── .streamlit/
│   ├── config.toml        # Configurações de tema (pode commitar)
│   └── secrets.toml       # Credenciais locais (NÃO COMMITAR!)
├── app.py                 # Aplicativo principal
├── requirements.txt       # Dependências Python
├── .gitignore            # Arquivos ignorados pelo Git
└── README.md             # Documentação
```

---

## 📊 Estrutura das Planilhas

O sistema cria automaticamente duas abas:

**Aba "Produtos":**
| ID | Nome | Categoria | Preço | Unidade | Imagem | Data_Cadastro |
|----|------|-----------|-------|---------|--------|---------------|
| 1 | Água | Bebidas | 2.50 | un | https://... | 2024-01-01 |

**Aba "Compras":**
| ID_Compra | Data | Produto | Quantidade | Preço_Unit | Total | Pagamento | Observação |
|-----------|------|---------|------------|------------|-------|-----------|------------|
| CMP0001 | 2024-01-01 | Água | 10 | 2.50 | 25.00 | Pix | Cliente X |

---

## 💳 Métodos de Pagamento Suportados

- 💠 Pix
- 💳 Crédito
- 💳 Débito
- 💵 Dinheiro
- 🍽️ Vale Alimentação
- 📄 Boleto
- 🏦 Transferência
- 📋 Outro

---

## 🔒 Segurança

**NUNCA** faça commit de:
- `credentials.json`
- `.streamlit/secrets.toml`

O `.gitignore` já está configurado para proteger esses arquivos.

---

## 🛠️ Tecnologias

- **Python 3.8+**
- **Streamlit** - Interface web
- **gspread** - Integração com Google Sheets
- **google-auth** - Autenticação Google
- **pandas** - Manipulação de dados
- **openpyxl** - Exportação Excel

---

## ❓ Solução de Problemas

### Erro 429 (Quota exceeded)
O Google Sheets tem limite de 60 requisições/minuto. Aguarde 1 minuto e tente novamente.

### Erro de permissão
Verifique se a planilha foi compartilhada com o email da conta de serviço.

### Secrets não funcionam
No Streamlit Cloud, vá em **Settings > Secrets** e verifique se o formato TOML está correto.

---

## 📝 Licença

MIT License - Use livremente!
