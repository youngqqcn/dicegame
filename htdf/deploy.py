#coding:utf8
#author: yqq
#date: 2021/2/2 下午3:10
#descriptions:
from binascii import unhexlify

import pytest
import json
import time
from pprint import pprint

from eth_utils import remove_0x_prefix, to_checksum_address
from htdfsdk import HtdfRPC, Address, HtdfPrivateKey, HtdfTxBuilder, HtdfContract, htdf_to_satoshi

import coincurve
from binascii import  hexlify, unhexlify

from coincurve import ecdsa
from eth_hash.auto import keccak
from eth_keys.backends import BaseECCBackend, CoinCurveECCBackend
from eth_keys.datatypes import PrivateKey, Signature

import os



PARAMETERS_INNER = {
    'CHAINID': 'testchain',
    'ADDRESS': 'htdf1xwpsq6yqx0zy6grygy7s395e2646wggufqndml',
    'PRIVATE_KEY': '279bdcd8dccec91f9e079894da33d6888c0f9ef466c0b200921a1bf1ea7d86e8',
    'RPC_HOST': '192.168.0.171',
    'RPC_PORT': 1317,
}

hrc20_contract_address = [
    'htdf1xn5e2m68qs5m827dn5w9amnyzwgex88zhct7q6'
]


def parse_truffe_compile_outputs(json_path: str):
    with open(json_path, 'r') as infile:
        compile_outputs = json.loads(infile.read())
        abi = compile_outputs['abi']
        bytecode = compile_outputs['deployedBytecode']
        bytecode = bytecode.replace('0x', '')
        return abi, bytecode



# @pytest.fixture(scope='module', autouse=True)
def test_create_hrc20_token_contract(conftest_args, bytecode):
    """
    test create hrc20 token contract which implement HRC20.
    # test contract AJC.sol
    """

    gas_wanted = 5000000
    gas_price = 100
    tx_amount = 0
    data = bytecode
    memo = 'test_create_hrc20_token_contract'

    htdfrpc = HtdfRPC(chaid_id=conftest_args['CHAINID'], rpc_host=conftest_args['RPC_HOST'], rpc_port=conftest_args['RPC_PORT'])

    from_addr = Address(conftest_args['ADDRESS'])

    # new_to_addr = HtdfPrivateKey('').address
    private_key = HtdfPrivateKey(conftest_args['PRIVATE_KEY'])
    from_acc = htdfrpc.get_account_info(address=from_addr.address)

    assert from_acc is not None
    assert from_acc.balance_satoshi > gas_price * gas_wanted + tx_amount

    signed_tx = HtdfTxBuilder(
        from_address=from_addr,
        to_address='',
        amount_satoshi=tx_amount,
        sequence=from_acc.sequence,
        account_number=from_acc.account_number,
        chain_id=htdfrpc.chain_id,
        gas_price=gas_price,
        gas_wanted=gas_wanted,
        data=data,
        memo=memo
    ).build_and_sign(private_key=private_key)

    tx_hash = htdfrpc.broadcast_tx(tx_hex=signed_tx)
    print('tx_hash: {}'.format(tx_hash))

    tx = htdfrpc.get_tranaction_until_timeout(transaction_hash=tx_hash)
    pprint(tx)

    assert tx['logs'][0]['success'] == True
    txlog = tx['logs'][0]['log']
    txlog = json.loads(txlog)

    assert tx['gas_wanted'] == str(gas_wanted)
    assert int(tx['gas_used']) <= gas_wanted

    tv = tx['tx']['value']
    assert len(tv['msg']) == 1
    assert tv['msg'][0]['type'] == 'htdfservice/send'
    assert int(tv['fee']['gas_wanted']) == gas_wanted
    assert int(tv['fee']['gas_price']) == gas_price
    assert tv['memo'] == memo

    mv = tv['msg'][0]['value']
    assert mv['From'] == from_addr.address
    assert mv['To'] == ''  # new_to_addr.address
    assert mv['Data'] == data
    assert int(mv['GasPrice']) == gas_price
    assert int(mv['GasWanted']) == gas_wanted
    assert 'satoshi' == mv['Amount'][0]['denom']
    assert tx_amount == int(mv['Amount'][0]['amount'])

    pprint(tx)

    time.sleep(8)  # wait for chain state update

    # to_acc = htdfrpc.get_account_info(address=new_to_addr.address)
    # assert to_acc is not None
    # assert to_acc.balance_satoshi == tx_amount

    from_acc_new = htdfrpc.get_account_info(address=from_addr.address)
    assert from_acc_new.address == from_acc.address
    assert from_acc_new.sequence == from_acc.sequence + 1
    assert from_acc_new.account_number == from_acc.account_number
    assert from_acc_new.balance_satoshi == from_acc.balance_satoshi - (gas_price * int(tx['gas_used']))

    logjson = json.loads(tx['logs'][0]['log'])
    contract_address = logjson['contract_address']

    hrc20_contract_address.append(contract_address)

    pass




def test_normal_tx_send(conftest_args, to_addr):
    gas_wanted = 30000
    gas_price = 100
    tx_amount = 101 * 10**8
    data = ''
    memo = 'test_normal_transaction'

    htdfrpc = HtdfRPC(chaid_id=conftest_args['CHAINID'], rpc_host=conftest_args['RPC_HOST'], rpc_port=conftest_args['RPC_PORT'])

    from_addr = Address(conftest_args['ADDRESS'])

    # new_to_addr = HtdfPrivateKey('').address
    private_key = HtdfPrivateKey(conftest_args['PRIVATE_KEY'])
    from_acc = htdfrpc.get_account_info(address=from_addr.address)

    assert from_acc is not None
    assert from_acc.balance_satoshi > gas_price * gas_wanted + tx_amount

    signed_tx = HtdfTxBuilder(
        from_address=from_addr,
        to_address=to_addr,
        amount_satoshi=tx_amount,
        sequence=from_acc.sequence,
        account_number=from_acc.account_number,
        chain_id=htdfrpc.chain_id,
        gas_price=gas_price,
        gas_wanted=gas_wanted,
        data=data,
        memo=memo
    ).build_and_sign(private_key=private_key)

    tx_hash = htdfrpc.broadcast_tx(tx_hex=signed_tx)
    print('tx_hash: {}'.format(tx_hash))

    mempool = htdfrpc.get_mempool_trasactions()
    pprint(mempool)

    memtx = htdfrpc.get_mempool_transaction(transaction_hash=tx_hash)
    pprint(memtx)

    tx = htdfrpc.get_tranaction_until_timeout(transaction_hash=tx_hash)
    pprint(tx)

    tx = htdfrpc.get_transaction(transaction_hash=tx_hash)
    assert tx['logs'][0]['success'] == True
    assert tx['gas_wanted'] == str(gas_wanted)
    assert tx['gas_used'] == str(gas_wanted)

    tv = tx['tx']['value']
    assert len(tv['msg']) == 1
    assert tv['msg'][0]['type'] == 'htdfservice/send'
    assert int(tv['fee']['gas_wanted']) == gas_wanted
    assert int(tv['fee']['gas_price']) == gas_price
    assert tv['memo'] == memo

    mv = tv['msg'][0]['value']
    assert mv['From'] == from_addr.address
    assert mv['To'] == to_addr
    assert mv['Data'] == data
    assert int(mv['GasPrice']) == gas_price
    assert int(mv['GasWanted']) == gas_wanted
    assert 'satoshi' == mv['Amount'][0]['denom']
    assert tx_amount == int(mv['Amount'][0]['amount'])

    pprint(tx)

    # time.sleep(8)  # wait for chain state update

    # to_acc = htdfrpc.get_account_info(address=to_addr)
    # assert to_acc is not None
    # assert to_acc.balance_satoshi == tx_amount
    #
    # from_acc_new = htdfrpc.get_account_info(address=from_addr.address)
    # assert from_acc_new.address == from_acc.address
    # assert from_acc_new.sequence == from_acc.sequence + 1
    # assert from_acc_new.account_number == from_acc.account_number
    # assert from_acc_new.balance_satoshi == from_acc.balance_satoshi - (gas_price * gas_wanted + tx_amount)




def test_hrc20_transfer(conftest_args, abi):
    assert len(hrc20_contract_address) > 0
    contract_address = Address(hrc20_contract_address[0])
    htdfrpc = HtdfRPC(chaid_id=conftest_args['CHAINID'], rpc_host=conftest_args['RPC_HOST'], rpc_port=conftest_args['RPC_PORT'])

    hc = HtdfContract(rpc=htdfrpc, address=contract_address, abi=abi)

    new_to_addr = HtdfPrivateKey('').address

    from_addr = Address(conftest_args['ADDRESS'])
    private_key = HtdfPrivateKey(conftest_args['PRIVATE_KEY'])
    from_acc = htdfrpc.get_account_info(address=from_addr.address)

    ####################
    blk = htdfrpc.get_latest_block()
    last_block_number = int(blk['block_meta']['header']['height'])

    reveal = int(os.urandom(32).hex(), 16)
    commitLastBlock = unhexlify('%010x' % last_block_number)  # 和uint40对应
    commit = keccak(  unhexlify('%064x' % reveal) )
    print('0x' + commit.hex() )

    privateKey = unhexlify('dbbad2a5682517e4ff095f948f721563231282ca4179ae0dfea1c76143ba9607')

    pk = PrivateKey(privateKey, CoinCurveECCBackend)
    sig = pk.sign_msg(message=commitLastBlock + commit)

    print('"0x' +  sig.to_bytes()[:32].hex() + '"')
    print('"0x'+ sig.to_bytes()[32:-1].hex() + '"')
    print( sig.to_bytes()[-1])
    r = sig.to_bytes()[:32]
    s = sig.to_bytes()[32:-1]
    v = sig.to_bytes()[-1] + 27
    ######################

    placeBetTx =hc.functions.placeBet(
        betMask = 1,
        modulo = 2, 
        commitLastBlock = last_block_number,
        commit = int(commit.hex(), 16),
        r = r,
        s = s,
        v = v,
    ).buildTransaction_htdf()

    data = remove_0x_prefix(placeBetTx['data'])
    signed_tx = HtdfTxBuilder(
        from_address=from_addr,
        to_address=contract_address,
        amount_satoshi=0,
        sequence=from_acc.sequence,
        account_number=from_acc.account_number,
        chain_id=htdfrpc.chain_id,
        gas_price=100,
        gas_wanted=5000000,
        data=data,
        memo='test_hrc20_transfer'
    ).build_and_sign(private_key=private_key)

    tx_hash = htdfrpc.broadcast_tx(tx_hex=signed_tx)
    print('tx_hash: {}'.format(tx_hash))

    tx = htdfrpc.get_tranaction_until_timeout(transaction_hash=tx_hash)
    pprint(tx)

    pass



def test_get_croupier(conftest_args, abi):
    assert len(hrc20_contract_address) > 0
    contract_address = Address(hrc20_contract_address[0])
    htdfrpc = HtdfRPC(chaid_id=conftest_args['CHAINID'], rpc_host=conftest_args['RPC_HOST'],
                      rpc_port=conftest_args['RPC_PORT'])

    hc = HtdfContract(rpc=htdfrpc, address=contract_address, abi=abi)

    # from_addr = Address(conftest_args['ADDRESS'])
    # private_key = HtdfPrivateKey(conftest_args['PRIVATE_KEY'])
    # from_acc = htdfrpc.get_account_info(address=from_addr.address)

    croupier = hc.call(hc.functions.croupier())
    print(croupier)

    pass



def main():
    abi, bytecode = parse_truffe_compile_outputs('../build/contracts/Dice2Win.json')
    # test_create_hrc20_token_contract(conftest_args=PARAMETERS_INNER, bytecode=bytecode)

    # time.sleep(15)
    # test_normal_tx_send(conftest_args=PARAMETERS_INNER, to_addr=hrc20_contract_address[0])

    # time.sleep(15)

    test_get_croupier(conftest_args=PARAMETERS_INNER, abi=abi)

    # test_hrc20_transfer(conftest_args=PARAMETERS_INNER, abi=abi)

    pass


if __name__ == '__main__':
    main()
    pass



# 227ada37
# 0000000000000000000000000000000000000000000000000000000000000001
# 0000000000000000000000000000000000000000000000000000000000000002
# 00000000000000000000000000000000000000000000000000000000000622ec
# 92ff1287a7b7324c63a3a21ca8602c2ebcdd47a6e9cf9341954a16810b61a720
# 56070c680fbdd47404cb99523e02696d08a0a15d1bc99d85c9767dd979c53318
# 7c5524c9bb16c12d895c7c75591929d3f4d53634781b142fa5fa265c2b88c5aa
# 0000000000000000000000000000000000000000000000000000000000000000



# 227ada37
# 0000000000000000000000000000000000000000000000000000000000000001
# 0000000000000000000000000000000000000000000000000000000000000002
# 00000000000000000000000000000000000000000000000000000000000000d9
# 7446a3658e60397521ac00c4ad4c1dd4c86a6b8deda35062356e6633ac3bbdfc
# ff5426c5120990e3cceed9e5a63c03fe83960576fc2b26c884b57e33b3a2d9f3
# 63e513cee6287a2d849bceae90607be8c941dfc66ef2bd990a3c4a37a4f60a66
# 000000000000000000000000000000000000000000000000000000000000001b