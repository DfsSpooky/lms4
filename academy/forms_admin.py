from django import forms
from django.contrib.auth.models import User
from .models import Profile, HeroSlide, Category, CertificationCard, AnnouncementCard, Institution, PaymentMethod, TopBanner, SiteConfiguration

class AdminUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Contraseña")
    role = forms.ChoiceField(choices=[('student', 'Estudiante'), ('teacher', 'Profesor')], required=True, label="Rol")

    # Extra fields usually needed for creating a user
    first_name = forms.CharField(max_length=150, required=True, label="Nombres")
    last_name = forms.CharField(max_length=150, required=True, label="Apellidos")
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Handle Profile role
            if hasattr(user, 'profile'):
                user.profile.role = self.cleaned_data['role']
                user.profile.save()
            else:
                Profile.objects.create(user=user, role=self.cleaned_data['role'])
        return user

class HeroSlideForm(forms.ModelForm):
    class Meta:
        model = HeroSlide
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'description': forms.Textarea(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white', 'rows': 3}),
            'style': forms.Select(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'tag_text': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'btn1_text': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'btn1_url': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'btn2_text': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'btn2_url': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'order': forms.NumberInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'slug': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'icon': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white', 'placeholder': 'fas fa-code'}),
        }

class CertificationCardForm(forms.ModelForm):
    class Meta:
        model = CertificationCard
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'subtitle': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'provider': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'icon_class': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'rating': forms.NumberInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white', 'step': '0.1'}),
            'reviews_count': forms.NumberInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'style': forms.Select(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'url': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'order': forms.NumberInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
        }

class AnnouncementCardForm(forms.ModelForm):
    class Meta:
        model = AnnouncementCard
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'description': forms.Textarea(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white', 'rows': 3}),
            'btn_text': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'btn_url': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'style': forms.Select(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'order': forms.NumberInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
        }

class InstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'website': forms.URLInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
        }

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'account_info': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'instructions': forms.Textarea(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white', 'rows': 3}),
            'color': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
        }

class TopBannerForm(forms.ModelForm):
    class Meta:
        model = TopBanner
        fields = '__all__'
        widgets = {
            'message': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'sub_message': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'btn_text': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'btn_url': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'style': forms.Select(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-indigo-600 bg-slate-800 border-slate-600 rounded focus:ring-indigo-500'}),
        }

class SiteConfigurationForm(forms.ModelForm):
    class Meta:
        model = SiteConfiguration
        fields = '__all__'
        widgets = {
            'site_name': forms.TextInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'logo_width': forms.NumberInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
            'logo_height': forms.NumberInput(attrs={'class': 'block w-full rounded-lg bg-slate-800 border-slate-600 text-white'}),
        }
