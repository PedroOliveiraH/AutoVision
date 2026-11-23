"""Catálogo em SQLite: ficha técnica separada do reconhecimento visual."""
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "autovision.sqlite3"

# Campos propositalmente não preenchidos significam "não verificado".
CARROS = [
    (
        "fiat-uno", "Fiat", "Uno", "Primeira geração ('Uno quadrado')", "Hatch",
        "A definir", "A definir por versão/ano", "A definir", 
        "Modelo clássico de carroceria quadrada. Ano e motorização dependem da versão.",
        "", 
    ),
    (
        "volkswagen-fusca", "Volkswagen", "Fusca", "Modelo clássico (Type 1)", "Automóvel clássico",
        "A definir", "A definir por versão/ano", "A definir",
        "Não confundir com New Beetle / Beetle moderno.",
        "https://www.volkswagen-newsroom.com/en/the-volkswagen-beetle-a-success-story-2341/vw-beetle-the-real-miracle-2356",
    ),
    (
        "chevrolet-opala-ss", "Chevrolet", "Opala", "SS", "Sedã ou cupê, conforme o ano",
        "A definir", "A definir por versão/ano (SS4 ou SS6)", "A definir",
        "Recorte inicial: Opala SS. É necessário escolher o ano/carroceria para ficha técnica específica.",
        "https://quatrorodas.abril.com.br/carros-classicos/classicos-chevrolet-opala-ss-trouxe-esportividade-no-motor-4-1-e-no-visual/",
    ),
    (
        "porsche-911-gt3-rs-2010", "Porsche", "911", "GT3 RS (997.2)", "Cupê esportivo",
        "2010", "Boxer de 6 cilindros, 3,8 litros", "Gasolina",
        "A geração 997.2 GT3 RS possui 450 PS. A identificação por foto pode confundir versões próximas.",
        "https://www.porsche.com/stories/mobility/how-fast-porsche-911-gt3-rs/",
    ),
    (
        "ford-mustang-1964-meio", "Ford", "Mustang", "1964½ (primeira série)", "Cupê ou conversível",
        "Fabricado em 1964; ano/modelo 1965", "Varia conforme a configuração", "Gasolina",
        "A designação 1964½ é informal para a primeira leva do Mustang ano/modelo 1965.",
        "https://corporate.ford.com/corporate/corporate/articles/history/mustang/",
    ),
]


def connect(db_path: Path = DB_PATH):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DB_PATH):
    with connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS veiculos (
              slug TEXT PRIMARY KEY,
              marca TEXT NOT NULL,
              modelo TEXT NOT NULL,
              versao TEXT NOT NULL,
              tipo TEXT NOT NULL,
              periodo TEXT NOT NULL,
              motorizacao TEXT NOT NULL,
              combustivel TEXT NOT NULL,
              observacoes TEXT NOT NULL,
              fonte_url TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS imagens (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              veiculo_slug TEXT NOT NULL,
              caminho_relativo TEXT NOT NULL,
              finalidade TEXT NOT NULL,
              angulo TEXT,
              origem TEXT,
              licenca TEXT,
              FOREIGN KEY(veiculo_slug) REFERENCES veiculos(slug)
            )
        """)
        conn.executemany("""
            INSERT OR IGNORE INTO veiculos
            (slug, marca, modelo, versao, tipo, periodo, motorizacao, combustivel, observacoes, fonte_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, CARROS)


def get_all_vehicles(db_path: Path = DB_PATH):
    with connect(db_path) as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM veiculos ORDER BY marca, modelo")]


def get_vehicle(slug: str, db_path: Path = DB_PATH):
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM veiculos WHERE slug = ?", (slug,)).fetchone()
        return dict(row) if row else None
