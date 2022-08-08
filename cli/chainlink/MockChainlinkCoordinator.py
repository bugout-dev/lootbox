# Code generated by moonworm : https://github.com/bugout-dev/moonworm
# Moonworm version : 0.1.18

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


class MockChainlinkCoordinator:
    def __init__(self, contract_address: Optional[ChecksumAddress]):
        self.contract_name = "MockChainlinkCoordinator"
        self.address = contract_address
        self.contract = None
        self.abi = get_abi_json("MockChainlinkCoordinator")
        if self.address is not None:
            self.contract: Optional[Contract] = Contract.from_abi(
                self.contract_name, self.address, self.abi
            )

    def deploy(self, _link: ChecksumAddress, transaction_config):
        contract_class = contract_from_build(self.contract_name)
        deployed_contract = contract_class.deploy(_link, transaction_config)
        self.address = deployed_contract.address
        self.contract = deployed_contract

    def assert_contract_is_instantiated(self) -> None:
        if self.contract is None:
            raise Exception("contract has not been instantiated")

    def verify_contract(self):
        self.assert_contract_is_instantiated()
        contract_class = contract_from_build(self.contract_name)
        contract_class.publish_source(self.contract)

    def preseed_offset(self) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.PRESEED_OFFSET.call()

    def public_key_offset(self) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.PUBLIC_KEY_OFFSET.call()

    def callbacks(self, arg1: bytes) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.callbacks.call(arg1)

    def mock_fulfill_randomness_request(
        self,
        request_id: bytes,
        randomness: int,
        callback_contract: ChecksumAddress,
        transaction_config,
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.mockFulfillRandomnessRequest(
            request_id, randomness, callback_contract, transaction_config
        )

    def on_token_transfer(
        self, _sender: ChecksumAddress, _fee: int, _data: bytes, transaction_config
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.onTokenTransfer(_sender, _fee, _data, transaction_config)

    def service_agreements(self, arg1: bytes) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.serviceAgreements.call(arg1)

    def withdrawable_tokens(self, arg1: ChecksumAddress) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.withdrawableTokens.call(arg1)


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


def handle_deploy(args: argparse.Namespace) -> None:
    network.connect(args.network)
    transaction_config = get_transaction_config(args)
    contract = MockChainlinkCoordinator(None)
    result = contract.deploy(_link=args.link_arg, transaction_config=transaction_config)
    print(result)


def handle_verify_contract(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = MockChainlinkCoordinator(args.address)
    result = contract.verify_contract()
    print(result)


def handle_preseed_offset(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = MockChainlinkCoordinator(args.address)
    result = contract.preseed_offset()
    print(result)


def handle_public_key_offset(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = MockChainlinkCoordinator(args.address)
    result = contract.public_key_offset()
    print(result)


def handle_callbacks(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = MockChainlinkCoordinator(args.address)
    result = contract.callbacks(arg1=args.arg1)
    print(result)


def handle_mock_fulfill_randomness_request(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = MockChainlinkCoordinator(args.address)
    transaction_config = get_transaction_config(args)
    result = contract.mock_fulfill_randomness_request(
        request_id=args.request_id,
        randomness=args.randomness,
        callback_contract=args.callback_contract,
        transaction_config=transaction_config,
    )
    print(result)


def handle_on_token_transfer(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = MockChainlinkCoordinator(args.address)
    transaction_config = get_transaction_config(args)
    result = contract.on_token_transfer(
        _sender=args.sender_arg,
        _fee=args.fee_arg,
        _data=args.data_arg,
        transaction_config=transaction_config,
    )
    print(result)


def handle_service_agreements(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = MockChainlinkCoordinator(args.address)
    result = contract.service_agreements(arg1=args.arg1)
    print(result)


def handle_withdrawable_tokens(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = MockChainlinkCoordinator(args.address)
    result = contract.withdrawable_tokens(arg1=args.arg1)
    print(result)


def generate_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI for MockChainlinkCoordinator")
    parser.set_defaults(func=lambda _: parser.print_help())
    subcommands = parser.add_subparsers()

    deploy_parser = subcommands.add_parser("deploy")
    add_default_arguments(deploy_parser, True)
    deploy_parser.add_argument("--link-arg", required=True, help="Type: address")
    deploy_parser.set_defaults(func=handle_deploy)

    verify_contract_parser = subcommands.add_parser("verify-contract")
    add_default_arguments(verify_contract_parser, False)
    verify_contract_parser.set_defaults(func=handle_verify_contract)

    preseed_offset_parser = subcommands.add_parser("preseed-offset")
    add_default_arguments(preseed_offset_parser, False)
    preseed_offset_parser.set_defaults(func=handle_preseed_offset)

    public_key_offset_parser = subcommands.add_parser("public-key-offset")
    add_default_arguments(public_key_offset_parser, False)
    public_key_offset_parser.set_defaults(func=handle_public_key_offset)

    callbacks_parser = subcommands.add_parser("callbacks")
    add_default_arguments(callbacks_parser, False)
    callbacks_parser.add_argument(
        "--arg1", required=True, help="Type: bytes32", type=bytes_argument_type
    )
    callbacks_parser.set_defaults(func=handle_callbacks)

    mock_fulfill_randomness_request_parser = subcommands.add_parser(
        "mock-fulfill-randomness-request"
    )
    add_default_arguments(mock_fulfill_randomness_request_parser, True)
    mock_fulfill_randomness_request_parser.add_argument(
        "--request-id", required=True, help="Type: bytes32", type=bytes_argument_type
    )
    mock_fulfill_randomness_request_parser.add_argument(
        "--randomness", required=True, help="Type: uint256", type=int
    )
    mock_fulfill_randomness_request_parser.add_argument(
        "--callback-contract", required=True, help="Type: address"
    )
    mock_fulfill_randomness_request_parser.set_defaults(
        func=handle_mock_fulfill_randomness_request
    )

    on_token_transfer_parser = subcommands.add_parser("on-token-transfer")
    add_default_arguments(on_token_transfer_parser, True)
    on_token_transfer_parser.add_argument(
        "--sender-arg", required=True, help="Type: address"
    )
    on_token_transfer_parser.add_argument(
        "--fee-arg", required=True, help="Type: uint256", type=int
    )
    on_token_transfer_parser.add_argument(
        "--data-arg", required=True, help="Type: bytes", type=bytes_argument_type
    )
    on_token_transfer_parser.set_defaults(func=handle_on_token_transfer)

    service_agreements_parser = subcommands.add_parser("service-agreements")
    add_default_arguments(service_agreements_parser, False)
    service_agreements_parser.add_argument(
        "--arg1", required=True, help="Type: bytes32", type=bytes_argument_type
    )
    service_agreements_parser.set_defaults(func=handle_service_agreements)

    withdrawable_tokens_parser = subcommands.add_parser("withdrawable-tokens")
    add_default_arguments(withdrawable_tokens_parser, False)
    withdrawable_tokens_parser.add_argument(
        "--arg1", required=True, help="Type: address"
    )
    withdrawable_tokens_parser.set_defaults(func=handle_withdrawable_tokens)

    return parser


def main() -> None:
    parser = generate_cli()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
