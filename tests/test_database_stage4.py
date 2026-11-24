"""Testes isolados da atualização de catálogo (sem YOLO, CLIP ou internet)."""
import sqlite3

from src.database import (
    ANTIGOS, BASE_FIELDS, CARROS, EXTRA_FIELDS, EXTRAS,
    get_all_vehicles, get_vehicle, get_vehicle_sources, init_db,
)


def test_catalogo_completo_em_banco_novo(tmp_path):
    db = tmp_path / 'novo.sqlite3'
    init_db(db)
    rows = get_all_vehicles(db)
    assert len(rows) == 5
    assert {r['slug'] for r in rows} == set(EXTRAS)
    for row in rows:
        for field in ('periodo', 'motorizacao', 'combustivel', 'carroceria', 'potencia', 'transmissao', 'tracao'):
            assert row[field] and 'A definir' not in row[field]
        assert len(get_vehicle_sources(row['slug'], db)) >= 2


def test_migracao_da_versao_3_com_imagem_e_dados_preservados(tmp_path):
    db = tmp_path / 'antigo.sqlite3'
    with sqlite3.connect(db) as con:
        con.execute('''CREATE TABLE veiculos (
          slug TEXT PRIMARY KEY, marca TEXT NOT NULL, modelo TEXT NOT NULL,
          versao TEXT NOT NULL, tipo TEXT NOT NULL, periodo TEXT NOT NULL,
          motorizacao TEXT NOT NULL, combustivel TEXT NOT NULL,
          observacoes TEXT NOT NULL, fonte_url TEXT NOT NULL)''')
        con.execute('''CREATE TABLE imagens (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          veiculo_slug TEXT NOT NULL, caminho_relativo TEXT NOT NULL,
          finalidade TEXT NOT NULL, angulo TEXT, origem TEXT, licenca TEXT,
          FOREIGN KEY(veiculo_slug) REFERENCES veiculos(slug))''')
        for row in CARROS:
            data = dict(zip(BASE_FIELDS, row))
            data.update(ANTIGOS[data['slug']])
            con.execute('INSERT INTO veiculos VALUES (?,?,?,?,?,?,?,?,?,?)',
                        tuple(data[key] for key in BASE_FIELDS))
        con.execute('INSERT INTO imagens(veiculo_slug,caminho_relativo,finalidade) VALUES(?,?,?)',
                    ('fiat-uno', 'local/example.jpg', 'teste'))
    init_db(db)
    fiat = get_vehicle('fiat-uno', db)
    assert fiat['periodo'].startswith('Brasil: 1984')
    assert fiat['motorizacao'].startswith('Quatro cilindros:')
    assert fiat['tracao'].startswith('Dianteira')
    assert get_vehicle('porsche-911-gt3-rs-2010', db)['potencia'].startswith('450 PS')
    with sqlite3.connect(db) as con:
        assert con.execute('SELECT COUNT(*) FROM imagens').fetchone()[0] == 1


def test_edicao_local_preservada_e_idempotencia(tmp_path):
    db = tmp_path / 'customizado.sqlite3'
    init_db(db)
    with sqlite3.connect(db) as con:
        con.execute('UPDATE veiculos SET motorizacao=?, potencia=? WHERE slug=?',
                    ('Motor revisado pela equipe', 'Potência revisada', 'fiat-uno'))
    init_db(db)
    init_db(db)
    row = get_vehicle('fiat-uno', db)
    assert row['motorizacao'] == 'Motor revisado pela equipe'
    assert row['potencia'] == 'Potência revisada'
    assert len(get_vehicle_sources('fiat-uno', db)) == 3
    assert len(get_all_vehicles(db)) == 5


def test_nao_troca_chaves_de_reconhecimento(tmp_path):
    db = tmp_path / 'catalogo.sqlite3'
    init_db(db)
    from src.recognition import CANDIDATES
    assert set(CANDIDATES) == {r['slug'] for r in get_all_vehicles(db)}
    assert get_vehicle('inexistente', db) is None
