from django.contrib import admin
from django.utils.html import format_html
from .models import *

# --- INLINES Y CONFIGURACIÓN DE CURSOS ---

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]

class ModuleInline(admin.StackedInline):
    model = Module
    extra = 0

class CourseAdmin(admin.ModelAdmin):
    inlines = [ModuleInline]
    list_display = ('title', 'category', 'instructor', 'price', 'course_type', 'created_at')
    list_filter = ('category', 'level', 'course_type')
    search_fields = ('title', 'instructor__username')
    filter_horizontal = ('allowed_payment_methods',)

    fieldsets = (
        ('Información Principal', {
            'fields': ('title', 'slug', 'category', 'course_type', 'description', 'short_description', 'thumbnail', 'institution')
        }),
        ('Configuración de Seminario', {
            'fields': ('start_date', 'end_date', 'live_url'),
            'classes': ('collapse',),
            'description': 'Llenar solo si el tipo es "Seminario en Vivo"'
        }),
        ('Precios y Pagos', {
            'fields': ('price', 'old_price', 'allowed_payment_methods')
        }),
        ('Detalles Adicionales', {
            'fields': ('level', 'instructor', 'preview_video_url')
        }),
    )

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_info', 'color')
    search_fields = ('name', 'account_info')

# --- NUEVO: ADMINISTRACIÓN DE CATEGORÍAS ---
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon_preview', 'course_count')
    prepopulated_fields = {'slug': ('name',)} # Rellena el slug automáticamente al escribir el nombre
    search_fields = ('name',)

    def icon_preview(self, obj):
        if obj.icon:
            # Muestra el icono de FontAwesome en el admin
            return format_html('<i class="{}" style="font-size: 1.2em;"></i> <span style="color: #888;">{}</span>', obj.icon, obj.icon)
        return "-"
    icon_preview.short_description = "Icono"

    def course_count(self, obj):
        return obj.courses.count()
    course_count.short_description = "Cursos"

# --- ADMINISTRACIÓN DE PAGOS (BACKOFFICE) ---

@admin.action(description='Aprobar inscripciones seleccionadas')
def approve_enrollment(modeladmin, request, queryset):
    queryset.update(status='approved')

@admin.action(description='Rechazar inscripciones seleccionadas')
def reject_enrollment(modeladmin, request, queryset):
    queryset.update(status='rejected')

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_info', 'course', 'status_badge', 'voucher_link', 'enrolled_at')
    list_filter = ('status', 'course', 'enrolled_at')
    search_fields = ('user__username', 'user__email', 'user__profile__dni')
    actions = [approve_enrollment, reject_enrollment]
    
    def user_info(self, obj):
        return f"{obj.user.username} ({obj.user.email})"
    user_info.short_description = "Usuario"

    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'review': 'blue',
            'approved': 'green',
            'rejected': 'red'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 10px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = "Estado"

    def voucher_link(self, obj):
        if obj.voucher_image:
            return format_html('<a href="{}" target="_blank">Ver Voucher</a>', obj.voucher_image.url)
        return "-"
    voucher_link.short_description = "Voucher"

# --- CMS DEL HOME ---

class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'style', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('style', 'is_active')
    ordering = ('order',)

class CertificationCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'style', 'rating', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('style', 'provider')
    ordering = ('order',)

# --- REGISTRO DE MODELOS ---

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'dni', 'academic_profile', 'role', 'phone_number', 'gender')
    list_filter = ('role', 'academic_profile', 'gender')
    search_fields = ('user__username', 'user__email', 'dni', 'phone_number')

@admin.register(AnnouncementCard)
class AnnouncementCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'style', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('style', 'is_active')
    search_fields = ('title', 'description')

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'website')
    search_fields = ('name',)

@admin.register(TopBanner)
class TopBannerAdmin(admin.ModelAdmin):
    list_display = ('message', 'style', 'is_active', 'created_at')
    list_editable = ('is_active', 'style')
    list_filter = ('is_active', 'style')

admin.site.register(Category, CategoryAdmin) # <--- ¡AQUÍ ESTÁ LA NUEVA LÍNEA!
admin.site.register(Course, CourseAdmin)
admin.site.register(Module)
admin.site.register(Lesson)
admin.site.register(Quiz)
admin.site.register(QuizSubmission)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Installment)
admin.site.register(HeroSlide, HeroSlideAdmin)
admin.site.register(CertificationCard, CertificationCardAdmin)