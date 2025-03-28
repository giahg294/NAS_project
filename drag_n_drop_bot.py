import os
import shutil

destination = "GNS/project-files/dynamips"

# Définir la liste des répertoires cibles : 14 routers
target_directory = [
    "/9191d186-c209-4e08-a6df-8f9201c8c7be/configs", # R1
    "/2102be25-f3ed-40de-b0a3-02774184d998/configs", # R2
    "/f22252b5-97a1-4a22-8f63-f4807e494969/configs", # R3
    "/dd1b9ebf-1a1a-4af0-af18-8c97b4fea94f/configs", # R4
]

def drag_file(i, fichiers_config):
    file = fichiers_config[i]
    target_file = destination + target_directory[i] + "/" + fichiers_config[i]
    shutil.move(file,target_file)
    print(f"le bot s'est occupé {fichiers_config[i]} avec succès.")