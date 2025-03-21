from flask_swagger_ui import get_swaggerui_blueprint

from src import create_app

app = create_app()

SWAGGER_URL = "/docs"
API_URL = "/static/swagger.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "CRM Tool"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
