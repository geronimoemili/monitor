# Todo List per il Sistema di Monitoraggio OpenData del Parlamento Europeo

## Struttura del Progetto
- [x] Creare la directory principale del progetto
- [x] Definire la struttura delle sottocartelle per i vari moduli
- [x] Creare file README.md con descrizione del progetto

## Modulo di Recupero Dati
- [x] Ricercare le API OpenData disponibili del Parlamento Europeo
- [x] Implementare il modulo di connessione alle API
- [x] Creare funzioni per il recupero periodico dei dati
- [x] Implementare gestione degli errori e tentativi di riconnessione

## Modulo di Analisi Keyword
- [x] Creare file di esempio con keyword relative al fintech
- [x] Implementare funzioni per il caricamento delle keyword da file
- [x] Sviluppare algoritmo di ricerca delle keyword nei documenti
- [x] Ottimizzare le performance di ricerca per grandi volumi di dati

## Sistema di Notifica Email
- [x] Implementare modulo per l'invio di email
- [x] Creare template per le email di notifica
- [x] Configurare l'invio a geronimo.emili@gmail.com
- [x] Implementare gestione degli errori nell'invio

## Reportistica
- [x] Sviluppare funzioni per la generazione di report giornalieri
- [x] Implementare la logica per i report settimanali predittivi
- [x] Creare template per i report in formato testo
- [x] Implementare l'analisi dei trend e previsioni

## Sistema di Configurazione
- [x] Creare file di configurazione (config.json)
- [x] Implementare funzioni per la lettura della configurazione
- [x] Rendere parametrizzabili orari, fonti e altri parametri

## Persistenza Dati
- [x] Definire la struttura dei file CSV per il salvataggio dei dati
- [x] Implementare funzioni per la lettura/scrittura dei dati
- [x] Ottimizzare la gestione della persistenza per grandi volumi

## Scheduler
- [x] Implementare lo scheduler per l'esecuzione periodica
- [x] Configurare job orari per il recupero dati
- [x] Configurare job giornalieri per i report (18:00)
- [x] Configurare job settimanali per l'analisi predittiva

## Testing
- [x] Creare test unitari per i vari moduli
- [x] Implementare test di integrazione
- [x] Verificare la scalabilità del sistema

## Documentazione
- [x] Documentare l'architettura del sistema
- [x] Creare documentazione per l'utilizzo e la configurazione
- [x] Preparare esempi di utilizzo
