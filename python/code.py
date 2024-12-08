import os  # Gestion des fichiers et dossiers
import tkinter  # Interface graphique
from tkinter import filedialog, messagebox  # Boîtes de dialogue pour sélection de fichier et messages
from PIL import Image, ImageTk  # Manipulation et affichage d'images
import pandas  # Manipulation de données tabulaires (fichiers CSV)
from diagrams import Diagram, Edge  # Création de diagrammes
from diagrams.custom import Custom  # Utilisation d'icônes personnalisées dans les diagrammes
from diagrams.generic.device import Mobile  # Icône pour les téléphones
from diagrams.gcp.network import Router  # Icône pour les routeurs
from diagrams.aws.game import GameTech  # Icône pour les consoles de jeu
from diagrams.generic.device import Tablet  # Icône pour les tablettes
from diagrams.aws.robotics import Robotics  # Icône pour les dispositifs IA
from diagrams.generic.compute import Rack  # Icône pour les serveurs
from diagrams.generic.network import Switch  # Icône pour les commutateurs réseau
from diagrams.programming.flowchart import Inspection  # Icône générique pour un appareil inconnu

# Dictionnaire pour chaque type d'appareil
mappage_icone = {
    'imprimante': lambda label: Custom(label, "icone/imprimante.png"),
    'ordinateur': lambda label: Custom(label, "icone/pc.png"),
    'telephone': Mobile,
    'routeur': Router,
    'console': GameTech,
    'camera': lambda label: Custom(label, "icone/cam_secu.png"),
    'tablette': Tablet,
    'tv': lambda label: Custom(label, "icone/tv.png"),
    'ia': Robotics,
    'serveur': Rack,
    'switch': Switch,
    'scanner': lambda label: Custom(label, "icone/scanner.png"),
    'montre': lambda label: Custom(label, "icone/montre.png"),
    'autre': Inspection
}





# Fonction pour ouvrir un fichier avec l'application par défaut
def ouvrir_fichier(chemin_fichier):
    try:#pour gérer les erreurs pouvant survenir lors de l'ouverture du fichier
        os.startfile(chemin_fichier)  # Pour Windows
    except AttributeError:# si c'est pas  Windows (Linux ou MacOS), ça déclenche une exception 
        import subprocess#bibliothèque pour exécuter des commandes système et de lancer des processus en sous-tâche
        subprocess.call(('open' if os.name == 'posix' else 'xdg-open', chemin_fichier))
        #Sur MacOS (os.name == 'posix'), utilise la commande open
        #Sur d'autres systèmes Unix/Linux, utilise la commande xdg-open
    except Exception as e:#sinon erreur
        messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {e}")




# Générer le diagramme
def generer_diagramme():
    #pour bien selectionner les fichiers
    if not fichier_appareil.get() or not fichier_connexion.get():
        messagebox.showerror("Erreur", "Veuillez sélectionner les fichiers CSV nécessaires.")
        return

    try:
        # Charge les fichiers CSV dans des DataFrames pandas
        appareil_dict = pandas.read_csv(fichier_appareil.get(), sep=';')
        connexion_dict = pandas.read_csv(fichier_connexion.get(), sep=';')
        # Supprime les lignes vides du fichier des connexions(nan)
        connexion_dict_sans_nans = connexion_dict.dropna(how='all')
        # Définit le chemin du fichier de sortie pour le schéma généré
        nom_fichier = os.path.join("Schema_configuration_reseau")
        
#pour creer diagrzmme
        with Diagram(show=False, direction="TB", filename=nom_fichier):
            noeuds_appareils = {}# Initialise un dictionnaire pour stocker les nœuds

            for _, ligne in appareil_dict.iterrows():
                type_appareil = ligne['type']
                nom_appareil = ligne['nom']
                # Crée une étiquette pour chaques appareils
                ips_appareil = [ip for col, ip in ligne.items() if col.startswith('ip') and pandas.notna(ip)]
                etiquette_appareil = f"{nom_appareil}\n" + "\n".join(ips_appareil)
                #creer noeuds
                fonction_icone = mappage_icone.get(type_appareil, mappage_icone['autre'])
                #ajt noeuds dans un dict
                noeuds_appareils[nom_appareil] = fonction_icone(etiquette_appareil)
                
            #trouver cb ya de colonnes ip
            colonnes_ip = [col for col in appareil_dict.columns if col.startswith('ip')]
            
            #pour les connexions entre les appareils en utilisant les informations dans le fichier des connexions
            for _, ligne in connexion_dict_sans_nans.iterrows():
                nom_appareil = ligne['nom']
                if nom_appareil in noeuds_appareils:
                    # Récupère toutes les adresses IP de connexion non nulles
                    ips_connexion = [ip for col, ip in ligne.items() if col.startswith('c') and pandas.notna(ip)]
                    
                    #trouver l'appareil cible correspondant à une adresse IP donnée
                    for ip in ips_connexion:
                        appareil_cible = next(
                            (appareil for nom_appareil, appareil in noeuds_appareils.items()
                             if ip in appareil_dict.loc[appareil_dict['nom'] == nom_appareil, colonnes_ip].values.flatten()),
                            None
                        )
                        #creer connection
                        if appareil_cible:
                            noeuds_appareils[nom_appareil] >> Edge(label=ip) >> appareil_cible

        messagebox.showinfo("Succès", f"Diagramme généré avec succès : {nom_fichier}.png")
        afficher_diagramme(nom_fichier + ".png")

    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")




# Sélectionner le fichier CSV "afficher"
def choisir_fichier_appareil():
    chemin_fichier = filedialog.askopenfilename(filetypes=[("Fichiers CSV", "*.csv")])
    fichier_appareil.set(chemin_fichier)

# Sélectionner le fichier CSV "connexion"
def choisir_fichier_connexion():
    chemin_fichier = filedialog.askopenfilename(filetypes=[("Fichiers CSV", "*.csv")])
    fichier_connexion.set(chemin_fichier)
    
    
    

# Afficher le diagramme dans une fenêtre Tkinter
def afficher_diagramme(chemin_image):
    if not os.path.exists(chemin_image):
        messagebox.showerror("Erreur", "Le fichier de diagramme n'a pas été trouvé.")
        return

#creation fenetre tinker pour ajouter image diagramme
    fenetre_affichage = tkinter.Toplevel()
    fenetre_affichage.title("Schéma Réseau")
    img = Image.open(chemin_image)
    img = img.resize((1200, 600))
    img_tk = ImageTk.PhotoImage(img)#Convertit l'image Pillow au format compatible avec Tkinter 
    label = tkinter.Label(fenetre_affichage, image=img_tk) #Associer l'image convertie à un widget pour l'afficher dans la fenêtre Tkinter
    label.image = img_tk #pour pas perdre l'image
    label.pack()

#btn fermer
    bouton_fermer = tkinter.Button(fenetre_affichage, text="Fermer", command=fenetre_affichage.destroy, fg="red")
    bouton_fermer.pack(side="right")

#btn modifier
    bouton_modifier = tkinter.Button(fenetre_affichage, text="Modifier", command=choisir_et_ouvrir_fichier)
    bouton_modifier.pack(side="right")

    fenetre_affichage.mainloop()
    
    
    
    

# Fichier appareils ou connexions
def choisir_et_ouvrir_fichier():
    """Demande à l'utilisateur de choisir entre ouvrir le fichier des appareils (A)
    ou le fichier des connexions (B), puis ouvre le fichier choisi."""
    fenetre_choix = tkinter.Toplevel()#Crée une nouvelle sous-fenêtre
    fenetre_choix.title("Choix du fichier")
    fenetre_choix.geometry("300x150")

     #Ajoute un texte
    tkinter.Label(fenetre_choix, text="Quel fichier voulez-vous modifier ?").pack(pady=10)

#ouvrir le fichier appareils
    btn_appareil = tkinter.Button(
        fenetre_choix, text="Fichier CSV des appareils",
        command=lambda: ouvrir_fichier(fichier_appareil.get()) or fenetre_choix.destroy())
    btn_appareil.pack(pady=5)

#ouvrir le fichier connexions
    btn_connexion = tkinter.Button(fenetre_choix, text="Fichier CSV des connexions",
        command=lambda: ouvrir_fichier(fichier_connexion.get()) or fenetre_choix.destroy())
    btn_connexion.pack(pady=5)

#bouton annuler
    btn_annuler = tkinter.Button(fenetre_choix, text="Annuler", command=fenetre_choix.destroy, fg="red")
    btn_annuler.pack(pady=5)
    
    
    
    

#////////////////////la fenêtre principal///////////////////////
app = tkinter.Tk()
app.title("Générateur de Schéma Réseau")
app.geometry("500x300")
#Déclaration des variables pour les chemins des fichiers
fichier_appareil = tkinter.StringVar()
fichier_connexion = tkinter.StringVar()

# Interface pour le fichier CSV des appareils
tkinter.Label(app, text="Fichier CSV des appareils :").pack(pady=5)
tkinter.Entry(app, textvariable=fichier_appareil, width=50).pack()
tkinter.Button(app, text="Parcourir...", command=choisir_fichier_appareil).pack(pady=5)

# Interface pour le fichier CSV des connexions
tkinter.Label(app, text="Fichier CSV des connexions :").pack(pady=5)
tkinter.Entry(app, textvariable=fichier_connexion, width=50).pack()
tkinter.Button(app, text="Parcourir...", command=choisir_fichier_connexion).pack(pady=5)

#Bouton pour générer le schéma
tkinter.Button(app, text="Générer le Schéma", command=generer_diagramme).pack(pady=20)

app.mainloop()
