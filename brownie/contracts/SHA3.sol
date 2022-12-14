// SPDX-License-Identifier: MIT
 
pragma solidity 0.8.17;
 
contract CheckKeccak {
 
    function checkBatchYul(uint256 l) external  returns (bytes32 r) {
        uint256 len = l / 28;

        for (uint256 i; i<len; i++) {
            r = keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(keccak256(abi.encodePacked(bytes1(r)))))))))))))))))))))))))))))))))))))))))))))))))))))))));
        }
    }
}