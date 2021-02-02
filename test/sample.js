
const Dice2Win = artifacts.require("Dice2Win")
const Web3 = require('web3');
var web3 = new Web3(new Web3.providers.HttpProvider('http://localhost:8545'));
const utils = require('util')
const sp = require('sprintf-js')
var crypto = require('crypto');
const secp256k1 = require('secp256k1')

let diceInst;

contract('dice', (accounts) => {
    beforeEach(async () => {
        // 创建新的合约
        // diceInst = await Dice2Win.new({ from: accounts[0], value:  web3.utils.toWei( '300', 'ether' ) });
        // 部署新的合约
        // diceInst = await Dice2Win.deployed();  // await Dice2Win.new({ from: accounts[0], value:  web3.utils.toWei( '300', 'ether' ) });
        diceInst = await Dice2Win.at("0xd0Cf2D08D6818916d893Fb134AF9425463267EC0");
    });

    it('dicegame', async () => {
       
        console.log("deployed successfully...");
        console.log("accounts[0]", accounts[0]);

        let block = await web3.eth.getBlock("latest");
        console.log(block)
        lastBlock = block.number + 200;

        let buf = crypto.randomBytes(32);
        let reveal = BigInt("0x" + Buffer.from(buf).toString("hex"))
        console.log(reveal)

        console.log("reveal: ", reveal)
        commitLastBlock = sp.sprintf("%010x", lastBlock);
        console.log(commitLastBlock)
        hexReveal = reveal.toString(16) 
        console.log(hexReveal)
        commit = web3.utils.sha3(Buffer.from(hexReveal, "hex"))
        console.log(commit)
        sh3 = web3.utils.soliditySha3({ type: 'uint40', value: lastBlock }, { type: 'bytes32', value: commit });
        console.log(sh3)
        msg = commitLastBlock + commit.replaceAll("0x", "")
        console.log(msg)
        console.log(msg.length)


        pk = Buffer.from("dbbad2a5682517e4ff095f948f721563231282ca4179ae0dfea1c76143ba9607", "hex")

        sig = secp256k1.ecdsaSign(Buffer.from(sh3.replaceAll("0x", ""), 'hex'), pk)
        r = sig.signature.slice(0, 32)
        s = sig.signature.slice(32, 64)
        v = sig.recid + 27

        console.log(Buffer.from(r).toString("hex"))
        console.log(Buffer.from(s).toString("hex"))
        console.log(v)


        let result = await diceInst.placeBet(
            1,
            2,
            lastBlock,
            BigInt(commit),
            Buffer.from(r),
            Buffer.from(s),
            v,
            { 'from': accounts[1], 'value': web3.utils.toWei('2', 'ether'), 'password': '12345678' }
        );

        console.log("result:", result)
        console.log("tx:", result.tx)

        assert.strictEqual(result.receipt.status, true)


        // 开将
        let result2 = await diceInst.settleBet(
            reveal,
            Buffer.from(result.receipt.blockHash.replaceAll("0x", ""), "hex"),
        );

        console.log(result2)

    });
});




