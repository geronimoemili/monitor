# Documentazione del Sistema di Monitoraggio OpenData del Parlamento Europeo per il Fintech

## Architettura del Sistema

Il sistema di monitoraggio OpenData del Parlamento Europeo per il settore fintech è un'applicazione modulare sviluppata in Python che permette di recuperare, analizzare e monitorare documenti del Parlamento Europeo relativi al settore fintech. Il sistema è progettato per essere scalabile, configurabile e facilmente estendibile.

### Struttura dei Moduli

Il sistema è composto dai seguenti moduli principali:

1. **Modulo di Recupero Dati** (`data_fetcher`)
   - Si connette alle API OpenData del Parlamento Europeo
   - Recupera i documenti delle sessioni plenarie
   - Salva i dati in formato CSV

2. **Modulo di Analisi Keyword** (`keyword_analyzer`)
   - Carica le keyword relative al fintech da file
   - Analizza i documenti per trovare corrispondenze con le keyword
   - Fornisce statistiche sulle keyword trovate

3. **Sistema di Notifica Email** (`email_notifier`)
   - Gestisce l'invio di email di notifica
   - Supporta la configurazione di destinatari multipli
   - Crea template per le email di notifica

4. **Modulo di Reportistica** (`reporting`)
   - Genera report giornalieri alle 18:00
   - Crea report settimanali predittivi
   - Implementa analisi dei trend e previsioni

5. **Sistema di Configurazione** (`config`)
   - Gestisce la configurazione del sistema
   - Permette di personalizzare parametri come orari, fonti e keyword
   - Supporta la scalabilità del sistema

6. **Scheduler** (`utils`)
   - Gestisce l'esecuzione periodica delle varie funzionalità
   - Configura job orari per il recupero dati
   - Pianifica job giornalieri per i report e job settimanali per l'analisi predittiva

### Diagramma di Flusso

```
+----------------+     +------------------+     +------------------+
| Data Fetcher   |---->| Keyword Analyzer |---->| Email Notifier   |
+----------------+     +------------------+     +------------------+
        |                      |                        |
        v                      v                        v
+----------------+     +------------------+     +------------------+
| CSV Storage    |     | Report Generator |     | Scheduler        |
+----------------+     +------------------+     +------------------+
                              |
                              v
                      +------------------+
                      | Config Manager   |
                      +------------------+
```

## Installazione e Configurazione

### Requisiti di Sistema

- Python 3.6 o superiore
- Librerie Python: requests, pandas, matplotlib, schedule

### Installazione

1. Clonare il repository:
   ```
   git clone https://github.com/tuorepository/eu_parliament_fintech_monitor.git
   cd eu_parliament_fintech_monitor
   ```

2. Installare le dipendenze:
   ```
   pip install -r requirements.txt
   ```

### Configurazione

Il sistema utilizza un file di configurazione JSON per personalizzare i vari parametri. Il file di configurazione predefinito si trova in `config/config.json`.

Principali parametri configurabili:

- **API del Parlamento Europeo**:
  ```json
  "data_fetcher": {
    "api_base_url": "https://data.europarl.europa.eu/api/v2",
    "plenary_endpoint": "/plenary-documents",
    "fetch_interval_hours": 1
  }
  ```

- **Analisi delle Keyword**:
  ```json
  "keyword_analyzer": {
    "keyword_file": "fintech_keywords.txt",
    "case_sensitive": false,
    "match_whole_word": false
  }
  ```

- **Notifiche Email**:
  ```json
  "email_notifier": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "noreply@example.com",
    "recipients_file": "email_recipients.txt"
  }
  ```

- **Reportistica**:
  ```json
  "reporting": {
    "daily_report_time": "18:00",
    "weekly_report_day": 6,
    "report_format": "txt"
  }
  ```

- **Scheduler**:
  ```json
  "scheduler": {
    "data_fetch_cron": "0 * * * *",
    "daily_report_cron": "0 18 * * *",
    "weekly_report_cron": "0 12 * * 0"
  }
  ```

## Utilizzo

### Avvio del Sistema

Per avviare il sistema, eseguire lo script principale:

```
python main.py
```

### Personalizzazione delle Keyword

Le keyword relative al fintech sono definite nel file `data/fintech_keywords.txt`. È possibile modificare questo file per aggiungere o rimuovere keyword.

Formato del file:
```
fintech
blockchain
cryptocurrency
bitcoin
ethereum
...
```

### Configurazione dei Destinatari Email

I destinatari delle email di notifica sono definiti nel file `data/email_recipients.txt`. È possibile modificare questo file per aggiungere o rimuovere destinatari.

Formato del file:
```
geronimo.emili@gmail.com
altro.destinatario@example.com
...
```

### Esecuzione dei Test

Per eseguire i test unitari e di integrazione:

```
python -m unittest discover tests
```

## Funzionalità Principali

### Recupero Dati dal Parlamento Europeo

Il sistema si connette alle API OpenData del Parlamento Europeo per recuperare i documenti delle sessioni plenarie. I documenti vengono salvati in formato CSV nella directory `data`.

### Analisi delle Keyword

Il sistema analizza i documenti recuperati per trovare corrispondenze con le keyword relative al fintech. Le keyword sono definite nel file `data/fintech_keywords.txt`.

### Notifiche Email

Quando vengono trovati documenti che contengono keyword relative al fintech, il sistema invia una notifica email ai destinatari configurati. Le notifiche includono i dettagli dei documenti trovati e le statistiche delle keyword.

### Report Giornalieri

Il sistema genera report giornalieri alle 18:00 con tutte le keyword trovate e i documenti associati. I report vengono salvati nella directory `reports` e inviati via email.

### Report Settimanali Predittivi

Il sistema genera report settimanali predittivi con analisi dei trend e previsioni. I report includono grafici e suggerimenti basati sui dati raccolti.

## Estensione e Personalizzazione

### Aggiunta di Nuove Fonti di Dati

Per aggiungere nuove fonti di dati, è possibile estendere il modulo `data_fetcher` creando nuove classi che implementano l'interfaccia di recupero dati.

### Personalizzazione dei Report

I template dei report possono essere personalizzati modificando le funzioni di generazione dei report nel modulo `reporting`.

### Integrazione con Altri Sistemi

Il sistema può essere integrato con altri sistemi attraverso l'API di configurazione e l'interfaccia modulare.

## Risoluzione dei Problemi

### Errori di Connessione alle API

Se si verificano errori di connessione alle API del Parlamento Europeo, verificare:
- La connessione internet
- La configurazione dell'URL dell'API
- Eventuali limitazioni di accesso o modifiche nelle API

### Problemi con l'Invio delle Email

Se si verificano problemi con l'invio delle email, verificare:
- La configurazione del server SMTP
- Le credenziali di accesso
- Le impostazioni di sicurezza del server di posta

## Contatti e Supporto

Per assistenza o segnalazioni di bug, contattare:
- Email: geronimo.emili@gmail.com
- GitHub: https://github.com/tuorepository/eu_parliament_fintech_monitor
