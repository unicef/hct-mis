from typing import Dict, Optional

from django import forms
from django.core.exceptions import ValidationError
from django.forms import HiddenInput

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import Household, XlsxUpdateFile
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.targeting.models import TargetPopulation


class UpdateByXlsxStage1Form(forms.Form):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all())
    registration_data_import = forms.ModelChoiceField(queryset=RegistrationDataImport.objects.all())
    file = forms.FileField()

    def clean_registration_data_import(self) -> Optional[RegistrationDataImport]:
        data = self.cleaned_data.get("registration_data_import")

        if not data:
            return None

        registration_data_import = self._retrieve_rdi_by_name()

        self._check_rdi_has_correct_business_area(registration_data_import)

        return registration_data_import

    def _check_rdi_has_correct_business_area(self, registration_data_import) -> None:
        business_area = self.cleaned_data.get("business_area")
        if registration_data_import.business_area != business_area:
            raise ValidationError("Rdi should belong to selected business area")

    def _retrieve_rdi_by_name(self) -> RegistrationDataImport:
        data = self.cleaned_data.get("registration_data_import")
        registration_data_import = RegistrationDataImport.objects.filter(name=data).first()
        if not registration_data_import:
            raise ValidationError(f"Rdi with the name {data} doesn't exist")
        return registration_data_import


class UpdateByXlsxStage2Form(forms.Form):
    xlsx_update_file = forms.ModelChoiceField(queryset=XlsxUpdateFile.objects.all(), widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs) -> None:
        self.xlsx_columns = kwargs.pop("xlsx_columns", [])
        super().__init__(*args, **kwargs)
        self.fields["xlsx_match_columns"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=[(xlsx_column, xlsx_column) for xlsx_column in self.xlsx_columns],
        )

    def clean_xlsx_match_columns(self) -> Dict:
        data = self.cleaned_data["xlsx_match_columns"]
        required_columns = {"individual__unicef_id", "household__unicef_id"}
        all_columns = set(self.xlsx_columns)
        required_columns_in_this_form = all_columns & required_columns
        columns_not_found = required_columns_in_this_form - set(data)
        if not len(columns_not_found):
            return data
        raise ValidationError("Unicef Id columns have to be selected")


class UpdateIndividualsIBANFromXlsxForm(forms.Form):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all())
    file = forms.FileField()


class WithdrawForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    reason = forms.CharField(label="Log message", max_length=100, required=False)
    tag = forms.SlugField(
        max_length=100,
        required=False,
        help_text="HH will have a user_field with this name with value 'True'",
    )


class RestoreForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    reason = forms.CharField(label="Log message", max_length=100, required=False)
    reopen_tickets = forms.BooleanField(required=False, help_text="Restore all previously closed tickets")


class MassWithdrawForm(WithdrawForm):
    pass


class AddToTargetPopulationForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    action = forms.CharField(widget=forms.HiddenInput)
    target_population = forms.ModelChoiceField(
        queryset=TargetPopulation.objects.filter(status=TargetPopulation.STATUS_OPEN)
    )

    def __init__(self, *args, **kwargs) -> None:
        read_only = kwargs.pop("read_only", False)
        super().__init__(*args, **kwargs)
        if read_only:
            self.fields["target_population"].widget = HiddenInput()


class CreateTargetPopulationForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    action = forms.CharField(widget=forms.HiddenInput)
    name = forms.CharField()
    program = forms.ModelChoiceField(queryset=Program.objects.filter(status=Program.ACTIVE))

    def __init__(self, *args, **kwargs) -> None:
        read_only = kwargs.pop("read_only", False)
        super().__init__(*args, **kwargs)
        if "initial" in kwargs:
            first = Household.objects.get(pk=kwargs["initial"]["_selected_action"][0])
            self.fields["program"].queryset = Program.objects.filter(
                status=Program.ACTIVE, business_area=first.business_area
            )

        if read_only:
            self.fields["program"].widget = HiddenInput()
            self.fields["name"].widget = HiddenInput()
