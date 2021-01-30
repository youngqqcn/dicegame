#coding:utf8
#author: yqq
#date: 2021/1/29 上午11:49
#descriptions:

import hashlib
import coincurve
from binascii import  hexlify, unhexlify

from coincurve import ecdsa
from eth_hash.auto import keccak
from eth_keys.backends import BaseECCBackend, CoinCurveECCBackend
from eth_keys.datatypes import PrivateKey, Signature

#
# def safe_ord(value):
#     if isinstance(value, int):
#         return value
#     else:
#         return ord(value)
#
# def ecsign(rawhash, key):
#     if coincurve and hasattr(coincurve, 'PrivateKey'):
#         pk = coincurve.PrivateKey(key)
#         signature = pk.sign_recoverable(rawhash, hasher=None)
#         v = safe_ord(signature[64]) + 27
#         r = signature[0:32]
#         s = signature[32:64]
#         return r, s, v, signature

def new_sign(privkey, msg_hash):
    pk =  PrivateKey(privkey, CoinCurveECCBackend)
    sig = pk.sign_msg_hash(msg_hash)
    return sig


TT256 = 2 ** 256
TT256M1 = 2 ** 256 - 1
TT255 = 2 ** 255
SECP256K1P = 2**256 - 4294968273


def ecrecover_to_pub(sig, rawhash):
    pk =  coincurve.PublicKey.from_signature_and_message(serialized_sig=sig, message=rawhash)
    # print(pk.format().hex())
    r_sig = ecdsa.deserialize_recoverable(sig)
    n_sig = ecdsa.recoverable_convert(r_sig)
    der = ecdsa.cdata_to_der(n_sig)
    assert pk.verify(der, rawhash)
    x, y = pk.point()
    print('======')
    print(hex(x))
    print(hex(y))
    print('======')
    # return pk.format(compressed=False)[1:]
    return unhexlify( "%064x%064x" % (x, y) )



def pubkey_to_eth_address( pubKey):
    return keccak(pubKey)[-20:].hex()

def test_sign():

    # 对应智能合约  keccak256(abi.encodePacked(uint40(commitLastBlock), commit));
    commitLastBlock = unhexlify( '%010x' % 0xb34464 ) # 和uint40对应
    commit = unhexlify( '24027f1fe6692863385b95ab253f0700a35d03a8967dff8588e2de6b066b44e4' )

    h = keccak( commitLastBlock + commit )
    print(hexlify(h))

    #正确keccak结果, 正确是: A5CA2F7474A762F6EA97585911E0CC48FB1282D53A0A602056B61216AF7637FD
    sig = '2e608766579a55fffd6d7872e89d56642980358160b877fdb00855e716a8cbeb'
    sig += '3faac77026378c125f5ead4bb0cbf303554ba85d9920d158a9aacecfa2ada6a8'
    sig += '00' # 27
    sig = unhexlify(sig)

    sg = Signature(sig)
    pubk = sg.recover_public_key_from_msg_hash(h)
    print(pubk.to_checksum_address())  # 正确的应是 0xb00b5ca7ec0502f2f269e99b91ebbccbce9cccec

    pass



def test_playbet():
    lastBlock = 166
    reveal = 20
    commitLastBlock = unhexlify('%010x' % lastBlock)  # 和uint40对应
    commit = keccak(  unhexlify('%064x' % reveal) )
    print('0x' + commit.hex() )

    privateKey = unhexlify('dbbad2a5682517e4ff095f948f721563231282ca4179ae0dfea1c76143ba9607')
    # r, s, v, sig = ecsign(h, privateKey)
    # sig = new_sign(privkey=privateKey, msg_hash=h)

    pk = PrivateKey(privateKey, CoinCurveECCBackend)
    sig = pk.sign_msg(message=commitLastBlock + commit)
    # return sig

    print('"0x' +  sig.to_bytes()[:32].hex() + '"')
    print('"0x'+ sig.to_bytes()[32:-1].hex() + '"')
    print( sig.to_bytes()[-1])

    pass


def main():
    test_playbet()
    # test_sign()
    pass


if __name__ == '__main__':
    main()
    pass
