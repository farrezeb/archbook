#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GERADOR CSV UNIVERSAL DE PROSPECTOS - SERPRO EDITION (DuckDB)
Reescrito com DuckDB: menor uso de RAM, 3-10x mais rapido
Dependencias: pip install duckdb pandas openpyxl
"""

import os
import re
import sys
import glob
import duckdb
import pandas as pd
from datetime import datetime
from pathlib import Path

# ─── Configuracoes ───────────────────────────────────────────────────────────
OUTPUT_DIR = "1_prospectos_csv"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Dicionarios ─────────────────────────────────────────────────────────────
CNAES_ALVO = {
    '01': 'Agropecuaria',
    '46': 'Comercio Atacadista',
    '47': 'Comercio Varejista',
    '10': 'Industria Alimentos',
    '11': 'Industria Bebidas',
    '16': 'Industria Celulose/Papel',
    '31': 'Industria Diversos',
}

# Separados corretamente (sem chaves duplicadas)
QUALIFICACOES_SOCIO = {
    '05': 'Socio-Administrador',    '06': 'Socio-Gerente',
    '07': 'Socio',                  '08': 'Socio-Comanditado',
    '09': 'Socio-Comanditario',     '10': 'Socio-Capitalista',
    '11': 'Socio-Industrial',       '12': 'Socio-Comercial',
    '13': 'Socio de Industria',     '14': 'Socio de Comercio',
    '15': 'Socio de Servicos',      '16': 'Socio-Especial',
    '17': 'Socio-Fundador',         '18': 'Socio-Investidor',
    '19': 'Socio-Majoritario',      '20': 'Socio-Minoritario',
    '21': 'Socio-Responsavel',      '22': 'Socio-Cotista',
    '23': 'Socio-Ostensivo',        '28': 'Socio-Diretor',
    '49': 'Socio-Controladoria',    '50': 'Socio-Auditoria',
}

QUALIFICACOES_REPRESENTANTE = {
    '00': 'Nao Informado',          '01': 'Representante Legal',
    '02': 'Procurador',             '03': 'Administrador Judicial',
    '04': 'Inventariante',
}

PORTE_EMPRESA = {
    '00': 'Nao Informado', '01': 'Micro Empresa',  '02': 'Pequeno Porte',
    '03': 'Medio Porte',   '04': 'Grande Porte',   '05': 'MEI',
    '06': 'EPP',           '07': 'Demais',
}

NATUREZA_JURIDICA = {
    '2046': 'Sociedade Anonima Aberta',
    '2054': 'Sociedade Anonima Fechada',
    '2062': 'Sociedade Empresaria Limitada',
    '2143': 'Empresario Individual',
    '2240': 'Sociedade Simples Limitada',
}

NATUREZAS_ERP = ['2062', '2240', '2143', '2046', '2054']

# ─── Helpers ─────────────────────────────────────────────────────────────────
def sanitizar(nome: str) -> str:
    nome = re.sub(r'[\\/:*?"<>|]', '_', nome)
    nome = re.sub(r'\s+', '_', nome)
    return nome.strip('_')

def validar_email(email) -> dict:
    if not email or pd.isna(email) or str(email).strip() == '':
        return {'valido': False, 'email': '', 'status': 'Vazio'}
    email = str(email).strip().lower()
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(padrao, email):
        descartaveis = {'tempmail.com', '10minutemail.com', 'guerrillamail.com',
                        'fakeemail.com', 'throwaway.com', 'yopmail.com', 'mailinator.com'}
        dominio = email.split('@')[1]
        if dominio in descartaveis:
            return {'valido': False, 'email': email, 'status': 'Descartavel'}
        return {'valido': True, 'email': email, 'status': 'Valido'}
    return {'valido': False, 'email': email, 'status': 'Invalido'}

def formatar_telefone(ddd, numero) -> str:
    if not numero or pd.isna(numero):
        return ''
    ddd_l = re.sub(r'\D', '', str(ddd) if ddd else '')
    num_l = re.sub(r'\D', '', str(numero))
    if not num_l:
        return ''
    if len(num_l) == 9:
        fmt = num_l[:5] + '-' + num_l[5:]
    elif len(num_l) == 8:
        fmt = num_l[:4] + '-' + num_l[4:]
    elif len(num_l) > 9:
        fmt = num_l[-9:-4] + '-' + num_l[-4:]
    else:
        fmt = num_l
    return ('(' + ddd_l + ') ' + fmt) if ddd_l else fmt

def parse_data(texto: str, nome: str):
    if not texto.strip():
        return None
    try:
        return datetime.strptime(texto.strip(), '%d/%m/%Y')
    except ValueError:
        print('   ⚠️  ' + nome + ' invalida, ignorando')
        return None

def detectar_arquivos() -> dict:
    return {
        'empresas':          sorted(glob.glob('empresas[0-9].csv')),
        'estabelecimentos':  sorted(glob.glob('estabelecimentos[0-9].csv')),
        'socios':            sorted(glob.glob('socios[0-9].csv')),
        'municipios':        glob.glob('municipios.csv'),
    }

def agregar_socios(group: pd.DataFrame) -> pd.Series:
    """Agrega ate 3 socios por CNPJ base."""
    resultado = {}
    ultimo_i = 0
    for i, (_, row) in enumerate(group.iterrows(), 1):
        if i > 3:
            break
        ultimo_i = i
        cod = str(row.get('qualificacao_socio', '')).strip()
        resultado['Socio_' + str(i) + '_Nome']        = str(row.get('nome_socio', '')).strip()
        resultado['Socio_' + str(i) + '_Qualif_Cod']  = cod
        resultado['Socio_' + str(i) + '_Qualif_Texto'] = QUALIFICACOES_SOCIO.get(cod, 'Codigo ' + cod)
    # Preenche slots vazios
    for i in range(ultimo_i + 1, 4):
        resultado['Socio_' + str(i) + '_Nome']        = ''
        resultado['Socio_' + str(i) + '_Qualif_Cod']  = ''
        resultado['Socio_' + str(i) + '_Qualif_Texto'] = ''
    resultado['Total_Socios'] = len(group)
    return pd.Series(resultado)

# ─── Leitura via pandas → DuckDB ─────────────────────────────────────────────
def ler_csv_duckdb(con: duckdb.DuckDBPyConnection, arquivos: list, colunas: list,
                   alias: str) -> str:
    """
    Le CSVs do SERPRO via pandas (trata corretamente aspas internas)
    e registra o DataFrame como tabela no DuckDB para queries SQL.
    """
    chunks = []
    for arq in arquivos:
        print('      ' + os.path.basename(arq) + '...', end=' ', flush=True)
        try:
            for chunk in pd.read_csv(
                arq, sep=';', encoding='latin1', header=None,
                names=colunas, dtype=str, quoting=3,
                on_bad_lines='skip', chunksize=100_000, low_memory=False
            ):
                for col in chunk.columns:
                    chunk[col] = chunk[col].astype(str).str.replace('"', '', regex=False).str.strip()
                chunks.append(chunk)
            print('OK')
        except Exception as e:
            print('ERRO: ' + str(e))

    if not chunks:
        print('   AVISO: nenhum dado carregado para ' + alias)
        df = pd.DataFrame(columns=colunas)
    else:
        df = pd.concat(chunks, ignore_index=True)

    con.register(alias, df)
    print('   ' + alias + ': ' + str(len(df)) + ' registros carregados')
    return alias

# ─── Main ────────────────────────────────────────────────────────────────────
def main():
    print('=' * 80)
    print('GERADOR CSV UNIVERSAL DE PROSPECTOS - SERPRO (DuckDB Edition)')
    print('=' * 80)

    arquivos = detectar_arquivos()
    print('\nArquivos detectados:')
    print('   Empresas:         ' + str(len(arquivos['empresas'])))
    print('   Estabelecimentos: ' + str(len(arquivos['estabelecimentos'])))
    print('   Socios:           ' + str(len(arquivos['socios'])))
    print('   Municipios:       ' + ('✓' if arquivos['municipios'] else '✗'))

    if not arquivos['empresas'] or not arquivos['estabelecimentos']:
        print('\nERRO: Arquivos empresasX.csv / estabelecimentosX.csv nao encontrados.')
        sys.exit(1)

    # ── Inicializar DuckDB (memoria limitada a 4 GB para seguranca) ──────────
    con = duckdb.connect()
    con.execute("SET memory_limit='4GB'")
    con.execute("SET threads TO 2")

    # ── Colunas ──────────────────────────────────────────────────────────────
    cols_empresas = ['cnpj_base', 'razao_social', 'natureza', 'qualificacao',
                     'capital', 'porte', 'ente']

    cols_estab = ['cnpj_base', 'cnpj_ordem', 'cnpj_dv', 'matriz_filial', 'nome_fantasia',
                  'situacao', 'data_situacao', 'motivo_situacao', 'nome_cidade_exterior',
                  'pais', 'data_inicio', 'cnae_principal', 'cnae_secundario', 'tipo_logradouro',
                  'logradouro', 'numero', 'complemento', 'bairro', 'cep', 'uf', 'municipio',
                  'ddd1', 'telefone1', 'ddd2', 'telefone2', 'ddd_fax', 'fax', 'email',
                  'situacao_especial', 'data_situacao_especial']

    cols_socios = ['cnpj_base', 'identificador_socio', 'nome_socio', 'cnpj_cpf_socio',
                   'qualificacao_socio', 'data_entrada', 'pais_socio', 'representante',
                   'nome_representante', 'qualificacao_representante', 'faixa_etaria']

    # ── Registrar views ──────────────────────────────────────────────────────
    print('\nRegistrando arquivos no DuckDB...')
    ler_csv_duckdb(con, arquivos['empresas'], cols_empresas, 'v_empresas')
    ler_csv_duckdb(con, arquivos['estabelecimentos'], cols_estab, 'v_estab')
    if arquivos['socios']:
        ler_csv_duckdb(con, arquivos['socios'], cols_socios, 'v_socios')
    if arquivos['municipios']:
        ler_csv_duckdb(con, arquivos['municipios'], ['codigo_mun', 'nome_mun'], 'v_municipios')
    print('   OK')

    # ── Detectar UFs disponiveis ─────────────────────────────────────────────
    print('\nIdentificando UFs...')
    ufs_raw = con.execute(
        "SELECT DISTINCT TRIM(REPLACE(uf, '\"', '')) AS uf FROM v_estab WHERE LENGTH(TRIM(uf)) = 2"
    ).fetchall()
    ufs_validas = sorted([r[0] for r in ufs_raw if r[0].isalpha()])
    print('   Encontradas: ' + ', '.join(ufs_validas[:10]) + ('...' if len(ufs_validas) > 10 else ''))

    # ── Inputs do usuario ────────────────────────────────────────────────────
    print('\n' + '=' * 80)
    print('CONFIGURACOES DE FILTRO')
    print('=' * 80)

    ufs_input = input('\nUF(s) (ex: GO,SP) ou Enter=TODAS: ').upper().replace(' ', '')
    ESTADOS = ufs_input.split(',') if ufs_input else ufs_validas

    print('\nFiltro por Data de Abertura')
    data_inicio = parse_data(input('   Data inicial (DD/MM/AAAA): '), 'Data inicial')
    data_fim    = parse_data(input('   Data final   (DD/MM/AAAA): '), 'Data final')

    print('\nFiltro por Capital Social')
    cap_min_raw = input('   Capital MINIMO (padrao 100000): ').strip()
    cap_max_raw = input('   Capital MAXIMO (Enter=sem limite): ').strip()
    CAPITAL_MIN = float(cap_min_raw) if cap_min_raw else 100_000
    CAPITAL_MAX = float(cap_max_raw) if cap_max_raw else None

    print('\nFiltro por Porte')
    print('   00=N/I | 01=Micro | 02=Pequeno | 03=Medio | 04=Grande | 05=MEI | 06=EPP')
    porte_raw = input('   Porte(s) (ex: 02,03,04) ou Enter=TODOS: ').strip()
    PORTES = porte_raw.split(',') if porte_raw else list(PORTE_EMPRESA.keys())

    print('\nFiltro por CNAE Secundario (opcional)')
    cnae_sec_raw = input('   CNAE(s) secundario(s) (ex: 6202300): ').strip()
    CNAES_SEC = [c.strip() for c in cnae_sec_raw.split(',')] if cnae_sec_raw else []

    print('\nFiltro por Municipio (opcional)')
    mun_input = input('   Nome do municipio: ').strip().upper()

    print('\nOpcoes de Validacao')
    validar_emails = input('   Validar e-mails? (S/N): ').upper().startswith('S')
    formatar_tels  = input('   Formatar telefones? (S/N): ').upper().startswith('S')

    # ── Construir query SQL ──────────────────────────────────────────────────
    print('\nProcessando com DuckDB...')

    # Listas para SQL IN
    def sql_in(lst):
        return "('" + "', '".join(lst) + "')"

    naturezas_sql = sql_in(NATUREZAS_ERP)
    estados_sql   = sql_in(ESTADOS)
    portes_sql    = sql_in(PORTES)
    cnaes_2dig    = sql_in(list(CNAES_ALVO.keys()))

    capital_max_clause = ''
    if CAPITAL_MAX is not None:
        capital_max_clause = 'AND TRY_CAST(REPLACE(REPLACE(e.capital, \'.\', \'\'), \',\', \'.\') AS DOUBLE) <= ' + str(CAPITAL_MAX)

    data_inicio_clause = ''
    if data_inicio:
        data_inicio_clause = "AND strptime(NULLIF(est.data_inicio,''), '%Y%m%d') >= DATE '" + data_inicio.strftime('%Y-%m-%d') + "'"

    data_fim_clause = ''
    if data_fim:
        data_fim_clause = "AND strptime(NULLIF(est.data_inicio,''), '%Y%m%d') <= DATE '" + data_fim.strftime('%Y-%m-%d') + "'"

    cnae_sec_clause = ''
    if CNAES_SEC:
        like_parts = ["est.cnae_secundario LIKE '%" + c + "%'" for c in CNAES_SEC]
        cnae_sec_clause = 'AND (' + ' OR '.join(like_parts) + ')'

    mun_clause = ''
    if mun_input and arquivos['municipios']:
        mun_clause = "AND UPPER(COALESCE(m.nome_mun, '')) LIKE '%" + mun_input + "%'"

    mun_join = ''
    if arquivos['municipios']:
        mun_join = "LEFT JOIN v_municipios m ON TRIM(REPLACE(est.municipio,'\"','')) = TRIM(REPLACE(m.codigo_mun,'\"',''))"

    query = """
        SELECT
            -- Empresa
            e.cnpj_base AS cnpj_base,
            e.razao_social AS razao_social,
            e.natureza AS natureza,
            e.capital AS capital_raw,
            e.porte AS porte,
            TRY_CAST(
                REPLACE(REPLACE(e.capital, '.', ''), ',', '.')
                AS DOUBLE
            ) AS capital_num,

            -- Estabelecimento
            est.cnpj_ordem AS cnpj_ordem,
            est.cnpj_dv AS cnpj_dv,
            est.nome_fantasia AS nome_fantasia,
            est.data_inicio AS data_inicio,
            est.cnae_principal AS cnae_principal,
            est.cnae_secundario AS cnae_secundario,
            est.logradouro AS logradouro,
            est.numero AS numero,
            est.complemento AS complemento,
            est.bairro AS bairro,
            est.cep AS cep,
            est.uf AS uf,
            est.municipio AS municipio_cod,
            est.ddd1 AS ddd1,
            est.telefone1 AS telefone1,
            est.email AS email,
            COALESCE(m.nome_mun, est.municipio) AS municipio_nome,
            LEFT(est.cnae_principal, 2) AS cnae_2dig

        FROM v_estab est
        INNER JOIN v_empresas e
            ON est.cnpj_base = e.cnpj_base
        {mun_join}

        WHERE
            est.matriz_filial = '1'
            AND est.situacao = '02'
            AND est.uf IN {estados}
            AND LEFT(est.cnae_principal, 2) IN {cnaes}
            AND e.natureza IN {naturezas}
            AND e.porte IN {portes}
            AND TRY_CAST(
                REPLACE(REPLACE(e.capital, '.', ''), ',', '.')
                AS DOUBLE
            ) >= {cap_min}
            {cap_max}
            {dt_ini}
            {dt_fim}
            {cnae_sec}
            {mun_filter}
    """.format(
        mun_join=mun_join,
        estados=estados_sql,
        cnaes=cnaes_2dig,
        naturezas=naturezas_sql,
        portes=portes_sql,
        cap_min=CAPITAL_MIN,
        cap_max=capital_max_clause,
        dt_ini=data_inicio_clause,
        dt_fim=data_fim_clause,
        cnae_sec=cnae_sec_clause,
        mun_filter=mun_clause,
    )

    print('   Executando query principal...', end=' ', flush=True)
    df = con.execute(query).df()
    print('OK — ' + str(len(df)) + ' registros')

    if df.empty:
        print('Nenhum registro encontrado com os criterios informados.')
        sys.exit(0)

    # ── Socios ───────────────────────────────────────────────────────────────
    df_socios = pd.DataFrame()
    if arquivos['socios']:
        print('   Carregando socios...', end=' ', flush=True)
        cnpj_lista = "('" + "', '".join(df['cnpj_base'].unique()) + "')"
        df_soc_raw = con.execute("""
            SELECT
                cnpj_base AS cnpj_base,
                nome_socio AS nome_socio,
                qualificacao_socio AS qualificacao_socio
            FROM v_socios
            WHERE cnpj_base IN {cnpjs}
        """.format(cnpjs=cnpj_lista)).df()
        print('OK — ' + str(len(df_soc_raw)) + ' socios')

        if not df_soc_raw.empty:
            print('   Agregando socios...', end=' ', flush=True)
            df_socios = df_soc_raw.groupby('cnpj_base').apply(agregar_socios).reset_index()
            print('OK — ' + str(len(df_socios)) + ' empresas com socios')

    con.close()

    # ── Merge socios ─────────────────────────────────────────────────────────
    if not df_socios.empty:
        df = pd.merge(df, df_socios, on='cnpj_base', how='left')

    # ── Enriquecer colunas ───────────────────────────────────────────────────
    df['Porte_Descricao']    = df['porte'].map(PORTE_EMPRESA).fillna('Nao Informado')
    df['Natureza_Descricao'] = df['natureza'].map(NATUREZA_JURIDICA).fillna('Outra')
    df['Ramo']               = df['cnae_2dig'].map(CNAES_ALVO)

    def montar_cnpj(row):
        base  = str(row['cnpj_base']).replace('nan', '').zfill(8)
        ordem = str(row['cnpj_ordem']).replace('nan', '').zfill(4)
        dv    = str(row['cnpj_dv']).replace('nan', '00').zfill(2)
        return base + '.' + ordem + '/' + dv

    df['CNPJ'] = df.apply(montar_cnpj, axis=1)

    def formatar_capital(x):
        try:
            return 'R$ ' + str(int(float(x)))
        except (ValueError, TypeError):
            return 'R$ 0'

    df['Capital_Social'] = df['capital_num'].apply(formatar_capital)

    try:
        df['Data_Abertura'] = pd.to_datetime(df['data_inicio'], format='%Y%m%d', errors='coerce').dt.strftime('%d/%m/%Y')
    except Exception:
        df['Data_Abertura'] = ''

    # ── Validacao de e-mails ─────────────────────────────────────────────────
    if validar_emails:
        print('   Validando e-mails...', end=' ', flush=True)
        validados = df['email'].apply(validar_email)
        df['Email_Status'] = validados.apply(lambda x: x['status'])
        df['Email_Limpo']  = validados.apply(lambda x: x['email'] if x['valido'] else '')
        validos = (df['Email_Status'] == 'Valido').sum()
        print('OK — ' + str(validos) + '/' + str(len(df)) + ' validos (' + str(round(validos/len(df)*100, 1)) + '%)')

    # ── Formatacao de telefones ──────────────────────────────────────────────
    if formatar_tels:
        print('   Formatando telefones...', end=' ', flush=True)
        df['Telefone_Fmt'] = df.apply(lambda r: formatar_telefone(r['ddd1'], r['telefone1']), axis=1)
        print('OK')

    # ── Montar DataFrame de exportacao ───────────────────────────────────────
    mapeamento = {
        'CNPJ':             'CNPJ',
        'razao_social':     'Razao Social',
        'nome_fantasia':    'Nome Fantasia',
        'Data_Abertura':    'Data Abertura',
        'Capital_Social':   'Capital Social',
        'capital_num':      'Capital_Numerico',
        'Porte_Descricao':  'Porte',
        'Natureza_Descricao': 'Natureza Juridica',
        'cnae_principal':   'CNAE Principal',
        'cnae_secundario':  'CNAE Secundario',
        'Ramo':             'Ramo de Atividade',
        'municipio_nome':   'Municipio',
        'uf':               'UF',
        'logradouro':       'Logradouro',
        'numero':           'Numero',
        'complemento':      'Complemento',
        'bairro':           'Bairro',
        'cep':              'CEP',
    }

    if formatar_tels:
        mapeamento['Telefone_Fmt'] = 'Telefone'
    else:
        mapeamento['ddd1']      = 'DDD'
        mapeamento['telefone1'] = 'Telefone'

    if validar_emails:
        mapeamento['Email_Limpo']  = 'E-mail Valido'
        mapeamento['Email_Status'] = 'Status E-mail'
    else:
        mapeamento['email'] = 'E-mail'

    if not df_socios.empty:
        for i in range(1, 4):
            mapeamento['Socio_' + str(i) + '_Nome']        = 'Socio_' + str(i) + '_Nome'
            mapeamento['Socio_' + str(i) + '_Qualif_Texto'] = 'Socio_' + str(i) + '_Qualif'
        mapeamento['Total_Socios'] = 'Total_Socios'

    df_export = pd.DataFrame()
    for origem, destino in mapeamento.items():
        if origem in df.columns:
            df_export[destino] = df[origem]

    df_export['APROVADO_PARA_IMPORTACAO'] = 'PENDENTE'
    df_export['OBSERVACOES']              = ''
    df_export = df_export.sort_values('Capital_Numerico', ascending=False)

    # ── Salvar arquivos ──────────────────────────────────────────────────────
    print('\nGerando arquivos...')
    ts       = datetime.now().strftime('%Y%m%d_%H%M%S')
    ufs_tag  = sanitizar('_'.join(ESTADOS) if len(ESTADOS) < 4 else str(len(ESTADOS)) + 'EST')
    arq_tag  = str(len(arquivos['empresas'])) + 'ARQ'
    base_nome = OUTPUT_DIR + '/PROSPECTOS_' + ufs_tag + '_' + arq_tag + '_' + str(len(df_export)) + '_' + ts

    nome_csv   = base_nome + '.csv'
    nome_excel = base_nome + '.xlsx'

    print('   CSV...  ', end='', flush=True)
    df_export.to_csv(nome_csv, index=False, encoding='utf-8-sig', sep=';')
    print('OK')

    print('   Excel...', end='', flush=True)
    try:
        df_export.to_excel(nome_excel, index=False, sheet_name='Prospectos', engine='openpyxl')
        print('OK')
    except Exception as e:
        print('ERRO: ' + str(e) + '  (instale: pip install openpyxl)')

    # ── Resumo ───────────────────────────────────────────────────────────────
    print('\n' + '=' * 80)
    print('CONCLUIDO!')
    print('=' * 80)
    print('Registros gerados : ' + str(len(df_export)))
    print('CSV               : ' + nome_csv)
    if os.path.exists(nome_excel):
        print('Excel             : ' + nome_excel)
    print('=' * 80)


if __name__ == '__main__':
    main()
