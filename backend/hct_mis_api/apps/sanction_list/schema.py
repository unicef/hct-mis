from django.db.models.functions import Lower

import graphene
from django_filters import CharFilter, FilterSet
from graphene import relay
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import DjangoPermissionFilterConnectionField
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.utils import CustomOrderingFilter
from hct_mis_api.apps.sanction_list.filters import SanctionListIndividualFilter
from hct_mis_api.apps.sanction_list.models import (
    SanctionListIndividual,
    SanctionListIndividualAliasName,
    SanctionListIndividualCountries,
    SanctionListIndividualDateOfBirth,
    SanctionListIndividualDocument,
    SanctionListIndividualNationalities,
)


class SanctionListIndividualNode(DjangoObjectType):
    country_of_birth = graphene.String(description="Country of birth")

    class Meta:
        model = SanctionListIndividual
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_country_of_birth(self, info):
        return self.country_of_birth.name


class SanctionListIndividualDocumentNode(DjangoObjectType):
    issuing_country = graphene.String(description="Issuing country name")

    class Meta:
        model = SanctionListIndividualDocument
        exclude = ("individual",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_issuing_country(self, info):
        return self.issuing_country.name


class SanctionListIndividualNationalitiesNode(DjangoObjectType):
    nationality = graphene.String()

    class Meta:
        model = SanctionListIndividualNationalities
        exclude = ("individual",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_nationality(self, info):
        return self.nationality.name


class SanctionListIndividualCountriesNode(DjangoObjectType):
    country = graphene.String()

    class Meta:
        model = SanctionListIndividualCountries
        exclude = ("individual",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_country(self, info):
        return self.country.name


class SanctionListIndividualAliasNameNode(DjangoObjectType):
    class Meta:
        model = SanctionListIndividualAliasName
        exclude = ("individual",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class SanctionListIndividualDateOfBirthNode(DjangoObjectType):
    class Meta:
        model = SanctionListIndividualDateOfBirth
        exclude = ("individual",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    sanction_list_individual = relay.Node.Field(SanctionListIndividualNode)
    all_sanction_list_individuals = DjangoPermissionFilterConnectionField(
        SanctionListIndividualNode,
        filterset_class=SanctionListIndividualFilter,
    )
