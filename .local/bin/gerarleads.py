#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GERADOR CSV UNIVERSAL DE PROSPECTOS - SERPRO EDITION

"""

import pandas as pd
import os
import re
import sys
import glob
import gc
import traceback
from datetime import datetime
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

# Configuracoes
OUTPUT_DIR = "prospectos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Detectar capacidade do sistema - MAIS CONSERVADOR
MEMORIA_TOTAL_GB = 8
CHUNKSIZE_EMPRESAS = 50000
CHUNKSIZE_ESTAB = 25000
CHUNKSIZE_SOCIOS = 50000

print("=" * 80)
print("GERADOR CSV UNIVERSAL DE PROSPECTOS - SERPRO")
print("=" * 80)

# Dicionarios (mantidos do original)
CNAES_ALVO = {
    '01': 'Agropecuaria', '46': 'Comercio Atacadista', '47': 'Comercio Varejista',
    '10': 'Industria Alimentos', '11': 'Industria Bebidas',
    '16': 'Industria Celulose/Papel',
    '31': 'Industria Diversos'
}

QUALIFICACOES_SOCIO = {
    '05': 'Socio-Administrador', '06': 'Socio-Gerente', '07': 'Socio',
    '08': 'Socio-Comanditado', '09': 'Socio-Comanditario', '10': 'Socio-Capitalista',
    '11': 'Socio-Industrial', '12': 'Socio-Comercial', '13': 'Socio de Industria',
    '14': 'Socio de Comercio', '15': 'Socio de Servicos', '16': 'Socio-Especial',
    '17': 'Socio-Fundador', '18': 'Socio-Investidor', '19': 'Socio-Majoritario',
    '20': 'Socio-Minoritario', '21': 'Socio-Responsavel', '22': 'Socio-Cotista',
    '23': 'Socio-Ostensivo', '24': 'Socio-Secretario', '25': 'Socio-Tesoureiro',
    '26': 'Socio-Presidente', '27': 'Socio-Vice-Presidente', '28': 'Socio-Diretor',
    '29': 'Socio-Superintendente', '30': 'Socio-Gerente Geral', '31': 'Socio-Executivo',
    '32': 'Socio-Operacional', '33': 'Socio-Estrategico', '34': 'Socio-Financeiro',
    '35': 'Socio-Tecnico', '36': 'Socio-Comercial', '37': 'Socio-Marketing',
    '38': 'Socio-Producao', '39': 'Socio-Logistica', '40': 'Socio-RH',
    '41': 'Socio-Juridico', '42': 'Socio-TI', '43': 'Socio-Inovacao',
    '44': 'Socio-Sustentabilidade', '45': 'Socio-Relacoes Institucionais',
    '46': 'Socio-Compliance', '47': 'Socio-Governanca', '48': 'Socio-Riscos',
    '49': 'Socio-Controladoria', '50': 'Socio-Auditoria', '51': 'Socio-Planejamento',
    '52': 'Socio-Negocios', '53': 'Socio-Desenvolvimento', '54': 'Socio-Pesquisa',
    '55': 'Socio-Qualidade', '56': 'Socio-Seguranca', '57': 'Socio-Meio Ambiente',
    '58': 'Socio-Saude', '59': 'Socio-Educacao', '60': 'Socio-Cultura',
    '61': 'Socio-Esportes', '62': 'Socio-Lazer', '63': 'Socio-Turismo',
    '64': 'Socio-Entretenimento', '65': 'Socio-Moda', '66': 'Socio-Beleza',
    '67': 'Socio-Gastronomia', '68': 'Socio-Agronegocio', '69': 'Socio-Imobiliario',
    '70': 'Socio-Construcao', '71': 'Socio-Energia', '72': 'Socio-Mineracao',
    '73': 'Socio-Quimica', '74': 'Socio-Farmaceutico', '75': 'Socio-Medico',
    '76': 'Socio-Odontologico', '77': 'Socio-Veterinario', '78': 'Socio-Contabil',
    '79': 'Socio-Economico', '80': 'Socio-Atuario', '81': 'Socio-Estatistico',
    '82': 'Socio-Engenharia', '83': 'Socio-Arquitetura', '84': 'Socio-Agronomia',
    '85': 'Socio-Medicina', '86': 'Socio-Odontologia', '87': 'Socio-Farmacia',
    '88': 'Socio-Enfermagem', '89': 'Socio-Fisioterapia', '90': 'Socio-Nutricao',
    '91': 'Socio-Psicologia', '92': 'Socio-Servico Social', '93': 'Socio-Direito',
    '94': 'Socio-Jornalismo', '95': 'Socio-Publicidade', '96': 'Socio-Propaganda',
    '97': 'Socio-Marketing Digital', '98': 'Socio-Design', '99': 'Socio-Arte',
    '00': 'Nao Informado', '01': 'Representante Legal', '02': 'Procurador',
    '03': 'Administrador Judicial', '04': 'Inventariante'
}

PORTE_EMPRESA = {
    '00': 'Nao Informado', '01': 'Micro Empresa', '02': 'Pequeno Porte',
    '03': 'Medio Porte', '04': 'Grande Porte', '05': 'MEI', '06': 'EPP', '07': 'Demais'
}

NATUREZA_JURIDICA = {
    '2046': 'Sociedade Anonima Aberta', '2054': 'Sociedade Anonima Fechada',
    '2062': 'Sociedade Empresaria Limitada', '2143': 'Empresario Individual',
    '2240': 'Sociedade Simples Limitada'
}

NATUREZAS_ERP = ['2062', '2240', '2143', '2046', '2054']

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
            return {'valido': False, 'email': email, 'status': 'Descartavel'}
        return {'valido': True, 'email': email, 'status': 'Valido'}
    return {'valido': False, 'email': email, 'status': 'Invalido'}

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
        formatado = num_limpo[:5] + '-' + num_limpo[5:]
    elif len(num_limpo) == 8:
        formatado = num_limpo[:4] + '-' + num_limpo[4:]
    elif len(num_limpo) > 9:
        formatado = num_limpo[-9:-4] + '-' + num_limpo[-4:]
    else:
        formatado = num_limpo
    if ddd_limpo:
        return '(' + ddd_limpo + ') ' + formatado
    return formatado

def agregar_socios(group):
    resultado = {}
    for i, (idx, row) in enumerate(group.iterrows(), 1):
        if i > 3:
            break
        nome_socio = str(row.get('nome_socio', '')).strip()
        cod_qualif = str(row.get('qualificacao_socio', '')).strip()
        qualif_texto = QUALIFICACOES_SOCIO.get(cod_qualif, 'Codigo ' + cod_qualif)
        resultado['Socio_' + str(i) + '_Nome'] = nome_socio
        resultado['Socio_' + str(i) + '_Qualif_Cod'] = cod_qualif
        resultado['Socio_' + str(i) + '_Qualif_Texto'] = qualif_texto
    for i in range(len(group) + 1, 4):
        resultado['Socio_' + str(i) + '_Nome'] = ''
        resultado['Socio_' + str(i) + '_Qualif_Cod'] = ''
        resultado['Socio_' + str(i) + '_Qualif_Texto'] = ''
    resultado['Total_Socios'] = len(group)
    return pd.Series(resultado)

def parse_data_input(texto, nome_campo):
    if not texto.strip():
        return None
    try:
        return datetime.strptime(texto.strip(), '%d/%m/%Y')
    except ValueError:
        print("   ⚠️ " + nome_campo + " invalida, ignorando")
        return None

def detectar_arquivos():
    """Detecta automaticamente quais arquivos numerados existem"""
    arquivos = {
        'empresas': sorted(glob.glob('empresas[0-9].csv')),
        'estabelecimentos': sorted(glob.glob('estabelecimentos[0-9].csv')),
        'socios': sorted(glob.glob('socios[0-9].csv')),
        'municipios': glob.glob('municipios.csv')
    }
    return arquivos

def processar_empresas_arquivo(args):
    """Processa um arquivo de empresas com tratamento de erro robusto"""
    arquivo, CAPITAL_MIN, CAPITAL_MAX, PORTES_ALVO = args
    chunks = []
    total_lido = 0
    try:
        for chunk in pd.read_csv(arquivo, sep=';', encoding='latin1', header=None, chunksize=CHUNKSIZE_EMPRESAS,
                                 names=['cnpj_base', 'razao_social', 'natureza', 'qualificacao', 'capital', 'porte', 'ente'],
                                 dtype=str, on_bad_lines='skip', quoting=3, low_memory=False):
            total_lido += len(chunk)
            for col in chunk.columns:
                chunk[col] = chunk[col].astype(str).str.replace('"', '').str.strip()

            # Converter capital com tratamento de erro
            def parse_capital(x):
                try:
                    if x and str(x).replace('.', '').replace(',', '').replace('-', '').isdigit():
                        return float(str(x).replace('.', '').replace(',', '.'))
                    return 0
                except:
                    return 0

            chunk['capital_num'] = chunk['capital'].apply(parse_capital)

            filtro_cap = (chunk['capital_num'] >= CAPITAL_MIN)
            if CAPITAL_MAX != float('inf'):
                filtro_cap &= (chunk['capital_num'] <= CAPITAL_MAX)

            filtro = chunk['natureza'].isin(NATUREZAS_ERP) & filtro_cap & chunk['porte'].isin(PORTES_ALVO)

            if filtro.any():
                chunks.append(chunk[filtro])

        resultado = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()
        return {'arquivo': arquivo, 'df': resultado, 'total_lido': total_lido, 'erro': None}
    except Exception as e:
        erro_msg = str(type(e).__name__) + ': ' + str(e)
        return {'arquivo': arquivo, 'df': pd.DataFrame(), 'total_lido': 0, 'erro': erro_msg}

def processar_empresas_sequencial(args_empresas):
    """Processamento sequencial como fallback"""
    resultados = []
    for i, args in enumerate(args_empresas, 1):
        arquivo = args[0]
        print("   [" + str(i) + "/" + str(len(args_empresas)) + "] Processando " + os.path.basename(arquivo) + " (sequencial)...", end=' ', flush=True)
        resultado = processar_empresas_arquivo(args)
        if resultado['erro']:
            print("ERRO: " + resultado['erro'])
        else:
            print("OK (" + str(len(resultado['df'])) + " registros)")
        resultados.append(resultado)
    return resultados

def main():
    """Funcao principal - protegida para multiprocessing"""

    # Configuracoes locais - MAIS CONSERVADORAS
    MAX_WORKERS = min(2, mp.cpu_count())

    print("\n" + "=" * 80)
    print("CONFIGURACOES DE FILTRO")
    print("=" * 80)

    # Detectar arquivos disponiveis
    arquivos_disponiveis = detectar_arquivos()

    print("\nArquivos detectados:")
    print("   Empresas: " + str(len(arquivos_disponiveis['empresas'])) + " arquivo(s)")
    print("   Estabelecimentos: " + str(len(arquivos_disponiveis['estabelecimentos'])) + " arquivo(s)")
    print("   Socios: " + str(len(arquivos_disponiveis['socios'])) + " arquivo(s)")
    mun_ok = '✓' if arquivos_disponiveis['municipios'] else '✗'
    print("   Municipios: " + mun_ok)

    if not arquivos_disponiveis['empresas'] or not arquivos_disponiveis['estabelecimentos']:
        print("\nERRO: Nao foram encontrados arquivos empresasX.csv ou estabelecimentosX.csv")
        sys.exit(1)

    # UF
    print("\nIdentificando estados...")
    ufs_validas = []
    try:
        arquivo_uf = arquivos_disponiveis['estabelecimentos'][0]
        for chunk in pd.read_csv(arquivo_uf, sep=';', encoding='latin1',
                                 header=None, usecols=[19], chunksize=50000,
                                 dtype=str, on_bad_lines='skip', quoting=3):
            chunk[19] = chunk[19].astype(str).str.replace('"', '').str.strip()
            ufs_validas.extend(chunk[19].dropna().unique())
        ufs_validas = sorted(list(set([uf for uf in ufs_validas if len(str(uf)) == 2 and str(uf).isalpha()])))
        print("   Encontrados: " + ', '.join(ufs_validas[:10]) + ('...' if len(ufs_validas) > 10 else ''))
    except Exception as e:
        print("   ⚠️ Usando lista padrao: " + str(e))
        ufs_validas = ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']

    estados_input = input("\nUF(s) desejadas (ex: GO,SP) ou Enter para TODAS: ").upper().replace(" ", "")
    ESTADOS_ALVO = estados_input.split(',') if estados_input else ufs_validas
    print("Selecionado: " + str(len(ESTADOS_ALVO)) + " estado(s)")

    # Data
    print("\nFiltro por Data de Abertura")
    data_inicio = parse_data_input(input("   Data inicial (DD/MM/AAAA): "), "Data inicial")
    data_fim = parse_data_input(input("   Data final (DD/MM/AAAA): "), "Data final")

    # Capital
    print("\nFiltro por Capital Social")
    cap_min = input("   Capital MINIMO (padrao: 50000): ").strip()
    CAPITAL_MIN = float(cap_min) if cap_min else 50000
    cap_max = input("   Capital MAXIMO (Enter=sem limite): ").strip()
    CAPITAL_MAX = float(cap_max) if cap_max else float('inf')
    print("   R$ " + str(int(CAPITAL_MIN)) + " a R$ " + ("inf" if CAPITAL_MAX == float('inf') else str(int(CAPITAL_MAX))))

    # Porte
    print("\nFiltro por Porte")
    print("   00=N/I | 01=Micro | 02=Pequeno | 03=Medio | 04=Grande | 05=MEI | 06=EPP")
    porte_input = input("   Porte(s) (ex: 02,03,04) ou Enter=TODOS: ").strip()
    PORTES_ALVO = porte_input.split(',') if porte_input else list(PORTE_EMPRESA.keys())

    # CNAE Secundario
    print("\nFiltro por CNAE Secundario (opcional)")
    cnae_sec_input = input("   CNAE(s) secundario(s) (ex: 6202300): ").strip()
    CNAE_SEC_ALVO = [c.strip() for c in cnae_sec_input.split(',')] if cnae_sec_input else []

    # Municipio
    print("\nFiltro por Municipio (opcional)")
    mun_input = input("   Nome do municipio: ").strip().upper()
    MUNICIPIO_ALVO = mun_input if mun_input else None

    # Validacao
    print("\nOpcoes de Validacao")
    validar_emails = input("   Validar e-mails? (S/N): ").upper().startswith('S')
    formatar_tels = input("   Formatar telefones? (S/N): ").upper().startswith('S')

    # Escolha do modo de processamento
    print("\nModo de Processamento")
    print("   1 = Paralelo (mais rapido, pode dar erro em memoria limitada)")
    print("   2 = Sequencial (mais lento, mais seguro)")
    modo_input = input("   Escolha (1/2) [padrao=2]: ").strip()
    MODO_SEQUENCIAL = (modo_input == '2') or (modo_input == '')

    if not MODO_SEQUENCIAL:
        print("\nAtenção: Modo paralelo com " + str(MAX_WORKERS) + " workers")
        print("   Se der erro de memoria, rode novamente escolhendo modo sequencial.")

    # Processamento
    print("\nCarregando municipios...")
    municipios_dict = {}
    if arquivos_disponiveis['municipios']:
        try:
            df_mun = pd.read_csv('municipios.csv', sep=';', encoding='latin1',
                                header=None, names=['codigo', 'nome'], dtype=str, on_bad_lines='skip', quoting=3)
            df_mun['codigo'] = df_mun['codigo'].astype(str).str.replace('"', '').str.strip()
            df_mun['nome'] = df_mun['nome'].astype(str).str.replace('"', '').str.strip().str.upper()
            municipios_dict = dict(zip(df_mun['codigo'], df_mun['nome']))
            print("Carregados " + str(len(municipios_dict)) + " municipios")
        except Exception as e:
            print("Erro ao carregar municipios: " + str(e))

    # Processar EMPRESAS
    print("\nProcessando EMPRESAS (" + str(len(arquivos_disponiveis['empresas'])) + " arquivo(s))...")
    args_empresas = [(f, CAPITAL_MIN, CAPITAL_MAX, PORTES_ALVO) for f in arquivos_disponiveis['empresas']]

    resultados_empresas = []

    if MODO_SEQUENCIAL:
        print("   Modo: SEQUENCIAL (mais seguro para sistemas com pouca RAM)")
        resultados_empresas = processar_empresas_sequencial(args_empresas)
    else:
        print("   Modo: PARALELO (" + str(MAX_WORKERS) + " workers)")
        try:
            with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = [executor.submit(processar_empresas_arquivo, args) for args in args_empresas]
                for future in as_completed(futures):
                    try:
                        resultado = future.result(timeout=300)
                        resultados_empresas.append(resultado)
                        status = "OK" if not resultado['erro'] else "ERRO"
                        print("   " + os.path.basename(resultado['arquivo']) + ": " + str(len(resultado['df'])) + " regs - " + status)
                    except Exception as e:
                        print("   ERRO em future: " + str(e))
        except Exception as e:
            print("\nErro no paralelismo: " + str(e))
            print("   Fallback para modo sequencial...")
            resultados_empresas = processar_empresas_sequencial(args_empresas)

    # Verificar erros
    erros = [r for r in resultados_empresas if r['erro']]
    if erros:
        print("\n" + str(len(erros)) + " arquivo(s) com erro")

    # Consolidar resultados
    empresas_chunks = [r['df'] for r in resultados_empresas if not r['df'].empty]
    if not empresas_chunks:
        print("Nenhuma empresa encontrada com os criterios especificados")
        sys.exit(1)

    df_empresas = pd.concat(empresas_chunks, ignore_index=True)
    df_empresas['Porte_Descricao'] = df_empresas['porte'].map(PORTE_EMPRESA).fillna('Nao Informado')
    df_empresas['Natureza_Descricao'] = df_empresas['natureza'].map(NATUREZA_JURIDICA).fillna('Outra')
    cnpj_validos = set(df_empresas['cnpj_base'])
    print("Empresas filtradas: " + str(len(df_empresas)) + " | CNPJs unicos: " + str(len(cnpj_validos)))

    del empresas_chunks, resultados_empresas
    gc.collect()

    # Processar ESTABELECIMENTOS (sempre sequencial)
    print("\nProcessando ESTABELECIMENTOS (" + str(len(arquivos_disponiveis['estabelecimentos'])) + " arquivo(s))...")
    colunas_estab = ['cnpj_base', 'cnpj_ordem', 'cnpj_dv', 'matriz_filial', 'nome_fantasia',
                     'situacao', 'data_situacao', 'motivo_situacao', 'nome_cidade_exterior',
                     'pais', 'data_inicio', 'cnae_principal', 'cnae_secundario', 'tipo_logradouro',
                     'logradouro', 'numero', 'complemento', 'bairro', 'cep', 'uf', 'municipio',
                     'ddd1', 'telefone1', 'ddd2', 'telefone2', 'ddd_fax', 'fax', 'email',
                     'situacao_especial', 'data_situacao_especial']

    estab_chunks = []
    total_processado = 0

    for idx, arquivo in enumerate(arquivos_disponiveis['estabelecimentos'], 1):
        print("   [" + str(idx) + "/" + str(len(arquivos_disponiveis['estabelecimentos'])) + "] " + os.path.basename(arquivo) + "...", end=' ', flush=True)
        arquivo_encontrados = 0

        try:
            for chunk in pd.read_csv(arquivo, sep=';', encoding='latin1', header=None,
                                     chunksize=CHUNKSIZE_ESTAB, names=colunas_estab, dtype=str,
                                     on_bad_lines='skip', quoting=3, low_memory=False):
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

                if MUNICIPIO_ALVO and municipios_dict:
                    chunk['nome_mun_temp'] = chunk['municipio'].map(municipios_dict).fillna('')
                    filtro &= (chunk['nome_mun_temp'].str.contains(MUNICIPIO_ALVO, case=False, na=False))

                if filtro.any():
                    estab_chunks.append(chunk[filtro])
                    arquivo_encontrados += filtro.sum()

                total_processado += len(chunk)

            print("OK (" + str(arquivo_encontrados) + " encontrados)")

            if idx % 2 == 0:
                gc.collect()

        except Exception as e:
            print("ERRO: " + str(e))

    if not estab_chunks:
        print("Nenhum estabelecimento encontrado com os criterios especificados")
        sys.exit(1)

    df_estab = pd.concat(estab_chunks, ignore_index=True)
    df_estab['Nome_Municipio'] = df_estab['municipio'].map(municipios_dict).fillna(df_estab['municipio'])
    df_estab['Ramo'] = df_estab['cnae_2dig'].map(CNAES_ALVO)
    cnpj_com_estab = set(df_estab['cnpj_base'])
    print("Estabelecimentos filtrados: " + str(len(df_estab)) + " | CNPJs unicos: " + str(len(cnpj_com_estab)))

    # Atualizar empresas
    df_empresas = df_empresas[df_empresas['cnpj_base'].isin(cnpj_com_estab)]
    print("   Empresas atualizadas: " + str(len(df_empresas)))

    del estab_chunks
    gc.collect()

    # Validacao de e-mails
    if validar_emails:
        print("\nValidando e-mails...")
        df_estab['Email_Validacao'] = df_estab['email'].apply(validar_email)
        df_estab['Email_Status'] = df_estab['Email_Validacao'].apply(lambda x: x['status'])
        df_estab['Email_Limpo'] = df_estab['Email_Validacao'].apply(lambda x: x['email'] if x['valido'] else '')
        validos = (df_estab['Email_Status'] == 'Valido').sum()
        pct = round(validos/len(df_estab)*100, 1)
        print("   Validos: " + str(validos) + " / " + str(len(df_estab)) + " (" + str(pct) + "%)")

    # Formatacao de telefones
    if formatar_tels:
        print("\nFormatando telefones...")
        df_estab['telefone_formatado'] = df_estab.apply(
            lambda x: formatar_telefone(x['ddd1'], x['telefone1']), axis=1
        )

    # Processar SOCIOS (sequencial)
    df_socios = pd.DataFrame()
    if arquivos_disponiveis['socios']:
        print("\nProcessando SOCIOS (" + str(len(arquivos_disponiveis['socios'])) + " arquivo(s))...")
        socios_chunks = []
        cnpj_estab = set(df_estab['cnpj_base'])

        for idx, arquivo in enumerate(arquivos_disponiveis['socios'], 1):
            print("   [" + str(idx) + "/" + str(len(arquivos_disponiveis['socios'])) + "] " + os.path.basename(arquivo) + "...", end=' ', flush=True)
            try:
                for chunk in pd.read_csv(arquivo, sep=';', encoding='latin1', header=None, chunksize=CHUNKSIZE_SOCIOS,
                                        names=['cnpj_base', 'identificador_socio', 'nome_socio', 'cnpj_cpf_socio',
                                               'qualificacao_socio', 'data_entrada', 'pais', 'representante',
                                               'nome_representante', 'qualificacao_representante', 'faixa_etaria'],
                                        dtype=str, on_bad_lines='skip', quoting=3, low_memory=False):
                    for col in chunk.columns:
                        chunk[col] = chunk[col].astype(str).str.replace('"', '').str.strip()
                    filtro = chunk['cnpj_base'].isin(cnpj_estab)
                    if filtro.any():
                        socios_chunks.append(chunk[filtro])
                print("OK")
            except Exception as e:
                print("ERRO: " + str(e))

        if socios_chunks:
            df_socios_raw = pd.concat(socios_chunks, ignore_index=True)
            print("   Agregando socios...")
            df_socios = df_socios_raw.groupby('cnpj_base').apply(agregar_socios).reset_index()
            print("Empresas com socios: " + str(len(df_socios)))
            del socios_chunks, df_socios_raw
            gc.collect()

    # Cruzamento final
    print("\nCruzando dados finais...")
    df_final = pd.merge(df_estab, df_empresas, on='cnpj_base', how='left')
    if not df_socios.empty:
        df_final = pd.merge(df_final, df_socios, on='cnpj_base', how='left')

    # Montar CNPJ formatado
    def montar_cnpj(x):
        base = str(x['cnpj_base']).zfill(8)
        ordem = str(x['cnpj_ordem']).zfill(4)
        dv = str(x['cnpj_dv']).zfill(2)
        return base + "." + ordem + "/" + dv

    df_final['CNPJ'] = df_final.apply(montar_cnpj, axis=1)

    # Capital social formatado
    def formatar_capital(x):
        return "R$ " + str(int(x))

    df_final['Capital_Social'] = df_final['capital_num'].apply(formatar_capital)
    df_final['Data_Abertura'] = df_final['data_inicio_dt'].dt.strftime('%d/%m/%Y')

    # Geracao dos arquivos
    print("\nGerando arquivos de saida...")

    mapeamento_colunas = {
        'CNPJ': 'CNPJ',
        'razao_social': 'Razao Social',
        'nome_fantasia': 'Nome Fantasia',
        'Data_Abertura': 'Data Abertura',
        'Capital_Social': 'Capital Social',
        'capital_num': 'Capital_Numerico',
        'Porte_Descricao': 'Porte',
        'Natureza_Descricao': 'Natureza Juridica',
        'cnae_principal': 'CNAE Principal',
        'cnae_secundario': 'CNAE Secundario',
        'Ramo': 'Ramo de Atividade',
        'Nome_Municipio': 'Municipio',
        'uf': 'UF',
        'logradouro': 'Logradouro',
        'numero': 'Numero',
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
        mapeamento_colunas['Email_Limpo'] = 'E-mail Valido'
        mapeamento_colunas['Email_Status'] = 'Status E-mail'
    else:
        mapeamento_colunas['email'] = 'E-mail'

    if not df_socios.empty:
        for i in range(1, 4):
            mapeamento_colunas['Socio_' + str(i) + '_Nome'] = 'Socio_' + str(i) + '_Nome'
            mapeamento_colunas['Socio_' + str(i) + '_Qualif_Texto'] = 'Socio_' + str(i) + '_Qualif_Texto'
        mapeamento_colunas['Total_Socios'] = 'Total_Socios'

    df_export = pd.DataFrame()
    for origem, destino in mapeamento_colunas.items():
        if origem in df_final.columns:
            df_export[destino] = df_final[origem]

    df_export['APROVADO_PARA_IMPORTACAO'] = 'PENDENTE'
    df_export['OBSERVACOES'] = ''
    df_export = df_export.sort_values('Capital_Numerico', ascending=False)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    ufs_nome = sanitizar_nome_arquivo("_".join(ESTADOS_ALVO) if len(ESTADOS_ALVO) < 4 else str(len(ESTADOS_ALVO)) + "EST")
    qtd_arquivos = str(len(arquivos_disponiveis['empresas'])) + "ARQ"

    nome_csv = OUTPUT_DIR + "/PROSPECTOS_" + ufs_nome + "_" + qtd_arquivos + "_" + str(len(df_export)) + "_" + timestamp + ".csv"
    nome_excel = OUTPUT_DIR + "/PROSPECTOS_" + ufs_nome + "_" + qtd_arquivos + "_" + str(len(df_export)) + "_" + timestamp + ".xlsx"

    print("   Salvando CSV...", end=' ')
    df_export.to_csv(nome_csv, index=False, encoding='utf-8-sig', sep=';')
    print("OK")

    print("   Salvando Excel...", end=' ')
    try:
        df_export.to_excel(nome_excel, index=False, sheet_name='Prospectos', engine='openpyxl')
        print("OK")
    except Exception as e:
        print("ERRO: " + str(e))
        print("   Instale: pip install openpyxl")

    # Resumo
    print("\n" + "=" * 80)
    print("PROCESSAMENTO CONCLUIDO!")
    print("=" * 80)
    modo_str = 'Sequencial' if MODO_SEQUENCIAL else 'Paralelo'
    print("Modo: " + modo_str + " | OS: Arch Linux")
    print("Arquivos processados: " + str(len(arquivos_disponiveis['empresas'])) + " empresas + " + str(len(arquivos_disponiveis['estabelecimentos'])) + " estabelecimentos")
    print("Resultado: " + str(len(df_export)) + " prospectos gerados")
    print("\nArquivos:")
    print("   CSV:  " + nome_csv)
    if os.path.exists(nome_excel):
        print("   Excel: " + nome_excel)
    print("=" * 80)

if __name__ == '__main__':
    main()
