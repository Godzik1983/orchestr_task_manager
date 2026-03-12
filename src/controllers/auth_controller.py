"""Контроллер модуля auth."""

from src.interfaces.auth_schemas import AuthTokenSchema, UserLoginSchema, UserRegisterSchema, UserResponseSchema
from src.modules.auth.service import AuthService
from src.views.auth_view import to_user_response


class AuthController:
    """Прослойка между auth-роутером и сервисом аутентификации."""

    def __init__(self, service: AuthService) -> None:
        self._service = service

    def register(self, payload: UserRegisterSchema) -> UserResponseSchema:
        """Регистрирует пользователя и возвращает данные профиля."""

        user = self._service.register(payload)
        return to_user_response(user)

    def login(self, payload: UserLoginSchema) -> AuthTokenSchema:
        """Выполняет вход и возвращает access token."""

        token = self._service.login(payload)
        return AuthTokenSchema(access_token=token)

    def me(self, token: str) -> UserResponseSchema:
        """Возвращает данные текущего пользователя из токена."""

        user = self._service.get_current_user(token)
        return to_user_response(user)
