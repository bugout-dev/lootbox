// SPDX-License-Identifier: Apache-2.0

/**
 * Authors: Moonstream Engineering (engineering@moonstream.to)
 * GitHub: https://github.com/bugout-dev/dao
 */

pragma solidity ^0.8.9;

import "@moonstream/contracts/terminus/TerminusFacet.sol";
import "@openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin-contracts/contracts/token/ERC1155/IERC1155.sol";
import "@openzeppelin-contracts/contracts/access/Ownable.sol";
import "@openzeppelin-contracts/contracts/security/Pausable.sol";
import "@openzeppelin-contracts/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin-contracts/contracts/token/ERC1155/utils/ERC1155Holder.sol";

/**
 * @title Moonstream Dropper
 * @author Moonstream Engineering (engineering@moonstream.to)
 * @notice This contract manages drops for ERC20, ERC1155, and ERC721 tokens.
 */
contract Dropper is ERC1155Holder, Ownable, Pausable, ReentrancyGuard {
    // - [ ] withdrawERC20Tokens onlyOwner
    // - [ ] withdrawERC1155Tokens onlyOwner
    // - [ ] withdrawERC721Tokens onlyOwner
    // - [ ] claimERC20 (transfer with signature) nonReentrant
    // - [ ] claimERC1155 (transfer with signature) nonReentrant
    // - [ ] claimERC721 (transfer with signature) nonReentrant
    // - [ ] claimERC20MessageHash
    // - [ ] claimERC1155MessageHash
    // - [ ] claimERC721MessageHash
    // - [ ] onERC721Received nonReentrant
    // - [x] onERC1155Received nonReentrant (implemented by ERC1155Holder)
    // - [x] onERC1155BatchReceived nonReentrant (implemented by ERC1155Holder)
    // - [x] claimStatus view method
    // - [x] setSignerForClaim onlyOwner
    // - [x] getSignerForClaim public view
    // - [x] createClaim onlyOwner
    // - [x] numClaims public view
    // - [x] setClaimStatus onlyOwner
    // - [x] getClaim external view

    // Claim data structure:
    // (player address, claimId, requestId) -> true/false

    // Signer data structure
    // token address -> signer address

    uint256 public ERC20_REWARD_TYPE = 20;
    uint256 public ERC1155_REWARD_TYPE = 1155;

    struct ClaimableToken{
        uint256 tokenType;
        address tokenAddress; // address of the token
        uint256 tokenId;
        uint256 amount;
    }

    uint256 private NumClaims;
    mapping(uint256 => bool) IsClaimActive;
    mapping(uint256 => address) ClaimSigner;
    mapping(uint256 => ClaimableToken) ClaimToken;

    event ClaimCreated(uint256 claimId, uint256 tokenType, address tokenAddress, uint256 tokenId, uint256 amount);
    event ClaimStatusChanged(uint256 claimId, bool status);
    event ClaimSignerChanged(uint256 claimId, address signer);

    function createClaim(uint256 tokenType, address tokenAddress, uint256 tokenId, uint256 amount) external onlyOwner returns (uint256)
    {
        NumClaims++;

        ClaimableToken memory tokenMetadata;
        tokenMetadata.tokenType = tokenType;
        tokenMetadata.tokenAddress = tokenAddress;
        tokenMetadata.tokenId = tokenId;
        tokenMetadata.amount = amount;
        ClaimToken[NumClaims] = tokenMetadata;
        emit ClaimCreated(NumClaims, tokenType, tokenAddress, tokenId, amount);

        IsClaimActive[NumClaims] = true;
        emit ClaimStatusChanged(NumClaims, true);

        return NumClaims;
    }

    function numClaims() external view returns (uint256) {
        return NumClaims;
    }

    function getClaim(uint256 claimId) external view returns (ClaimableToken memory) {
        return ClaimToken[claimId];
    }

    function setClaimStatus(uint256 claimId, bool status) external onlyOwner {
        IsClaimActive[claimId] = status;
        emit ClaimStatusChanged(claimId, status);
    }

    function claimStatus(uint256 claimId) external view returns (bool) {
        return IsClaimActive[claimId];
    }

    function setSignerForClaim(uint256 claimId, address signer) external onlyOwner {
        ClaimSigner[claimId] = signer;
        emit ClaimSignerChanged(claimId, signer);
    }

    function getSignerForClaim(uint256 claimId) external view returns (address) {
        return ClaimSigner[claimId];
    }
}
