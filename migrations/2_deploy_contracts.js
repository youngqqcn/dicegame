// const ConvertLib = artifacts.require("ConvertLib");
const Dice2Win = artifacts.require("Dice2Win")

module.exports = function(deployer) {
  // deployer.deploy(ConvertLib);
  // deployer.link(ConvertLib, MetaCoin);
  // deployer.deploy(MetaCoin);
    deployer.deploy(Dice2Win)
};
