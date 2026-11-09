"""The only place that builds the OpenAI client, so changing provider stays contained."""

from openai import OpenAI
from pydantic import SecretStr


def openai_client(api_key: SecretStr) -> OpenAI:
    return OpenAI(api_key=api_key.get_secret_value())
