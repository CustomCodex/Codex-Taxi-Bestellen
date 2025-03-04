# Discord Taxi Bot 🚕💨 (Nederlands)

[![Discord](https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com)

![Discord Taxi Bot in actie in een Discord kanaal](https://i.imgur.com/JV9cDkX.png)

## Beschrijving

Deze Discord bot is ontworpen om taxi bestellingen te vereenvoudigen en te organiseren binnen je Discord server. Gebruikers kunnen eenvoudig taxi's aanvragen, taxi chauffeurs kunnen bestellingen accepteren en prijzen opgeven, en server beheerders hebben tools om de bestellingen effectief te beheren.

## Functies

*   **Taxi Bestellen:** Gebruikers kunnen met het commando `/taxi-bestellen` een taxi aanvragen via een eenvoudig modal formulier, waarin ze de ophaallocatie en eventuele notities kunnen specificeren.
*   **Taxi Acceptatie & Prijsopgave:** Taxi chauffeurs (met de juiste rol) kunnen nieuwe bestellingen in een speciaal kanaal zien en accepteren. Bij acceptatie kunnen ze direct een prijs opgeven voor de rit, die vervolgens naar de aanvrager wordt gecommuniceerd.
*   **Beschikbaarheidsbeheer voor Chauffeurs:** Taxi chauffeurs kunnen het commando `/taxi-status` gebruiken om hun beschikbaarheidsstatus in te stellen op "Beschikbaar" of "Niet Beschikbaar".
*   **Automatische Timeout:** Taxi bestellingen die niet binnen een bepaalde tijd worden geaccepteerd, worden automatisch geannuleerd (timeout).
*   **Annulering door Aanvrager:** Gebruikers kunnen hun eigen taxi bestellingen annuleren.
*   **Log Kanalen:** Alle belangrijke acties (bestellingen, acceptaties, annuleringen, timeouts, statuswijzigingen, admin acties) worden gelogd in een configureerbaar log kanaal voor beheer en overzicht.
*   **Admin Commando voor Bestellingenbeheer:** Server administrators kunnen het commando `/taxi-requests-clear` gebruiken om alle actieve taxi bestellingen in één keer te verwijderen.

## Setup en Installatie

Volg deze stappen om de Discord Taxi Bot op je server te installeren en te laten draaien:

### Vereisten

1.  **Python 3.8 of hoger:** Zorg ervoor dat Python op je systeem is geïnstalleerd. Je kunt Python downloaden van [python.org](https://www.python.org/).
2.  **Discord Bot Account:** Je hebt een Discord bot account nodig. Maak er een aan via de [Discord Developer Portal](https://discord.com/developers/applications).
    *   Ga naar "Applications" en klik op "Create Application".
    *   Geef je bot een naam.
    *   Ga naar het "Bot" tabblad en klik op "Add Bot".
    *   **Schakel "Message Content Intent" in** onder "Privileged Gateway Intents" (belangrijk voor het lezen van berichtinhoud).
    *   Kopieer de **Bot Token** (bewaar deze veilig!).
3.  **Nodig de Bot uit op je Server:** Gebruik de OAuth2 URL Generator in de Discord Developer Portal (onder "OAuth2" -> "URL Generator") om de bot naar je server uit te nodigen. Selecteer de `bot` scope en de `application.commands` permissie, en kies de server waaraan je de bot wilt toevoegen.

### Installatie Stappen

1.  **Clone de Repository:** Clone deze GitHub repository naar je lokale machine met:
    ```bash
    git clone [REPOSITORY_URL]
    cd [REPOSITORY_DIRECTORY]
    ```
    Vervang `[REPOSITORY_URL]` met de URL van deze repository en `[REPOSITORY_DIRECTORY]` met de mapnaam waar je de repository wilt klonen.

2.  **Installeer Vereiste Python Pakketten:** Installeer de benodigde Python libraries met pip:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configureer Omgevingsvariabelen:**
    *   Maak een bestand aan met de naam `.env` in dezelfde directory als `codex-taxi-bot.py`.
    *   Voeg de volgende omgevingsvariabelen toe aan `.env` en vul de juiste waarden in:

    ```env
    DISCORD_BOT_TOKEN="YOUR_DISCORD_BOT_TOKEN"
    TAXI_DRIVER_ROLE_ID="YOUR_TAXI_DRIVER_ROLE_ID"
    TAXI_REQUEST_CHANNEL_ID="YOUR_TAXI_REQUEST_CHANNEL_ID"
    LOG_CHANNEL_ID="YOUR_LOG_CHANNEL_ID" # Optioneel, laat leeg als je geen log kanaal wilt
    REQUEST_TIMEOUT_SECONDS=300 # Optioneel, timeout in seconden voor taxi bestellingen (standaard 300 seconden = 5 minuten)
    ```

    Vervang de placeholders met de volgende waarden:

    *   `YOUR_DISCORD_BOT_TOKEN`: De **Bot Token** die je hebt gekopieerd van de Discord Developer Portal.
    *   `YOUR_TAXI_DRIVER_ROLE_ID`: De **ID van de Discord rol** die je wilt toewijzen aan taxi chauffeurs op je server. Om de rol ID te vinden, schakel Discord Developer Mode in (Gebruikersinstellingen -> Geavanceerd) en rechtsklik op de taxi chauffeur rol -> "ID kopiëren".
    *   `YOUR_TAXI_REQUEST_CHANNEL_ID`: De **ID van het Discord kanaal** waar gebruikers taxi bestellingen kunnen plaatsen en waar taxi chauffeurs de bestellingen zien. Rechtsklik op het kanaal -> "ID kopiëren".
    *   `YOUR_LOG_CHANNEL_ID`: (Optioneel) De **ID van het Discord kanaal** waar de bot logberichten naartoe moet sturen. Indien leeg gelaten, wordt logging naar een Discord kanaal uitgeschakeld. Rechtsklik op het kanaal -> "ID kopiëren".
    *   `REQUEST_TIMEOUT_SECONDS`: (Optioneel) De tijd in seconden waarna een taxi bestelling automatisch wordt geannuleerd als deze niet is geaccepteerd. De standaardwaarde is 300 seconden (5 minuten). Je kunt dit aanpassen in `.env` of weglaten om de standaard te gebruiken.

4.  **Start de Bot:** Voer het bot script uit met Python:
    ```bash
    python codex-taxi-bot.py
    ```
    Als alles correct is geconfigureerd, zou de bot online moeten komen en een bericht in de console printen zoals "Ingelogd als [Bot Naam] ([Bot ID])" en "Gesynced [Aantal] commando('s')".

## Gebruik

Zodra de bot online is, kunnen gebruikers en taxi chauffeurs de volgende commando's gebruiken:

### Commando's voor Iedereen

*   **`/taxi-bestellen`**:
    *   **Beschrijving:** Opent een modal om een taxi te bestellen.
    *   **Gebruik:** Typ `/taxi-bestellen` in een Discord kanaal en vul de locatie en notities in het modal formulier.

### Commando's voor Taxi Chauffeurs (met de Taxi Chauffeur rol)

*   **`/taxi-status`**:
    *   **Beschrijving:** Stel je beschikbaarheid in als taxi chauffeur (Beschikbaar/Niet Beschikbaar).
    *   **Gebruik:** Typ `/taxi-status` en kies "Beschikbaar" of "Niet Beschikbaar" in het keuzemenu.

### Commando's voor Server Administrators

*   **`/taxi-requests-clear`**:
    *   **Beschrijving:** Verwijder alle actieve taxi bestellingen.
    *   **Gebruik:** Typ `/taxi-requests-clear` om alle openstaande taxi bestellingen te verwijderen.

## Configuratie (.env variabelen) in Detail

*   **`DISCORD_BOT_TOKEN`**: **Verplicht**. De unieke token van je Discord bot account. Dit is essentieel om de bot met Discord te verbinden.
*   **`TAXI_DRIVER_ROLE_ID`**: **Verplicht**. De ID van de Discord rol die identificeert wie taxi chauffeurs zijn. Alleen gebruikers met deze rol kunnen bestellingen accepteren en hun status wijzigen.
*   **`TAXI_REQUEST_CHANNEL_ID`**: **Verplicht**. De ID van het Discord kanaal waar taxi bestellingen worden geplaatst en weergegeven.
*   **`LOG_CHANNEL_ID`**: **Optioneel**. De ID van het Discord kanaal waar de bot logberichten naartoe stuurt. Indien niet ingesteld, wordt logging naar een Discord kanaal uitgeschakeld.
*   **`REQUEST_TIMEOUT_SECONDS`**: **Optioneel**. De timeout in seconden voor taxi bestellingen. Standaard is 300 seconden (5 minuten). Pas aan naar wens.

## Logging

De bot biedt uitgebreide logging functionaliteit. Indien `LOG_CHANNEL_ID` is geconfigureerd, worden de volgende gebeurtenissen gelogd in het opgegeven log kanaal:

*   **Nieuwe Taxi Bestellingen**: Wanneer een gebruiker een taxi bestelling plaatst.
*   **Taxi Bestellingen Geaccepteerd**: Wanneer een taxi chauffeur een bestelling accepteert, inclusief de opgegeven prijs.
*   **Taxi Bestellingen Geannuleerd (door aanvrager)**: Wanneer een gebruiker zijn eigen bestelling annuleert.
*   **Taxi Bestellingen Timeout**: Wanneer een bestelling automatisch wordt geannuleerd wegens timeout.
*   **Status Updates van Chauffeurs**: Wanneer een taxi chauffeur zijn beschikbaarheidsstatus wijzigt.
*   **Admin Acties (Bestellingen Opkuisen)**: Wanneer een administrator alle actieve bestellingen verwijdert.
*   **Errors**: Fouten die optreden in de bot (bijvoorbeeld in modals of commando's).
*   **Command Sync Errors**: Fouten tijdens het synchroniseren van slash commando's bij het opstarten van de bot.

De logs bevatten details zoals gebruikersnamen, locaties, notities, prijzen, timestamps en error details, en zijn voorzien van emojis voor betere visuele herkenbaarheid.

## Bijdragen

Bijdragen aan dit project zijn welkom! Als je bug fixes, verbeteringen of nieuwe features wilt toevoegen, maak dan een pull request.

## Licentie

Dit project is gelicenseerd onder de [MIT License](LICENSE) (indien van toepassing, voeg een LICENSE bestand toe).

## Support / Contact

Voor vragen of support, open een issue in deze GitHub repository.

---

**Veel plezier met je Discord Taxi Bot! 🚕💨**