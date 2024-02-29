from flask import Flask
from prisma import Prisma, register
from app.routes.api.location import location_blueprint
from app.routes.api.run import run_blueprint

# Import any DB stuff here when needed
db = Prisma()
db.connect()
register(db)

app = Flask(__name__)

# Load configuration from your config.py
app.config.from_object("config.DevelopmentConfig")

app.register_blueprint(location_blueprint, url_prefix="/api/location")
app.register_blueprint(run_blueprint, url_prefix="/api/run")

# Import routes after initializing app to avoid circular dependencies
from app.routes import routes
