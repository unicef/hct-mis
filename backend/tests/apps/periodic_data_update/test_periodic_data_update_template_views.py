from typing import Callable

import freezegun
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.periodic_data_update.fixtures import (
    PeriodicDataUpdateTemplateFactory,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory

pytestmark = pytest.mark.django_db


@freezegun.freeze_time("2022-01-01")
class TestPeriodicDataUpdateTemplateViews:
    def set_up(self, api_client: Callable, afghanistan: BusinessAreaFactory, id_to_base64: Callable) -> None:
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)
        self.afghanistan = afghanistan
        self.program1 = ProgramFactory(business_area=self.afghanistan, name="Program1")
        self.program2 = ProgramFactory(business_area=self.afghanistan, name="Program2")

        self.pdu_template1 = PeriodicDataUpdateTemplateFactory(program=self.program1, created_by=self.user)
        self.pdu_template2 = PeriodicDataUpdateTemplateFactory(program=self.program1, created_by=self.user)
        self.pdu_template3 = PeriodicDataUpdateTemplateFactory(program=self.program1, created_by=self.user)
        self.pdu_template_program2 = PeriodicDataUpdateTemplateFactory(program=self.program2)
        self.url_list = reverse(
            "api:periodic-data-update:periodic-data-update-templates-list",
            kwargs={
                "business_area": self.afghanistan.slug,
                "program_id": id_to_base64(self.program1.id, "Program"),
            },
        )
        self.url_detail_pdu_template_program2 = reverse(
            "api:periodic-data-update:periodic-data-update-templates-detail",
            kwargs={
                "business_area": self.afghanistan.slug,
                "program_id": id_to_base64(self.program2.id, "Program"),
                "pk": self.pdu_template_program2.id,
            },
        )
        self.url_detail_pdu_template1 = reverse(
            "api:periodic-data-update:periodic-data-update-templates-detail",
            kwargs={
                "business_area": self.afghanistan.slug,
                "program_id": id_to_base64(self.program1.id, "Program"),
                "pk": self.pdu_template1.id,
            },
        )

    @pytest.mark.parametrize(
        "permissions, partner_permissions, access_to_program, expected_status",
        [
            ([], [], True, status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_VIEW_LIST_AND_DETAILS], [], True, status.HTTP_200_OK),
            ([], [Permissions.PDU_VIEW_LIST_AND_DETAILS], True, status.HTTP_200_OK),
            (
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                True,
                status.HTTP_200_OK,
            ),
            ([], [], False, status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_VIEW_LIST_AND_DETAILS], [], False, status.HTTP_403_FORBIDDEN),
            ([], [Permissions.PDU_VIEW_LIST_AND_DETAILS], False, status.HTTP_403_FORBIDDEN),
            (
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                False,
                status.HTTP_403_FORBIDDEN,
            ),
        ],
    )
    def test_list_periodic_data_update_templates_permission(
        self,
        permissions: list,
        partner_permissions: list,
        access_to_program: bool,
        expected_status: str,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        create_partner_role_with_permissions: Callable,
        update_partner_access_to_program: Callable,
        id_to_base64: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan, id_to_base64)
        create_user_role_with_permissions(
            self.user,
            permissions,
            self.afghanistan,
        )
        create_partner_role_with_permissions(self.partner, partner_permissions, self.afghanistan)
        if access_to_program:
            update_partner_access_to_program(self.partner, self.program1)

        response = self.client.get(self.url_list)
        assert response.status_code == expected_status

    def test_list_periodic_data_update_templates(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        id_to_base64: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan, id_to_base64)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            self.afghanistan,
            self.program1,
        )
        response = self.client.get(self.url_list)
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()["results"]
        assert len(response_json) == 3

        assert {
            "id": self.pdu_template1.id,
            "status": self.pdu_template1.status,
            "number_of_records": self.pdu_template1.number_of_records,
            "created_at": "2022-01-01T00:00:00Z",
            "created_by": self.pdu_template1.created_by.get_full_name(),
        } in response_json
        assert {
            "id": self.pdu_template2.id,
            "status": self.pdu_template2.status,
            "number_of_records": self.pdu_template2.number_of_records,
            "created_at": "2022-01-01T00:00:00Z",
            "created_by": self.pdu_template2.created_by.get_full_name(),
        } in response_json
        assert {
            "id": self.pdu_template3.id,
            "status": self.pdu_template3.status,
            "number_of_records": self.pdu_template3.number_of_records,
            "created_at": "2022-01-01T00:00:00Z",
            "created_by": self.pdu_template3.created_by.get_full_name(),
        } in response_json
        assert {
            "id": self.pdu_template_program2.id,
            "status": self.pdu_template_program2.status,
            "number_of_records": self.pdu_template_program2.number_of_records,
            "created_at": "2022-01-01T00:00:00Z",
            "created_by": self.pdu_template_program2.created_by.get_full_name(),
        } not in response_json

    @pytest.mark.parametrize(
        "permissions, partner_permissions, access_to_program, expected_status",
        [
            ([], [], True, status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_VIEW_LIST_AND_DETAILS], [], True, status.HTTP_200_OK),
            ([], [Permissions.PDU_VIEW_LIST_AND_DETAILS], True, status.HTTP_200_OK),
            (
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                True,
                status.HTTP_200_OK,
            ),
            ([], [], False, status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_VIEW_LIST_AND_DETAILS], [], False, status.HTTP_403_FORBIDDEN),
            ([], [Permissions.PDU_VIEW_LIST_AND_DETAILS], False, status.HTTP_403_FORBIDDEN),
            (
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                False,
                status.HTTP_403_FORBIDDEN,
            ),
        ],
    )
    def test_detail_periodic_data_update_template_permission(
        self,
        permissions: list,
        partner_permissions: list,
        access_to_program: bool,
        expected_status: str,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        create_partner_role_with_permissions: Callable,
        update_partner_access_to_program: Callable,
        id_to_base64: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan, id_to_base64)
        create_user_role_with_permissions(
            self.user,
            permissions,
            self.afghanistan,
        )
        create_partner_role_with_permissions(self.partner, partner_permissions, self.afghanistan)
        if access_to_program:
            update_partner_access_to_program(self.partner, self.program2)

        response = self.client.get(self.url_detail_pdu_template_program2)
        assert response.status_code == expected_status

        # no access to pdu_template1 for any case as it is in Program1 and user has access to Program2
        response_forbidden = self.client.get(self.url_detail_pdu_template1)
        assert response_forbidden.status_code == 403

    def test_detail_periodic_data_update_templates(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        id_to_base64: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan, id_to_base64)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            self.afghanistan,
            self.program2,
        )

        response = self.client.get(self.url_detail_pdu_template_program2)
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert {
            "id": self.pdu_template_program2.id,
            "rounds_data": self.pdu_template_program2.rounds_data,
        } == response_json
