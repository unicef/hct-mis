import logging

from django.contrib.auth import get_user_model
from social_core.exceptions import InvalidEmail
from social_core.pipeline import social_auth
from social_core.pipeline import user as social_core_user

from account.microsoft_graph import MicrosoftGraphAPI
from account.models import UserRole, Role, ACTIVE
from core.models import BusinessArea

logger = logging.getLogger("console")


def social_details(backend, details, response, *args, **kwargs):
    logger.debug(f"social_details response:\n{response}")
    logger.debug(f"user_data:\n{backend.user_data(None, response=response)}")
    r = social_auth.social_details(backend, details, response, *args, **kwargs)

    if not r["details"].get("email"):
        user_data = backend.user_data(None, response=response) or {}
        r["details"]["email"] = user_data.get("email", user_data.get("signInNames.emailAddress"))

    r["details"]["idp"] = response.get("idp", "")
    return r


def user_details(strategy, details, backend, user=None, *args, **kwargs):
    logger.debug(f"user_details for user {user} details:\n{details}")
    if user:
        user.first_name = details.get("first_name")
        user.last_name = details.get("last_name")
        user.username = details["email"]
        user.status = ACTIVE
        user.save()

    return social_core_user.user_details(strategy, details, backend, user, *args, **kwargs)


def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    if user and user.email:
        return
    elif is_new and not details.get("email"):
        raise InvalidEmail(strategy)


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {"is_new": False}

    fullname = details["fullname"].split(" ")

    user = get_user_model().objects.create(
        email=details["email"],
        username=details["email"],
        first_name=details.get("first_name"),
        last_name=details.get("last_name"),
        status=ACTIVE,
    )
    ms_graph = MicrosoftGraphAPI()
    user_data = ms_graph.get_user_data(details["email"])
    business_area_code = user_data.get("extension_f4805b4021f643d0aa596e1367d432f1_unicefBusinessAreaCode")

    user.set_unusable_password()
    user.save()
    if business_area_code:
        basic_user_role = UserRole()
        basic_user_role.role = Role.objects.filter(name="Basic").first()
        basic_user_role.business_area = BusinessArea.objects.get(code=business_area_code)
        basic_user_role.user = user
        basic_user_role.save()

    return {"is_new": True, "user": user}
