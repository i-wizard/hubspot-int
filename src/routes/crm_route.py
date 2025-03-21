from flask import Blueprint, request, jsonify

from src.schemas.contact_schema import ContactSchema
from src.schemas.deal_schema import DealSchema
from src.schemas.ticket_schema import TicketSchema
from src.services.crm_service import CrmService
from src.utils.validators import validate_request


def create_crm_routes(crm_service: CrmService):
    bp = Blueprint("crm", __name__)

    @bp.route("/contacts", methods=["POST"])
    @validate_request(ContactSchema)
    def create_or_update_contact(data: ContactSchema):
        result = crm_service.create_or_update_contact(data)
        return jsonify(result), 200

    @bp.route("/deals", methods=["POST"])
    @validate_request(DealSchema)
    def create_or_update_deal(data: DealSchema):
        result = crm_service.create_or_update_deal(data)
        return jsonify(result), 200

    @bp.route("/tickets", methods=["POST"])
    @validate_request(TicketSchema)
    def create_ticket(data: TicketSchema):
        result = crm_service.create_ticket(data)
        return jsonify(result), 200

    @bp.route("/objects", methods=["GET"])
    def get_new_crm_objects():
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", 10))
        start_date_str = request.args.get("start_date", default="", type=str)
        result = crm_service.get_new_crm_objects(
            page, size, start_date_str=start_date_str
        )
        return jsonify(result), 200

    return bp
