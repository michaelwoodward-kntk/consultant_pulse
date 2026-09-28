from consultant_pulse.main import main


def test_score_flag_prints_normalized_value(capsys):
    main(["--score", "0"])
    assert capsys.readouterr().out.strip() == "1.0"


def test_show_config_and_ddl(capsys, monkeypatch):
    monkeypatch.setenv("CONSULTANT_PULSE_CATALOG", "workspace")
    monkeypatch.setenv("CONSULTANT_PULSE_SCHEMA", "consultant_pulse")
    monkeypatch.setenv("CONSULTANT_PULSE_VOLUME", "feedback_raw")
    monkeypatch.setenv("CONSULTANT_PULSE_BRONZE_TABLE", "feedback_bronze")
    monkeypatch.setenv("DATABRICKS_HOST", "https://dbc-c43489fd-406c.cloud.databricks.com")
    monkeypatch.setenv("DATABRICKS_CONFIG_PROFILE", "dbc-c43489fd")

    main(["--show-config", "--bronze-ddl"])
    output = capsys.readouterr().out

    assert "schema=consultant_pulse" in output
    assert "CREATE TABLE IF NOT EXISTS `workspace`.`consultant_pulse`.`feedback_bronze`" in output
