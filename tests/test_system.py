import unittest
import os
import json
from pathlib import Path
from config.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    """Test per il modulo di gestione della configurazione."""

    def setUp(self):
        """Prepara un file di configurazione di test valido."""
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.test_config_file = os.path.join(self.base_dir, 'config', 'test_config.json')

        # Crea la struttura minima per i test
        self.test_config = {
            "general": {
                "debug_mode": True,
                "log_level": "DEBUG"
            },
            "data_fetcher": {
                "api_base_url": "https://test.example.com/api",
                "plenary_endpoint": "/test-endpoint",
                "fetch_interval_hours": 1,
                "max_retries": 3,
                "timeout": 30,
                "csv_storage": False
            },
            "keyword_analyzer": {},
            "email_notifier": {},
            "reporting": {},
            "scheduler": {}
        }

        # Scrive il file JSON di test
        os.makedirs(os.path.dirname(self.test_config_file), exist_ok=True)
        with open(self.test_config_file, 'w') as f:
            json.dump(self.test_config, f, indent=2)

        self.manager = ConfigManager(self.base_dir, os.path.basename(self.test_config_file))

    def tearDown(self):
        """Elimina il file di test dopo l'esecuzione."""
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)

    def test_initialization(self):
        """Verifica che il manager sia inizializzato correttamente."""
        self.assertTrue(isinstance(self.manager.base_dir, Path))
        self.assertTrue(isinstance(self.manager.config_dir, Path))
        self.assertTrue(isinstance(self.manager.config_file, Path))
        self.assertIn('general', self.manager.default_config)
        self.assertIn('data_fetcher', self.manager.default_config)

    def test_load_and_save_config(self):
        """Verifica il salvataggio e il caricamento della configurazione."""
        updated_config = {
            "general": {
                "debug_mode": False,
                "log_level": "INFO"
            }
        }
        self.manager.save_config(updated_config)
        loaded = self.manager.load_config()
        self.assertEqual(loaded["general"]["debug_mode"], False)
        self.assertEqual(loaded["general"]["log_level"], "INFO")

    def test_get_config(self):
        """Verifica il recupero della configurazione di un modulo."""
        data_fetcher_config = self.manager.get_config('data_fetcher')
        self.assertEqual(data_fetcher_config["api_base_url"], "https://test.example.com/api")
        self.assertEqual(data_fetcher_config["plenary_endpoint"], "/test-endpoint")
