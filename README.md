# Stock Radar

This python script allows to track multiple stock tickers and send you a telegram notification when a price hits a certain limit.

The possible limits which can be set are:

- Current Price `>` Limit
- Current Price `<` Limit
- (Current Price / lowest_price_last_7_days - 1) `>` Limit
- (1 - Current Price / highest_price_last_7_days) `>` Limit


## Json File

In the json file the limit values are defined:

```
{
    "Aktien": [
        {
            "Ticker": "GC=F",
            "Name": "Gold",
            "Ziel_Preis_Hoch": 4500.0,
            "Ziel_Preis_Tief": 3500.0,
            "Prozent_Woche_Steigt": 5.0,
            "Prozent_Woche_Faellt": 5.0,
            "Aktiv": true
        },
        {
            "Ticker": "NVDA",
            "Name": "Nvidia",
            "Ziel_Preis_Hoch": 213.0,
            "Ziel_Preis_Tief": null,
            "Prozent_Woche_Steigt": 15,
            "Prozent_Woche_Faellt": 15,
            "Aktiv": true
        },
        {
            "Ticker": "GOOGL",
            "Name": "Google",
            "Ziel_Preis_Hoch": null,
            "Ziel_Preis_Tief": null,
            "Prozent_Woche_Steigt": null,
            "Prozent_Woche_Faellt": 15,
            "Aktiv": true
        }

        ...

    ]
}

```


## Disclaimer

Sorry for the german-english mix. Copy-pasted from AI and was to lazy to rename all. Might do it later.


