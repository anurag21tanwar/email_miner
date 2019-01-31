from lib.vault import Vault
from config.config import vault_conf
import hashlib
from lib.error import *


def fetch_word_cloud(username):
    try:
        vault = Vault.instance(**vault_conf)
        client = vault.client
        res = client.read('kv/usernames/{}'.format(hashlib.sha512(str(username).encode('utf-8')).hexdigest()))
    except:
        raise VaultError('VE')

    try:
        entity_id = res['data']['entity_id']
    except:
        raise VaultUserNotFound('VUNF')

    try:
        res = client.read('kv/words/{}'.format(entity_id))
    except:
        raise VaultUserWordCloudNotAccessible('VUWCNA')

    try:
        word_cloud = res['data']
    except:
        raise VaultUserWordCloudNotFound('VUWCNF')

    return word_cloud
