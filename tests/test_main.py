import main
from unittest.mock import patch


def test_procesar_registro():
    chat_id = 12345

    datos = {
        "intencion": "registro",
        "entidades": {
            "nombre": "Ana",
            "barrio": "Centro"
        }
    }

    with patch("main.db_manager.guardar_usuario") as mock_guardar_usuario:
        with patch("main.bot.send_message") as mock_send_message:

            main.procesar_datos_llm(chat_id, datos)

            mock_guardar_usuario.assert_called_once_with(
                chat_id,
                "Ana",
                "Centro"
            )

            mock_send_message.assert_called_once()

def test_procesar_reporte():
    chat_id = 12345

    datos = {
        "intencion": "reporte",
        "entidades": {
            "tipo_problema": "Calle inundada"
        }
    }

    usuario = {
        "chat_id": chat_id,
        "nombre": "Ana",
        "barrio": "Centro"
    }

    with patch(
        "main.db_manager.obtener_usuario",
        return_value=usuario
    ) as mock_obtener_usuario:

        with patch(
            "main.db_manager.guardar_reporte"
        ) as mock_guardar_reporte:

            with patch("main.bot.send_message") as mock_send_message:

                main.procesar_datos_llm(chat_id, datos)

                mock_obtener_usuario.assert_called_once_with(chat_id)

                mock_guardar_reporte.assert_called_once_with(
                    chat_id,
                    "Calle inundada",
                    "Centro"
                )

                mock_send_message.assert_called_once()

def test_procesar_reporte_usuario_no_registrado():
    chat_id = 99999

    datos = {
        "intencion": "reporte",
        "entidades": {
            "tipo_problema": "Calle inundada"
        }
    }

    with patch(
        "main.db_manager.obtener_usuario",
        return_value=None
    ):

        with patch(
            "main.db_manager.guardar_reporte"
        ) as mock_guardar_reporte:

            with patch("main.bot.send_message") as mock_send_message:

                main.procesar_datos_llm(chat_id, datos)

                mock_guardar_reporte.assert_not_called()

                mock_send_message.assert_called_once()

def test_procesar_intencion_desconocida():
    chat_id = 12345

    datos = {
        "intencion": "algo_que_no_existe",
        "entidades": {}
    }

    with patch("main.bot.send_message") as mock_send_message:

        main.procesar_datos_llm(chat_id, datos)

        mock_send_message.assert_called_once()