import argparse

from brownie import network

from . import Dropper, MockTerminus


def handle_setup_drop(args: argparse.Namespace) -> None:
    network.connect(args.network)
    tx_config = Dropper.get_transaction_config(args)
    claim_id, claim_info, claim_uri, signer_address = setup_drop(
        args.address,
        args.claim_id,
        args.claim_type,
        args.claim_address,
        args.claim_pool_id,
        args.claim_default_amount,
        args.claim_uri,
        args.signer_address,
        args.use_pool_uri,
        tx_config,
    )

    print(f"Set up claim: {claim_id} -- {claim_info}")
    print(f"URI: {claim_uri}, Signer: {signer_address}")


def setup_drop(
    address,
    claim_id,
    claim_type,
    claim_address,
    claim_pool_id,
    claim_default_amount,
    claim_uri,
    signer_address,
    use_pool_uri,
    tx_config,
):
    dropper = Dropper.Dropper(address)

    if claim_type == 1 or claim_type == 1155:
        terminus = MockTerminus.MockTerminus(claim_address)

        if claim_type == 1:
            dropper_is_approved_for_pool = terminus.is_approved_for_pool(
                claim_pool_id, dropper.address
            )
            if not dropper_is_approved_for_pool:
                pool_approval_check = input(
                    f"Dropper contract {dropper.address} is not approved to mint tokens from Terminus pool {claim_pool_id} on {terminus.address}. Approve dropper? (y/N)"
                )
                if pool_approval_check.strip().lower() == "y":
                    terminus.approve_for_pool(claim_pool_id, dropper.address, tx_config)

        if use_pool_uri:
            if claim_uri is not None:
                raise ValueError(
                    "You cannot use use_pool_uri and provide a claim_uri at the same time"
                )
            else:
                claim_uri = terminus.uri(claim_pool_id)

    if claim_id is None:
        if claim_type is None or claim_address is None or claim_pool_id is None:
            raise ValueError(
                "Please specify the following arguments: claim_type, claim_address, claim_pool_id"
            )

        dropper.create_claim(
            claim_type,
            claim_address,
            claim_pool_id,
            claim_default_amount,
            tx_config,
        )

        claim_id = dropper.num_claims()

    claim_info = dropper.get_claim(claim_id)
    permission_check = input(f"Claim ID: {claim_id} -- {claim_info}? (y/N)")
    if permission_check.strip().lower() != "y":
        raise Exception(f"You did not wish to proceed with setup of claim: {claim_id}")

    if claim_uri:
        dropper.set_claim_uri(claim_id, claim_uri, tx_config)
        print(f"Claim ID: {claim_id}, claim URI: {claim_uri}")

    if signer_address:
        dropper.set_signer_for_claim(claim_id, signer_address, tx_config)
        print(f"Claim ID: {claim_id}, signer: {signer_address}")

    return claim_id, claim_info, claim_uri, signer_address


def generate_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Set up a drop on a Dropper contract instance"
    )
    Dropper.add_default_arguments(parser, True)
    parser.add_argument(
        "--claim-id",
        type=int,
        default=None,
        help="Claim ID of drop to set up (if known)",
    )
    parser.add_argument("--claim-type", type=int, choices=[1, 20, 1155], default=None)
    parser.add_argument("--claim-address", help="Address of contract to claim from")
    parser.add_argument("--claim-pool-id", help="Pool ID for ERC1155-based claims")
    parser.add_argument(
        "--claim-default-amount", type=int, default=1, help="Default amount for claim"
    )
    parser.add_argument("--claim-uri", help="Metadata URI for claim")
    parser.add_argument("--signer-address", help="Address for signer")
    parser.add_argument(
        "--use-pool-uri",
        action="store_true",
        help="For Terminus claim types, use the Terminus pool URI as the claim URI",
    )
    parser.set_defaults(func=handle_setup_drop)
    return parser


if __name__ == "__main__":
    parser = generate_cli()
    args = parser.parse_args()
    args.func(args)
