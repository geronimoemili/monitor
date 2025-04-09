import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple, Any

# Configurazione del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('keyword_analyzer')

class KeywordAnalyzer:
    """
    Classe per l'analisi delle keyword nei documenti.
    Si occupa di caricare le keyword da file e analizzare i documenti
    per trovare corrispondenze con le keyword relative al settore fintech.
    """
    
    def __init__(self, base_dir: str, config: Optional[Dict[str, Any]] = None):
        """
        Inizializza l'analizzatore di keyword con la directory di base e la configurazione.
        
        Args:
            base_dir (str): Directory di base del progetto
            config (dict, optional): Configurazione personalizzata
        """
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / 'data'
        
        # Configurazione di default
        self.config = {
            'keyword_file': 'fintech_keywords.txt',
            'case_sensitive': False,
            'match_whole_word': False,
            'min_keyword_length': 3,
            'max_results': 1000
        }
        
        # Aggiorna la configurazione con i valori personalizzati
        if config:
            self.config.update(config)
        
        self.keywords: Set[str] = set()
        self.load_keywords()
        
        logger.info(f"Inizializzato KeywordAnalyzer con {len(self.keywords)} keyword")
    
    def load_keywords(self, file_path: Optional[str] = None) -> None:
        """
        Carica le keyword da un file di testo.
        
        Args:
            file_path (str, optional): Percorso del file contenente le keyword.
                                      Se non specificato, usa il percorso di default.
        """
        if not file_path:
            file_path = self.data_dir / self.config['keyword_file']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    keyword = line.strip()
                    if len(keyword) >= self.config['min_keyword_length']:
                        if self.config['case_sensitive']:
                            self.keywords.add(keyword)
                        else:
                            self.keywords.add(keyword.lower())
            
            logger.info(f"Caricate {len(self.keywords)} keyword da {file_path}")
        
        except Exception as e:
            logger.error(f"Errore durante il caricamento delle keyword da {file_path}: {e}")
    
    def add_keyword(self, keyword: str) -> None:
        """
        Aggiunge una nuova keyword all'insieme delle keyword.
        
        Args:
            keyword (str): Keyword da aggiungere
        """
        if len(keyword) >= self.config['min_keyword_length']:
            if not self.config['case_sensitive']:
                keyword = keyword.lower()
            
            self.keywords.add(keyword)
            logger.info(f"Aggiunta nuova keyword: {keyword}")
    
    def remove_keyword(self, keyword: str) -> None:
        """
        Rimuove una keyword dall'insieme delle keyword.
        
        Args:
            keyword (str): Keyword da rimuovere
        """
        if not self.config['case_sensitive']:
            keyword = keyword.lower()
        
        if keyword in self.keywords:
            self.keywords.remove(keyword)
            logger.info(f"Rimossa keyword: {keyword}")
        else:
            logger.warning(f"Keyword non trovata: {keyword}")
    
    def save_keywords(self, file_path: Optional[str] = None) -> None:
        """
        Salva le keyword correnti in un file di testo.
        
        Args:
            file_path (str, optional): Percorso del file in cui salvare le keyword.
                                      Se non specificato, usa il percorso di default.
        """
        if not file_path:
            file_path = self.data_dir / self.config['keyword_file']
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for keyword in sorted(self.keywords):
                    f.write(f"{keyword}\n")
            
            logger.info(f"Salvate {len(self.keywords)} keyword in {file_path}")
        
        except Exception as e:
            logger.error(f"Errore durante il salvataggio delle keyword in {file_path}: {e}")
    
    def analyze_text(self, text: str) -> Dict[str, int]:
        """
        Analizza un testo per trovare corrispondenze con le keyword.
        
        Args:
            text (str): Testo da analizzare
            
        Returns:
            dict: Dizionario con le keyword trovate e il numero di occorrenze
        """
        if not text:
            return {}
        
        if not self.config['case_sensitive']:
            text = text.lower()
        
        results: Dict[str, int] = {}
        
        for keyword in self.keywords:
            if self.config['match_whole_word']:
                # Cerca solo parole intere
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, text)
            else:
                # Cerca anche parti di parole
                matches = re.findall(re.escape(keyword), text)
            
            if matches:
                results[keyword] = len(matches)
        
        return results
    
    def analyze_document(self, document: Dict[str, Any]) -> Tuple[bool, Dict[str, int]]:
        """
        Analizza un documento per trovare corrispondenze con le keyword.
        
        Args:
            document (dict): Documento da analizzare
            
        Returns:
            tuple: (bool, dict) - Indica se sono state trovate corrispondenze e
                                 un dizionario con le keyword trovate e il numero di occorrenze
        """
        # Estrae il testo dal documento
        # Nota: la struttura del documento dipende dal formato specifico
        # dei dati restituiti dalle API del Parlamento Europeo
        text = ""
        
        # Prova a estrarre il testo da campi comuni
        for field in ['title', 'content', 'description', 'text', 'summary']:
            if field in document and isinstance(document[field], str):
                text += document[field] + " "
        
        # Se non è stato trovato testo nei campi comuni, usa l'intero documento
        if not text:
            text = str(document)
        
        # Analizza il testo
        results = self.analyze_text(text)
        
        return bool(results), results
    
    def filter_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filtra una lista di documenti per trovare quelli che contengono le keyword.
        
        Args:
            documents (list): Lista di documenti da filtrare
            
        Returns:
            list: Lista di documenti che contengono almeno una delle keyword
        """
        if not documents:
            return []
        
        matching_documents = []
        
        for doc in documents:
            has_match, _ = self.analyze_document(doc)
            if has_match:
                matching_documents.append(doc)
                
                # Limita il numero di risultati se necessario
                if len(matching_documents) >= self.config['max_results']:
                    logger.warning(f"Raggiunto il limite massimo di risultati ({self.config['max_results']})")
                    break
        
        logger.info(f"Trovati {len(matching_documents)} documenti su {len(documents)} che contengono le keyword")
        return matching_documents
    
    def get_document_keyword_stats(self, documents: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Calcola le statistiche delle keyword trovate in una lista di documenti.
        
        Args:
            documents (list): Lista di documenti da analizzare
            
        Returns:
            dict: Dizionario con le keyword trovate e il numero totale di occorrenze
        """
        if not documents:
            return {}
        
        total_stats: Dict[str, int] = {}
        
        for doc in documents:
            _, doc_stats = self.analyze_document(doc)
            
            for keyword, count in doc_stats.items():
                if keyword in total_stats:
                    total_stats[keyword] += count
                else:
                    total_stats[keyword] = count
        
        # Ordina le statistiche per numero di occorrenze (decrescente)
        sorted_stats = {k: v for k, v in sorted(total_stats.items(), key=lambda item: item[1], reverse=True)}
        
        return sorted_stats
