// SPDX-License-Identifier: MIT
 
pragma solidity =0.8.19;
 
contract CheckExtCodeSize100 {
    // event TestEvent(address addr);

    function checkBatchYul(address[] calldata addresses) external returns (uint256 length) {
        uint256 ptr = 68;
        uint256 len = addresses.length/100;
        uint8 inc = 32;
        for (uint256 i=0; i<len; i++) {
            assembly {
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))
                ptr := add(ptr, inc)
                length := extcodesize(calldataload(ptr))       
                ptr := add(ptr, inc)                                                                                                                        
            }
        }
        return length;
    }
}