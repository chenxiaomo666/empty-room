
from flask import Flask
from .config import Config
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
db = SQLAlchemy()
# config
app.config.from_object(Config)

# init ext
db.init_app(app)
from .models import init_model
init_model()

with app.app_context():
    from .views import user_view
    app.register_blueprint(user_view, url_prefix="/cxm")

