// 'use strict';

const path = require("path");
const fs = require("fs");
const solc = require("solc");

const srcpath = path.resolve(__dirname, "contracts", "dice.sol");
// console.log(srcpath);


const source = fs.readFileSync(srcpath, 'utf-8');
// console.log(source);

const result =  solc.compile(source, 1);
console.log(result);

module.exports = result.contracts[':Dice2Win'];   //导出编译结果, 部署合约时需要用到