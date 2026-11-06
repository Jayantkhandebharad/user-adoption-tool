from app.config import Settings


def test_empty_values_mean_unset() -> None:
    # Compose passes unset optional variables as empty strings.
    settings = Settings(setup_token="", studio_dist="", _env_file=None)
    assert settings.setup_token is None
    assert settings.studio_dist is None


def test_public_origin_and_secure_cookies() -> None:
    settings = Settings(public_url="https://guide.example.com/studio", _env_file=None)
    assert settings.public_origin == "https://guide.example.com"
    assert settings.secure_cookies is True
