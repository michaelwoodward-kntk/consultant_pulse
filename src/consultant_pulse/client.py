"""Databricks workspace connectivity.

Local use passes the CLI profile. CI passes a service principal through
environment variables and does not use the profile.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from typing import Any

from consultant_pulse.config import Settings

ClientFactory = Callable[..., Any]


def connect(
    settings: Settings | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    client_factory: ClientFactory | None = None,
) -> Any:
    """Return a Databricks WorkspaceClient for the given settings."""
    env = os.environ if environ is None else environ
    active = settings or Settings.from_env(env)
    factory = client_factory or _workspace_client

    client_id = env.get("DATABRICKS_CLIENT_ID", "").strip()
    client_secret = env.get("DATABRICKS_CLIENT_SECRET", "").strip()
    if client_id and client_secret:
        return factory(host=active.host, client_id=client_id, client_secret=client_secret)

    token = env.get("DATABRICKS_TOKEN", "").strip()
    if token:
        return factory(host=active.host, token=token)

    return factory(host=active.host, profile=active.profile)


def _workspace_client(**kwargs: Any) -> Any:
    from databricks.sdk import WorkspaceClient

    return WorkspaceClient(**kwargs)
