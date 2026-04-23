from des_socket_utils import encrypt_des_cbc, decrypt_des_cbc


def test_tampered_ciphertext_should_fail_or_change_plaintext():
    plain = b"Thong diep dung de test tamper"
    key, iv, cipher_bytes = encrypt_des_cbc(plain, key=b"12345678", iv=b"abcdefgh")
    tampered = bytearray(cipher_bytes)
    tampered[-1] ^= 0x01

    try:
        recovered = decrypt_des_cbc(key, iv, bytes(tampered))
        assert recovered != plain
    except ValueError:
        assert True
