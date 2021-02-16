from .base import DjangoOperator


class RDIDeduplicationOperator(DjangoOperator):
    def try_execute(self, context, **kwargs):
        from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask
        from hct_mis_api.apps.registration_datahub.models import RegistrationDataImportDatahub

        dag_run = context["dag_run"]
        config_vars = dag_run.conf

        registration_data_import_id = config_vars.get(
            "registration_data_import_id"
        )
        rdi_obj = RegistrationDataImportDatahub.objects.get(
            id=registration_data_import_id
        )

        DeduplicateTask.deduplicate_imported_individuals(
            registration_data_import_datahub=rdi_obj
        )
