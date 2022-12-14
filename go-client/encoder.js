const { ethers } = require("ethers");


const abi = new ethers.utils.Interface(
    [
      "function submitBlock(bytes calldata _data) external"      
    ]
  );

let input = abi.encodeFunctionData("0");
// to l1 bridge
// tx = { to: '0x936a70c0b28532aa22240dce21f89a8399d6ac60', value, data }
console.log(input)