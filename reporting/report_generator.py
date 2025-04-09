import os
import logging
import csv
import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Set
import numpy as np
from collections import Counter

# Configurazione del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('reporting')

class ReportGenerator:
    """
    Classe per la generazione di report giornalieri e settimanali
    con analisi dei dati raccolti dal Parlamento Europeo relativi al fintech.
    """
    
    def __init__(self, base_dir: str, config: Optional[Dict[str, Any]] = None):
        """
        Inizializza il generatore di report con la directory di base e la configurazione.
        
        Args:
            base_dir (str): Directory di base del progetto
            config (dict, optional): Configurazione personalizzata
        """
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / 'data'
        self.reports_dir = self.base_dir / 'reports'
        
        # Crea la directory dei report se non esiste
        self.reports_dir.mkdir(exist_ok=True)
        
        # Configurazione di default
        self.config = {
            'daily_report_time': '18:00',
            'weekly_report_day': 6,  # 0 = lunedì, 6 = domenica
            'report_format': 'txt',
            'max_keywords_in_report': 20,
            'max_documents_in_report': 50,
            'charts_enabled': True,
            'trend_analysis_days': 30,
            'prediction_horizon_days': 7
        }
        
        # Aggiorna la configurazione con i valori personalizzati
        if config:
            self.config.update(config)
        
        logger.info(f"Inizializzato ReportGenerator con base_dir: {base_dir}")
    
    def generate_daily_report(self, date: Optional[datetime] = None) -> str:
        """
        Genera un report giornaliero con tutte le keyword trovate e i documenti associati.
        
        Args:
            date (datetime, optional): Data per cui generare il report.
                                      Se non specificata, usa la data corrente.
        
        Returns:
            str: Percorso del file di report generato
        """
        if not date:
            date = datetime.now()
        
        date_str = date.strftime('%Y-%m-%d')
        logger.info(f"Generazione report giornaliero per la data {date_str}")
        
        # Crea il nome del file di report
        report_file = self.reports_dir / f"daily_report_{date_str}.{self.config['report_format']}"
        
        # Raccoglie i dati per il report
        documents = self._collect_daily_documents(date)
        keyword_stats = self._analyze_keyword_stats(documents)
        
        # Genera il report
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"REPORT GIORNALIERO - {date_str}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Generato il: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Statistiche generali
            f.write("STATISTICHE GENERALI\n")
            f.write("-" * 30 + "\n")
            f.write(f"Documenti analizzati: {len(documents)}\n")
            f.write(f"Keyword trovate: {len(keyword_stats)}\n\n")
            
            # Statistiche delle keyword
            f.write("KEYWORD TROVATE\n")
            f.write("-" * 30 + "\n")
            
            if keyword_stats:
                # Limita il numero di keyword mostrate
                top_keywords = list(keyword_stats.items())[:self.config['max_keywords_in_report']]
                
                for keyword, count in top_keywords:
                    f.write(f"- {keyword}: {count} occorrenze\n")
                
                if len(keyword_stats) > self.config['max_keywords_in_report']:
                    f.write(f"\n... e altre {len(keyword_stats) - self.config['max_keywords_in_report']} keyword\n")
            else:
                f.write("Nessuna keyword trovata nei documenti analizzati.\n")
            
            f.write("\n")
            
            # Documenti trovati
            f.write("DOCUMENTI ANALIZZATI\n")
            f.write("-" * 30 + "\n")
            
            if documents:
                # Limita il numero di documenti mostrati
                shown_docs = documents[:self.config['max_documents_in_report']]
                
                for i, doc in enumerate(shown_docs):
                    # Estrae le informazioni principali dal documento
                    title = doc.get('title', 'Titolo non disponibile')
                    date = doc.get('date', 'Data non disponibile')
                    url = doc.get('url', '')
                    keywords_in_doc = self._get_keywords_in_document(doc, keyword_stats.keys())
                    
                    f.write(f"{i+1}. {title} ({date})\n")
                    if url:
                        f.write(f"   URL: {url}\n")
                    
                    if keywords_in_doc:
                        f.write(f"   Keyword trovate: {', '.join(keywords_in_doc)}\n")
                    
                    f.write("\n")
                
                if len(documents) > self.config['max_documents_in_report']:
                    f.write(f"\n... e altri {len(documents) - self.config['max_documents_in_report']} documenti\n")
            else:
                f.write("Nessun documento trovato per la data specificata.\n")
        
        # Genera grafici se abilitati
        if self.config['charts_enabled'] and keyword_stats:
            self._generate_keyword_chart(keyword_stats, date_str, "daily")
        
        logger.info(f"Report giornaliero generato: {report_file}")
        return str(report_file)
    
    def generate_weekly_predictive_report(self, end_date: Optional[datetime] = None) -> str:
        """
        Genera un report settimanale predittivo con analisi dei trend e previsioni.
        
        Args:
            end_date (datetime, optional): Data di fine della settimana.
                                         Se non specificata, usa la data corrente.
        
        Returns:
            str: Percorso del file di report generato
        """
        if not end_date:
            end_date = datetime.now()
        
        # Calcola la data di inizio della settimana (7 giorni prima)
        start_date = end_date - timedelta(days=7)
        
        date_range = f"{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}"
        logger.info(f"Generazione report settimanale predittivo per il periodo {date_range}")
        
        # Crea il nome del file di report
        report_file = self.reports_dir / f"weekly_predictive_report_{date_range}.{self.config['report_format']}"
        
        # Raccoglie i dati per il report
        weekly_documents = self._collect_weekly_documents(start_date, end_date)
        weekly_keyword_stats = self._analyze_keyword_stats(weekly_documents)
        
        # Analisi dei trend
        trend_data = self._analyze_trends(end_date)
        
        # Previsioni
        predictions = self._generate_predictions(trend_data)
        
        # Genera il report
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"REPORT SETTIMANALE PREDITTIVO - {date_range}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Generato il: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Statistiche generali
            f.write("STATISTICHE GENERALI\n")
            f.write("-" * 30 + "\n")
            f.write(f"Periodo analizzato: {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}\n")
            f.write(f"Documenti analizzati: {len(weekly_documents)}\n")
            f.write(f"Keyword trovate: {len(weekly_keyword_stats)}\n\n")
            
            # Analisi dei trend
            f.write("ANALISI DEI TREND\n")
            f.write("-" * 30 + "\n")
            
            if trend_data:
                for keyword, trend in trend_data.items():
                    direction = "in aumento" if trend > 0 else "in diminuzione" if trend < 0 else "stabile"
                    f.write(f"- {keyword}: {direction} ({trend:+.2f}%)\n")
            else:
                f.write("Dati insufficienti per l'analisi dei trend.\n")
            
            f.write("\n")
            
            # Previsioni
            f.write("PREVISIONI PER LA PROSSIMA SETTIMANA\n")
            f.write("-" * 30 + "\n")
            
            if predictions:
                for keyword, prediction in predictions.items():
                    f.write(f"- {keyword}: si prevede un'occorrenza di circa {prediction:.0f} volte\n")
            else:
                f.write("Dati insufficienti per generare previsioni.\n")
            
            f.write("\n")
            
            # Suggerimenti
            f.write("SUGGERIMENTI E OPPORTUNITÀ\n")
            f.write("-" * 30 + "\n")
            
            if trend_data:
                # Identifica le keyword con trend più significativi
                top_trends = sorted(trend_data.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
                
                for keyword, trend in top_trends:
                    if trend > 10:
                        f.write(f"- {keyword}: Trend fortemente positivo, potrebbe rappresentare un'opportunità emergente nel settore fintech.\n")
                    elif trend > 5:
                        f.write(f"- {keyword}: Trend positivo, consigliato monitoraggio attento per potenziali opportunità.\n")
                    elif trend < -10:
                        f.write(f"- {keyword}: Trend fortemente negativo, potrebbe indicare un declino di interesse o cambiamenti normativi.\n")
                    elif trend < -5:
                        f.write(f"- {keyword}: Trend negativo, consigliato verificare le cause del calo di interesse.\n")
            else:
                f.write("Dati insufficienti per generare suggerimenti.\n")
        
        # Genera grafici se abilitati
        if self.config['charts_enabled']:
            if weekly_keyword_stats:
                self._generate_keyword_chart(weekly_keyword_stats, date_range, "weekly")
            
            if trend_data:
                self._generate_trend_chart(trend_data, date_range)
            
            if predictions:
                self._generate_prediction_chart(predictions, date_range)
        
        logger.info(f"Report settimanale predittivo generato: {report_file}")
        return str(report_file)
    
    def _collect_daily_documents(self, date: datetime) -> List[Dict[str, Any]]:
        """
        Raccoglie i documenti per una data specifica.
        
        Args:
            date (datetime): Data per cui raccogliere i documenti
            
        Returns:
            list: Lista di documenti
        """
        date_str = date.strftime('%Y-%m-%d')
        documents = []
        
        # Cerca file CSV con i documenti per la data specificata
        csv_pattern = f"*{date_str}*.csv"
        csv_files = list(self.data_dir.glob(csv_pattern))
        
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        documents.append(dict(row))
                
                logger.info(f"Caricati {len(documents)} documenti da {csv_file}")
                
            except Exception as e:
                logger.error(f"Errore durante il caricamento dei documenti da {csv_file}: {e}")
        
        return documents
    
    def _collect_weekly_documents(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Raccoglie i documenti per un periodo specifico.
        
        Args:
            start_date (datetime): Data di inizio del periodo
            end_date (datetime): Data di fine del periodo
            
        Returns:
            list: Lista di documenti
        """
        documents = []
        current_date = start_date
        
        # Raccoglie i documenti per ogni giorno nel periodo
        while current_date <= end_date:
            daily_docs = self._collect_daily_documents(current_date)
            documents.extend(daily_docs)
            current_date += timedelta(days=1)
        
        logger.info(f"Raccolti {len(documents)} documenti per il periodo {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}")
        return documents
    
    def _analyze_keyword_stats(self, documents: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Analizza le statistiche delle keyword nei documenti.
        
        Args:
            documents (list): Lista di documenti da analizzare
            
        Returns:
            dict: Dizionario con le keyword trovate e il numero di occorrenze
        """
        if not documents:
            return {}
        
        # Carica le keyword
        keywords = self._load_keywords()
        
        # Conta le occorrenze delle keyword
        keyword_counts: Dict[str, int] = {}
        
        for doc in documents:
            # Converte il documento in testo
            doc_text = json.dumps(doc, ensure_ascii=False).lower()
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                count = doc_text.count(keyword_lower)
                
                if count > 0:
                    if keyword in keyword_counts:
                        keyword_counts[keyword] += count
                    else:
                        keyword_counts[keyword] = count
        
        # Ordina le keyword per numero di occorrenze (decrescente)
        sorted_counts = {k: v for k, v in sorted(keyword_counts.items(), key=lambda item: item[1], reverse=True)}
        
        logger.info(f"Analizzate {len(keywords)} keyword in {len(documents)} documenti, trovate {len(sorted_counts)} keyword")
        return sorted_counts
    
    def _load_keywords(self) -> Set[str]:
        """
        Carica le keyword dal file.
        
        Returns:
            set: Insieme di keyword
        """
        keywords = set()
        keyword_file = self.data_dir / 'fintech_keywords.txt'
        
        try:
            with open(keyword_file, 'r', encoding='utf-8') as f:
                for line in f:
                    keyword = line.strip()
                    if keyword:
                        keywords.add(keyword)
            
            logger.info(f"Caricate {len(keywords)} keyword da {keyword_file}")
            
        except Exception as e:
            logger.error(f"Errore durante il caricamento delle keyword da {keyword_file}: {e}")
        
        return keywords
    
    def _get_keywords_in_document(self, document: Dict[str, Any], keywords: Set[str]) -> List[str]:
        """
        Trova le keyword presenti in un documento.
        
        Args:
            document (dict): Documento da analizzare
            keywords (set): Insieme di keyword da cercare
            
        Returns:
            list: Lista di keyword trovate nel documento
        """
        found_keywords = []
        doc_text = json.dumps(document, ensure_ascii=False).lower()
        
        for keyword in keywords:
            if keyword.lower() in doc_text:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _analyze_trends(self, end_date: datetime) -> Dict[str, float]:
        """
        Analizza i trend delle keyword nel tempo.
        
        Args:
            end_date (datetime): Data di fine dell'analisi
            
        Returns:
            dict: Dizionario con le keyword e il loro trend percentuale
        """
        # Periodo di analisi (ultimi N giorni)
        days = self.config['trend_analysis_days']
        start_date = end_date - timedelta(days=days)
        
        # Divide il periodo in due metà per confrontare i trend
        mid_date = start_date + timedelta(days=days//2)
        
        # Raccoglie i documenti per le due metà del periodo
        first_half_docs = self._collect_weekly_documents(start_date, mid_date)
        second_half_docs = self._collect_weekly_documents(mid_date + timedelta(days=1), end_date)
        
        # Analizza le statistiche delle keyword per le due metà
        first_half_stats = self._analyze_keyword_stats(first_half_docs)
        second_half_stats = self._analyze_keyword_stats(second_half_docs)
        
        # Calcola i trend percentuali
        trends = {}
        
        # Unisce tutte le keyword trovate
        all_keywords = set(first_half_stats.keys()) | set(second_half_stats.keys())
        
        for keyword in all_keywords:
            first_count = first_half_stats.get(keyword, 0)
            second_count = second_half_stats.get(keyword, 0)
            
            # Calcola la variazione percentuale
            if first_count > 0:
                trend = ((second_count - first_count) / first_count) * 100
            elif second_count > 0:
                trend = 100  # Se prima era 0 e ora è > 0, consideriamo un aumento del 100%
            else:
                trend = 0  # Se entrambi sono 0, non c'è trend
            
            trends[keyword] = trend
        
        # Ordina i trend per valore assoluto (decrescente)
        sorted_trends = {k: v for k, v in sorted(trends.items(), key=lambda item: abs(item[1]), reverse=True)}
        
        logger.info(f"Analizzati trend per {len(sorted_trends)} keyword")
        return sorted_trends
    
    def _generate_predictions(self, trend_data: Dict[str, float]) -> Dict[str, float]:
        """
        Genera previsioni basate sui trend.
        
        Args:
            trend_data (dict): Dizionario con le keyword e i loro trend
            
        Returns:
            dict: Dizionario con le keyword e le previsioni di occorrenza
        """
        if not trend_data:
            return {}
        
        # Raccoglie i dati storici per le previsioni
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.config['trend_analysis_days'])
        
        historical_docs = self._collect_weekly_documents(start_date, end_date)
        historical_stats = self._analyze_keyword_stats(historical_docs)
        
        # Calcola le previsioni
        predictions = {}
        
        for keyword, trend in trend_data.items():
            if keyword in historical_stats:
                # Media giornaliera attuale
                current_count = historical_stats[keyword]
                days = self.config['trend_analysis_days']
                daily_avg = current_count / days
                
                # Applica il trend per prevedere il futuro
                prediction_horizon = self.config['prediction_horizon_days']
                predicted_daily_avg = daily_avg * (1 + (trend / 100))
                predicted_total = predicted_daily_avg * prediction_horizon
                
                predictions[keyword] = max(0, predicted_total)  # Evita previsioni negative
        
        # Ordina le previsioni per valore (decrescente)
        sorted_predictions = {k: v for k, v in sorted(predictions.items(), key=lambda item: item[1], reverse=True)}
        
        logger.info(f"Generate previsioni per {len(sorted_predictions)} keyword")
        return sorted_predictions
    
    def _generate_keyword_chart(self, keyword_stats: Dict[str, int], date_str: str, report_type: str) -> str:
        """
        Genera un grafico delle keyword più frequenti.
        
        Args:
            keyword_stats (dict): Statistiche delle keyword
            date_str (str): Stringa della data per il nome del file
            report_type (str): Tipo di report ('daily' o 'weekly')
            
        Returns:
            str: Percorso del file del grafico generato
        """
        if not keyword_stats:
            return ""
        
        # Limita il numero di keyword nel grafico
        top_n = min(10, len(keyword_stats))
        top_keywords = list(keyword_stats.items())[:top_n]
        
        # Crea il grafico
        plt.figure(figsize=(12, 8))
        
        keywords = [k for k, _ in top_keywords]
        counts = [v for _, v in top_keywords]
        
        # Crea un grafico a barre orizzontale
        bars = plt.barh(keywords, counts, color='skyblue')
        
        # Aggiungi i valori alle barre
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.3, bar.get_y() + bar.get_height()/2, f'{width:.0f}', 
                    ha='left', va='center')
        
        plt.xlabel('Numero di occorrenze')
        plt.ylabel('Keyword')
        plt.title(f'Top {top_n} keyword - {date_str}')
        plt.tight_layout()
        
        # Salva il grafico
        chart_file = self.reports_dir / f"{report_type}_keyword_chart_{date_str}.png"
        plt.savefig(chart_file)
        plt.close()
        
        logger.info(f"Grafico delle keyword generato: {chart_file}")
        return str(chart_file)
    
    def _generate_trend_chart(self, trend_data: Dict[str, float], date_range: str) -> str:
        """
        Genera un grafico dei trend delle keyword.
        
        Args:
            trend_data (dict): Dati dei trend
            date_range (str): Intervallo di date per il nome del file
            
        Returns:
            str: Percorso del file del grafico generato
        """
        if not trend_data:
            return ""
        
        # Limita il numero di keyword nel grafico
        top_n = min(10, len(trend_data))
        top_trends = sorted(trend_data.items(), key=lambda x: abs(x[1]), reverse=True)[:top_n]
        
        # Crea il grafico
        plt.figure(figsize=(12, 8))
        
        keywords = [k for k, _ in top_trends]
        trends = [v for _, v in top_trends]
        
        # Crea un grafico a barre orizzontale con colori basati sul trend
        colors = ['green' if t > 0 else 'red' for t in trends]
        bars = plt.barh(keywords, trends, color=colors)
        
        # Aggiungi i valori alle barre
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', 
                    ha='left' if width >= 0 else 'right', va='center')
        
        plt.axvline(x=0, color='black', linestyle='-', alpha=0.3)
        plt.xlabel('Variazione percentuale')
        plt.ylabel('Keyword')
        plt.title(f'Trend delle keyword - {date_range}')
        plt.tight_layout()
        
        # Salva il grafico
        chart_file = self.reports_dir / f"trend_chart_{date_range}.png"
        plt.savefig(chart_file)
        plt.close()
        
        logger.info(f"Grafico dei trend generato: {chart_file}")
        return str(chart_file)
    
    def _generate_prediction_chart(self, predictions: Dict[str, float], date_range: str) -> str:
        """
        Genera un grafico delle previsioni.
        
        Args:
            predictions (dict): Dati delle previsioni
            date_range (str): Intervallo di date per il nome del file
            
        Returns:
            str: Percorso del file del grafico generato
        """
        if not predictions:
            return ""
        
        # Limita il numero di keyword nel grafico
        top_n = min(10, len(predictions))
        top_predictions = list(predictions.items())[:top_n]
        
        # Crea il grafico
        plt.figure(figsize=(12, 8))
        
        keywords = [k for k, _ in top_predictions]
        values = [v for _, v in top_predictions]
        
        # Crea un grafico a barre orizzontale
        bars = plt.barh(keywords, values, color='purple')
        
        # Aggiungi i valori alle barre
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.3, bar.get_y() + bar.get_height()/2, f'{width:.0f}', 
                    ha='left', va='center')
        
        plt.xlabel('Occorrenze previste')
        plt.ylabel('Keyword')
        plt.title(f'Previsioni per la prossima settimana - {date_range}')
        plt.tight_layout()
        
        # Salva il grafico
        chart_file = self.reports_dir / f"prediction_chart_{date_range}.png"
        plt.savefig(chart_file)
        plt.close()
        
        logger.info(f"Grafico delle previsioni generato: {chart_file}")
        return str(chart_file)
