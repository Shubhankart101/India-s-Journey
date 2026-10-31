from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    order = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    badges = models.JSONField(default=list, blank=True)
    art = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Subgroup(models.Model):
    category = models.ForeignKey(Category, related_name='subgroups', on_delete=models.CASCADE)
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180)
    order = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=220, blank=True)
    description = models.TextField(blank=True)
    art = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ['category__order', 'order', 'name']
        constraints = [models.UniqueConstraint(fields=['category', 'slug'], name='unique_subgroup_slug_per_category')]

    def __str__(self):
        return f'{self.category.name} / {self.name}'


class Indicator(models.Model):
    key = models.SlugField(max_length=160, unique=True)
    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=500, blank=True)
    frequency = models.CharField(max_length=80, blank=True)
    color = models.CharField(max_length=20, default='#58a6ff')
    suffix = models.CharField(max_length=80, blank=True)
    source_url = models.URLField(max_length=600, blank=True)
    details = models.TextField(blank=True)
    category = models.ForeignKey(Category, related_name='indicators', on_delete=models.PROTECT)
    subgroup = models.ForeignKey(Subgroup, related_name='indicators', on_delete=models.PROTECT)
    position = models.PositiveIntegerField(default=0, db_index=True)
    labels = models.JSONField(default=list, blank=True)
    datasets = models.JSONField(default=list, blank=True)
    preview = models.JSONField(default=dict, blank=True)
    chart_type = models.CharField(max_length=20, default='line')
    index_axis = models.CharField(max_length=1, default='x')
    scope = models.CharField(max_length=40, blank=True)
    scope_label = models.CharField(max_length=120, blank=True)
    note = models.TextField(blank=True)
    source = models.TextField(blank=True)
    unit = models.CharField(max_length=80, blank=True)
    error = models.TextField(blank=True)
    is_live = models.BooleanField(default=False, db_index=True)
    point_count = models.PositiveIntegerField(default=0)
    first_label = models.CharField(max_length=80, blank=True)
    latest_label = models.CharField(max_length=80, blank=True)
    latest_value = models.FloatField(null=True, blank=True)
    search_text = models.TextField(blank=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.title

    @property
    def is_radial(self):
        return self.chart_type in {'pie', 'doughnut'}


class Article(models.Model):
    KIND_CHOICES = [
        ('indian_matrix', 'Indian Matrix'),
        ('polity_policy', 'Polity and Policy'),
        ('pew', 'Pew Research Center'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=500)
    url = models.URLField(max_length=700, unique=True)
    published = models.CharField(max_length=80, blank=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    publisher = models.CharField(max_length=120, blank=True)
    kind = models.CharField(max_length=30, choices=KIND_CHOICES, default='other', db_index=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-published_at', 'title']

    def __str__(self):
        return self.title


class SavedChart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='saved_charts', on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, related_name='saved_by', on_delete=models.CASCADE)
    note = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [models.UniqueConstraint(fields=['user', 'indicator'], name='unique_saved_chart_per_user')]

    def __str__(self):
        return f'{self.user} saved {self.indicator.key}'


class DataRefresh(models.Model):
    STATUS_CHOICES = [('running', 'Running'), ('success', 'Success'), ('failed', 'Failed')]

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    source_generated_at = models.CharField(max_length=60, blank=True)
    indicators_count = models.PositiveIntegerField(default=0)
    live_count = models.PositiveIntegerField(default=0)
    articles_count = models.PositiveIntegerField(default=0)
    message = models.TextField(blank=True)

    class Meta:
        ordering = ['-started_at']
        verbose_name_plural = 'data refreshes'

    def __str__(self):
        return f'{self.started_at:%Y-%m-%d %H:%M} {self.status}'
