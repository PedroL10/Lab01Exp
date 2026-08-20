import json
import os
import sys

from github_client import run_query

SEARCH_QUERY = "stars:>1 sort:stars-desc"
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "repositorios_lab01_s01.json")

REPOSITORIES_QUERY = """
query ($searchQuery: String!, $first: Int!, $after: String) {
  search(query: $searchQuery, type: REPOSITORY, first: $first, after: $after) {
    repositoryCount
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      ... on Repository {
        nameWithOwner
        stargazerCount
        createdAt
        pushedAt
        primaryLanguage {
          name
        }
        releases {
          totalCount
        }
        issues {
          totalCount
        }
        closedIssues: issues(states: CLOSED) {
          totalCount
        }
        pullRequests(states: MERGED) {
          totalCount
        }
      }
    }
  }
}
"""


def _flatten(node):
    return {
        "name_with_owner": node["nameWithOwner"],
        "stargazers": node["stargazerCount"],
        "created_at": node["createdAt"],
        "pushed_at": node["pushedAt"],
        "primary_language": (node["primaryLanguage"] or {}).get("name"),
        "releases_total": node["releases"]["totalCount"],
        "issues_total": node["issues"]["totalCount"],
        "issues_closed_total": node["closedIssues"]["totalCount"],
        "pull_requests_merged_total": node["pullRequests"]["totalCount"],
    }


def fetch_top_repositories(count, page_size=10):
    repos = []
    cursor = None

    while len(repos) < count:
        variables = {
            "searchQuery": SEARCH_QUERY,
            "first": min(page_size, count - len(repos)),
            "after": cursor,
        }
        page = run_query(REPOSITORIES_QUERY, variables)["search"]
        repos.extend(_flatten(node) for node in page["nodes"])

        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]

    return repos


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    repos = fetch_top_repositories(count)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(repos, f, indent=2, ensure_ascii=False)

    print(f"{len(repos)} repositorios salvos em {OUTPUT_PATH}")
