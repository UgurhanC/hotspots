# Technisch ontwerp

## Controllers
### Routes:
- Login (inloggen met verplicht invullen gebruikersnaam en wachtwoord)
    - @app.route("/login")
    - met scherm
    - GET & POST
    - functie:
        - gebruikersnaam/ mail en wachtwoord checken in database
        - checken of alle velden ingevuld zijn
        - session id opslaan
        - doorsturen naar index

- Register (registeren met herhalen wachtwoord en direct naar de homepage)
    - @app.route("/register")
    - met scherm
    - GET & POST
    - functie:
        - checken of alle velden (naam, gebruikersnaam, wachtwoord, wachtwoordherhaling, E-mail) ingevuld zijn
        - checken of gebruikersnaam nog niet bestaat
        - checken of wachtwoorden overeenkomen
        - checken of E-mail geldig is
        - alle informatie opslaan in database
        - session id opslaan
        - doorsturen naar index

- Logout (uitloggen en terug naar login)
    - @app.route("/logout")
    - geen scherm
    - functie:
        - clear de session
        - doorsturen naar login

- Index (tijdlijn met steden die je volgt)
    - @app.route("/index")
    - met scherm
    - GET & POST
    - functie:
        - check welke locaties deze persoon volgt
        - laadt foto's van deze locatie naar tijdlijn

- Profile (foto's zichtbaar die jezelf geupload heb)
    - @app.route("/profile")
    - met scherm
    - GET & POST
    - functie:
        - check welke foto's deze persoon heeft geupload

- Browse (zoeken naar steden met als resultaat foto's van die stad)
    - @app.route("/browse")
    - geen scherm
    - POST
    - functie:
        - open een bar voor zoekopdracht
        - checken of de ingevulde stad in de database staat
        - redirect naar resultspagina

- Results (resultaten van browse functie)
    - @app.route("/results")
    - met scherm
    - GET & POST
    - functie:
        - laadt de foto's van de ingevulde stad

- Settings (instellingen om wachtwoord en gebruikersnaam te veranderen)
    - @app.route("/settings")
    - met scherm
    - GET & POST
    - functie:
        - laadt de functies changeww, changegb, forget zien

- Changeww (veranderen wachtwoord)
    - @app.route("/changeww")
    - geen scherm
    - GET & POST
    - functie:
        - check of oude wachtwoord klopt
        - check of er een nieuw wachtwoord ingevuld is
        - check of herhaling nieuwe wachtwoord hetzelfde is als nieuwe wachtwoord
        - update database met nieuw wachtwoord
        - redirect naar index of pop up

- Changegb (veranderen gebruikersnaam)
    - @app.route("/changegb")
    - geen scherm
    - GET & POST
    - functie:
        - check of oude gebruikersnaam klopt
        - check of er een nieuwe gebruikersnaam ingevuld is
        - check of nieuwe gebruikersnaam nog niet bestaat in database
        - update database met nieuwe gebruikersnaam
        - redirect naar index of pop up
        -
- Forget (wachtwoord opvragen wanneer vergeten)
    - @app.route("/fotget")
    - geen scherm
    - GET & POST
    - functie:
        - geef E-mail
        - check E-mail bestaat in de database
        - mail een random ww voor nieuwe inlog
        - random ww opslaan in de database opslaan

- Upload (nieuwe fotos uploaden)
    - @app.route("/upload")
    - met scherm
    - GET & POST
    - funcite:
        - foto selecteren
        - locatie checken van de foto
        - vraag om coördinaten van de foto (wellicht redirect naar google)
        - check of de coördinaten kloppen
        - plaats foto in de database

- Follow (functie om steden te volgen, zodat deze in je tijdlijn verschijnen)
    - @app.route("/follow")
    - geen scherm
    - functie:
        - plaats in database: session_id, tag

- Location (opvragen precieze locatie van een foto)
    - @app.route("/location")
    - geen scherm
    - functie:
        - gekoppelde locatie van foto opzoeken
        - return naar lookup

- Lookup (pop-up google maps met de locatie van de hotspot)
    - javascript realtime
    - functie:
        - laat de precieze locatie van een foto op google maps zien

- Like (likes van een foto bijhouden in een database)
    - in helpers.py
    - geen scherm
    - functie:
        - check of de foto al geliked is
        - als foto al geliked is unlike de foto bij klikken
        - als foto nog niet geliked is like de foto bij klikken
        - sla likes van foto op in de database

- Nearby (foto's te zien krijgen die in jouw buurt zijn gemaakt)
    - @app.route("/nearby")
    - met scherm
    - GET
    - functie:
        - check gps locatie
        - check in database dichtbijzijnde locaties
        - laadt de foto's van dichtbijzijnde locaties

- React (reageren op foto's met gif)
    - @app.route("/react")
    - geen eigen scherm, maar naar gif
    - GET & POST
    - functie:
        - ?

## Views

![alt text](schetsen/register.jpeg "Register")
![alt text](schetsen/login.jpeg "Login")
![alt text](schetsen/index.jpeg "Index")
![alt text](schetsen/profile.jpeg "Profile")
![alt text](schetsen/hotspot.jpeg "Hotspots")
![alt text](schetsen//maps.jpeg "Map")
![alt text](schetsen/settings.jpeg "Settings")

## Helpers
- Apology (returned een error 400 als iemand een gebruikersfout maakt)
- Lookup (pop-up google maps met de locatie van de hotspot)
    - javascript realtime
- Like (likes van een foto bijhouden in een database)
- Follow (functie om steden te volgen, zodat deze in je tijdlijn verschijnen)
    - @app.route("/follow")
    - geen scherm

## Plugins & frameworks
- Google Maps
    - https://www.google.com/maps
- Bootstrap
    - https://getbootstrap.com/docs/4.1/layout/overview/
-  Giphy
    - https://giphy.com/

