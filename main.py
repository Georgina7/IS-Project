from flask import Flask, render_template
# from firebase import firebase
# firebase = firebase.FirebaseApplication('https://is-project-d3db4.firebaseio.com', None)

app = Flask(__name__)

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/sign_up")
def sign_up():
    return render_template("sign_up.html")

@app.route("/landing")
def landing():
    return render_template("landing.html")

@app.route("/organ_contouring")
def organ_contouring():
    return render_template("organ_contouring.html")
    
if __name__ == "__main__":
    app.run(debug=True)