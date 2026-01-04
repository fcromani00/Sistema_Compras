import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuração da página
st.set_page_config(
    page_title="Sistema de Compras",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para visual moderno
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(30, 58, 95, 0.3);
    }
    
    .main-header h1 {
        color: #ffffff;
        margin: 0;
        font-weight: 700;
        font-size: 2.2rem;
    }
    
    .main-header p {
        color: #a8c5e2;
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #2d5a87;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e3a5f;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #2d5a87 0%, #1e3a5f 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(45, 90, 135, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(45, 90, 135, 0.4);
    }
    
    .success-message {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e3a5f 0%, #0f172a 100%);
    }
    
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #0f172a 100%);
    }
    
    div[data-testid="stSidebar"] .stRadio label {
        color: #e2e8f0 !important;
    }
    
    .product-item {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #e2e8f0;
    }
    
    .cart-item {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        padding: 1rem;
        border-radius: 12px;
        margin: 0.75rem 0;
        border: 1px solid #e2e8f0;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .cart-item-image {
        width: 60px;
        height: 60px;
        border-radius: 8px;
        object-fit: cover;
        border: 2px solid #e2e8f0;
    }
    
    .cart-item-info {
        flex: 1;
    }
    
    .cart-item-name {
        font-weight: 600;
        color: #1e3a5f;
        font-size: 1rem;
        margin-bottom: 0.25rem;
    }
    
    .cart-item-details {
        color: #64748b;
        font-size: 0.85rem;
    }
    
    .cart-item-price {
        font-weight: 700;
        color: #2d5a87;
        font-size: 1.1rem;
    }
    
    .payment-option {
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .payment-option:hover {
        border-color: #2d5a87;
        background: #f0f9ff;
    }
    
    .payment-option.selected {
        border-color: #2d5a87;
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
    }
    
    .pix-badge {
        background: linear-gradient(135deg, #00d4aa 0%, #00a884 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .credito-badge {
        background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ==================== CONEXÃO COM GOOGLE SHEETS ====================

@st.cache_resource
def conectar_gsheets():
    """
    Conecta ao Google Sheets usando credenciais de conta de serviço.
    Suporta:
    - Streamlit Cloud: usa st.secrets
    - Desenvolvimento local: usa credentials.json ou .streamlit/secrets.toml
    """
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # MÉTODO 1: Tenta usar st.secrets (Streamlit Cloud ou secrets.toml local)
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            client = gspread.authorize(creds)
            return client
    except Exception:
        pass  # Continua para tentar o arquivo local
    
    # MÉTODO 2: Tenta usar arquivo credentials.json local
    try:
        creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Erro ao conectar: {e}")
        return None


@st.cache_resource(ttl=600)
def obter_planilha(_client, spreadsheet_name):
    """Obtém ou cria a planilha principal (com cache de 10 minutos)"""
    try:
        spreadsheet = _client.open(spreadsheet_name)
    except gspread.SpreadsheetNotFound:
        # Cria a planilha se não existir
        spreadsheet = _client.create(spreadsheet_name)
        # Compartilha com você mesmo (opcional - ajuste o email)
        # spreadsheet.share('seu-email@gmail.com', perm_type='user', role='writer')
    
    return spreadsheet


def garantir_abas(spreadsheet):
    """Garante que as abas Produtos, Compras e Movimentações existam com todas as colunas necessárias"""
    # Verifica se já foi executado nesta sessão
    if st.session_state.get('abas_verificadas', False):
        return spreadsheet
    
    try:
        worksheets = [ws.title for ws in spreadsheet.worksheets()]
        
        # ==================== ABA PRODUTOS ====================
        # Colunas esperadas na aba Produtos (com estoque)
        COLUNAS_PRODUTOS = ['ID', 'Nome', 'Categoria', 'Preço', 'Unidade', 'Estoque_Atual', 'Estoque_Minimo', 'Imagem', 'Data_Cadastro']
        
        if 'Produtos' not in worksheets:
            # Cria aba nova com todas as colunas
            ws_produtos = spreadsheet.add_worksheet(title='Produtos', rows=1000, cols=15)
            ws_produtos.append_row(COLUNAS_PRODUTOS, value_input_option='RAW')
        else:
            # Verifica e adiciona colunas faltantes
            ws_produtos = spreadsheet.worksheet('Produtos')
            headers = ws_produtos.row_values(1)
            
            # Se não tem headers, adiciona todos
            if not headers:
                ws_produtos.append_row(COLUNAS_PRODUTOS, value_input_option='RAW')
            else:
                # Verifica cada coluna necessária
                for idx, coluna in enumerate(COLUNAS_PRODUTOS):
                    if coluna not in headers:
                        # Adiciona na posição correta ou no final
                        pos = len(headers) + 1
                        ws_produtos.update_cell(1, pos, coluna)
                        headers.append(coluna)  # Atualiza lista local
        
        # ==================== ABA COMPRAS ====================
        # Colunas esperadas na aba Compras
        COLUNAS_COMPRAS = ['ID_Compra', 'Data', 'Produto', 'Quantidade', 'Preço_Unit', 'Total', 'Pagamento', 'Observação']
        
        if 'Compras' not in worksheets:
            # Cria aba nova com todas as colunas
            ws_compras = spreadsheet.add_worksheet(title='Compras', rows=1000, cols=10)
            ws_compras.append_row(COLUNAS_COMPRAS, value_input_option='RAW')
        else:
            # Verifica e adiciona colunas faltantes
            ws_compras = spreadsheet.worksheet('Compras')
            headers = ws_compras.row_values(1)
            
            # Se não tem headers, adiciona todos
            if not headers:
                ws_compras.append_row(COLUNAS_COMPRAS, value_input_option='RAW')
            else:
                # Verifica cada coluna necessária
                for idx, coluna in enumerate(COLUNAS_COMPRAS):
                    if coluna not in headers:
                        pos = len(headers) + 1
                        ws_compras.update_cell(1, pos, coluna)
                        headers.append(coluna)
        
        # ==================== ABA MOVIMENTAÇÕES (ESTOQUE) ====================
        # Colunas para controle de entrada/saída de estoque
        COLUNAS_MOVIMENTACOES = ['ID_Mov', 'Data', 'Tipo', 'Produto', 'Quantidade', 'Motivo', 'Observação']
        
        if 'Movimentacoes' not in worksheets:
            ws_mov = spreadsheet.add_worksheet(title='Movimentacoes', rows=1000, cols=10)
            ws_mov.append_row(COLUNAS_MOVIMENTACOES, value_input_option='RAW')
        else:
            ws_mov = spreadsheet.worksheet('Movimentacoes')
            headers = ws_mov.row_values(1)
            if not headers:
                ws_mov.append_row(COLUNAS_MOVIMENTACOES, value_input_option='RAW')
            else:
                for coluna in COLUNAS_MOVIMENTACOES:
                    if coluna not in headers:
                        pos = len(headers) + 1
                        ws_mov.update_cell(1, pos, coluna)
                        headers.append(coluna)
        
        # ==================== ABA ALERTAS ====================
        # Colunas para configuração de alertas
        COLUNAS_ALERTAS = ['ID', 'Email', 'Ativo', 'Ultima_Verificacao']
        
        if 'Alertas_Config' not in worksheets:
            ws_alertas = spreadsheet.add_worksheet(title='Alertas_Config', rows=100, cols=10)
            ws_alertas.append_row(COLUNAS_ALERTAS, value_input_option='RAW')
        
        # ==================== LIMPEZA ====================
        # Remove a Sheet1 padrão se existir e há outras abas
        if 'Sheet1' in worksheets and len(worksheets) > 1:
            try:
                sheet1 = spreadsheet.worksheet('Sheet1')
                spreadsheet.del_worksheet(sheet1)
            except:
                pass
        
        # Marca como verificado nesta sessão
        st.session_state.abas_verificadas = True
        
    except Exception as e:
        st.warning(f"⚠️ Aviso na verificação das abas: {e}")
    
    return spreadsheet


@st.cache_data(ttl=300, show_spinner=False)
def carregar_produtos(_spreadsheet, _cache_key):
    """Carrega todos os produtos da aba Produtos (com cache de 5 minutos)"""
    # Colunas esperadas (incluindo estoque)
    COLUNAS_PRODUTOS = ['ID', 'Nome', 'Categoria', 'Preço', 'Unidade', 'Estoque_Atual', 'Estoque_Minimo', 'Imagem', 'Data_Cadastro']
    
    try:
        ws = _spreadsheet.worksheet('Produtos')
        # Usa UNFORMATTED_VALUE para obter números corretamente
        dados = ws.get_all_records(value_render_option='UNFORMATTED_VALUE')
        
        if dados:
            df = pd.DataFrame(dados)
        else:
            # Retorna DataFrame vazio com as colunas esperadas
            df = pd.DataFrame(columns=COLUNAS_PRODUTOS)
        
        # Garante que todas as colunas existam
        for col in COLUNAS_PRODUTOS:
            if col not in df.columns:
                df[col] = 0 if col in ['Estoque_Atual', 'Estoque_Minimo'] else ''
        
        # Garante que colunas numéricas sejam numéricas
        if 'Preço' in df.columns:
            df['Preço'] = pd.to_numeric(df['Preço'], errors='coerce').fillna(0)
        
        if 'ID' in df.columns:
            df['ID'] = pd.to_numeric(df['ID'], errors='coerce').fillna(0).astype(int)
        
        if 'Estoque_Atual' in df.columns:
            df['Estoque_Atual'] = pd.to_numeric(df['Estoque_Atual'], errors='coerce').fillna(0)
        
        if 'Estoque_Minimo' in df.columns:
            df['Estoque_Minimo'] = pd.to_numeric(df['Estoque_Minimo'], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        # Em caso de erro, retorna DataFrame vazio com estrutura correta
        return pd.DataFrame(columns=COLUNAS_PRODUTOS)


def adicionar_produto(spreadsheet, nome, categoria, preco, unidade, estoque_atual=0, estoque_minimo=5, imagem_url=""):
    """Adiciona um novo produto com tratamento de erros"""
    try:
        ws = spreadsheet.worksheet('Produtos')
        dados = ws.get_all_values()
        novo_id = len(dados)  # ID simples baseado na linha
        
        # Garante que preço seja float
        preco_float = float(preco) if preco else 0.0
        estoque_atual_float = float(estoque_atual) if estoque_atual else 0.0
        estoque_minimo_float = float(estoque_minimo) if estoque_minimo else 5.0
        
        # Garante que valores não sejam None
        nome = str(nome or "").strip()
        categoria = str(categoria or "").strip()
        unidade = str(unidade or "un").strip()
        imagem_url = str(imagem_url or "").strip()
        
        # Usa value_input_option='RAW' para salvar números corretamente
        ws.append_row([
            novo_id,
            nome,
            categoria,
            preco_float,
            unidade,
            estoque_atual_float,
            estoque_minimo_float,
            imagem_url,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ], value_input_option='RAW')
        return True
    except Exception as e:
        st.error(f"❌ Erro ao adicionar produto: {e}")
        return False


@st.cache_data(ttl=300, show_spinner=False)
def carregar_compras(_spreadsheet, _cache_key):
    """Carrega todas as compras (com cache de 5 minutos)"""
    # Colunas esperadas
    COLUNAS_COMPRAS = ['ID_Compra', 'Data', 'Produto', 'Quantidade', 'Preço_Unit', 'Total', 'Pagamento', 'Observação']
    
    try:
        ws = _spreadsheet.worksheet('Compras')
        # Usa UNFORMATTED_VALUE para obter números corretamente
        dados = ws.get_all_records(value_render_option='UNFORMATTED_VALUE')
        
        if dados:
            df = pd.DataFrame(dados)
        else:
            # Retorna DataFrame vazio com as colunas esperadas
            df = pd.DataFrame(columns=COLUNAS_COMPRAS)
        
        # Garante que todas as colunas existam
        for col in COLUNAS_COMPRAS:
            if col not in df.columns:
                df[col] = ''
        
        # Garante que colunas numéricas sejam numéricas
        for col in ['Quantidade', 'Preço_Unit', 'Total']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        # Em caso de erro, retorna DataFrame vazio com estrutura correta
        return pd.DataFrame(columns=COLUNAS_COMPRAS)


def registrar_compra(spreadsheet, itens, metodo_pagamento, observacao=""):
    """Registra uma nova compra/venda com múltiplos itens, desconta do estoque e verifica alertas"""
    try:
        ws_compras = spreadsheet.worksheet('Compras')
        ws_produtos = spreadsheet.worksheet('Produtos')
        
        dados = ws_compras.get_all_values()
        id_compra = f"CMP{len(dados):04d}"
        data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Garante valores válidos
        metodo_pagamento = str(metodo_pagamento or "Não informado").strip()
        observacao = str(observacao or "").strip()
        
        # Carrega dados dos produtos para atualizar estoque
        produtos_dados = ws_produtos.get_all_records()
        headers_produtos = ws_produtos.row_values(1)
        col_estoque = headers_produtos.index('Estoque_Atual') + 1 if 'Estoque_Atual' in headers_produtos else None
        
        produtos_criticos = []
        
        for item in itens:
            quantidade = float(item.get('quantidade', 0))
            preco = float(item.get('preco', 0))
            total = quantidade * preco
            produto = str(item.get('produto', '')).strip()
            
            # Registra a venda na aba Compras
            ws_compras.append_row([
                id_compra,
                data_atual,
                produto,
                quantidade,
                preco,
                total,
                metodo_pagamento,
                observacao
            ], value_input_option='RAW')
            
            # Desconta do estoque do produto
            if col_estoque:
                for idx, prod in enumerate(produtos_dados, start=2):
                    if prod.get('Nome') == produto:
                        estoque_atual = float(prod.get('Estoque_Atual', 0) or 0)
                        novo_estoque = max(0, estoque_atual - quantidade)  # Não deixa ficar negativo
                        estoque_minimo = float(prod.get('Estoque_Minimo', 0) or 0)
                        
                        # Atualiza estoque na planilha
                        ws_produtos.update_cell(idx, col_estoque, novo_estoque)
                        
                        # Verifica se ficou crítico
                        if novo_estoque <= estoque_minimo:
                            produtos_criticos.append({
                                'Nome': produto,
                                'Estoque_Atual': novo_estoque,
                                'Estoque_Minimo': estoque_minimo
                            })
                        
                        # Registra movimentação de saída
                        try:
                            registrar_movimentacao(spreadsheet, "Saída", produto, quantidade, "Venda", f"Compra {id_compra}")
                        except:
                            pass  # Não falha se não conseguir registrar movimentação
                        
                        break
        
        return id_compra, produtos_criticos
    except Exception as e:
        st.error(f"❌ Erro ao registrar compra: {e}")
        return None, []


# ==================== FUNÇÕES DE ESTOQUE ====================

@st.cache_data(ttl=300, show_spinner=False)
def carregar_movimentacoes(_spreadsheet, _cache_key):
    """Carrega todas as movimentações de estoque"""
    COLUNAS_MOV = ['ID_Mov', 'Data', 'Tipo', 'Produto', 'Quantidade', 'Motivo', 'Observação']
    
    try:
        ws = _spreadsheet.worksheet('Movimentacoes')
        dados = ws.get_all_records(value_render_option='UNFORMATTED_VALUE')
        
        if dados:
            df = pd.DataFrame(dados)
        else:
            df = pd.DataFrame(columns=COLUNAS_MOV)
        
        for col in COLUNAS_MOV:
            if col not in df.columns:
                df[col] = ''
        
        if 'Quantidade' in df.columns:
            df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce').fillna(0)
        
        return df
    except:
        return pd.DataFrame(columns=COLUNAS_MOV)


def registrar_movimentacao(spreadsheet, tipo, produto, quantidade, motivo="", observacao=""):
    """Registra uma movimentação de estoque (Entrada ou Saída)"""
    try:
        ws = spreadsheet.worksheet('Movimentacoes')
        dados = ws.get_all_values()
        id_mov = f"MOV{len(dados):05d}"
        data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        ws.append_row([
            id_mov,
            data_atual,
            tipo,  # "Entrada" ou "Saída"
            str(produto),
            float(quantidade),
            str(motivo or ""),
            str(observacao or "")
        ], value_input_option='RAW')
        
        return id_mov
    except Exception as e:
        st.error(f"❌ Erro ao registrar movimentação: {e}")
        return None


def atualizar_estoque_produto(spreadsheet, nome_produto, nova_quantidade):
    """Atualiza o estoque de um produto específico"""
    try:
        ws = spreadsheet.worksheet('Produtos')
        dados = ws.get_all_records()
        
        # Encontra a linha do produto
        for idx, row in enumerate(dados, start=2):  # start=2 porque linha 1 é cabeçalho
            if row.get('Nome') == nome_produto:
                # Encontra a coluna de Estoque_Atual
                headers = ws.row_values(1)
                if 'Estoque_Atual' in headers:
                    col_idx = headers.index('Estoque_Atual') + 1
                    ws.update_cell(idx, col_idx, float(nova_quantidade))
                    return True
        return False
    except Exception as e:
        st.error(f"❌ Erro ao atualizar estoque: {e}")
        return False


def obter_produtos_estoque_critico(df_produtos):
    """Retorna produtos com estoque abaixo do mínimo"""
    if df_produtos.empty:
        return pd.DataFrame()
    
    if 'Estoque_Atual' not in df_produtos.columns or 'Estoque_Minimo' not in df_produtos.columns:
        return pd.DataFrame()
    
    # Filtra produtos com estoque crítico
    criticos = df_produtos[df_produtos['Estoque_Atual'] <= df_produtos['Estoque_Minimo']].copy()
    
    if not criticos.empty:
        criticos['Deficit'] = criticos['Estoque_Minimo'] - criticos['Estoque_Atual']
    
    return criticos


def enviar_alerta_email(destinatario, produtos_criticos, config_email=None):
    """Envia alerta por email sobre produtos com estoque crítico"""
    try:
        # Configurações de email (pode vir do secrets)
        if config_email is None:
            if "email_config" in st.secrets:
                config_email = dict(st.secrets["email_config"])
            else:
                return False, "Configuração de email não encontrada"
        
        smtp_server = config_email.get('smtp_server', 'smtp.gmail.com')
        smtp_port = config_email.get('smtp_port', 587)
        email_sender = config_email.get('email_sender', '')
        email_password = config_email.get('email_password', '')
        
        if not email_sender or not email_password:
            return False, "Credenciais de email não configuradas"
        
        # Monta o corpo do email
        html_produtos = ""
        for _, prod in produtos_criticos.iterrows():
            html_produtos += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">{prod.get('Nome', 'N/A')}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{prod.get('Estoque_Atual', 0)}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{prod.get('Estoque_Minimo', 0)}</td>
            </tr>
            """
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color: white; padding: 20px; border-radius: 10px;">
                <h1>⚠️ Alerta de Estoque Crítico</h1>
                <p>Os seguintes produtos estão com estoque abaixo do nível mínimo:</p>
            </div>
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <thead>
                    <tr style="background-color: #1e3a5f; color: white;">
                        <th style="padding: 10px; border: 1px solid #ddd;">Produto</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Estoque Atual</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Estoque Mínimo</th>
                    </tr>
                </thead>
                <tbody>
                    {html_produtos}
                </tbody>
            </table>
            <p style="margin-top: 20px; color: #666;">
                Este é um alerta automático do Sistema de Compras.<br>
                Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
            </p>
        </body>
        </html>
        """
        
        # Cria a mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"⚠️ ALERTA: {len(produtos_criticos)} produto(s) com estoque crítico"
        msg['From'] = email_sender
        msg['To'] = destinatario
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Envia o email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_sender, email_password)
            server.sendmail(email_sender, destinatario, msg.as_string())
        
        return True, "Email enviado com sucesso!"
    except Exception as e:
        return False, f"Erro ao enviar email: {e}"


def carregar_config_alertas(spreadsheet):
    """Carrega configurações de alertas"""
    try:
        ws = spreadsheet.worksheet('Alertas_Config')
        dados = ws.get_all_records()
        return dados
    except:
        return []


def salvar_config_alerta(spreadsheet, email, ativo=True):
    """Salva configuração de alerta"""
    try:
        ws = spreadsheet.worksheet('Alertas_Config')
        dados = ws.get_all_values()
        novo_id = len(dados)
        
        ws.append_row([
            novo_id,
            email,
            "Sim" if ativo else "Não",
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ], value_input_option='RAW')
        return True
    except:
        return False


# ==================== INTERFACE STREAMLIT ====================

def mostrar_config():
    """Mostra instruções de configuração"""
    st.markdown("""
    <div class="main-header">
        <h1>⚙️ Configuração Necessária</h1>
        <p>Configure sua conta de serviço Google para começar</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.warning("⚠️ Arquivo `credentials.json` não encontrado!")
    
    st.markdown("""
    ### 📋 Siga os passos abaixo:
    
    #### 1️⃣ Criar Projeto no Google Cloud
    1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
    2. Clique em **"Criar Projeto"** ou selecione um existente
    3. Dê um nome ao projeto (ex: "Sistema de Compras")
    
    #### 2️⃣ Ativar APIs necessárias
    1. No menu lateral, vá em **"APIs e Serviços"** → **"Biblioteca"**
    2. Pesquise e ative:
       - **Google Sheets API**
       - **Google Drive API**
    
    #### 3️⃣ Criar Conta de Serviço
    1. Vá em **"APIs e Serviços"** → **"Credenciais"**
    2. Clique em **"Criar Credenciais"** → **"Conta de serviço"**
    3. Dê um nome (ex: "sheets-service")
    4. Clique em **"Criar e Continuar"** → **"Concluído"**
    
    #### 4️⃣ Gerar Chave JSON
    1. Na lista de contas de serviço, clique na que você criou
    2. Vá na aba **"Chaves"**
    3. Clique em **"Adicionar Chave"** → **"Criar nova chave"**
    4. Selecione **JSON** e clique em **"Criar"**
    5. **Renomeie o arquivo baixado para `credentials.json`**
    6. **Coloque na pasta do projeto**
    
    #### 5️⃣ Compartilhar a Planilha
    1. Crie uma planilha no Google Sheets
    2. No arquivo `credentials.json`, copie o valor de `client_email`
    3. Compartilhe a planilha com esse email (permissão de **Editor**)
    
    ---
    
    ✅ Após colocar o `credentials.json` na pasta, **recarregue esta página**!
    """)


def pagina_produtos(spreadsheet):
    """Página de gerenciamento de produtos"""
    st.markdown("""
    <div class="main-header">
        <h1>📦 Produtos da Loja</h1>
        <p>Gerencie o catálogo de produtos disponíveis</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("➕ Adicionar Produto")
        
        with st.form("form_produto", clear_on_submit=True):
            nome = st.text_input("Nome do Produto *")
            categoria = st.selectbox(
                "Categoria",
                ["Alimentos", "Bebidas", "Limpeza", "Higiene", "Outros"]
            )
            preco = st.number_input("Preço (R$)", min_value=0.01, step=0.01, format="%.2f")
            unidade = st.selectbox("Unidade", ["un", "kg", "L", "cx", "pct"])
            
            # Campos de estoque
            st.markdown("##### 📦 Estoque")
            col_est1, col_est2 = st.columns(2)
            with col_est1:
                estoque_atual = st.number_input("Estoque Inicial", min_value=0.0, step=1.0, format="%.1f", value=0.0)
            with col_est2:
                estoque_minimo = st.number_input("Estoque Mínimo", min_value=0.0, step=1.0, format="%.1f", value=5.0,
                                                  help="Alerta quando estoque ficar abaixo deste valor")
            
            imagem_url = st.text_input(
                "🖼️ URL da Imagem (opcional)",
                placeholder="https://exemplo.com/imagem.jpg",
                help="Cole a URL de uma imagem da web para o produto"
            )
            
            # Preview da imagem se URL fornecida
            if imagem_url:
                st.image(imagem_url, width=150, caption="Preview da imagem")
            
            submitted = st.form_submit_button("💾 Salvar Produto", use_container_width=True)
            
            if submitted:
                if nome:
                    sucesso = adicionar_produto(spreadsheet, nome, categoria, preco, unidade, estoque_atual, estoque_minimo, imagem_url)
                    if sucesso:
                        st.success(f"✅ Produto '{nome}' adicionado com sucesso!")
                        # Invalida cache de produtos
                        st.session_state.cache_key_produtos += 1
                        st.rerun()
                else:
                    st.error("❌ Informe o nome do produto!")
    
    with col2:
        st.subheader("📋 Lista de Produtos")
        
        df_produtos = carregar_produtos(spreadsheet, st.session_state.cache_key_produtos)
        
        if not df_produtos.empty:
            # Filtro de busca
            busca = st.text_input("🔍 Buscar produto...")
            
            if busca:
                df_filtrado = df_produtos[
                    df_produtos['Nome'].str.contains(busca, case=False, na=False)
                ]
            else:
                df_filtrado = df_produtos
            
            # Verifica produtos com estoque crítico
            produtos_criticos = obter_produtos_estoque_critico(df_filtrado)
            if not produtos_criticos.empty:
                st.warning(f"⚠️ **{len(produtos_criticos)} produto(s) com estoque crítico!**")
            
            # Configuração das colunas (só inclui as que existem no DataFrame)
            column_config = {}
            
            if 'ID' in df_filtrado.columns:
                column_config["ID"] = st.column_config.NumberColumn("ID", width="small")
            if 'Nome' in df_filtrado.columns:
                column_config["Nome"] = st.column_config.TextColumn("Produto", width="medium")
            if 'Categoria' in df_filtrado.columns:
                column_config["Categoria"] = st.column_config.TextColumn("Categoria", width="small")
            if 'Preço' in df_filtrado.columns:
                column_config["Preço"] = st.column_config.NumberColumn("Preço", format="R$ %.2f")
            if 'Unidade' in df_filtrado.columns:
                column_config["Unidade"] = st.column_config.TextColumn("Un.", width="small")
            if 'Estoque_Atual' in df_filtrado.columns:
                column_config["Estoque_Atual"] = st.column_config.NumberColumn("📦 Estoque", format="%.1f")
            if 'Estoque_Minimo' in df_filtrado.columns:
                column_config["Estoque_Minimo"] = st.column_config.NumberColumn("⚠️ Mín.", format="%.1f")
            if 'Imagem' in df_filtrado.columns:
                column_config["Imagem"] = st.column_config.ImageColumn("📷", width="small")
            if 'Data_Cadastro' in df_filtrado.columns:
                column_config["Data_Cadastro"] = st.column_config.TextColumn("Cadastrado em", width="medium")
            
            st.dataframe(
                df_filtrado,
                use_container_width=True,
                hide_index=True,
                column_config=column_config
            )
            
            st.info(f"📊 Total de {len(df_filtrado)} produto(s)")
        else:
            st.info("📭 Nenhum produto cadastrado ainda.")


def pagina_compras(spreadsheet):
    """Página de registro de compras"""
    st.markdown("""
    <div class="main-header">
        <h1>🛒 Registrar Compra</h1>
        <p>Adicione produtos ao carrinho e finalize a compra</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializa o carrinho na sessão
    if 'carrinho' not in st.session_state:
        st.session_state.carrinho = []
    
    df_produtos = carregar_produtos(spreadsheet, st.session_state.cache_key_produtos)
    
    if df_produtos.empty:
        st.warning("⚠️ Cadastre produtos primeiro na aba 'Produtos'!")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("➕ Adicionar ao Carrinho")
        
        # Seleção de produto (filtra nomes vazios)
        opcoes_produtos = [nome for nome in df_produtos['Nome'].tolist() if nome and str(nome).strip()]
        
        if not opcoes_produtos:
            st.warning("⚠️ Nenhum produto válido encontrado!")
            return
        
        produto_selecionado = st.selectbox("Selecione o Produto", opcoes_produtos)
        
        # Busca dados do produto selecionado com tratamento de erros
        try:
            produto_info = df_produtos[df_produtos['Nome'] == produto_selecionado].iloc[0]
            preco_produto = float(produto_info.get('Preço', 0) or 0)
            unidade_produto = str(produto_info.get('Unidade', 'un') or 'un')
            imagem_produto = str(produto_info.get('Imagem', '') or '') if 'Imagem' in df_produtos.columns else ''
        except (IndexError, KeyError):
            st.error("❌ Erro ao carregar dados do produto!")
            return
        
        # Mostra imagem do produto se disponível
        col_img, col_info = st.columns([1, 2])
        with col_img:
            if imagem_produto and str(imagem_produto).strip():
                st.image(imagem_produto, width=100)
            else:
                st.markdown("📦")
        with col_info:
            st.info(f"💰 Preço: R$ {preco_produto:.2f} / {unidade_produto}")
        
        quantidade = st.number_input(
            f"Quantidade ({unidade_produto})", 
            min_value=0.01, 
            value=1.0, 
            step=0.5,
            format="%.2f"
        )
        
        subtotal = quantidade * preco_produto
        st.markdown(f"**Subtotal: R$ {subtotal:.2f}**")
        
        if st.button("🛒 Adicionar ao Carrinho", use_container_width=True):
            item = {
                'produto': produto_selecionado,
                'quantidade': quantidade,
                'preco': preco_produto,
                'subtotal': subtotal,
                'imagem': imagem_produto if imagem_produto else ""
            }
            st.session_state.carrinho.append(item)
            st.success(f"✅ {produto_selecionado} adicionado!")
            st.rerun()
    
    with col2:
        st.subheader("🧺 Carrinho de Compras")
        
        if st.session_state.carrinho:
            # Exibe itens do carrinho com imagens
            for idx, item in enumerate(st.session_state.carrinho):
                col_img_cart, col_info_cart, col_remove = st.columns([1, 3, 1])
                
                with col_img_cart:
                    if item.get('imagem') and str(item['imagem']).strip():
                        st.image(item['imagem'], width=60)
                    else:
                        st.markdown("📦")
                
                with col_info_cart:
                    st.markdown(f"**{item['produto']}**")
                    st.caption(f"{item['quantidade']:.2f} x R$ {item['preco']:.2f} = **R$ {item['subtotal']:.2f}**")
                
                with col_remove:
                    if st.button("🗑️", key=f"remove_{idx}", help="Remover item"):
                        st.session_state.carrinho.pop(idx)
                        st.rerun()
                
                st.markdown("---")
            
            total_compra = sum(item['subtotal'] for item in st.session_state.carrinho)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total da Compra</div>
                <div class="metric-value">R$ {total_compra:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 💳 Método de Pagamento")
            
            # Opções de pagamento com ícones
            METODOS_PAGAMENTO = {
                "Pix": {"icone": "💠", "cor": "#00d4aa", "desc": "Pagamento instantâneo"},
                "Crédito": {"icone": "💳", "cor": "#8b5cf6", "desc": "Cartão de crédito"},
                "Débito": {"icone": "💳", "cor": "#3b82f6", "desc": "Cartão de débito"},
                "Dinheiro": {"icone": "💵", "cor": "#22c55e", "desc": "Pagamento em espécie"},
                "Vale Alimentação": {"icone": "🍽️", "cor": "#f97316", "desc": "VA/VR"},
                "Boleto": {"icone": "📄", "cor": "#64748b", "desc": "Boleto bancário"},
                "Transferência": {"icone": "🏦", "cor": "#0ea5e9", "desc": "TED/DOC"},
                "Outro": {"icone": "📋", "cor": "#71717a", "desc": "Outros métodos"}
            }
            
            metodo_pagamento = st.selectbox(
                "Escolha como deseja pagar:",
                list(METODOS_PAGAMENTO.keys()),
                label_visibility="collapsed"
            )
            
            # Visual do método selecionado
            info = METODOS_PAGAMENTO[metodo_pagamento]
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {info['cor']}20 0%, {info['cor']}10 100%); 
                        padding: 1rem; border-radius: 10px; border: 2px solid {info['cor']};">
                <span style="font-size: 1.5rem;">{info['icone']}</span> 
                <strong>{metodo_pagamento}</strong> - {info['desc']}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("🗑️ Limpar Carrinho", use_container_width=True):
                    st.session_state.carrinho = []
                    st.rerun()
            
            with col_btn2:
                observacao = st.text_input("Observação (opcional)")
                
                if st.button("✅ Finalizar Compra", use_container_width=True, type="primary"):
                    resultado = registrar_compra(spreadsheet, st.session_state.carrinho, metodo_pagamento, observacao)
                    
                    if resultado and resultado[0]:
                        id_compra, produtos_criticos = resultado
                        
                        st.success(f"🎉 Compra {id_compra} registrada com sucesso!")
                        st.info("📦 Estoque atualizado automaticamente!")
                        
                        # Alerta de produtos críticos
                        if produtos_criticos:
                            st.warning(f"⚠️ **ATENÇÃO:** {len(produtos_criticos)} produto(s) ficaram com estoque crítico!")
                            
                            for prod in produtos_criticos:
                                st.error(f"🔴 **{prod['Nome']}** - Estoque: {prod['Estoque_Atual']:.0f} (Mín: {prod['Estoque_Minimo']:.0f})")
                            
                            # Tenta enviar alerta por email se configurado
                            try:
                                config_alertas = carregar_config_alertas(spreadsheet)
                                if config_alertas:
                                    for config in config_alertas:
                                        if config.get('Ativo') == 'Sim' and config.get('Email'):
                                            df_criticos = pd.DataFrame(produtos_criticos)
                                            enviar_alerta_email(config['Email'], df_criticos)
                                            st.info(f"📧 Alerta enviado para {config['Email']}")
                            except:
                                pass  # Silenciosamente ignora erros de email
                        
                        st.session_state.carrinho = []
                        # Invalida caches
                        st.session_state.cache_key_compras += 1
                        st.session_state.cache_key_produtos += 1
                        if 'cache_key_movimentacoes' in st.session_state:
                            st.session_state.cache_key_movimentacoes += 1
                        
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
        else:
            st.info("🛒 Carrinho vazio. Adicione produtos!")


def pagina_historico(spreadsheet):
    """Página de histórico de compras"""
    st.markdown("""
    <div class="main-header">
        <h1>📊 Histórico de Compras</h1>
        <p>Visualize todas as compras registradas</p>
    </div>
    """, unsafe_allow_html=True)
    
    df_compras = carregar_compras(spreadsheet, st.session_state.cache_key_compras)
    
    if not df_compras.empty:
        # Converte coluna de data para datetime para filtros
        if 'Data' in df_compras.columns:
            df_compras['Data_dt'] = pd.to_datetime(df_compras['Data'], errors='coerce')
            df_compras['Ano'] = df_compras['Data_dt'].dt.year
            df_compras['Mes'] = df_compras['Data_dt'].dt.month
            df_compras['Dia'] = df_compras['Data_dt'].dt.day
        
        # ==================== FILTROS ====================
        st.subheader("🔍 Filtros")
        
        with st.expander("📅 Filtros de Data", expanded=True):
            col_data1, col_data2, col_data3, col_data4 = st.columns(4)
            
            with col_data1:
                # Anos disponíveis
                if 'Ano' in df_compras.columns:
                    anos_disponiveis = sorted(df_compras['Ano'].dropna().unique().tolist(), reverse=True)
                    anos_opcoes = ['Todos'] + [int(a) for a in anos_disponiveis if pd.notna(a)]
                    filtro_ano = st.selectbox("📆 Ano", anos_opcoes)
            
            with col_data2:
                # Meses
                meses_nomes = {
                    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
                }
                meses_opcoes = ['Todos'] + list(meses_nomes.values())
                filtro_mes = st.selectbox("📅 Mês", meses_opcoes)
            
            with col_data3:
                # Data inicial
                if 'Data_dt' in df_compras.columns:
                    data_min = df_compras['Data_dt'].min()
                    if pd.notna(data_min):
                        data_min = data_min.date()
                    else:
                        data_min = datetime.now().date() - timedelta(days=365)
                else:
                    data_min = datetime.now().date() - timedelta(days=365)
                
                filtro_data_inicio = st.date_input(
                    "📅 Data Inicial",
                    value=data_min,
                    format="DD/MM/YYYY"
                )
            
            with col_data4:
                # Data final
                filtro_data_fim = st.date_input(
                    "📅 Data Final",
                    value=datetime.now().date(),
                    format="DD/MM/YYYY"
                )
        
        # Outros filtros
        col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
        
        with col_filtro1:
            if 'ID_Compra' in df_compras.columns:
                compras_unicas = ['Todas'] + df_compras['ID_Compra'].unique().tolist()
                filtro_compra = st.selectbox("🏷️ Filtrar por Compra", compras_unicas)
        
        with col_filtro2:
            if 'Produto' in df_compras.columns:
                produtos_unicos = ['Todos'] + sorted(df_compras['Produto'].unique().tolist())
                filtro_produto = st.selectbox("📦 Filtrar por Produto", produtos_unicos)
        
        with col_filtro3:
            if 'Pagamento' in df_compras.columns:
                pagamentos_unicos = df_compras['Pagamento'].unique().tolist()
                pagamentos = ['Todos'] + sorted([p for p in pagamentos_unicos if p])
                filtro_pagamento = st.selectbox("💳 Filtrar por Pagamento", pagamentos)
        
        st.markdown("---")
        
        # ==================== APLICA FILTROS ====================
        df_filtrado = df_compras.copy()
        
        # Filtro de ano
        if 'filtro_ano' in dir() and filtro_ano != 'Todos' and 'Ano' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Ano'] == filtro_ano]
        
        # Filtro de mês
        if 'filtro_mes' in dir() and filtro_mes != 'Todos' and 'Mes' in df_filtrado.columns:
            mes_num = list(meses_nomes.keys())[list(meses_nomes.values()).index(filtro_mes)]
            df_filtrado = df_filtrado[df_filtrado['Mes'] == mes_num]
        
        # Filtro de data inicial e final
        if 'Data_dt' in df_filtrado.columns:
            df_filtrado = df_filtrado[
                (df_filtrado['Data_dt'].dt.date >= filtro_data_inicio) &
                (df_filtrado['Data_dt'].dt.date <= filtro_data_fim)
            ]
        
        # Filtro de compra
        if 'filtro_compra' in dir() and filtro_compra != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['ID_Compra'] == filtro_compra]
        
        # Filtro de produto
        if 'filtro_produto' in dir() and filtro_produto != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Produto'] == filtro_produto]
        
        # Filtro de pagamento
        if 'filtro_pagamento' in dir() and filtro_pagamento != 'Todos' and 'Pagamento' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Pagamento'] == filtro_pagamento]
        
        # ==================== MÉTRICAS FILTRADAS ====================
        total_geral = df_filtrado['Total'].sum() if 'Total' in df_filtrado.columns else 0
        num_compras = df_filtrado['ID_Compra'].nunique() if 'ID_Compra' in df_filtrado.columns else 0
        num_itens = len(df_filtrado)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Filtrado</div>
                <div class="metric-value">R$ {total_geral:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Nº de Compras</div>
                <div class="metric-value">{num_compras}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Itens</div>
                <div class="metric-value">{num_itens}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Métricas por método de pagamento (só mostra os que existem)
        if 'Pagamento' in df_filtrado.columns and not df_filtrado.empty:
            st.markdown("#### 💳 Totais por Método de Pagamento")
            
            totais_pagamento = df_filtrado.groupby('Pagamento')['Total'].sum().to_dict()
            
            # Cores para cada método
            cores_pagamento = {
                "Pix": "#00d4aa",
                "Crédito": "#8b5cf6",
                "Débito": "#3b82f6",
                "Dinheiro": "#22c55e",
                "Vale Alimentação": "#f97316",
                "Boleto": "#64748b",
                "Transferência": "#0ea5e9",
                "Outro": "#71717a"
            }
            
            if totais_pagamento:
                cols_pag = st.columns(min(len(totais_pagamento), 4))
                for idx, (metodo, total) in enumerate(totais_pagamento.items()):
                    cor = cores_pagamento.get(metodo, "#64748b")
                    with cols_pag[idx % 4]:
                        st.markdown(f"""
                        <div class="metric-card" style="border-left-color: {cor};">
                            <div class="metric-label">{metodo}</div>
                            <div class="metric-value" style="color: {cor}; font-size: 1.3rem;">R$ {total:.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ==================== TABELA E EXPORTAÇÃO ====================
        col_titulo, col_export = st.columns([3, 1])
        
        with col_titulo:
            st.subheader(f"📋 Registros ({len(df_filtrado)} itens)")
        
        with col_export:
            # Prepara DataFrame para exportação (remove colunas auxiliares)
            df_export = df_filtrado.drop(columns=['Data_dt', 'Ano', 'Mes', 'Dia'], errors='ignore')
            
            # Cria arquivo Excel em memória
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Histórico')
            
            st.download_button(
                label="📥 Exportar Excel",
                data=buffer.getvalue(),
                file_name=f"historico_compras_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        # Configuração das colunas (remove colunas auxiliares da visualização)
        df_exibir = df_filtrado.drop(columns=['Data_dt', 'Ano', 'Mes', 'Dia'], errors='ignore')
        
        column_config = {
            "ID_Compra": st.column_config.TextColumn("ID Compra", width="small"),
            "Data": st.column_config.TextColumn("Data/Hora", width="medium"),
            "Produto": st.column_config.TextColumn("Produto", width="medium"),
            "Quantidade": st.column_config.NumberColumn("Qtd", format="%.2f"),
            "Preço_Unit": st.column_config.NumberColumn("Preço Unit.", format="R$ %.2f"),
            "Total": st.column_config.NumberColumn("Total", format="R$ %.2f"),
            "Observação": st.column_config.TextColumn("Obs.", width="medium")
        }
        
        # Adiciona coluna de pagamento se existir
        if 'Pagamento' in df_exibir.columns:
            column_config["Pagamento"] = st.column_config.TextColumn("💳 Pagamento", width="small")
        
        st.dataframe(
            df_exibir,
            use_container_width=True,
            hide_index=True,
            column_config=column_config
        )
        
        # Resumo por produto
        if not df_filtrado.empty:
            with st.expander("📊 Resumo por Produto"):
                resumo = df_filtrado.groupby('Produto').agg({
                    'Quantidade': 'sum',
                    'Total': 'sum'
                }).reset_index()
                resumo.columns = ['Produto', 'Qtd Total', 'Valor Total']
                resumo = resumo.sort_values('Valor Total', ascending=False)
                
                st.dataframe(
                    resumo,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Produto": st.column_config.TextColumn("Produto"),
                        "Qtd Total": st.column_config.NumberColumn("Qtd Total", format="%.2f"),
                        "Valor Total": st.column_config.NumberColumn("Valor Total", format="R$ %.2f")
                    }
                )
    else:
        st.info("📭 Nenhuma compra registrada ainda.")


def pagina_estoque(spreadsheet):
    """Página de controle de estoque"""
    st.markdown("""
    <div class="main-header">
        <h1>📦 Controle de Estoque</h1>
        <p>Gerencie entradas, saídas e alertas de reposição</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializa cache key de movimentações
    if 'cache_key_movimentacoes' not in st.session_state:
        st.session_state.cache_key_movimentacoes = 0
    
    df_produtos = carregar_produtos(spreadsheet, st.session_state.cache_key_produtos)
    
    if df_produtos.empty:
        st.warning("⚠️ Cadastre produtos primeiro na aba 'Produtos'!")
        return
    
    # ==================== ALERTAS DE ESTOQUE CRÍTICO ====================
    produtos_criticos = obter_produtos_estoque_critico(df_produtos)
    
    if not produtos_criticos.empty:
        st.markdown("### 🚨 Produtos com Estoque Crítico")
        
        for _, prod in produtos_criticos.iterrows():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
            with col1:
                st.markdown(f"**{prod.get('Nome', 'N/A')}**")
            with col2:
                st.markdown(f"📦 Atual: **{prod.get('Estoque_Atual', 0):.0f}**")
            with col3:
                st.markdown(f"⚠️ Mín: **{prod.get('Estoque_Minimo', 0):.0f}**")
            with col4:
                deficit = prod.get('Estoque_Minimo', 0) - prod.get('Estoque_Atual', 0)
                st.error(f"Repor: **{max(0, deficit):.0f}** unidades")
        
        st.markdown("---")
    else:
        st.success("✅ Todos os produtos estão com estoque adequado!")
        st.markdown("---")
    
    # ==================== TABS ====================
    tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "📥 Movimentações", "⚙️ Configurar Alertas"])
    
    with tab1:
        # Métricas gerais
        col1, col2, col3, col4 = st.columns(4)
        
        total_produtos = len(df_produtos)
        total_criticos = len(produtos_criticos)
        total_estoque = df_produtos['Estoque_Atual'].sum() if 'Estoque_Atual' in df_produtos.columns else 0
        valor_estoque = (df_produtos['Estoque_Atual'] * df_produtos['Preço']).sum() if 'Estoque_Atual' in df_produtos.columns else 0
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total de Produtos</div>
                <div class="metric-value">{total_produtos}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            cor_critico = "#dc2626" if total_criticos > 0 else "#22c55e"
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {cor_critico};">
                <div class="metric-label">🚨 Estoque Crítico</div>
                <div class="metric-value" style="color: {cor_critico};">{total_criticos}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📦 Itens em Estoque</div>
                <div class="metric-value">{total_estoque:.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #22c55e;">
                <div class="metric-label">💰 Valor do Estoque</div>
                <div class="metric-value" style="color: #22c55e;">R$ {valor_estoque:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 📋 Estoque por Produto")
        
        # Tabela de estoque
        if not df_produtos.empty:
            df_estoque = df_produtos[['Nome', 'Categoria', 'Estoque_Atual', 'Estoque_Minimo', 'Preço']].copy()
            df_estoque['Valor_Total'] = df_estoque['Estoque_Atual'] * df_estoque['Preço']
            df_estoque['Status'] = df_estoque.apply(
                lambda x: '🔴 Crítico' if x['Estoque_Atual'] <= x['Estoque_Minimo'] else '🟢 OK', 
                axis=1
            )
            
            st.dataframe(
                df_estoque,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Nome": st.column_config.TextColumn("Produto"),
                    "Categoria": st.column_config.TextColumn("Categoria"),
                    "Estoque_Atual": st.column_config.NumberColumn("📦 Atual", format="%.0f"),
                    "Estoque_Minimo": st.column_config.NumberColumn("⚠️ Mínimo", format="%.0f"),
                    "Preço": st.column_config.NumberColumn("Preço Un.", format="R$ %.2f"),
                    "Valor_Total": st.column_config.NumberColumn("💰 Valor Total", format="R$ %.2f"),
                    "Status": st.column_config.TextColumn("Status")
                }
            )
    
    with tab2:
        st.markdown("### 📥 Registrar Movimentação de Estoque")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            with st.form("form_movimentacao", clear_on_submit=True):
                tipo_mov = st.selectbox(
                    "Tipo de Movimentação",
                    ["Entrada", "Saída"],
                    help="Entrada: aumenta estoque | Saída: diminui estoque"
                )
                
                opcoes_produtos = [nome for nome in df_produtos['Nome'].tolist() if nome and str(nome).strip()]
                produto_mov = st.selectbox("Produto", opcoes_produtos)
                
                quantidade_mov = st.number_input(
                    "Quantidade", 
                    min_value=0.1, 
                    step=1.0, 
                    format="%.1f"
                )
                
                motivos_entrada = ["Compra de fornecedor", "Devolução", "Ajuste de inventário", "Produção", "Outro"]
                motivos_saida = ["Venda", "Perda/Avaria", "Vencimento", "Ajuste de inventário", "Consumo interno", "Outro"]
                
                motivo_mov = st.selectbox(
                    "Motivo",
                    motivos_entrada if tipo_mov == "Entrada" else motivos_saida
                )
                
                obs_mov = st.text_input("Observação (opcional)")
                
                submitted_mov = st.form_submit_button(
                    f"{'📥 Registrar Entrada' if tipo_mov == 'Entrada' else '📤 Registrar Saída'}", 
                    use_container_width=True
                )
                
                if submitted_mov:
                    # Busca estoque atual do produto
                    estoque_atual = df_produtos[df_produtos['Nome'] == produto_mov]['Estoque_Atual'].values[0]
                    
                    # Calcula novo estoque
                    if tipo_mov == "Entrada":
                        novo_estoque = estoque_atual + quantidade_mov
                    else:
                        if quantidade_mov > estoque_atual:
                            st.error(f"❌ Quantidade maior que o estoque disponível ({estoque_atual:.0f})")
                        else:
                            novo_estoque = estoque_atual - quantidade_mov
                    
                    if tipo_mov == "Entrada" or quantidade_mov <= estoque_atual:
                        # Registra movimentação
                        id_mov = registrar_movimentacao(spreadsheet, tipo_mov, produto_mov, quantidade_mov, motivo_mov, obs_mov)
                        
                        if id_mov:
                            # Atualiza estoque do produto
                            if atualizar_estoque_produto(spreadsheet, produto_mov, novo_estoque):
                                st.success(f"✅ {tipo_mov} registrada! Novo estoque de '{produto_mov}': {novo_estoque:.0f}")
                                st.session_state.cache_key_produtos += 1
                                st.session_state.cache_key_movimentacoes += 1
                                time.sleep(1)
                                st.rerun()
        
        with col2:
            st.markdown("### 📜 Últimas Movimentações")
            
            df_mov = carregar_movimentacoes(spreadsheet, st.session_state.cache_key_movimentacoes)
            
            if not df_mov.empty:
                # Mostra últimas 10 movimentações
                df_ultimas = df_mov.tail(10).iloc[::-1]  # Inverte para mostrar mais recentes primeiro
                
                st.dataframe(
                    df_ultimas,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "ID_Mov": st.column_config.TextColumn("ID", width="small"),
                        "Data": st.column_config.TextColumn("Data"),
                        "Tipo": st.column_config.TextColumn("Tipo"),
                        "Produto": st.column_config.TextColumn("Produto"),
                        "Quantidade": st.column_config.NumberColumn("Qtd", format="%.0f"),
                        "Motivo": st.column_config.TextColumn("Motivo")
                    }
                )
            else:
                st.info("📭 Nenhuma movimentação registrada ainda.")
    
    with tab3:
        st.markdown("### ⚙️ Configurar Alertas por Email")
        
        st.info("""
        📧 **Configure alertas automáticos** para receber notificações quando produtos 
        atingirem o estoque crítico.
        """)
        
        # Configuração de email
        with st.expander("📨 Configurar Email de Alerta", expanded=True):
            email_destinatario = st.text_input(
                "Email para receber alertas",
                placeholder="seu-email@exemplo.com"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("🔔 Testar Alerta", use_container_width=True, disabled=not email_destinatario):
                    if not produtos_criticos.empty:
                        with st.spinner("Enviando email de teste..."):
                            sucesso, msg = enviar_alerta_email(email_destinatario, produtos_criticos)
                            if sucesso:
                                st.success(f"✅ {msg}")
                            else:
                                st.error(f"❌ {msg}")
                    else:
                        st.warning("Não há produtos com estoque crítico para enviar alerta.")
            
            with col_btn2:
                if st.button("💾 Salvar Configuração", use_container_width=True, disabled=not email_destinatario):
                    if salvar_config_alerta(spreadsheet, email_destinatario):
                        st.success("✅ Configuração salva!")
                    else:
                        st.error("❌ Erro ao salvar configuração")
        
        st.markdown("---")
        
        st.markdown("""
        ### 📋 Como configurar o envio de emails
        
        Para que os alertas funcionem, adicione ao seu `secrets.toml` ou no Streamlit Cloud:
        
        ```toml
        [email_config]
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        email_sender = "seu-email@gmail.com"
        email_password = "sua-senha-de-app"
        ```
        
        **⚠️ Para Gmail:**
        1. Ative a verificação em duas etapas
        2. Crie uma "Senha de App" em [myaccount.google.com](https://myaccount.google.com/apppasswords)
        3. Use essa senha no campo `email_password`
        """)


# ==================== MAIN ====================

def main():
    # Inicializa cache keys no session_state (para invalidar cache quando necessário)
    if 'cache_key_produtos' not in st.session_state:
        st.session_state.cache_key_produtos = 0
    if 'cache_key_compras' not in st.session_state:
        st.session_state.cache_key_compras = 0
    
    # Sidebar para navegação
    with st.sidebar:
        # Logo e título
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <img src="https://img.icons8.com/fluency/96/shopping-cart.png" width="70">
            <h2 style="margin: 0.5rem 0 0 0; color: #e2e8f0;">Sistema de Compras</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Menu de navegação bonito
        st.markdown("##### 📌 Menu")
        
        # Inicializa página selecionada
        if 'pagina_atual' not in st.session_state:
            st.session_state.pagina_atual = "🏠 Início"
        
        # CSS para botões do menu
        st.markdown("""
        <style>
            div[data-testid="stSidebar"] .stButton button {
                width: 100%;
                text-align: left;
                padding: 0.75rem 1rem;
                margin: 0.25rem 0;
                border-radius: 10px;
                border: none;
                background: transparent;
                color: #e2e8f0;
                font-size: 1rem;
                transition: all 0.3s ease;
            }
            div[data-testid="stSidebar"] .stButton button:hover {
                background: rgba(255,255,255,0.1);
                transform: translateX(5px);
            }
            div[data-testid="stSidebar"] .menu-ativo button {
                background: linear-gradient(135deg, #2d5a87 0%, #1e3a5f 100%) !important;
                box-shadow: 0 4px 12px rgba(45, 90, 135, 0.4);
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Definição do menu
        menu_items = [
            ("🏠 Início", "home"),
            ("📦 Produtos", "produtos"),
            ("🛒 Nova Compra", "compra"),
            ("📊 Estoque", "estoque"),
            ("📈 Histórico", "historico")
        ]
        
        # Botões do menu
        for label, key in menu_items:
            is_active = st.session_state.pagina_atual == label
            
            # Wrapper com classe para estilo ativo
            if is_active:
                st.markdown('<div class="menu-ativo">', unsafe_allow_html=True)
            
            if st.button(label, key=f"menu_{key}", use_container_width=True):
                st.session_state.pagina_atual = label
                st.rerun()
            
            if is_active:
                st.markdown('</div>', unsafe_allow_html=True)
        
        pagina = st.session_state.pagina_atual
        
        st.markdown("---")
        
        # Configurações em expander
        with st.expander("⚙️ Configurações", expanded=False):
            nome_planilha = st.text_input(
                "📋 Nome da Planilha",
                value="Sistema_Compras",
                help="Nome da planilha no Google Sheets"
            )
            
            st.markdown("")
            
            if st.button("🔄 Recarregar Dados", use_container_width=True):
                # Invalida todos os caches
                st.session_state.cache_key_produtos += 1
                st.session_state.cache_key_compras += 1
                st.session_state.abas_verificadas = False
                st.rerun()
            
            st.markdown("---")
            st.caption("v1.0 - Sistema de Compras")
    
    # Tenta conectar
    client = conectar_gsheets()
    
    if client is None:
        mostrar_config()
        return
    
    # Obtém/cria a planilha
    try:
        spreadsheet = obter_planilha(client, nome_planilha)
        garantir_abas(spreadsheet)
    except Exception as e:
        erro_str = str(e)
        st.error(f"Erro ao acessar planilha: {e}")
        
        # Mensagens de ajuda específicas para cada tipo de erro
        if "429" in erro_str or "RATE_LIMIT" in erro_str or "quota" in erro_str.lower():
            st.warning("""
            ⏱️ **Limite de requisições atingido!**
            
            O Google Sheets tem um limite de 60 requisições por minuto.
            
            **Soluções:**
            - Aguarde 1 minuto e clique em "🔄 Recarregar Dados"
            - Evite atualizar a página (F5) repetidamente
            """)
        elif "404" in erro_str or "not found" in erro_str.lower():
            st.info("💡 A planilha não foi encontrada. Verifique o nome da planilha.")
        elif "403" in erro_str or "permission" in erro_str.lower():
            st.info("""
            💡 **Sem permissão de acesso!**
            
            Verifique se você compartilhou a planilha com o email da conta de serviço.
            O email está no arquivo `credentials.json` no campo `client_email`.
            """)
        else:
            st.info("💡 Verifique se você compartilhou a planilha com o email da conta de serviço.")
        return
    
    # Roteamento de páginas
    if pagina == "🏠 Início":
        st.markdown("""
        <div class="main-header">
            <h1>🏠 Bem-vindo ao Sistema de Compras</h1>
            <p>Gerencie produtos e registre suas compras de forma simples</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ### 🚀 Como usar:
        
        1. **📦 Produtos** - Cadastre os produtos da sua loja
        2. **🛒 Nova Compra** - Registre suas compras adicionando produtos ao carrinho
        3. **📊 Histórico** - Visualize o histórico completo de compras
        
        ---
        
        💡 **Dica:** Todos os dados são salvos automaticamente no Google Sheets!
        """)
        
        # Mostra estatísticas rápidas
        df_produtos = carregar_produtos(spreadsheet, st.session_state.cache_key_produtos)
        df_compras = carregar_compras(spreadsheet, st.session_state.cache_key_compras)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Produtos Cadastrados</div>
                <div class="metric-value">{len(df_produtos)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            num_compras = df_compras['ID_Compra'].nunique() if not df_compras.empty and 'ID_Compra' in df_compras.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Compras Realizadas</div>
                <div class="metric-value">{num_compras}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total = df_compras['Total'].sum() if not df_compras.empty and 'Total' in df_compras.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total em Compras</div>
                <div class="metric-value">R$ {total:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
    
    elif pagina == "📦 Produtos":
        pagina_produtos(spreadsheet)
    
    elif pagina == "🛒 Nova Compra":
        pagina_compras(spreadsheet)
    
    elif pagina == "📊 Estoque":
        pagina_estoque(spreadsheet)
    
    elif pagina == "📈 Histórico":
        pagina_historico(spreadsheet)


if __name__ == "__main__":
    main()

