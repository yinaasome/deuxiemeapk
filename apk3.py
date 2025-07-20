#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application Mobile Money - Version Réajustée avec Gestion Complète des Clients
"""

import sqlite3
import hashlib
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import os

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import ListProperty, StringProperty
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.utils import platform 
from plyer import storagepath
# Configuration Matplotlib
plt.switch_backend('agg')

# =============================================================================
# CONFIGURATION DES STYLES
# =============================================================================

COLORS = {
    'PRIMARY': [0.129, 0.588, 0.953, 1],    # Bleu Orange
    'SECONDARY': [0.961, 0.341, 0.133, 1],   # Orange vif
    'BACKGROUND': [0.95, 0.95, 0.95, 1],     # Gris clair
    'TEXT': [0.2, 0.2, 0.2, 1],             # Noir
    'WHITE': [1, 1, 1, 1],
    'ERROR': [0.9, 0.1, 0.1, 1],             # Rouge
    'SUCCESS': [0.2, 0.7, 0.2, 1]            # Vert
}

OPERATORS = ['Orange', 'Moov', 'Telecel', 'Sank', 'Waves', 'TNT']
OPERATIONS = ['Retrait', 'Dépôt', 'Unité']

Builder.load_string(f'''
#:import dp kivy.metrics.dp
#:set PRIMARY {COLORS["PRIMARY"]}
#:set SECONDARY {COLORS["SECONDARY"]}
#:set BACKGROUND {COLORS["BACKGROUND"]}
#:set TEXT {COLORS["TEXT"]}
#:set WHITE {COLORS["WHITE"]}
#:set ERROR {COLORS["ERROR"]}
#:set SUCCESS {COLORS["SUCCESS"]}

<CustomButton>:
    background_color: [0,0,0,0]
    background_normal: ''
    size_hint_y: None
    height: dp(50)
    canvas.before:
        Color:
            rgba: self.background_color_custom if self.background_color_custom else PRIMARY
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10),]
    color: WHITE
    bold: True
    font_size: '16sp'

<CustomTextInput>:
    size_hint_y: None
    height: dp(40)
    padding: [dp(10), dp(10), dp(10), dp(10)]
    background_color: WHITE
    foreground_color: TEXT
    multiline: False
    canvas.before:
        Color:
            rgba: [0.8, 0.8, 0.8, 1] if self.focus else [0.7, 0.7, 0.7, 1]
        Line:
            width: 1.2 if self.focus else 1
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(5))

<RoundedBox@BoxLayout>:
    canvas.before:
        Color:
            rgba: WHITE
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(15),]
''')

# =============================================================================
# COMPOSANTS PERSONNALISÉS
# =============================================================================

class CustomButton(Button):
    background_color_custom = ListProperty(None)


class CustomTextInput(TextInput):
    pass


# =============================================================================
# GESTION DE LA BASE DE DONNÉES
# =============================================================================

class DatabaseManager:
    
    @staticmethod
    def init_database():
        conn = sqlite3.connect('mobile_money.db')
        c = conn.cursor()
        
        # Table des utilisateurs
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        
        # Table des transactions avec informations client complètes
        c.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER,
                client_nom TEXT NOT NULL,
                client_prenom TEXT NOT NULL,
                client_telephone TEXT NOT NULL,
                client_cnib TEXT NOT NULL,
                operator TEXT NOT NULL,
                operation TEXT NOT NULL,
                amount REAL NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (agent_id) REFERENCES users(id)
            )
        ''')
        
        # Créer admin par défaut
        c.execute("SELECT * FROM users WHERE username='admin'")
        if not c.fetchone():
            hashed_password = hashlib.sha256('admin123'.encode()).hexdigest()
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                     ('admin', hashed_password, 'admin'))
        
        conn.commit()
        conn.close()

    @staticmethod
    def add_user(username, password, role):
        conn = sqlite3.connect('mobile_money.db')
        c = conn.cursor()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                     (username, hashed_password, role))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    @staticmethod
    def get_user(username, password):
        conn = sqlite3.connect('mobile_money.db')
        c = conn.cursor()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", 
                 (username, hashed_password))
        user = c.fetchone()
        conn.close()
        return user

    @staticmethod
    def get_all_agents():
        conn = sqlite3.connect('mobile_money.db')
        c = conn.cursor()
        c.execute("SELECT id, username FROM users WHERE role='agent'")
        agents = c.fetchall()
        conn.close()
        return agents

    @staticmethod
    def record_transaction(agent_id, client_nom, client_prenom, client_telephone, 
                         client_cnib, operator, operation, amount):
        conn = sqlite3.connect('mobile_money.db')
        c = conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('''INSERT INTO transactions 
                    (agent_id, client_nom, client_prenom, client_telephone, 
                     client_cnib, operator, operation, amount, timestamp) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (agent_id, client_nom, client_prenom, client_telephone, 
                  client_cnib, operator, operation, amount, timestamp))
        conn.commit()
        conn.close()

    @staticmethod
    def get_transactions_by_agent(agent_id):
        conn = sqlite3.connect('mobile_money.db')
        c = conn.cursor()
        c.execute('''SELECT client_nom, client_prenom, client_telephone, client_cnib,
                    operator, operation, amount, timestamp 
                    FROM transactions WHERE agent_id=? ORDER BY timestamp DESC''', (agent_id,))
        transactions = c.fetchall()
        conn.close()
        return transactions

    @staticmethod
    def get_agent_stats(agent_id):
        conn = sqlite3.connect('mobile_money.db')
        c = conn.cursor()

        # Statistiques par jour
        c.execute('''
                  SELECT 
                  DATE(timestamp) AS date,
                  COUNT(*) AS nb_clients,
                  SUM(amount) AS total_amount
                  FROM transactions 
                  WHERE agent_id=?
                  GROUP BY date
                  ORDER BY date DESC
                  LIMIT 30
                  ''', (agent_id,))
        daily_stats = c.fetchall()

        # Statistiques par réseau
        c.execute('''
                  SELECT 
                  operator,
                  COUNT(*) AS nb_clients,
                  SUM(amount) AS total_amount
                  FROM transactions 
                  WHERE agent_id=?
                  GROUP BY operator
                  ''', (agent_id,))
        operator_stats = c.fetchall()

        # Statistiques par opération
        c.execute('''
                  SELECT 
                  operation,
                  COUNT(*) AS nb_clients,
                  SUM(amount) AS total_amount
                  FROM transactions 
                  WHERE agent_id=?
                  GROUP BY operation
                  ''', (agent_id,))
        operation_stats = c.fetchall()

        # Total général
        c.execute('''
                  SELECT 
                  COUNT(*) AS total_clients,
                  SUM(amount) AS total_amount
                  FROM transactions 
                  WHERE agent_id=?
                  ''', (agent_id,))
        total_stats = c.fetchone()
        conn.close()
        return daily_stats, operator_stats, operation_stats, total_stats

    @staticmethod
    def get_all_transactions():
        conn = sqlite3.connect('mobile_money.db')
        c = conn.cursor()
        c.execute('''SELECT t.client_nom, t.client_prenom, t.client_telephone, 
                    t.client_cnib, t.operator, t.operation, t.amount, 
                    t.timestamp, u.username 
                    FROM transactions t JOIN users u ON t.agent_id = u.id
                    ORDER BY t.timestamp DESC''')
        transactions = c.fetchall()
        conn.close()
        return transactions

    @staticmethod
    def get_transactions_by_agent_for_export(agent_id):
        conn = sqlite3.connect('mobile_money.db')
        c = conn.cursor()
        c.execute('''SELECT client_nom, client_prenom, client_telephone, client_cnib,
                    operator, operation, amount, timestamp 
                    FROM transactions WHERE agent_id=? ORDER BY timestamp DESC''', (agent_id,))
        transactions = c.fetchall()
        conn.close()
        return transactions

    @staticmethod
    def export_to_csv(agent_id=None, filename=None):
        if agent_id:
            transactions = DatabaseManager.get_transactions_by_agent_for_export(agent_id)
            columns = ['Nom', 'Prénom', 'Téléphone', 'CNIB', 'Opérateur', 'Opération', 'Montant', 'Date/Heure']
        else:
            transactions = DatabaseManager.get_all_transactions()
            columns = ['Nom', 'Prénom', 'Téléphone', 'CNIB', 'Opérateur', 'Opération', 'Montant', 'Date/Heure', 'Agent']
        
        df = pd.DataFrame(transactions, columns=columns)
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if agent_id:
                filename = f'transactions_agent_{agent_id}_{timestamp}.csv'
            else:
                filename = f'transactions_all_{timestamp}.csv'
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        return filename

    @staticmethod
    def export_to_xlsx(agent_id=None, filename=None):
        if agent_id:
            transactions = DatabaseManager.get_transactions_by_agent_for_export(agent_id)
            columns = ['Nom', 'Prénom', 'Téléphone', 'CNIB', 'Opérateur', 'Opération', 'Montant', 'Date/Heure']
        else:
            transactions = DatabaseManager.get_all_transactions()
            columns = ['Nom', 'Prénom', 'Téléphone', 'CNIB', 'Opérateur', 'Opération', 'Montant', 'Date/Heure', 'Agent']
        
        df = pd.DataFrame(transactions, columns=columns)
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if agent_id:
                filename = f'transactions_agent_{agent_id}_{timestamp}.xlsx'
            else:
                filename = f'transactions_all_{timestamp}.xlsx'
        
        df.to_excel(filename, index=False)
        return filename

    @staticmethod
    def get_global_stats():
        conn = sqlite3.connect('mobile_money.db')
        c = conn.cursor()

        # Total général
        c.execute('''
                  SELECT COUNT(*) AS total_clients, SUM(amount) AS total_amount
                  FROM transactions
                  ''')
        total = c.fetchone()

        # Par agent
        c.execute('''
                  SELECT u.username, COUNT(t.id), SUM(t.amount)
                  FROM transactions t
                  JOIN users u ON t.agent_id = u.id
                  GROUP BY u.username
                  ''')
        by_agent = c.fetchall()

        # Par réseau
        c.execute('''
                  SELECT operator, COUNT(*), SUM(amount)
                  FROM transactions
                  GROUP BY operator
                  ''')
        by_operator = c.fetchall()

        # Par opération (Dépôt, Retrait, Unité)
        c.execute('''
                  SELECT operation, COUNT(*), SUM(amount)
                  FROM transactions
                  GROUP BY operation
                  ''')
        by_operation = c.fetchall()

        # Montants par agent et opération
        c.execute('''
                  SELECT u.username, t.operation, SUM(t.amount)
                  FROM transactions t
                  JOIN users u ON t.agent_id = u.id
                  GROUP BY u.username, t.operation
                  ''')
        agent_operation_amount = c.fetchall()
        conn.close()
        return {
            'total': total,
            'by_agent': by_agent,
            'by_operator': by_operator,
            'by_operation': by_operation,
            'agent_operation_amount': agent_operation_amount
        }


# =============================================================================
# ÉCRANS DE L'APPLICATION
# =============================================================================

class LoginScreen(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        with self.canvas.before:
            Color(*COLORS['BACKGROUND'])
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        layout = BoxLayout(orientation='vertical', padding=dp(50), spacing=dp(20))
        
        # Titre
        title = Label(text='MOBILE MONEY', 
                     font_size='32sp',
                     bold=True,
                     color=COLORS['PRIMARY'],
                     size_hint_y=None,
                     height=dp(60))
        layout.add_widget(title)
        
        # Formulaire
        form = BoxLayout(orientation='vertical',
                        size_hint=(1, None),
                        height=dp(250),
                        spacing=dp(15),
                        padding=dp(30))
        
        with form.canvas.before:
            Color(*COLORS['WHITE'])
            RoundedRectangle(size=form.size, pos=form.pos, radius=[dp(15),])
        
        # Champs de saisie
        form.add_widget(Label(text="Nom d'utilisateur",
                            color=COLORS['TEXT'],
                            size_hint_y=None,
                            height=dp(30)))
        
        self.username = CustomTextInput(hint_text="Votre nom d'utilisateur")
        form.add_widget(self.username)
        
        form.add_widget(Label(text="Mot de passe",
                            color=COLORS['TEXT'],
                            size_hint_y=None,
                            height=dp(30)))
        
        self.password = CustomTextInput(hint_text="Votre mot de passe",
                                     password=True)
        form.add_widget(self.password)
        
        # Bouton de connexion
        btn_login = CustomButton(text='CONNEXION')
        btn_login.bind(on_press=self.authenticate)
        form.add_widget(btn_login)
        
        layout.add_widget(form)
        self.add_widget(layout)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def authenticate(self, instance):
        username = self.username.text
        password = self.password.text
        
        if not username or not password:
            self.show_popup('Erreur', 'Veuillez remplir tous les champs', 'ERROR')
            return
        
        user = DatabaseManager.get_user(username, password)
        
        if user:
            app = App.get_running_app()
            app.current_user = {
                'id': user[0],
                'username': user[1],
                'role': user[3]
            }
            
            if user[3] == 'admin':
                self.manager.current = 'admin_menu'
            else:
                self.manager.current = 'menu'
        else:
            self.show_popup('Erreur', 'Identifiants incorrects', 'ERROR')
    
    def show_popup(self, title, message, message_type):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=message, 
                               color=COLORS[message_type]))
        
        btn_close = CustomButton(text='OK', size_hint_y=None, height=dp(40))
        popup = Popup(title=title,
                     content=content,
                     size_hint=(0.7, 0.4))
        
        btn_close.bind(on_press=popup.dismiss)
        content.add_widget(btn_close)
        popup.open()


class MenuScreen(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        with self.canvas.before:
            Color(*COLORS['BACKGROUND'])
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        
        # Titre avec nom de l'agent
        self.title = Label(text='MENU AGENT',
                         font_size='28sp',
                         bold=True,
                         color=COLORS['PRIMARY'],
                         size_hint_y=None,
                         height=dp(60))
        layout.add_widget(self.title)
        
        # Boutons
        buttons = [
            ('NOUVELLE TRANSACTION', self.go_to_transaction),
            ('MES STATISTIQUES', self.go_to_stats),
            ('DÉCONNEXION', self.logout)
        ]
        
        for text, callback in buttons:
            btn = CustomButton(text=text)
            btn.bind(on_press=callback)
            layout.add_widget(btn)
        
        self.add_widget(layout)
    
    def on_enter(self, *args):
        app = App.get_running_app()
        if app.current_user:
            self.title.text = f'MENU AGENT - {app.current_user["username"]}'
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def go_to_transaction(self, instance):
        self.manager.current = 'transaction'
    
    def go_to_stats(self, instance):
        self.manager.current = 'agent_stats'
    
    def logout(self, instance):
        App.get_running_app().current_user = None
        self.manager.current = 'login'


class TransactionScreen(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        with self.canvas.before:
            Color(*COLORS['BACKGROUND'])
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # ScrollView pour permettre le défilement
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', 
                          padding=dp(20), 
                          spacing=dp(15),
                          size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        # Titre
        title = Label(text='NOUVELLE TRANSACTION',
                     font_size='24sp',
                     bold=True,
                     color=COLORS['PRIMARY'],
                     size_hint_y=None,
                     height=dp(50))
        layout.add_widget(title)
        
        # Formulaire client
        client_form = BoxLayout(orientation='vertical',
                              size_hint=(1, None),
                              height=dp(400),
                              spacing=dp(10),
                              padding=dp(20))
        
        with client_form.canvas.before:
            Color(*COLORS['WHITE'])
            RoundedRectangle(size=client_form.size, pos=client_form.pos, radius=[dp(15),])
        
        client_form.add_widget(Label(text='INFORMATIONS CLIENT',
                                   font_size='18sp',
                                   bold=True,
                                   color=COLORS['PRIMARY'],
                                   size_hint_y=None,
                                   height=dp(30)))
        
        # Nom
        client_form.add_widget(Label(text='Nom:',
                                   color=COLORS['TEXT'],
                                   size_hint_y=None,
                                   height=dp(25)))
        self.client_nom = CustomTextInput(hint_text='Nom du client')
        client_form.add_widget(self.client_nom)
        
        # Prénom
        client_form.add_widget(Label(text='Prénom:',
                                   color=COLORS['TEXT'],
                                   size_hint_y=None,
                                   height=dp(25)))
        self.client_prenom = CustomTextInput(hint_text='Prénom du client')
        client_form.add_widget(self.client_prenom)
        
        # Téléphone
        client_form.add_widget(Label(text='Numéro de téléphone:',
                                   color=COLORS['TEXT'],
                                   size_hint_y=None,
                                   height=dp(25)))
        self.client_telephone = CustomTextInput(hint_text='Ex: 70123456',
                                               input_filter='int')
        client_form.add_widget(self.client_telephone)
        
        # CNIB
        client_form.add_widget(Label(text='CNIB:',
                                   color=COLORS['TEXT'],
                                   size_hint_y=None,
                                   height=dp(25)))
        self.client_cnib = CustomTextInput(hint_text='Numéro CNIB')
        client_form.add_widget(self.client_cnib)
        
        layout.add_widget(client_form)
        
        # Formulaire transaction
        trans_form = BoxLayout(orientation='vertical',
                             size_hint=(1, None),
                             height=dp(280),
                             spacing=dp(10),
                             padding=dp(20))
        
        with trans_form.canvas.before:
            Color(*COLORS['WHITE'])
            RoundedRectangle(size=trans_form.size, pos=trans_form.pos, radius=[dp(15),])
        
        trans_form.add_widget(Label(text='DÉTAILS TRANSACTION',
                                  font_size='18sp',
                                  bold=True,
                                  color=COLORS['PRIMARY'],
                                  size_hint_y=None,
                                  height=dp(30)))
        
        # Opérateur
        trans_form.add_widget(Label(text='Réseau:',
                                  color=COLORS['TEXT'],
                                  size_hint_y=None,
                                  height=dp(25)))
        self.operator = Spinner(text='Sélectionnez le réseau',
                              values=OPERATORS,
                              size_hint_y=None,
                              height=dp(40))
        trans_form.add_widget(self.operator)
        
        # Opération
        trans_form.add_widget(Label(text='Opération:',
                                  color=COLORS['TEXT'],
                                  size_hint_y=None,
                                  height=dp(25)))
        self.operation = Spinner(text='Sélectionnez l\'opération',
                               values=OPERATIONS,
                               size_hint_y=None,
                               height=dp(40))
        trans_form.add_widget(self.operation)
        
        # Montant
        trans_form.add_widget(Label(text='Montant (XOF):',
                                  color=COLORS['TEXT'],
                                  size_hint_y=None,
                                  height=dp(25)))
        self.amount = CustomTextInput(hint_text='0.00',
                                    input_filter='float')
        trans_form.add_widget(self.amount)
        
        layout.add_widget(trans_form)
        
        # Boutons
        btn_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        
        btn_save = CustomButton(text='ENREGISTRER TRANSACTION')
        btn_save.bind(on_press=self.save_transaction)
        btn_layout.add_widget(btn_save)
        
        btn_back = CustomButton(text='RETOUR',
                              background_color_custom=COLORS['SECONDARY'])
        btn_back.bind(on_press=self.go_back)
        btn_layout.add_widget(btn_back)
        
        layout.add_widget(btn_layout)
        
        scroll.add_widget(layout)
        self.add_widget(scroll)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def save_transaction(self, instance):
        # Validation des champs client
        nom = self.client_nom.text.strip()
        prenom = self.client_prenom.text.strip()
        telephone = self.client_telephone.text.strip()
        cnib = self.client_cnib.text.strip()
        
        if not all([nom, prenom, telephone, cnib]):
            self.show_popup('Erreur', 'Veuillez remplir toutes les informations client', 'ERROR')
            return
        
        # Validation des champs transaction
        operator = self.operator.text
        operation = self.operation.text
        amount = self.amount.text
        
        if operator in ['Sélectionnez le réseau', '']:
            self.show_popup('Erreur', 'Veuillez sélectionner un réseau', 'ERROR')
            return
        
        if operation in ['Sélectionnez l\'opération', '']:
            self.show_popup('Erreur', 'Veuillez sélectionner une opération', 'ERROR')
            return
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Le montant doit être positif")
        except ValueError:
            self.show_popup('Erreur', 'Montant invalide', 'ERROR')
            return
        
        # Enregistrer la transaction
        app = App.get_running_app()
        DatabaseManager.record_transaction(
            app.current_user['id'],
            nom, prenom, telephone, cnib,
            operator, operation, amount
        )
        
        self.show_popup('Succès', 'Transaction enregistrée avec succès', 'SUCCESS')
        self.clear_form()
    
    def clear_form(self):
        """Vider le formulaire après enregistrement"""
        self.client_nom.text = ''
        self.client_prenom.text = ''
        self.client_telephone.text = ''
        self.client_cnib.text = ''
        self.operator.text = 'Sélectionnez le réseau'
        self.operation.text = 'Sélectionnez l\'opération'
        self.amount.text = ''
    
    def go_back(self, instance):
        self.manager.current = 'menu'
    
    def show_popup(self, title, message, message_type):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=message, 
                               color=COLORS[message_type]))
        
        btn_close = CustomButton(text='OK', size_hint_y=None, height=dp(40))
        popup = Popup(title=title,
                     content=content,
                     size_hint=(0.7, 0.4))
        
        btn_close.bind(on_press=popup.dismiss)
        content.add_widget(btn_close)
        popup.open()


class AgentStatsScreen(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        with self.canvas.before:
            Color(*COLORS['BACKGROUND'])
            self.rect = Rectangle(size=Window.size, pos=self.pos)  # Création d'abord
    
            self.bind(pos=self.update_rect, size=self.update_rect)
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Panneau à onglets
        tabs = TabbedPanel(do_default_tab=False)
        
        # Onglet Résumé
        summary_tab = TabbedPanelItem(text='Résumé')
        self.summary_content = self.create_summary_tab()
        summary_tab.add_widget(self.summary_content)
        tabs.add_widget(summary_tab)
        
        # Onglet Historique
        history_tab = TabbedPanelItem(text='Historique')
        self.history_content = self.create_history_tab()
        history_tab.add_widget(self.history_content)
        tabs.add_widget(history_tab)
        
        # Onglet Export
        export_tab = TabbedPanelItem(text='Export')
        self.export_content = self.create_export_tab()
        export_tab.add_widget(self.export_content)
        tabs.add_widget(export_tab)
        
        self.add_widget(tabs)
        
        # Bouton retour
        btn_back = CustomButton(text='RETOUR',
                              size_hint=(None, None),
                              size=(dp(100), dp(40)),
                              pos_hint={'right': 0.98, 'top': 0.98})
        btn_back.bind(on_press=self.go_back)
        self.add_widget(btn_back)
    
    def create_summary_tab(self):
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Titre
        title = Label(text='MES STATISTIQUES',
                     font_size='24sp',
                     bold=True,
                     color=COLORS['PRIMARY'],
                     size_hint_y=None,
                     height=dp(50))
        layout.add_widget(title)
        
        # ScrollView pour les statistiques
        scroll = ScrollView()
        stats_layout = BoxLayout(orientation='vertical', 
                                size_hint_y=None,
                                spacing=dp(15))
        stats_layout.bind(minimum_height=stats_layout.setter('height'))
        
        # Contenu des statistiques sera mis à jour dans on_enter
        self.stats_container = stats_layout
        
        scroll.add_widget(stats_layout)
        layout.add_widget(scroll)
        
        return layout
    
    def create_history_tab(self):
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Titre
        title = Label(text='HISTORIQUE DES TRANSACTIONS',
                     font_size='20sp',
                     bold=True,
                     color=COLORS['PRIMARY'],
                     size_hint_y=None,
                     height=dp(40))
        layout.add_widget(title)
        
        # ScrollView pour l'historique
        scroll = ScrollView()
        self.history_container = BoxLayout(orientation='vertical',
                                         size_hint_y=None,
                                         spacing=dp(5))
        self.history_container.bind(minimum_height=self.history_container.setter('height'))
        
        scroll.add_widget(self.history_container)
        layout.add_widget(scroll)
        
        return layout
    
    def create_export_tab(self):
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Titre
        title = Label(text='EXPORT DES DONNÉES',
                     font_size='20sp',
                     bold=True,
                     color=COLORS['PRIMARY'],
                     size_hint_y=None,
                     height=dp(40))
        layout.add_widget(title)
        
        # Instructions
        info = Label(text='Exportez vos transactions au format CSV ou Excel',
                    color=COLORS['TEXT'],
                    size_hint_y=None,
                    height=dp(30))
        layout.add_widget(info)
        
        # Boutons d'export
        btn_csv = CustomButton(text='EXPORTER EN CSV')
        btn_csv.bind(on_press=self.export_csv)
        layout.add_widget(btn_csv)
        
        btn_excel = CustomButton(text='EXPORTER EN EXCEL')
        btn_excel.bind(on_press=self.export_excel)
        layout.add_widget(btn_excel)
        
        # Espace vide
        layout.add_widget(Label())
        
        return layout
    
    def on_enter(self, *args):
        self.load_stats()
        self.load_history()
    
    def load_stats(self):
        app = App.get_running_app()
        agent_id = app.current_user['id']
        
        daily_stats, operator_stats, operation_stats, total_stats = DatabaseManager.get_agent_stats(agent_id)
        
        # Vider le conteneur
        self.stats_container.clear_widgets()
        
        # Statistiques générales
        general_box = BoxLayout(orientation='vertical',
                               size_hint=(1, None),
                               height=dp(120),
                               spacing=dp(10),
                               padding=dp(15))
        
        with general_box.canvas.before:
            Color(*COLORS['WHITE'])
            RoundedRectangle(size=general_box.size, pos=general_box.pos, radius=[dp(10),])
        
        general_box.add_widget(Label(text='STATISTIQUES GÉNÉRALES',
                                   font_size='16sp',
                                   bold=True,
                                   color=COLORS['PRIMARY'],
                                   size_hint_y=None,
                                   height=dp(30)))
        
        if total_stats:
            total_clients, total_amount = total_stats
            general_box.add_widget(Label(text=f'Total clients: {total_clients or 0}',
                                       color=COLORS['TEXT'],
                                       size_hint_y=None,
                                       height=dp(25)))
            general_box.add_widget(Label(text=f'Montant total: {total_amount or 0:,.0f} XOF',
                                       color=COLORS['TEXT'],
                                       size_hint_y=None,
                                       height=dp(25)))
        
        self.stats_container.add_widget(general_box)
        
        # Statistiques par réseau
        if operator_stats:
            operator_box = BoxLayout(orientation='vertical',
                                   size_hint=(1, None),
                                   height=dp(len(operator_stats) * 30 + 60),
                                   spacing=dp(5),
                                   padding=dp(15))
            
            with operator_box.canvas.before:
                Color(*COLORS['WHITE'])
                RoundedRectangle(size=operator_box.size, pos=operator_box.pos, radius=[dp(10),])
            
            operator_box.add_widget(Label(text='PAR RÉSEAU',
                                        font_size='16sp',
                                        bold=True,
                                        color=COLORS['PRIMARY'],
                                        size_hint_y=None,
                                        height=dp(30)))
            
            for operator, nb_clients, total_amount in operator_stats:
                operator_box.add_widget(Label(text=f'{operator}: {nb_clients} clients - {total_amount:,.0f} XOF',
                                            color=COLORS['TEXT'],
                                            size_hint_y=None,
                                            height=dp(25)))
            
            self.stats_container.add_widget(operator_box)
        
        # Statistiques par opération
        if operation_stats:
            operation_box = BoxLayout(orientation='vertical',
                                    size_hint=(1, None),
                                    height=dp(len(operation_stats) * 30 + 60),
                                    spacing=dp(5),
                                    padding=dp(15))
            
            with operation_box.canvas.before:
                Color(*COLORS['WHITE'])
                RoundedRectangle(size=operation_box.size, pos=operation_box.pos, radius=[dp(10),])
            
            operation_box.add_widget(Label(text='PAR OPÉRATION',
                                         font_size='16sp',
                                         bold=True,
                                         color=COLORS['PRIMARY'],
                                         size_hint_y=None,
                                         height=dp(30)))
            
            for operation, nb_clients, total_amount in operation_stats:
                operation_box.add_widget(Label(text=f'{operation}: {nb_clients} clients - {total_amount:,.0f} XOF',
                                             color=COLORS['TEXT'],
                                             size_hint_y=None,
                                             height=dp(25)))
            
            self.stats_container.add_widget(operation_box)
    
    def load_history(self):
        app = App.get_running_app()
        agent_id = app.current_user['id']
        
        transactions = DatabaseManager.get_transactions_by_agent(agent_id)
        
        # Vider le conteneur
        self.history_container.clear_widgets()
        
        if not transactions:
            no_data = Label(text='Aucune transaction enregistrée',
                          color=COLORS['TEXT'],
                          size_hint_y=None,
                          height=dp(50))
            self.history_container.add_widget(no_data)
            return
        
        for transaction in transactions:
            client_nom, client_prenom, client_telephone, client_cnib, operator, operation, amount, timestamp = transaction
            
            trans_box = BoxLayout(orientation='vertical',
                                size_hint=(1, None),
                                height=dp(120),
                                spacing=dp(5),
                                padding=dp(10))
            
            with trans_box.canvas.before:
                Color(*COLORS['WHITE'])
                RoundedRectangle(size=trans_box.size, pos=trans_box.pos, radius=[dp(8),])
            
            # Ligne 1: Client et montant
            line1 = BoxLayout(size_hint_y=None, height=dp(25))
            line1.add_widget(Label(text=f'{client_prenom} {client_nom}',
                                 color=COLORS['PRIMARY'],
                                 bold=True,
                                 text_size=(None, None),
                                 halign='left'))
            line1.add_widget(Label(text=f'{amount:,.0f} XOF',
                                 color=COLORS['SECONDARY'],
                                 bold=True,
                                 text_size=(None, None),
                                 halign='right'))
            trans_box.add_widget(line1)
            
            # Ligne 2: Téléphone et CNIB
            line2 = BoxLayout(size_hint_y=None, height=dp(20))
            line2.add_widget(Label(text=f'Tél: {client_telephone}',
                                 color=COLORS['TEXT'],
                                 font_size='12sp',
                                 text_size=(None, None),
                                 halign='left'))
            line2.add_widget(Label(text=f'CNIB: {client_cnib}',
                                 color=COLORS['TEXT'],
                                 font_size='12sp',
                                 text_size=(None, None),
                                 halign='right'))
            trans_box.add_widget(line2)
            
            # Ligne 3: Réseau et opération
            line3 = BoxLayout(size_hint_y=None, height=dp(20))
            line3.add_widget(Label(text=f'{operator} - {operation}',
                                 color=COLORS['TEXT'],
                                 font_size='12sp',
                                 text_size=(None, None),
                                 halign='left'))
            line3.add_widget(Label(text=timestamp,
                                 color=COLORS['TEXT'],
                                 font_size='12sp',
                                 text_size=(None, None),
                                 halign='right'))
            trans_box.add_widget(line3)
            
            self.history_container.add_widget(trans_box)
    
    def export_csv(self, instance):
        app = App.get_running_app()
        agent_id = app.current_user['id']
        
        try:
            filename = DatabaseManager.export_to_csv(agent_id)
            self.show_popup('Succès', f'Export CSV réussi: {filename}', 'SUCCESS')
        except Exception as e:
            self.show_popup('Erreur', f'Erreur lors de l\'export: {str(e)}', 'ERROR')
    
    def export_excel(self, instance):
        app = App.get_running_app()
        agent_id = app.current_user['id']
        
        try:
            filename = DatabaseManager.export_to_xlsx(agent_id)
            self.show_popup('Succès', f'Export Excel réussi: {filename}', 'SUCCESS')
        except Exception as e:
            self.show_popup('Erreur', f'Erreur lors de l\'export: {str(e)}', 'ERROR')
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def go_back(self, instance):
        self.manager.current = 'menu'
    
    def show_popup(self, title, message, message_type):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=message, 
                               color=COLORS[message_type]))
        
        btn_close = CustomButton(text='OK', size_hint_y=None, height=dp(40))
        popup = Popup(title=title,
                     content=content,
                     size_hint=(0.7, 0.4))
        
        btn_close.bind(on_press=popup.dismiss)
        content.add_widget(btn_close)
        popup.open()


class AdminMenuScreen(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        with self.canvas.before:
            Color(*COLORS['BACKGROUND'])
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        
        # Titre
        title = Label(text='MENU ADMINISTRATEUR',
                     font_size='28sp',
                     bold=True,
                     color=COLORS['PRIMARY'],
                     size_hint_y=None,
                     height=dp(60))
        layout.add_widget(title)
        
        # Boutons
        buttons = [
            ('GÉRER LES AGENTS', self.go_to_agents),
            ('STATISTIQUES GLOBALES', self.go_to_global_stats),
            ('EXPORT GLOBAL', self.go_to_global_export),
            ('DÉCONNEXION', self.logout)
        ]
        
        for text, callback in buttons:
            btn = CustomButton(text=text)
            btn.bind(on_press=callback)
            layout.add_widget(btn)
        
        self.add_widget(layout)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def go_to_agents(self, instance):
        self.manager.current = 'manage_agents'
    
    def go_to_global_stats(self, instance):
        self.manager.current = 'global_stats'
    
    def go_to_global_export(self, instance):
        self.manager.current = 'global_export'
    
    def logout(self, instance):
        App.get_running_app().current_user = None
        self.manager.current = 'login'


class ManageAgentsScreen(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        with self.canvas.before:
            Color(*COLORS['BACKGROUND'])
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Titre
        title = Label(text='GESTION DES AGENTS',
                     font_size='24sp',
                     bold=True,
                     color=COLORS['PRIMARY'],
                     size_hint_y=None,
                     height=dp(50))
        layout.add_widget(title)
        
        # Formulaire d'ajout d'agent
        form = BoxLayout(orientation='vertical',
                        size_hint=(1, None),
                        height=dp(200),
                        spacing=dp(10),
                        padding=dp(20))
        
        with form.canvas.before:
            Color(*COLORS['WHITE'])
            RoundedRectangle(size=form.size, pos=form.pos, radius=[dp(15),])
        
        form.add_widget(Label(text='AJOUTER UN NOUVEL AGENT',
                            font_size='16sp',
                            bold=True,
                            color=COLORS['PRIMARY'],
                            size_hint_y=None,
                            height=dp(30)))
        
        # Nom d'utilisateur
        form.add_widget(Label(text='Nom d\'utilisateur:',
                            color=COLORS['TEXT'],
                            size_hint_y=None,
                            height=dp(25)))
        self.new_username = CustomTextInput(hint_text='Nom d\'utilisateur')
        form.add_widget(self.new_username)
        
        # Mot de passe
        form.add_widget(Label(text='Mot de passe:',
                            color=COLORS['TEXT'],
                            size_hint_y=None,
                            height=dp(25)))
        self.new_password = CustomTextInput(hint_text='Mot de passe',
                                          password=True)
        form.add_widget(self.new_password)
        
        # Bouton ajouter
        btn_add = CustomButton(text='AJOUTER AGENT',
                             size_hint_y=None,
                             height=dp(40))
        btn_add.bind(on_press=self.add_agent)
        form.add_widget(btn_add)
        
        layout.add_widget(form)
        
        # Liste des agents
        agents_label = Label(text='LISTE DES AGENTS',
                           font_size='16sp',
                           bold=True,
                           color=COLORS['PRIMARY'],
                           size_hint_y=None,
                           height=dp(30))
        layout.add_widget(agents_label)
        
        # ScrollView pour la liste des agents
        scroll = ScrollView()
        self.agents_container = BoxLayout(orientation='vertical',
                                        size_hint_y=None,
                                        spacing=dp(5))
        self.agents_container.bind(minimum_height=self.agents_container.setter('height'))
        
        scroll.add_widget(self.agents_container)
        layout.add_widget(scroll)
        
        # Bouton retour
        btn_back = CustomButton(text='RETOUR',
                              background_color_custom=COLORS['SECONDARY'],
                              size_hint_y=None,
                              height=dp(50))
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)
        
        self.add_widget(layout)
    
    def on_enter(self, *args):
        self.load_agents()
    
    def load_agents(self):
        agents = DatabaseManager.get_all_agents()
        
        # Vider le conteneur
        self.agents_container.clear_widgets()
        
        if not agents:
            no_agents = Label(text='Aucun agent enregistré',
                            color=COLORS['TEXT'],
                            size_hint_y=None,
                            height=dp(50))
            self.agents_container.add_widget(no_agents)
            return
        
        for agent_id, username in agents:
            agent_box = BoxLayout(orientation='horizontal',
                                size_hint=(1, None),
                                height=dp(50),
                                spacing=dp(10),
                                padding=dp(10))
            
            with agent_box.canvas.before:
                Color(*COLORS['WHITE'])
                RoundedRectangle(size=agent_box.size, pos=agent_box.pos, radius=[dp(8),])
            
            agent_box.add_widget(Label(text=f'Agent: {username}',
                                     color=COLORS['TEXT'],
                                     text_size=(None, None),
                                     halign='left'))
            
            self.agents_container.add_widget(agent_box)
    
    def add_agent(self, instance):
        username = self.new_username.text.strip()
        password = self.new_password.text.strip()
        
        if not username or not password:
            self.show_popup('Erreur', 'Veuillez remplir tous les champs', 'ERROR')
            return
        
        if len(password) < 4:
            self.show_popup('Erreur', 'Le mot de passe doit contenir au moins 4 caractères', 'ERROR')
            return
        
        if DatabaseManager.add_user(username, password, 'agent'):
            self.show_popup('Succès', 'Agent ajouté avec succès', 'SUCCESS')
            self.new_username.text = ''
            self.new_password.text = ''
            self.load_agents()
        else:
            self.show_popup('Erreur', 'Ce nom d\'utilisateur existe déjà', 'ERROR')
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def go_back(self, instance):
        self.manager.current = 'admin_menu'
    
    def show_popup(self, title, message, message_type):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=message, 
                               color=COLORS[message_type]))
        
        btn_close = CustomButton(text='OK', size_hint_y=None, height=dp(40))
        popup = Popup(title=title,
                     content=content,
                     size_hint=(0.7, 0.4))
        
        btn_close.bind(on_press=popup.dismiss)
        content.add_widget(btn_close)
        popup.open()


class GlobalStatsScreen(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        with self.canvas.before:
            Color(*COLORS['BACKGROUND'])
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Titre
        title = Label(text='STATISTIQUES GLOBALES',
                     font_size='24sp',
                     bold=True,
                     color=COLORS['PRIMARY'],
                     size_hint_y=None,
                     height=dp(50))
        layout.add_widget(title)
        
        # ScrollView pour les statistiques
        scroll = ScrollView()
        self.stats_container = BoxLayout(orientation='vertical',
                                       size_hint_y=None,
                                       spacing=dp(15))
        self.stats_container.bind(minimum_height=self.stats_container.setter('height'))
        
        scroll.add_widget(self.stats_container)
        layout.add_widget(scroll)
        
        # Bouton retour
        btn_back = CustomButton(text='RETOUR',
                              background_color_custom=COLORS['SECONDARY'],
                              size_hint_y=None,
                              height=dp(50))
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)
        
        self.add_widget(layout)
    
    def on_enter(self, *args):
        self.load_global_stats()
    
    def load_global_stats(self):
        stats = DatabaseManager.get_global_stats()
        
        # Vider le conteneur
        self.stats_container.clear_widgets()
        
        # Statistiques générales
        if stats['total']:
            total_clients, total_amount = stats['total']
            
            general_box = BoxLayout(orientation='vertical',
                                   size_hint=(1, None),
                                   height=dp(100),
                                   spacing=dp(5),
                                   padding=dp(15))
            
            with general_box.canvas.before:
                Color(*COLORS['WHITE'])
                RoundedRectangle(size=general_box.size, pos=general_box.pos, radius=[dp(10),])
            
            general_box.add_widget(Label(text='STATISTIQUES GÉNÉRALES',
                                       font_size='16sp',
                                       bold=True,
                                       color=COLORS['PRIMARY'],
                                       size_hint_y=None,
                                       height=dp(30)))
            
            general_box.add_widget(Label(text=f'Total clients: {total_clients or 0}',
                                       color=COLORS['TEXT'],
                                       size_hint_y=None,
                                       height=dp(25)))
            
            general_box.add_widget(Label(text=f'Montant total: {total_amount or 0:,.0f} XOF',
                                       color=COLORS['TEXT'],
                                       size_hint_y=None,
                                       height=dp(25)))
            
            self.stats_container.add_widget(general_box)
        
        # Statistiques par agent
        if stats['by_agent']:
            agents_box = BoxLayout(orientation='vertical',
                                 size_hint=(1, None),
                                 height=dp(len(stats['by_agent']) * 30 + 60),
                                 spacing=dp(5),
                                 padding=dp(15))
            
            with agents_box.canvas.before:
                Color(*COLORS['WHITE'])
                RoundedRectangle(size=agents_box.size, pos=agents_box.pos, radius=[dp(10),])
            
            agents_box.add_widget(Label(text='PAR AGENT',
                                      font_size='16sp',
                                      bold=True,
                                      color=COLORS['PRIMARY'],
                                      size_hint_y=None,
                                      height=dp(30)))
            
            for username, nb_clients, total_amount in stats['by_agent']:
                agents_box.add_widget(Label(text=f'{username}: {nb_clients} clients - {total_amount:,.0f} XOF',
                                          color=COLORS['TEXT'],
                                          size_hint_y=None,
                                          height=dp(25)))
            
            self.stats_container.add_widget(agents_box)
        
        # Statistiques par réseau
        if stats['by_operator']:
            operators_box = BoxLayout(orientation='vertical',
                                    size_hint=(1, None),
                                    height=dp(len(stats['by_operator']) * 30 + 60),
                                    spacing=dp(5),
                                    padding=dp(15))
            
            with operators_box.canvas.before:
                Color(*COLORS['WHITE'])
                RoundedRectangle(size=operators_box.size, pos=operators_box.pos, radius=[dp(10),])
            
            operators_box.add_widget(Label(text='PAR RÉSEAU',
                                         font_size='16sp',
                                         bold=True,
                                         color=COLORS['PRIMARY'],
                                         size_hint_y=None,
                                         height=dp(30)))
            
            for operator, nb_clients, total_amount in stats['by_operator']:
                operators_box.add_widget(Label(text=f'{operator}: {nb_clients} clients - {total_amount:,.0f} XOF',
                                             color=COLORS['TEXT'],
                                             size_hint_y=None,
                                             height=dp(25)))
            
            self.stats_container.add_widget(operators_box)
        
        # Statistiques par opération
        if stats['by_operation']:
            operations_box = BoxLayout(orientation='vertical',
                                     size_hint=(1, None),
                                     height=dp(len(stats['by_operation']) * 30 + 60),
                                     spacing=dp(5),
                                     padding=dp(15))
            
            with operations_box.canvas.before:
                Color(*COLORS['WHITE'])
                RoundedRectangle(size=operations_box.size, pos=operations_box.pos, radius=[dp(10),])
            
            operations_box.add_widget(Label(text='PAR OPÉRATION',
                                          font_size='16sp',
                                          bold=True,
                                          color=COLORS['PRIMARY'],
                                          size_hint_y=None,
                                          height=dp(30)))
            
            for operation, nb_clients, total_amount in stats['by_operation']:
                operations_box.add_widget(Label(text=f'{operation}: {nb_clients} clients - {total_amount:,.0f} XOF',
                                              color=COLORS['TEXT'],
                                              size_hint_y=None,
                                              height=dp(25)))
            
            self.stats_container.add_widget(operations_box)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def go_back(self, instance):
        self.manager.current = 'admin_menu'


class GlobalExportScreen(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        with self.canvas.before:
            Color(*COLORS['BACKGROUND'])
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        layout = BoxLayout
        class GlobalExportScreen(Screen):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.setup_ui()
    
    def setup_ui(self):
        with self.canvas.before:
            Color(*COLORS['BACKGROUND'])
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Titre
        title = Label(text='EXPORT GLOBAL',
                     font_size='24sp',
                     bold=True,
                     color=COLORS['PRIMARY'],
                     size_hint_y=None,
                     height=dp(50))
        layout.add_widget(title)
        
        # Instructions
        info = Label(text='Exportez toutes les transactions au format CSV ou Excel',
                    color=COLORS['TEXT'],
                    size_hint_y=None,
                    height=dp(30))
        layout.add_widget(info)
        
        # Boutons d'export
        btn_csv = CustomButton(text='EXPORTER EN CSV')
        btn_csv.bind(on_press=self.export_csv)
        layout.add_widget(btn_csv)
        
        btn_excel = CustomButton(text='EXPORTER EN EXCEL')
        btn_excel.bind(on_press=self.export_excel)
        layout.add_widget(btn_excel)
        
        # Bouton retour
        btn_back = CustomButton(text='RETOUR',
                              background_color_custom=COLORS['SECONDARY'],
                              size_hint_y=None,
                              height=dp(50))
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)
        
        self.add_widget(layout)
    
    def export_csv(self, instance):
        try:
            filename = DatabaseManager.export_to_csv()
            self.show_popup('Succès', f'Export CSV réussi: {filename}', 'SUCCESS')
        except Exception as e:
            self.show_popup('Erreur', f'Erreur lors de l\'export: {str(e)}', 'ERROR')
    
    def export_excel(self, instance):
        try:
            filename = DatabaseManager.export_to_xlsx()
            self.show_popup('Succès', f'Export Excel réussi: {filename}', 'SUCCESS')
        except Exception as e:
            self.show_popup('Erreur', f'Erreur lors de l\'export: {str(e)}', 'ERROR')
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def go_back(self, instance):
        self.manager.current = 'admin_menu'
    
    def show_popup(self, title, message, message_type):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=message, 
                               color=COLORS[message_type]))
        
        btn_close = CustomButton(text='OK', size_hint_y=None, height=dp(40))
        popup = Popup(title=title,
                     content=content,
                     size_hint=(0.7, 0.4))
        
        btn_close.bind(on_press=popup.dismiss)
        content.add_widget(btn_close)
        popup.open()


# =============================================================================
# APPLICATION PRINCIPALE
# =============================================================================

class MobileMoneyApp(App):
    
    def build(self):
        # Initialiser la base de données
        DatabaseManager.init_database()
        
        # Créer le gestionnaire d'écrans
        sm = ScreenManager()
        
        # Ajouter les écrans
        screens = [
            LoginScreen(name='login'),
            MenuScreen(name='menu'),
            TransactionScreen(name='transaction'),
            AgentStatsScreen(name='agent_stats'),
            AdminMenuScreen(name='admin_menu'),
            ManageAgentsScreen(name='manage_agents'),
            GlobalStatsScreen(name='global_stats'),
            GlobalExportScreen(name='global_export')
        ]
        
        for screen in screens:
            sm.add_widget(screen)
        
        return sm
    
    def export_data(self):
        if platform == 'android':
            downloads_dir = storagepath.get_downloads_dir()
        else:
            downloads_dir = os.path.expanduser("~")


if __name__ == '__main__':
    MobileMoneyApp().run()