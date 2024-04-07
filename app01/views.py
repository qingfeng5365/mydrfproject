from django.contrib.auth import authenticate, login, logout
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
# from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from app01.models import Admin
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


# Create your views here.
class HourUserRateThrottle(UserRateThrottle):
    scope = 'limit_per_hour'


class LoginAnonRateThrottle(AnonRateThrottle):
    THROTTLE_RATES = {"anon": "5/min"}


class AdminUserRateThrottle(UserRateThrottle):
    THROTTLE_RATES = {"user": "20/min"}


class AdminPageNumberPagination(PageNumberPagination):
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = None  # 最大页码数限制

    page_size_query_param = 'size'  # URL中每页显示条数的参数
    page_size = 10  # 每页显示多少条


class AdminModelSerializers(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = "__all__"


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)


class AdminView(ModelViewSet):
    queryset = Admin.objects.all().order_by('id')
    serializer_class = AdminModelSerializers
    pagination_class = AdminPageNumberPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    # authentication_classes = (JWTAuthentication, )
    # authentication_classes = (SessionAuthentication,)
    throttle_classes = [AdminUserRateThrottle, HourUserRateThrottle]

    def get_queryset(self):
        keyword = self.request.query_params.get('q')
        if not keyword:
            queryset = Admin.objects.all()
        else:
            queryset = Admin.objects.filter(username__icontains=keyword)
        return queryset


class LoginView(APIView):
    # throttle_scope = 'limit_login'
    throttle_classes = [LoginAnonRateThrottle, ]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(**serializer.validated_data)
        if user and user.is_active:
            login(request, user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']


@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        # print(request.data)
        # print(serializer.validated_data)
        # user = serializer.save()
        user = serializer.validated_data
        # print(user.get("username"))
        username = user.get("username")
        password = user.get("password")
        User.objects.create_user(username=username, password=password)
        return Response({'status': 'success', 'user': username})
    else:
        return Response(serializer.errors)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
