from typing import Any

from django.contrib.auth import get_user_model
from django.db.models.signals import m2m_changed, post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone

from hct_mis_api.apps.account.models import Partner, Role, User, UserRole
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.models import Program, ProgramPartnerThrough


@receiver(post_save, sender=UserRole)
def post_save_userrole(sender: Any, instance: User, *args: Any, **kwargs: Any) -> None:
    instance.user.last_modify_date = timezone.now()
    instance.user.save()


@receiver(pre_delete, sender=UserRole)
def pre_delete_userrole(sender: Any, instance: User, *args: Any, **kwargs: Any) -> None:
    instance.user.last_modify_date = timezone.now()
    instance.user.save()


@receiver(pre_save, sender=get_user_model())
def pre_save_user(sender: Any, instance: User, *args: Any, **kwargs: Any) -> None:
    instance.available_for_export = True
    instance.last_modify_date = timezone.now()


@receiver(post_save, sender=get_user_model())
def post_save_user(sender: Any, instance: User, created: bool, *args: Any, **kwargs: Any) -> None:
    if created is False:
        return

    business_area = BusinessArea.objects.filter(slug="global").first()
    role = Role.objects.filter(name="Basic User").first()
    if business_area and role:
        UserRole.objects.get_or_create(business_area=business_area, user=instance, role=role)


@receiver(m2m_changed, sender=Partner.allowed_business_areas.through)
def allowed_business_areas_changed(sender: Any, instance: Partner, action: str, pk_set: set, **kwargs: Any) -> None:
    if action == "post_add":
        added_business_areas_ids = pk_set
        programs_to_add_access = Program.objects.filter(
            business_area_id__in=added_business_areas_ids,
            partner_access=Program.ALL_PARTNERS_ACCESS,
        )
        for program in programs_to_add_access:
            program_partner = ProgramPartnerThrough.objects.create(program=program, partner=instance)
            program_partner.full_area_access = True
            program_partner.save()

    elif action == "post_remove":
        removed_business_areas_ids = pk_set
        programs_to_remove_access = Program.objects.filter(
            business_area_id__in=removed_business_areas_ids,
            partner_access=Program.ALL_PARTNERS_ACCESS,
        )
        for program in programs_to_remove_access:
            program.partners.remove(instance)

    elif action == "pre_clear":
        instance._removed_business_areas = list(instance.allowed_business_areas.all())

    elif action == "post_clear":
        removed_business_areas = getattr(instance, "_removed_business_areas", [])
        programs_to_remove_access = Program.objects.filter(
            business_area__in=removed_business_areas,
            partner_access=Program.ALL_PARTNERS_ACCESS,
        )
        for program in programs_to_remove_access:
            program.partners.remove(instance)
