all:compile migrate

#truffle compile
compile:clean
	node --stack-size=1200  /usr/local/node-v15.6.0-linux-x64/lib/node_modules/truffle/build/cli.bundled.js compile

#truffle migrate
migrate:
	node --stack-size=1200  /usr/local/node-v15.6.0-linux-x64/lib/node_modules/truffle/build/cli.bundled.js  migrate  --reset --network development --f 1

geth:
	geth --datadir /data/gethdata/  --ipcpath /data/gethdata/geth.ipc --rpc --rpccorsdomain="http://localhost:8080" --rpcapi web3,eth,debug,personal,net --vmdebug    --rpcport "8545" --rpcaddr "0.0.0.0"    --nodiscover  --dev

attach:
	geth attach ipc:/data/gethdata/geth.ipc

clean:
	- rm -rf build
	- rm -rf ./contract/artifacts


remixd:
	remixd -s /data/work/dicegame  --remix-ide http://localhost:8080