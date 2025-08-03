"""
BrainSAIT Healthcare Identity Service - Business Logic Components
Following OidTree 5-component pattern
"""

from typing import List, Optional
from models.healthcare import HealthcareIdentity, EntityType
from core.database import get_db_connection
from core.oid_generator import generate_oid
import logging
import json

logger = logging.getLogger(__name__)


class HealthcareIdentityService:
    """Healthcare identity management service"""
    
    async def get_identities(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        entity_type: Optional[str] = None
    ) -> List[dict]:
        """Get healthcare identities with filtering"""
        try:
            with get_db_connection() as (conn, cursor):
                query = "SELECT * FROM healthcare_identities WHERE is_active = TRUE"
                params = []
                
                if entity_type:
                    query += " AND entity_type = ?"
                    params.append(entity_type)
                
                query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, skip])
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"Error retrieving healthcare identities: {e}")
            raise
    
    async def register_identity(self, identity: HealthcareIdentity) -> dict:
        """Register new healthcare identity"""
        try:
            oid = generate_oid(identity.entity_type)
            
            with get_db_connection() as (conn, cursor):
                cursor.execute("""
                    INSERT INTO healthcare_identities 
                    (entity_type, user_id, name, name_ar, role, access_level, 
                     national_id, nphies_id, organization, department, oid, 
                     expires, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    identity.entity_type, identity.user_id, identity.name,
                    identity.name_ar, identity.role, identity.access_level,
                    identity.national_id, identity.nphies_id, identity.organization,
                    identity.department, oid, identity.expires,
                    json.dumps(identity.metadata) if identity.metadata else None
                ))
                
                return {
                    "success": True,
                    "message": "Healthcare identity registered successfully",
                    "oid": oid,
                    "user_id": identity.user_id
                }
                
        except Exception as e:
            logger.error(f"Error registering healthcare identity: {e}")
            raise
    
    async def update_identity(self, identity_id: str, identity: HealthcareIdentity) -> dict:
        """Update healthcare identity"""
        try:
            with get_db_connection() as (conn, cursor):
                cursor.execute("""
                    UPDATE healthcare_identities 
                    SET name = ?, name_ar = ?, role = ?, access_level = ?,
                        organization = ?, department = ?, expires = ?, metadata = ?
                    WHERE user_id = ? AND is_active = TRUE
                """, (
                    identity.name, identity.name_ar, identity.role, 
                    identity.access_level, identity.organization, identity.department,
                    identity.expires, json.dumps(identity.metadata) if identity.metadata else None,
                    identity_id
                ))
                
                if cursor.rowcount == 0:
                    raise ValueError(f"Healthcare identity {identity_id} not found")
                
                return {
                    "success": True,
                    "message": "Healthcare identity updated successfully"
                }
                
        except Exception as e:
            logger.error(f"Error updating healthcare identity: {e}")
            raise
    
    async def revoke_identity(self, identity_id: str) -> dict:
        """Revoke (soft delete) healthcare identity"""
        try:
            with get_db_connection() as (conn, cursor):
                cursor.execute("""
                    UPDATE healthcare_identities 
                    SET is_active = FALSE
                    WHERE user_id = ? AND is_active = TRUE
                """, (identity_id,))
                
                if cursor.rowcount == 0:
                    raise ValueError(f"Healthcare identity {identity_id} not found")
                
                return {
                    "success": True,
                    "message": "Healthcare identity revoked successfully"
                }
                
        except Exception as e:
            logger.error(f"Error revoking healthcare identity: {e}")
            raise