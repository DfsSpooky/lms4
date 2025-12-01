from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages
from ..models import ForumTopic, ForumReply, Enrollment

class ForumTopicListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = ForumTopic
    template_name = 'academy/forum_list.html'
    context_object_name = 'topics'
    paginate_by = 20

    def test_func(self):
        return Enrollment.objects.filter(user=self.request.user, status='approved').exists()

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.warning(self.request, "El foro es exclusivo para estudiantes inscritos en al menos un curso.")
            return redirect('academy:course_catalog')
        return super().handle_no_permission()

    def get_queryset(self):
        return ForumTopic.objects.all().select_related('user', 'user__profile').order_by('-created_at')

class ForumTopicDetailView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    model = ForumTopic
    template_name = 'academy/forum_detail.html'
    context_object_name = 'topic'

    def test_func(self):
        return Enrollment.objects.filter(user=self.request.user, status='approved').exists()

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
             messages.warning(self.request, "El foro es exclusivo para estudiantes inscritos.")
             return redirect('academy:course_catalog')
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['replies'] = self.object.replies.select_related('user', 'user__profile').order_by('created_at')
        self.object.views += 1
        self.object.save(update_fields=['views'])
        return ctx

    def post(self, request, *args, **kwargs):
        topic = self.get_object()
        content = request.POST.get('content')
        if content:
            reply = ForumReply.objects.create(topic=topic, user=request.user, content=content)
            messages.success(request, "Respuesta publicada.")
            return redirect('academy:forum_topic_detail', pk=topic.id)
        return redirect('academy:forum_topic_detail', pk=topic.id)

class CreateTopicView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = ForumTopic
    fields = ['title', 'content', 'course']
    template_name = 'academy/forum_topic_form.html'
    success_url = reverse_lazy('academy:forum_list')

    def test_func(self):
        return Enrollment.objects.filter(user=self.request.user, status='approved').exists()

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
             messages.warning(self.request, "Debes estar inscrito en un curso para crear temas.")
             return redirect('academy:course_catalog')
        return super().handle_no_permission()

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Tema creado exitosamente.")
        return super().form_valid(form)
