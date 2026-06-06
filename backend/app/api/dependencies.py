from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt
from app.services.inference_service import InferenceService
from app.services.model_registry import ModelRegistry
from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

def get_inference_service() -> InferenceService:
    return InferenceService()

def require_model_loaded_for_target(target: str) -> str:
    registry_state = ModelRegistry.get_registry_state()
    target_info = registry_state.get(target, {})
    if not target_info.get("active_version"):
        raise HTTPException(
            status_code=503, 
            detail=f"No active model currently loaded for target '{target}'"
        )
    return target

async def get_current_user(
    api_key: str = Security(api_key_header),
    token: str = Depends(oauth2_scheme)
):
    # 1. Check API Key
    if api_key:
        if api_key == settings.api_key:
            return "api_client"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
        
    # 2. Check JWT Token
    if token:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            return username
        except JWTError:
            raise credentials_exception
            
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
