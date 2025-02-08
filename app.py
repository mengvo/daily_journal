from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

from models import db, User
from routes import main_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=False)