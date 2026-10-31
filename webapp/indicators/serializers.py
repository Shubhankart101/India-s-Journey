from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Article, Category, Indicator, SavedChart, Subgroup


class SubgroupSerializer(serializers.ModelSerializer):
    indicator_count = serializers.IntegerField(read_only=True)
    live_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Subgroup
        fields = ['name', 'slug', 'order', 'title', 'description', 'art', 'indicator_count', 'live_count']


class CategorySerializer(serializers.ModelSerializer):
    subgroups = serializers.SerializerMethodField()
    indicator_count = serializers.IntegerField(read_only=True)
    live_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['name', 'slug', 'order', 'title', 'description', 'badges', 'art', 'indicator_count', 'live_count', 'subgroups']

    @extend_schema_field(SubgroupSerializer(many=True))
    def get_subgroups(self, obj):
        return SubgroupSerializer(getattr(obj, 'annotated_subgroups', obj.subgroups.all()), many=True).data


class IndicatorSummarySerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name')
    category_slug = serializers.CharField(source='category.slug')
    subgroup = serializers.CharField(source='subgroup.name')
    subgroup_slug = serializers.CharField(source='subgroup.slug')

    class Meta:
        model = Indicator
        fields = [
            'key', 'title', 'subtitle', 'frequency', 'color', 'suffix', 'category', 'category_slug', 'subgroup',
            'subgroup_slug', 'chart_type', 'index_axis', 'scope', 'is_live', 'point_count', 'first_label',
            'latest_label', 'latest_value', 'preview', 'updated_at',
        ]


class IndicatorDetailSerializer(IndicatorSummarySerializer):
    is_saved = serializers.SerializerMethodField()
    category_art = serializers.CharField(source='category.art')
    subgroup_art = serializers.CharField(source='subgroup.art')

    class Meta(IndicatorSummarySerializer.Meta):
        fields = IndicatorSummarySerializer.Meta.fields[:-2] + [
            'source_url', 'details', 'labels', 'datasets', 'scope_label', 'note', 'source', 'unit', 'error',
            'category_art', 'subgroup_art', 'is_saved', 'updated_at',
        ]

    def get_is_saved(self, obj) -> bool:
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return SavedChart.objects.filter(user=request.user, indicator=obj).exists()


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['title', 'url', 'published', 'published_at', 'publisher', 'kind', 'is_featured']


class SavedChartSerializer(serializers.ModelSerializer):
    indicator = IndicatorSummarySerializer(read_only=True)
    key = serializers.SlugRelatedField(
        source='indicator', slug_field='key', queryset=Indicator.objects.all(), write_only=True)

    class Meta:
        model = SavedChart
        fields = ['key', 'indicator', 'note', 'created_at']
        read_only_fields = ['created_at']


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    providers = serializers.SerializerMethodField()
    saved_count = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'name', 'email', 'date_joined', 'is_staff', 'providers', 'saved_count']

    def get_name(self, obj) -> str:
        return obj.get_full_name() or obj.username

    def get_providers(self, obj) -> list[str]:
        return sorted({account.provider for account in obj.socialaccount_set.all()})

    def get_saved_count(self, obj) -> int:
        return obj.saved_charts.count()


class AuthStateSerializer(serializers.Serializer):
    authenticated = serializers.BooleanField()
    user = UserSerializer(allow_null=True)


class ProviderSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    login_url = serializers.CharField(help_text='POST here (form submit with csrfmiddlewaretoken and next) to start OAuth.')


class CompareSeriesSerializer(serializers.Serializer):
    key = serializers.CharField()
    title = serializers.CharField()
    suffix = serializers.CharField()
    color = serializers.CharField()
    category = serializers.CharField()
    subgroup = serializers.CharField()
    chart_type = serializers.CharField()
    values = serializers.ListField(child=serializers.FloatField(allow_null=True))


class CompareSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    series = CompareSeriesSerializer(many=True)
    missing = serializers.ListField(child=serializers.CharField())


class StatsSerializer(serializers.Serializer):
    indicators = serializers.IntegerField()
    live_indicators = serializers.IntegerField()
    radial_indicators = serializers.IntegerField()
    categories = serializers.IntegerField()
    subgroups = serializers.IntegerField()
    articles = serializers.IntegerField()
    data_points = serializers.IntegerField()
    source_generated_at = serializers.DateTimeField(allow_null=True)
    last_refresh = serializers.DateTimeField(allow_null=True)


class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()
    indicators = serializers.IntegerField()
    backup_url = serializers.URLField()


class DetailSerializer(serializers.Serializer):
    detail = serializers.CharField()