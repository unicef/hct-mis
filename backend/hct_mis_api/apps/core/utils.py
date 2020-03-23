import enum
import json
import re
from typing import List

import django
import factory
from django.template.defaultfilters import slugify


def decode_id_string(id_string):
    if not id_string:
        return

    from base64 import b64decode

    return b64decode(id_string).decode().split(":")[1]


def unique_slugify(
    instance, value, slug_field_name="slug", queryset=None, slug_separator="-"
):
    """
    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = "%s%s" % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[: slug_len - len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = "%s%s" % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)


def _slug_strip(value, separator="-"):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """
    separator = separator or ""
    if separator == "-" or not separator:
        re_sep = "-"
    else:
        re_sep = "(?:-|%s)" % re.escape(separator)
    # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub("%s+" % re_sep, separator, value)
    # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != "-":
            re_sep = re.escape(separator)
        value = re.sub(r"^%s+|%s+$" % (re_sep, re_sep), "", value)
    return value


class EnumGetChoices(enum.Enum):
    """Subclasses Enum class for additional methods."""

    def __init__(self, *args, **kwargs):
        super().__init__()

    @classmethod
    def get_choices(cls) -> List[tuple]:
        return [(field.name, field.value) for field in cls]


class JSONFactory(factory.DictFactory):
    """A Json factory class to get JSON strings."""

    @classmethod
    def _generate(cls, create, attrs):
        obj_dict = super()._generate(create, attrs)
        return json.dumps(obj_dict)


def update_model(model: django.db.models.Model, changeset: dict):
    for attrib, value in changeset.items():
        if hasattr(model, attrib):
            setattr(model, attrib, value)


def get_choices_values(choices):
    return tuple(
        choice[0] if isinstance(choice, tuple) else choice for choice in choices
    )


def serialize_flex_attributes():
    """
    Flexible Attributes objects to dict mapping:
        "individuals": {
            "id_type_i_f": {
                "type": "SINGLE_CHOICE",
                "choices": (
                    ("BIRTH_CERTIFICATE", "Birth Certificate"),
                    ("DRIVERS_LICENSE", "Driver's License"),
                    ("UNHCR_ID", "UNHCR ID"),
                    ("NATIONAL_ID", "National ID"),
                    ("NATIONAL_PASSPORT", "National Passport"),
                    ("OTHER", "Other"),
                    ("NOT_AVAILABLE", "Not Available"),
                ),
            },
        },
        "households": {
            "assistance_type_h_f": {
                "type": "MULTIPLE_CHOICE",
                "choices": (
                    (1, "Option 1"),
                    (2, "Option 2"),
                    (3, "Option 3"),
                    (4, "Option 4"),
                    (5, "Option 5"),
                    (6, "Option 6"),
                    (7, "Option 7"),
                ),
            },
        }
    """
    from core.models import FlexibleAttribute

    flex_attributes = FlexibleAttribute.objects.all()

    result_dict = {
        "individuals": {},
        "households": {},
    }

    for attr in flex_attributes:
        associated_with = (
            "households" if attr.associated_with == 0 else "individuals"
        )

        result_dict[associated_with][attr.name] = {
            "type": attr.type,
            "choices": list(attr.choices.values_list("name", flat=True)),
        }

    return result_dict
