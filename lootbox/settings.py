import os

from bugout.app import Bugout

# Bugout
BUGOUT_BROOD_URL = os.environ.get("BUGOUT_BROOD_URL", "https://auth.bugout.dev")
BUGOUT_SPIRE_URL = os.environ.get("BUGOUT_SPIRE_URL", "https://spire.bugout.dev")

bugout_client = Bugout(brood_api_url=BUGOUT_BROOD_URL, spire_api_url=BUGOUT_SPIRE_URL)

# MOONSTREAM_ENGINE_APPLICATION_ID = os.environ.get(
#     "MOONSTREAM_ENGINE_APPLICATION_ID", ""
# )
# if MOONSTREAM_ENGINE_APPLICATION_ID == "":
#     raise ValueError(
#         "MOONSTREAM_ENGINE_APPLICATION_ID environment variable must be set"
#     )

MOONSTREAM_ENGINE_ADMIN_ACCESS_TOKEN = os.environ.get(
    "MOONSTREAM_ENGINE_ADMIN_ACCESS_TOKEN", ""
)
if MOONSTREAM_ENGINE_ADMIN_ACCESS_TOKEN == "":
    raise ValueError(
        "MOONSTREAM_ENGINE_ADMIN_ACCESS_TOKEN environment variable must be set"
    )

DROP_JOURNAL_ID = os.environ.get("DROP_JOURNAL_ID")
if DROP_JOURNAL_ID is None:
    raise ValueError("DROP_JOURNAL_ID environment variable must be set")


# Origin
RAW_ORIGINS = os.environ.get("MOONSTREAM_CORS_ALLOWED_ORIGINS")
if RAW_ORIGINS is None:
    raise ValueError(
        "MOONSTREAM_CORS_ALLOWED_ORIGINS environment variable must be set (comma-separated list of CORS allowed origins)"
    )
ORIGINS = RAW_ORIGINS.split(",")

BROWNIE_NETWORK = os.environ.get("BROWNIE_NETWORK")
if BROWNIE_NETWORK is None:
    raise ValueError("BROWNIE_NETWORK environment variable must be set")

DROPPER_ADDRESS = os.environ.get("DROPPER_ADDRESS")
if DROPPER_ADDRESS is None:
    raise ValueError("DROPPER_ADDRESS environment variable must be set")

SIGNER_KEYSTORE = os.environ.get("SIGNER_KEYSTORE")
SIGNER_PASSWORD = os.environ.get("SIGNER_PASSWORD")

MOONSTREAM_SIGNING_SERVER_IP = os.environ.get("MOONSTREAM_SIGNING_SERVER_IP", None)

# DROP_DEADLINE_RAW = os.environ.get("DROP_DEADLINE")
# if DROP_DEADLINE_RAW is None:
#     raise ValueError("DROP_DEADLINE environment variable must be set")
# DROP_DEADLINE = int(DROP_DEADLINE_RAW)


# OpenAPI
DOCS_TARGET_PATH = "docs"

# AWS signer
AWS_DEFAULT_REGION = os.environ.get("AWS_DEFAULT_REGION")
if AWS_DEFAULT_REGION is None:
    raise ValueError("AWS_DEFAULT_REGION environment variable must be set")

MOONSTREAM_AWS_SIGNER_LAUNCH_TEMPLATE_ID = os.environ.get(
    "MOONSTREAM_AWS_SIGNER_LAUNCH_TEMPLATE_ID"
)
if MOONSTREAM_AWS_SIGNER_LAUNCH_TEMPLATE_ID is None:
    raise ValueError(
        "MOONSTREAM_AWS_SIGNER_LAUNCH_TEMPLATE_ID environment variable must be set"
    )

MOONSTREAM_AWS_SIGNER_IMAGE_ID = os.environ.get("MOONSTREAM_AWS_SIGNER_IMAGE_ID")
if MOONSTREAM_AWS_SIGNER_IMAGE_ID is None:
    raise ValueError("MOONSTREAM_AWS_SIGNER_IMAGE_ID environment variable must be set")

MOONSTREAM_AWS_SIGNER_INSTANCE_PORT = 17181
