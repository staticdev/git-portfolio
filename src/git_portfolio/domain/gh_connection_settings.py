"""Github connection settings model."""
import collections


GhConnectionSettings = collections.namedtuple(
    "ConnectGithub", ["github_access_token", "github_hostname"]
)
