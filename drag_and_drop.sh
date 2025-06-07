#si sur windows, taper la commande dos2unix drag_and_drop.sh avant de lancer le script

nb_routers=12
config_files=()
origin_directory=$(dirname "$0")

for i in $(seq 1 $nb_routers); do
    file_name="i${i}_startup-config.cfg"
    config_files+=("$file_name")
done

for config_file in "${config_files[@]}"; do
    for file in $(find "$origin_directory" -type f -name "$config_file"); do
        dir=$(dirname "$file")
        echo "Le fichier '$config_file' a été trouvé dans le dossier '$dir'"
        mv "$origin_directory/$config_file" "$file"
        echo "Fichier '$config_file' déplacé"
    done
done
