from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 
from flask_login import LoginManager


app = Flask(__name__,
    template_folder="../templates",
    static_folder="../static"
    )
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:tahauchiha1717@localhost/shopnest'
app.config['SECRET_KEY']='7f590dae42a606b1adf503c4'
db=SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager=LoginManager(app)

from shop import routes
from shop import models



