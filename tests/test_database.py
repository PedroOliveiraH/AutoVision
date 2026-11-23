from src.database import init_db, get_all_vehicles, get_vehicle


def test_db_cria_cinco_carros(tmp_path):
    p = tmp_path / "teste.sqlite3"
    init_db(p)
    rows = get_all_vehicles(p)
    assert len(rows) == 5
    assert get_vehicle("porsche-911-gt3-rs-2010", p)["versao"] == "GT3 RS (997.2)"
    assert get_vehicle("inexistente", p) is None
