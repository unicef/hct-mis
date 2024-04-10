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
from hct_mis_api.apps.geo.fixtures import AreaFactory
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

        cls.program = ProgramFactory.create(
            name="initial name",
            status=Program.DRAFT,
            business_area=cls.business_area,
            data_collecting_type=data_collecting_type,
        )
        cls.program_finished = ProgramFactory.create(
            status=Program.FINISHED,
            business_area=cls.business_area,
        )

        cls.partner = PartnerFactory(name="WFP")
        cls.user = UserFactory.create(partner=cls.partner)

    def test_update_program_not_authenticated(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "updated name",
                    "status": Program.ACTIVE,
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
                    "partners": [{"id": str(self.partner.id), "areaAccess": "BUSINESS_AREA"}],
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

    def test_update_program_partners(self) -> None:
        area1 = AreaFactory()
        area2 = AreaFactory()
        area_to_de_unselected = AreaFactory()
        existing_partner = PartnerFactory(name="Other Partner")
        program_partner = ProgramPartnerThrough.objects.create(
            program=self.program,
            partner=self.partner,
        )
        program_partner.areas.set([area1, area_to_de_unselected])
        program_partner_to_be_deleted = ProgramPartnerThrough.objects.create(
            program=self.program,
            partner=existing_partner,
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
                    "partners": [{"id": str(self.partner.id), "areaAccess": "BUSINESS_AREA"}],
                    "dataCollectingTypeCode": "partial_individuals",
                    "partnersAccess": [
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

        updated_program = Program.objects.get(id=self.program.id)
        self.assertEqual(updated_program.status, Program.DRAFT)
        self.assertEqual(updated_program.name, "updated name")
        self.assertEqual(updated_program.partners.count(), 2)
        self.assertEqual(updated_program.program_partner_through.count(), 2)
        self.assertEqual(updated_program.program_partner_through.first().areas.count(), 2)
        self.assertEqual(updated_program.program_partner_through.last().areas.count(), 2)
        self.assertIn(area1, updated_program.program_partner_through.first().areas.all())
        self.assertIn(area2, updated_program.program_partner_through.first().areas.all())
        self.assertIn(area1, updated_program.program_partner_through.last().areas.all())
        self.assertIn(area2, updated_program.program_partner_through.last().areas.all())
        self.assertNotIn(area_to_de_unselected, updated_program.program_partner_through.first().areas.all())
        self.assertNotIn(area_to_de_unselected, updated_program.program_partner_through.last().areas.all())
        self.assertFalse(ProgramPartnerThrough.objects.filter(id=program_partner_to_be_deleted.id).exists())

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
                    "partners": [{"id": str(self.partner.id), "areaAccess": "BUSINESS_AREA"}],
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
                    "partners": [{"id": str(self.partner.id), "areaAccess": "BUSINESS_AREA"}],
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
                    "partners": [{"id": str(self.partner.id), "areaAccess": "BUSINESS_AREA"}],
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
                    "partners": [{"id": str(self.partner.id), "areaAccess": "BUSINESS_AREA"}],
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
                    "partners": [{"id": str(self.partner.id), "areaAccess": "BUSINESS_AREA"}],
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
                    "partners": [{"id": str(self.partner.id), "areaAccess": "BUSINESS_AREA"}],
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
                    "partners": [{"id": str(another_partner.id), "areaAccess": "BUSINESS_AREA"}],
                },
                "version": self.program.version,
            },
        )

    def test_update_program_with_programme_code(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.business_area)

        self.graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "xyz",
                    "partners": [{"id": str(self.partner.id), "areaAccess": "BUSINESS_AREA"}],
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
                    "partners": [{"id": str(self.partner.id), "areaAccess": "BUSINESS_AREA"}],
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
                    "partners": [{"id": str(self.partner.id), "areaAccess": "BUSINESS_AREA"}],
                    "programmeCode": "abc2",
                },
                "version": self.program.version,
            },
        )
        program = Program.objects.get(id=self.program.id)
        self.assertIsNotNone(program.programme_code)
        self.assertEqual(len(program.programme_code), 4)
        self.assertEqual(program.programme_code, "ABC3")
