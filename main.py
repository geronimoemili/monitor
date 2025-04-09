#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script principale per il sistema di monitoraggio OpenData del Parlamento Europeo per il fintech.
Questo script inizializza tutti i moduli e avvia lo scheduler per l'esecuzione periodica.
"""

import os
import sys
import logging
import time
from pathlib import Path

# Configurazione del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("eu_parliament_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('main')

# Aggiungi la directory corrente al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa i moduli del sistema
from config.config_manager import ConfigManager
from data_fetcher.eu_parliament_fetcher import EUParliamentDataFetcher
from keyword_analyzer.keyword_analyzer import KeywordAnalyzer
from email_notifier.email_notifier import EmailNotifier
from reporting.report_generator import ReportGenerator
from utils.scheduler import Scheduler

def main():
    """
    Funzione principale che inizializza e avvia il sistema.
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
        
        # Inizializza lo scheduler
        logger.info("Inizializzazione dello scheduler...")
        scheduler = Scheduler(base_dir, config_manager)
        
        # Pianifica l'esecuzione di tutte le funzionalità
        logger.info("Pianificazione delle funzionalità...")
        scheduler.schedule_all(data_fetcher, keyword_analyzer, report_generator, email_notifier)
        
        # Avvia lo scheduler
        logger.info("Avvio dello scheduler...")
        scheduler.start()
        
        # Esegui un recupero dati iniziale
        logger.info("Esecuzione del recupero dati iniziale...")
        documents = data_fetcher.fetch_plenary_documents()
        
        if documents:
            logger.info(f"Recuperati {len(documents)} documenti")
            
            # Filtra i documenti in base alle keyword
            matching_documents = keyword_analyzer.filter_documents(documents)
            
            if matching_documents:
                logger.info(f"Trovati {len(matching_documents)} documenti con keyword")
                
                # Calcola le statistiche delle keyword
                keyword_stats = keyword_analyzer.get_document_keyword_stats(matching_documents)
                
                # Invia notifica email
                email_notifier.notify_matching_documents(matching_documents, keyword_stats)
                
                # Genera un report giornaliero
                report_generator.generate_daily_report()
            else:
                logger.info("Nessun documento contiene le keyword")
        else:
            logger.info("Nessun documento recuperato")
        
        # Mantieni il processo in esecuzione
        logger.info("Sistema avviato e in esecuzione. Premi Ctrl+C per terminare.")
        
        try:
            # Loop infinito per mantenere il processo in esecuzione
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Interruzione richiesta dall'utente")
            
            # Ferma lo scheduler
            scheduler.stop()
            
            logger.info("Sistema terminato")
    
    except Exception as e:
        logger.error(f"Errore durante l'esecuzione del sistema: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
