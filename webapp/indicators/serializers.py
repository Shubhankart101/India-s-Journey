from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
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

    def get_is_saved(self, obj):
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
    saved_count = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'date_joined', 'is_staff', 'saved_count']

    def get_saved_count(self, obj):
        return obj.saved_charts.count()


class RegisterSerializer(serializers.Serializer):
    username = serializers.RegexField(r'^[\w.@+-]{3,150}$', error_messages={
        'invalid': 'Use 3-150 letters, digits or @/./+/-/_ characters.'})
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_username(self, value):
        if get_user_model().objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('That username is already taken.')
        return value

    def validate(self, attrs):
        user = get_user_model()(username=attrs['username'], email=attrs.get('email', ''))
        validate_password(attrs['password'], user)
        return attrs

    def create(self, validated_data):
        return get_user_model().objects.create_user(
            username=validated_data['username'], email=validated_data.get('email', ''), password=validated_data['password'])


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
