from consultant_pulse.client import connect
from consultant_pulse.config import Settings


def _settings() -> Settings:
    return Settings(
        catalog="workspace",
        schema="consultant_pulse",
        volume="feedback_raw",
        bronze_table="feedback_bronze",
        host="https://dbc-c43489fd-406c.cloud.databricks.com",
        profile="dbc-c43489fd",
    )


def test_connect_uses_profile_when_no_credentials_are_set():
    captured: dict[str, str] = {}

    def factory(**kwargs: str) -> dict[str, str]:
        captured.update(kwargs)
        return captured

    connect(_settings(), environ={}, client_factory=factory)

    assert captured == {
        "host": "https://dbc-c43489fd-406c.cloud.databricks.com",
        "profile": "dbc-c43489fd",
    }


def test_connect_prefers_service_principal_over_profile():
    captured: dict[str, str] = {}

    def factory(**kwargs: str) -> dict[str, str]:
        captured.update(kwargs)
        return captured

    connect(
        _settings(),
        environ={
            "DATABRICKS_CLIENT_ID": "client-id",
            "DATABRICKS_CLIENT_SECRET": "client-secret",
        },
        client_factory=factory,
    )

    assert captured["client_id"] == "client-id"
    assert captured["client_secret"] == "client-secret"
    assert "profile" not in captured


def test_api_client_uses_the_injected_connector():
    from consultant_pulse.api import ConsultantPulseApi

    settings = _settings()
    seen: list[Settings] = []

    def connector(active: Settings) -> str:
        seen.append(active)
        return "workspace-client"

    api = ConsultantPulseApi(settings, connector=connector)

    assert api.client() == "workspace-client"
    assert seen == [settings]
