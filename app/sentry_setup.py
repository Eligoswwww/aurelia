import os
import sentry_sdk

def setup_sentry():
    sentry_dsn = os.getenv("SENTRY_DSN", "")
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            traces_sample_rate=1.0,
            environment=os.getenv("ENVIRONMENT", "development"),
        )
