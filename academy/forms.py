from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Enrollment, Course, LessonComment, LessonProgress, Installment, Ticket, TicketTier, Event
from .forms_content import *
from django.forms import inlineformset_factory
from tinymce.widgets import TinyMCE

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, label='Nombres')
    last_name = forms.CharField(max_length=150, required=True, label='Apellidos')
    email = forms.EmailField(required=True, label='Correo Electrónico')

    # Campos del Perfil
    dni = forms.CharField(max_length=8, min_length=8, required=True, label='DNI', help_text="8 dígitos")
    address = forms.CharField(max_length=255, required=True, label='Dirección')
    academic_profile = forms.ChoiceField(choices=Profile.ACADEMIC_CHOICES, label='Perfil Académico')
    gender = forms.ChoiceField(choices=[('male', 'Masculino'), ('female', 'Femenino')], label='Género')
    phone_number = forms.CharField(max_length=20, required=True, label='Celular')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            return email
        domain = email.split('@')[1].lower()
        allowed_domains = ['gmail.com', 'outlook.com', 'hotmail.com', 'live.com']
        is_edu = '.edu' in domain
        if domain not in allowed_domains and not is_edu:
            raise forms.ValidationError("Solo se permiten correos de Gmail, Microsoft o educativos (.edu)")
        return email

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if not dni.isdigit():
            raise forms.ValidationError("El DNI debe contener solo números.")
        if len(dni) != 8:
            raise forms.ValidationError("El DNI debe tener exactamente 8 dígitos.")
        return dni

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            if hasattr(user, 'profile'):
                profile = user.profile
                profile.dni = self.cleaned_data['dni']
                profile.address = self.cleaned_data['address']
                profile.academic_profile = self.cleaned_data['academic_profile']
                profile.gender = self.cleaned_data['gender']
                profile.phone_number = self.cleaned_data['phone_number']
                profile.save()
        return user

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    # Hacer explícitamente obligatorios los campos para la edición de perfil (ej. al completar registro Google)
    dni = forms.CharField(max_length=8, min_length=8, required=True, label='DNI', help_text="8 dígitos")
    phone_number = forms.CharField(max_length=20, required=True, label='Celular')
    address = forms.CharField(max_length=255, required=True, label='Dirección')

    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'dni', 'address', 'academic_profile', 'gender', 'phone_number', 'facebook_url', 'website']

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if dni:
            if not dni.isdigit():
                raise forms.ValidationError("El DNI debe contener solo números.")
            if len(dni) != 8:
                raise forms.ValidationError("El DNI debe tener exactamente 8 dígitos.")
        return dni

# --- FORMULARIOS PARA EL FLUJO DE PAGO E INSCRIPCIÓN ---

class EnrollmentDataForm(forms.ModelForm):
    first_name = forms.CharField(label="Nombres", max_length=150, required=True)
    last_name = forms.CharField(label="Apellidos", max_length=150, required=True)
    dni = forms.CharField(label="DNI", max_length=8, min_length=8, help_text="8 dígitos numéricos")
    address = forms.CharField(label="Dirección", max_length=255, required=True)
    academic_profile = forms.ChoiceField(label="Perfil Académico", choices=Profile.ACADEMIC_CHOICES)

    class Meta:
        model = Profile
        fields = ['dni', 'address', 'academic_profile']
    
    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if not dni.isdigit():
            raise forms.ValidationError("El DNI debe contener solo números.")
        return dni

class VoucherUploadForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['voucher_image']
        widgets = {
            'voucher_image': forms.FileInput(attrs={
                'class': 'absolute inset-0 w-full h-full opacity-0 cursor-pointer z-50',
                'accept': 'image/*',
                'onchange': 'updateFileName(this)'
            }),
        }

class InstallmentVoucherForm(forms.ModelForm):
    class Meta:
        model = Installment
        fields = ['voucher_image']
        widgets = {
            'voucher_image': forms.FileInput(attrs={
                'class': 'w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer',
                'accept': 'image/*'
            }),
        }

class TicketVoucherForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['voucher_image']
        widgets = {
             'voucher_image': forms.FileInput(attrs={
                'class': 'w-full bg-slate-900/50 border border-slate-600 rounded-xl px-4 py-3 text-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 transition-all cursor-pointer',
                'accept': 'image/*'
            }),
        }

class TicketTierForm(forms.ModelForm):
    class Meta:
        model = TicketTier
        fields = ['name', 'price', 'capacity', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white', 'placeholder': 'Ej: VIP'}),
            'price': forms.NumberInput(attrs={'class': 'w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white', 'placeholder': '0.00'}),
            'capacity': forms.NumberInput(attrs={'class': 'w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white', 'placeholder': '100'}),
            'description': forms.Textarea(attrs={'class': 'w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white', 'rows': 2, 'placeholder': 'Descripción...'})
        }

TicketTierFormSet = inlineformset_factory(
    Event, TicketTier, form=TicketTierForm,
    extra=1, can_delete=True
)

class CourseForm(forms.ModelForm):
    # --- CAMPOS PERSONALIZADOS CON WIDGETS CORREGIDOS ---
    
    # Precios
    duration_months = forms.IntegerField(
        required=False, 
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all font-mono',
            'placeholder': 'Ej: 6'
        })
    )
    monthly_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl pl-10 pr-4 py-3 text-emerald-400 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all font-mono font-bold',
            'placeholder': 'Ej: 50.00'
        })
    )

    # Fechas (CORRECCIÓN CRÍTICA: input_formats y format en el widget)
    launch_date = forms.DateTimeField(
        required=False,
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            attrs={
                'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500',
                'type': 'datetime-local'
            },
            format='%Y-%m-%dT%H:%M' # Forzar formato con 'T' para que el navegador lo lea
        )
    )
    start_date = forms.DateTimeField(
        required=False,
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            attrs={
                'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500',
                'type': 'datetime-local'
            },
            format='%Y-%m-%dT%H:%M'
        )
    )
    end_date = forms.DateTimeField(
        required=False,
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            attrs={
                'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500',
                'type': 'datetime-local'
            },
            format='%Y-%m-%dT%H:%M'
        )
    )

    class Meta:
        model = Course
        fields = [
            'title', 'category', 'course_type', 'level', 'status', 'institution',
            'price', 'old_price', 'allow_monthly_payment', 'monthly_price', 'duration_months',
            'start_date', 'end_date', 'live_url', 'launch_date',
            'preview_video_url', 'description', 'short_description', 'learning_objectives', 'requirements', 'thumbnail'
        ]
        widgets = {
            'learning_objectives': forms.Textarea(attrs={
                'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 placeholder-slate-500 transition-all resize-y font-mono text-sm',
                'rows': 5,
                'placeholder': '- Aprenderás a crear apps con Django\n- Dominarás el ORM\n- Desplegarás en producción'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 placeholder-slate-500 transition-all resize-y font-mono text-sm',
                'rows': 4,
                'placeholder': '- Conocimientos básicos de Python\n- Computadora con acceso a internet'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all cursor-pointer'
            }),
            'institution': forms.Select(attrs={
                'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all cursor-pointer'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 placeholder-slate-500 transition-all font-bold text-lg',
                'placeholder': 'Ej: Master en Python 2025'
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 placeholder-slate-500 transition-all resize-none',
                'rows': 2,
                'placeholder': 'Breve resumen para la tarjeta del curso (Max 300 caracteres)'
            }),
            'description': TinyMCE(attrs={'cols': 80, 'rows': 30}),
            'price': forms.NumberInput(attrs={
                'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl pl-10 pr-4 py-3 text-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all font-mono font-bold text-emerald-400',
                'placeholder': 'Ej: 71.00'
            }),
            'old_price': forms.NumberInput(attrs={
                'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl pl-10 pr-4 py-3 text-slate-400 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all font-mono',
                'placeholder': 'Ej: 100.00'
            }),
            'allow_monthly_payment': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-indigo-600 bg-slate-900 border-slate-700 rounded focus:ring-indigo-500 focus:ring-2',
                'x-model': 'monthlyEnabled' 
            }),
            'preview_video_url': forms.URLInput(attrs={
                'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl pl-12 pr-4 py-3 text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all',
                'placeholder': 'https://www.youtube.com/watch?v=...'
            }),
            'live_url': forms.URLInput(attrs={
                'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl pl-12 pr-4 py-3 text-white focus:ring-2 focus:ring-indigo-500',
                'placeholder': 'https://zoom.us/j/...'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all cursor-pointer'
            }),
            'level': forms.Select(attrs={
                'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all cursor-pointer'
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'hidden',
                'id': 'file-upload',
                'onchange': 'previewImage(event)'
            }),
            'course_type': forms.Select(attrs={
                'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all cursor-pointer',
                'x-model': 'courseType'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        allow_monthly = cleaned_data.get('allow_monthly_payment')
        monthly_price = cleaned_data.get('monthly_price')
        duration_months = cleaned_data.get('duration_months')
        total_price = cleaned_data.get('price') # Precio full

        if allow_monthly:
            # Si se activa el pago mensual, ES OBLIGATORIO tener precio y duración válidos
            if not monthly_price or monthly_price <= 0:
                self.add_error('monthly_price', "Debes indicar un precio mensual mayor a 0.")
            
            if not duration_months or duration_months < 1:
                self.add_error('duration_months', "La duración debe ser de al menos 1 mes.")

            # --- NUEVA VALIDACIÓN DE LÓGICA ---
            if total_price and monthly_price and duration_months:
                # Caso 1: La mensualidad es igual o mayor al precio total (y son varios meses)
                if monthly_price >= total_price and duration_months > 1:
                    self.add_error('monthly_price', "Error Lógico: La cuota mensual no puede ser igual o mayor al precio total del curso.")

                # Caso 2: El total financiado es ridículamente bajo (ej: menos del 50% del precio real)
                financed_total = monthly_price * duration_months

                # Convertir 0.5 a Decimal para evitar error de tipos
                from decimal import Decimal
                if financed_total < (total_price * Decimal('0.5')):
                    self.add_error('monthly_price', f"Cuidado: El total financiado ({financed_total}) es mucho menor al precio de contado ({total_price}). Revisa los montos.")

        else:
            # Si se DESACTIVA el pago mensual, guardamos valores seguros (0 y 1)
            cleaned_data['monthly_price'] = 0
            cleaned_data['duration_months'] = 1

        return cleaned_data

class LessonCommentForm(forms.ModelForm):
    class Meta:
        model = LessonComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full bg-slate-800 border border-slate-700 rounded-xl p-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all resize-none text-sm',
                'rows': 3,
                'placeholder': '¿Tienes alguna duda sobre esta lección? Pregunta aquí...'
            })
        }

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = LessonProgress
        fields = ['assignment_text', 'assignment_file']
        widgets = {
            'assignment_text': forms.Textarea(attrs={
                'class': 'w-full bg-slate-800 border border-slate-700 rounded-xl p-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all resize-none text-sm',
                'rows': 5,
                'placeholder': 'Escribe tu respuesta aquí...'
            }),
            'assignment_file': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer'
            })
        }

class AssignmentGradingForm(forms.ModelForm):
    class Meta:
        model = LessonProgress
        fields = ['score', 'instructor_feedback']
        widgets = {
            'score': forms.NumberInput(attrs={
                'class': 'bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 w-24',
                'placeholder': '0.00'
            }),
            'instructor_feedback': forms.Textarea(attrs={
                'class': 'w-full bg-slate-800 border border-slate-700 rounded-xl p-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all resize-none text-sm',
                'rows': 4,
                'placeholder': 'Deja tus comentarios al estudiante...'
            })
        }