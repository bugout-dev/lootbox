// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.0;

/**
 * Authors: Moonstream Engineering (engineering - at - moonstream.to)
 * GitHub: https://github.com/moonstream-to/web3
 */

// Interface ID: 458bb0c0
//
// Calculated by solface: https://github.com/moonstream-to/solface
// solface version: 0.1.0
//
// To recalculate from root directory of this repo:
// $ jq .abi build/contracts/IStatBlock.json  | solface -name IStatBlock -annotations | grep "Interface ID:"
interface IStatBlock {
    event StatCreated(uint256 statID, string descriptor);
    event StatAssigned(
        address indexed tokenAddress,
        uint256 indexed tokenID,
        uint256 indexed statID,
        uint256 value
    );

    function isAdministrator(address account) external view returns (bool);

    function createStat(string memory descriptor) external returns (uint256);

    function describeStat(uint256) external view returns (string memory);

    function assignStats(
        address tokenAddress,
        uint256 tokenID,
        uint256[] memory statIDs,
        uint256[] memory values
    ) external;

    function batchAssignStats(
        address[] memory tokenAddresses,
        uint256[] memory tokenIDs,
        uint256[][] memory statIDs,
        uint256[][] memory values
    ) external;

    function getStats(
        address tokenAddress,
        uint256 tokenID,
        uint256[] memory statIDs
    ) external view returns (uint256[] memory);

    function batchGetStats(
        address[] memory tokenAddresses,
        uint256[] memory tokenIDs,
        uint256[] memory statIDs
    ) external view returns (uint256[][] memory);
}
