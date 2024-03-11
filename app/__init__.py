from quart import Quart, session

# Import any DB stuff here when needed
# db = Prisma()
# db.connect()
# register(db)

app = Quart(__name__)


# Load configuration from your config.py
app.config.from_object("config.DevelopmentConfig")
app.secret_key = "7ec9428e6d245eb89afd19dc82d30f1cb9b74ecddf02eae87bf05f38effc07ed"

# Import routes after initializing app to avoid circular dependencies
from app.routes import routes
from app.routes.api.location import location_blueprint
from app.routes.api.run import run_blueprint
app.register_blueprint(location_blueprint, url_prefix="/api/location")
app.register_blueprint(run_blueprint, url_prefix="/api/run")
