from django.urls import path, include
from . import views
from . import views_organizer

app_name = 'academy'

urlpatterns = [
    # --- RUTAS DE ORGANIZADOR ---
    path('organizer/dashboard/', views_organizer.OrganizerDashboardView.as_view(), name='organizer_dashboard'),
    path('organizer/event/add/', views_organizer.OrganizerEventCreateView.as_view(), name='organizer_event_add'),
    path('organizer/event/<int:pk>/edit/', views_organizer.OrganizerEventUpdateView.as_view(), name='organizer_event_edit'),
    path('organizer/event/<int:pk>/detail/', views_organizer.OrganizerEventDetailView.as_view(), name='organizer_event_detail'),

    path('', views.CourseListView.as_view(), name='course_list'),
    path('search/', views.GlobalSearchView.as_view(), name='global_search'),
    path('dashboard/', views.StudentDashboardView.as_view(), name='dashboard'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('profile/', views.user_settings, name='profile_edit'),
    path('settings/', views.user_settings, name='user_settings'),
    
    path('courses/', views.CourseCatalogView.as_view(), name='course_catalog'),
    path('course/<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),

    path('course/<slug:slug>/play/', views.course_play, name='course_play'),
    
    # Flujo de Inscripción y Pago
    path('course/<slug:slug>/enroll/step1/', views.enroll_course_step1, name='enroll_step1'),
    path('enrollment/<int:pk>/payment/', views.payment_gateway, name='payment_gateway'),

    # NUEVAS RUTAS PARA TOP BANNER
    path('admin-dashboard/banner/add/', views.TopBannerCreateView.as_view(), name='top_banner_add'),
    path('admin-dashboard/banner/<int:pk>/edit/', views.TopBannerUpdateView.as_view(), name='top_banner_edit'),

    # Nuevas rutas para pagos recurrentes
    path('my-payments/', views.StudentPaymentsView.as_view(), name='student_payments'),
    path('installment/<int:installment_id>/upload/', views.upload_installment_voucher, name='upload_installment_voucher'),

    path('lesson/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('lesson/<int:pk>/complete/', views.mark_lesson_complete, name='complete_lesson'),
    path('lesson/<int:lesson_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('quiz/<int:pk>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('quiz/<int:pk>/take/', views.take_quiz, name='take_quiz'),

    # Coments
    path('lesson/<int:lesson_id>/comment/', views.add_comment, name='add_comment'),
    
    # Teacher
    path('teacher/dashboard/', views.TeacherDashboardView.as_view(), name='teacher_dashboard'),
    path('teacher/course/add/', views.CourseCreateView.as_view(), name='course_add'),
    path('teacher/course/<slug:slug>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('teacher/course/<slug:slug>/students/', views.TeacherCourseStudentsView.as_view(), name='course_students'),
    path('teacher/course/<slug:slug>/content/', views.course_content_manage, name='course_content'),
    path('teacher/course/<slug:slug>/module/add/', views.add_module, name='add_module'),
    path('teacher/lesson/add/', views.add_lesson, name='add_lesson'),
    path('teacher/module/<int:pk>/delete/', views.delete_module, name='delete_module'),
    path('teacher/lesson/<int:pk>/delete/', views.delete_lesson, name='delete_lesson'),
    path('teacher/lesson/<int:pk>/edit/', views.edit_lesson, name='edit_lesson'),
    path('teacher/lesson/<int:lesson_id>/submissions/', views.lesson_submissions, name='lesson_submissions'),
    path('teacher/course/generate-ai/', views.AICourseGeneratorView.as_view(), name='ai_course_generator'),
    path('teacher/submission/<int:progress_id>/grade/', views.grade_submission, name='grade_submission'),
    path('teacher/content/reorder/', views.reorder_content, name='reorder_content'),
    path('teacher/course/<slug:slug>/preview/', views.course_preview, name='course_preview'),
    path('teacher/inbox/', views.TeacherInboxView.as_view(), name='teacher_inbox'),
    path('teacher/inbox/reply/<int:comment_id>/', views.teacher_reply_comment, name='teacher_reply_comment'),

    # Quiz Management
    path('teacher/quiz/add/', views.add_quiz, name='add_quiz'),
    path('teacher/quiz/<int:pk>/edit/', views.edit_quiz, name='edit_quiz'),
    path('teacher/quiz/<int:pk>/delete/', views.delete_quiz, name='delete_quiz'),
    path('teacher/quiz/<int:quiz_id>/question/add/', views.add_question, name='add_question'),
    path('teacher/question/<int:pk>/delete/', views.delete_question, name='delete_question'),

    # Quiz Submission & Grading
    path('teacher/quiz/<int:quiz_id>/submissions/', views.quiz_submissions, name='quiz_submissions'),
    path('teacher/quiz/submission/<int:submission_id>/grade/', views.quiz_grade_submission, name='quiz_grade_submission'),

    # Admin
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-dashboard/user/add/', views.AdminUserCreateView.as_view(), name='admin_user_add'),
    path('admin-dashboard/user/<int:pk>/edit/', views.AdminUserUpdateView.as_view(), name='admin_user_edit'),
    path('admin-dashboard/user/<int:pk>/delete/', views.AdminUserDeleteView.as_view(), name='admin_user_delete'),
    path('admin-dashboard/slide/add/', views.HeroSlideCreateView.as_view(), name='hero_slide_add'),
    path('admin-dashboard/slide/<int:pk>/edit/', views.HeroSlideUpdateView.as_view(), name='hero_slide_edit'),

    path('admin-dashboard/category/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('admin-dashboard/category/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),

    path('admin-dashboard/certification/add/', views.CertificationCardCreateView.as_view(), name='certification_add'),
    path('admin-dashboard/certification/<int:pk>/edit/', views.CertificationCardUpdateView.as_view(), name='certification_edit'),

    # NEW: Announcement, Institution, PaymentMethod Management
    path('admin-dashboard/announcement/add/', views.AnnouncementCardCreateView.as_view(), name='announcement_add'),
    path('admin-dashboard/announcement/<int:pk>/edit/', views.AnnouncementCardUpdateView.as_view(), name='announcement_edit'),

    path('admin-dashboard/institution/add/', views.InstitutionCreateView.as_view(), name='institution_add'),
    path('admin-dashboard/institution/<int:pk>/edit/', views.InstitutionUpdateView.as_view(), name='institution_edit'),

    path('admin-dashboard/payment-method/add/', views.PaymentMethodCreateView.as_view(), name='payment_method_add'),
    path('admin-dashboard/payment-method/<int:pk>/edit/', views.PaymentMethodUpdateView.as_view(), name='payment_method_edit'),

    # RUTAS AÑADIDAS PARA GESTIÓN DE EVENTOS
    path('admin-dashboard/event/add/', views.EventCreateView.as_view(), name='admin_event_add'),
    path('admin-dashboard/event/<int:pk>/edit/', views.EventUpdateView.as_view(), name='admin_event_edit'),

    # Certificate
    path('course/<slug:slug>/certificate/', views.CertificateView.as_view(), name='certificate'),

    # Public Profile
    path('u/<str:username>/', views.PublicProfileView.as_view(), name='public_profile'),

    # Forum
    path('forum/', views.ForumTopicListView.as_view(), name='forum_list'),
    path('forum/topic/add/', views.CreateTopicView.as_view(), name='create_topic'),
    path('forum/topic/<int:pk>/', views.ForumTopicDetailView.as_view(), name='forum_topic_detail'),

    # Notifications
    path('notifications/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),

    # Empresas y Eventos
    path('empresas/', views.EnterpriseLandingView.as_view(), name='enterprise_services'),
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/<slug:slug>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<int:pk>/register/', views.EventRegistrationView.as_view(), name='event_register'),
    path('ticket/<uuid:ticket_id>/', views.TicketDetailView.as_view(), name='ticket_detail'),
]