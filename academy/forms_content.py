from django import forms
from tinymce.widgets import TinyMCE
from .models import Module, Lesson, Quiz, Question

# Estilos comunes para inputs (DRY)
INPUT_CLASSES = 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 placeholder-slate-500 transition-all'

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'pass_mark']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Título del Examen'}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 3, 'placeholder': 'Descripción del examen'}),
            'pass_mark': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': '70'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'points', 'explanation', 'order']
        widgets = {
            'text': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Pregunta'}),
            'question_type': forms.Select(attrs={'class': INPUT_CLASSES, 'x-model': 'questionType'}),
            'points': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': '1.0'}),
            'explanation': forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 2, 'placeholder': 'Explicación (opcional)'}),
            'order': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': '0'}),
        }

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Ej: Introducción a la Programación'}),
            'order': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': '1'})
        }

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['lesson_type', 'title', 'video_url', 'file', 'content', 'duration', 'order', 'due_date']
        widgets = {
            'lesson_type': forms.Select(attrs={'class': INPUT_CLASSES, 'x-model': 'lessonType'}), # Vinculamos con AlpineJS
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Título de la lección'}),
            'video_url': forms.URLInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'https://youtube.com/...'}),
            'file': forms.FileInput(attrs={'class': 'block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-700'}),
            'content': TinyMCE(attrs={'cols': 80, 'rows': 20}),
            'duration': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Minutos'}),
            'order': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': '1'}),
            'due_date': forms.DateTimeInput(attrs={'class': INPUT_CLASSES, 'type': 'datetime-local'}),
        }