import pytest
from des_socket_utils import encrypt_des_cbc, decrypt_des_cbc


def test_wrong_key_should_not_recover_original_plaintext():
    plain = b"Thong diep dung de test wrong key"
    key, iv, cipher_bytes = encrypt_des_cbc(plain, key=b"12345678", iv=b"abcdefgh")
    wrong_key = b"87654321"

    try:
        recovered = decrypt_des_cbc(wrong_key, iv, cipher_bytes)
        assert recovered != plain
    except ValueError:
        assert True
