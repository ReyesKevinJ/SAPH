import json
import unittest
from unittest.mock import patch, mock_open

import enviar_alertas_json

class TestEnvioAlertas(unittest.TestCase):

    @patch("enviar_alertas_json.bot.send_message")
    @patch("enviar_alertas_json.db_manager.obtener_chat_ids_por_barrio")
    def test_enviar_alertas_diferentes(self, mock_obtener_chat_ids, mock_send_message):
        # Mocks: Retornar ID de chat solo si son los barrios con usuarios
        mock_obtener_chat_ids.side_effect = lambda barrio: [111] if barrio == "Cambá Cuá" else ([222] if barrio == "17 de Agosto" else [])
        
        json_content = {
            "mensaje_general": "ALERTA TEST",
            "analisis_barrios": {
                "Cambá Cuá": {"nivel": 4, "alerta": "ALERTA ROJA: Tormenta severa."},
                "17 de Agosto": {"nivel": 3, "alerta": "ALERTA NARANJA: Lluvia fuerte."},
                "Centro": {"nivel": 0, "alerta": "CIELO DESPEJADO"} # Este barrio no tiene usuarios (mock)
            }
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(json_content))):
            enviar_alertas_json.enviar_alertas_desde_json("dummy.json")
            
        # Verificar que el barrio Cambá Cuá recibe alerta roja (nivel 4)
        mock_send_message.assert_any_call(111, "🔴 ATENCIÓN - Cambá Cuá\nNivel de Alerta: 4\nSituación: ALERTA ROJA: Tormenta severa.")
        
        # Verificar que 17 de Agosto recibe alerta naranja (nivel 3)
        mock_send_message.assert_any_call(222, "🟠 ATENCIÓN - 17 de Agosto\nNivel de Alerta: 3\nSituación: ALERTA NARANJA: Lluvia fuerte.")
        
        # Validar que solo se mandaron 2 mensajes
        self.assertEqual(mock_send_message.call_count, 2)
