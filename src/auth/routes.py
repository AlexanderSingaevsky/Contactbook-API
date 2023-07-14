from fastapi import APIRouter, HTTPException, Depends, status, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.auth.schemas import UserModel, UserResponse, TokenModel
from src.auth import repository as repository_users
from src.auth.service import auth_service

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, db: AsyncSession = Depends(get_session)):
    """
       ## Create a new user account.

       ### Args:
           body (UserModel): The user information for creating the account.
           db (AsyncSession): The database session.

       ### Returns:
           UserResponse: The newly created user's information.

       ### Raises:
           HTTPException: If an account with the provided email already exists.
               Returns HTTP status code 409 (Conflict).
       """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    return {"user": new_user, "detail": "User successfully created"}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    """
        ## Log in to the user account and generate access and refresh tokens.

        ### Args:
            body (OAuth2PasswordRequestForm): The login request body containing username (email) and password.
            db (AsyncSession): The database session.

        ### Returns:
            TokenModel: The access and refresh tokens.

        ### Raises:
            HTTPException: If the provided email is invalid or the password is incorrect.
                Returns HTTP status code 401 (Unauthorized).
        """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel, include_in_schema=False)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security),
                        db: AsyncSession = Depends(get_session)):
    """
        ## Refresh the access token using a valid refresh token.

        ### Args:
            credentials (HTTPAuthorizationCredentials): The authorization credentials containing the refresh token.
            db (AsyncSession): The database session.

        ### Returns:
            TokenModel: The refreshed access and refresh tokens.

        ### Raises:
            HTTPException: If the provided refresh token is invalid or expired.
                Returns HTTP status code 401 (Unauthorized).
        """
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
