def decode_id_string(id_string):
    if not id_string:
        return

    from base64 import b64decode

    return b64decode(id_string).decode().split(":")[1]
