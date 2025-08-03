#!/usr/bin/env python3
"""
BrainSAIT Healthcare Platform - Enhanced Backend Service
Fixes critical API endpoints and adds missing OID Tree functionality
"""

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import logging
import psycopg2
import psycopg2.extras
import json
from datetime import datetime
import uuid

# Enhanced logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BrainSAIT Healthcare Platform",
    description="Enhanced healthcare identity and OID management system",
    version="2.1.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4200", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "brainsait_healthcare",
    "user": "brainsait_admin",
    "password": "brainsait_healthcare_2025!"
}

BASE_OID = "1.3.6.1.4.1.61026"

def get_db_connection():
    """Get database connection with enhanced error handling"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# Fix missing OID Tree endpoint
@app.get("/oid-tree")
async def get_oid_tree(
    depth: Optional[int] = Query(3, ge=1, le=10),
    filter_type: Optional[str] = Query(None),
    include_metadata: bool = Query(True)
):
    """Get OID tree structure with hierarchical organization"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Get all healthcare identities for tree structure
        query = """
            SELECT
                id,
                entity_type,
                name,
                name_ar,
                role,
                organization,
                full_oid,
                status,
                created_at,
                metadata
            FROM healthcare_identities
            WHERE status = 'active'
            ORDER BY full_oid
        """

        cur.execute(query)
        identities = cur.fetchall()

        # Build hierarchical tree structure
        tree_structure = {
            "base_oid": BASE_OID,
            "name": "BrainSAIT Healthcare Platform",
            "name_ar": "منصة برينسايت الصحية",
            "children": {},
            "total_nodes": len(identities),
            "last_updated": datetime.now().isoformat()
        }

        for identity in identities:
            oid_parts = identity['full_oid'].split('.')
            current_level = tree_structure["children"]

            # Build path through OID hierarchy
            path = []
            for i, part in enumerate(oid_parts):
                path.append(part)
                key = '.'.join(path)

                if key not in current_level:
                    current_level[key] = {
                        "oid": key,
                        "name": identity['name'] if i == len(oid_parts) - 1 else f"Branch {part}",
                        "name_ar": identity['name_ar'] if i == len(oid_parts) - 1 else f"فرع {part}",
                        "type": identity['entity_type'] if i == len(oid_parts) - 1 else "branch",
                        "children": {},
                        "is_leaf": i == len(oid_parts) - 1
                    }

                    if i == len(oid_parts) - 1 and include_metadata:
                        current_level[key].update({
                            "id": str(identity['id']),
                            "role": identity['role'],
                            "organization": identity['organization'],
                            "status": identity['status'],
                            "created_at": identity['created_at'].isoformat() if identity['created_at'] else None,
                            "metadata": identity['metadata'] or {}
                        })

                current_level = current_level[key]["children"]

        cur.close()
        conn.close()

        return tree_structure

    except Exception as e:
        logger.error(f"Failed to get OID tree: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve OID tree: {str(e)}")

# Enhanced healthcare identities endpoint with better error handling
@app.get("/healthcare-identities")
async def list_healthcare_identities_enhanced(
    entity_type: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    organization: Optional[str] = Query(None),
    status: Optional[str] = Query("active"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Enhanced healthcare identities listing with better filtering"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Build dynamic query with proper parameterization
        conditions = ["1=1"]
        params = []

        if entity_type:
            conditions.append("entity_type = %s")
            params.append(entity_type)

        if role:
            conditions.append("role = %s")
            params.append(role)

        if organization:
            conditions.append("organization ILIKE %s")
            params.append(f"%{organization}%")

        if status:
            conditions.append("status = %s")
            params.append(status)

        query = f"""
            SELECT
                id,
                entity_type,
                user_id,
                name,
                name_ar,
                role,
                access_level,
                national_id,
                nphies_id,
                organization,
                department,
                expires,
                full_oid,
                metadata,
                status,
                created_at,
                updated_at
            FROM healthcare_identities
            WHERE {' AND '.join(conditions)}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """

        params.extend([limit, offset])
        cur.execute(query, params)
        identities = cur.fetchall()

        # Get total count
        count_query = f"""
            SELECT COUNT(*)
            FROM healthcare_identities
            WHERE {' AND '.join(conditions)}
        """
        cur.execute(count_query, params[:-2])  # Exclude limit and offset
        total = cur.fetchone()[0]

        cur.close()
        conn.close()

        return {
            "success": True,
            "identities": [dict(identity) for identity in identities],
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            },
            "filters_applied": {
                "entity_type": entity_type,
                "role": role,
                "organization": organization,
                "status": status
            }
        }

    except Exception as e:
        logger.error(f"Failed to list healthcare identities: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Failed to retrieve healthcare identities",
                "detail": str(e)
            }
        )

# Enhanced healthcare identity registration
@app.post("/healthcare-identities")
async def register_healthcare_identity_enhanced(identity_data: dict):
    """Enhanced healthcare identity registration with validation"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Generate unique ID and OID
        identity_id = str(uuid.uuid4())

        # Simple OID generation for now
        entity_type = identity_data.get('entity_type', 'PROVIDER')
        timestamp_suffix = str(int(datetime.now().timestamp()))[-6:]
        full_oid = f"{BASE_OID}.1.{timestamp_suffix}"

        # Insert with proper error handling
        insert_query = """
            INSERT INTO healthcare_identities (
                id, entity_type, user_id, name, name_ar, role, access_level,
                national_id, nphies_id, organization, department, expires,
                full_oid, metadata, status, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        current_time = datetime.now()
        expires = datetime.fromisoformat(identity_data.get('expires', (current_time.replace(year=current_time.year + 1)).isoformat()))

        cur.execute(insert_query, (
            identity_id,
            identity_data.get('entity_type', 'PROVIDER'),
            identity_data.get('user_id', ''),
            identity_data.get('name', ''),
            identity_data.get('name_ar', ''),
            identity_data.get('role', 'USER'),
            identity_data.get('access_level', 'MEDIUM'),
            identity_data.get('national_id'),
            identity_data.get('nphies_id'),
            identity_data.get('organization', ''),
            identity_data.get('department', ''),
            expires,
            full_oid,
            json.dumps(identity_data.get('metadata', {})),
            'active',
            current_time,
            current_time
        ))

        cur.close()
        conn.close()

        logger.info(f"Healthcare identity registered: {full_oid} for {identity_data.get('name')}")

        return {
            "success": True,
            "status": "registered",
            "identity_id": identity_id,
            "oid": full_oid,
            "entity_type": identity_data.get('entity_type'),
            "name": identity_data.get('name'),
            "expires": expires.isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to register healthcare identity: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Failed to register healthcare identity",
                "detail": str(e)
            }
        )

# Enhanced OIDs endpoint (legacy compatibility)
@app.get("/oids")
async def list_oids_enhanced():
    """Enhanced legacy OID endpoint with better error handling"""
    try:
        result = await list_healthcare_identities_enhanced()

        # Transform to legacy format if needed
        if isinstance(result, dict) and result.get('success'):
            return {
                "success": True,
                "oids": result['identities'],
                "total": result['pagination']['total']
            }
        else:
            return result

    except Exception as e:
        logger.error(f"Failed to list OIDs: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Failed to retrieve OIDs",
                "detail": str(e)
            }
        )

# System status and diagnostics
@app.get("/system/status")
async def get_system_status():
    """Comprehensive system status endpoint"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check database tables
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cur.fetchall()]

        # Count records in main tables
        counts = {}
        if 'healthcare_identities' in tables:
            cur.execute("SELECT COUNT(*) FROM healthcare_identities WHERE status = 'active'")
            counts['active_identities'] = cur.fetchone()[0]

        if 'nphies_claims' in tables:
            cur.execute("SELECT COUNT(*) FROM nphies_claims")
            counts['nphies_claims'] = cur.fetchone()[0]

        cur.close()
        conn.close()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "BrainSAIT Healthcare Platform Enhanced",
            "version": "2.1.0",
            "database": {
                "connected": True,
                "tables": tables,
                "counts": counts
            },
            "endpoints": {
                "oid_tree": "/oid-tree",
                "healthcare_identities": "/healthcare-identities",
                "legacy_oids": "/oids",
                "system_status": "/system/status"
            }
        }

    except Exception as e:
        logger.error(f"System status check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
