import schedule
import time
import logging
import threading
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Callable, Optional

# Configurazione del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('scheduler')

class Scheduler:
    """
    Classe per la gestione dell'esecuzione periodica delle varie funzionalità
    del sistema di monitoraggio OpenData del Parlamento Europeo.
    """
    
    def __init__(self, base_dir: str, config_manager: Any):
        """
        Inizializza lo scheduler con la directory di base e il gestore di configurazione.
        
        Args:
            base_dir (str): Directory di base del progetto
            config_manager (Any): Gestore della configurazione
        """
        self.base_dir = Path(base_dir)
        self.config_manager = config_manager
        self.config = config_manager.get_config('scheduler')
        self.running = False
        self.thread = None
        
        logger.info(f"Inizializzato Scheduler con base_dir: {base_dir}")
    
    def start(self) -> None:
        """
        Avvia lo scheduler in un thread separato.
        """
        if self.running:
            logger.warning("Lo scheduler è già in esecuzione")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info("Scheduler avviato")
    
    def stop(self) -> None:
        """
        Ferma lo scheduler.
        """
        if not self.running:
            logger.warning("Lo scheduler non è in esecuzione")
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("Scheduler fermato")
    
    def _run_scheduler(self) -> None:
        """
        Esegue lo scheduler in un ciclo infinito.
        """
        logger.info("Scheduler in esecuzione")
        
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def schedule_data_fetch(self, data_fetcher: Any, keyword_analyzer: Any, email_notifier: Any) -> None:
        """
        Pianifica l'esecuzione periodica del recupero dati.
        
        Args:
            data_fetcher (Any): Modulo di recupero dati
            keyword_analyzer (Any): Modulo di analisi delle keyword
            email_notifier (Any): Modulo di notifica email
        """
        def fetch_and_analyze():
            try:
                logger.info("Esecuzione recupero dati periodico")
                
                # Recupera i documenti
                documents = data_fetcher.fetch_plenary_documents()
                
                if not documents:
                    logger.info("Nessun documento recuperato")
                    return
                
                # Filtra i documenti in base alle keyword
                matching_documents = keyword_analyzer.filter_documents(documents)
                
                if not matching_documents:
                    logger.info("Nessun documento contiene le keyword")
                    return
                
                # Calcola le statistiche delle keyword
                keyword_stats = keyword_analyzer.get_document_keyword_stats(matching_documents)
                
                # Invia notifica email
                email_notifier.notify_matching_documents(matching_documents, keyword_stats)
                
                logger.info(f"Recupero dati completato: trovati {len(matching_documents)} documenti con keyword")
                
            except Exception as e:
                logger.error(f"Errore durante il recupero dati periodico: {e}")
        
        # Pianifica l'esecuzione in base alla configurazione
        cron_expression = self.config.get('data_fetch_cron', '0 * * * *')  # Default: ogni ora
        
        # Converte l'espressione cron in un formato compatibile con schedule
        minute, hour, day_of_month, month, day_of_week = cron_expression.split()
        
        if minute == '0' and hour == '*':
            # Ogni ora all'inizio dell'ora
            schedule.every().hour.at(':00').do(fetch_and_analyze)
            logger.info("Recupero dati pianificato: ogni ora")
        else:
            # Usa l'espressione cron completa
            # Nota: schedule ha supporto limitato per le espressioni cron,
            # quindi questa è una semplificazione
            if hour == '*':
                # Ogni ora a un minuto specifico
                schedule.every().hour.at(f':{minute}').do(fetch_and_analyze)
                logger.info(f"Recupero dati pianificato: ogni ora al minuto {minute}")
            else:
                # Orari specifici
                for h in range(24):
                    if hour == '*' or str(h) == hour:
                        schedule.every().day.at(f'{h:02d}:{minute}').do(fetch_and_analyze)
                
                logger.info(f"Recupero dati pianificato: alle {hour}:{minute}")
    
    def schedule_daily_report(self, report_generator: Any, email_notifier: Any) -> None:
        """
        Pianifica l'esecuzione giornaliera della generazione del report.
        
        Args:
            report_generator (Any): Modulo di generazione dei report
            email_notifier (Any): Modulo di notifica email
        """
        def generate_daily_report():
            try:
                logger.info("Esecuzione generazione report giornaliero")
                
                # Genera il report
                report_file = report_generator.generate_daily_report()
                
                if not report_file:
                    logger.warning("Impossibile generare il report giornaliero")
                    return
                
                # Legge il contenuto del report
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_content = f.read()
                
                # Invia il report via email
                date_str = datetime.now().strftime('%Y-%m-%d')
                subject = f"Report giornaliero fintech - {date_str}"
                email_notifier.send_notification(subject, report_content)
                
                logger.info(f"Report giornaliero generato e inviato: {report_file}")
                
            except Exception as e:
                logger.error(f"Errore durante la generazione del report giornaliero: {e}")
        
        # Pianifica l'esecuzione in base alla configurazione
        report_time = self.config.get('daily_report_cron', '0 18 * * *').split()[1]  # Default: alle 18:00
        
        schedule.every().day.at(f"{report_time}:00").do(generate_daily_report)
        logger.info(f"Generazione report giornaliero pianificata: alle {report_time}:00")
    
    def schedule_weekly_report(self, report_generator: Any, email_notifier: Any) -> None:
        """
        Pianifica l'esecuzione settimanale della generazione del report predittivo.
        
        Args:
            report_generator (Any): Modulo di generazione dei report
            email_notifier (Any): Modulo di notifica email
        """
        def generate_weekly_report():
            try:
                logger.info("Esecuzione generazione report settimanale predittivo")
                
                # Genera il report
                report_file = report_generator.generate_weekly_predictive_report()
                
                if not report_file:
                    logger.warning("Impossibile generare il report settimanale predittivo")
                    return
                
                # Legge il contenuto del report
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_content = f.read()
                
                # Invia il report via email
                date_str = datetime.now().strftime('%Y-%m-%d')
                subject = f"Report settimanale predittivo fintech - {date_str}"
                email_notifier.send_notification(subject, report_content)
                
                logger.info(f"Report settimanale predittivo generato e inviato: {report_file}")
                
            except Exception as e:
                logger.error(f"Errore durante la generazione del report settimanale predittivo: {e}")
        
        # Pianifica l'esecuzione in base alla configurazione
        cron_parts = self.config.get('weekly_report_cron', '0 12 * * 0').split()  # Default: domenica alle 12:00
        day_of_week = int(cron_parts[4])  # 0 = lunedì, 6 = domenica
        hour = cron_parts[1]
        
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        day_name = days[day_of_week]
        
        # Pianifica l'esecuzione
        getattr(schedule.every(), day_name).at(f"{hour}:00").do(generate_weekly_report)
        logger.info(f"Generazione report settimanale predittivo pianificata: ogni {day_name} alle {hour}:00")
    
    def schedule_all(self, data_fetcher: Any, keyword_analyzer: Any, report_generator: Any, email_notifier: Any) -> None:
        """
        Pianifica l'esecuzione di tutte le funzionalità.
        
        Args:
            data_fetcher (Any): Modulo di recupero dati
            keyword_analyzer (Any): Modulo di analisi delle keyword
            report_generator (Any): Modulo di generazione dei report
            email_notifier (Any): Modulo di notifica email
        """
        # Pianifica il recupero dati
        self.schedule_data_fetch(data_fetcher, keyword_analyzer, email_notifier)
        
        # Pianifica la generazione del report giornaliero
        self.schedule_daily_report(report_generator, email_notifier)
        
        # Pianifica la generazione del report settimanale predittivo
        self.schedule_weekly_report(report_generator, email_notifier)
        
        logger.info("Tutte le funzionalità sono state pianificate")
