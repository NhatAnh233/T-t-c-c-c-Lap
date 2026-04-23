from des_socket_utils import pad, unpad, encrypt_des_cbc, build_packet, parse_header


def test_pad_unpad_roundtrip():
    data = b"hello DES socket"
    assert unpad(pad(data)) == data


def test_build_packet_contains_correct_length():
    key, iv, cipher_bytes = encrypt_des_cbc(b"FIT4012")
    packet = build_packet(key, iv, cipher_bytes)
    header = packet[:20]
    k2, iv2, length = parse_header(header)
    assert k2 == key
    assert iv2 == iv
    assert length == len(cipher_bytes)
    assert packet[20:] == cipher_bytes
