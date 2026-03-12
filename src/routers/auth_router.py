"""Роутер аутентификации пользователей."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.controllers.auth_controller import AuthController
from src.interfaces.auth_schemas import AuthTokenSchema, UserLoginSchema, UserRegisterSchema, UserResponseSchema
from src.modules.auth.repository import AuthRepository
from src.modules.auth.service import AuthService, InvalidCredentialsError, InvalidTokenError, UserAlreadyExistsError

router = APIRouter(prefix="/auth", tags=["auth"])
_bearer = HTTPBearer(auto_error=False)

_repository = AuthRepository()
_service = AuthService(_repository)
_controller = AuthController(_service)


def configure_auth_repository(db_path: str | None = None) -> None:
    """Переключает модуль auth на конкретный файл БД."""

    global _repository, _service, _controller
    _repository = AuthRepository(db_path=db_path)
    _service = AuthService(_repository)
    _controller = AuthController(_service)


def _extract_bearer_token(credentials: HTTPAuthorizationCredentials | None) -> str:
    """Извлекает bearer token из заголовка Authorization."""

    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Требуется токен авторизации")
    return credentials.credentials


@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegisterSchema) -> UserResponseSchema:
    """Регистрирует нового пользователя."""

    try:
        return _controller.register(payload)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/login", response_model=AuthTokenSchema)
def login(payload: UserLoginSchema) -> AuthTokenSchema:
    """Выполняет вход пользователя."""

    try:
        return _controller.login(payload)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.get("/me", response_model=UserResponseSchema)
def me(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> UserResponseSchema:
    """Возвращает профиль текущего пользователя."""

    token = _extract_bearer_token(credentials)
    try:
        return _controller.me(token)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


def reset_auth_module_state() -> None:
    """Очищает состояние auth-модуля для тестов."""

    _repository.reset()
