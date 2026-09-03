import db_manager


def test_guardar_y_obtener_usuario(tmp_path, monkeypatch):

    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db_manager, "DB_PATH", str(db_path))

    db_manager.init_db()

    db_manager.guardar_usuario(
        12345,
        "Matias",
        "Centro"
    )

    usuario = db_manager.obtener_usuario(12345)

    assert usuario is not None
    assert usuario["chat_id"] == 12345
    assert usuario["nombre"] == "Matias"
    assert usuario["barrio"] == "Centro"


def test_obtener_usuario_inexistente(tmp_path, monkeypatch):

    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db_manager, "DB_PATH", str(db_path))

    db_manager.init_db()

    usuario = db_manager.obtener_usuario(99999)

    assert usuario is None


def test_obtener_barrio(tmp_path, monkeypatch):

    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db_manager, "DB_PATH", str(db_path))

    db_manager.init_db()

    db_manager.guardar_usuario(
        12346,
        "Juan",
        "Camba Cua"
    )

    barrio = db_manager.obtener_barrio(12346)

    assert barrio == "Camba Cua"


def test_obtener_barrio_usuario_inexistente(tmp_path, monkeypatch):

    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db_manager, "DB_PATH", str(db_path))

    db_manager.init_db()

    barrio = db_manager.obtener_barrio(99999)

    assert barrio is None


def test_obtener_chat_ids_por_barrio(tmp_path, monkeypatch):

    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db_manager, "DB_PATH", str(db_path))

    db_manager.init_db()

    db_manager.guardar_usuario(1, "Juan", "Centro")
    db_manager.guardar_usuario(2, "Pedro", "Centro")
    db_manager.guardar_usuario(3, "Maria", "Camba Cua")

    usuarios = db_manager.obtener_chat_ids_por_barrio("Centro")

    assert 1 in usuarios
    assert 2 in usuarios
    assert 3 not in usuarios


def test_busqueda_barrio_sin_importar_mayusculas(tmp_path, monkeypatch):

    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db_manager, "DB_PATH", str(db_path))

    db_manager.init_db()

    db_manager.guardar_usuario(4, "Ana", "Centro")

    usuarios = db_manager.obtener_chat_ids_por_barrio("centro")

    assert 4 in usuarios


def test_guardar_y_obtener_alerta(tmp_path, monkeypatch):

    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db_manager, "DB_PATH", str(db_path))

    db_manager.init_db()

    db_manager.guardar_alerta(
        "Centro",
        "Naranja",
        "Se detectó un incremento en los niveles hídricos."
    )

    alerta = db_manager.obtener_alerta_barrio("Centro")

    assert alerta is not None
    assert alerta["nivel"] == "Naranja"
    assert alerta["mensaje"] == "Se detectó un incremento en los niveles hídricos."


def test_alerta_inexistente(tmp_path, monkeypatch):

    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db_manager, "DB_PATH", str(db_path))

    db_manager.init_db()

    alerta = db_manager.obtener_alerta_barrio("BarrioInexistente")

    assert alerta is None

def test_guardar_reporte(tmp_path, monkeypatch):

    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db_manager, "DB_PATH", str(db_path))

    db_manager.init_db()

    db_manager.guardar_usuario(
        12345,
        "Matias",
        "Centro"
    )

    db_manager.guardar_reporte(
        12345,
        "inundacion",
        "Centro"
    )

    conn = db_manager.get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT chat_id, tipo_problema, barrio
        FROM Reportes
        WHERE chat_id = ?
        """,
        (12345,)
    )

    reporte = cur.fetchone()

    conn.close()

    assert reporte is not None
    assert reporte[0] == 12345
    assert reporte[1] == "inundacion"
    assert reporte[2] == "Centro"