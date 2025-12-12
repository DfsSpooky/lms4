import re
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from .validators import validate_file_extension

# --- USUARIO EXTENDIDO ---
class Profile(models.Model):
    ACADEMIC_CHOICES = [
        ('student', 'Estudiante'),
        ('graduate', 'Egresado'),
        ('professional', 'Profesional'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=20, choices=[('student', 'Estudiante'), ('teacher', 'Profesor'), ('organizer', 'Organizador')], default='student')
    
    dni = models.CharField(max_length=8, blank=True, help_text="DNI de 8 dígitos")
    address = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    academic_profile = models.CharField(max_length=20, choices=ACADEMIC_CHOICES, default='student', verbose_name="Perfil Académico")
    gender = models.CharField(max_length=10, choices=[('male', 'Masculino'), ('female', 'Femenino')], blank=True, verbose_name="Género")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Número de Celular")
    facebook_url = models.URLField(max_length=200, blank=True, verbose_name="Facebook")
    website = models.URLField(max_length=200, blank=True, verbose_name="Sitio Web")

    def __str__(self): return self.user.username

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"{self.user.username} - {self.session_key}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created: Profile.objects.create(user=instance)

# --- CATEGORÍAS & INSTITUCIONES ---
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome class or similar") 

    class Meta: verbose_name_plural = "Categories"
    def __str__(self): return self.name

    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Institution(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre de la Institución")
    logo = models.ImageField(upload_to='institutions/', verbose_name="Logo")
    website = models.URLField(blank=True, null=True, verbose_name="Sitio Web")
    def __str__(self): return self.name

class PaymentMethod(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre del Banco/Método")
    account_info = models.CharField(max_length=200, verbose_name="Información de Cuenta/Celular")
    qr_image = models.ImageField(upload_to='payment_qrs/', blank=True, null=True, verbose_name="Código QR")
    instructions = models.TextField(verbose_name="Instrucciones Adicionales")
    color = models.CharField(max_length=20, default='blue', help_text="Color para el botón (ej: purple, green, blue)", verbose_name="Color de Identidad")
    def __str__(self): return self.name

# --- CURSOS ---
class Course(models.Model):
    LEVEL_CHOICES = [('beginner', 'Principiante'), ('intermediate', 'Intermedio'), ('advanced', 'Avanzado')]
    TYPE_CHOICES = [('course', 'Curso Grabado'), ('seminar', 'Seminario en Vivo')]
    STATUS_CHOICES = [('draft', 'Borrador'), ('published', 'Publicado'), ('archived', 'Archivado')]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey('Category', related_name='courses', on_delete=models.SET_NULL, null=True, blank=True)
    course_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='course', verbose_name="Tipo de Producto")
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    learning_objectives = models.TextField(blank=True, verbose_name="Lo que aprenderás (un punto por línea)")
    requirements = models.TextField(blank=True, verbose_name="Requisitos (un punto por línea)")
    thumbnail = models.ImageField(upload_to='courses/', blank=True, null=True)
    preview_video_url = models.URLField(blank=True, null=True, verbose_name="Video de Vista Previa (YouTube)")
    
    start_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Inicio (Seminarios)")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Fin (Opcional)")
    live_url = models.URLField(blank=True, null=True, verbose_name="Enlace de Zoom/YouTube Live")
    launch_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Lanzamiento (Cuenta Regresiva)")

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Precio Actual (Oferta)")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Precio Normal (Sin descuento)")
    
    allow_monthly_payment = models.BooleanField(default=False, verbose_name="¿Permitir Pago Mensual?")
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0, verbose_name="Precio Mensual")
    duration_months = models.PositiveIntegerField(default=1, verbose_name="Duración en Meses")
    allowed_payment_methods = models.ManyToManyField('PaymentMethod', blank=True, related_name='courses', verbose_name="Métodos de Pago Aceptados")
    
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    institution = models.ForeignKey('Institution', on_delete=models.SET_NULL, null=True, blank=True, related_name='courses', verbose_name="Institución que Respalda")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Estado")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            count = 1
            while Course.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
        super().save(*args, **kwargs)

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            try:
                return int(100 - ((self.price / self.old_price) * 100))
            except ZeroDivisionError: return 0
        return 0
    
    @property
    def preview_youtube_id(self):
        if not self.preview_video_url: return None
        regex = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        match = re.search(regex, self.preview_video_url)
        return match.group(1) if match else None

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        return sum(r.rating for r in reviews) / len(reviews) if reviews else 0

    @property
    def total_duration(self):
        total_minutes = sum(lesson.duration for module in self.modules.all() for lesson in module.lessons.all())
        hours, minutes = divmod(total_minutes, 60)
        return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

    @property
    def is_upcoming(self):
        from django.utils import timezone
        return self.launch_date and self.launch_date > timezone.now()

class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    class Meta: ordering = ['order']
    def __str__(self): return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    LESSON_TYPES = [
        ('video', 'Video (YouTube/Vimeo)'),
        ('article', 'Artículo / Lectura'),
        ('pdf', 'Documento PDF'),
        ('resource', 'Recurso Descargable (ZIP/Excel/Etc)'),
        ('assignment', 'Tarea / Asignación'),
    ]
    module = models.ForeignKey(Module, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, default='video', verbose_name="Tipo de Lección")
    video_url = models.URLField(blank=True, null=True, verbose_name="URL del Video")
    content = models.TextField(blank=True, verbose_name="Contenido / Descripción")
    file = models.FileField(upload_to='lessons/files/', blank=True, null=True, verbose_name="Archivo Adjunto", validators=[validate_file_extension])
    due_date = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de Entrega")
    duration = models.PositiveIntegerField(default=0, help_text="Duration in minutes")
    order = models.PositiveIntegerField(default=0)
    class Meta: ordering = ['order']
    def __str__(self): return self.title
    @property
    def youtube_id(self):
        if not self.video_url: return None
        regex = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        match = re.search(regex, self.video_url)
        return match.group(1) if match else None
    @property
    def icon_class(self):
        icons = {'video': 'fas fa-play-circle', 'article': 'fas fa-book-open', 'pdf': 'fas fa-file-pdf', 'resource': 'fas fa-download', 'assignment': 'fas fa-tasks'}
        return icons.get(self.lesson_type, 'fas fa-file')

class LessonComment(models.Model):
    lesson = models.ForeignKey(Lesson, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='lesson_comments', on_delete=models.CASCADE)
    content = models.TextField(verbose_name="Comentario")
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created_at']
    def __str__(self): return f"Comment by {self.user.username} on {self.lesson.title}"

class Review(models.Model):
    course = models.ForeignKey(Course, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = ('course', 'user')
    def __str__(self): return f"{self.user.username} - {self.course.title}"

# --- EXÁMENES ---
class Quiz(models.Model):
    module = models.ForeignKey(Module, related_name='quizzes', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, verbose_name="Descripción")
    pass_mark = models.IntegerField(default=70)
    duration = models.PositiveIntegerField(default=0, help_text="Duración en minutos (0 para sin límite)")
    randomize_questions = models.BooleanField(default=False, verbose_name="¿Aleatorizar preguntas?")
    questions_to_show = models.PositiveIntegerField(default=10, help_text="Número de preguntas a mostrar (si es aleatorio)")
    is_final_exam = models.BooleanField(default=False, verbose_name="¿Es examen final?")
    def __str__(self): return self.title

class Question(models.Model):
    QUESTION_TYPES = [('single_choice', 'Opción Múltiple (Una respuesta)'), ('multiple_choice', 'Opción Múltiple (Varias respuestas)'), ('true_false', 'Verdadero / Falso'), ('short_answer', 'Respuesta Corta'), ('matching', 'Relacionar Columnas'), ('ordering', 'Ordenamiento / Secuencia')]
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='single_choice')
    points = models.FloatField(default=1.0)
    explanation = models.TextField(blank=True, help_text="Explicación que se muestra después de responder")
    order = models.PositiveIntegerField(default=0)
    class Meta: ordering = ['order']
    def __str__(self): return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    match_text = models.CharField(max_length=200, blank=True, help_text="Texto correspondiente para relacionar (Columna B)")
    order = models.PositiveIntegerField(default=0, help_text="Orden correcto para preguntas de secuencia")
    class Meta: ordering = ['order']
    def __str__(self): return self.text

class QuizSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    passed = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_by = models.ForeignKey(User, null=True, blank=True, related_name='graded_quizzes', on_delete=models.SET_NULL)
    teacher_feedback = models.TextField(blank=True)
    def __str__(self): return f"{self.user.username} - {self.quiz.title}: {self.score}"

class StudentAnswer(models.Model):
    submission = models.ForeignKey(QuizSubmission, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answers = models.ManyToManyField(Answer, blank=True)
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    points_awarded = models.FloatField(default=0.0)
    def __str__(self): return f"Answer to {self.question.id} by {self.submission.user.username}"

# --- PROGRESO E INSCRIPCIONES ---
class Enrollment(models.Model):
    PAYMENT_STATUS_CHOICES = [('pending', 'Pendiente de Pago'), ('review', 'En Revisión'), ('approved', 'Aprobado'), ('rejected', 'Rechazado')]
    user = models.ForeignKey(User, related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    selected_payment_plan = models.CharField(max_length=20, choices=[('full', 'Pago Completo'), ('monthly', 'Mensualidad')], default='full')
    installments_paid = models.PositiveIntegerField(default=0, verbose_name="Cuotas Pagadas")
    voucher_image = models.ImageField(upload_to='vouchers/', blank=True, null=True, verbose_name="Constancia de Pago")
    is_completed = models.BooleanField(default=False)
    class Meta: unique_together = ('user', 'course')
    def __str__(self): return f"{self.user.username} -> {self.course.title}"

    def generate_installments(self):
        if self.selected_payment_plan != 'monthly' or not self.course.duration_months or not self.course.monthly_price: return
        from dateutil.relativedelta import relativedelta
        from django.utils import timezone
        for i in range(1, self.course.duration_months + 1):
            due_date = self.enrolled_at.date() + relativedelta(months=i-1)
            initial_status = 'approved' if i == 1 and self.status == 'approved' else 'pending'
            paid_date = self.enrolled_at if i == 1 and self.status == 'approved' else None
            Installment.objects.get_or_create(enrollment=self, installment_number=i, defaults={'amount': self.course.monthly_price, 'due_date': due_date, 'status': initial_status, 'paid_at': paid_date})

    @property
    def is_up_to_date(self):
        if self.selected_payment_plan == 'full': return True
        from django.utils import timezone
        return not self.installments.filter(due_date__lt=timezone.now().date(), status__in=['pending', 'rejected', 'review']).exists()

class Installment(models.Model):
    STATUS_CHOICES = [('pending', 'Pendiente'), ('review', 'En Revisión'), ('approved', 'Aprobado'), ('rejected', 'Rechazado')]
    enrollment = models.ForeignKey(Enrollment, related_name='installments', on_delete=models.CASCADE)
    installment_number = models.PositiveIntegerField(verbose_name="Número de Cuota")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto")
    due_date = models.DateField(verbose_name="Fecha de Vencimiento")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    voucher_image = models.ImageField(upload_to='vouchers/installments/', blank=True, null=True, verbose_name="Comprobante")
    feedback = models.TextField(blank=True, verbose_name="Observaciones")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Pago")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ['installment_number']; unique_together = ('enrollment', 'installment_number'); verbose_name = "Cuota"; verbose_name_plural = "Cuotas"
    def __str__(self): return f"Cuota {self.installment_number} - {self.enrollment.user.username}"

class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    assignment_text = models.TextField(blank=True, verbose_name="Texto de la Tarea")
    assignment_file = models.FileField(upload_to='assignments/', blank=True, null=True, verbose_name="Archivo de la Tarea", validators=[validate_file_extension])
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Nota")
    instructor_feedback = models.TextField(blank=True, verbose_name="Feedback del Instructor")
    class Meta: unique_together = ('user', 'lesson')

# --- CMS ---
class HeroSlide(models.Model):
    STYLE_CHOICES = [('promo', 'Estilo Promo'), ('business', 'Estilo Negocios'), ('new', 'Estilo Lanzamiento')]
    title = models.CharField(max_length=200, help_text="Soporta HTML")
    description = models.TextField(blank=True)
    style = models.CharField(max_length=20, choices=STYLE_CHOICES, default='promo')
    tag_text = models.CharField(max_length=50, blank=True)
    btn1_text = models.CharField(max_length=50, default="Ver más")
    btn1_url = models.CharField(max_length=200, default="#")
    btn2_text = models.CharField(max_length=50, blank=True)
    btn2_url = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='hero/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ['order']; verbose_name = "Slide del Home"
    def __str__(self): return self.title

class CertificationCard(models.Model):
    STYLE_CHOICES = [('blue', 'Azul'), ('indigo', 'Indigo'), ('green', 'Verde')]
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100, default="Certificado Profesional")
    provider = models.CharField(max_length=50)
    icon_class = models.CharField(max_length=50, default="fab fa-microsoft")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.8)
    reviews_count = models.IntegerField(default=100)
    style = models.CharField(max_length=20, choices=STYLE_CHOICES, default='blue')
    url = models.CharField(max_length=200, default="#")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ['order']; verbose_name = "Tarjeta de Certificación"
    def __str__(self): return self.title

class AnnouncementCard(models.Model):
    STYLE_CHOICES = [('primary', 'Azul Brillante'), ('dark', 'Azul Oscuro'), ('gradient', 'Gradiente')]
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descripción")
    btn_text = models.CharField(max_length=50, default="Ver más", verbose_name="Texto del Botón")
    btn_url = models.CharField(max_length=200, default="#", verbose_name="Enlace del Botón")
    image = models.ImageField(upload_to='announcements/', blank=True, null=True, verbose_name="Imagen Decorativa")
    style = models.CharField(max_length=20, choices=STYLE_CHOICES, default='primary', verbose_name="Estilo de Fondo")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    class Meta: ordering = ['order']; verbose_name = "Tarjeta de Anuncio"
    def __str__(self): return self.title

class ForumTopic(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título del Tema")
    content = models.TextField(verbose_name="Contenido")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_topics')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='forum_topics')
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    class Meta: ordering = ['-created_at']
    def __str__(self): return self.title

class ForumReply(models.Model):
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_replies')
    content = models.TextField(verbose_name="Respuesta")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['created_at']
    def __str__(self): return f"Reply by {self.user.username}"

class Notification(models.Model):
    TYPE_CHOICES = [('reply', 'Respuesta'), ('grade', 'Nota'), ('system', 'Sistema')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=200, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created_at']
    def __str__(self): return f"Notif: {self.message}"

class TopBanner(models.Model):
    STYLE_CHOICES = [('cyber', 'Cyber'), ('black_friday', 'Black Friday'), ('info', 'Info'), ('warning', 'Alerta')]
    message = models.CharField(max_length=200)
    sub_message = models.CharField(max_length=200, blank=True)
    btn_text = models.CharField(max_length=50, blank=True)
    btn_url = models.CharField(max_length=200, blank=True)
    style = models.CharField(max_length=20, choices=STYLE_CHOICES, default='cyber')
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: verbose_name = "Barra de Anuncio Top"
    def __str__(self): return self.message

class SiteConfiguration(models.Model):
    site_name = models.CharField(max_length=100, default="LMS Academy")
    logo = models.ImageField(upload_to='site_config/', blank=True, null=True)
    logo_width = models.PositiveIntegerField(default=40)
    logo_height = models.PositiveIntegerField(default=40)
    class Meta: verbose_name = "Configuración del Sitio"
    def __str__(self): return self.site_name
    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

class ServiceRequest(models.Model):
    company_name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_handled = models.BooleanField(default=False)
    def __str__(self): return self.company_name

# --- MODELOS DE EVENTOS ACTUALIZADOS (MULTI-DÍA Y AGENDA) ---
class Event(models.Model):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events', null=True, blank=True)
    title = models.CharField(max_length=200, verbose_name="Título del Evento")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name="Descripción")
    
    start_date = models.DateTimeField(verbose_name="Inicio del Evento")
    end_date = models.DateTimeField(verbose_name="Fin del Evento")
    
    location = models.CharField(max_length=200, verbose_name="Ubicación Principal")
    capacity = models.PositiveIntegerField(default=100, verbose_name="Capacidad Máxima (Aforo)")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Precio de Entrada")
    image = models.ImageField(upload_to='events/', blank=True, null=True, verbose_name="Imagen del Evento")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original = self.slug
            c = 1
            while Event.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original}-{c}"
                c += 1
        super().save(*args, **kwargs)

    @property
    def spots_left(self):
        sold = self.tickets.count()
        return max(0, self.capacity - sold)

    @property
    def duration_days(self):
        if self.end_date and self.start_date:
            delta = self.end_date - self.start_date
            return delta.days + 1
        return 1

class EventSession(models.Model):
    SESSION_TYPES = [('workshop', 'Taller Práctico'), ('lecture', 'Conferencia'), ('break', 'Receso/Almuerzo'), ('networking', 'Networking')]
    event = models.ForeignKey(Event, related_name='sessions', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, verbose_name="Título de la Sesión")
    description = models.TextField(blank=True, verbose_name="Descripción")
    start_time = models.DateTimeField(verbose_name="Hora Inicio")
    end_time = models.DateTimeField(verbose_name="Hora Fin")
    room = models.CharField(max_length=100, blank=True, verbose_name="Sala / Ambiente")
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='lecture')
    speaker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions_speaking')

    class Meta: ordering = ['start_time']; verbose_name = "Sesión de Agenda"; verbose_name_plural = "Agenda del Evento"
    def __str__(self): return f"{self.title} ({self.start_time.strftime('%H:%M')})"

class TicketTier(models.Model):
    event = models.ForeignKey(Event, related_name='tiers', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="Nombre del Tipo (ej: VIP)")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    capacity = models.PositiveIntegerField(default=100, verbose_name="Cantidad Disponible")

    def __str__(self): return f"{self.name} - {self.event.title}"

    @property
    def sold_count(self):
        return self.tickets.count()

    @property
    def remaining(self):
        return max(0, self.capacity - self.sold_count)

class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    tier = models.ForeignKey(TicketTier, on_delete=models.PROTECT, null=True, blank=True, related_name='tickets')
    purchase_date = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False, verbose_name="Usado / Asistió")

    # Campos para pago (similar a Enrollment)
    STATUS_CHOICES = [('pending', 'Pendiente de Pago'), ('review', 'En Revisión'), ('approved', 'Aprobado'), ('rejected', 'Rechazado')]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved') # Default approved for backward compatibility/free events
    voucher_image = models.ImageField(upload_to='vouchers/tickets/', blank=True, null=True, verbose_name="Constancia de Pago")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Monto Pagado")

    # Attendee Details (Assignment)
    attendee_first_name = models.CharField(max_length=150, blank=True, verbose_name="Nombre Asistente")
    attendee_last_name = models.CharField(max_length=150, blank=True, verbose_name="Apellido Asistente")
    attendee_email = models.EmailField(blank=True, verbose_name="Email Asistente")

    def __str__(self): return f"Ticket {self.id} - {self.user.username}"