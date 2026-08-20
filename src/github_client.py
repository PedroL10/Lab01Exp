import os
import sys
from typing import Optional

import requests
from dotenv import load_dotenv

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

load_dotenv()


def run_query(query: str, variables: Optional[dict] = None) -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN nao encontrado. Copie .env.example para .env e "
            "preencha com seu token pessoal do GitHub."
        )

    response = requests.post(
        GITHUB_GRAPHQL_URL,
        json={"query": query, "variables": variables or {}},
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    response.raise_for_status()

    payload = response.json()
    if "errors" in payload:
        raise RuntimeError(f"Erro na API GraphQL: {payload['errors']}")

    return payload["data"]


AUTH_CHECK_QUERY = """
query {
  viewer {
    login
  }
  rateLimit {
    limit
    remaining
    resetAt
  }
}
"""


if __name__ == "__main__":
    try:
        data = run_query(AUTH_CHECK_QUERY)
    except Exception as exc:
        print(f"Falha na autenticacao: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Autenticado como: {data['viewer']['login']}")
    print(f"Rate limit: {data['rateLimit']['remaining']}/{data['rateLimit']['limit']}")
