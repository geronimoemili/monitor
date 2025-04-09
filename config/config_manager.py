import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configurazione del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('config_manager')

class ConfigManager:
    """
    Classe per la gestione della configurazione del sistema.
    Si occupa di caricare, salvare e fornire accesso alle impostazioni di configurazione.
    """
    
    def __init__(self, base_dir: str, config_file: str = 'config.json'):
        """
        Inizializza il gestore di configurazione.
        
        Args:
            base_dir (str): Directory di base del progetto
            config_file (str, optional): Nome del file di configurazione
        """
        self.base_dir = Path(base_dir)
        self.config_dir = self.base_dir / 'config'
        self.config_file = self.config_dir / config_file
        
        # Configurazione di default
        self.default_config = {
            # Configurazione generale
            'general': {
                'debug_mode': False,
                'log_level': 'INFO',
                'data_storage_format': 'csv'
            },
            
            # Configurazione per il recupero dati
            'data_fetcher': {
                'api_base_url': 'https://data.europarl.europa.eu/api/v2',
                'plenary_endpoint': '/plenary-documents',
                'fetch_interval_hours': 1,
                'max_retries': 3,
                'timeout': 30,
                'csv_storage': True
            },
            
            # Configurazione per l'analisi delle keyword
            'keyword_analyzer': {
                'keyword_file': 'fintech_keywords.txt',
                'case_sensitive': False,
                'match_whole_word': False,
                'min_keyword_length': 3,
                'max_results': 1000
            },
            
            # Configurazione per le notifiche email
            'email_notifier': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'smtp_username': '',
                'smtp_password': '',
                'sender_email': 'noreply@example.com',
                'recipients_file': 'email_recipients.txt',
                'use_tls': True,
                'email_subject_prefix': '[EU Parliament Fintech Monitor] ',
                'max_documents_in_email': 10
            },
            
            # Configurazione per la reportistica
            'reporting': {
                'daily_report_time': '18:00',
                'weekly_report_day': 6,  # 0 = lunedì, 6 = domenica
                'report_format': 'txt',
                'max_keywords_in_report': 20,
                'max_documents_in_report': 50,
                'charts_enabled': True,
                'trend_analysis_days': 30,
                'prediction_horizon_days': 7
            },
            
            # Configurazione per lo scheduler
            'scheduler': {
                'data_fetch_cron': '0 * * * *',  # Ogni ora
                'daily_report_cron': '0 18 * * *',  # Alle 18:00 ogni giorno
                'weekly_report_cron': '0 12 * * 0',  # Alle 12:00 ogni domenica
                'timezone': 'Europe/Rome'
            }
        }
        
        # Carica la configurazione dal file o crea il file con la configurazione di default
        self.config = self.load_config()
        
        logger.info(f"Inizializzato ConfigManager con config_file: {self.config_file}")
    
    def load_config(self) -> Dict[str, Any]:
        """
        Carica la configurazione dal file.
        Se il file non esiste, crea un nuovo file con la configurazione di default.
        
        Returns:
            dict: Configurazione caricata
        """
        # Crea la directory di configurazione se non esiste
        self.config_dir.mkdir(exist_ok=True)
        
        # Se il file di configurazione non esiste, crea un nuovo file con la configurazione di default
        if not self.config_file.exists():
            return self.save_config(self.default_config)
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info(f"Configurazione caricata da {self.config_file}")
            
            # Aggiorna la configurazione con eventuali nuovi parametri di default
            updated_config = self._update_with_defaults(config)
            
            # Se la configurazione è stata aggiornata, salva il file
            if updated_config != config:
                logger.info("Configurazione aggiornata con nuovi parametri di default")
                return self.save_config(updated_config)
            
            return config
            
        except Exception as e:
            logger.error(f"Errore durante il caricamento della configurazione: {e}")
            logger.info("Utilizzo della configurazione di default")
            return self.save_config(self.default_config)
    
    def save_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Salva la configurazione nel file.
        
        Args:
            config (dict): Configurazione da salvare
            
        Returns:
            dict: Configurazione salvata
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Configurazione salvata in {self.config_file}")
            return config
            
        except Exception as e:
            logger.error(f"Errore durante il salvataggio della configurazione: {e}")
            return self.default_config
    
    def get_config(self, module: Optional[str] = None) -> Dict[str, Any]:
        """
        Restituisce la configurazione completa o di un modulo specifico.
        
        Args:
            module (str, optional): Nome del modulo per cui ottenere la configurazione
            
        Returns:
            dict: Configurazione richiesta
        """
        if module and module in self.config:
            return self.config[module]
        
        return self.config
    
    def update_config(self, module: str, key: str, value: Any) -> bool:
        """
        Aggiorna un valore specifico nella configurazione.
        
        Args:
            module (str): Nome del modulo
            key (str): Chiave da aggiornare
            value (Any): Nuovo valore
            
        Returns:
            bool: True se l'aggiornamento è avvenuto con successo, False altrimenti
        """
        if module not in self.config:
            logger.error(f"Modulo non trovato nella configurazione: {module}")
            return False
        
        if key not in self.config[module]:
            logger.error(f"Chiave non trovata nella configurazione del modulo {module}: {key}")
            return False
        
        # Aggiorna il valore
        self.config[module][key] = value
        
        # Salva la configurazione aggiornata
        self.save_config(self.config)
        
        logger.info(f"Configurazione aggiornata: {module}.{key} = {value}")
        return True
    
    def reset_to_default(self, module: Optional[str] = None) -> bool:
        """
        Ripristina la configurazione di default per un modulo specifico o per l'intero sistema.
        
        Args:
            module (str, optional): Nome del modulo da ripristinare
            
        Returns:
            bool: True se il ripristino è avvenuto con successo, False altrimenti
        """
        try:
            if module:
                if module not in self.default_config:
                    logger.error(f"Modulo non trovato nella configurazione di default: {module}")
                    return False
                
                self.config[module] = self.default_config[module].copy()
                logger.info(f"Configurazione del modulo {module} ripristinata ai valori di default")
            else:
                self.config = self.default_config.copy()
                logger.info("Configurazione completa ripristinata ai valori di default")
            
            # Salva la configurazione aggiornata
            self.save_config(self.config)
            
            return True
            
        except Exception as e:
            logger.error(f"Errore durante il ripristino della configurazione: {e}")
            return False
    
    def _update_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggiorna la configurazione con eventuali nuovi parametri di default.
        
        Args:
            config (dict): Configurazione da aggiornare
            
        Returns:
            dict: Configurazione aggiornata
        """
        updated_config = config.copy()
        
        # Aggiunge moduli mancanti
        for module, module_config in self.default_config.items():
            if module not in updated_config:
                updated_config[module] = module_config.copy()
                continue
            
            # Aggiunge parametri mancanti nei moduli esistenti
            for key, value in module_config.items():
                if key not in updated_config[module]:
                    updated_config[module][key] = value
        
        return updated_config
    
    def create_example_config(self) -> str:
        """
        Crea un file di configurazione di esempio.
        
        Returns:
            str: Percorso del file di configurazione di esempio
        """
        example_file = self.config_dir / 'config.example.json'
        
        try:
            with open(example_file, 'w', encoding='utf-8') as f:
                json.dump(self.default_config, f, indent=4, ensure_ascii=False)
            
            logger.info(f"File di configurazione di esempio creato: {example_file}")
            return str(example_file)
            
        except Exception as e:
            logger.error(f"Errore durante la creazione del file di configurazione di esempio: {e}")
            return ""
