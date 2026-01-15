from django import forms
from .models import Profile, Role, Permission


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})


class RoleForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Role
        fields = ["name", "description", "permissions"]

    def __init__(self, *args, **kwargs):
        permissions_queryset = kwargs.pop("permissions_queryset", Permission.objects.none())
        super().__init__(*args, **kwargs)

        self.fields["permissions"].queryset = permissions_queryset.order_by("name")

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({"class": "list-unstyled"})
            else:
                field.widget.attrs.update({"class": "form-control"})
