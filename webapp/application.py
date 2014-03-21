import hashlib
import os
from flask import Flask, render_template, redirect, request, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename

from wsc.Configuration import Configuration
from wsc.iam import IAM
from wsc.exc import InvalidCredentials
from wsc.repo import BalanceRepository, DocumentRepository

app = Flask(__name__)
app.config.from_object('config')

from security import UserAndSession

login_manager = LoginManager()
login_manager.init_app(app)

wsc_config = Configuration()
wsc_config.iam_endpoint = app.config['WS_IAM_ENDPOINT']
wsc_config.invoicing_endpoint = app.config['WS_INVOICING_ENDPOINT']
wsc_config.docs_endpoint = app.config['WS_DOCS_ENDPOINT']


@login_manager.user_loader
def load_user_and_session(user_session_id):
    return UserAndSession.from_id(str(user_session_id))


@app.route('/', methods=['GET'])
def index_action():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def login_action():
    username = request.form['username']
    password = request.form['password']

    iam = IAM(wsc_config)
    try:
        # Open a WS session
        wsc_session = iam.login(username, hashlib.sha1(password).hexdigest())

        # Store session data via flask-login
        login_user(UserAndSession(wsc_session.user_id, wsc_session.session_id))

        return redirect('/home')

    except InvalidCredentials:
        flash('Nom d\'utilisateur ou mot de passe invalide.', 'danger')
        return render_template('index.html')


@app.route('/logout')
def logout_action():
    # Close the WS session
    iam = IAM(wsc_config)
    iam.logout(current_user.get_wsc_session())

    logout_user()
    return redirect('/')


@app.route('/home')
@login_required
def home_action():
    # Retrieve balance
    repo = BalanceRepository(wsc_config, current_user.get_wsc_session())
    balance = repo.get(current_user.user_id)

    return render_template('main.html', balance=balance)


@app.route('/upload', methods=['POST'])
@login_required
def upload_action():
    # Save file to a temporary location
    uploaded_file = request.files['file']
    tmp_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(uploaded_file.filename))
    uploaded_file.save(tmp_path)

    # Post to Docs WS
    repo = DocumentRepository(wsc_config, current_user.get_wsc_session())
    repo.upload(request.form['filename'], tmp_path)

    return redirect('/home')


if __name__ == '__main__':
    app.run(port=app.config['PORT'], debug=True)