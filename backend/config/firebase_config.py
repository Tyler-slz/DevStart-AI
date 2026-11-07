import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from config.settings import BASE_DIR, settings

logger = logging.getLogger(__name__)

_firestore_client = None
_firebase_initialized = False


def init_firebase():
    """Initialize Firebase Admin SDK if credentials are provided."""
    global _firestore_client, _firebase_initialized

    if _firebase_initialized:
        return _firestore_client

    _firebase_initialized = True
    cred_val = settings.FIREBASE_CREDENTIALS
    if not cred_val:
        logger.info("FIREBASE_CREDENTIALS not set; running without Firestore persistence.")
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            # Support either a JSON string or a file path
            if cred_val.startswith("{"):
                cred_dict = json.loads(cred_val)
                cred = credentials.Certificate(cred_dict)
            else:
                cred_path = Path(cred_val)
                if not cred_path.is_absolute():
                    cred_path = BASE_DIR / cred_path
                if not cred_path.exists():
                    logger.warning("Firebase credentials file not found at %s", cred_path)
                    return None
                cred = credentials.Certificate(str(cred_path))

            firebase_admin.initialize_app(cred)

        _firestore_client = firestore.client()
        logger.info("Firebase Admin initialized successfully.")
    except Exception as exc:
        logger.warning("Could not initialize Firebase Admin: %s", exc)
        _firestore_client = None

    return _firestore_client


def save_analysis_record(repo_full_name: str, record_type: str, payload: Dict[str, Any]) -> Optional[str]:
    """Persist an analysis result or PR draft to Firestore if configured."""
    db = init_firebase()
    if db is None:
        return None

    try:
        from datetime import datetime, timezone

        doc_ref = db.collection("repositories").document(repo_full_name.replace("/", "__"))
        doc_ref.set(
            {
                "repo": repo_full_name,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                record_type: payload,
            },
            merge=True,
        )
        return doc_ref.id
    except Exception as exc:
        logger.warning("Failed to save record to Firestore: %s", exc)
        return None


def get_analysis_record(repo_full_name: str) -> Optional[Dict[str, Any]]:
    """Retrieve cached analysis record for a repository from Firestore if available."""
    db = init_firebase()
    if db is None:
        return None

    try:
        doc_ref = db.collection("repositories").document(repo_full_name.replace("/", "__"))
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
    except Exception as exc:
        logger.warning("Failed to read record from Firestore: %s", exc)
    return None

