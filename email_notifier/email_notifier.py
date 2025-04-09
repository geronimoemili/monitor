import smtplib
import logging
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

# Configurazione del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('email_notifier')

class EmailNotifier:
    """
    Classe per l'invio di email di notifica quando vengono trovate corrispondenze
    tra i documenti del Parlamento Europeo e le keyword fintech.
    """
    
    def __init__(self, base_dir: str, config: Optional[Dict[str, Any]] = None):
        """
        Inizializza il notificatore email con la directory di base e la configurazione.
        
        Args:
            base_dir (str): Directory di base del progetto
            config (dict, optional): Configurazione personalizzata
        """
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / 'data'
        
        # Configurazione di default
        self.config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_username': '',
            'smtp_password': '',
            'sender_email': 'geronimo.emili@gmail.com',
            'recipients_file': 'email_recipients.txt',
            'use_tls': True,
            'email_subject_prefix': '[EU Parliament Fintech Monitor] ',
            'max_documents_in_email': 10
        }
        
        # Aggiorna la configurazione con i valori personalizzati
        if config:
            self.config.update(config)
        
        self.recipients = self._load_recipients()
        
        logger.info(f"Inizializzato EmailNotifier con {len(self.recipients)} destinatari")
    
    def _load_recipients(self) -> List[str]:
        """
        Carica i destinatari delle email da un file.
        
        Returns:
            list: Lista di indirizzi email dei destinatari
        """
        recipients = []
        recipients_file = self.data_dir / self.config['recipients_file']
        
        # Se il file non esiste, lo crea con un indirizzo di default
        if not recipients_file.exists():
            with open(recipients_file, 'w', encoding='utf-8') as f:
                f.write("geronimo.emili@gmail.com\n")
            logger.info(f"Creato file dei destinatari con indirizzo di default")
            return ["geronimo.emili@gmail.com"]
        
        try:
            with open(recipients_file, 'r', encoding='utf-8') as f:
                for line in f:
                    email = line.strip()
                    if email and '@' in email:  # Verifica minima della validità dell'email
                        recipients.append(email)
            
            logger.info(f"Caricati {len(recipients)} destinatari da {recipients_file}")
            return recipients
            
        except Exception as e:
            logger.error(f"Errore durante il caricamento dei destinatari da {recipients_file}: {e}")
            return ["geronimo.emili@gmail.com"]  # Fallback all'indirizzo di default
    
    def add_recipient(self, email: str) -> None:
        """
        Aggiunge un nuovo destinatario alla lista.
        
        Args:
            email (str): Indirizzo email da aggiungere
        """
        if email and '@' in email and email not in self.recipients:
            self.recipients.append(email)
            self._save_recipients()
            logger.info(f"Aggiunto nuovo destinatario: {email}")
        else:
            logger.warning(f"Indirizzo email non valido o già presente: {email}")
    
    def remove_recipient(self, email: str) -> None:
        """
        Rimuove un destinatario dalla lista.
        
        Args:
            email (str): Indirizzo email da rimuovere
        """
        if email in self.recipients:
            self.recipients.remove(email)
            self._save_recipients()
            logger.info(f"Rimosso destinatario: {email}")
        else:
            logger.warning(f"Destinatario non trovato: {email}")
    
    def _save_recipients(self) -> None:
        """
        Salva la lista dei destinatari nel file.
        """
        recipients_file = self.data_dir / self.config['recipients_file']
        
        try:
            with open(recipients_file, 'w', encoding='utf-8') as f:
                for email in self.recipients:
                    f.write(f"{email}\n")
            
            logger.info(f"Salvati {len(self.recipients)} destinatari in {recipients_file}")
            
        except Exception as e:
            logger.error(f"Errore durante il salvataggio dei destinatari in {recipients_file}: {e}")
    
    def send_notification(self, subject: str, body: str) -> bool:
        """
        Invia un'email di notifica a tutti i destinatari.
        
        Args:
            subject (str): Oggetto dell'email
            body (str): Corpo dell'email
            
        Returns:
            bool: True se l'invio è avvenuto con successo, False altrimenti
        """
        if not self.recipients:
            logger.warning("Nessun destinatario configurato, impossibile inviare l'email")
            return False
        
        # Aggiunge il prefisso all'oggetto
        full_subject = f"{self.config['email_subject_prefix']}{subject}"
        
        # Crea il messaggio
        msg = MIMEMultipart()
        msg['From'] = self.config['sender_email']
        msg['To'] = ', '.join(self.recipients)
        msg['Subject'] = full_subject
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            # Connessione al server SMTP
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.ehlo()
            
            # Attiva TLS se richiesto
            if self.config['use_tls']:
                server.starttls()
                server.ehlo()
            
            # Login se sono fornite le credenziali
            if self.config['smtp_username'] and self.config['smtp_password']:
                server.login(self.config['smtp_username'], self.config['smtp_password'])
            
            # Invia l'email
            server.sendmail(self.config['sender_email'], self.recipients, msg.as_string())
            server.quit()
            
            logger.info(f"Email inviata con successo a {len(self.recipients)} destinatari")
            return True
            
        except Exception as e:
            logger.error(f"Errore durante l'invio dell'email: {e}")
            return False
    
    def notify_matching_documents(self, documents: List[Dict[str, Any]], keyword_stats: Dict[str, int]) -> bool:
        """
        Invia una notifica con i documenti che contengono le keyword.
        
        Args:
            documents (list): Lista di documenti che contengono le keyword
            keyword_stats (dict): Statistiche sulle keyword trovate
            
        Returns:
            bool: True se l'invio è avvenuto con successo, False altrimenti
        """
        if not documents:
            logger.info("Nessun documento da notificare")
            return False
        
        # Crea l'oggetto dell'email
        subject = f"Trovati {len(documents)} documenti con keyword fintech"
        
        # Crea il corpo dell'email
        body = f"""Salve,

Sono stati trovati {len(documents)} documenti del Parlamento Europeo che contengono keyword relative al fintech.

Statistiche delle keyword trovate:
"""
        
        # Aggiunge le statistiche delle keyword
        for keyword, count in keyword_stats.items():
            body += f"- {keyword}: {count} occorrenze\n"
        
        body += "\nDocumenti trovati:\n"
        
        # Aggiunge i dettagli dei documenti (limitati al numero massimo configurato)
        max_docs = min(len(documents), self.config['max_documents_in_email'])
        for i, doc in enumerate(documents[:max_docs]):
            # Estrae le informazioni principali dal documento
            title = doc.get('title', 'Titolo non disponibile')
            date = doc.get('date', 'Data non disponibile')
            url = doc.get('url', '')
            
            body += f"\n{i+1}. {title} ({date})"
            if url:
                body += f"\n   URL: {url}"
        
        # Se ci sono più documenti di quelli mostrati, aggiunge una nota
        if len(documents) > max_docs:
            body += f"\n\nNota: sono stati mostrati solo {max_docs} documenti su {len(documents)} trovati."
        
        body += f"""

Questo messaggio è stato generato automaticamente dal sistema di monitoraggio OpenData del Parlamento Europeo per il settore fintech.
Data e ora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Invia la notifica
        return self.send_notification(subject, body)
    
    def create_email_recipients_file(self) -> None:
        """
        Crea un file di esempio con i destinatari delle email.
        """
        recipients_file = self.data_dir / self.config['recipients_file']
        
        if not recipients_file.exists():
            try:
                with open(recipients_file, 'w', encoding='utf-8') as f:
                    f.write("geronimo.emili@gmail.com\n")
                
                logger.info(f"Creato file dei destinatari con indirizzo di default")
                
            except Exception as e:
                logger.error(f"Errore durante la creazione del file dei destinatari: {e}")
        else:
            logger.info(f"Il file dei destinatari esiste già: {recipients_file}")
