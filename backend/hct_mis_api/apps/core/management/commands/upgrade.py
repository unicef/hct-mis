from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command("collectstatic", interactive=False)
        call_command("migratealldb")
        call_command("generateroles")
        from adminactions.perms import create_extra_permissions

        create_extra_permissions()
