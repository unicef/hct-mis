from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.household.models import RELATIONSHIP_UNKNOWN


def handle_role(role, household, individual):
    from hct_mis_api.apps.household.models import ROLE_PRIMARY, ROLE_ALTERNATE, IndividualRoleInHousehold

    if role in (ROLE_PRIMARY, ROLE_ALTERNATE) and household:
        already_existing_role = IndividualRoleInHousehold.objects.filter(household=household, role=role).first()
        if already_existing_role:
            already_existing_role.individual = individual
            already_existing_role.save()
        else:
            IndividualRoleInHousehold.objects.create(individual=individual, household=household, role=role)


def handle_add_document(document, individual):
    from django_countries.fields import Country
    from graphql import GraphQLError
    from hct_mis_api.apps.household.models import DocumentType, Document

    type_name = document.get("type")
    country_code = document.get("country")
    country = Country(country_code)
    number = document.get("number")
    document_type = DocumentType.objects.get(country=country, type=type_name)

    document_already_exists = Document.objects.filter(document_number=number, type=document_type).exists()
    if document_already_exists:
        raise GraphQLError(f"Document with number {number} of type {type_name} for country {country} already exist")

    return Document(document_number=number, individual=individual, type=document_type)


def prepare_previous_documents(documents_to_remove_with_approve_status):
    from django.shortcuts import get_object_or_404
    from hct_mis_api.apps.core.utils import decode_id_string, encode_id_base64
    from hct_mis_api.apps.household.models import Document

    previous_documents = {}
    for document_data in documents_to_remove_with_approve_status:

        document_id = decode_id_string(document_data.get("value"))
        document = get_object_or_404(Document, id=document_id)
        previous_documents[encode_id_base64(document.id, "Document")] = {
            "id": encode_id_base64(document.id, "Document"),
            "document_number": document.document_number,
            "individual": encode_id_base64(document.individual.id, "Individual"),
            "label": document.type.label,
            "country": document.type.country.alpha3,
        }

    return previous_documents


def verify_required_arguments(input_data, field_name, options):
    from graphql import GraphQLError
    from hct_mis_api.apps.core.utils import nested_dict_get

    for key, value in options.items():
        if key != input_data.get(field_name):
            continue
        for required in value.get("required"):
            if nested_dict_get(input_data, required) is None:
                raise GraphQLError(f"You have to provide {required} in {key}")
        for not_allowed in value.get("not_allowed"):
            if nested_dict_get(input_data, not_allowed) is not None:
                raise GraphQLError(f"You can't provide {not_allowed} in {key}")


def remove_parsed_data_fields(data_dict, fields_list):
    for field in fields_list:
        data_dict.pop(field, None)


def verify_flex_fields(flex_fields_to_verify, associated_with):
    from hct_mis_api.apps.core.core_fields_attributes import (
        FIELD_TYPES_TO_INTERNAL_TYPE,
        TYPE_SELECT_ONE,
        TYPE_SELECT_MANY,
    )
    from hct_mis_api.apps.core.utils import serialize_flex_attributes

    if associated_with not in ("households", "individuals"):
        raise ValueError("associated_with argument must be one of ['household', 'individual']")

    all_flex_fields = serialize_flex_attributes().get(associated_with, {})

    for name, value in flex_fields_to_verify.items():
        flex_field = all_flex_fields.get(name)
        if flex_field is None:
            raise ValueError(f"{name} is not a correct `flex field")
        field_type = flex_field["type"]
        field_choices = set(f.get("value") for f in flex_field["choices"])
        if not isinstance(value, FIELD_TYPES_TO_INTERNAL_TYPE[field_type]) or value is None:
            raise ValueError(f"invalid value type for a field {name}")

        if field_type == TYPE_SELECT_ONE and value not in field_choices:
            raise ValueError(f"invalid value: {value} for a field {name}")

        if field_type == TYPE_SELECT_MANY:
            values = set(value)
            if values.issubset(field_choices) is False:
                raise ValueError(f"invalid value: {value} for a field {name}")


def remove_individual_and_reassign_roles(ticket_details, individual_to_remove, info):
    from django.shortcuts import get_object_or_404
    from hct_mis_api.apps.core.utils import decode_id_string
    from graphql import GraphQLError
    from hct_mis_api.apps.household.models import (
        Household,
        Individual,
        IndividualRoleInHousehold,
        HEAD,
        ROLE_PRIMARY,
        ROLE_ALTERNATE,
        ROLE_NO_ROLE,
    )

    old_individual_to_remove = Individual.objects.get(id=individual_to_remove.id)
    roles_to_bulk_update = []
    for role_data in ticket_details.role_reassign_data.values():
        role_name = role_data.get("role")

        individual_id = decode_id_string(role_data.get("individual"))
        household_id = decode_id_string(role_data.get("household"))

        old_new_individual = get_object_or_404(Individual, id=individual_id)
        new_individual = get_object_or_404(Individual, id=individual_id)

        household = get_object_or_404(Household, id=household_id)

        if role_name == HEAD:
            household.head_of_household = new_individual
            # can be directly saved, because there is always only one head of household to update
            household.save()
            household.individuals.exclude(id=new_individual.id).update(relationship=RELATIONSHIP_UNKNOWN)
            new_individual.relationship = HEAD
            new_individual.save()
            log_create(
                Individual.ACTIVITY_LOG_MAPPING,
                "business_area",
                info.context.user,
                old_new_individual,
                new_individual,
            )

        if role_name in (ROLE_PRIMARY, ROLE_ALTERNATE):
            role = get_object_or_404(
                IndividualRoleInHousehold, role=role_name, household=household, individual=individual_to_remove
            )
            role.individual = new_individual
            roles_to_bulk_update.append(role)

    if len(roles_to_bulk_update) != individual_to_remove.households_and_roles.exclude(role=ROLE_NO_ROLE).count():
        raise GraphQLError("Ticket cannot be closed not all roles has been reassigned")

    if roles_to_bulk_update:
        IndividualRoleInHousehold.objects.bulk_update(roles_to_bulk_update, ["individual"])

    removed_individual_household = individual_to_remove.household

    if removed_individual_household:
        removed_individual_is_head = removed_individual_household.head_of_household.id == individual_to_remove.id
    else:
        removed_individual_is_head = False

    if (
        not any(True if HEAD in key else False for key in ticket_details.role_reassign_data.keys())
        and removed_individual_is_head
    ):
        raise GraphQLError("Ticket cannot be closed head of household has not been reassigned")

    individual_to_remove.delete()

    log_create(
        Individual.ACTIVITY_LOG_MAPPING,
        "business_area",
        info.context.user,
        old_individual_to_remove,
        individual_to_remove,
    )
    if removed_individual_household:
        if removed_individual_household.individuals.count() == 0:
            removed_individual_household.delete()
        else:
            removed_individual_household.size -= 1
            removed_individual_household.save()
