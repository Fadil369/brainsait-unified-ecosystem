"""
BrainSAIT OID Generator - Utility Components
Following OidTree 5-component pattern
"""

import time
import uuid
import hashlib
from models.healthcare import EntityType


def generate_oid(entity_type: EntityType) -> str:
    """
    Generate Healthcare Object Identifier (OID) for BrainSAIT platform
    
    OID Structure: 1.3.6.1.4.1.12345.{entity_type}.{unique_id}
    - 1.3.6.1.4.1: ISO/IEC standard prefix
    - 12345: BrainSAIT organization identifier
    - entity_type: Numeric representation of entity type
    - unique_id: Time-based unique identifier
    """
    
    # Base OID for BrainSAIT Healthcare Platform
    base_oid = "1.3.6.1.4.1.12345"
    
    # Entity type mapping
    entity_mapping = {
        EntityType.PATIENT: "1",
        EntityType.PROVIDER: "2", 
        EntityType.ORGANIZATION: "3",
        EntityType.DEVICE: "4",
        EntityType.PROCEDURE: "5",
        EntityType.MEDICATION: "6",
        EntityType.RECORD: "7",
        EntityType.INSURANCE: "8",
        EntityType.APPOINTMENT: "9",
        EntityType.AI_SERVICE: "10"
    }
    
    # Get entity type number
    entity_num = entity_mapping.get(entity_type, "99")
    
    # Generate unique identifier based on timestamp and UUID
    timestamp = str(int(time.time() * 1000))  # milliseconds
    unique_uuid = str(uuid.uuid4()).replace("-", "")[:12]
    
    # Create hash for additional uniqueness
    hash_input = f"{entity_type}{timestamp}{unique_uuid}"
    hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
    
    # Combine to create final OID
    unique_id = f"{timestamp}{hash_value}"
    
    return f"{base_oid}.{entity_num}.{unique_id}"