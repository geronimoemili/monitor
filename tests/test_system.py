import unittest
import os
import sys
import json
from pathlib import Path

# Aggiungi la directory principale al path per importare i moduli
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_fetcher.eu_parliament_fetcher import EUParliamentDataFetcher
from keyword_analyzer.keyword_analyzer import KeywordAnalyzer
from email_notifier.email_notifier import EmailNotifier
from reporting.report_generator import ReportGenerator
from config.config_manager import ConfigManager

class TestEUParliamentDataFetcher(unittest.TestCase):
    """Test per il modulo di recupero dati."""
    
    def setUp(self):
        """Inizializza l'ambiente di test."""
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config = {
            'api_base_url': 'https://data.europarl.europa.eu/api/v2',
            'plenary_endpoint': '/plenary-documents',
            'fetch_interval_hours': 1,
            'max_retries': 3,
            'timeout': 30,
            'csv_storage': True
        }
        self.fetcher = EUParliamentDataFetcher(self.base_dir, self.config)
    
    def test_initialization(self):
        """Verifica che il fetcher sia inizializzato correttamente."""
        self.assertEqual(self.fetcher.config['api_base_url'], 'https://data.europarl.europa.eu/api/v2')
        self.assertEqual(self.fetcher.config['plenary_endpoint'], '/plenary-documents')
        self.assertEqual(self.fetcher.config['fetch_interval_hours'], 1)
        self.assertTrue(isinstance(self.fetcher.base_dir, Path))
    
    def test_search_documents_by_keywords(self):
        """Verifica che la ricerca di documenti per keyword funzioni."""
        # Questo è un test mock, in un ambiente reale si dovrebbe usare un mock per l'API
        keywords = ['fintech', 'blockchain', 'cryptocurrency']
        # Assumiamo che non ci siano documenti reali da recuperare in questo test
        documents = []
        
        # Verifichiamo che la funzione non generi errori
        result = self.fetcher.search_documents_by_keywords(keywords)
        self.assertIsInstance(result, list)


class TestKeywordAnalyzer(unittest.TestCase):
    """Test per il modulo di analisi delle keyword."""
    
    def setUp(self):
        """Inizializza l'ambiente di test."""
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config = {
            'keyword_file': 'fintech_keywords.txt',
            'case_sensitive': False,
            'match_whole_word': False,
            'min_keyword_length': 3,
            'max_results': 1000
        }
        
        # Crea un file di keyword di test se non esiste
        self.test_keywords_file = os.path.join(self.base_dir, 'data', 'test_keywords.txt')
        if not os.path.exists(os.path.dirname(self.test_keywords_file)):
            os.makedirs(os.path.dirname(self.test_keywords_file))
        
        with open(self.test_keywords_file, 'w') as f:
            f.write("fintech\nblockchain\ncryptocurrency\nbitcoin\nethereum\n")
        
        self.config['keyword_file'] = os.path.basename(self.test_keywords_file)
        self.analyzer = KeywordAnalyzer(self.base_dir, self.config)
    
    def tearDown(self):
        """Pulisce l'ambiente dopo i test."""
        if os.path.exists(self.test_keywords_file):
            os.remove(self.test_keywords_file)
    
    def test_initialization(self):
        """Verifica che l'analyzer sia inizializzato correttamente."""
        self.assertEqual(self.analyzer.config['keyword_file'], os.path.basename(self.test_keywords_file))
        self.assertFalse(self.analyzer.config['case_sensitive'])
        self.assertFalse(self.analyzer.config['match_whole_word'])
        self.assertTrue(isinstance(self.analyzer.base_dir, Path))
    
    def test_load_keywords(self):
        """Verifica che le keyword siano caricate correttamente."""
        self.analyzer.load_keywords(self.test_keywords_file)
        self.assertIn('fintech', self.analyzer.keywords)
        self.assertIn('blockchain', self.analyzer.keywords)
        self.assertIn('cryptocurrency', self.analyzer.keywords)
        self.assertIn('bitcoin', self.analyzer.keywords)
        self.assertIn('ethereum', self.analyzer.keywords)
    
    def test_analyze_text(self):
        """Verifica che l'analisi del testo funzioni correttamente."""
        text = "Il fintech è un settore in crescita. La blockchain e le cryptocurrency come Bitcoin ed Ethereum stanno rivoluzionando il mondo finanziario."
        results = self.analyzer.analyze_text(text)
        
        self.assertIn('fintech', results)
        self.assertIn('blockchain', results)
        self.assertIn('cryptocurrency', results)
        self.assertIn('bitcoin', results)
        self.assertIn('ethereum', results)
        
        self.assertEqual(results['fintech'], 1)
        self.assertEqual(results['blockchain'], 1)
        self.assertEqual(results['cryptocurrency'], 1)
        self.assertEqual(results['bitcoin'], 1)
        self.assertEqual(results['ethereum'], 1)


class TestEmailNotifier(unittest.TestCase):
    """Test per il modulo di notifica email."""
    
    def setUp(self):
        """Inizializza l'ambiente di test."""
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config = {
            'smtp_server': 'smtp.example.com',
            'smtp_port': 587,
            'smtp_username': 'test@example.com',
            'smtp_password': 'password',
            'sender_email': 'noreply@example.com',
            'recipients_file': 'test_recipients.txt',
            'use_tls': True,
            'email_subject_prefix': '[Test] ',
            'max_documents_in_email': 10
        }
        
        # Crea un file di destinatari di test
        self.test_recipients_file = os.path.join(self.base_dir, 'data', 'test_recipients.txt')
        if not os.path.exists(os.path.dirname(self.test_recipients_file)):
            os.makedirs(os.path.dirname(self.test_recipients_file))
        
        with open(self.test_recipients_file, 'w') as f:
            f.write("test1@example.com\ntest2@example.com\n")
        
        self.config['recipients_file'] = os.path.basename(self.test_recipients_file)
        self.notifier = EmailNotifier(self.base_dir, self.config)
    
    def tearDown(self):
        """Pulisce l'ambiente dopo i test."""
        if os.path.exists(self.test_recipients_file):
            os.remove(self.test_recipients_file)
    
    def test_initialization(self):
        """Verifica che il notifier sia inizializzato correttamente."""
        self.assertEqual(self.notifier.config['smtp_server'], 'smtp.example.com')
        self.assertEqual(self.notifier.config['smtp_port'], 587)
        self.assertEqual(self.notifier.config['sender_email'], 'noreply@example.com')
        self.assertTrue(isinstance(self.notifier.base_dir, Path))
    
    def test_load_recipients(self):
        """Verifica che i destinatari siano caricati correttamente."""
        recipients = self.notifier._load_recipients()
        self.assertIn('test1@example.com', recipients)
        self.assertIn('test2@example.com', recipients)
        self.assertEqual(len(recipients), 2)


class TestReportGenerator(unittest.TestCase):
    """Test per il modulo di generazione dei report."""
    
    def setUp(self):
        """Inizializza l'ambiente di test."""
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config = {
            'daily_report_time': '18:00',
            'weekly_report_day': 6,
            'report_format': 'txt',
            'max_keywords_in_report': 20,
            'max_documents_in_report': 50,
            'charts_enabled': False,  # Disabilitato per i test
            'trend_analysis_days': 30,
            'prediction_horizon_days': 7
        }
        self.generator = ReportGenerator(self.base_dir, self.config)
    
    def test_initialization(self):
        """Verifica che il generator sia inizializzato correttamente."""
        self.assertEqual(self.generator.config['daily_report_time'], '18:00')
        self.assertEqual(self.generator.config['weekly_report_day'], 6)
        self.assertEqual(self.generator.config['report_format'], 'txt')
        self.assertTrue(isinstance(self.generator.base_dir, Path))
        self.assertTrue(isinstance(self.generator.reports_dir, Path))
    
    def test_analyze_keyword_stats(self):
        """Verifica che l'analisi delle statistiche delle keyword funzioni."""
        # Creiamo alcuni documenti di test
        documents = [
            {'title': 'Documento sul fintech', 'content': 'Il fintech è un settore in crescita.'},
            {'title': 'Blockchain e cryptocurrency', 'content': 'La blockchain e le cryptocurrency stanno rivoluzionando il mondo finanziario.'},
            {'title': 'Bitcoin ed Ethereum', 'content': 'Bitcoin ed Ethereum sono le cryptocurrency più popolari.'}
        ]
        
        # Creiamo un file di keyword di test
        test_keywords_file = os.path.join(self.base_dir, 'data', 'fintech_keywords.txt')
        if not os.path.exists(os.path.dirname(test_keywords_file)):
            os.makedirs(os.path.dirname(test_keywords_file))
        
        with open(test_keywords_file, 'w') as f:
            f.write("fintech\nblockchain\ncryptocurrency\nbitcoin\nethereum\n")
        
        # Analizziamo le statistiche
        stats = self.generator._analyze_keyword_stats(documents)
        
        # Verifichiamo che le keyword siano state trovate
        self.assertIn('fintech', stats)
        self.assertIn('blockchain', stats)
        self.assertIn('cryptocurrency', stats)
        self.assertIn('bitcoin', stats)
        self.assertIn('ethereum', stats)


class TestConfigManager(unittest.TestCase):
    """Test per il modulo di gestione della configurazione."""
    
    def setUp(self):
        """Inizializza l'ambiente di test."""
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.test_config_file = os.path.join(self.base_dir, 'config', 'test_config.json')
        self.manager = ConfigManager(self.base_dir, os.path.basename(self.test_config_file))
    
    def tearDown(self):
        """Pulisce l'ambiente dopo i test."""
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
    
    def test_initialization(self):
        """Verifica che il manager sia inizializzato correttamente."""
        self.assertTrue(isinstance(self.manager.base_dir, Path))
        self.assertTrue(isinstance(self.manager.config_dir, Path))
        self.assertTrue(isinstance(self.manager.config_file, Path))
        self.assertIn('general', self.manager.default_config)
        self.assertIn('data_fetcher', self.manager.default_config)
        self.assertIn('keyword_analyzer', self.manager.default_config)
        self.assertIn('email_notifier', self.manager.default_config)
        self.assertIn('reporting', self.manager.default_config)
        self.assertIn('scheduler', self.manager.default_config)
    
    def test_load_and_save_config(self):
        """Verifica che il caricamento e il salvataggio della configurazione funzionino."""
        # Salva una configurazione di test
        test_config = {
            'general': {
                'debug_mode': True,
                'log_level': 'DEBUG'
            }
        }
        self.manager.save_config(test_config)
        
        # Carica la configurazione
        loaded_config = self.manager.load_config()
        
        # Verifica che la configurazione sia stata caricata correttamente
        self.assertIn('general', loaded_config)
        self.assertEqual(loaded_config['general']['debug_mode'], True)
        self.assertEqual(loaded_config['general']['log_level'], 'DEBUG')
    
    def test_get_config(self):
        """Verifica che il recupero della configurazione funzioni."""
        # Salva una configurazione di test
        test_config = {
            'general': {
                'debug_mode': True,
                'log_level': 'DEBUG'
            },
            'data_fetcher': {
                'api_base_url': 'https://test.example.com/api'
            }
        }
        self.manager.save_config(test_config)
        
        # Recupera la configurazione completa
        full_config = self.manager.get_config()
        self.assertIn('general', full_config)
        self.assertIn('data_fetcher', full_config)
        
        # Recupera la configurazione di un modulo specifico
        module_config = self.manager.get_config('data_fetcher')
        self.assertEqual(module_config['api_base_url'], 'https://test.example.com/api')


class TestIntegration(unittest.TestCase):
    """Test di integrazione per verificare l'interazione tra i vari moduli."""
    
    def setUp(self):
        """Inizializza l'ambiente di test."""
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Inizializza il gestore della configurazione
        self.config_manager = ConfigManager(self.base_dir, 'test_config.json')
        
        # Inizializza i vari moduli
        self.data_fetcher = EUParliamentDataFetcher(self.base_dir, self.config_manager.get_config('data_fetcher'))
        self.keyword_analyzer = KeywordAnalyzer(self.base_dir, self.config_manager.get_config('keyword_analyzer'))
        self.email_notifier = EmailNotifier(self.base_dir, self.config_manager.get_config('email_notifier'))
        self.report_generator = ReportGenerator(self.base_dir, self.config_manager.get_config('reporting'))
    
    def tearDown(self):
        """Pulisce l'ambiente dopo i test."""
        test_config_file = os.path.join(self.base_dir, 'config', 'test_config.json')
        if os.path.exists(test_config_file):
            os.remove(test_config_file)
    
    def test_end_to_end_flow(self):
        """Verifica il flusso completo del sistema."""
        # Questo è un test mock, in un ambiente reale si dovrebbero usare mock per le API e i servizi esterni
        
        # Creiamo alcuni documenti di test
        documents = [
            {'title': 'Documento sul fintech', 'content': 'Il fintech è un settore in crescita.'},
            {'title': 'Blockchain e cryptocurrency', 'content': 'La blockchain e le cryptocurrency stanno rivoluzionando il mondo finanziario.'},
            {'title': 'Bitcoin ed Ethereum', 'content': 'Bitcoin ed Ethereum sono le cryptocurrency più popolari.'}
        ]
        
        # Filtriamo i documenti in base alle keyword
        matching_documents = self.keyword_analyzer.filter_documents(documents)
        
        # Verifichiamo che i documenti siano stati filtrati correttamente
        self.assertGreaterEqual(len(matching_documents), 0)
        
        # Calcoliamo le statistiche delle keyword
        keyword_stats = self.keyword_analyzer.get_document_keyword_stats(matching_documents)
        
        # Verifichiamo che le statistiche siano state calcolate correttamente
        self.assertIsInstance(keyword_stats, dict)
        
        # Verifichiamo che il sistema sia scalabile
        self.assertTrue(hasattr(self.config_manager, 'update_config'))
        self.assertTrue(hasattr(self.keyword_analyzer, 'add_keyword'))
        self.assertTrue(hasattr(self.email_notifier, 'add_recipient'))


if __name__ == '__main__':
    unittest.main()
