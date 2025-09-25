#!/bin/bash

# Script to download images for players with transfer fees above 10.0m
# Creates team-season directories and downloads player images using the download_web_image.py script

cd "$(dirname "$0")"

declare -a players=(
    # AS Monaco 2017-18
    "As_Monca:2017-18:Keita Baldé"
    "As_Monca:2017-18:Youri Tielemans"
    "As_Monca:2017-18:Pietro Pellegri"
    "As_Monca:2017-18:Terence Kongolo"
    "As_Monca:2017-18:Stevan Jovetić"
    
    # Atletico Madrid 2014-15
    "Atletico_Madrid:2014-15:Antoine Griezmann"
    "Atletico_Madrid:2014-15:Mario Mandžukić"
    "Atletico_Madrid:2014-15:Jan Oblak"
    "Atletico_Madrid:2014-15:Alessio Cerci"
    "Atletico_Madrid:2014-15:Raúl Jiménez"
    "Atletico_Madrid:2014-15:Ángel Correa"
    
    # Chelsea FC 2017-18
    "Chelsea_Fc:2017-18:Álvaro Morata"
    "Chelsea_Fc:2017-18:Tiemoué Bakayoko"
    "Chelsea_Fc:2017-18:Danny Drinkwater"
    "Chelsea_Fc:2017-18:Antonio Rüdiger"
    "Chelsea_Fc:2017-18:Davide Zappacosta"
    "Chelsea_Fc:2017-18:Emerson"
    "Chelsea_Fc:2017-18:Olivier Giroud"
    "Chelsea_Fc:2017-18:Ross Barkley"
    
    # Chelsea FC 2022-23
    "Chelsea_Fc:2022-23:Enzo Fernández"
    "Chelsea_Fc:2022-23:Wesley Fofana"
    "Chelsea_Fc:2022-23:Mykhaylo Mudryk"
    "Chelsea_Fc:2022-23:Marc Cucurella"
    "Chelsea_Fc:2022-23:Raheem Sterling"
    "Chelsea_Fc:2022-23:Kalidou Koulibaly"
    "Chelsea_Fc:2022-23:Benoît Badiashile"
    "Chelsea_Fc:2022-23:Noni Madueke"
    "Chelsea_Fc:2022-23:Malo Gusto"
    "Chelsea_Fc:2022-23:Carney Chukwuemeka"
    "Chelsea_Fc:2022-23:Cesare Casadei"
    "Chelsea_Fc:2022-23:Andrey Santos"
    "Chelsea_Fc:2022-23:Pierre-Emerick Aubameyang"
    "Chelsea_Fc:2022-23:David Datro Fofana"
    "Chelsea_Fc:2022-23:João Félix"
    
    # FC Barcelona 2017-18
    "Fc_Barcelona:2017-18:Philippe Coutinho"
    "Fc_Barcelona:2017-18:Ousmane Dembélé"
    "Fc_Barcelona:2017-18:Paulinho"
    "Fc_Barcelona:2017-18:Nélson Semedo"
    "Fc_Barcelona:2017-18:Yerry Mina"
    "Fc_Barcelona:2017-18:Gerard Deulofeu"
    
    # FC Barcelona 2019-20
    "Fc_Barcelona:2019-20:Antoine Griezmann"
    "Fc_Barcelona:2019-20:Frenkie de Jong"
    "Fc_Barcelona:2019-20:Neto"
    "Fc_Barcelona:2019-20:Pedri"
    "Fc_Barcelona:2019-20:Junior Firpo"
    "Fc_Barcelona:2019-20:Martin Braithwaite"
    
    # Juventus FC 2018-19
    "Juventus_Fc:2018-19:Cristiano Ronaldo"
    "Juventus_Fc:2018-19:João Cancelo"
    "Juventus_Fc:2018-19:Douglas Costa"
    "Juventus_Fc:2018-19:Leonardo Bonucci"
    "Juventus_Fc:2018-19:Mattia Perin"
    
    # Liverpool FC 2025-26
    "Liverpool_Fc:2025-26:Florian Wirtz"
    "Liverpool_Fc:2025-26:Hugo Ekitiké"
    "Liverpool_Fc:2025-26:Milos Kerkez"
    "Liverpool_Fc:2025-26:Jeremie Frimpong"
    
    # Manchester City 2023-24
    "Manchester_City:2023-24:Josko Gvardiol"
    "Manchester_City:2023-24:Matheus Nunes"
    "Manchester_City:2023-24:Jérémy Doku"
    "Manchester_City:2023-24:Mateo Kovacic"
    "Manchester_City:2023-24:Claudio Echeverri"
    
    # Paris Saint Germain 2023-24
    "Paris_Saint_Germain:2023-24:Randal Kolo Muani"
    "Paris_Saint_Germain:2023-24:Gonçalo Ramos"
    "Paris_Saint_Germain:2023-24:Manuel Ugarte"
    "Paris_Saint_Germain:2023-24:Ousmane Dembélé"
    "Paris_Saint_Germain:2023-24:Lucas Hernández"
    "Paris_Saint_Germain:2023-24:Bradley Barcola"
    "Paris_Saint_Germain:2023-24:Hugo Ekitiké"
    "Paris_Saint_Germain:2023-24:Kang-in Lee"
    "Paris_Saint_Germain:2023-24:Lucas Beraldo"
    "Paris_Saint_Germain:2023-24:Gabriel Moscardo"
    
    # Real Madrid 2009-10
    "Real_Madrid:2009-10:Cristiano Ronaldo"
    "Real_Madrid:2009-10:Kaká"
    "Real_Madrid:2009-10:Karim Benzema"
    "Real_Madrid:2009-10:Xabi Alonso"
    "Real_Madrid:2009-10:Raúl Albiol"
    
    # Real Madrid 2018-19
    "Real_Madrid:2018-19:Vinicius Junior"
    "Real_Madrid:2018-19:Thibaut Courtois"
    "Real_Madrid:2018-19:Álvaro Odriozola"
    "Real_Madrid:2018-19:Mariano Díaz"
    "Real_Madrid:2018-19:Brahim Díaz"
)

echo "Starting image download process..."
echo "Total players to process: ${#players[@]}"
echo "========================================="

for player_data in "${players[@]}"; do
    # Split the player data by colon
    IFS=':' read -r team season player_name <<< "$player_data"
    
    echo
    echo "Processing: $team $season - $player_name"
    
    # Create directory structure
    team_season_dir="../images/${team}_${season}"
    mkdir -p "$team_season_dir"
    
    # Create search query combining season, team, and player name
    search_query="$player_name $team $season"
    
    # Call the download script
    python3 download_web_image.py "$search_query" --output-dir "$team_season_dir" --filename "${player_name// /_}.jpg"
    
    # Check if download was successful
    if [ $? -eq 0 ]; then
        echo "✓ Successfully downloaded image for $player_name"
    else
        echo "✗ Failed to download image for $player_name"
    fi
    
    echo "----------------------------------------"
done

echo
echo "Image download process completed!"
echo "Check the ../images/ directory for downloaded files."