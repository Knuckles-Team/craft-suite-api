"""The served backend API description, built from the pinned published document.

CONN-CRAFT-SUITE-API-R007. The input is the backend's own published OpenAPI
document, shipped byte for byte in ``api_spec/backend.openapi.json`` and
pinned by sha256 in ``api_spec/backend.source.json``. The server repairs it
in memory when it first builds the backend tools; nothing generated is
committed. Every change is a deterministic repair, never a new operation:

* a ``$ref`` to a schema the document omits becomes a typed open object;
* a parameter without a schema becomes a string;
* a multipart upload documented as a bogus ``request`` path parameter gets
  its real form body, with the file part carried as base64 text;
* the session credential scheme the backend reads is declared;
* each operation is classified ``read`` or one write class for governance.
"""

from __future__ import annotations

import copy
import hashlib
import json
from importlib import resources
from typing import Any

__all__ = ["CLASS_KEY", "normalize", "pinned_source", "served_document", "write_class"]

#: The vendor extension that carries an operation's governance class.
CLASS_KEY = "x-craft-suite-class"

METHODS = ("get", "put", "post", "delete", "patch")

#: Upload operations whose form schema the document names; the rest use the
#: generic upload form the backend drains field by field.
UPLOAD_FORMS = {
    "upload_audio_media_file_handler": "UploadAudioMediaFileForm",
    "upload_image_media_file_handler": "UploadImageMediaFileForm",
    "upload_new_engine_asset_media_file_handler": "UploadNewEngineAssetFileForm",
    "upload_new_scene_media_file_handler": "UploadNewSceneMediaFileForm",
    "upload_new_video_media_file_handler": "UploadNewVideoMediaFileForm",
    "upload_pmx_media_file_handler": "UploadPmxFileForm",
    "upload_saved_scene_media_file_handler": "UploadSavedSceneMediaFileForm",
    "upload_scene_snapshot_media_file_handler": "UploadSceneSnapshotMediaFileForm",
    "upload_spz_media_file_handler": "UploadSpzMediaFileForm",
    "upload_studio_shot_media_file_handler": "UploadStudioShotFileForm",
    "omni_upload_audio_media_file_handler": "OmniUploadAudioMediaFileForm",
    "omni_upload_image_media_file_handler": "OmniUploadImageMediaFileForm",
    "omni_upload_video_media_file_handler": "OmniUploadVideoMediaFileForm",
    "video_info_upload_handler": "VideoInfoUploadForm",
    "upload_new_editor_2d_project_handler": "NewProjectMultipartForm",
    "upload_new_mood_board_project_handler": "NewProjectMultipartForm",
    "upload_new_scene_3d_project_handler": "NewProjectMultipartForm",
    "upload_new_video_timeline_project_handler": "NewProjectMultipartForm",
    "upload_updated_editor_2d_project_handler": "UpdateProjectMultipartForm",
    "upload_updated_mood_board_project_handler": "UpdateProjectMultipartForm",
    "upload_updated_scene_3d_project_handler": "UpdateProjectMultipartForm",
    "upload_updated_video_timeline_project_handler": "UpdateProjectMultipartForm",
}

GENERIC_UPLOAD_FORM = {
    "type": "object",
    "required": ["uuid_idempotency_token", "file"],
    "properties": {
        "uuid_idempotency_token": {"type": "string"},
        "source": {"type": ["string", "null"], "enum": ["device", "file", None]},
        "title": {"type": ["string", "null"]},
        "visibility": {"type": ["string", "null"]},
        "maybe_generation_provider": {"type": ["string", "null"]},
    },
}

FILE_PART = {
    "type": "string",
    "contentEncoding": "base64",
    "description": "The file content, base64-encoded; sent as a binary part.",
}

SESSION_SCHEME = {"type": "apiKey", "in": "header", "name": "session"}

#: Path segments that mark an account-class write.
ACCOUNT_SEGMENTS = (
    "accounts",
    "api_keys",
    "beta_keys",
    "billing",
    "create_account",
    "credits",
    "login",
    "logout",
    "mcp",
    "session",
    "session_token",
    "user",
    "user_bans",
    "user_referral_codes",
)


def write_class(method: str, path: str) -> str:
    """``read`` for GET; else the governance class of the write."""
    if method == "get":
        return "read"
    parts = path.strip("/").split("/")
    segment = parts[1] if len(parts) > 1 else ""
    if "upload" in parts:
        return "upload"
    if segment in ("generate", "omni_gen", "image_studio") or "generate" in parts:
        return "generation"
    if segment == "moderation":
        return "moderation"
    if segment in ACCOUNT_SEGMENTS:
        return "account"
    return "write"


def references(value, found: set[str]) -> None:
    if isinstance(value, dict):
        ref = value.get("$ref")
        if isinstance(ref, str):
            found.add(ref.rsplit("/", 1)[1])
        for item in value.values():
            references(item, found)
    elif isinstance(value, list):
        for item in value:
            references(item, found)


def _typed_file_parts(schema: dict) -> dict:
    """Replace byte-array file parts with base64 text parts."""
    schema = copy.deepcopy(schema)
    for name, prop in schema.get("properties", {}).items():
        items = prop.get("items", {}) if isinstance(prop, dict) else {}
        if prop.get("type") == "array" and items.get("format") == "binary":
            schema["properties"][name] = dict(
                FILE_PART, description=prop.get("description", FILE_PART["description"])
            )
    if "file" not in schema.get("properties", {}):
        schema.setdefault("properties", {})["file"] = dict(FILE_PART)
    return schema


def _repair_upload(operation: dict, schemas: dict) -> None:
    operation["parameters"] = [
        p
        for p in operation.get("parameters", [])
        if not (p.get("in") == "path" and p.get("name") == "request")
    ]
    form = UPLOAD_FORMS.get(operation["operationId"])
    body = copy.deepcopy(schemas[form]) if form else copy.deepcopy(GENERIC_UPLOAD_FORM)
    operation["requestBody"] = {
        "required": True,
        "content": {"multipart/form-data": {"schema": _typed_file_parts(body)}},
    }


def _repair_parameters(operation: dict) -> None:
    for parameter in operation.get("parameters", []):
        schema = parameter.get("schema")
        if not schema or set(schema) <= {"default", "description"}:
            parameter["schema"] = {"type": "string"}


def normalize(document: dict) -> dict:
    document = copy.deepcopy(document)
    document.pop("servers", None)
    components = document.setdefault("components", {})
    schemas = components.setdefault("schemas", {})
    found: set[str] = set()
    references(document, found)
    for name in sorted(found - set(schemas)):
        schemas[name] = {
            "type": "object",
            "additionalProperties": True,
            "description": f"{name}: not described by the published document.",
        }
    components.setdefault("securitySchemes", {})["signed_session"] = SESSION_SCHEME
    document["security"] = [{}, {"signed_session": []}]
    for path, item in document["paths"].items():
        for method in METHODS:
            operation = item.get(method)
            if operation is None:
                continue
            if any(
                p.get("in") == "path" and p.get("name") == "request"
                for p in operation.get("parameters", [])
            ):
                _repair_upload(operation, schemas)
            _repair_parameters(operation)
            operation[CLASS_KEY] = write_class(method, path)
    return document


def pinned_source() -> tuple[bytes, dict[str, Any]]:
    """The published document's bytes and its provenance record."""
    root = resources.files(__package__).joinpath("api_spec")
    data = root.joinpath("backend.openapi.json").read_bytes()
    provenance = json.loads(root.joinpath("backend.source.json").read_text())
    return data, provenance


def served_document() -> dict[str, Any]:
    """The repaired description the backend tools are built from.

    Raises:
        ValueError: the shipped document does not match its pinned sha256.
    """
    data, provenance = pinned_source()
    actual = hashlib.sha256(data).hexdigest()
    if actual != provenance["sha256"]:
        raise ValueError(
            f"pinned backend document sha256 {actual} != {provenance['sha256']}"
        )
    return normalize(json.loads(data))
