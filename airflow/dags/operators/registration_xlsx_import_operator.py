from .base import DjangoOperator


class RegistrationXLSXImportOperator(DjangoOperator):
    def execute(self, context, **kwargs):
        from hct_mis_api.apps.registration_datahub.tasks.rdi_create import RdiXlsxCreateTask

        dag_run = context["dag_run"]
        config_vars = dag_run.conf

        task = RdiXlsxCreateTask()
        task.execute(
            registration_data_import_id=config_vars.get(
                "registration_data_import_id"
            ),
            import_data_id=config_vars.get("import_data_id"),
            business_area_id=config_vars.get("business_area"),
        )
