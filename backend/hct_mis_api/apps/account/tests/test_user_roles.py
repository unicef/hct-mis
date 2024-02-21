from typing import List

from django.forms.models import inlineformset_factory
from django.forms.utils import ErrorList
from django.test import TestCase

from hct_mis_api.apps.account.admin.forms import (
    UserRoleAdminForm,
    UserRoleInlineFormSet,
)
from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import IncompatibleRoles, Role, User, UserRole
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea


class UserRolesTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.role_1 = Role.objects.create(name="Role_1")
        cls.role_2 = Role.objects.create(name="Role_2")
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory()

    def test_user_can_be_assigned_role(self) -> None:
        data = {"role": self.role_1.id, "user": self.user.id, "business_area": self.business_area.id}
        form = UserRoleAdminForm(data=data)
        self.assertTrue(form.is_valid())

    def test_user_cannot_be_assigned_incompatible_role_in_same_business_area(self) -> None:
        IncompatibleRoles.objects.create(role_one=self.role_1, role_two=self.role_2)
        user_role = UserRole.objects.create(role=self.role_1, business_area=self.business_area, user=self.user)

        data = {"role": self.role_2.id, "user": self.user.id, "business_area": self.business_area.id}
        form = UserRoleAdminForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("role", form.errors.keys())
        self.assertIn(f"This role is incompatible with {self.role_1.name}", form.errors["role"])

        # reverse role from incompatible roles pair
        user_role.role = self.role_2
        user_role.save()
        data["role"] = self.role_1.id
        form = UserRoleAdminForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("role", form.errors.keys())
        self.assertIn(f"This role is incompatible with {self.role_2.name}", form.errors["role"])

    def test_assign_multiple_roles_for_user_at_the_same_time(self) -> None:
        data = {
            "user_roles-TOTAL_FORMS": "2",
            "user_roles-INITIAL_FORMS": "0",
            "user_roles-0-role": self.role_1.id,
            "user_roles-1-role": self.role_2.id,
            "user_roles-0-business_area": self.business_area.id,
            "user_roles-1-business_area": self.business_area.id,
        }
        UserRoleFormSet = inlineformset_factory(User, UserRole, fields=("__all__"), formset=UserRoleInlineFormSet)
        formset = UserRoleFormSet(instance=self.user, data=data)
        self.assertTrue(formset.is_valid())

    def test_assign_multiple_roles_for_user_at_the_same_time_fails_for_incompatible_roles(self) -> None:
        IncompatibleRoles.objects.create(role_one=self.role_1, role_two=self.role_2)

        data = {
            "user_roles-TOTAL_FORMS": "2",
            "user_roles-INITIAL_FORMS": "0",
            "user_roles-0-role": self.role_1.id,
            "user_roles-1-role": self.role_2.id,
            "user_roles-0-business_area": self.business_area.id,
            "user_roles-1-business_area": self.business_area.id,
        }
        UserRoleFormSet = inlineformset_factory(User, UserRole, fields=("__all__"), formset=UserRoleInlineFormSet)
        formset = UserRoleFormSet(instance=self.user, data=data)
        self.assertFalse(formset.is_valid())
        self.assertEqual(len(formset.errors), 2)

        errors: List[ErrorList] = formset.errors
        role = errors[0]["role"]  # type: ignore # mypy doesn't see that you can call __getitem__ with str on ErrorList
        self.assertIn(f"{self.role_1.name} is incompatible with {self.role_2.name}.", role)

    def test_user_role_exclude_by_expiry_date(self) -> None:
        user_not_unicef_partner = UserFactory(partner=PartnerFactory(name="Test123"))
        role_1 = Role.objects.create(name="111", permissions=[Permissions.RDI_VIEW_LIST.value])
        role_2 = Role.objects.create(name="222", permissions=[Permissions.REPORTING_EXPORT.value])
        # user_role_active
        user_role_1 = UserRole.objects.create(
            role=role_1, business_area=self.business_area, user=user_not_unicef_partner
        )
        # user_role_inactive
        user_role_2 = UserRole.objects.create(
            role=role_2, business_area=self.business_area, user=user_not_unicef_partner, expiry_date="2024-02-16"
        )

        self.assertEqual(
            user_not_unicef_partner.permissions_in_business_area(self.business_area.slug),
            [Permissions.RDI_VIEW_LIST.value],
        )
        self.assertTrue(
            user_not_unicef_partner.cached_has_user_roles_for_business_area_and_permission(
                self.business_area, Permissions.RDI_VIEW_LIST.value
            )
        )
        self.assertFalse(
            user_not_unicef_partner.cached_has_user_roles_for_business_area_and_permission(
                self.business_area, Permissions.REPORTING_EXPORT.value
            )
        )

        user_role_1.expiry_date = "2024-02-02"
        user_role_1.save()
        user_role_1.refresh_from_db()
        self.assertEqual(str(user_role_1.expiry_date), "2024-02-02")
        self.assertEqual(str(user_role_2.expiry_date), "2024-02-16")
        # empty list
        self.assertEqual(
            user_not_unicef_partner.permissions_in_business_area(self.business_area.slug),
            [],
        )
        self.assertFalse(
            user_not_unicef_partner.cached_has_user_roles_for_business_area_and_permission(
                self.business_area, Permissions.RDI_VIEW_LIST.value
            )
        )
        self.assertFalse(
            user_not_unicef_partner.cached_has_user_roles_for_business_area_and_permission(
                self.business_area, Permissions.REPORTING_EXPORT.value
            )
        )
