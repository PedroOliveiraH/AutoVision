"""Catálogo SQLite do AutoVision.

Etapa 4: fichas técnicas com dados históricos verificados, sem supor que o
classificador identifique o ano, motor, combustível ou versão de cada exemplar.

A migração preenche SOMENTE valores idênticos aos antigos valores do projeto
ou campos novos vazios; dados editados pela equipe são preservados.
"""
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "autovision.sqlite3"

# Ordem dos dez campos do esquema original, mantida por compatibilidade.
BASE_FIELDS = (
    "slug", "marca", "modelo", "versao", "tipo", "periodo",
    "motorizacao", "combustivel", "observacoes", "fonte_url",
)
EXTRA_FIELDS = ("carroceria", "potencia", "transmissao", "tracao")

# Evite potência única em famílias de carros que tiveram várias motorizações.
CARROS = [
    (
        "fiat-uno", "Fiat", "Uno", "Primeira geração ('Uno quadrado')",
        "Hatch compacto", "Brasil: 1984–2013 (primeira geração)",
        "Quatro cilindros: 1.0, 1.3, 1.5 e 1.6 L; Uno Turbo 1.4 L (conforme versão e ano)",
        "Gasolina; também versões a etanol ou flex, dependendo do ano",
        "A ficha cobre a família de carroceria quadrada, incluindo o Mille; não inclui o Novo Uno de 2010. "
        "Ano, motor e versão exatos não são inferidos pela foto.",
        "https://www.media.stellantis.com/br-pt/fiat/press/novo-uno-completa-15-anos-de-historia",
    ),
    (
        "volkswagen-fusca", "Volkswagen", "Fusca", "Modelo clássico (Type 1)",
        "Sedã clássico compacto", "Brasil: 1959–1986 e 1993–1996",
        "Boxer de quatro cilindros refrigerado a ar: 1.2, 1.3, 1.5 ou 1.6 L (conforme ano)",
        "Gasolina; versões brasileiras a etanol em anos específicos",
        "Motor traseiro refrigerado a ar e tração traseira. Não confundir o Fusca original "
        "com o New Beetle nem com o Beetle A5. A ficha varia conforme a versão.",
        "https://www.volkswagen-newsroom.com/en/the-volkswagen-beetle-a-success-story-2341/vw-beetle-through-the-years-2361",
    ),
    (
        "chevrolet-opala-ss", "Chevrolet", "Opala", "SS",
        "Sedã ou cupê, conforme o ano", "Brasil: 1971–1980 (raras unidades registradas em 1981)",
        "SS4: quatro cilindros 2.5 L (151-S); SS6: seis cilindros em linha 3.8/4.1 L, incluindo 250-S",
        "Gasolina nas configurações históricas aqui referenciadas",
        "A denominação SS identifica uma linha esportiva com diferentes motores e carrocerias. "
        "O sistema não determina se um exemplar é SS4, SS6 ou qual é seu ano.",
        "https://quatrorodas.abril.com.br/carros-classicos/classicos-chevrolet-opala-ss-trouxe-esportividade-no-motor-4-1-e-no-visual/",
    ),
    (
        "porsche-911-gt3-rs-2010", "Porsche", "911", "GT3 RS (997.2)",
        "Cupê esportivo", "2010 — GT3 RS 3.8 (geração 997.2)",
        "Boxer de seis cilindros aspirado, 3,8 L, montado na traseira",
        "Gasolina de alta octanagem",
        "Referência técnica: Porsche 911 GT3 RS 3.8 de 2010 (450 PS). "
        "A identificação visual pode confundir outros GT3 RS e não confirma a geração ou o ano.",
        "https://newsroom.porsche.com/en/history/porsche-911-seven-generations-part-6-type-997-16489.html",
    ),
    (
        "ford-mustang-1964-meio", "Ford", "Mustang", "1964½ (primeira série)",
        "Cupê hardtop ou conversível", "Abril de 1964: primeira série do ano/modelo 1965",
        "Seis em linha 170 pol³ (2,8 L); V8 260 pol³ (4,3 L) ou 289 pol³ (4,7 L), conforme opção",
        "Gasolina",
        "'1964½' é a designação informal dos Mustang lançados em 1964 como ano/modelo 1965. "
        "O fastback foi adicionado posteriormente; não integra a primeira série 1964½.",
        "https://www.ford.com/mustang/history/",
    ),
]

EXTRAS = {
    "fiat-uno": {
        "carroceria": "Hatch de 2 ou 4 portas, conforme versão",
        "potencia": "Varia por versão; exemplo histórico: Uno Turbo 1.4 de 1994, 116 cv",
        "transmissao": "Manual; quantidade de marchas conforme versão/ano",
        "tracao": "Dianteira (motor dianteiro transversal)",
    },
    "volkswagen-fusca": {
        "carroceria": "Sedã clássico de 2 portas",
        "potencia": "Varia conforme motor/ano e padrão de medição; não é inferida pela foto",
        "transmissao": "Manual de 4 marchas (configuração tradicional brasileira)",
        "tracao": "Traseira (motor traseiro)",
    },
    "chevrolet-opala-ss": {
        "carroceria": "Sedã ou cupê; configuração depende do ano",
        "potencia": "SS4 151-S: 98 cv brutos; SS6 250-S: 153 cv líquidos (padrões de medição distintos)",
        "transmissao": "Manual de 4 marchas com alavanca no assoalho (referência histórica)",
        "tracao": "Traseira (motor dianteiro longitudinal)",
    },
    "porsche-911-gt3-rs-2010": {
        "carroceria": "Cupê de 2 portas com aerofólio traseiro",
        "potencia": "450 PS (cavalos métricos)",
        "transmissao": "Manual de 6 marchas",
        "tracao": "Traseira (motor traseiro)",
    },
    "ford-mustang-1964-meio": {
        "carroceria": "Hardtop de 2 portas ou conversível de 2 portas; não inclui o fastback posterior",
        "potencia": "170: 101 hp; V8 260: 164 hp; V8 289: 210 ou 271 hp (valores brutos de época)",
        "transmissao": "Manual de 3 ou 4 marchas; automática opcional em certas configurações",
        "tracao": "Traseira (motor dianteiro longitudinal)",
    },
}

# Valores literais distribuídos na Etapa 1/2/3. Só substituímos dados
# que ainda são IGUAIS a esses valores de fábrica, preservando edições locais.
ANTIGOS = {
    "fiat-uno": {
        "tipo": "Hatch", "periodo": "A definir", "motorizacao": "A definir por versão/ano",
        "combustivel": "A definir",
        "observacoes": "Modelo clássico de carroceria quadrada. Ano e motorização dependem da versão.",
        "fonte_url": "",
    },
    "volkswagen-fusca": {
        "tipo": "Automóvel clássico", "periodo": "A definir",
        "motorizacao": "A definir por versão/ano", "combustivel": "A definir",
        "observacoes": "Não confundir com New Beetle / Beetle moderno.",
        "fonte_url": "https://www.volkswagen-newsroom.com/en/the-volkswagen-beetle-a-success-story-2341/vw-beetle-the-real-miracle-2356",
    },
    "chevrolet-opala-ss": {
        "tipo": "Sedã ou cupê, conforme o ano", "periodo": "A definir",
        "motorizacao": "A definir por versão/ano (SS4 ou SS6)", "combustivel": "A definir",
        "observacoes": "Recorte inicial: Opala SS. É necessário escolher o ano/carroceria para ficha técnica específica.",
        "fonte_url": "https://quatrorodas.abril.com.br/carros-classicos/classicos-chevrolet-opala-ss-trouxe-esportividade-no-motor-4-1-e-no-visual/",
    },
    "porsche-911-gt3-rs-2010": {
        "tipo": "Cupê esportivo", "periodo": "2010",
        "motorizacao": "Boxer de 6 cilindros, 3,8 litros", "combustivel": "Gasolina",
        "observacoes": "A geração 997.2 GT3 RS possui 450 PS. A identificação por foto pode confundir versões próximas.",
        "fonte_url": "https://www.porsche.com/stories/mobility/how-fast-porsche-911-gt3-rs/",
    },
    "ford-mustang-1964-meio": {
        "tipo": "Cupê ou conversível", "periodo": "Fabricado em 1964; ano/modelo 1965",
        "motorizacao": "Varia conforme a configuração", "combustivel": "Gasolina",
        "observacoes": "A designação 1964½ é informal para a primeira leva do Mustang ano/modelo 1965.",
        "fonte_url": "https://corporate.ford.com/corporate/corporate/articles/history/mustang/",
    },
}

# Catálogo de referências, separado das fotos usadas para treino/testes.
FONTES = {
    "fiat-uno": [
        ("Fiat/Stellantis — história e gerações do Uno", "https://www.media.stellantis.com/br-pt/fiat/press/novo-uno-completa-15-anos-de-historia"),
        ("Quatro Rodas — Fiat Uno Mille", "https://quatrorodas.abril.com.br/carros-classicos/fiat-uno-mille-historia-carro-popular-brasil/"),
        ("Quatro Rodas — Uno 30 anos", "https://quatrorodas.abril.com.br/noticias/galeria-uno-30-anos/"),
    ],
    "volkswagen-fusca": [
        ("Volkswagen — evolução do Beetle original", "https://www.volkswagen-newsroom.com/en/the-volkswagen-beetle-a-success-story-2341/vw-beetle-through-the-years-2361"),
        ("Quatro Rodas — Fusca no Brasil", "https://quatrorodas.abril.com.br/carros-classicos/do-sedan-ao-itamar-como-o-volkswagen-fusca-se-tornou-um-sucesso-no-brasil/"),
        ("Quatro Rodas — motor a etanol", "https://quatrorodas.abril.com.br/carros-classicos/10-motivos-para-voce-nao-comprar-um-volkswagen-fusca/"),
    ],
    "chevrolet-opala-ss": [
        ("Quatro Rodas — lançamento e evolução do SS", "https://quatrorodas.abril.com.br/carros-classicos/classicos-chevrolet-opala-ss-trouxe-esportividade-no-motor-4-1-e-no-visual/"),
        ("Quatro Rodas — 151-S e 250-S", "https://quatrorodas.abril.com.br/carros-classicos/chevrolet-opala-ss-deixou-muito-esportivo-v8-para-tras-nos-anos-1970/"),
    ],
    "porsche-911-gt3-rs-2010": [
        ("Porsche — geração 997", "https://newsroom.porsche.com/en/history/porsche-911-seven-generations-part-6-type-997-16489.html"),
        ("Porsche — ficha técnica original GT3 RS 2010 (PDF)", "https://newsroom.porsche.com/dam/jcr%3Af3e401b7-b334-4442-a9b6-f719c3675d85/2010_911_GT3-RS_Specs.pdf.PDF"),
    ],
    "ford-mustang-1964-meio": [
        ("Ford — história do Mustang", "https://www.ford.com/mustang/history/"),
        ("Arquivo de comunicado Ford de 13 abril 1964 — motores", "https://www.early-mustang.com/index.php/press-release"),
    ],
}


def connect(db_path: Path = DB_PATH):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path = DB_PATH):
    """Cria ou migra o catálogo sem destruir informações editadas pelo usuário."""
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
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(veiculos)")}
        for field in EXTRA_FIELDS:
            if field not in cols:
                conn.execute(f"ALTER TABLE veiculos ADD COLUMN {field} TEXT NOT NULL DEFAULT ''")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fontes_veiculos (
              veiculo_slug TEXT NOT NULL,
              titulo TEXT NOT NULL,
              url TEXT NOT NULL,
              PRIMARY KEY(veiculo_slug, url),
              FOREIGN KEY(veiculo_slug) REFERENCES veiculos(slug)
            )
        """)
        conn.executemany("""
            INSERT OR IGNORE INTO veiculos
            (slug, marca, modelo, versao, tipo, periodo, motorizacao, combustivel, observacoes, fonte_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, CARROS)

        for vals in CARROS:
            record = dict(zip(BASE_FIELDS, vals))
            slug = record["slug"]
            current = dict(conn.execute("SELECT * FROM veiculos WHERE slug = ?", (slug,)).fetchone())
            defaults = ANTIGOS[slug]
            updates = {}
            for field in BASE_FIELDS[1:]:
                # Só campos de valores exatos da versão antiga, nunca marca/modelo/versao.
                if field in defaults and current[field] == defaults[field]:
                    updates[field] = record[field]
            for field in EXTRA_FIELDS:
                if not current.get(field):
                    updates[field] = EXTRAS[slug][field]
            if updates:
                setters = ", ".join(f"{key} = ?" for key in updates)
                conn.execute(f"UPDATE veiculos SET {setters} WHERE slug = ?", [*updates.values(), slug])
            conn.executemany(
                "INSERT OR IGNORE INTO fontes_veiculos (veiculo_slug, titulo, url) VALUES (?, ?, ?)",
                [(slug, titulo, url) for titulo, url in FONTES[slug]],
            )


def get_all_vehicles(db_path: Path = DB_PATH):
    with connect(db_path) as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM veiculos ORDER BY marca, modelo")]


def get_vehicle(slug: str, db_path: Path = DB_PATH):
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM veiculos WHERE slug = ?", (slug,)).fetchone()
        return dict(row) if row else None


def get_vehicle_sources(slug: str, db_path: Path = DB_PATH):
    with connect(db_path) as conn:
        # A função é utilizada depois de init_db, como get_vehicle.
        return [dict(r) for r in conn.execute(
            "SELECT titulo, url FROM fontes_veiculos WHERE veiculo_slug = ? ORDER BY titulo",
            (slug,),
        )]
