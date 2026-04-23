from des_socket_utils import encrypt_des_cbc, build_packet


def test_protocol_contract_order_is_key_iv_length_ciphertext():
    key, iv, cipher_bytes = encrypt_des_cbc(b"FIT4012 contract test", key=b"12345678", iv=b"abcdefgh")
    packet = build_packet(key, iv, cipher_bytes)
    assert packet[:8] == key
    assert packet[8:16] == iv
    assert len(packet[20:]) == len(cipher_bytes)
    assert len(cipher_bytes) % 8 == 0
