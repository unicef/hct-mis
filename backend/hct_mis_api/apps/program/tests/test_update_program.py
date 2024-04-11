from typing import Any, List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    create_afghanistan,
    generate_data_collecting_types,
)
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.geo.fixtures import AreaFactory, CountryFactory, AreaTypeFactory
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramPartnerThrough


class TestUpdateProgram(APITestCase):
    UPDATE_PROGRAM_MUTATION = """
    mutation UpdateProgram($programData: UpdateProgramInput, $version: BigInt) {
      updateProgram(programData: $programData, version: $version) {
        program {
          name
          status
          dataCollectingType {
            label
            code
          }
          partners {   
            partnerName       
            areas {
              name
            }
          }
          partnerAccess
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        generate_data_collecting_types()
        data_collecting_type = DataCollectingType.objects.get(code="full_collection")

        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.business_area.data_collecting_types.set(DataCollectingType.objects.all().values_list("id", flat=True))
        cls.unicef_partner = PartnerFactory(name="UNICEF")

        cls.program = ProgramFactory.create(
            name="initial name",
            status=Program.DRAFT,
            business_area=cls.business_area,
            data_collecting_type=data_collecting_type,
            partner_access=Program.NONE_PARTNERS_ACCESS,
        )
        unicef_program = ProgramPartnerThrough.objects.create(
            program=cls.program,
            partner=cls.unicef_partner,
        )
        cls.program_finished = ProgramFactory.create(
            status=Program.FINISHED,
            business_area=cls.business_area,
        )

        cls.partner = PartnerFactory(name="WFP")
        cls.user = UserFactory.create(partner=cls.partner)

        cls.other_partner = PartnerFactory(name="Other Partner")
        cls.other_partner.allowed_business_areas.set([cls.business_area])
        cls.partner_not_allowed_in_BA = PartnerFactory(name="Partner not allowed in BA")

        country_afg = CountryFactory(name="Afghanistan")
        country_afg.business_areas.set([cls.business_area])
        area_type_afg = AreaTypeFactory(name="Area Type in Afg", country=country_afg)
        country_other = CountryFactory(name="Other Country", short_name="Oth",
            iso_code2="O",
            iso_code3="OTH",
            iso_num="111",
        )
        cls.area_type_other = AreaTypeFactory(name="Area Type Other", country=country_other)

        cls.area_in_afg_1 = AreaFactory(name="Area in AFG 1", area_type=area_type_afg)
        cls.area_in_afg_2 = AreaFactory(name="Area in AFG 2", area_type=area_type_afg)
        cls.area_not_in_afg = AreaFactory(name="Area not in AFG", area_type=cls.area_type_other)

        unicef_program.areas.set([cls.area_in_afg_1, cls.area_in_afg_2])

    def test_update_program_not_authenticated(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "updated name",
                    "status": Program.ACTIVE,
                    "partnerAccess": Program.NONE_PARTNERS_ACCESS,
                },
                "version": self.program.version,
            },
        )

    @parameterized.expand(
        [
            ("with_permissions", [Permissions.PROGRAMME_UPDATE, Permissions.PROGRAMME_ACTIVATE], True),
            (
                "with_partial_permissions",
                [
                    Permissions.PROGRAMME_UPDATE,
                ],
                False,
            ),
            ("without_permissions", [], False),
        ]
    )
    def test_update_program_authenticated(
        self, _: Any, permissions: List[Permissions], should_be_updated: bool
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "updated name",
                    "status": Program.ACTIVE,
                    "dataCollectingTypeCode": "partial_individuals",
                },
                "version": self.program.version,
            },
        )
        updated_program = Program.objects.get(id=self.program.id)
        if should_be_updated:
            assert updated_program.status == Program.ACTIVE
            assert updated_program.name == "updated name"
        else:
            assert updated_program.status == Program.DRAFT
            assert updated_program.name == "initial name"

    @parameterized.expand(
        [
            ("valid", Program.SELECTED_PARTNERS_ACCESS),
            ("invalid_all_partner_access", Program.ALL_PARTNERS_ACCESS),
            ("invalid_none_partner_access", Program.NONE_PARTNERS_ACCESS),
        ]
    )
    def test_update_program_partners(self, _: Any, partner_access: str) -> None:
        area1 = AreaFactory(name="Area1", area_type=self.area_type_other)
        area2 = AreaFactory(name="Area2", area_type=self.area_type_other)
        area_to_be_unselected = AreaFactory(name="AreaToBeUnselected", area_type=self.area_type_other)
        program_partner = ProgramPartnerThrough.objects.create(
            program=self.program,
            partner=self.partner,
        )
        program_partner.areas.set([area1, area_to_be_unselected])
        ProgramPartnerThrough.objects.create(
            program=self.program,
            partner=self.other_partner,
        )
        partner_to_be_added = PartnerFactory(name="Partner to be added")
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "updated name",
                    "status": Program.DRAFT,
                    "dataCollectingTypeCode": "partial_individuals",
                    "partners": [
                        {
                            "partner": str(self.partner.id),
                            "areas": [str(area1.id), str(area2.id)],
                        },
                        {
                            "partner": str(partner_to_be_added.id),
                            "areas": [str(area1.id), str(area2.id)],
                        },
                    ],
                    "partnerAccess": partner_access,
                },
                "version": self.program.version,
            },
        )

    def test_update_program_partners_invalid_access_type_from_object(self) -> None:
        area1 = AreaFactory(name="Area1", area_type=self.area_type_other)
        area2 = AreaFactory(name="Area2", area_type=self.area_type_other)
        area_to_be_unselected = AreaFactory(name="AreaToBeUnselected", area_type=self.area_type_other)
        program_partner = ProgramPartnerThrough.objects.create(
            program=self.program,
            partner=self.partner,
        )
        program_partner.areas.set([area1, area_to_be_unselected])
        ProgramPartnerThrough.objects.create(
            program=self.program,
            partner=self.other_partner,
        )
        partner_to_be_added = PartnerFactory(name="Partner to be added")
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "updated name",
                    "status": Program.DRAFT,
                    "dataCollectingTypeCode": "partial_individuals",
                    "partners": [
                        {
                            "partner": str(self.partner.id),
                            "areas": [str(area1.id), str(area2.id)],
                        },
                        {
                            "partner": str(partner_to_be_added.id),
                            "areas": [str(area1.id), str(area2.id)],
                        },
                    ],
                },
                "version": self.program.version,
            },
        )


    def test_update_program_partners_all_partners_access(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "updated name",
                    "status": Program.DRAFT,
                    "dataCollectingTypeCode": "partial_individuals",
                    "partnerAccess": Program.ALL_PARTNERS_ACCESS,
                },
                "version": self.program.version,
            },
        )

    def test_update_active_program_with_dct(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)
        data_collecting_type = DataCollectingType.objects.get(code="full_collection")
        data_collecting_type.limit_to.add(self.business_area)
        Program.objects.filter(id=self.program.id).update(
            status=Program.ACTIVE, data_collecting_type=data_collecting_type
        )

        self.program.refresh_from_db()
        self.assertEqual(self.program.status, Program.ACTIVE)
        self.assertEqual(self.program.data_collecting_type.code, "full_collection")

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "dataCollectingTypeCode": "partial_individuals",
                },
                "version": self.program.version,
            },
        )
        self.assertEqual(self.program.data_collecting_type.code, "full_collection")

    def test_update_draft_not_empty_program_with_dct(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)
        data_collecting_type = DataCollectingType.objects.get(code="full_collection")
        data_collecting_type.limit_to.add(self.business_area)
        create_household(household_args={"program": self.program})

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "dataCollectingTypeCode": "partial_individuals",
                },
                "version": self.program.version,
            },
        )
        self.assertEqual(self.program.data_collecting_type.code, "full_collection")


    def test_update_program_with_deprecated_dct(self) -> None:
        dct, _ = DataCollectingType.objects.update_or_create(
            **{"label": "Deprecated", "code": "deprecated", "description": "Deprecated", "deprecated": True}
        )
        dct.limit_to.add(self.business_area)

        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "dataCollectingTypeCode": "deprecated",
                },
                "version": self.program.version,
            },
        )

    def test_update_program_with_inactive_dct(self) -> None:
        dct, _ = DataCollectingType.objects.update_or_create(
            **{"label": "Inactive", "code": "inactive", "description": "Inactive", "active": False}
        )
        dct.limit_to.add(self.business_area)

        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "dataCollectingTypeCode": "inactive",
                },
                "version": self.program.version,
            },
        )

    def test_update_program_with_dct_from_other_ba(self) -> None:
        other_ba = BusinessAreaFactory()
        dct, _ = DataCollectingType.objects.update_or_create(
            **{"label": "Test Wrong BA", "code": "test_wrong_ba", "description": "Test Wrong BA"}
        )
        dct.limit_to.add(other_ba)
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CREATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "dataCollectingTypeCode": "test_wrong_ba",
                },
                "version": self.program.version,
            },
        )

    def test_update_program_when_finished(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program_finished.id, "ProgramNode"),
                    "name": "xyz",
                },
                "version": self.program_finished.version,
            },
        )

    def test_update_program_of_other_partner_raise_error(self) -> None:
        partner = PartnerFactory(name="UHCR")
        another_partner = PartnerFactory(name="WFP")
        user = UserFactory.create(partner=partner)
        self.create_user_role_with_permissions(user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "xyz",
                    "partnerAccess": Program.SELECTED_PARTNERS_ACCESS,
                    "partners": [
                        {
                            "partner": str(another_partner.id),
                            "areas": [],
                        },
                    ],
                },
                "version": self.program.version,
            },
        )

    def test_update_program_with_programme_code(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        x = self.graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "xyz",
                    "programmeCode": "ab/2",
                },
                "version": self.program.version,
            },
        )
        program = Program.objects.get(id=self.program.id)
        self.assertIsNotNone(program.programme_code)
        self.assertEqual(program.programme_code, "AB/2")

    def test_update_program_without_programme_code(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        self.program.programme_code = ""
        self.program.save()

        self.graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "xyz",
                    "programmeCode": "",
                },
                "version": self.program.version,
            },
        )
        program = Program.objects.get(id=self.program.id)
        self.assertIsNotNone(program.programme_code)
        self.assertEqual(len(program.programme_code), 4)

    def test_update_program_with_duplicated_programme_code_among_the_same_business_area(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        ProgramFactory(programme_code="ABC2", business_area=self.business_area)
        self.program.programme_code = "ABC3"
        self.program.save()

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "xyz",
                    "programmeCode": "abc2",
                },
                "version": self.program.version,
            },
        )
        program = Program.objects.get(id=self.program.id)
        self.assertIsNotNone(program.programme_code)
        self.assertEqual(len(program.programme_code), 4)
        self.assertEqual(program.programme_code, "ABC3")
