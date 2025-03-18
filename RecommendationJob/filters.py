import django_filters
from .models import Job

class JobsFilter(django_filters.FilterSet):
    keyword = django_filters.CharFilter(method='filter_by_keyword')

    class Meta:
        model = Job
        fields = ['title', 'description', 'required_skills', 'location']

    def filter_by_keyword(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(required_skills__icontains=value) |
            Q(location__icontains=value)
            )
            