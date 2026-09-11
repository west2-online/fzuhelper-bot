import asconnect
import asconnect.models
from asconnect.sorting import BuildsSort


def build_client(issuer_id: str, key_id: str, key_contents: str) -> asconnect.Client:
    return asconnect.Client(
        issuer_id=issuer_id,
        key_id=key_id,
        key_contents=key_contents.replace("\\n", "\n"),
    )


def query_ready_test_version(
    client: asconnect.Client, app_id: str, limit: int = 10
) -> list[str]:
    builds = list(
        client.build.get_builds(app_id=app_id, sort=BuildsSort.VERSION_REVERSED)
    )
    ready_versions: list[str] = []
    for build in builds[:limit]:
        beta = client.build.get_beta_detail(build)
        if beta is None:
            continue
        if (
            beta.attributes.external_build_state
            == asconnect.models.ExternalBetaState.IN_BETA_TESTING
        ):
            ready_versions.append(build.attributes.version)
    return ready_versions
