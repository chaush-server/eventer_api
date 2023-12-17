"""API blueprint configuration."""
from flask import Blueprint
from flask_restx import Api

from .mock_data import namespace as mock_data_ns
from .auth import namespace as auth_ns
from .booking import namespace as booking_ns
from .category import namespace as category_ns
from .city import namespace as city_ns
from .country import namespace as country_ns
from .event import namespace as event_ns
from .event_dates import namespace as event_dates_ns
from .event_donation import namespace as event_donation_ns
from .favourite_organizer import namespace as favourite_organizer_ns
from .feedback import namespace as feedback_ns
from .genre import namespace as genre_ns
from .organizer import namespace as organizer_ns
from .state import namespace as state_ns
from .ticket import namespace as ticket_ns
from .user import namespace as user_ns
from .venue import namespace as venue_ns

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")
authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(
    api_bp,
    title='Eventer',
    version='1.0',
    description='Rest API Eventer',
    authorizations=authorizations,
)

api.add_namespace(mock_data_ns, path="/mock_data")
api.add_namespace(auth_ns, path="/auth")
api.add_namespace(user_ns, path="/user")
api.add_namespace(organizer_ns, path="/organizer")
api.add_namespace(event_ns, path="/event")
api.add_namespace(category_ns, path="/category")
api.add_namespace(genre_ns, path="/genre")
api.add_namespace(booking_ns, path="/booking")
api.add_namespace(ticket_ns, path="/ticket")
api.add_namespace(country_ns, path="/country")
api.add_namespace(state_ns, path="/state")
api.add_namespace(city_ns, path="/city")
api.add_namespace(venue_ns, path="/venue")
api.add_namespace(event_dates_ns, path="/event_dates")
api.add_namespace(event_donation_ns, path="/event_donation")
api.add_namespace(feedback_ns, path="/feedback")
api.add_namespace(favourite_organizer_ns, path="/favourite_organizer")


