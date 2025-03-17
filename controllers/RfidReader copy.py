import threading
from controllers.ApiPlateforme import ApiPlateforme
from smartcard.System import readers
from smartcard.util import toHexString
import time
# from controllers.App import App

class RfidReader:
    
    def start_rfid_thread(self,appInstance,part2_frame, canvas, part3_frame, data_badges, callback):
        print('démarrage du processus de lecteur de carte');
        thread = threading.Thread(target=self.read_rfid, args=(
            part2_frame, canvas, part3_frame, data_badges, appInstance, callback))
        
        thread.daemon = True
        thread.start()


    def read_rfid(self, part2_frame, canvas, part3_frame, data_badges, appInstance, callback):
        print("En attente d'une carte...")

        reader_list = readers()
        if not reader_list:
            print("Aucun lecteur détecté.")
            return
        
        reader = reader_list[0]
        connection = reader.createConnection()

        while True:
            try:
                # Vérifier si une carte est insérée en tentant de se connecter
                try:
                    connection.connect()
                except Exception as e:
                    if "No smart card inserted" in str(e):
                        print("Aucune carte détectée, attente...")
                        time.sleep(1)
                        continue  # Retour au début de la boucle
                    else:
                        raise  # Si ce n'est pas une erreur de carte absente, on affiche l'erreur

                print("Carte détectée ! Lecture en cours...")

                # Lire le numéro de série de la carte
                READ_SERIAL = [0xFF, 0xCA, 0x00, 0x00, 0x00]
                try:
                    response, sw1, sw2 = connection.transmit(READ_SERIAL)
                except Exception as e:
                    print(f"Erreur lors de la transmission : {e}")
                    time.sleep(1)
                    continue  # Recommencer la boucle proprement

                # Vérification du statut SW1 SW2
                if sw1 == 0x90 and sw2 == 0x00:
                    card_id = int(toHexString(response[::-1]).replace(" ", ""), 16)
                    print(f"ID de la carte : {card_id}")

                    student_email = ApiPlateforme.get_student_by_badge(data_badges, card_id)

                    if student_email:
                        callback(student_email, True)
                        print(f"Email étudiant : {student_email}")
                    else:
                        print("L'email étudiant est vide.")
                else:
                    print(f"Erreur lors de la lecture : statut SW1={sw1}, SW2={sw2}")

                connection.disconnect()
                time.sleep(0.5)  # Petite pause pour éviter les erreurs

                # Attendre que la carte soit retirée avant de continuer
                while True:
                    try:
                        connection.connect()
                        time.sleep(0.5)  # Pause avant de revérifier
                    except:
                        print("Carte retirée, en attente d'une nouvelle carte...")
                        break  # Sortie de la boucle pour attendre une nouvelle carte

            except Exception as e:
                print(f"Erreur lors de la lecture : {e}")
                time.sleep(1)  # Attendre avant de réessayer


    # root.after(10000, read_rfid, root)
