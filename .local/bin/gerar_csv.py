#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PASSO 1: GERAR CSV UNIVERSAL DE PROSPECTOS
Gera arquivo CSV padronizado para importação em qualquer CRM
100% offline, sem dependências de API
"""

import pandas as pd
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Pastas
OUTPUT_DIR = "1_prospectos_csv"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 80)
print("🚀 GERADOR CSV UNIVERSAL DE PROSPECTOS")
print("   Compatível com: HubSpot, EspoCRM, Salesforce, Odoo, etc.")
print("=" * 80)

# Dicionários
CNAES_ALVO = {
    '01': 'Agropecuária', '46': 'Comércio Atacadista', '47': 'Comércio Varejista',
    '10': 'Indústria Alimentos', '11': 'Indústria Bebidas',
    '17': 'Indústria Celulose/Papel', '22': 'Indústria Plástico/Borracha', 
    '26': 'Indústria Equipamentos', '32': 'Indústria Diversos'
}

QUALIFICACOES_SOCIO = {
    '05': 'Sócio-Administrador', '06': 'Sócio-Gerente', '07': 'Sócio',
    '08': 'Sócio-Comanditado', '09': 'Sócio-Comanditário', '10': 'Sócio-Capitalista',
    '11': 'Sócio-Industrial', '12': 'Sócio-Comercial', '13': 'Sócio de Indústria',
    '14': 'Sócio de Comércio', '15': 'Sócio de Serviços', '16': 'Sócio-Especial',
    '17': 'Sócio-Fundador', '18': 'Sócio-Investidor', '19': 'Sócio-Majoritário',
    '20': 'Sócio-Minoritário', '21': 'Sócio-Responsável', '22': 'Sócio-Cotista',
    '23': 'Sócio-Ostensivo', '24': 'Sócio-Secretário', '25': 'Sócio-Tesoureiro',
    '26': 'Sócio-Presidente', '27': 'Sócio-Vice-Presidente', '28': 'Sócio-Diretor',
    '29': 'Sócio-Superintendente', '30': 'Sócio-Gerente Geral', '31': 'Sócio-Executivo',
    '32': 'Sócio-Operacional', '33': 'Sócio-Estratégico', '34': 'Sócio-Financeiro',
    '35': 'Sócio-Técnico', '36': 'Sócio-Comercial', '37': 'Sócio-Marketing',
    '38': 'Sócio-Produção', '39': 'Sócio-Logística', '40': 'Sócio-RH',
    '41': 'Sócio-Jurídico', '42': 'Sócio-TI', '43': 'Sócio-Inovação',
    '44': 'Sócio-Sustentabilidade', '45': 'Sócio-Relações Institucionais',
    '46': 'Sócio-Compliance', '47': 'Sócio-Governança', '48': 'Sócio-Riscos',
    '49': 'Sócio-Controladoria', '50': 'Sócio-Auditoria', '51': 'Sócio-Planejamento',
    '52': 'Sócio-Negócios', '53': 'Sócio-Desenvolvimento', '54': 'Sócio-Pesquisa',
    '55': 'Sócio-Qualidade', '56': 'Sócio-Segurança', '57': 'Sócio-Meio Ambiente',
    '58': 'Sócio-Saúde', '59': 'Sócio-Educação', '60': 'Sócio-Cultura',
    '61': 'Sócio-Esportes', '62': 'Sócio-Lazer', '63': 'Sócio-Turismo',
    '64': 'Sócio-Entretenimento', '65': 'Sócio-Moda', '66': 'Sócio-Beleza',
    '67': 'Sócio-Gastronomia', '68': 'Sócio-Agronegócio', '69': 'Sócio-Imobiliário',
    '70': 'Sócio-Construção', '71': 'Sócio-Energia', '72': 'Sócio-Mineração',
    '73': 'Sócio-Química', '74': 'Sócio-Farmacêutico', '75': 'Sócio-Médico',
    '76': 'Sócio-Odontológico', '77': 'Sócio-Veterinário', '78': 'Sócio-Contábil',
    '79': 'Sócio-Econômico', '80': 'Sócio-Atuário', '81': 'Sócio-Estatístico',
    '82': 'Sócio-Engenharia', '83': 'Sócio-Arquitetura', '84': 'Sócio-Agronomia',
    '85': 'Sócio-Medicina', '86': 'Sócio-Odontologia', '87': 'Sócio-Farmácia',
    '88': 'Sócio-Enfermagem', '89': 'Sócio-Fisioterapia', '90': 'Sócio-Nutrição',
    '91': 'Sócio-Psicologia', '92': 'Sócio-Serviço Social', '93': 'Sócio-Direito',
    '94': 'Sócio-Jornalismo', '95': 'Sócio-Publicidade', '96': 'Sócio-Propaganda',
    '97': 'Sócio-Marketing Digital', '98': 'Sócio-Design', '99': 'Sócio-Arte',
    '00': 'Não Informado', '01': 'Representante Legal', '02': 'Procurador',
    '03': 'Administrador Judicial', '04': 'Inventariante'
}

PORTE_EMPRESA = {
    '00': 'Não Informado', '01': 'Micro Empresa', '02': 'Pequeno Porte',
    '03': 'Médio Porte', '04': 'Grande Porte', '05': 'MEI', '06': 'EPP', '07': 'Demais'
}

NATUREZA_JURIDICA = {
    '2046': 'Sociedade Anônima Aberta', '2054': 'Sociedade Anônima Fechada',
    '2062': 'Sociedade Empresária Limitada', '2143': 'Empresário Individual',
    '2240': 'Sociedade Simples Limitada'
}

NATUREZAS_ERP = ['2062', '2240', '2143', '2046', '2054']

# Funções utilitárias
def sanitizar_nome_arquivo(nome):
    nome = re.sub(r'[\\/:*?"<>|]', '_', nome)
    nome = re.sub(r'\s+', '_', nome)
    return nome.strip('_')

def validar_email(email):
    if not email or pd.isna(email) or str(email).strip() == '':
        return {'valido': False, 'email': '', 'status': 'Vazio'}
    email = str(email).strip().lower()
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(padrao, email):
        dominios_ruins = ['tempmail.com', '10minutemail.com', 'guerrillamail.com', 
                         'fakeemail.com', 'throwaway.com', 'yopmail.com', 'mailinator.com']
        dominio = email.split('@')[1]
        if dominio in dominios_ruins:
            return {'valido': False, 'email': email, 'status': 'Descartável'}
        return {'valido': True, 'email': email, 'status': 'Válido'}
    return {'valido': False, 'email': email, 'status': 'Inválido'}

def formatar_telefone(ddd, numero):
    if not numero or pd.isna(numero):
        return ''
    ddd = str(ddd).strip() if ddd else ''
    num = str(numero).strip()
    num_limpo = re.sub(r'\D', '', num)
    ddd_limpo = re.sub(r'\D', '', ddd)
    if not num_limpo:
        return ''
    if len(num_limpo) == 9:
        formatado = f"{num_limpo[:5]}-{num_limpo[5:]}"
    elif len(num_limpo) == 8:
        formatado = f"{num_limpo[:4]}-{num_limpo[4:]}"
    elif len(num_limpo) > 9:
        formatado = f"{num_limpo[-9:-4]}-{num_limpo[-4:]}"
    else:
        formatado = num_limpo
    if ddd_limpo:
        return f"({ddd_limpo}) {formatado}"
    return formatado

def agregar_socios(group):
    resultado = {}
    for i, (idx, row) in enumerate(group.iterrows(), 1):
        if i > 3:
            break
        nome_socio = str(row.get('nome_socio', '')).strip()
        cod_qualif = str(row.get('qualificacao_socio', '')).strip()
        qualif_texto = QUALIFICACOES_SOCIO.get(cod_qualif, f'Código {cod_qualif}')
        resultado[f'Socio_{i}_Nome'] = nome_socio
        resultado[f'Socio_{i}_Qualif_Cod'] = cod_qualif
        resultado[f'Socio_{i}_Qualif_Texto'] = qualif_texto
    for i in range(len(group) + 1, 4):
        resultado[f'Socio_{i}_Nome'] = ''
        resultado[f'Socio_{i}_Qualif_Cod'] = ''
        resultado[f'Socio_{i}_Qualif_Texto'] = ''
    resultado['Total_Socios'] = len(group)
    return pd.Series(resultado)

def parse_data_input(texto, nome_campo):
    if not texto.strip():
        return None
    try:
        return datetime.strptime(texto.strip(), '%d/%m/%Y')
    except ValueError:
        print(f"   ⚠️ {nome_campo} inválida, ignorando")
        return None

# =============================================================================
# CONFIGURAÇÕES DO USUÁRIO
# =============================================================================

print("\n" + "=" * 80)
print("⚙️  CONFIGURAÇÕES DE FILTRO")
print("=" * 80)

# UF
print("\n🌍 Identificando estados...")
ufs_validas = []
try:
    for chunk in pd.read_csv('estabelecimentos.csv', sep=';', encoding='latin1', 
                             header=None, usecols=[19], chunksize=100000, 
                             dtype=str, on_bad_lines='skip', quoting=3):
        chunk[19] = chunk[19].astype(str).str.replace('"', '').str.strip()
        ufs_validas.extend(chunk[19].dropna().unique())
    ufs_validas = sorted(list(set([uf for uf in ufs_validas if len(str(uf)) == 2 and str(uf).isalpha()])))
    print(f"   Encontrados: {', '.join(ufs_validas[:10])}{'...' if len(ufs_validas) > 10 else ''}")
except:
    ufs_validas = ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']

estados_input = input("\n👉 UF(s) desejadas (ex: GO,SP) ou Enter para TODAS: ").upper().replace(" ", "")
ESTADOS_ALVO = estados_input.split(',') if estados_input else ufs_validas
print(f"📍 Selecionado: {len(ESTADOS_ALVO)} estado(s)")

# Data
print("\n📅 Filtro por Data de Abertura")
data_inicio = parse_data_input(input("   Data inicial (DD/MM/AAAA): "), "Data inicial")
data_fim = parse_data_input(input("   Data final (DD/MM/AAAA): "), "Data final")

# Capital
print("\n💰 Filtro por Capital Social")
cap_min = input("   Capital MÍNIMO (padrão: 100000): ").strip()
CAPITAL_MIN = float(cap_min) if cap_min else 100000
cap_max = input("   Capital MÁXIMO (Enter=sem limite): ").strip()
CAPITAL_MAX = float(cap_max) if cap_max else float('inf')
print(f"   ✅ R$ {CAPITAL_MIN:,.0f} a R$ {CAPITAL_MAX:,.0f}".replace(',', '.'))

# Porte
print("\n📊 Filtro por Porte")
print("   00=N/I | 01=Micro | 02=Pequeno | 03=Médio | 04=Grande | 05=MEI | 06=EPP")
porte_input = input("   Porte(s) (ex: 02,03,04) ou Enter=TODOS: ").strip()
PORTES_ALVO = porte_input.split(',') if porte_input else list(PORTE_EMPRESA.keys())

# CNAE Secundário
print("\n🏭 Filtro por CNAE Secundário (opcional)")
cnae_sec_input = input("   CNAE(s) secundário(s) (ex: 6202300): ").strip()
CNAE_SEC_ALVO = [c.strip() for c in cnae_sec_input.split(',')] if cnae_sec_input else []

# Município
print("\n📍 Filtro por Município (opcional)")
mun_input = input("   Nome do município: ").strip().upper()
MUNICIPIO_ALVO = mun_input if mun_input else None

# Validação
print("\n✅ Opções de Validação")
validar_emails = input("   Validar e-mails? (S/N): ").upper().startswith('S')
formatar_tels = input("   Formatar telefones? (S/N): ").upper().startswith('S')

# =============================================================================
# PROCESSAMENTO
# =============================================================================

print("\n📂 Carregando municípios...")
municipios_dict = {}
try:
    df_mun = pd.read_csv('municipios.csv', sep=';', encoding='latin1',
                        header=None, names=['codigo', 'nome'], dtype=str, on_bad_lines='skip', quoting=3)
    df_mun['codigo'] = df_mun['codigo'].astype(str).str.replace('"', '').str.strip()
    df_mun['nome'] = df_mun['nome'].astype(str).str.replace('"', '').str.strip().str.upper()
    municipios_dict = dict(zip(df_mun['codigo'], df_mun['nome']))
    print(f"✅ {len(municipios_dict)} municípios")
except Exception as e:
    print(f"⚠️ {e}")

print(f"\n📂 Carregando empresas...")
empresas_chunks = []
for chunk in pd.read_csv('empresas.csv', sep=';', encoding='latin1', header=None, chunksize=100000,
                         names=['cnpj_base', 'razao_social', 'natureza', 'qualificacao', 'capital', 'porte', 'ente'],
                         dtype=str, on_bad_lines='skip', quoting=3):
    for col in chunk.columns:
        chunk[col] = chunk[col].astype(str).str.replace('"', '').str.strip()
    chunk['capital_num'] = chunk['capital'].apply(
        lambda x: float(str(x).replace('.', '').replace(',', '.')) if x and str(x).replace('.', '').replace(',', '').replace('-', '').isdigit() else 0
    )
    filtro_cap = (chunk['capital_num'] >= CAPITAL_MIN)
    if CAPITAL_MAX != float('inf'):
        filtro_cap &= (chunk['capital_num'] <= CAPITAL_MAX)
    filtro = chunk['natureza'].isin(NATUREZAS_ERP) & filtro_cap & chunk['porte'].isin(PORTES_ALVO)
    if filtro.any():
        empresas_chunks.append(chunk[filtro])

df_empresas = pd.concat(empresas_chunks, ignore_index=True)
df_empresas['Porte_Descricao'] = df_empresas['porte'].map(PORTE_EMPRESA).fillna('Não Informado')
df_empresas['Natureza_Descricao'] = df_empresas['natureza'].map(NATUREZA_JURIDICA).fillna('Outra')
print(f"✅ {len(df_empresas):,} empresas")

print(f"\n📂 Carregando estabelecimentos...")
colunas_estab = ['cnpj_base', 'cnpj_ordem', 'cnpj_dv', 'matriz_filial', 'nome_fantasia', 
                 'situacao', 'data_situacao', 'motivo_situacao', 'nome_cidade_exterior', 
                 'pais', 'data_inicio', 'cnae_principal', 'cnae_secundario', 'tipo_logradouro', 
                 'logradouro', 'numero', 'complemento', 'bairro', 'cep', 'uf', 'municipio', 
                 'ddd1', 'telefone1', 'ddd2', 'telefone2', 'ddd_fax', 'fax', 'email', 
                 'situacao_especial', 'data_situacao_especial']

estab_chunks = []
cnpj_validos = set(df_empresas['cnpj_base'])
processado = 0

for chunk in pd.read_csv('estabelecimentos.csv', sep=';', encoding='latin1', header=None, 
                         chunksize=50000, names=colunas_estab, dtype=str, on_bad_lines='skip', quoting=3):
    for col in chunk.columns:
        chunk[col] = chunk[col].astype(str).str.replace('"', '').str.strip()
    
    chunk['data_inicio_dt'] = pd.to_datetime(chunk['data_inicio'], format='%Y%m%d', errors='coerce')
    chunk['cnae_2dig'] = chunk['cnae_principal'].str[:2]
    
    filtro = (chunk['cnpj_base'].isin(cnpj_validos) & (chunk['matriz_filial'] == '1') & 
              (chunk['situacao'] == '02') & chunk['uf'].isin(ESTADOS_ALVO) & 
              chunk['cnae_2dig'].isin(list(CNAES_ALVO.keys())))
    
    if CNAE_SEC_ALVO:
        filtro_cnae_sec = chunk['cnae_secundario'].str.contains('|'.join(CNAE_SEC_ALVO), na=False)
        filtro &= filtro_cnae_sec
    
    if data_inicio:
        filtro &= (chunk['data_inicio_dt'] >= data_inicio)
    if data_fim:
        filtro &= (chunk['data_inicio_dt'] <= data_fim)
    
    if MUNICIPIO_ALVO:
        chunk['nome_mun_temp'] = chunk['municipio'].map(municipios_dict).fillna('')
        filtro &= (chunk['nome_mun_temp'].str.contains(MUNICIPIO_ALVO, case=False, na=False))
    
    if filtro.any():
        estab_chunks.append(chunk[filtro])
    
    processado += len(chunk)
    if processado % 1000000 == 0:
        print(f"   Processado: {processado:,} | Encontrados: {sum(len(e) for e in estab_chunks)}")

if not estab_chunks:
    print("❌ Nenhum estabelecimento encontrado")
    sys.exit(1)

df_estab = pd.concat(estab_chunks, ignore_index=True)
df_estab['Nome_Municipio'] = df_estab['municipio'].map(municipios_dict).fillna(df_estab['municipio'])
df_estab['Ramo'] = df_estab['cnae_2dig'].map(CNAES_ALVO)
print(f"✅ {len(df_estab):,} estabelecimentos")

# Validação de e-mails
if validar_emails:
    print("\n📧 Validando e-mails...")
    df_estab['Email_Validacao'] = df_estab['email'].apply(validar_email)
    df_estab['Email_Status'] = df_estab['Email_Validacao'].apply(lambda x: x['status'])
    df_estab['Email_Limpo'] = df_estab['Email_Validacao'].apply(lambda x: x['email'] if x['valido'] else '')
    print(f"   Válidos: {(df_estab['Email_Status'] == 'Válido').sum()}")

# Formatação de telefones
if formatar_tels:
    print("\n📱 Formatando telefones...")
    df_estab['telefone_formatado'] = df_estab.apply(
        lambda x: formatar_telefone(x['ddd1'], x['telefone1']), axis=1
    )

print(f"\n📂 Carregando sócios...")
try:
    socios_chunks = []
    cnpj_estab = set(df_estab['cnpj_base'])
    for chunk in pd.read_csv('socios.csv', sep=';', encoding='latin1', header=None, chunksize=100000,
                            names=['cnpj_base', 'identificador_socio', 'nome_socio', 'cnpj_cpf_socio',
                                   'qualificacao_socio', 'data_entrada', 'pais', 'representante',
                                   'nome_representante', 'qualificacao_representante', 'faixa_etaria'],
                            dtype=str, on_bad_lines='skip', quoting=3):
        for col in chunk.columns:
            chunk[col] = chunk[col].astype(str).str.replace('"', '').str.strip()
        filtro = chunk['cnpj_base'].isin(cnpj_estab)
        if filtro.any():
            socios_chunks.append(chunk[filtro])
    
    if socios_chunks:
        df_socios_raw = pd.concat(socios_chunks, ignore_index=True)
        df_socios = df_socios_raw.groupby('cnpj_base').apply(agregar_socios).reset_index()
        print(f"✅ {len(df_socios)} empresas com sócios")
    else:
        df_socios = pd.DataFrame()
except Exception as e:
    print(f"⚠️ {e}")
    df_socios = pd.DataFrame()

# Cruzamento
print(f"\n🔗 Cruzando dados...")
df_final = pd.merge(df_estab, df_empresas, on='cnpj_base', how='left')
if not df_socios.empty:
    df_final = pd.merge(df_final, df_socios, on='cnpj_base', how='left')

df_final['CNPJ'] = df_final.apply(
    lambda x: f"{str(x['cnpj_base']).zfill(8)}.{str(x['cnpj_ordem']).zfill(4)}/{str(x['cnpj_dv']).zfill(2)}", axis=1
)
df_final['Capital_Social'] = df_final['capital_num'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
df_final['Data_Abertura'] = df_final['data_inicio_dt'].dt.strftime('%d/%m/%Y')

# =============================================================================
# GERAÇÃO DO CSV UNIVERSAL
# =============================================================================

print(f"\n💾 Gerando CSV Universal...")

# Colunas padronizadas para CRMs (nomes em inglês = compatibilidade máxima)
colunas_crm = {
    'CNPJ': 'cnpj',
    'Razão Social': 'company_name',
    'Nome Fantasia': 'trading_name',
    'Data Abertura': 'opening_date',
    'Capital Social': 'capital_formatted',
    'Capital_Numerico': 'capital_numeric',
    'Porte': 'company_size',
    'Natureza Jurídica': 'legal_nature',
    'CNAE Principal': 'cnae_primary',
    'CNAE Secundário': 'cnae_secondary',
    'Ramo de Atividade': 'business_sector',
    'Município': 'city',
    'UF': 'state',
    'Logradouro': 'street',
    'Número': 'number',
    'Complemento': 'complement',
    'Bairro': 'neighborhood',
    'CEP': 'zip_code',
    'Telefone': 'phone',
    'E-mail Válido': 'email_valid',
    'Status E-mail': 'email_status',
    'Socio_1_Nome': 'partner_1_name',
    'Socio_1_Qualif_Texto': 'partner_1_role',
    'Socio_2_Nome': 'partner_2_name',
    'Socio_2_Qualif_Texto': 'partner_2_role',
    'Socio_3_Nome': 'partner_3_name',
    'Socio_3_Qualif_Texto': 'partner_3_role',
    'Total_Socios': 'total_partners',
    'APROVADO_PARA_IMPORTACAO': 'approved_for_import',
    'OBSERVACOES': 'notes'
}

# Preparar DataFrame para exportação
df_export = pd.DataFrame()

# Mapear colunas existentes
mapeamento_colunas = {
    'CNPJ': 'CNPJ',
    'razao_social': 'Razão Social',
    'nome_fantasia': 'Nome Fantasia',
    'Data_Abertura': 'Data Abertura',
    'Capital_Social': 'Capital Social',
    'capital_num': 'Capital_Numerico',
    'Porte_Descricao': 'Porte',
    'Natureza_Descricao': 'Natureza Jurídica',
    'cnae_principal': 'CNAE Principal',
    'cnae_secundario': 'CNAE Secundário',
    'Ramo': 'Ramo de Atividade',
    'Nome_Municipio': 'Município',
    'uf': 'UF',
    'logradouro': 'Logradouro',
    'numero': 'Número',
    'complemento': 'Complemento',
    'bairro': 'Bairro',
    'cep': 'CEP'
}

if formatar_tels:
    mapeamento_colunas['telefone_formatado'] = 'Telefone'
else:
    mapeamento_colunas['ddd1'] = 'DDD'
    mapeamento_colunas['telefone1'] = 'Telefone'

if validar_emails:
    mapeamento_colunas['Email_Limpo'] = 'E-mail Válido'
    mapeamento_colunas['Email_Status'] = 'Status E-mail'
else:
    mapeamento_colunas['email'] = 'E-mail'

if not df_socios.empty:
    for i in range(1, 4):
        mapeamento_colunas[f'Socio_{i}_Nome'] = f'Socio_{i}_Nome'
        mapeamento_colunas[f'Socio_{i}_Qualif_Texto'] = f'Socio_{i}_Qualif_Texto'
    mapeamento_colunas['Total_Socios'] = 'Total_Socios'

# Criar DataFrame com colunas renomeadas
for origem, destino in mapeamento_colunas.items():
    if origem in df_final.columns:
        df_export[destino] = df_final[origem]

# Adicionar colunas de controle
df_export['APROVADO_PARA_IMPORTACAO'] = 'PENDENTE'
df_export['OBSERVACOES'] = ''

# Ordenar por capital (maior primeiro)
df_export = df_export.sort_values('Capital_Numerico', ascending=False)

# Gerar arquivo CSV
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
ufs_nome = sanitizar_nome_arquivo("_".join(ESTADOS_ALVO) if len(ESTADOS_ALVO) < 4 else f"{len(ESTADOS_ALVO)}EST")

nome_csv = f"{OUTPUT_DIR}/PROSPECTOS_{ufs_nome}_{len(df_export)}_{timestamp}.csv"

# Salvar CSV com encoding UTF-8 (compatível com todos os sistemas)
df_export.to_csv(nome_csv, index=False, encoding='utf-8-sig', sep=';')

# Também gerar versão Excel para análise mais fácil
nome_excel = f"{OUTPUT_DIR}/PROSPECTOS_{ufs_nome}_{len(df_export)}_{timestamp}.xlsx"
df_export.to_excel(nome_excel, index=False, sheet_name='Prospectos')

print(f"\n✅ Arquivos gerados:")
print(f"   📄 CSV:  {nome_csv}")
print(f"   📊 Excel: {nome_excel}")

# Resumo
print("\n" + "=" * 80)
print("✅ CSV UNIVERSAL GERADO COM SUCESSO!")
print("=" * 80)
print(f"🏢 Total: {len(df_export):,} empresas")
print(f"\n📁 Arquivos em: ./{OUTPUT_DIR}/")
print(f"\n📝 PRÓXIMOS PASSOS:")
print(f"   1. Abra o arquivo Excel para análise visual")
print(f"   2. Na coluna 'APROVADO_PARA_IMPORTACAO', marque:")
print(f"      → 'SIM' para aprovar")
print(f"      → 'NAO' para rejeitar")
print(f"   3. Salve como CSV (se editou o Excel)")
print(f"   4. Importe no CRM de sua escolha:")
print(f"      • HubSpot: Settings → Import & Export → Import Contacts")
print(f"      • EspoCRM: Administration → Import")
print(f"      • Salesforce: Setup → Data Import Wizard")
print(f"      • Odoo: Settings → Import")
print(f"      • Planilha Google: File → Import")
print(f"\n💡 DICA: O arquivo CSV usa ';' como separador e UTF-8")
print("=" * 80)