import os
import sys
import logging
from pathlib import Path

# Configurazione del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('example')

# Aggiungi la directory corrente al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa i moduli del sistema
from config.config_manager import ConfigManager
from data_fetcher.eu_parliament_fetcher import EUParliamentDataFetcher
from keyword_analyzer.keyword_analyzer import KeywordAnalyzer
from email_notifier.email_notifier import EmailNotifier
from reporting.report_generator import ReportGenerator

def main():
    """
    Esempio di utilizzo del sistema di monitoraggio OpenData del Parlamento Europeo.
    Questo script dimostra come utilizzare i vari moduli del sistema.
    """
    try:
        # Ottieni il percorso della directory base
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Directory base: {base_dir}")
        
        # Inizializza il gestore della configurazione
        logger.info("Inizializzazione del gestore della configurazione...")
        config_manager = ConfigManager(base_dir)
        
        # Inizializza i vari moduli
        logger.info("Inizializzazione dei moduli...")
        data_fetcher = EUParliamentDataFetcher(base_dir, config_manager.get_config('data_fetcher'))
        keyword_analyzer = KeywordAnalyzer(base_dir, config_manager.get_config('keyword_analyzer'))
        email_notifier = EmailNotifier(base_dir, config_manager.get_config('email_notifier'))
        report_generator = ReportGenerator(base_dir, config_manager.get_config('reporting'))
        
        # Esempio 1: Recupero dati
        logger.info("Esempio 1: Recupero dati dal Parlamento Europeo")
        documents = data_fetcher.fetch_plenary_documents(limit=5)
        logger.info(f"Recuperati {len(documents)} documenti")
        
        # Esempio 2: Analisi delle keyword
        logger.info("Esempio 2: Analisi delle keyword nei documenti")
        matching_documents = keyword_analyzer.filter_documents(documents)
        logger.info(f"Trovati {len(matching_documents)} documenti con keyword")
        
        # Esempio 3: Statistiche delle keyword
        logger.info("Esempio 3: Statistiche delle keyword")
        keyword_stats = keyword_analyzer.get_document_keyword_stats(matching_documents)
        for keyword, count in keyword_stats.items():
            logger.info(f"Keyword: {keyword}, Occorrenze: {count}")
        
        # Esempio 4: Generazione di un report giornaliero
        logger.info("Esempio 4: Generazione di un report giornaliero")
        report_file = report_generator.generate_daily_report()
        logger.info(f"Report generato: {report_file}")
        
        # Esempio 5: Generazione di un report settimanale predittivo
        logger.info("Esempio 5: Generazione di un report settimanale predittivo")
        report_file = report_generator.generate_weekly_predictive_report()
        logger.info(f"Report generato: {report_file}")
        
        # Esempio 6: Invio di una notifica email
        logger.info("Esempio 6: Invio di una notifica email")
        # Nota: questo esempio non invia effettivamente l'email per evitare problemi di configurazione
        logger.info("Per inviare effettivamente l'email, configura il server SMTP in config.json")
        
        logger.info("Esempi completati con successo")
    
    except Exception as e:
        logger.error(f"Errore durante l'esecuzione degli esempi: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
