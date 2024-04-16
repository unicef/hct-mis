from hct_mis_api.config.env import env

AZURE_ACCOUNT_NAME = env("STORAGE_AZURE_ACCOUNT_NAME", default="")
AZURE_ACCOUNT_KEY = env("STORAGE_AZURE_ACCOUNT_KEY", default="")

if AZURE_ACCOUNT_NAME and AZURE_ACCOUNT_KEY:
    # STORAGE
    STATIC_LOCATION = env("STATIC_LOCATION", default="static")
    MEDIA_LOCATION = env("MEDIA_LOCATION", default="media")

    MEDIA_STORAGE_AZURE_ACCOUNT_NAME = env("MEDIA_STORAGE_AZURE_ACCOUNT_NAME", default=AZURE_ACCOUNT_NAME)
    MEDIA_STORAGE_AZURE_ACCOUNT_KEY = env("MEDIA_STORAGE_AZURE_ACCOUNT_KEY", default=AZURE_ACCOUNT_KEY)
    STATIC_STORAGE_AZURE_ACCOUNT_NAME = env("STATIC_STORAGE_AZURE_ACCOUNT_NAME", default=AZURE_ACCOUNT_NAME)
    STATIC_STORAGE_AZURE_ACCOUNT_KEY = env("STATIC_STORAGE_AZURE_ACCOUNT_KEY", default=AZURE_ACCOUNT_KEY)

    AZURE_URL_EXPIRATION_SECS = 10800

    AZURE_STATIC_CUSTOM_DOMAIN = f"{STATIC_STORAGE_AZURE_ACCOUNT_NAME}.blob.core.windows.net"
    AZURE_MEDIA_CUSTOM_DOMAIN = f"{MEDIA_STORAGE_AZURE_ACCOUNT_NAME}.blob.core.windows.net"
    STATIC_URL = f"https://{AZURE_STATIC_CUSTOM_DOMAIN}/{STATIC_LOCATION}/"
    MEDIA_URL = f"https://{AZURE_MEDIA_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/"

    DEFAULT_FILE_STORAGE = "hct_mis_api.apps.core.storage.AzureMediaStorage"
    STATICFILES_STORAGE = "hct_mis_api.apps.core.storage.AzureStaticStorage"
