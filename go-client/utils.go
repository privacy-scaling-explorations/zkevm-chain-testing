package main

import (
	"context"
	"fmt"
	"log"
	"math/big"
	rand "math/rand"
	"os/exec"
	"strconv"
	"strings"

	// crand "crypto/rand"

	ethereum "github.com/ethereum/go-ethereum"

	"zkevmchaintest/fuzz"

	"github.com/ethereum/go-ethereum/accounts"
	"github.com/ethereum/go-ethereum/accounts/keystore"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/common/hexutil"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/ethclient"
)

///////////////////////////////////////////////////////////////////////////
////////////////////// CUSTOM TYPES ///////////////////////////////////////
///////////////////////////////////////////////////////////////////////////

type ctx context.Context

type accs []accounts.Account

type txData struct {
	_to       common.Address
	_nonce    uint64
	_amount   *big.Int
	_gasLimit uint64
	_gasPrice *big.Int
	_data     []byte
}

type balance struct {
	hexaddr     common.Address
	layer1Funds *big.Int
	layer2Funds *big.Int
}

type balances []balance

type SolidityFunctionInputs struct {
	methodName    string
	methSignature string
	receiverAddr  string
	fee           string
	deadline      string
	nonce         string
	calldata      string
}

type Conf_params struct {
	dummy_prover         bool
	mock_prover          bool
	mock_prover_if_error bool
	unsafe_rpc           bool
}

type Flush_params struct {
	cache     bool
	pending   bool
	completed bool
}

///////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////
/////////////////////////// HELPERS ///////////////////////////////////////
///////////////////////////////////////////////////////////////////////////

func ConfigCoordinator(config Conf_params) {

}

func LoadAccounts(ksDir string) (accs, keystore.KeyStore) {
	ks := keystore.NewKeyStore(ksDir, keystore.StandardScryptN, keystore.StandardScryptP)
	return ks.Accounts(), *ks
}

// Calculate accounts' balances on l1 and l2
func GetBalances(ac accs, ec1 ethclient.Client, ec2 ethclient.Client, c ctx) balances {
	_balances := balances{}
	for _, _acc := range ac {
		bal1 := CalculateFunds(ec1, c, _acc.Address)
		bal2 := CalculateFunds(ec2, c, _acc.Address)

		_balance := balance{
			_acc.Address,
			bal1,
			bal2,
		}
		_balances = append(_balances, _balance)
	}
	return _balances
}

// Calcuate account balance in selected layer
func CalculateFunds(ec ethclient.Client, c ctx, accountaddr common.Address) *big.Int {
	bal, _ := ec.BalanceAt(c, accountaddr, nil)
	return bal
}

// Returns common.Address of two randomly selected accounts
func ShuffleAccounts(ac accs, r *rand.Rand) (common.Address, common.Address, int, int) {
	si := r.Intn(len(ac)) // sender's index (from accs slice)
	senderaddr := ac[si].Address
	ri := r.Intn(len(ac)) // receiver's index (from accs slice)
	receiveraddr := ac[ri].Address
	return senderaddr, receiveraddr, si, ri
}

// Calculate the nonce of a given account
func CalcAccNonce(addr common.Address, ec ethclient.Client, c ctx) uint64 {
	nonce, err := ec.NonceAt(c, addr, nil)
	if err != nil {
		fmt.Println(err)
		// log.Fatal(err)
	}
	return nonce
}

// Calculate network-estimated Gas based on total rpc call payload. To be used as GasLimit value
func EstimateGasLimit(saddr common.Address, ec ethclient.Client, data []byte, c ctx) (uint64, int) {
	eg, err := ec.EstimateGas(c, ethereum.CallMsg{
		To:   &saddr,
		Data: data,
	},
	)
	if err != nil {
		fmt.Println(err)
		// log.Fatal(err)
	}
	return eg, len(data)
}

// Calculate network-suggested GasPrice
func EstimateGasPrice(ec ethclient.Client, c ctx) *big.Int {
	egp, err := ec.SuggestGasPrice(c)
	if err != nil {
		fmt.Println(err)
		// log.Fatal(err)
	}
	return egp
}

// Calculate additional Gas due to message payload - maybe not needed due to func EstimateGasLimit
func AddGasLimit(estimatedgl uint64, payloadlength int) uint64 {
	addedgas := uint64(1000) * uint64(payloadlength)
	gl := estimatedgl + addedgas
	return gl
}

// Calculate Tx amount (divide the avaibable funds by cli selected int64)
func CalculateAmount(accbalance *big.Int, balancedivisor int64) *big.Int {
	amount := new(big.Int).Div(accbalance, big.NewInt(balancedivisor))
	return amount
}

// Calaculate total payload length (Tx data + function calldata)
// if ! crosschain, this is a simple l1>l1 or l2>l2 Tx. Therefore fcalldata = []byte{0},
// and txdata = []byte{0}, unless we fuzz the parameter.
// If crosschain, fcalldata is the []byte equivalent to the output of EncodeFunction

// Add this condition in main()

//In case of crosschain tx, toAddr is set to the contract address, otherwise
//set to receiver account address
// Implement this condition in main
func NewTxData(toAddr common.Address, ec ethclient.Client, c ctx, nonce uint64, amount *big.Int, gaslimit uint64, gasprice *big.Int, data []byte) txData {
	return txData{
		toAddr,
		nonce,
		amount,
		gaslimit,
		gasprice,
		data,
	}
}

// func NewTx(newtxdata txData) *types.Transaction {
// 	tx := types.NewTransaction(
// 		newtxdata._nonce,
// 		newtxdata._to,
// 		newtxdata._amount,
// 		newtxdata._gasLimit,
// 		newtxdata._gasPrice,
// 		newtxdata._data,
// 	)
// 	return tx
// }

// func EncodeFunction(methName, methSig, receiver, fee, deadline, nonce, calldata string) string {
// 	jscommand := "node encodeData.js " + methName + " " + methSig + " " + receiver + " " + fee + " " + deadline + " " + nonce + " " + calldata
// 	jsparts := strings.Fields(jscommand)
// 	jsdata, err := exec.Command(jsparts[0], jsparts[1:]...).Output()
// 	if err != nil {
// 		fmt.Println(err)
// 	}

// 	jsoutput := string(jsdata)
// 	return jsoutput
// }

func NewTx(newtxdata txData) *types.Transaction {
	tx := types.NewTransaction(
		newtxdata._nonce,
		newtxdata._to,
		newtxdata._amount,
		newtxdata._gasLimit,
		newtxdata._gasPrice,
		newtxdata._data,
	)
	return tx
}

func InstantiateEthClient(c ctx, testEnv string, strlayer string, tnEnv map[string]string) (*ethclient.Client, *big.Int) {
	ethcl, err := ethclient.Dial(tnEnv[testEnv+"_L"+strlayer])
	if err != nil {
		fmt.Println(err)
		log.Fatal(err)
	}
	chainId, err := ethcl.NetworkID(c)
	if err != nil {
		fmt.Println(err)
		log.Fatal(err)
	}
	return ethcl, chainId
}

func NewSolidityFuncInputs(nonce uint64, receiver common.Address, methName, methSig, fee, deadline, data string) SolidityFunctionInputs {
	inputs := SolidityFunctionInputs{
		methName,
		methSig,
		// common.Bytes2Hex(receiver.Bytes()),
		hexutil.Encode(receiver.Bytes()),
		fee,
		deadline,
		strconv.FormatUint(nonce, 10),
		data,
	}

	return inputs
}

func EncodeFunction(newfuncinputs SolidityFunctionInputs) string {
	jscommand := "node encodeData.js " + newfuncinputs.methodName + " " + newfuncinputs.methSignature + " " + newfuncinputs.receiverAddr + " " + newfuncinputs.fee + " " + newfuncinputs.deadline + " " + newfuncinputs.nonce + " " + newfuncinputs.calldata
	jsparts := strings.Fields(jscommand)
	jsdata, err := exec.Command(jsparts[0], jsparts[1:]...).Output()
	if err != nil {
		fmt.Println(err)
	}

	jsoutput := string(jsdata)
	return jsoutput
}

// Generates a []byte of random/fuzzed size and elements
func NewFuzzedData65535() []byte {
	var ddata []byte
	var myByte byte
	f := fuzz.New()
	// fuzz the slice length
	var sliceCount uint16
	f.Fuzz(&sliceCount)
	fmt.Printf("creating a random []bytes with %v elements\n", sliceCount)
	for ii := 1; ii <= int(sliceCount); ii++ {
		f.Fuzz(&myByte)
		ddata = append(ddata, myByte)
	}

	// fmt.Println(ddata)
	return ddata
}
