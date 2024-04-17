# Code generated by moonworm : https://github.com/moonstream-to/moonworm
# Moonworm version : 0.8.0

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from brownie import Contract, network, project
from brownie.network.contract import ContractContainer
from eth_typing.evm import ChecksumAddress


PROJECT_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUILD_DIRECTORY = os.path.join(PROJECT_DIRECTORY, "build", "contracts")


def boolean_argument_type(raw_value: str) -> bool:
    TRUE_VALUES = ["1", "t", "y", "true", "yes"]
    FALSE_VALUES = ["0", "f", "n", "false", "no"]

    if raw_value.lower() in TRUE_VALUES:
        return True
    elif raw_value.lower() in FALSE_VALUES:
        return False

    raise ValueError(
        f"Invalid boolean argument: {raw_value}. Value must be one of: {','.join(TRUE_VALUES + FALSE_VALUES)}"
    )


def bytes_argument_type(raw_value: str) -> str:
    return raw_value


def get_abi_json(abi_name: str) -> List[Dict[str, Any]]:
    abi_full_path = os.path.join(BUILD_DIRECTORY, f"{abi_name}.json")
    if not os.path.isfile(abi_full_path):
        raise IOError(
            f"File does not exist: {abi_full_path}. Maybe you have to compile the smart contracts?"
        )

    with open(abi_full_path, "r") as ifp:
        build = json.load(ifp)

    abi_json = build.get("abi")
    if abi_json is None:
        raise ValueError(f"Could not find ABI definition in: {abi_full_path}")

    return abi_json


def contract_from_build(abi_name: str) -> ContractContainer:
    # This is workaround because brownie currently doesn't support loading the same project multiple
    # times. This causes problems when using multiple contracts from the same project in the same
    # python project.
    PROJECT = project.main.Project("moonworm", Path(PROJECT_DIRECTORY))

    abi_full_path = os.path.join(BUILD_DIRECTORY, f"{abi_name}.json")
    if not os.path.isfile(abi_full_path):
        raise IOError(
            f"File does not exist: {abi_full_path}. Maybe you have to compile the smart contracts?"
        )

    with open(abi_full_path, "r") as ifp:
        build = json.load(ifp)

    return ContractContainer(PROJECT, build)


class VILToken:
    def __init__(self, contract_address: Optional[ChecksumAddress]):
        self.contract_name = "VILToken"
        self.address = contract_address
        self.contract = None
        self.abi = get_abi_json("VILToken")
        if self.address is not None:
            self.contract: Optional[Contract] = Contract.from_abi(
                self.contract_name, self.address, self.abi
            )

    def deploy(self, transaction_config):
        contract_class = contract_from_build(self.contract_name)
        deployed_contract = contract_class.deploy(transaction_config)
        self.address = deployed_contract.address
        self.contract = deployed_contract
        return deployed_contract.tx

    def assert_contract_is_instantiated(self) -> None:
        if self.contract is None:
            raise Exception("contract has not been instantiated")

    def verify_contract(self):
        self.assert_contract_is_instantiated()
        contract_class = contract_from_build(self.contract_name)
        contract_class.publish_source(self.contract)

    def allowance(
        self,
        owner: ChecksumAddress,
        spender: ChecksumAddress,
        block_number: Optional[Union[str, int]] = "latest",
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.allowance.call(
            owner, spender, block_identifier=block_number
        )

    def approve(self, spender: ChecksumAddress, amount: int, transaction_config) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.approve(spender, amount, transaction_config)

    def balance_of(
        self,
        account: ChecksumAddress,
        block_number: Optional[Union[str, int]] = "latest",
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.balanceOf.call(account, block_identifier=block_number)

    def check_whitelist(
        self,
        _address: ChecksumAddress,
        block_number: Optional[Union[str, int]] = "latest",
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.checkWhitelist.call(
            _address, block_identifier=block_number
        )

    def decimals(self, block_number: Optional[Union[str, int]] = "latest") -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.decimals.call(block_identifier=block_number)

    def decrease_allowance(
        self, spender: ChecksumAddress, subtracted_value: int, transaction_config
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.decreaseAllowance(
            spender, subtracted_value, transaction_config
        )

    def increase_allowance(
        self, spender: ChecksumAddress, added_value: int, transaction_config
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.increaseAllowance(spender, added_value, transaction_config)

    def max_total_supply(
        self, block_number: Optional[Union[str, int]] = "latest"
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.maxTotalSupply.call(block_identifier=block_number)

    def mint(self, amount: int, transaction_config) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.mint(amount, transaction_config)

    def name(self, block_number: Optional[Union[str, int]] = "latest") -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.name.call(block_identifier=block_number)

    def owner(self, block_number: Optional[Union[str, int]] = "latest") -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.owner.call(block_identifier=block_number)

    def renounce_ownership(self, transaction_config) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.renounceOwnership(transaction_config)

    def set_whitelist(
        self, _whitelist_address: ChecksumAddress, approved: bool, transaction_config
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.setWhitelist(
            _whitelist_address, approved, transaction_config
        )

    def symbol(self, block_number: Optional[Union[str, int]] = "latest") -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.symbol.call(block_identifier=block_number)

    def total_supply(self, block_number: Optional[Union[str, int]] = "latest") -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.totalSupply.call(block_identifier=block_number)

    def transfer(
        self, recipient: ChecksumAddress, amount: int, transaction_config
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.transfer(recipient, amount, transaction_config)

    def transfer_from(
        self,
        sender: ChecksumAddress,
        recipient: ChecksumAddress,
        amount: int,
        transaction_config,
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.transferFrom(sender, recipient, amount, transaction_config)

    def transfer_ownership(self, new_owner: ChecksumAddress, transaction_config) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.transferOwnership(new_owner, transaction_config)

    def withdraw(self, transaction_config) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.withdraw(transaction_config)


def get_transaction_config(args: argparse.Namespace) -> Dict[str, Any]:
    signer = network.accounts.load(args.sender, args.password)
    transaction_config: Dict[str, Any] = {"from": signer}
    if args.gas_price is not None:
        transaction_config["gas_price"] = args.gas_price
    if args.max_fee_per_gas is not None:
        transaction_config["max_fee"] = args.max_fee_per_gas
    if args.max_priority_fee_per_gas is not None:
        transaction_config["priority_fee"] = args.max_priority_fee_per_gas
    if args.confirmations is not None:
        transaction_config["required_confs"] = args.confirmations
    if args.nonce is not None:
        transaction_config["nonce"] = args.nonce
    return transaction_config


def add_default_arguments(parser: argparse.ArgumentParser, transact: bool) -> None:
    parser.add_argument(
        "--network", required=True, help="Name of brownie network to connect to"
    )
    parser.add_argument(
        "--address", required=False, help="Address of deployed contract to connect to"
    )
    if not transact:
        parser.add_argument(
            "--block-number",
            required=False,
            type=int,
            help="Call at the given block number, defaults to latest",
        )
        return
    parser.add_argument(
        "--sender", required=True, help="Path to keystore file for transaction sender"
    )
    parser.add_argument(
        "--password",
        required=False,
        help="Password to keystore file (if you do not provide it, you will be prompted for it)",
    )
    parser.add_argument(
        "--gas-price", default=None, help="Gas price at which to submit transaction"
    )
    parser.add_argument(
        "--max-fee-per-gas",
        default=None,
        help="Max fee per gas for EIP1559 transactions",
    )
    parser.add_argument(
        "--max-priority-fee-per-gas",
        default=None,
        help="Max priority fee per gas for EIP1559 transactions",
    )
    parser.add_argument(
        "--confirmations",
        type=int,
        default=None,
        help="Number of confirmations to await before considering a transaction completed",
    )
    parser.add_argument(
        "--nonce", type=int, default=None, help="Nonce for the transaction (optional)"
    )
    parser.add_argument(
        "--value", default=None, help="Value of the transaction in wei(optional)"
    )
    parser.add_argument("--verbose", action="store_true", help="Print verbose output")


def handle_deploy(args: argparse.Namespace) -> None:
    network.connect(args.network)
    transaction_config = get_transaction_config(args)
    contract = VILToken(None)
    result = contract.deploy(transaction_config=transaction_config)
    print(result)
    if args.verbose:
        print(result.info())


def handle_verify_contract(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    result = contract.verify_contract()
    print(result)


def handle_allowance(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    result = contract.allowance(
        owner=args.owner, spender=args.spender, block_number=args.block_number
    )
    print(result)


def handle_approve(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    transaction_config = get_transaction_config(args)
    result = contract.approve(
        spender=args.spender, amount=args.amount, transaction_config=transaction_config
    )
    print(result)
    if args.verbose:
        print(result.info())


def handle_balance_of(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    result = contract.balance_of(account=args.account, block_number=args.block_number)
    print(result)


def handle_check_whitelist(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    result = contract.check_whitelist(
        _address=args.address_arg, block_number=args.block_number
    )
    print(result)


def handle_decimals(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    result = contract.decimals(block_number=args.block_number)
    print(result)


def handle_decrease_allowance(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    transaction_config = get_transaction_config(args)
    result = contract.decrease_allowance(
        spender=args.spender,
        subtracted_value=args.subtracted_value,
        transaction_config=transaction_config,
    )
    print(result)
    if args.verbose:
        print(result.info())


def handle_increase_allowance(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    transaction_config = get_transaction_config(args)
    result = contract.increase_allowance(
        spender=args.spender,
        added_value=args.added_value,
        transaction_config=transaction_config,
    )
    print(result)
    if args.verbose:
        print(result.info())


def handle_max_total_supply(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    result = contract.max_total_supply(block_number=args.block_number)
    print(result)


def handle_mint(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    transaction_config = get_transaction_config(args)
    result = contract.mint(amount=args.amount, transaction_config=transaction_config)
    print(result)
    if args.verbose:
        print(result.info())


def handle_name(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    result = contract.name(block_number=args.block_number)
    print(result)


def handle_owner(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    result = contract.owner(block_number=args.block_number)
    print(result)


def handle_renounce_ownership(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    transaction_config = get_transaction_config(args)
    result = contract.renounce_ownership(transaction_config=transaction_config)
    print(result)
    if args.verbose:
        print(result.info())


def handle_set_whitelist(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    transaction_config = get_transaction_config(args)
    result = contract.set_whitelist(
        _whitelist_address=args.whitelist_address_arg,
        approved=args.approved,
        transaction_config=transaction_config,
    )
    print(result)
    if args.verbose:
        print(result.info())


def handle_symbol(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    result = contract.symbol(block_number=args.block_number)
    print(result)


def handle_total_supply(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    result = contract.total_supply(block_number=args.block_number)
    print(result)


def handle_transfer(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    transaction_config = get_transaction_config(args)
    result = contract.transfer(
        recipient=args.recipient,
        amount=args.amount,
        transaction_config=transaction_config,
    )
    print(result)
    if args.verbose:
        print(result.info())


def handle_transfer_from(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    transaction_config = get_transaction_config(args)
    result = contract.transfer_from(
        sender=args.sender_arg,
        recipient=args.recipient,
        amount=args.amount,
        transaction_config=transaction_config,
    )
    print(result)
    if args.verbose:
        print(result.info())


def handle_transfer_ownership(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    transaction_config = get_transaction_config(args)
    result = contract.transfer_ownership(
        new_owner=args.new_owner, transaction_config=transaction_config
    )
    print(result)
    if args.verbose:
        print(result.info())


def handle_withdraw(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = VILToken(args.address)
    transaction_config = get_transaction_config(args)
    result = contract.withdraw(transaction_config=transaction_config)
    print(result)
    if args.verbose:
        print(result.info())


def generate_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI for VILToken")
    parser.set_defaults(func=lambda _: parser.print_help())
    subcommands = parser.add_subparsers()

    deploy_parser = subcommands.add_parser("deploy")
    add_default_arguments(deploy_parser, True)
    deploy_parser.set_defaults(func=handle_deploy)

    verify_contract_parser = subcommands.add_parser("verify-contract")
    add_default_arguments(verify_contract_parser, False)
    verify_contract_parser.set_defaults(func=handle_verify_contract)

    allowance_parser = subcommands.add_parser("allowance")
    add_default_arguments(allowance_parser, False)
    allowance_parser.add_argument("--owner", required=True, help="Type: address")
    allowance_parser.add_argument("--spender", required=True, help="Type: address")
    allowance_parser.set_defaults(func=handle_allowance)

    approve_parser = subcommands.add_parser("approve")
    add_default_arguments(approve_parser, True)
    approve_parser.add_argument("--spender", required=True, help="Type: address")
    approve_parser.add_argument(
        "--amount", required=True, help="Type: uint256", type=int
    )
    approve_parser.set_defaults(func=handle_approve)

    balance_of_parser = subcommands.add_parser("balance-of")
    add_default_arguments(balance_of_parser, False)
    balance_of_parser.add_argument("--account", required=True, help="Type: address")
    balance_of_parser.set_defaults(func=handle_balance_of)

    check_whitelist_parser = subcommands.add_parser("check-whitelist")
    add_default_arguments(check_whitelist_parser, False)
    check_whitelist_parser.add_argument(
        "--address-arg", required=True, help="Type: address"
    )
    check_whitelist_parser.set_defaults(func=handle_check_whitelist)

    decimals_parser = subcommands.add_parser("decimals")
    add_default_arguments(decimals_parser, False)
    decimals_parser.set_defaults(func=handle_decimals)

    decrease_allowance_parser = subcommands.add_parser("decrease-allowance")
    add_default_arguments(decrease_allowance_parser, True)
    decrease_allowance_parser.add_argument(
        "--spender", required=True, help="Type: address"
    )
    decrease_allowance_parser.add_argument(
        "--subtracted-value", required=True, help="Type: uint256", type=int
    )
    decrease_allowance_parser.set_defaults(func=handle_decrease_allowance)

    increase_allowance_parser = subcommands.add_parser("increase-allowance")
    add_default_arguments(increase_allowance_parser, True)
    increase_allowance_parser.add_argument(
        "--spender", required=True, help="Type: address"
    )
    increase_allowance_parser.add_argument(
        "--added-value", required=True, help="Type: uint256", type=int
    )
    increase_allowance_parser.set_defaults(func=handle_increase_allowance)

    max_total_supply_parser = subcommands.add_parser("max-total-supply")
    add_default_arguments(max_total_supply_parser, False)
    max_total_supply_parser.set_defaults(func=handle_max_total_supply)

    mint_parser = subcommands.add_parser("mint")
    add_default_arguments(mint_parser, True)
    mint_parser.add_argument("--amount", required=True, help="Type: uint256", type=int)
    mint_parser.set_defaults(func=handle_mint)

    name_parser = subcommands.add_parser("name")
    add_default_arguments(name_parser, False)
    name_parser.set_defaults(func=handle_name)

    owner_parser = subcommands.add_parser("owner")
    add_default_arguments(owner_parser, False)
    owner_parser.set_defaults(func=handle_owner)

    renounce_ownership_parser = subcommands.add_parser("renounce-ownership")
    add_default_arguments(renounce_ownership_parser, True)
    renounce_ownership_parser.set_defaults(func=handle_renounce_ownership)

    set_whitelist_parser = subcommands.add_parser("set-whitelist")
    add_default_arguments(set_whitelist_parser, True)
    set_whitelist_parser.add_argument(
        "--whitelist-address-arg", required=True, help="Type: address"
    )
    set_whitelist_parser.add_argument(
        "--approved", required=True, help="Type: bool", type=boolean_argument_type
    )
    set_whitelist_parser.set_defaults(func=handle_set_whitelist)

    symbol_parser = subcommands.add_parser("symbol")
    add_default_arguments(symbol_parser, False)
    symbol_parser.set_defaults(func=handle_symbol)

    total_supply_parser = subcommands.add_parser("total-supply")
    add_default_arguments(total_supply_parser, False)
    total_supply_parser.set_defaults(func=handle_total_supply)

    transfer_parser = subcommands.add_parser("transfer")
    add_default_arguments(transfer_parser, True)
    transfer_parser.add_argument("--recipient", required=True, help="Type: address")
    transfer_parser.add_argument(
        "--amount", required=True, help="Type: uint256", type=int
    )
    transfer_parser.set_defaults(func=handle_transfer)

    transfer_from_parser = subcommands.add_parser("transfer-from")
    add_default_arguments(transfer_from_parser, True)
    transfer_from_parser.add_argument(
        "--sender-arg", required=True, help="Type: address"
    )
    transfer_from_parser.add_argument(
        "--recipient", required=True, help="Type: address"
    )
    transfer_from_parser.add_argument(
        "--amount", required=True, help="Type: uint256", type=int
    )
    transfer_from_parser.set_defaults(func=handle_transfer_from)

    transfer_ownership_parser = subcommands.add_parser("transfer-ownership")
    add_default_arguments(transfer_ownership_parser, True)
    transfer_ownership_parser.add_argument(
        "--new-owner", required=True, help="Type: address"
    )
    transfer_ownership_parser.set_defaults(func=handle_transfer_ownership)

    withdraw_parser = subcommands.add_parser("withdraw")
    add_default_arguments(withdraw_parser, True)
    withdraw_parser.set_defaults(func=handle_withdraw)

    return parser


def main() -> None:
    parser = generate_cli()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
