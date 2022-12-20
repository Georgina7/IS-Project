import pyrebase

config = {
    'apiKey': "AIzaSyDun9D8j0McAzdocexs28MSVPJ4TwYnnEM",
    'authDomain': "is-project-d3db4.firebaseapp.com",
    'projectId': "is-project-d3db4",
    'storageBucket': "is-project-d3db4.appspot.com",
    'messagingSenderId': "101040743578",
    'appId': "1:101040743578:web:ee6a4164ab9321eb0b6b23",
    'measurementId': "G-6DH7ZZZ11R",
    'databaseURL': ""
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

email = 'test@gmail.com'
password = '123456'

# user = auth.create_user_with_email_and_password(email, password)
# print(user)

user = auth.sign_in_with_email_and_password(email, password)
# info = auth.get_account_info(user['idToken'])
# print(info)

# auth.send_email_verification(user['idToken'])
# auth.send_password_reset_email(user['idToken'])