from django.views import generic
from django.db.models import Q
from ..models import Course, Event, ForumTopic

class GlobalSearchView(generic.TemplateView):
    template_name = 'academy/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q')
        category_slug = self.request.GET.get('category')
        level = self.request.GET.get('level')
        price_filter = self.request.GET.get('price') # free, paid
        
        # Facets Context
        from ..models import Category
        context['categories'] = Category.objects.all()
        context['levels'] = [('beginner', 'Principiante'), ('intermediate', 'Intermedio'), ('advanced', 'Avanzado')]
        
        if query:
            context['query'] = query
            
            # 1. Filter Courses
            courses = Course.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query),
                status='published'
            )
            
            # Apply Facets
            if category_slug:
                courses = courses.filter(category__slug=category_slug)
            if level:
                courses = courses.filter(level=level)
            if price_filter == 'free':
                courses = courses.filter(price=0)
            elif price_filter == 'paid':
                courses = courses.filter(price__gt=0)

            context['courses'] = courses
            
            # 2. Events & Forum (Basic Search)
            # Only search these if no specific course filters are active to avoid confusion, 
            # or keep them but maybe move to bottom. For now, keep them.
            if not category_slug and not level and not price_filter:
                context['events'] = Event.objects.filter(
                    Q(title__icontains=query) | Q(description__icontains=query),
                    is_active=True
                )[:5]
                context['forum_topics'] = ForumTopic.objects.filter(
                    Q(title__icontains=query) | Q(content__icontains=query)
                )[:5]
            else:
                context['events'] = []
                context['forum_topics'] = []
            
            context['total_results'] = len(context['courses']) + len(context['events']) + len(context['forum_topics'])
        
        return context
