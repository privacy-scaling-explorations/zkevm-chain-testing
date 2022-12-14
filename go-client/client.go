package main

import (
	// "os"

	"bytes"
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"math/big"
	rand "math/rand"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/common/hexutil"
	"github.com/joho/godotenv"
)

// type conf_params struct {
// 	dummy_prover bool
// }

var showBalances bool
var tnEnv map[string]string
var zeros []*big.Int
var doTxs bool
var layer int
var testEnv string
var TxCount int
var crosschain bool
var balanceDivisor int64
var methodName string
var testFuzz bool
var TxSleep string
var debug bool
var config bool
var node string
var blocknumber int64
var dummy_prover bool
var mock_prover bool
var mock_prover_if_error bool
var unsafe_rpc bool
var flush bool

// var dbgresponse map[string]interface{}
var pjson bytes.Buffer

/////////////////////////////////////////////////////////////
// Declare variables to broaden scope outside of conditionals
/////////////////////////////////////////////////////////////
var txdata []byte
var fdata []byte
var toAddr common.Address
var ctrMethods map[string]string
var bridgeaddress common.Address
var abiencoding string
var internalCallData string

// var config_params conf_params

func init() {
	flag.BoolVar(&flush, "flush", false, "flush prover tasks")
	flag.BoolVar(&unsafe_rpc, "unsafe_rpc", false, "enable unsafe methods")
	flag.BoolVar(&dummy_prover, "dummy_prover", true, "enable/disable proof_request")
	flag.BoolVar(&mock_prover_if_error, "mock_prover_if_error", true, "engage mock prover on proof failure")
	flag.BoolVar(&mock_prover, "mock_prover", true, "enable/disable mock_prover")
	flag.Int64Var(&blocknumber, "blocknumber", 1, "block to debug")
	flag.BoolVar(&debug, "debug", false, "collect Tx trace for a given block")
	flag.BoolVar(&config, "config", false, "provide config params to coordinator via json-rpc call")
	flag.StringVar(&node, "node", "coordinator", "")
	flag.StringVar(&TxSleep, "TxSleep", "1s", "select number of seconds to pause inbetween Txs || example: -TxSleep='3s'")
	// flag.StringVar(&TxSleep, "TxSleep", "1s", "select number of seconds to pause inbetween Txs || example: -TxSleep='3s'")
	flag.BoolVar(&testFuzz, "testFuzz", false, "boolean, if set, script will calculate and display account balances in l1 and l2")
	flag.BoolVar(&showBalances, "showBalances", false, "boolean")
	flag.BoolVar(&doTxs, "doTxs", false, "boolean, if set, script will run simple Txs on selected layer, until exited")
	flag.IntVar(&layer, "layer", 0, "select layer, must be 1 or 2 - only relevant when doTxs is TRUE")
	flag.StringVar(&testEnv, "testEnv", "TESTNET", "select environment as test target")
	flag.IntVar(&TxCount, "TxCount", 1, "select number of Txs to execute")
	flag.Int64Var(&balanceDivisor, "balanceDivisor", 1000000, "int64, amount to transfer equals balance/balanceDivisor")
	flag.BoolVar(&crosschain, "crosschain", false, "boolean, indicates id this is a crosschain operation, ie deposit (layer=1) or withdraw (layer=2)")
	flag.StringVar(&methodName, "methodName", "", "select target solidity method, mandatory if crosschain is set")
}

func main() {
	flag.Parse()
	TxSl, _ := time.ParseDuration(TxSleep)

	if doTxs && layer != 1 && layer != 2 {
		fmt.Println("Invalid cli inputs. Must set layer to 1 or 2")
		os.Exit(1)
	}

	if crosschain && methodName == "" {
		fmt.Println("Invalid cli inputs. Must set methodName for crosschain operation")
		os.Exit(1)
	}

	strlayer := strconv.Itoa(layer)
	tnEnv, err := godotenv.Read()
	if err != nil {
		fmt.Println(err)
		log.Fatal(err)
	}

	ksdir := tnEnv["KEYSTORE"]
	passw0rd := tnEnv["PASSWORD"]

	_accounts, ks := LoadAccounts(ksdir)
	_ctx := context.Background()

	for _, account := range _accounts {
		ks.Unlock(account, passw0rd)
	}

	if crosschain {
		// lOnebridge := tnEnv["L1BRIDGEADDR"]
		// lTwobridge := tnEnv["L2BRIDGEADDR"]

		ctrMethods, err = godotenv.Read(".solidityMethods")
		if err != nil {
			fmt.Println(err)
			log.Fatal(err)
		}

	}

	if flush {
		// rpcUrl := tnEnv[fmt.Sprintf("%v_L%v", testEnv, strlayer)]
		rpcUrl := tnEnv[fmt.Sprintf("%v_%v", testEnv, node)]
		fmt.Println(rpcUrl)
		// config_params := conf_params{dummy_prover}
		// config_params := fmt.Sprint(params)
		flush_params := Flush_params{true, true, true}
		// [{dummy_prover:true}]
		data := fmt.Sprintf(`{"jsonrpc":"2.0","id": 1, "method": "flush", "params": [{"cache":%v,"pending":%v,"completed":%v}]}`, flush_params.cache, flush_params.pending, flush_params.completed)
		fmt.Println(data)
		jsonData := []byte(data)
		dReader := bytes.NewReader(jsonData)
		req, err := http.NewRequest("POST", rpcUrl, dReader)
		if err != nil {
			fmt.Printf("client: could not create request: %s\n", err)
			os.Exit(1)
		}

		res, err := http.DefaultClient.Do(req)
		if err != nil {
			fmt.Printf("client: error making http request: %s\n", err)
			os.Exit(1)
		}

		fmt.Printf("client: status code: %d\n", res.StatusCode)

		resBody, err := ioutil.ReadAll(res.Body)
		if err != nil {
			fmt.Printf("client: could not read response body: %s\n", err)
			os.Exit(1)
		}

		_ = json.Indent(&pjson, resBody, "", "    ")

		// fmt.Println(pjson.String())
		// _ = json.Unmarshal(resBody, &dbgresponse)

		fileName := fmt.Sprintf("flush_response.json")
		jsonFile, err := os.Create(fileName)

		if err != nil {
			panic(err)
		}
		defer jsonFile.Close()

		jsonFile.Write([]byte(pjson.String()))
		jsonFile.Close()

	}

	if config {
		fmt.Println(mock_prover)
		// rpcUrl := tnEnv[fmt.Sprintf("%v_L%v", testEnv, strlayer)]
		rpcUrl := tnEnv[fmt.Sprintf("%v_%v", testEnv, node)]
		fmt.Println(rpcUrl)
		// config_params := conf_params{dummy_prover}
		// config_params := fmt.Sprint(params)
		fmt.Println(dummy_prover)
		config_params := Conf_params{
			dummy_prover,
			mock_prover,
			mock_prover_if_error,
			unsafe_rpc,
		}
		// [{dummy_prover:true}]
		// var mock_prover_if_error bool
		data := fmt.Sprintf(`{"jsonrpc":"2.0","id": 1, "method": "config", "params": [{"dummy_prover":%v,"mock_prover":%v,"mock_prover_if_error":%v,"unsafe_rpc":%v}]}`, config_params.dummy_prover, config_params.mock_prover, config_params.mock_prover_if_error, config_params.unsafe_rpc)
		fmt.Println(data)
		jsonData := []byte(data)
		dReader := bytes.NewReader(jsonData)
		req, err := http.NewRequest("POST", rpcUrl, dReader)
		if err != nil {
			fmt.Printf("client: could not create request: %s\n", err)
			os.Exit(1)
		}

		res, err := http.DefaultClient.Do(req)
		if err != nil {
			fmt.Printf("client: error making http request: %s\n", err)
			os.Exit(1)
		}

		fmt.Printf("client: status code: %d\n", res.StatusCode)

		resBody, err := ioutil.ReadAll(res.Body)
		if err != nil {
			fmt.Printf("client: could not read response body: %s\n", err)
			os.Exit(1)
		}

		_ = json.Indent(&pjson, resBody, "", "    ")

		// fmt.Println(pjson.String())
		// _ = json.Unmarshal(resBody, &dbgresponse)

		fileName := fmt.Sprintf("Coordinator_Config.json")
		jsonFile, err := os.Create(fileName)

		if err != nil {
			panic(err)
		}
		defer jsonFile.Close()

		jsonFile.Write([]byte(pjson.String()))
		jsonFile.Close()

	}

	if debug {
		// fmt.Printf("Must provide block number, environment name and layer, block=%v\n", blocknumber)
		ethcl, _ := InstantiateEthClient(_ctx, testEnv, strlayer, tnEnv)
		rpcUrl := tnEnv[fmt.Sprintf("%v_L%v", testEnv, strlayer)]
		block, err := ethcl.BlockByNumber(context.Background(), big.NewInt(blocknumber))
		if err != nil {
			log.Fatal(err)
		}

		transacts := block.Transactions()
		for i := 0; i < transacts.Len(); i++ {
			hash := transacts[i].Hash()
			hash2string := hash.Hex()
			data := fmt.Sprintf(`{"id": 1, "method": "debug_traceTransaction", "params": ["%v"]}`, hash2string)
			jsonData := []byte(data)
			dReader := bytes.NewReader(jsonData)
			req, err := http.NewRequest("POST", rpcUrl, dReader)
			if err != nil {
				fmt.Printf("client: could not create request: %s\n", err)
				os.Exit(1)
			}

			res, err := http.DefaultClient.Do(req)
			if err != nil {
				fmt.Printf("client: error making http request: %s\n", err)
				os.Exit(1)
			}

			fmt.Printf("client: status code: %d\n", res.StatusCode)

			resBody, err := ioutil.ReadAll(res.Body)
			if err != nil {
				fmt.Printf("client: could not read response body: %s\n", err)
				os.Exit(1)
			}

			_ = json.Indent(&pjson, resBody, "", "    ")

			// fmt.Println(pjson.String())
			// _ = json.Unmarshal(resBody, &dbgresponse)

			// fmt.Println(dbgresponse)

			fileName := fmt.Sprintf("Layer_%v_Block_%v_%v.json", strlayer, blocknumber, hash2string)
			jsonFile, err := os.Create(fileName)

			if err != nil {
				panic(err)
			}
			defer jsonFile.Close()

			jsonFile.Write([]byte(pjson.String()))
			jsonFile.Close()

		}

	}

	if showBalances {
		fmt.Println("INSTANTIATING")
		ethcl1, _ := InstantiateEthClient(_ctx, testEnv, "1", tnEnv)
		ethcl2, _ := InstantiateEthClient(_ctx, testEnv, "2", tnEnv)
		bal := GetBalances(_accounts, *ethcl1, *ethcl2, _ctx)
		for _, b := range bal {
			fmt.Printf("account %x has %v funds in l2 and %v funds in l1\n", b.hexaddr, b.layer2Funds, b.layer1Funds)

		}
	}

	if doTxs {
		source := rand.NewSource(time.Now().UnixNano())
		r := rand.New(source)
		ethcl, chainid := InstantiateEthClient(_ctx, testEnv, strlayer, tnEnv)
		for ii := 1; ii <= TxCount; ii++ {
			senderaddr, receiveraddr, si, _ := ShuffleAccounts(_accounts, r)
			nonce := CalcAccNonce(senderaddr, *ethcl, _ctx)
			if crosschain {
				bridgeaddress = common.HexToAddress(tnEnv["L"+strlayer+"BRIDGEADDR"])
				toAddr = bridgeaddress
				// fdatastring := EncodeFunction(
				// 	methodName,
				// 	ctrMethods[methodName],
				// 	common.Bytes2Hex(receiveraddr.Bytes()),
				// 	"0",
				// 	"0xffffffffffffffff",
				// 	strconv.FormatUint(nonce, 10),
				// 	"0x",
				// )
				if testFuzz {
					internalCallDataBytes := NewFuzzedData65535()
					internalCallData = hexutil.Encode(internalCallDataBytes)
				} else {
					internalCallData = "0x"
				}
				newfuncinputs := NewSolidityFuncInputs(
					nonce,
					receiveraddr,
					methodName,
					ctrMethods[methodName],
					"0",
					"0xffffffffffffffff",
					internalCallData,
				)

				abiencoding := EncodeFunction(newfuncinputs)
				abiencodingbytes, _ := hexutil.Decode(abiencoding)
				fdata = abiencodingbytes
				txdata = fdata

			} else {
				toAddr = receiveraddr
				txdata = []byte{0}
				fdata = []byte{0}
			}

			payload := txdata

			// toAddr = common.HexToAddress("a499d680c1854e15fd009cc8c84b68f545e46d34")
			amount := CalculateAmount(CalculateFunds(*ethcl, _ctx, senderaddr), balanceDivisor)
			gaslimit, payloadLength := EstimateGasLimit(senderaddr, *ethcl, payload, _ctx)
			gasprice := EstimateGasPrice(*ethcl, _ctx)

			gasLimitADjusted := AddGasLimit(gaslimit, payloadLength)
			fmt.Printf("a: %v\n", gasLimitADjusted)
			gasLimitADjustedUsed := uint64(1000000)
			// fmt.Printf("a: %v\n", gasLimitADjustedUsed)
			newtxdata := NewTxData(toAddr, *ethcl, _ctx, nonce, amount, gasLimitADjustedUsed, gasprice, txdata)
			tx := NewTx(newtxdata)
			signedTx, err := ks.SignTxWithPassphrase(_accounts[si], passw0rd, tx, chainid)
			fmt.Printf("TxHash: %v\n", signedTx.Hash())
			if err != nil {
				fmt.Println(err)
				// log.Fatal(err)
			}

			err = ethcl.SendTransaction(_ctx, signedTx)
			if err != nil {
				fmt.Println(err)
				// log.Fatal(err)
			}

			time.Sleep(TxSl)
		}

	}

}
