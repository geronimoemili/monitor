import requests
import logging
import csv
import os
import json
from datetime import datetime
from pathlib import Path

# Configurazione del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('eu_parliament_data_fetcher')

class EUParliamentDataFetcher:
    """
    Classe per il recupero dei dati dalle API OpenData del Parlamento Europeo.
    Si occupa di connettersi alle API, recuperare i documenti e salvarli localmente.
    """
    
    def __init__(self, base_dir, config=None):
        """
        Inizializza il fetcher con la directory di base e la configurazione.
        
        Args:
            base_dir (str): Directory di base per il salvataggio dei dati
            config (dict, optional): Configurazione personalizzata
        """
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / 'data'
        self.data_dir.mkdir(exist_ok=True)
        
        # Configurazione di default
        self.config = {
            'api_base_url': 'https://data.europarl.europa.eu/api/v2',
            'plenary_endpoint': '/plenary-documents',
            'fetch_interval_hours': 1,
            'max_retries': 3,
            'timeout': 30,
            'csv_storage': True
        }
        
        # Aggiorna la configurazione con i valori personalizzati
        if config:
            self.config.update(config)
        
        logger.info(f"Inizializzato EUParliamentDataFetcher con base_dir: {base_dir}")
    
    def fetch_plenary_documents(self, year=None, limit=100):
        """
        Recupera i documenti delle sessioni plenarie del Parlamento Europeo.
        
        Args:
            year (int, optional): Anno specifico per cui recuperare i documenti
            limit (int, optional): Numero massimo di documenti da recuperare
            
        Returns:
            list: Lista di documenti recuperati
        """
        # Se non è specificato l'anno, usa l'anno corrente
        if not year:
            year = datetime.now().year
            
        endpoint = f"{self.config['api_base_url']}{self.config['plenary_endpoint']}"
        params = {
            'year': year,
            'limit': limit,
            'format': 'json'
        }
        
        logger.info(f"Recupero documenti plenari per l'anno {year}")
        
        try:
            response = requests.get(endpoint, params=params, timeout=self.config['timeout'])
            response.raise_for_status()
            
            documents = response.json()
            logger.info(f"Recuperati {len(documents)} documenti")
            
            # Salva i documenti in formato CSV se richiesto
            if self.config['csv_storage']:
                self._save_documents_to_csv(documents, year)
                
            return documents
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Errore durante il recupero dei documenti: {e}")
            return []
    
    def _save_documents_to_csv(self, documents, year):
        """
        Salva i documenti recuperati in un file CSV.
        
        Args:
            documents (list): Lista di documenti da salvare
            year (int): Anno di riferimento per il nome del file
        """
        if not documents:
            logger.warning("Nessun documento da salvare")
            return
            
        csv_file = self.data_dir / f"plenary_documents_{year}.csv"
        
        try:
            # Determina i campi dai documenti
            if isinstance(documents, list) and documents:
                fieldnames = documents[0].keys()
            else:
                logger.warning("Formato documenti non valido")
                return
                
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(documents)
                
            logger.info(f"Documenti salvati in {csv_file}")
            
        except Exception as e:
            logger.error(f"Errore durante il salvataggio dei documenti in CSV: {e}")
    
    def fetch_document_content(self, document_id):
        """
        Recupera il contenuto completo di un documento specifico.
        
        Args:
            document_id (str): ID del documento da recuperare
            
        Returns:
            dict: Contenuto del documento
        """
        endpoint = f"{self.config['api_base_url']}{self.config['plenary_endpoint']}/{document_id}"
        
        try:
            response = requests.get(endpoint, timeout=self.config['timeout'])
            response.raise_for_status()
            
            content = response.json()
            logger.info(f"Recuperato contenuto del documento {document_id}")
            
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Errore durante il recupero del contenuto del documento {document_id}: {e}")
            return None
    
    def search_documents_by_keywords(self, keywords, year=None, limit=100):
        """
        Cerca documenti che contengono specifiche keyword.
        
        Args:
            keywords (list): Lista di keyword da cercare
            year (int, optional): Anno specifico per cui cercare
            limit (int, optional): Numero massimo di documenti da recuperare
            
        Returns:
            list: Lista di documenti che contengono almeno una delle keyword
        """
        # Recupera i documenti
        documents = self.fetch_plenary_documents(year, limit)
        
        if not documents:
            return []
            
        # Filtra i documenti che contengono almeno una delle keyword
        matching_documents = []
        
        for doc in documents:
            # Controlla se il documento contiene almeno una delle keyword
            # Nota: questa è una ricerca semplificata, in un'implementazione reale
            # potrebbe essere necessario accedere al contenuto completo del documento
            doc_text = json.dumps(doc, ensure_ascii=False).lower()
            
            if any(keyword.lower() in doc_text for keyword in keywords):
                matching_documents.append(doc)
        
        logger.info(f"Trovati {len(matching_documents)} documenti che contengono le keyword")
        return matching_documents
