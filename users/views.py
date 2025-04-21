from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsProfileOwner, CanViewUserProfile
from users.serializers import UserSerializer, ChangePasswordSerializer


class UserCreateAPIView(generics.CreateAPIView):
    """ Класс для регистрации пользователя """

    permission_classes = [AllowAny]
    serializer_class = UserSerializer


class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """ Класс для просмотра, изменения и удаления пользователя """

    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()

    def get_permissions(self):
        """ Настройка разрешений просмотра, редактирования и удаления """
        if self.request.method == 'DELETE':  # только администратор может принимать решение об удалении аккаунта,
            # т.к. при удалении аккаунта удаляются объекты `SupplyChainMember`, которые были созданы этим сотрудником
            return [IsAdminUser()]
        if self.request.method in SAFE_METHODS:  # чтение доступно сотрудникам, владельцу профиля и администратору
            return [CanViewUserProfile()]
        return [IsProfileOwner()]  # редактирование профиля доступно только владельцу


class ChangePasswordAPIView(APIView):
    """ Класс для смены пароля """

    def post(self, *args, **kwargs):
        user = self.request.user
        serializer = ChangePasswordSerializer(data=self.request.data, context={'user': user})
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"detail": 'Пароль успешно изменён.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
