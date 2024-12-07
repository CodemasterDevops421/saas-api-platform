from fastapi import APIRouter, Depends
from ..core.cache_manager import CacheManager
from ..core.auth import get_current_admin_user

router = APIRouter(prefix='/cache', tags=['cache'])

@router.post('/clear/{pattern}')
async def clear_cache(pattern: str, _=Depends(get_current_admin_user)):
    await CacheManager.invalidate_pattern(pattern)
    return {'message': f'Cache cleared for pattern: {pattern}'}

@router.get('/stats')
async def get_cache_stats(_=Depends(get_current_admin_user)):
    return CacheManager.get_stats()