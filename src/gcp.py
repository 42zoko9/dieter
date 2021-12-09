import google.cloud.storage as storage


def store_gcs(
    from_path: str,
    to_path: str,
    bucket_name: str = 'export_from_devices'
) -> None:
    '''from_pathのデータをGCS上の指定したバケットのto_pathへ格納する

    Args:
        from_path (str): 転送元のデータのパス
        to_path (str): 転送先のパス
        bucket_name (str, optional): バケット名. Defaults to 'exported_from_api'.
    '''
    # If you don't specify credentials when constructing the client, the
    # client library will look for credentials in the environment.
    # Error: google.auth.exceptions.DefaultCredentialsError
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(to_path)

    blob.upload_from_filename(from_path)
