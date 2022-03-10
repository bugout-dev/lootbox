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
 * @title Moonstream Lootbox managing contract
 * @author Moonstream Engineering (engineering@moonstream.to)
 * @notice You can create lootboxes represented by terminus pools that includes ERC20 and ERC1155 tokens
 */
contract Lootbox is ERC1155Holder, Ownable, Pausable, ReentrancyGuard {
    uint256 public administratorPoolId;
    address public terminusAddress;
    uint256 private _totalLootboxCount;

    enum RewardType {
        ERC20, //0
        ERC1155 //1
    }
    /**
     * @dev Lootbox item structure
     * @notice Only for erc20 and erc1155 tokens
     */

    struct LootboxItem {
        RewardType rewardType;
        address tokenAddress; // address of the token
        uint256 tokenId;
        uint256 amount;
    }

    // Mapping from lootbox id to lootbox items (access by index)
    mapping(uint256 => mapping(uint256 => LootboxItem)) private lootboxItems;
    // Mapping from lootbox id to lootbox item count
    mapping(uint256 => uint256) private lootboxItemCounts;

    mapping(uint256 => uint256) public terminusPoolIdbyLootboxId;
    mapping(uint256 => uint256) public lootboxIdbyTerminusPoolId;

    event LootboxCreated(uint256 indexed lootboxId);
    event LootboxItemAdded(uint256 indexed lootboxId, LootboxItem lootboxItem);
    event LootboxItemRemoved(
        uint256 indexed lootboxId,
        LootboxItem lootboxItem
    );
    // How to call the user who opened the lootbox?
    event LootboxOpened(
        uint256 indexed lootboxId,
        address opener,
        uint256 lootboxItemCount
    );

    /**
     * @dev Initializes the Lootbox contract with the terminus address and administrator pool id.
     * @param _terminusAddress The address of the Terminus contract.
     * @param _administratorPoolId The id of the administrator terminus pool.
     */
    constructor(address _terminusAddress, uint256 _administratorPoolId) {
        administratorPoolId = _administratorPoolId;
        terminusAddress = _terminusAddress;
    }

    /**
     * @dev throws if called by account that doesn't hold the administrator pool token
     */
    modifier onlyAdministrator() {
        require(
            getTerminusContract().balanceOf(msg.sender, administratorPoolId) > 0
        );
        _;
    }

    /**
     * @dev Returns a initialized Terminus contract from the terminusAddress
     */
    function getTerminusContract() private view returns (TerminusFacet) {
        return TerminusFacet(terminusAddress);
    }

    /**
     * @dev Returns the total lootbox count
     */
    function totalLootboxCount() public view returns (uint256) {
        return _totalLootboxCount;
    }

    /**
     * @dev Returns the lootbox item count for a lootbox id
     * @param lootboxId The id of the lootbox
     */
    function lootboxItemCount(uint256 lootboxId) public view returns (uint256) {
        return lootboxItemCounts[lootboxId];
    }

    /**
     * @dev Returns the lootbox item for a lootbox id and item index
     * @param lootboxId The id of the lootbox
     * @param itemIndex The index of the item in the lootbox
     */
    function getLootboxItemByIndex(uint256 lootboxId, uint256 itemIndex)
        public
        view
        returns (LootboxItem memory)
    {
        return lootboxItems[lootboxId][itemIndex];
    }

    /**
     * @dev creates a new lootbox with the given terminus pool id and lootbox items
     * @param terminusPoolId The id of the terminus pool that represents the given pool
     * @param items The lootbox items
     */
    function createLootbox(uint256 terminusPoolId, LootboxItem[] memory items)
        public
        onlyAdministrator
    {
        uint256 lootboxId = _totalLootboxCount;
        _totalLootboxCount++;

        require(
            lootboxIdbyTerminusPoolId[terminusPoolId] == 0,
            "Another lootbox already exists formeaning this terminus pool"
        );
        lootboxIdbyTerminusPoolId[terminusPoolId] = lootboxId;
        terminusPoolIdbyLootboxId[lootboxId] = terminusPoolId;
        emit LootboxCreated(lootboxId);

        // Add the lootbox items
        for (uint256 i = 0; i < items.length; i++) {
            lootboxItems[lootboxId][i] = items[i];
            emit LootboxItemAdded(lootboxId, items[i]);
        }

        // Add the lootbox item count
        lootboxItemCounts[lootboxId] = items.length;
    }

    /**
     * @dev Adds an item to a lootbox
     * @param lootboxId The id of the lootbox
     * @param item The item to add to the lootbox
     */
    function addLootboxItem(uint256 lootboxId, LootboxItem memory item)
        public
        onlyAdministrator
    {
        uint256 itemIndex = lootboxItemCounts[lootboxId];
        lootboxItems[lootboxId][itemIndex] = item;
        lootboxItemCounts[lootboxId]++;

        emit LootboxItemAdded(lootboxId, item);
    }

    /**
     * @dev Removes an item from a lootbox
     * @param lootboxId The id of the lootbox
     * @param itemIndex The index of the item in the lootbox
     */
    function removeLootboxItem(uint256 lootboxId, uint256 itemIndex)
        public
        onlyAdministrator
    {
        //swap the item at the index with the last item in the array
        uint256 lastItemIndex = lootboxItemCounts[lootboxId] - 1;

        LootboxItem memory lastItem = lootboxItems[lootboxId][lastItemIndex];
        lootboxItems[lootboxId][lastItemIndex] = lootboxItems[lootboxId][
            itemIndex
        ];

        lootboxItems[lootboxId][itemIndex] = lastItem;
        //TODO: delete from mapping?
        lootboxItemCounts[lootboxId]--;
    }

    /**
     * @dev user opens a lootbox and gets a lootbox items from it
     * @param lootboxId The id of the lootbox
     * @param count The number of lootboxes to open
     */
    function openLootbox(uint256 lootboxId, uint256 count)
        public
        whenNotPaused
        nonReentrant
    {
        uint256 terminusPoolForLootbox = terminusPoolIdbyLootboxId[lootboxId];
        TerminusFacet terminusContract = getTerminusContract();

        require(
            terminusContract.balanceOf(msg.sender, terminusPoolForLootbox) >
                count,
            "You don't have enough tokens in your terminus pool"
        );

        terminusContract.burn(msg.sender, terminusPoolForLootbox, count);
        for (uint256 i = 0; i < lootboxItemCounts[lootboxId]; i++) {
            LootboxItem memory item = lootboxItems[lootboxId][i];
            if (item.rewardType == RewardType.ERC20) {
                IERC20(item.tokenAddress).transfer(
                    msg.sender,
                    item.amount * count
                );
            } else if (item.rewardType == RewardType.ERC1155) {
                IERC1155(item.tokenAddress).safeTransferFrom(
                    address(this),
                    msg.sender,
                    item.tokenId,
                    item.amount * count,
                    ""
                );
            } else {
                revert("Unsupported reward type");
            }
        }
    }

    /**
     * @dev Owner withdraws erc20 tokens from the contract
     * @param tokenAddress The address of the erc20 token contract
     * @param amount The amount to withdraw
     */
    function withdrawERC20(address tokenAddress, uint256 amount)
        external
        onlyOwner
    {
        IERC20 erc20Contract = IERC20(tokenAddress);
        erc20Contract.transfer(_msgSender(), amount);
    }

    /**
     * @dev Owner withdraws erc1155 tokens from the contract
     * @param tokenAddress The address of the erc1155 token contract
     * @param tokenId The id of the erc1155 token
     * @param amount The amount to withdraw
     */

    function withdrawERC1155(
        address tokenAddress,
        uint256 tokenId,
        uint256 amount
    ) external onlyOwner {
        IERC1155 erc1155Contract = IERC1155(tokenAddress);
        erc1155Contract.safeTransferFrom(
            address(this),
            _msgSender(),
            tokenId,
            amount,
            ""
        );
    }

    /**
     * @dev Transfer controll of the terminus pools from contract to owner
     * @param poolIds The array of terminus pool ids
     */
    function surrenderTerminusPools(uint256[] calldata poolIds)
        external
        onlyOwner
    {
        address _owner = owner();
        TerminusFacet terminusContract = TerminusFacet(terminusAddress);
        for (uint256 i = 0; i < poolIds.length; i++) {
            terminusContract.setPoolController(poolIds[i], _owner);
        }
    }

    /**
     * @dev pause the contract
     * @notice only pauses the openLootbox function
     */
    function pause() external onlyOwner {
        require(!paused(), "Already paused");
        _pause();
    }

    /**
     * @dev unpause the contract
     */
    function unpause() external onlyOwner {
        require(paused(), "Already unpaused");
        _unpause();
    }
}
