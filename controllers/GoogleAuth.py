import sys
import google.auth.transport.requests
import os
from controllers.Tools import Tools
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google.oauth2.id_token
from controllers.Tools import Tools
from plyer import notification

class GoogleAuth:
    
    
    userEmail= ''
    userName= ''

    CLIENT_SECRETS_FILE = Tools.get_resource_path("config/client_secrets.json")

    CREDENTIALS = Tools.get_resource_path("config/credentials.json")

    SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile']

    def __init__(self):

        self.credentials_file = self.CREDENTIALS
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.gc = None

       

    def authenticate(self):        
        
        creds = None
        
        

        # Vérifiez si les informations d'identification existent déjà
        if os.path.exists('temp/token.json'):
            creds = Credentials.from_authorized_user_file('temp/token.json', self.SCOPES)

        # Si aucune information d'identification valide n'existe, effectuez le flux OAuth 2.0
        if not creds or not creds.valid:
            
            notification.notify(
                title = "Authentification Google",
                message = "Veuillez vous rendre sur votre navigateur",
                timeout = 5,
                app_name="Badgeuse la plateforme", 
                app_icon=Tools.get_resource_path("assets/logo_laplateforme_icon.ico"),                
            )
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(google.auth.transport.requests.Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CLIENT_SECRETS_FILE, self.SCOPES)
                creds = flow.run_local_server(port=8080) 
                

            if not os.path.exists('temp'):
                os.makedirs('temp')    

            # Enregistrez les informations d'identification pour les réutiliser ultérieurement
            with open('temp/token.json', 'w') as token:
                token.write(creds.to_json())
        
                
        user_info_service = build('oauth2', 'v2', credentials=creds)
        user_info = user_info_service.userinfo().get().execute()
        creds.user_name = user_info['name']    
        creds.user_email = user_info['email']    
        self.userName = user_info['email']
        self.userEmail = user_info['name']
        Tools.write_in_file("temp/token_google_id", creds.id_token)        
       

        return creds    
