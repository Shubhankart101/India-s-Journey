from django.contrib import admin

from .models import Article, Category, DataRefresh, Indicator, SavedChart, Subgroup


class SubgroupInline(admin.TabularInline):
    model = Subgroup
    extra = 0
    fields = ['name', 'slug', 'order', 'art']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'art']
    list_editable = ['order']
    search_fields = ['name', 'title']
    prepopulated_fields = {'slug': ['name']}
    inlines = [SubgroupInline]


@admin.register(Subgroup)
class SubgroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'order', 'art']
    list_filter = ['category']
    search_fields = ['name', 'title']


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ['key', 'title', 'category', 'subgroup', 'chart_type', 'is_live', 'point_count', 'latest_label', 'updated_at']
    list_filter = ['is_live', 'chart_type', 'category']
    search_fields = ['key', 'title', 'subtitle', 'source_url']
    readonly_fields = ['labels', 'datasets', 'preview', 'point_count', 'latest_label', 'latest_value', 'updated_at']
    list_select_related = ['category', 'subgroup']
    fieldsets = [
        (None, {'fields': ['key', 'title', 'subtitle', 'category', 'subgroup', 'position']}),
        ('Presentation', {'fields': ['frequency', 'color', 'suffix', 'chart_type', 'index_axis', 'scope', 'scope_label']}),
        ('Source', {'fields': ['source_url', 'source', 'details', 'note', 'error', 'is_live']}),
        ('Data (refreshed by the pipelines)', {'classes': ['collapse'], 'fields': [
            'labels', 'datasets', 'preview', 'point_count', 'latest_label', 'latest_value', 'updated_at']}),
    ]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'publisher', 'kind', 'published_at', 'is_featured']
    list_filter = ['kind', 'is_featured', 'publisher']
    list_editable = ['is_featured']
    search_fields = ['title', 'url']
    date_hierarchy = 'published_at'


@admin.register(SavedChart)
class SavedChartAdmin(admin.ModelAdmin):
    list_display = ['user', 'indicator', 'note', 'created_at']
    search_fields = ['user__username', 'indicator__key', 'indicator__title']
    autocomplete_fields = ['indicator']
    list_select_related = ['user', 'indicator']


@admin.register(DataRefresh)
class DataRefreshAdmin(admin.ModelAdmin):
    list_display = ['started_at', 'status', 'indicators_count', 'live_count', 'articles_count', 'source_generated_at']
    list_filter = ['status']
    readonly_fields = [field.name for field in DataRefresh._meta.fields]

    def has_add_permission(self, request):
        return False
