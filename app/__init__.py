from quart import Quart, session
from app.routes.api.location import location_blueprint
from app.routes.api.run import run_blueprint
from threading import Thread

# Import any DB stuff here when needed
# db = Prisma()
# db.connect()
# register(db)

app = Quart(__name__)

# Global thread tracker- Key: Run/Thread ID Value: Progress 0-100
app.thread_tracker = {}

# App thread object
app.thread = Thread


# Load configuration from your config.py
app.config.from_object("config.DevelopmentConfig")
app.secret_key = "7ec9428e6d245eb89afd19dc82d30f1cb9b74ecddf02eae87bf05f38effc07ed"

app.register_blueprint(location_blueprint, url_prefix="/api/location")
app.register_blueprint(run_blueprint, url_prefix="/api/run")

# Import routes after initializing app to avoid circular dependencies
from app.routes import routes
