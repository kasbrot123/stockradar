#!python3
# -*- coding: utf-8 -*-

"""
File: stockradar.py

Created by: Michael T.
Date: 2025-11-01 17:38:14



script that watches stock tickers and sends you a telegram message.
created this with gemini. thats why there is this german-english mess..



"""

import os
import numpy as np
import json
# import telegram
import yfinance as yf
import time


CONFIG_FILE = 'aktien_config.json'
CHECK_INTERVAL_SECONDS = 300 # 5 minutes 
# yahoo requests should be below 2000 a day
# gemini suggests 3-5 seconds per request but i doubt it


# Füge oben im Skript diese Konstanten hinzu:
TELEGRAM_TOKEN = "DEIN_BOT_TOKEN_HIER"
TELEGRAM_CHAT_ID = "DEINE_CHAT_ID_HIER"



def lade_konfiguration():
    """Lädt die Aktienliste und Schwellenwerte aus der JSON-Datei."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Filtert nur aktive Aktien heraus
            return [aktie for aktie in data.get('Aktien', []) if aktie.get('Aktiv', False)]
    except FileNotFoundError:
        print(f"Fehler: Konfigurationsdatei '{CONFIG_FILE}' nicht gefunden.")
        return []
    except json.JSONDecodeError:
        print(f"Fehler: Konfigurationsdatei '{CONFIG_FILE}' ist keine gültige JSON-Datei.")
        return []

def deactivate(index):
    print('deactivate ticker index {} ->'.format(index))
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(data['Aktien'][index]['name'])
        data['Aktien'][index]['Aktiv'] = False

        with open(CONFIG_FILE, 'w') as file:
            json.dump(data, file, indent=4)

    except FileNotFoundError:
        print(f"Fehler: Konfigurationsdatei '{CONFIG_FILE}' nicht gefunden.")
        return []
    except json.JSONDecodeError:
        print(f"Fehler: Konfigurationsdatei '{CONFIG_FILE}' ist keine gültige JSON-Datei.")
        return []


def send_telegram(nachricht, local=True):
    if local:
        if not os.system('telegram-send "{}"'.format(nachricht)):
            print('error with telegram')
            # should log this somewhere
    else:
        try:
            bot = telegram.Bot(token=TELEGRAM_TOKEN)
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=nachricht)
        except Exception as e:
            print(f"FEHLER beim Senden der Telegram-Nachricht: {e}")


def send_alarm(text):
    print(text)
    send_telegram(text)


def pruefe_aktien(aktien_liste):

    if not aktien_liste:
        print("Keine aktiven Aktien in der Konfiguration gefunden. Warte...")
        return


    ticker_symbole = [aktie['Ticker'] for aktie in aktien_liste]
    print(f"\nPrüfe {len(ticker_symbole)} Aktien: {', '.join(ticker_symbole)}...")


    aktuelle_preise = {}
    for ticker in ticker_symbole:
         try:
            info = yf.Ticker(ticker).info
            preis = info.get('regularMarketPrice')
            währung = info.get('currency')

            if preis:
                aktuelle_preise[ticker] = {'Preis': preis, 'Währung': währung}
            else:
                print(f"Warnung: Konnte aktuellen Preis für {ticker} nicht abrufen.")
         except Exception as e:
            aktuelle_preise[ticker] = {'Preis': np.nan, 'Währung': 'NaN'}
            print(f"Fehler beim Abrufen von {ticker} (Info): {e}")


    stock_history = yf.download(ticker_symbole, period="7d", interval="1d", progress=False, auto_adjust=True)

    highest_price = stock_history['High'].max()
    lowest_price = stock_history['Low'].min()



    # for aktie in aktien_liste:
    for index in range(len(aktien_liste)):

        aktie = aktien_liste[index]
        ticker = aktie['Ticker']
        name = aktie['Name']

        if ticker not in aktuelle_preise:
            continue

        aktueller_preis = aktuelle_preise[ticker]['Preis']
        währung = aktuelle_preise[ticker]['Währung']

        # defined limits absolute
        ziel_hoch = aktie.get('Ziel_Preis_Hoch')
        ziel_tief = aktie.get('Ziel_Preis_Tief')

        # defined limits relative
        prozent_plus = aktie.get('Prozent_Woche_Steigt')
        prozent_minus = aktie.get('Prozent_Woche_Faellt')


        if ziel_hoch is not None and aktueller_preis >= ziel_hoch:
            send_alarm(f'The stock {name} ({ticker}) is above your limit: {ziel_hoch} {währung}. Current price: {aktueller_preis} {währung}.')
            deactivate(index)

        if ziel_tief is not None and aktueller_preis <= ziel_tief:
            send_alarm(f'The stock {name} ({ticker}) is below your limit: {ziel_tief} {währung}. Current price: {aktueller_preis} {währung}.')
            deactivate(index)

        if prozent_plus is not None and prozent_plus < (aktueller_preis/lowest_price[ticker]-1)*100:
            send_alarm(f'The stock {name} ({ticker}) is up more than +{prozent_plus}%. Current price: {aktueller_preis} {währung}.')
            deactivate(index)

        if prozent_minus is not None and prozent_minus < (1 - aktueller_preis/highest_price[ticker])*100:
            send_alarm(f'The stock {name} ({ticker}) is down more than -{prozent_minus}%. Current price: {aktueller_preis} {währung}.')
            deactivate(index)


if __name__ == "__main__":

    while True:
        aktive_aktien = lade_konfiguration()
        pruefe_aktien(aktive_aktien)
        print('finish')
        # break

        time.sleep(CHECK_INTERVAL_SECONDS)

