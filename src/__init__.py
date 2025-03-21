from flask import Flask

from src.config import Config
from src.utils.error_handlers import register_error_handlers


def create_app():

    app = Flask(__name__)
    with app.app_context():
        from src.factories.repository_factory import RepositoryFactory
        from src.routes.crm_route import create_crm_routes
        from src.services.crm_service import CrmService
        repo = RepositoryFactory.get_provider(Config.REPOSITORY)
        service = CrmService(repo)

        hubspot_bp = create_crm_routes(service)
        app.register_blueprint(hubspot_bp, url_prefix="/api/v1/crm")
        register_error_handlers(app)
    return app
