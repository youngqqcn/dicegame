module.exports = {
    // Uncommenting the defaults below
    // provides for an easier quick-start with Ganache.
    // You can also follow this format for other networks;
    // see <http://truffleframework.com/docs/advanced/configuration>
    // for more details on how to specify configuration options!
    //
    networks: {
        development: {
            host: "127.0.0.1",
            port: 8545,
            network_id: "*",
            BlockLimit: 0x7691b7  ,
            // gas: 0xfffffffffff,
            gas: 0
        }
        // test: {
        //   host: "127.0.0.1",
        //   port: 7545,
        //   network_id: "*"
        // }
    },
    compilers:{
        solc: {
            version: "0.8.0",
            parser: "solcjs",
            // optimizer: {
            //     enabled: true,
            //     runs: 200
            // },
            settings: {
                optimizer: {
                    enabled: true,
                    runs: 20  // Optimize for how many times you intend to run the code
                }
            },
        }
    }
};
