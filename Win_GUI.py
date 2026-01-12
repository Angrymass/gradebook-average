import sys
import os
import re

from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QLabel, QPushButton, QScrollArea, QDialog, QVBoxLayout, QDialogButtonBox, QLineEdit, QMessageBox
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt
import requests

import Web_Agent
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT

ICONA_APP = "assets/icon.ico"

current_key = ""
current_user = ""

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def sist_stringa(stringa):
    return re.sub(r'[^\w\s]', ' ', stringa, flags=re.UNICODE)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__() 

        self.medie = []
        self.list_voti = []
        self.crono_materie = {}
        self.default_crono = "Nessun Voto"
        self.default_media_tot = "Nessun Voto"
        self.default_media_materie = "Nessuna Materia"

        self.setWindowTitle("Calcolatore Media Ponderata Materie")
        self.setWindowIcon(QIcon(resource_path(ICONA_APP)))
        self.setMinimumSize(300, 300)

        self.label_crono_voti = QLabel(self.default_crono)
        self.label_crono_voti.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.label_crono_voti.setWordWrap(True)

        self.label_media_tot = QLabel(self.default_media_tot)
        self.label_media_tot.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.label_media_tot.setWordWrap(True)
        self.label_media_tot.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        self.button_aggvoto = QPushButton("Aggiungi voto...")
        self.button_aggvoto.setToolTip("Aggiungi un nuovo voto manualmente")
        self.button_aggvoto.setMinimumHeight(40)
        self.button_aggvoto.clicked.connect(self.nvoto)

        self.label_media_materie = QLabel(self.default_media_materie)
        self.label_media_materie.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.label_media_materie.setWordWrap(True)

        self.cancella_voto = QPushButton("Cancella Ultimo Voto")
        self.cancella_voto.setToolTip("Cancella l'ultimo voto inserito")
        self.cancella_voto.setMinimumHeight(40)
        self.cancella_voto.clicked.connect(self.on_cancella_voto)

        self.scrollvoti = QScrollArea()
        self.scrollvoti.setWidgetResizable(True)
        self.scrollvoti.setWidget(self.label_crono_voti)

        self.scrollmaterie = QScrollArea()
        self.scrollmaterie.setWidgetResizable(True)
        self.scrollmaterie.setWidget(self.label_media_materie)

        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.fig)   
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        layout = QGridLayout()

        layout.addWidget(self.scrollvoti, 0, 0, 3, 1)
        layout.addWidget(self.button_aggvoto, 3, 0, 1, 1)
        layout.addWidget(self.cancella_voto, 4, 0, 1, 1)
        layout.addWidget(self.label_media_tot, 0, 1, 2, 1)
        layout.addWidget(self.scrollmaterie, 2, 1, 3, 1)
        layout.addWidget(self.toolbar, 0, 2, 1, 1)
        layout.addWidget(self.canvas, 1, 2, 4, 1)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.aggiorna()

    def nvoto(self):
        DialogAggiungiVoto(self).exec()
        self.aggiorna()

    def fetchvoti(self):
        global current_key
        global current_user
        try:
            voti = Web_Agent.voti(current_key, current_user)
        except Web_Agent.LoginError:
            QMessageBox.critical(self, "Errore", "Sessione scaduta o non valida. Effettua nuovamente il login.")
            return
        except requests.exceptions.RequestException:
            QMessageBox.critical(self, "Errore", "Errore di connessione. Controlla la connessione e riprova.")
            return
        except Exception:
            QMessageBox.critical(self, "Errore", "Errore sconosciuto durante il recupero dei voti.")
            return
        if not voti:
            QMessageBox.information(self, "Info", "Nessun voto trovato nel registro.")
            return
        self.list_voti = []
        for voto in voti:
            voto = [float(voto["voto"]), sist_stringa(voto["materia"]), int(voto["peso"])]
            self.list_voti.append([voto[0], voto[1], voto[2]])
        self.aggiorna()
    
    def on_cancella_voto(self):
        if len(self.list_voti) > 0:
            self.list_voti.pop()
        self.aggiorna()
    
    def aggiorna(self):
        self.make_crono_materie()
        self.make_label_crono_voti()
        self.make_label_media_tot()
        self.make_label_media_materie()
        self.make_medie()
        self.make_grafico()

    def make_medie(self):
        self.medie = []
        tot = 0
        peso = 0
        for voto, materia, p in self.list_voti:
            tot += voto * (p / 100)
            peso += (p / 100)
            self.medie.append(tot / peso if peso != 0 else 0)

    def make_grafico(self):
        self.ax.clear()
        self.ax.plot(self.medie, marker='o')
        self.ax.set_ylim(0, 10)
        self.ax.set_title("Andamento Media")
        self.ax.set_xlabel("Numero Voti")
        self.ax.set_ylabel("Media")
        self.ax.grid(True)
        self.canvas.draw()

    def make_crono_materie(self):
        self.crono_materie = {}
        for voto in self.list_voti:
            materia = voto[1]
            if materia not in self.crono_materie:
                self.crono_materie[materia] = []
            self.crono_materie[materia].append([voto[0], voto[2]])

    def make_crono_materie(self):
        self.crono_materie = {}
        for voto in self.list_voti:
            materia = voto[1]
            if materia not in self.crono_materie:
                self.crono_materie[materia] = []
            self.crono_materie[materia].append([voto[0], voto[2]])

    def make_label_crono_voti(self):
        if len(self.list_voti) != 0:
            text = ""
            for i in range(len(self.list_voti), 0, -1):
                voto = self.list_voti[i-1]
                if voto[2] == 100:
                    text += "%s - %s\n" % (voto[0], voto[1])
                else:
                    text += "%s (peso %s) - %s\n" % (voto[0], str(voto[2]) + "%", voto[1])
        else:
            text = self.default_crono
        self.label_crono_voti.setText(text)

    def make_label_media_tot(self):
        if len(self.list_voti) != 0:
            total = 0
            peso = 0
            for voto in self.list_voti:
                total += voto[0] * (voto[2] / 100)
                peso += (voto[2] / 100)
            media = (total / peso) if peso != 0 else 0
            media = str(round(media, 2))
            text = "Media: %s" % media
        else:
            text = self.default_media_tot
        self.label_media_tot.setText(text)

    def make_label_media_materie(self):	
        if len(self.crono_materie) != 0:
            text = ""
            for materia, voti in self.crono_materie.items():
                media_materia = 0
                peso = 0
                for voto in voti:
                    media_materia += voto[0] * (voto[1] / 100)
                    peso += (voto[1] / 100)
                media_materia = (media_materia / peso) if peso != 0 else 0
                media_materia = str(round(media_materia, 2))
                text += "%s: %s\n" % (materia, media_materia)
        else:
            text = self.default_media_materie
        self.label_media_materie.setText(text)

class DialogLogin(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login...")
        self.setWindowIcon(QIcon(resource_path(ICONA_APP)))

        self.login_label = QLabel("Inserisci username e password:")
        self.login_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.username_line = QLineEdit()
        self.username_line.setPlaceholderText("Username")

        self.password_line = QLineEdit()
        self.password_line.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_line.setPlaceholderText("Password")
        
        buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonbox.accepted.connect(self.endloginok)
        buttonbox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.login_label)
        layout.addWidget(self.username_line)
        layout.addWidget(self.password_line)
        layout.addWidget(buttonbox)
        self.setLayout(layout)  
    
    def endloginok(self):
        global current_key
        global current_user
        username = self.username_line.text()
        password = self.password_line.text()
        if username == "" or password == "":
            QMessageBox.warning(self, "Errore", "Inserisci username e password validi.")
            return
        try:
            current_key, current_user = Web_Agent.login(username, password)
        except Web_Agent.LoginError:
            QMessageBox.critical(self, "Errore", "Login fallito. Controlla username e password.")
            return
        except requests.exceptions.RequestException:
            QMessageBox.critical(self, "Errore", "Errore di connessione. Controlla la connessione e riprova.")
            return
        except FileNotFoundError:
            QMessageBox.critical(self, "Errore", "File di configurazione non trovato. Consultare la documentazione.")
            return
        except Exception:
            QMessageBox.critical(self, "Errore", "Errore sconosciuto durante il login.")
            return
        self.parent().fetchvoti()
        self.accept()

class DialogAggiungiVoto(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aggiungi Voto")
        self.setWindowIcon(QIcon(resource_path(ICONA_APP)))

        self.votolabel = QLabel("Inserisci il voto:")
        self.votolabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.matlabel = QLabel("Inserisci la materia:")
        self.matlabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.pesolabel = QLabel("Inserisci il peso:")
        self.pesolabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.votoinput = QLineEdit()
        self.votoinput.setPlaceholderText("Voto (0.0-10.0)")

        self.matinput = QLineEdit()
        self.matinput.setPlaceholderText("Materia")

        self.pesoinput = QLineEdit()
        self.pesoinput.setPlaceholderText("Peso (1-100)")
        self.pesoinput.setText("100")

        buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonbox.accepted.connect(self.okvoto)
        buttonbox.rejected.connect(self.reject)

        layout = QGridLayout()
        layout.addWidget(self.votolabel, 0, 0)
        layout.addWidget(self.votoinput, 0, 1)
        layout.addWidget(self.matlabel, 1, 0)
        layout.addWidget(self.matinput, 1, 1)
        layout.addWidget(self.pesolabel, 2, 0)
        layout.addWidget(self.pesoinput, 2, 1)
        layout.addWidget(buttonbox, 3, 0, 1, 2)
        self.setLayout(layout)

    def okvoto(self):
        try:
            voto = float(self.votoinput.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Errore", "Inserisci un voto valido.")
            return
        materia = self.matinput.text().strip()
        try:
            peso = int(self.pesoinput.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Errore", "Inserisci un peso valido.")
            return
        if peso < 1 or peso > 100:
            QMessageBox.warning(self, "Errore", "Inserisci un peso valido (1-100).")
            return
        if voto < 0 or voto > 10:
            QMessageBox.warning(self, "Errore", "Inserisci un voto valido (0.0-10.0).")
            return
        if materia == "":
            QMessageBox.warning(self, "Errore", "Inserisci una materia valida.")
            return
        voto_fin = [voto, sist_stringa(materia), peso]
        self.parent().list_voti.append(voto_fin)
        self.parent().aggiorna()
        self.accept()

app = QApplication(sys.argv)
window = MainWindow()
dialog = DialogLogin(window)
dialog.exec()
window.show()  
app.exec()