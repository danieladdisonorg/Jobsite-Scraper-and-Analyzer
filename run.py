import os
import dotenv

from web_server import init_app
from web_server.config import config_dict

dotenv.load_dotenv()

# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv("DEBUG", "False") == "True")

# The configuration
config_mode = "debug" if DEBUG else "production"
app = init_app(config_dict[config_mode])


if __name__ == "__main__":
    app.run()
