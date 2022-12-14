const { ethers } = require("ethers");

let methName = process.argv[2]
let methSig = process.argv.slice(3,-5).join(" ")
let receiver = process.argv[process.argv.length - 5]
let fee = process.argv[process.argv.length - 4]
let deadline = process.argv[process.argv.length - 3]
let nonce = process.argv[process.argv.length - 2]
let data = process.argv[process.argv.length - 1]

const abi = new ethers.utils.Interface(
    [
      methSig
    ]
  );

let input = abi.encodeFunctionData(methName, [receiver, fee, deadline, nonce, data]);
// to l1 bridge
// tx = { to: '0x936a70c0b28532aa22240dce21f89a8399d6ac60', value, data }
console.log(input)