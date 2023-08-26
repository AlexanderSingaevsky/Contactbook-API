from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter

from src.database_postgres import get_session
from src.auth.schemas import UserModel, UserResponse, TokenModel
from src.auth import repository as repository_users
from src.auth.service import auth_service
from src.mailing.service import mail_service


router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()

dependencies = [Depends(RateLimiter(times=2, seconds=5))]


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request,
                 db: AsyncSession = Depends(get_session)):
    """
    .. http:post:: /signup

       Register a new user and send a verification email.

       :param body: The input data required for user registration, including email, password, and other user details.
       :type body: UserModel
       :param background_tasks: A utility for background tasks execution, used here to send the verification email asynchronously.
       :type background_tasks: BackgroundTasks
       :param request: The current HTTP request object to extract base URL for email generation.
       :type request: Request
       :param db: The asynchronous database session to be used for the operation. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :return: A message indicating the successful registration of the user and a prompt to check the email for confirmation.
       :rtype: dict
       :status 201: User was successfully registered.
       :status 409: An account with the provided email already exists.
       :raises HTTPException: If an account with the provided email already exists, an HTTPException with a 409 status code is raised.

       **Dependencies**:

       - RateLimiter: Limits the number of requests to 2 every 5 seconds.
       - get_session: Dependency to get the current asynchronous database session.

       **Notes**:

       The function hashes the password before saving the user to the database. After successful registration, a verification email is sent to the user's email address asynchronously.
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(mail_service.send_verification_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login", response_model=TokenModel, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    """
    .. http:post:: /login

       Authenticate a user and provide an access and refresh token.

       :param body: The input data required for user authentication, which includes the username (email) and password.
       :type body: OAuth2PasswordRequestForm, optional
       :param db: The asynchronous database session to be used for the operation. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :return: A dictionary containing the access token, refresh token, and token type.
       :rtype: TokenModel
       :raises HTTPException:
           - 401 Unauthorized if the email is invalid, the email is not confirmed, or the password is incorrect.

       **Dependencies**:

       - RateLimiter: Limits the number of requests to 2 every 5 seconds.
       - OAuth2PasswordRequestForm: Dependency that provides the OAuth2 password request form data.
       - get_session: Dependency to get the current asynchronous database session.

       **Notes**:

       The function first checks the validity of the provided email and then confirms if the email is verified. It then verifies the provided password. If all checks pass, it generates and returns the access and refresh tokens.
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    elif not user.is_confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    elif not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    else:
        access_token = await auth_service.create_access_token(data={"sub": user.email})
        refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
        await repository_users.update_token(user, refresh_token, db)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel,
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security),
                        db: AsyncSession = Depends(get_session)):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
