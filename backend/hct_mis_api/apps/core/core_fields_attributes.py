from functools import reduce

from django.core.exceptions import ValidationError
from django.db.models import Q

from core.countries import Countries
from core.models import AdminArea
from core.utils import LazyEvalMethodsDict, age_to_birth_date_query
from household.models import (
    DATA_SHARING_CHOICES,
    DISABILITY_CHOICE,
    MARITAL_STATUS_CHOICE,
    ORG_ENUMERATOR_CHOICES,
    RELATIONSHIP_CHOICE,
    RESIDENCE_STATUS_CHOICE,
    ROLE_CHOICE,
    SEVERITY_OF_DISABILITY_CHOICES,
    SEX_CHOICE,
    WORK_STATUS_CHOICE,
    YES_NO_CHOICE,
)

TYPE_ID = "ID"
TYPE_INTEGER = "INTEGER"
TYPE_STRING = "STRING"
TYPE_LIST_OF_IDS = "LIST_OF_IDS"
TYPE_BOOL = "BOOL"
TYPE_DATE = "DATE"
TYPE_IMAGE = "IMAGE"
TYPE_SELECT_ONE = "SELECT_ONE"
TYPE_SELECT_MANY = "SELECT_MANY"
TYPE_GEOPOINT = "GEOPOINT"

_INDIVIDUAL = "Individual"
_HOUSEHOLD = "Household"

FILTERABLE_TYPES = [
    TYPE_INTEGER,
    TYPE_STRING,
    TYPE_SELECT_ONE,
    TYPE_SELECT_MANY,

]


def country_generic_query(comparision_method, args, lookup):
    query = Q(**{lookup: Countries.get_country_value(args[0])})
    if comparision_method == "EQUALS":
        return query
    elif comparision_method == "NOT_EQUALS":
        return ~query
    raise ValidationError(f"Country filter query does not support {comparision_method} type")


def country_query(comparision_method, args):
    return country_generic_query(comparision_method, args, "country")

def country_origin_query(comparision_method, args):
    return country_generic_query(comparision_method, args, "country_origin")


CORE_FIELDS_ATTRIBUTES = [
    {
        "id": "a1741e3c-0e24-4a60-8d2f-463943abaebb",
        "type": TYPE_INTEGER,
        "name": "age",
        "label": {"English(EN)": "Age (calculated)"},
        "hint": "",
        "required": False,
        "get_query": age_to_birth_date_query,
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "age",
    },
    {
        "id": "3c2473d6-1e81-4025-86c7-e8036dd92f4b",
        "type": TYPE_SELECT_ONE,
        "name": "residence_status",
        "lookup": "residence_status",
        "required": True,
        "label": {"English(EN)": "Residence status"},
        "hint": "",
        "choices": [{"label": {"English(EN)": label}, "value": value} for value, label in RESIDENCE_STATUS_CHOICE],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "residence_status_h_c",
    },
    {
        "id": "e47bafa7-0b86-4be9-a07f-d3fc7ac698cf",
        "type": TYPE_BOOL,
        "name": "consent",
        "lookup": "consent",
        "required": True,
        "label": {"English(EN)": "Do you consent?"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "consent_h_c",
    },
    {
        "id": "9480fc0d-1b88-45b0-9056-6a6fe0ebe509",
        "type": TYPE_IMAGE,
        "name": "consent_sign",
        "lookup": "consent_sign",
        "required": True,
        "label": {"English(EN)": "Do you consent?"},
        "hint": "Ask the head of household to sign or do an X as acknowledgement",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "consent_sign_h_c",
    },
    {
        "id": "e44efed6-47d6-4f60-bcf6-b1d2ffc4d7d1",
        "type": TYPE_SELECT_ONE,
        "name": "country_origin",
        "lookup": "country_origin",
        "required": False,
        "label": {"English(EN)": "Country origin"},
        "hint": "country origin",
        "get_query": country_origin_query,
        "choices": Countries.get_choices(output_code="alpha3"),
        "custom_validate_choices": Countries.is_valid_country_choice,
        "custom_cast_value": Countries.get_country_value,
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "country_origin_h_c",
    },
    {
        "id": "aa79985c-b616-453c-9884-0666252c3070",
        "type": TYPE_SELECT_ONE,
        "name": "country",
        "lookup": "country",
        "required": False,
        "label": {"English(EN)": "Country"},
        "hint": "",
        "get_query": country_query,
        "choices": Countries.get_choices(output_code="alpha3"),
        "custom_validate_choices": Countries.is_valid_country_choice,
        "custom_cast_value": Countries.get_country_value,
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "country_h_c",
    },
    {
        "id": "59685cec-69bf-4abe-81b4-70b8f05b89f3",
        "type": TYPE_STRING,
        "name": "address",
        "lookup": "address",
        "required": False,
        "label": {"English(EN)": "Address"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "address_h_c",
    },
    LazyEvalMethodsDict(
        {
            "id": "c53ea58b-e7cf-4bf3-82d0-dec41f66ef3a",
            "type": TYPE_SELECT_ONE,
            "name": "admin1",
            "lookup": "admin1",
            "required": False,
            "label": {"English(EN)": "Household resides in (Select administrative level 1)"},
            "hint": "",
            "choices": lambda: AdminArea.get_admin_areas_as_choices(1),
            "associated_with": _HOUSEHOLD,
            "xlsx_field": "admin1_h_c",
        }
    ),
    LazyEvalMethodsDict(
        {
            "id": "e4eb6632-8204-44ed-b39c-fe791ded9246",
            "type": TYPE_SELECT_ONE,
            "name": "admin2",
            "lookup": "admin2",
            "required": False,
            "label": {"English(EN)": "Household resides in (Select administrative level 2)"},
            "hint": "",
            "choices": lambda: AdminArea.get_admin_areas_as_choices(2),
            "associated_with": _HOUSEHOLD,
            "xlsx_field": "admin2_h_c",
        }
    ),
    {
        "id": "13a9d8b0-f278-47c2-9b1b-b06579b0ab35",
        "type": TYPE_GEOPOINT,
        "name": "geopoint",
        "lookup": "geopoint",
        "required": False,
        "label": {"English(EN)": "Household Geopoint"},
        "hint": "latitude and longitude of household",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "hh_geopoint_h_c",
    },
    {
        "id": "5b32bad5-ff7c-4e6b-af7e-a0287fe91ea2",
        "type": TYPE_STRING,
        "name": "unhcr_id",
        "lookup": "unhcr_id",
        "required": False,
        "label": {"English(EN)": "UNHCR Case ID"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "unhcr_id_h_c",
    },
    {
        "id": "5f530642-b889-4130-bf1a-5fac1b17cf09",
        "type": TYPE_BOOL,
        "name": "returnee",
        "lookup": "returnee",
        "required": False,
        "label": {"English(EN)": "Is this a returnee household?"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "returnee_h_c",
    },
    {
        "id": "d668ae31-12cf-418e-8f7f-4c6398d82ffd",
        "type": TYPE_INTEGER,
        "name": "size",
        "lookup": "size",
        "required": True,
        "label": {"English(EN)": "What is the household size?"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "size_h_c",
    },
    {
        "id": "8d9df01a-ce7c-4e78-b8ec-6f3eec8f30ce",
        "type": TYPE_SELECT_ONE,
        "name": "relationship",
        "lookup": "relationship",
        "required": True,
        "label": {"English(EN)": "Relationship to Head of Household"},
        "hint": "",
        "choices": [{"label": {"English(EN)": label}, "value": value} for value, label in RELATIONSHIP_CHOICE],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "relationship_i_c",
    },
    {
        "id": "36ab3421-6e7a-40d1-b816-ea5cbdcc0b6a",
        "type": TYPE_STRING,
        "name": "full_name",
        "lookup": "full_name",
        "required": True,
        "label": {"English(EN)": "Full Name"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "full_name_i_c",
    },
    {
        "id": "b1f90314-b8b8-4bcb-9265-9d48d1fce5a4",
        "type": TYPE_STRING,
        "name": "given_name",
        "lookup": "given_name",
        "required": False,
        "label": {"English(EN)": "Given Name"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "given_name_i_c",
    },
    {
        "id": "6f603107-bd88-4a8d-97cc-748a7238358d",
        "type": TYPE_STRING,
        "name": "middle_name",
        "lookup": "middle_name",
        "required": False,
        "label": {"English(EN)": "Middle Names"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "middle_name_i_c",
    },
    {
        "id": "3f74dd36-bfd2-4c84-bfc7-21f7adbff7f0",
        "type": TYPE_STRING,
        "name": "family_name",
        "lookup": "family_name",
        "required": False,
        "label": {"English(EN)": "Family Name"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "family_name_i_c",
    },
    {
        "id": "da726870-dfc9-48dc-aba9-b9138b611c74",
        "type": TYPE_SELECT_ONE,
        "name": "sex",
        "lookup": "sex",
        "required": True,
        "label": {"English(EN)": "Gender"},
        "hint": "",
        "choices": [{"label": {"English(EN)": label}, "value": value} for value, label in SEX_CHOICE],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "gender_i_c",
    },
    {
        "id": "416b0119-2d89-4517-819d-e563d2eb428c",
        "type": TYPE_DATE,
        "name": "birth_date",
        "lookup": "birth_date",
        "required": True,
        "label": {"English(EN)": "Birth Date"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "birth_date_i_c",
    },
    {
        "id": "6536a987-a50e-453b-9517-57c1dccd1340",
        "type": TYPE_DATE,
        "name": "first_registration_date",
        "lookup": "first_registration_date",
        "required": True,
        "label": {"English(EN)": "First individual registration date"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "first_registration_date_i_c",
    },
    {
        "id": "2fe6d876-388f-45d9-b497-eb2f8af923e8",
        "type": TYPE_DATE,
        "name": "first_registration_date",
        "lookup": "first_registration_date",
        "required": True,
        "label": {"English(EN)": "First household registration date"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "first_registration_date_h_c",
    },
    {
        "id": "5e2c2a7c-9651-4c07-873c-f594ae18a56a",
        "type": TYPE_BOOL,
        "name": "estimated_birth_date",
        "lookup": "estimated_birth_date",
        "required": False,
        "label": {"English(EN)": "Estimated Birth Date?"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "estimated_birth_date_i_c",
    },
    {
        "id": "84827966-17e5-407a-9424-1350c7ec3b64",
        "type": TYPE_IMAGE,
        "name": "photo",
        "lookup": "photo",
        "required": False,
        "label": {"English(EN)": "Photo"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "photo_i_c",
    },
    {
        "id": "35ede8c4-877e-40dc-a93a-0a9a3bc511dc",
        "type": TYPE_SELECT_ONE,
        "name": "marital_status",
        "lookup": "marital_status",
        "required": True,
        "label": {"English(EN)": "Marital Status"},
        "hint": "",
        "choices": [{"label": {"English(EN)": label}, "value": value} for value, label in MARITAL_STATUS_CHOICE],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "marital_status_i_c",
    },
    {
        "id": "01c1ae70-d8f8-4451-96c5-09afb4ff3057",
        "type": TYPE_STRING,
        "name": "phone_no",
        "lookup": "phone_no",
        "required": False,
        "label": {"English(EN)": "Phone number"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "phone_no_i_c",
    },
    {
        "id": "f7609980-95c4-4b18-82dc-132a04ce7d65",
        "type": TYPE_STRING,
        "name": "phone_no_alternative",
        "lookup": "phone_no_alternative",
        "required": False,
        "label": {"English(EN)": "Alternative phone number"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "phone_no_alternative_i_c",
    },
    {
        "id": "f1d0c0c1-53d7-422a-be3d-b3588ee0ff58",
        "type": TYPE_STRING,
        "name": "birth_certificate_no",
        "lookup": "birth_certificate_no",
        "required": False,
        "label": {"English(EN)": "Birth certificate number"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "birth_certificate_no_i_c",
    },
    {
        "id": "12ceb917-8942-4cb6-a9d0-6a97a097258a",
        "type": TYPE_IMAGE,
        "name": "birth_certificate_photo",
        "lookup": "birth_certificate_photo",
        "required": False,
        "label": {"English(EN)": "Birth certificate photo"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "birth_certificate_photo_i_c",
    },
    {
        "id": "34a9519f-9c42-4910-b097-157ec8e6e31f",
        "type": TYPE_STRING,
        "name": "drivers_license_no",
        "lookup": "drivers_license_no",
        "required": False,
        "label": {"English(EN)": "Driver's license number"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "drivers_license_no_i_c",
    },
    {
        "id": "7e6a41c5-0fbd-4f99-98ba-2c6a7da8dbe4",
        "type": TYPE_IMAGE,
        "name": "drivers_license_photo",
        "lookup": "drivers_license_photo",
        "required": False,
        "label": {"English(EN)": "Driver's license photo"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "drivers_license_photo_i_c",
    },
    {
        "id": "225832fc-c61b-4100-aac9-352d272d15fd",
        "type": TYPE_STRING,
        "name": "electoral_card_no",
        "lookup": "electoral_card_no",
        "required": False,
        "label": {"English(EN)": "Electoral card number"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "electoral_card_no_i_c",
    },
    {
        "id": "ffb6a487-a806-47d6-a12f-fe3c6c516976",
        "type": TYPE_IMAGE,
        "name": "electoral_card_photo",
        "lookup": "electoral_card_photo",
        "required": False,
        "label": {"English(EN)": "Electoral card photo"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "electoral_card_photo_i_c",
    },
    {
        "id": "1c7f6c85-1621-48f1-88f3-a172d69aa316",
        "type": TYPE_STRING,
        "name": "unhcr_id_no",
        "lookup": "unhcr_id_no",
        "required": False,
        "label": {"English(EN)": "UNHCR ID number"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "unhcr_id_no_i_c",
    },
    {
        "id": "2f9ca147-afde-4311-9d61-e906a8ef2334",
        "type": TYPE_IMAGE,
        "name": "unhcr_id_photo",
        "lookup": "unhcr_id_photo",
        "required": False,
        "label": {"English(EN)": "UNHCR ID photo"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "unhcr_id_photo_i_c",
    },
    {
        "id": "4e836832-2cf2-4073-80eb-21316eaf7277",
        "type": TYPE_STRING,
        "name": "national_passport",
        "lookup": "national_passport",
        "required": False,
        "label": {"English(EN)": "National passport number"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "national_passport_i_c",
    },
    {
        "id": "234a1b5b-7900-4f67-86a9-5fcaede3d09d",
        "type": TYPE_IMAGE,
        "name": "national_passport_photo",
        "lookup": "national_passport_photo",
        "required": False,
        "label": {"English(EN)": "National passport photo"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "national_passport_photo_i_c",
    },
    {
        "id": "eff20a18-4336-4273-bbb8-ed0e9a94ebbb",
        "type": TYPE_STRING,
        "name": "national_id_no",
        "lookup": "national_id_no",
        "required": False,
        "label": {"English(EN)": "National ID number"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "national_id_no_i_c",
    },
    {
        "id": "d43304d9-91e4-4317-9356-f7066b898b16",
        "type": TYPE_IMAGE,
        "name": "national_id_photo",
        "lookup": "national_id_photo",
        "required": False,
        "label": {"English(EN)": "National ID photo"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "national_id_photo_i_c",
    },
    {
        "id": "201c91d2-8f89-46c9-ba5a-db7130140402",
        "type": TYPE_STRING,
        "name": "scope_id_no",
        "lookup": "scope_id_no",
        "required": False,
        "label": {"English(EN)": "WFP Scope ID number"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "scope_id_no_i_c",
    },
    {
        "id": "4aa3d595-131a-48df-8752-ec171eabe3be",
        "type": TYPE_IMAGE,
        "name": "scope_id_photo",
        "lookup": "scope_id_photo",
        "required": False,
        "label": {"English(EN)": "WFP Scope ID photo"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "scope_id_photo_i_c",
    },
    {
        "id": "3bf6105f-87d0-479b-bf92-7f90af4d8462",
        "type": TYPE_STRING,
        "name": "other_id_type",
        "lookup": "other_id_type",
        "required": False,
        "label": {"English(EN)": "If other type of ID, specify the type"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "other_id_type_i_c",
    },
    {
        "id": "556e14af-9901-47f3-bf2c-20b4c721e8f7",
        "type": TYPE_STRING,
        "name": "other_id_no",
        "lookup": "other_id_no",
        "required": False,
        "label": {"English(EN)": "ID number"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "other_id_no_i_c",
    },
    {
        "id": "d4279a74-377f-4f74-baf2-e1ebd001ec5c",
        "type": TYPE_IMAGE,
        "name": "other_id_photo",
        "lookup": "other_id_photo",
        "required": False,
        "label": {"English(EN)": "ID photo"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "other_id_type_i_c",
    },
    {
        "id": "b886d636-36cd-4beb-b2f9-6ddb204532d5",
        "type": TYPE_INTEGER,
        "name": "pregnant_member",
        "lookup": "pregnant_member",
        "required": True,
        "label": {"English(EN)": "How many pregnant women are there in the Household?"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "pregnant_member_h_c",
    },
    {
        "id": "07f7005f-e70d-409b-9dee-4c3414aba40b",
        "type": TYPE_INTEGER,
        "name": "female_age_group_0_5_count",
        "lookup": "female_age_group_0_5_count",
        "required": True,
        "label": {"English(EN)": "Females Age 0-5"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "f_0_5_age_group_h_c",
    },
    {
        "id": "6b993af8-4a5d-4a08-a444-8ade115c39ad",
        "type": TYPE_INTEGER,
        "name": "female_age_group_6_11_count",
        "lookup": "female_age_group_6_11_count",
        "required": True,
        "label": {"English(EN)": "Females Age 6-11"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "f_6_11_age_group_h_c",
    },
    {
        "id": "71ce16b5-4e49-48fa-818c-0bd2eba079eb",
        "type": TYPE_INTEGER,
        "name": "female_age_group_12_17_count",
        "lookup": "female_age_group_12_17_count",
        "required": True,
        "label": {"English(EN)": "Females Age 12-17"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "f_12_17_age_group_h_c",
    },
    {
        "id": "c157ad2d-dfee-4c03-8a8d-b550779696ff",
        "type": TYPE_INTEGER,
        "name": "female_adults_count",
        "lookup": "female_adults_count",
        "required": True,
        "label": {"English(EN)": "Female Adults"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "f_adults_h_c",
    },
    {
        "id": "18fd9429-400f-4fce-b72f-035d2afca201",
        "type": TYPE_INTEGER,
        "name": "pregnant_count",
        "lookup": "pregnant_count",
        "required": True,
        "label": {"English(EN)": "Pregnant females"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "f_pregnant_h_c",
    },
    {
        "id": "57233f1b-93c3-4fd4-a885-92c512c5e32a",
        "type": TYPE_INTEGER,
        "name": "male_age_group_0_5_count",
        "lookup": "male_age_group_0_5_count",
        "required": True,
        "label": {"English(EN)": "Males Age 0-5"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "m_0_5_age_group_h_c",
    },
    {
        "id": "11e2a938-e93a-4c18-8eca-7e61355d7476",
        "type": TYPE_INTEGER,
        "name": "male_age_group_6_11_count",
        "lookup": "male_age_group_6_11_count",
        "required": True,
        "label": {"English(EN)": "Males Age 6-11"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "m_6_11_age_group_h_c",
    },
    {
        "id": "bf28628e-0f6a-46e8-9587-3b0c17977006",
        "type": TYPE_INTEGER,
        "name": "male_age_group_12_17_count",
        "lookup": "male_age_group_12_17_count",
        "required": True,
        "label": {"English(EN)": "Males Age 12-17"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "m_12_17_age_group_h_c",
    },
    {
        "id": "48d464f5-3a45-4f8d-bfbb-a71cc16c0434",
        "type": TYPE_INTEGER,
        "name": "male_adults_count",
        "lookup": "male_adults_count",
        "required": True,
        "label": {"English(EN)": "Male Adults"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "m_adults_h_c",
    },
    {
        "id": "4f59aca6-5900-40c0-a1e4-47c331a90a6f",
        "type": TYPE_INTEGER,
        "name": "female_age_group_0_5_disabled_count",
        "lookup": "female_age_group_0_5_disabled_count",
        "required": True,
        "label": {"English(EN)": "Female members with Disability age 0-5"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "f_0_5_disability_h_c",
    },
    {
        "id": "10e33d7b-b3c4-4383-a4f0-6eba00a15e9c",
        "type": TYPE_INTEGER,
        "name": "female_age_group_6_11_disabled_count",
        "lookup": "female_age_group_6_11_disabled_count",
        "required": True,
        "label": {"English(EN)": "Female members with Disability age 6-11"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "f_6_11_disability_h_c",
    },
    {
        "id": "623a6fd6-d863-40cc-a4d1-964f739747be",
        "type": TYPE_INTEGER,
        "name": "female_age_group_12_17_disabled_count",
        "lookup": "female_age_group_12_17_disabled_count",
        "required": True,
        "label": {"English(EN)": "Female members with Disability age 12-17"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "f_12_17_disability_h_c",
    },
    {
        "id": "9eb7c4e5-f27f-4fe6-8956-ddbe712eb97b",
        "type": TYPE_INTEGER,
        "name": "female_adults_disabled_count",
        "lookup": "female_adults_disabled_count",
        "required": True,
        "label": {"English(EN)": "Female members with Disability adults"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "f_adults_disability_h_c",
    },
    {
        "id": "d3b82576-1bba-44fa-9d5a-db04e71bb35b",
        "type": TYPE_INTEGER,
        "name": "male_age_group_0_5_disabled_count",
        "lookup": "male_age_group_0_5_disabled_count",
        "required": True,
        "label": {"English(EN)": "Male members with Disability age 0-5"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "m_0_5_disability_h_c",
    },
    {
        "id": "78340f8f-86ab-464a-8e19-ce3d6feec5d6",
        "type": TYPE_INTEGER,
        "name": "male_age_group_6_11_disabled_count",
        "lookup": "male_age_group_6_11_disabled_count",
        "required": True,
        "label": {"English(EN)": "Male members with Disability age 6-11"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "m_6_11_disability_h_c",
    },
    {
        "id": "519140f7-1a9e-4115-b736-2b09dbc6f036",
        "type": TYPE_INTEGER,
        "name": "male_age_group_12_17_disabled_count",
        "lookup": "male_age_group_12_17_disabled_count",
        "required": True,
        "label": {"English(EN)": "Male members with Disability age 12-17"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "m_12_17_disability_h_c",
    },
    {
        "id": "3ca9b3de-12df-4bb3-9414-d26ae1fac9b8",
        "type": TYPE_INTEGER,
        "name": "male_adults_disabled_count",
        "lookup": "male_adults_disabled_count",
        "required": True,
        "label": {"English(EN)": "Male members with Disability adults"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "m_adults_disability_h_c",
    },
    {
        "id": "b2593385-5a81-452e-ae9a-28292e35714b",
        "type": TYPE_BOOL,
        "name": "pregnant",
        "lookup": "pregnant",
        "required": False,
        "label": {"English(EN)": "Is pregnant?"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "pregnant_i_c",
    },
    {
        "id": "dca6748f-7831-4fa1-b5c8-e708a456656b",
        "type": TYPE_SELECT_ONE,
        "name": "work_status",
        "lookup": "work_status",
        "required": False,
        "label": {"English(EN)": "Does the individual work?"},
        "hint": "",
        "choices": [{"label": {"English(EN)": label}, "value": value} for value, label in WORK_STATUS_CHOICE],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "work_status_i_c",
    },
    {
        "id": "21cd9a35-b080-4f60-97da-6ec6918a49c0",
        "type": TYPE_SELECT_MANY,
        "name": "observed_disability",
        "lookup": "observed_disability",
        "required": False,
        "label": {"English(EN)": "Does the individual have disability?"},
        "hint": "",
        "choices": [{"label": {"English(EN)": label}, "value": value} for value, label in DISABILITY_CHOICE],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "observed_disability_i_c",
    },
    {
        "id": "244ec9ae-5eb8-4b80-9416-91024a3f32d7",
        "type": TYPE_SELECT_ONE,
        "name": "seeing_disability",
        "lookup": "seeing_disability",
        "required": False,
        "label": {"English(EN)": "If the individual has difficulty seeing, what is the severity?"},
        "hint": "",
        "choices": [
            {"label": {"English(EN)": label}, "value": value} for value, label in SEVERITY_OF_DISABILITY_CHOICES
        ],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "seeing_disability_i_c",
    },
    {
        "id": "bef35c02-1fe7-4f6b-a0af-8282ec31de89",
        "type": TYPE_SELECT_ONE,
        "name": "hearing_disability",
        "lookup": "hearing_disability",
        "required": False,
        "label": {"English(EN)": "If the individual has difficulty hearing, what is the severity?"},
        "hint": "",
        "choices": [
            {"label": {"English(EN)": label}, "value": value} for value, label in SEVERITY_OF_DISABILITY_CHOICES
        ],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "hearing_disability_i_c",
    },
    {
        "id": "b7346b1f-23ea-47a8-b2ec-c176c62cdb5b",
        "type": TYPE_SELECT_ONE,
        "name": "physical_disability",
        "lookup": "physical_disability",
        "required": False,
        "label": {"English(EN)": "If the individual has difficulty walking or climbing steps, what is the severity?"},
        "hint": "",
        "choices": [
            {"label": {"English(EN)": label}, "value": value} for value, label in SEVERITY_OF_DISABILITY_CHOICES
        ],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "physical_disability_i_c",
    },
    {
        "id": "0f24c374-4428-43ef-b162-86dc1b14e39d",
        "type": TYPE_SELECT_ONE,
        "name": "memory_disability",
        "lookup": "memory_disability",
        "required": False,
        "label": {
            "English(EN)": "If the individual has difficulty remembering or concentrating, what is the severity?"
        },
        "hint": "",
        "choices": [
            {"label": {"English(EN)": label}, "value": value} for value, label in SEVERITY_OF_DISABILITY_CHOICES
        ],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "memory_disability_i_c",
    },
    {
        "id": "59508af1-07d0-4e20-ac3d-f241bef319c1",
        "type": TYPE_SELECT_ONE,
        "name": "selfcare_disability",
        "lookup": "selfcare_disability",
        "required": False,
        "label": {"English(EN)": "Do you have difficulty (with self-care such as) washing all over or dressing"},
        "hint": "",
        "choices": [
            {"label": {"English(EN)": label}, "value": value} for value, label in SEVERITY_OF_DISABILITY_CHOICES
        ],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "selfcare_disability_i_c",
    },
    {
        "id": "78311be2-fb3f-443c-aac6-c0e7197af20d",
        "type": TYPE_SELECT_ONE,
        "name": "comms_disability",
        "lookup": "comms_disability",
        "required": False,
        "label": {"English(EN)": "If the individual has difficulty communicating, what is the severity?"},
        "hint": "",
        "choices": [
            {"label": {"English(EN)": label}, "value": value} for value, label in SEVERITY_OF_DISABILITY_CHOICES
        ],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "comms_disability_i_c",
    },
    {
        "id": "9fbd2b6f-6713-445c-a7bb-e1efc398b20d",
        "type": TYPE_BOOL,
        "name": "fchild_hoh",
        "lookup": "fchild_hoh",
        "required": False,
        "label": {"English(EN)": "Female child headed household"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "fchild_hoh_h_c",
    },
    {
        "id": "e92810b2-c6f1-480c-95a9-4f736a1f48bf",
        "type": TYPE_BOOL,
        "name": "child_hoh",
        "lookup": "child_hoh",
        "required": False,
        "label": {"English(EN)": "Child headed household"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "child_hoh_h_c",
    },
    {
        "id": "62692d6a-c054-418b-803a-e34393cbc1b0",
        "type": TYPE_STRING,
        "name": "village",
        "lookup": "village",
        "required": False,
        "label": {"English(EN)": "Village"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "village_h_c",
    },
    {
        "id": "9da8c56a-3c65-47d9-8149-699761842ce4",
        "type": TYPE_STRING,
        "name": "start",
        "lookup": "start",
        "required": False,
        "label": {"English(EN)": "Data collection start date"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "start_h_c",
    },
    {
        "id": "06e4c4a0-28d2-4530-be24-92623a5b48b0",
        "type": TYPE_STRING,
        "name": "end",
        "lookup": "end",
        "required": False,
        "label": {"English(EN)": "Data collection end date"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "end_h_c",
    },
    {
        "id": "c640fe45-368f-4206-afae-09700a495db3",
        "type": TYPE_STRING,
        "name": "deviceid",
        "lookup": "deviceid",
        "required": False,
        "label": {"English(EN)": "Device ID"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "deviceid_h_c",
    },
    {
        "id": "8f379d33-c5fd-4344-ba2b-73e136aba13a",
        "type": TYPE_STRING,
        "name": "name_enumerator",
        "lookup": "name_enumerator",
        "required": True,
        "label": {"English(EN)": "Name of the enumerator"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "name_enumerator_h_c",
    },
    {
        "id": "201e9a88-fb7d-4ba4-afec-66aba748fe55",
        "type": TYPE_SELECT_ONE,
        "name": "org_enumerator",
        "lookup": "org_enumerator",
        "required": True,
        "label": {"English(EN)": "Organization of the enumerator"},
        "hint": "",
        "choices": [{"label": {"English(EN)": label}, "value": value} for value, label in ORG_ENUMERATOR_CHOICES],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "org_enumerator_h_c",
    },
    {
        "id": "0858371e-4e5c-402e-9cda-b767eb2d337c",
        "type": TYPE_SELECT_MANY,
        "name": "consent_sharing",
        "lookup": "consent_sharing",
        "required": True,
        "label": {"English(EN)": "Which organizations may we share your information with?"},
        "hint": "",
        "choices": [{"label": {"English(EN)": label}, "value": value} for value, label in DATA_SHARING_CHOICES],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "consent_sharing_h_c",
    },
    {
        "id": "27bd4ef2-442d-4b49-976c-063df050b3ae",
        "type": TYPE_STRING,
        "name": "org_name_enumerator",
        "lookup": "org_name_enumerator",
        "required": True,
        "label": {"English(EN)": "Name of partner organization"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "org_name_enumerator_h_c",
    },
    {
        "id": "8e10289e-235a-4af5-a745-8c3082b820f5",
        "type": TYPE_STRING,
        "name": "who_answers_phone",
        "lookup": "who_answers_phone",
        "required": False,
        "label": {"English(EN)": "Who answers this phone?"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "who_answers_phone_i_c",
    },
    {
        "id": "2448dbfe-e746-4aea-9e74-e635a3195dc5",
        "type": TYPE_STRING,
        "name": "who_answers_alt_phone",
        "lookup": "who_answers_alt_phone",
        "required": False,
        "label": {"English(EN)": "Who answers this phone?"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "who_answers_alt_phone_i_c",
    },
]

HOUSEHOLD_ID_FIELDS = [
    {
        "id": "746b3d2d-19c5-4b91-ad37-d230e1d33eb5",
        "type": TYPE_ID,
        "name": "household_id",
        "lookup": "household_id",
        "required": False,
        "label": {"English(EN)": "Household ID"},
        "hint": "",
        "choices": [],
        "associated_with": _HOUSEHOLD,
        "xlsx_field": "household_id",
    },
    {
        "id": "1079bfd0-fc51-41ab-aa10-667e6b2034b9",
        "type": TYPE_ID,
        "name": "household_id",
        "lookup": "household_id",
        "required": False,
        "label": {"English(EN)": "Household ID"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "household_id",
    },
]

COLLECTORS_FIELDS = {
    "primary_collector_id": {
        "type": TYPE_LIST_OF_IDS,
        "name": "primary_collector_id",
        "required": True,
        "label": {"English(EN)": "List of primary collectors ids, separated by a semicolon"},
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "primary_collector_id",
        "custom_cast_value": Countries.get_country_value,
    },
    "alternate_collector_id": {
        "type": TYPE_LIST_OF_IDS,
        "name": "alternate_collector_id",
        "required": True,
        "label": {"English(EN)": "List of alternate collectors ids, separated by a semicolon"},
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "alternate_collector_id",
        "custom_cast_value": Countries.get_country_value,
    },
}

KOBO_COLLECTOR_FIELD = {
    "is_only_collector": {
        "type": TYPE_SELECT_ONE,
        "name": "is_only_collector",
        "required": True,
        "label": {"English(EN)": "Is only a collector, not a part of household"},
        "choices": [{"label": {"English(EN)": label}, "value": value} for value, label in YES_NO_CHOICE],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "is_only_collector",
    },
    "role_i_c": {
        "type": TYPE_SELECT_ONE,
        "name": "role",
        "lookup": "role",
        "required": True,
        "label": {"English(EN)": "Role"},
        "hint": "",
        "choices": [{"label": {"English(EN)": label}, "value": value} for value, label in ROLE_CHOICE],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "role_i_c",
    },
}


def _reduce_core_field_attr(old, new):
    old[new.get("name")] = new
    return old


def _core_fields_to_separated_dict(append_household_id=True):
    result_dict = {
        "individuals": {},
        "households": {},
    }

    core_fields_attrs = CORE_FIELDS_ATTRIBUTES

    if append_household_id:
        core_fields_attrs = HOUSEHOLD_ID_FIELDS + CORE_FIELDS_ATTRIBUTES

    for field in core_fields_attrs:
        associated_key = field["associated_with"].lower() + "s"
        result_dict[associated_key][field["xlsx_field"]] = field

    return result_dict


FILTERABLE_CORE_FIELDS_ATTRIBUTES = [x for x in CORE_FIELDS_ATTRIBUTES if x.get("type") in FILTERABLE_TYPES]

CORE_FIELDS_ATTRIBUTES_DICTIONARY = reduce(_reduce_core_field_attr, CORE_FIELDS_ATTRIBUTES, {})

CORE_FIELDS_SEPARATED_WITH_NAME_AS_KEY = _core_fields_to_separated_dict()
