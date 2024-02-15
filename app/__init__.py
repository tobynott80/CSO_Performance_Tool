from flask import Flask


app = Flask(__name__)


# Load configuration from your config.py
app.config.from_object("config.DevelopmentConfig")

# Import any DB stuff here when needed


# Import routes after initializing app to avoid circular dependencies
from app import routes
