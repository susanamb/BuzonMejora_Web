import pyrebase
config = {
    'apiKey': "AIzaSyBcJgd_BGJEBdtMO0RV_CWPE4DjVzNovtM",
    'authDomain': "buzonmejorafca.firebaseapp.com",
    'databaseURL': "https://buzonmejorafca-default-rtdb.firebaseio.com",
    'projectId': "buzonmejorafca",
    'storageBucket': "buzonmejorafca.appspot.com",
    'messagingSenderId': "912894005839",
    'appId': "1:912894005839:web:066b90363fd8ef90fdd03a",
    'measurementId': "G-YR53F6TZMS"
  }

firebase = pyrebase.initialize_app(config)