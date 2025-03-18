import django_filters
from .models import Job

class JobsFilter(django_filters.FilterSet):
    keyword = django_filters.CharFilter(method='filter_by_keyword')

    class Meta:
        model = Job
        fields = ['title', 'description', 'required_skills', 'location']

    def filter_by_keyword(self, queryset, name, value):
        return queryset.filter(
            title__icontains=value
        ) | queryset.filter(
            description__icontains=value
        ) | queryset.filter(
            required_skills__icontains=value
        ) | queryset.filter(
            location__icontains=value
        )
