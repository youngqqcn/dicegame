const Dice2Win = artifacts.require("Dice2Win")
const Web3 = require('web3');
var web3 = new Web3(new Web3.providers.HttpProvider('http://localhost:8545'));

module.exports = function(deployer) {
    deployer.deploy(Dice2Win, {value:  web3.utils.toWei( '300', 'ether' )})
};
