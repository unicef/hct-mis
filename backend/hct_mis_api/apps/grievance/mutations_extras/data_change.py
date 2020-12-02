from datetime import datetime, date

import graphene
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_countries.fields import Country
from graphene.utils.str_converters import to_snake_case
from graphql import GraphQLError

from core.utils import decode_id_string
from grievance.models import (
    GrievanceTicket,
    TicketIndividualDataUpdateDetails,
    TicketAddIndividualDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
)
from grievance.mutations_extras.utils import (
    handle_add_document,
    handle_role,
    prepare_previous_documents,
    verify_flex_fields,
)
from household.models import (
    Individual,
    Household,
    HEAD,
    Document,
    ROLE_NO_ROLE,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    IndividualRoleInHousehold,
)
from household.schema import HouseholdNode, IndividualNode


class HouseholdUpdateDataObjectType(graphene.InputObjectType):
    status = graphene.String()
    consent = graphene.Boolean()
    residence_status = graphene.String()
    country_origin = graphene.String()
    country = graphene.String()
    size = graphene.Int()
    address = graphene.String()
    female_age_group_0_5_count = graphene.Int()
    female_age_group_6_11_count = graphene.Int()
    female_age_group_12_17_count = graphene.Int()
    female_adults_count = graphene.Int()
    pregnant_count = graphene.Int()
    male_age_group_0_5_count = graphene.Int()
    male_age_group_6_11_count = graphene.Int()
    male_age_group_12_17_count = graphene.Int()
    male_adults_count = graphene.Int()
    female_age_group_0_5_disabled_count = graphene.Int()
    female_age_group_6_11_disabled_count = graphene.Int()
    female_age_group_12_17_disabled_count = graphene.Int()
    female_adults_disabled_count = graphene.Int()
    male_age_group_0_5_disabled_count = graphene.Int()
    male_age_group_6_11_disabled_count = graphene.Int()
    male_age_group_12_17_disabled_count = graphene.Int()
    male_adults_disabled_count = graphene.Int()
    returnee = graphene.Boolean()
    fchild_hoh = graphene.Boolean()
    child_hoh = graphene.Boolean()
    start = graphene.DateTime()
    end = graphene.DateTime()
    name_enumerator = graphene.String()
    org_enumerator = graphene.String()
    org_name_enumerator = graphene.String()
    village = graphene.String()


class IndividualDocumentObjectType(graphene.InputObjectType):
    country = graphene.String(required=True)
    type = graphene.String(required=True)
    number = graphene.String(required=True)


class IndividualUpdateDataObjectType(graphene.InputObjectType):
    status = graphene.String()
    full_name = graphene.String()
    given_name = graphene.String()
    middle_name = graphene.String()
    family_name = graphene.String()
    sex = graphene.String()
    birth_date = graphene.Date()
    estimated_birth_date = graphene.Boolean()
    marital_status = graphene.String()
    phone_no = graphene.String()
    phone_no_alternative = graphene.String()
    relationship = graphene.String()
    disability = graphene.Boolean()
    work_status = graphene.String()
    enrolled_in_nutrition_programme = graphene.Boolean()
    administration_of_rutf = graphene.Boolean()
    pregnant = graphene.Boolean()
    observed_disability = graphene.List(graphene.String)
    seeing_disability = graphene.String()
    hearing_disability = graphene.String()
    physical_disability = graphene.String()
    memory_disability = graphene.String()
    selfcare_disability = graphene.String()
    comms_disability = graphene.String()
    who_answers_phone = graphene.String()
    who_answers_alt_phone = graphene.String()
    role = graphene.String()
    documents = graphene.List(IndividualDocumentObjectType)
    documents_to_remove = graphene.List(graphene.ID)


class AddIndividualDataObjectType(graphene.InputObjectType):
    full_name = graphene.String(required=True)
    given_name = graphene.String()
    middle_name = graphene.String()
    family_name = graphene.String()
    sex = graphene.String(required=True)
    birth_date = graphene.Date(required=True)
    estimated_birth_date = graphene.Boolean()
    marital_status = graphene.String(required=True)
    phone_no = graphene.String()
    phone_no_alternative = graphene.String()
    relationship = graphene.String()
    disability = graphene.Boolean()
    work_status = graphene.String()
    enrolled_in_nutrition_programme = graphene.Boolean()
    administration_of_rutf = graphene.Boolean()
    pregnant = graphene.Boolean()
    observed_disability = graphene.List(graphene.String)
    seeing_disability = graphene.String()
    hearing_disability = graphene.String()
    physical_disability = graphene.String()
    memory_disability = graphene.String()
    selfcare_disability = graphene.String()
    comms_disability = graphene.String()
    who_answers_phone = graphene.String()
    who_answers_alt_phone = graphene.String()
    role = graphene.String()
    documents = graphene.List(IndividualDocumentObjectType)


class HouseholdDataUpdateIssueTypeExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=True)
    household_data = HouseholdUpdateDataObjectType(required=True)


class IndividualDataUpdateIssueTypeExtras(graphene.InputObjectType):
    individual = graphene.GlobalID(node=IndividualNode, required=True)
    individual_data = IndividualUpdateDataObjectType(required=True)


class AddIndividualIssueTypeExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=True)
    individual_data = AddIndividualDataObjectType(required=True)


class UpdateHouseholdDataUpdateIssueTypeExtras(graphene.InputObjectType):
    household_data = HouseholdUpdateDataObjectType(required=True)


class UpdateIndividualDataUpdateIssueTypeExtras(graphene.InputObjectType):
    individual_data = IndividualUpdateDataObjectType(required=True)


class UpdateAddIndividualIssueTypeExtras(graphene.InputObjectType):
    individual_data = AddIndividualDataObjectType(required=True)


class IndividualDeleteIssueTypeExtras(graphene.InputObjectType):
    individual = graphene.GlobalID(node=IndividualNode, required=True)


def to_date_string(dict, field_name):
    date = dict.get(field_name)
    if date:
        dict[field_name] = date.isoformat()


def save_data_change_extras(root, info, input, grievance_ticket, extras, **kwargs):
    issue_type = input.get("issue_type")
    if issue_type == GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE:
        return save_individual_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs)
    if issue_type == GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL:
        return save_add_individual_extras(root, info, input, grievance_ticket, extras, **kwargs)
    if issue_type == GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL:
        return save_individual_delete_extras(root, info, input, grievance_ticket, extras, **kwargs)
    if issue_type == GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE:
        return save_household_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs)


def update_data_change_extras(root, info, input, grievance_ticket, extras, **kwargs):
    issue_type = grievance_ticket.issue_type
    if issue_type == GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE:
        return update_individual_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs)
    if issue_type == GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL:
        return update_add_individual_extras(root, info, input, grievance_ticket, extras, **kwargs)
    if issue_type == GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE:
        return update_household_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs)


def save_household_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs):
    data_change_extras = extras.get("issue_type")
    household_data_update_issue_type_extras = data_change_extras.get("household_data_update_issue_type_extras")

    household_encoded_id = household_data_update_issue_type_extras.get("household")
    household_id = decode_id_string(household_encoded_id)
    household = get_object_or_404(Household, id=household_id)
    household_data = household_data_update_issue_type_extras.get("household_data", {})
    to_date_string(household_data, "start")
    to_date_string(household_data, "end")
    flex_fields = household_data.pop("flex_fields", {})
    verify_flex_fields(flex_fields, "households")
    household_data_with_approve_status = {
        to_snake_case(field): {"value": value, "approve_status": False} for field, value in household_data.items()
    }

    for field, field_data in household_data_with_approve_status.items():
        current_value = getattr(household, field, None)
        if isinstance(current_value, (datetime, date)):
            current_value = current_value.isoformat()
        if isinstance(current_value, Country):
            current_value = current_value.alpha3
        household_data_with_approve_status[field]["previous_value"] = current_value

    flex_fields_with_approve_status = {
        field: {"value": value, "approve_status": False, "previous_value": household.flex_fields.get(field)}
        for field, value in flex_fields.items()
    }
    household_data_with_approve_status["flex_fields"] = flex_fields_with_approve_status
    ticket_individual_data_update_details = TicketHouseholdDataUpdateDetails(
        household_data=household_data_with_approve_status, household=household, ticket=grievance_ticket,
    )
    ticket_individual_data_update_details.save()
    grievance_ticket.refresh_from_db()
    return [grievance_ticket]


def update_household_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs):
    ticket_details = grievance_ticket.household_data_update_ticket_details
    household_data_update_new_extras = extras.get("household_data_update_issue_type_extras")
    household = ticket_details.household
    new_household_data = household_data_update_new_extras.get("household_data", {})
    to_date_string(new_household_data, "start")
    to_date_string(new_household_data, "end")
    flex_fields = new_household_data.pop("flex_fields", {})
    verify_flex_fields(flex_fields, "households")
    household_data_with_approve_status = {
        to_snake_case(field): {"value": value, "approve_status": False} for field, value in new_household_data.items()
    }

    for field, field_data in household_data_with_approve_status.items():
        current_value = getattr(household, field, None)
        if isinstance(current_value, (datetime, date)):
            current_value = current_value.isoformat()
        if isinstance(current_value, Country):
            current_value = current_value.alpha3
        household_data_with_approve_status[field]["previous_value"] = current_value
    flex_fields_with_approve_status = {
        field: {"value": value, "approve_status": False, "previous_value": household.flex_fields.get(field)}
        for field, value in flex_fields.items()
    }
    household_data_with_approve_status["flex_fields"] = flex_fields_with_approve_status
    ticket_details.household_data = household_data_with_approve_status
    ticket_details.save()
    grievance_ticket.refresh_from_db()
    return grievance_ticket


def save_individual_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs):
    data_change_extras = extras.get("issue_type")
    individual_data_update_issue_type_extras = data_change_extras.get("individual_data_update_issue_type_extras")

    individual_encoded_id = individual_data_update_issue_type_extras.get("individual")
    individual_id = decode_id_string(individual_encoded_id)
    individual = get_object_or_404(Individual, id=individual_id)
    individual_data = individual_data_update_issue_type_extras.get("individual_data", {})
    documents = individual_data.pop("documents", [])
    documents_to_remove = individual_data.pop("documents_to_remove", [])
    to_date_string(individual_data, "birth_date")
    flex_fields = individual_data.pop("flex_fields", {})
    verify_flex_fields(flex_fields, "individuals")
    individual_data_with_approve_status = {
        to_snake_case(field): {"value": value, "approve_status": False} for field, value in individual_data.items()
    }

    for field, field_data in individual_data_with_approve_status.items():
        current_value = getattr(individual, field, None)
        if isinstance(current_value, (datetime, date)):
            current_value = current_value.isoformat()
        individual_data_with_approve_status[field]["previous_value"] = current_value

    documents_with_approve_status = [{"value": document, "approve_status": False} for document in documents]
    documents_to_remove_with_approve_status = [
        {"value": document_id, "approve_status": False} for document_id in documents_to_remove
    ]
    flex_fields_with_approve_status = {
        field: {"value": value, "approve_status": False, "previous_value": individual.flex_fields.get(field)}
        for field, value in flex_fields.items()
    }
    individual_data_with_approve_status["documents"] = documents_with_approve_status
    individual_data_with_approve_status["documents_to_remove"] = documents_to_remove_with_approve_status
    individual_data_with_approve_status["flex_fields"] = flex_fields_with_approve_status

    individual_data_with_approve_status["previous_documents"] = prepare_previous_documents(
        documents_to_remove_with_approve_status
    )
    ticket_individual_data_update_details = TicketIndividualDataUpdateDetails(
        individual_data=individual_data_with_approve_status, individual=individual, ticket=grievance_ticket,
    )
    ticket_individual_data_update_details.save()
    grievance_ticket.refresh_from_db()
    return [grievance_ticket]


def update_individual_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs):
    ticket_details = grievance_ticket.individual_data_update_ticket_details

    individual_data_update_extras = extras.get("individual_data_update_issue_type_extras")

    individual = ticket_details.individual
    new_individual_data = individual_data_update_extras.get("individual_data", {})
    documents = new_individual_data.pop("documents", [])
    documents_to_remove = new_individual_data.pop("documents_to_remove", [])
    flex_fields = new_individual_data.pop("flex_fields", {})
    to_date_string(new_individual_data, "birth_date")
    verify_flex_fields(flex_fields, "individuals")

    individual_data_with_approve_status = {
        to_snake_case(field): {"value": value, "approve_status": False} for field, value in new_individual_data.items()
    }

    for field, field_data in individual_data_with_approve_status.items():
        current_value = getattr(individual, field, None)
        if isinstance(current_value, (datetime, date)):
            current_value = current_value.isoformat()
        individual_data_with_approve_status[field]["previous_value"] = current_value

    documents_with_approve_status = [{"value": document, "approve_status": False} for document in documents]
    documents_to_remove_with_approve_status = [
        {"value": document_id, "approve_status": False} for document_id in documents_to_remove
    ]
    flex_fields_with_approve_status = {
        field: {"value": value, "approve_status": False, "previous_value": individual.flex_fields.get(field)}
        for field, value in flex_fields.items()
    }
    individual_data_with_approve_status["documents"] = documents_with_approve_status
    individual_data_with_approve_status["documents_to_remove"] = documents_to_remove_with_approve_status
    individual_data_with_approve_status["flex_fields"] = flex_fields_with_approve_status

    individual_data_with_approve_status["previous_documents"] = prepare_previous_documents(
        documents_to_remove_with_approve_status
    )

    ticket_details.individual_data = individual_data_with_approve_status
    ticket_details.save()
    grievance_ticket.refresh_from_db()
    return grievance_ticket


def save_individual_delete_extras(root, info, input, grievance_ticket, extras, **kwargs):
    data_change_extras = extras.get("issue_type")
    individual_data_update_issue_type_extras = data_change_extras.get("individual_delete_issue_type_extras")

    individual_encoded_id = individual_data_update_issue_type_extras.get("individual")
    individual_id = decode_id_string(individual_encoded_id)
    individual = get_object_or_404(Individual, id=individual_id)
    ticket_individual_data_update_details = TicketDeleteIndividualDetails(
        individual=individual, ticket=grievance_ticket,
    )
    ticket_individual_data_update_details.save()
    grievance_ticket.refresh_from_db()
    return [grievance_ticket]


def save_add_individual_extras(root, info, input, grievance_ticket, extras, **kwargs):
    data_change_extras = extras.get("issue_type")
    add_individual_issue_type_extras = data_change_extras.get("add_individual_issue_type_extras")

    household_encoded_id = add_individual_issue_type_extras.get("household")
    household_id = decode_id_string(household_encoded_id)
    household = get_object_or_404(Household, id=household_id)
    individual_data = add_individual_issue_type_extras.get("individual_data", {})
    to_date_string(individual_data, "birth_date")
    individual_data = {to_snake_case(key): value for key, value in individual_data.items()}
    flex_fields = individual_data.get("flex_fields", {})
    
    verify_flex_fields(flex_fields, "individuals")
    ticket_add_individual_details = TicketAddIndividualDetails(
        individual_data=individual_data, household=household, ticket=grievance_ticket,
    )
    ticket_add_individual_details.save()
    grievance_ticket.refresh_from_db()
    return [grievance_ticket]


def update_add_individual_extras(root, info, input, grievance_ticket, extras, **kwargs):
    ticket_details = grievance_ticket.add_individual_ticket_details
    new_add_individual_extras = extras.get("add_individual_issue_type_extras")

    new_individual_data = new_add_individual_extras.get("individual_data", {})
    to_date_string(new_individual_data, "birth_date")
    new_individual_data = {to_snake_case(key): value for key, value in new_individual_data.items()}
    flex_fields = new_individual_data.get("flex_fields", {})
    verify_flex_fields(flex_fields, "individuals")

    ticket_details.individual_data = new_individual_data
    ticket_details.approve_status = False
    ticket_details.save()

    grievance_ticket.refresh_from_db()
    return grievance_ticket


def close_add_individual_grievance_ticket(grievance_ticket):
    ticket_details = grievance_ticket.add_individual_ticket_details
    if not ticket_details or ticket_details.approve_status is False:
        return

    household = ticket_details.household
    individual_data = ticket_details.individual_data
    documents = individual_data.pop("documents", [])
    role = individual_data.pop("role", ROLE_NO_ROLE)
    first_registration_date = timezone.now()
    individual = Individual(
        household=household,
        first_registration_date=first_registration_date,
        last_registration_date=first_registration_date,
        **individual_data,
    )

    documents_to_create = [handle_add_document(document, individual) for document in documents]

    relationship_to_head_of_household = individual_data.get("relationship_to_head_of_household")
    if household:
        individual.save()
        if relationship_to_head_of_household == HEAD:
            household.head_of_household = individual
            household.individuals.exclude(id=individual.id).update(relationship_to_head_of_household="")
            household.save(update_fields=["head_of_household"])
        household.size += 1
        household.save()
    else:
        individual.relationship_to_head_of_household = ""
        individual.save()

    handle_role(role, household, individual)

    Document.objects.bulk_create(documents_to_create)


def close_update_individual_grievance_ticket(grievance_ticket):
    ticket_details = grievance_ticket.individual_data_update_ticket_details
    if not ticket_details:
        return

    individual = ticket_details.individual
    household = individual.household
    individual_data = ticket_details.individual_data
    role_data = individual_data.pop("role", {})
    flex_fields_with_additional_data = individual_data.pop("flex_fields", {})
    flex_fields = {
        field: data.get("value")
        for field, data in flex_fields_with_additional_data.items()
        if data.get("approve_status") is True
    }
    documents = individual_data.pop("documents", [])
    documents_to_remove_encoded = individual_data.pop("documents_to_remove", [])
    documents_to_remove = [
        decode_id_string(document_data["value"])
        for document_data in documents_to_remove_encoded
        if document_data["approve_status"] is True
    ]

    only_approved_data = {
        field: value_and_approve_status.get("value")
        for field, value_and_approve_status in individual_data.items()
        if value_and_approve_status.get("approve_status") is True and field != "previous_documents"
    }

    Individual.objects.filter(id=individual.id).update(flex_fields=flex_fields, **only_approved_data)

    relationship_to_head_of_household = individual_data.get("relationship_to_head_of_household")
    if household and relationship_to_head_of_household == HEAD:
        household.head_of_household = individual
        household.individuals.exclude(id=individual.id).update(relationship_to_head_of_household="")
        household.save()

    if role_data.get("approve_status") is True:
        handle_role(role_data.get("value"), household, individual)

    documents_to_create = [
        handle_add_document(document_data["value"], individual)
        for document_data in documents
        if document_data["approve_status"] is True
    ]
    Document.objects.bulk_create(documents_to_create)
    Document.objects.filter(id__in=documents_to_remove).delete()


def close_update_household_grievance_ticket(grievance_ticket):
    ticket_details = grievance_ticket.household_data_update_ticket_details
    if not ticket_details:
        return

    household = ticket_details.household
    household_data = ticket_details.household_data
    country_origin = household_data.get("country_origin", {})
    flex_fields_with_additional_data = household_data.pop("flex_fields", {})
    flex_fields = {
        field: data.get("value")
        for field, data in flex_fields_with_additional_data.items()
        if data.get("approve_status") is True
    }
    if country_origin.get("value") is not None:
        household_data["country_origin"]["value"] = Country(country_origin.get("value"))
    country = household_data.get("country", {})
    if country.get("value") is not None:
        household_data["country"]["value"] = Country(country.get("value"))
    only_approved_data = {
        field: value_and_approve_status.get("value")
        for field, value_and_approve_status in household_data.items()
        if value_and_approve_status.get("approve_status") is True
    }

    Household.objects.filter(id=household.id).update(flex_fields=flex_fields, **only_approved_data)


def close_delete_individual_ticket(grievance_ticket):
    ticket_details = grievance_ticket.delete_individual_ticket_details
    if not ticket_details or ticket_details.approve_status is False:
        return

    individual_to_remove = ticket_details.individual

    roles_to_bulk_update = []
    for role_data in ticket_details.role_reassign_data.values():
        role_name = role_data.get("role")
        individual_id = decode_id_string(role_data.get("individual"))
        household_id = decode_id_string(role_data.get("household"))
        new_individual = get_object_or_404(Individual, id=individual_id)
        household = get_object_or_404(Household, id=household_id)

        if role_name == HEAD:
            household.head_of_household = new_individual
            # can be directly saved, because there is always only one head of household to update
            household.save()
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

    if removed_individual_household:
        if removed_individual_household.individuals.count() == 0:
            removed_individual_household.delete()
        else:
            removed_individual_household.size -= 1
            removed_individual_household.save()
