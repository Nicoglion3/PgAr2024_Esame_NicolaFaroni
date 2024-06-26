from class_mazzo import Mazzo
from class_giocatore import Giocatore
from class_mano import Mano
import random
import json

class Partita:
    def __init__(self, num_giocatori: int, lista_giocatori: list, turno: int, pila_scarti: list, fine_partita: bool, tipo_partita: int):
        self._num_giocatori = num_giocatori
        self._lista_giocatori = lista_giocatori
        self._turno = turno
        self._mazzo = Mazzo.crea_mazzo()
        self._pila_scarti = pila_scarti
        self._fine_partita = fine_partita
        self._tipo_partita = tipo_partita

    def aggiungi_giocatori(self, num_giocatori: int):
        ruoli = self.assegna_ruoli(num_giocatori)
        self._lista_giocatori = [Giocatore(ruoli[i], ruoli[i] == 'Sceriffo', i, 4) for i in range(num_giocatori)]
        random.shuffle(self._lista_giocatori[1:])

    def aggiungi_pf(self):
        for giocatore in self._lista_giocatori:
            if giocatore._ruolo == "Sceriffo":
                giocatore._pf = 5
            else:
                giocatore._pf = 4

    def assegna_ruoli(self, num_giocatori: int):
        ruoli = ["Sceriffo", "Rinnegato"] + ["Fuorilegge"]*2
        if num_giocatori == 5:
            ruoli.append("Vice")
        if num_giocatori == 6:
            ruoli.append("Fuorilegge")
        if num_giocatori == 5:
            ruoli.append("Vice")
        random.shuffle(ruoli[1:])
        return ruoli

    def prendi_posizioni_giocatori(self):
        posizioni = []
        for giocatore in self._lista_giocatori:
            posizioni.append(giocatore._posizione)
        return posizioni
    
    def calcola_distanza(self, giocatore1: Giocatore, giocatore2: Giocatore):
        num_giocatori = len(self._lista_giocatori)
        distanza_orario = (giocatore1._posizione - giocatore2._posizione) % num_giocatori   # Questo garantisce che venga ritornato un valore positivo
        distanza_antiorario = num_giocatori - distanza_orario
        return min(distanza_orario, distanza_antiorario)
    
    def visualizza_distanza(self, giocatore1: Giocatore, giocatore2: Giocatore):
        if giocatore1._posizione == giocatore2._posizione:
            print(f"Il giocatore {giocatore1._id} è a distanza 0 da {giocatore2._id}")
        else:
            distanza = self.calcola_distanza(giocatore1, giocatore2)
            print(f"Il giocatore {giocatore1._id} è a distanza {distanza} da {giocatore2._id}")

    def scarta_carte(self, giocatore: Giocatore):
        while len(Mano._carte) > giocatore._pf:
            print(f"{Mano._carte}\n")
            print(f"Devi scartare {len(Mano._carte)-giocatore._pf}\n") 
            carta_da_scartare = input("Seleziona la carta che vuoi scartare: \n")
            if carta_da_scartare in Mano._carte:
                Mano.rimuovi_carta(Mano, carta_da_scartare, self._pila_scarti)
            else:
                print("La carta selezionata non è nella tua mano, Riprova\n")

    def verifica_condizioni_fine_partita(self, giocatore_eliminato: Giocatore):
        self._fine_partita = False
        vittoria_legge = False
        vittoria_rinnegato = False
        vittoria_fuorilegge = False
        if giocatore_eliminato._ruolo == "Sceriffo":
            rinnegato_in_gioco = False
            altri_giocatori_vivi = False
            for giocatori in self._lista_giocatori:
                if giocatori._ruolo == "Rinnegato" and giocatori._pf > 0:
                    rinnegato_in_gioco = True
                elif giocatori._pf > 0:
                    altri_giocatori_vivi = True
            if altri_giocatori_vivi and not rinnegato_in_gioco:
                print("I fuorilegge hanno vinto!")
                self._fine_partita = True
                vittoria_fuorilegge = True
            if not altri_giocatori_vivi and rinnegato_in_gioco:
                print("Il rinnegato ha vinto!")
                self._fine_partita = True
                vittoria_rinnegato = True
        if giocatore_eliminato._ruolo == "Fuorilegge" or giocatore_eliminato._ruolo == "Rinnegato":
            rinnegato_vivo = False
            fuorilegge_vivi = False
            for giocatori in self._lista_giocatori:
                if giocatori._ruolo == "Rinnegato" and giocatori._pf > 0:
                    rinnegato_vivo = True
                if giocatori._ruolo == "Fuorilegge" and giocatori._pf > 0:
                    fuorilegge_vivi = True
            if not fuorilegge_vivi and not rinnegato_vivo:
                for giocatori in self._lista_giocatori:
                    if giocatori._ruolo == "Sceriffo" or giocatori._ruolo == "Vice":
                        print("Lo sceriffo e i suoi Vice hanno vinto!")
                        self._fine_partita = True
                        vittoria_legge = True
        if vittoria_legge:
            self.calcolo_punti_legge()
        if vittoria_fuorilegge:
            self.calcolo_punti_fuorilegge()
        if vittoria_rinnegato:
            self.calcolo_punti_rinnegato()


    def elimina_giocatore(self, giocatore_colpito: Giocatore, attaccante: Giocatore):
        if giocatore_colpito._pf <= 0:
            print(f"Il giocatore eliminato aveva il ruolo di {giocatore_colpito._ruolo}")
            for carta in len(giocatore_colpito._mano):
                giocatore_colpito._mano.remove(carta)
                self._pila_scarti.append(carta)
            self.verifica_condizioni_fine_partita(giocatore_colpito)
            self._lista_giocatori.remove(giocatore_colpito)
        if attaccante._ruolo == "Sceriffo" and giocatore_colpito._pf <= 0 and giocatore_colpito._ruolo == "Vice":
            for i in attaccante._mano._carte:
                Mano.rimuovi_carta(i, self._pila_scarti)
            ## scarta equipaggiamento
        if giocatore_colpito._ruolo == "Fuorilegge" and giocatore_colpito._pf <= 0:
            for i in range(3):
                Giocatore.pesca_carte(attaccante, self._mazzo)

    def carta_bang(self, giocatore: Giocatore, attaccante: Giocatore):
        colpo_a_segno = False
        if giocatore.gioca_carte()._nome == "BANG!":
            bang_giocato = True
            self.visualizza_distanza(giocatore, attaccante)
            distanza = self.calcola_distanza(giocatore, attaccante)
            if not giocatore._equipaggiamento and distanza == 1:
                colpo_a_segno = True
                self.gestione_mancato(giocatore)
            if giocatore._equipaggiamento and distanza <= giocatore._equipaggiamento._distanza:
                colpo_a_segno = True
                self.gestione_mancato(giocatore)
        if giocatore.gioca_carte()._nome == "BANG!" and bang_giocato:
            print("Hai già giocato un BANG! questo turno, cambia carta\n")
            Giocatore.gioca_carte(giocatore)

    def gestione_mancato(self, giocatore: Giocatore):
        if "Mancato!" in giocatore._mano:
            risposta = input("Vuoi usare la carta Mancato! ?\n")
            if risposta == "si":
                giocatore._mano._carte.pop("Mancato!")
                print("Hai schivato l'attacco")
            else:
                giocatore._pf -= 1
                print("Hai subito un colpo, i tuoi punti ferita sono scesi")
        else:
            print("Non hai la carta Mancato! in mano")

    def equipaggiamento(giocatore: Giocatore):
        if giocatore.gioca_carte()._equipaggiabile:
            giocatore._equipaggiamento = giocatore.gioca_carte()
            arma = True
        if giocatore.gioca_carte()._equipaggiabile and arma:
            giocatore._equipaggiamento = giocatore.gioca_carte()

    def turno_giocatore(self, giocatore: Giocatore):
        print(f"È il turno del giocatore {giocatore._id} ({giocatore._ruolo})")
        for i in range(2):
            Giocatore.pesca_carte(giocatore, self._mazzo)
        while len(giocatore._mano) >= 0: 
            Giocatore.gioca_carte(giocatore)
            self.carta_bang()
            self.equipaggiamento()
        else:
            print("Hai finito le carte in mano\n")
        self.scarta_carte(giocatore)
        Giocatore.visualizza_pf(giocatore)
        print("Fine del turno")    

    def inizia_partita(self):
        while not self._fine_partita:
            print("In che modalità vuoi giocare?\n")
            risposta = int(input("Premi 1 per la modalità classica e 2 per la modalità torneo\n"))
            if risposta == 1:
                self._turno = 0
                giocatore_corrente = self._lista_giocatori[self._turno % len(self._lista_giocatori)]    
                self.turno_giocatore(giocatore_corrente)
                self._turno += 1
            else:
                self.modalità_torneo()

    def modalità_torneo(self):
        for giocatore in self._lista_giocatori:
            giocatore._sbleuri = 500
            giocatore._sbleuri -= 50
        self._turno = 0
        giocatore_corrente = self._lista_giocatori[self._turno % len(self._lista_giocatori)]    
        self.turno_giocatore(giocatore_corrente)
        self._turno += 1

    def calcolo_punti_legge(self):
        if self._num_giocatori == 4:
            for i in self._lista_giocatori:
                if i._ruolo == "Sceriffo":
                    i._sbleuri += 1400
                if i._ruolo == "Rinnegato":
                    i._sbleuri += 250
        if self._num_giocatori == 5:
            for i in self._lista_giocatori:
                if i._ruolo == "Sceriffo":
                    i._sbleuri += 1200
                if i._ruolo == "Vice":
                    i._sbleuri += 1200
                if i._ruolo == "Rinnegato":
                    i._sbleuri += 300
        if self._num_giocatori == 6:
            for i in self._lista_giocatori:
                if i._ruolo == "Sceriffo":
                    i._sbleuri += 1600
                if i._ruolo == "Vice":
                    i._sbleuri += 1600
                if i._ruolo == "Rinnegato":
                    i._sbleuri += 350
        if self._num_giocatori == 7:
            for i in self._lista_giocatori:
                if i._ruolo == "Sceriffo":
                    i._sbleuri += 1200
                if i._ruolo == "Vice":
                    i._sbleuri += 1200
                if i._ruolo == "Rinnegato":
                    i._sbleuri += 400
        print("Sbleuri assegnati")

    def calcolo_punti_fuorilegge(self):
        if self._num_giocatori == 4:
            for i in self._lista_giocatori:
                if i._ruolo == "Fuorilegge":
                    i._sbleuri += 2200
        if self._num_giocatori == 5:
            for i in self._lista_giocatori:
                if i._ruolo == "Fuorilegge":
                    i._sbleuri += 2400
        if self._num_giocatori == 6:
            for i in self._lista_giocatori:
                if i._ruolo == "Fuorilegge":
                    i._sbleuri += 2600
        if self._num_giocatori == 7:
            for i in self._lista_giocatori:
                if i._ruolo == "Fuorilegge":
                    i._sbleuri += 2800
        print("Sbleuri assegnati")

    def calcolo_punti_rinnegato(self):
        if self._num_giocatori == 4:
            for i in self._lista_giocatori:
                if i._ruolo == "Rinnegato":
                    i._sbleuri += 2200
        if self._num_giocatori == 5:
            for i in self._lista_giocatori:
                if i._ruolo == "Rinnegato":
                    i._sbleuri += 2400
        if self._num_giocatori == 6:
            for i in self._lista_giocatori:
                if i._ruolo == "Rinnegato":
                    i._sbleuri += 2600
        if self._num_giocatori == 7:
            for i in self._lista_giocatori:
                if i._ruolo == "Rinnegato":
                    i._sbleuri += 2800
        print("Sbleuri assegnati")

    def verifica_num_giocatori(self) -> int:
        num_giocatori = 0
        num_giocatori = int(input("Inserisci il numero di giocatori: "))
        while num_giocatori < 4 or num_giocatori > 7:
            num_giocatori = int(input("Hai sbagliato ad inserire il numero di giocatori, riprova (4-7)"))
        return num_giocatori
    
    def scrivi_classifica(self):
        percorso_file = "classifica_finale.json"
        with open(percorso_file, "w") as file:
            json.dump(self._lista_giocatori, file, indent=4)




