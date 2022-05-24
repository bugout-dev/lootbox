"""
Lootbox API.
"""
from atexit import register
import logging
import time
from typing import List, Dict, Optional
from uuid import UUID

from web3 import Web3
from brownie import network


from fastapi import APIRouter, Body, FastAPI, Request, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from .. import actions
from .. import data
from .. import db
from .. import Dropper
from .. import signatures
from ..middleware import DropperHTTPException, DropperAuthMiddleware
from ..settings import (
    ENGINE_BROWNIE_NETWORK,
    DOCS_TARGET_PATH,
    ORIGINS,
)

network.connect(ENGINE_BROWNIE_NETWORK)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/drops",
)


@router.get("", response_model=data.DropResponse)
async def get_drop_handler(
    dropper_claim_id: UUID,
    address: str,
    db_session: Session = Depends(db.yield_db_session),
) -> data.DropResponse:
    """
    Get signed transaction for user with the given address.
    """

    address = Web3.toChecksumAddress(address)

    try:
        claimant = actions.get_claimant(db_session, dropper_claim_id, address)
    except NoResultFound:
        raise DropperHTTPException(
            status_code=403, detail="You are not authorized to claim that reward"
        )
    except Exception as e:
        raise DropperHTTPException(status_code=500, detail="Can't get claimant")

    transformed_amount = actions.transform_claim_amount(
        db_session, dropper_claim_id, claimant.amount
    )

    if not claimant.active:
        raise DropperHTTPException(
            status_code=403, detail="Cannot claim rewards for an inactive claim"
        )

    # If block deadline has already been exceeded - the contract (or frontend) will handle it.
    if claimant.claim_block_deadline is None:
        raise DropperHTTPException(
            status_code=403,
            detail="Cannot claim rewards for a claim with no block deadline",
        )

    dropper_contract = Dropper.Dropper(claimant.dropper_contract_address)
    message_hash = dropper_contract.claim_message_hash(
        claimant.claim_id,
        claimant.address,
        claimant.claim_block_deadline,
        transformed_amount,
    )

    try:
        signature = signatures.DROP_SIGNER.sign_message(message_hash)
    except signatures.AWSDescribeInstancesFail:
        raise DropperHTTPException(status_code=500)
    except signatures.SignWithInstanceFail:
        raise DropperHTTPException(status_code=500)
    except Exception as err:
        logger.error(f"Unexpected error in signing message process: {err}")
        raise DropperHTTPException(status_code=500)

    return data.DropResponse(
        claimant=claimant.address,
        amount=transformed_amount,
        claim_id=claimant.claim_id,
        block_deadline=claimant.claim_block_deadline,
        signature=signature,
    )


@router.get("/batch", response_model=List[data.DropBatchResponseItem])
async def get_drop_batch_handler(
    blockchain: str,
    address: str,
    limit: int = 10,
    offset: int = 0,
    db_session: Session = Depends(db.yield_db_session),
) -> List[data.DropBatchResponseItem]:
    """
    Get signed transaction for all user drops.
    """

    address = Web3.toChecksumAddress(address)

    try:
        claimant_drops = actions.get_claimant_drops(
            db_session, blockchain, address, limit, offset
        )
    except NoResultFound:
        raise DropperHTTPException(
            status_code=403, detail="You are not authorized to claim that reward"
        )
    except Exception as e:
        raise DropperHTTPException(status_code=500, detail="Can't get claimant")

    # generate list of claims

    claims: List[data.DropBatchResponseItem] = []

    for claimant_drop in claimant_drops:

        transformed_amount = actions.transform_claim_amount(
            db_session, claimant_drop.dropper_claim_id, claimant_drop.amount
        )

        dropper_contract = Dropper.Dropper(claimant_drop.dropper_contract_address)

        message_hash = dropper_contract.claim_message_hash(
            claimant_drop.claim_id,
            claimant_drop.address,
            claimant_drop.claim_block_deadline,
            transformed_amount,
        )

        try:
            signature = signatures.DROP_SIGNER.sign_message(message_hash)
        except signatures.AWSDescribeInstancesFail:
            raise DropperHTTPException(status_code=500)
        except signatures.SignWithInstanceFail:
            raise DropperHTTPException(status_code=500)
        except Exception as err:
            logger.error(f"Unexpected error in signing message process: {err}")
            raise DropperHTTPException(status_code=500)

        claims.append(
            data.DropBatchResponseItem(
                claimant=claimant_drop.address,
                amount=transformed_amount,
                claim_id=claimant_drop.claim_id,
                block_deadline=claimant_drop.claim_block_deadline,
                signature=signature,
                dropper_claim_id=claimant_drop.dropper_claim_id,
                dropper_contract_address=claimant_drop.dropper_contract_address,
                blockchain=claimant_drop.blockchain,
                active=claimant_drop.active,
            )
        )

    return claims


@router.get("/contracts", response_model=List[data.DropperContractResponse])
async def get_dropper_contracts_handler(
    blockchain: Optional[str] = Query(None),
    db_session: Session = Depends(db.yield_db_session),
) -> List[data.DropperContractResponse]:
    """
    Get list of drops for a given dropper contract.
    """

    try:
        results = actions.list_dropper_contracts(
            db_session=db_session, blockchain=blockchain
        )
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="No drops found.")
    except Exception as e:
        logger.error(f"Can't get list of dropper contracts end with error: {e}")
        raise DropperHTTPException(status_code=500, detail="Can't get contracts")

    response = [
        data.DropperContractResponse(
            id=result.id,
            blockchain=result.blockchain,
            address=result.address,
            title=result.title,
            description=result.description,
            image_uri=result.image_uri,
        )
        for result in results
    ]

    return response


@router.get("/blockchains")
async def get_drops_blockchains_handler(
    db_session: Session = Depends(db.yield_db_session),
) -> List[data.DropperBlockchainResponse]:
    """
    Get list of blockchains.
    """

    try:
        results = actions.list_drops_blockchains(db_session=db_session)
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="No drops found.")
    except Exception as e:
        logger.error(f"Can't get list of drops end with error: {e}")
        raise DropperHTTPException(status_code=500, detail="Can't get drops")

    response = [
        data.DropperBlockchainResponse(
            blockchain=result.blockchain,
        )
        for result in results
    ]

    return response


@router.get("/terminus")
async def get_drops_terminus_handler(
    blockchain: str = Query(None),
    db_session: Session = Depends(db.yield_db_session),
) -> List[data.DropperTerminusResponse]:

    """
    Return distinct terminus pools
    """

    try:
        results = actions.list_drops_terminus(
            db_session=db_session, blockchain=blockchain
        )
    except Exception as e:
        logger.error(f"Can't get list of terminus contracts end with error: {e}")
        raise DropperHTTPException(
            status_code=500, detail="Can't get terminus contracts"
        )

    response = [
        data.DropperTerminusResponse(
            terminus_address=result.terminus_address,
            terminus_pool_id=result.terminus_pool_id,
            blockchain=result.blockchain,
        )
        for result in results
    ]

    return response


@router.get("/claims", response_model=data.DropListResponse)
async def get_drop_list_handler(
    blockchain: str,
    claimant_address: str,
    dropper_contract_address: Optional[str] = Query(None),
    terminus_address: Optional[str] = Query(None),
    terminus_pool_id: Optional[int] = Query(None),
    active: Optional[bool] = Query(None),
    limit: int = 20,
    offset: int = 0,
    db_session: Session = Depends(db.yield_db_session),
) -> data.DropListResponse:
    """
    Get list of drops for a given dropper contract and claimant address.
    dasdasd
    """

    if dropper_contract_address:
        dropper_contract_address = Web3.toChecksumAddress(dropper_contract_address)

    if claimant_address:
        claimant_address = Web3.toChecksumAddress(claimant_address)

    if terminus_address:
        terminus_address = Web3.toChecksumAddress(terminus_address)

    try:
        results = actions.get_claims(
            db_session=db_session,
            dropper_contract_address=dropper_contract_address,
            blockchain=blockchain,
            claimant_address=claimant_address,
            terminus_address=terminus_address,
            terminus_pool_id=terminus_pool_id,
            active=active,
            limit=limit,
            offset=offset,
        )
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="No drops found.")
    except Exception as e:
        logger.error(
            f"Can't get claims for user {claimant_address} end with error: {e}"
        )
        raise DropperHTTPException(status_code=500, detail="Can't get claims")

    return data.DropListResponse(drops=[result for result in results])


@router.get("/terminus/claims", response_model=data.DropListResponse)
async def get_drop_terminus_list_handler(
    blockchain: str,
    terminus_address: str,
    terminus_pool_id: int,
    dropper_contract_address: Optional[str] = Query(None),
    active: Optional[bool] = Query(None),
    limit: int = 20,
    offset: int = 0,
    db_session: Session = Depends(db.yield_db_session),
) -> data.DropListResponse:
    """
    Get list of drops for a given dropper contract and claimant address.
    """

    if dropper_contract_address:
        dropper_contract_address = Web3.toChecksumAddress(dropper_contract_address)

    terminus_address = Web3.toChecksumAddress(terminus_address)

    try:
        results = actions.get_terminus_claims(
            db_session=db_session,
            dropper_contract_address=dropper_contract_address,
            blockchain=blockchain,
            terminus_address=terminus_address,
            terminus_pool_id=terminus_pool_id,
            active=active,
            limit=limit,
            offset=offset,
        )
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="No drops found.")
    except Exception as e:
        logger.error(
            f"Can't get Terminus claims (blockchain={blockchain}, address={terminus_address}, pool_id={terminus_pool_id}): {e}"
        )
        raise DropperHTTPException(status_code=500, detail="Can't get claims")

    return data.DropListResponse(drops=[result for result in results])


@router.post("/claims", response_model=data.DropCreatedResponse)
async def create_drop(
    request: Request,
    register_request: data.DropRegisterRequest = Body(...),
    db_session: Session = Depends(db.yield_db_session),
) -> data.DropCreatedResponse:

    """
    Create a drop for a given dropper contract.
    """
    try:
        actions.ensure_dropper_contract_owner(
            db_session, register_request.dropper_contract_id, request.state.address
        )
    except actions.AuthorizationError as e:
        logger.error(e)
        raise DropperHTTPException(status_code=403)
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="Dropper contract not found")
    except Exception as e:
        logger.error(e)
        raise DropperHTTPException(status_code=500)

    if register_request.terminus_address:
        register_request.terminus_address = Web3.toChecksumAddress(
            register_request.terminus_address
        )

    try:
        claim = actions.create_claim(
            db_session=db_session,
            dropper_contract_id=register_request.dropper_contract_id,
            title=register_request.title,
            description=register_request.description,
            claim_block_deadline=register_request.claim_block_deadline,
            terminus_address=register_request.terminus_address,
            terminus_pool_id=register_request.terminus_pool_id,
            claim_id=register_request.claim_id,
        )
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="Dropper contract not found")
    except Exception as e:
        logger.error(f"Can't create claim: {e}")
        raise DropperHTTPException(status_code=500, detail="Can't create claim")

    return data.DropCreatedResponse(
        dropper_claim_id=claim.id,
        dropper_contract_id=claim.dropper_contract_id,
        title=claim.title,
        description=claim.description,
        claim_block_deadline=claim.claim_block_deadline,
        terminus_address=claim.terminus_address,
        terminus_pool_id=claim.terminus_pool_id,
        claim_id=claim.claim_id,
    )


@router.put(
    "/claims/{dropper_claim_id}/activate",
    response_model=data.DropUpdatedResponse,
)
async def activate_drop(
    request: Request,
    dropper_claim_id: UUID,
    db_session: Session = Depends(db.yield_db_session),
) -> data.DropUpdatedResponse:

    """
    Activate a given drop by drop id.
    """
    try:
        actions.ensure_admin_token_holder(
            db_session, dropper_claim_id, request.state.address
        )
    except actions.AuthorizationError as e:
        logger.error(e)
        raise DropperHTTPException(status_code=403)
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="Drop not found")

    try:
        drop = actions.activate_drop(
            db_session=db_session,
            dropper_claim_id=dropper_claim_id,
        )
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="Drop not found")
    except Exception as e:
        logger.error(f"Can't activate drop: {e}")
        raise DropperHTTPException(status_code=500, detail="Can't activate drop")

    return data.DropUpdatedResponse(
        dropper_claim_id=drop.id,
        dropper_contract_id=drop.dropper_contract_id,
        title=drop.title,
        description=drop.description,
        claim_block_deadline=drop.claim_block_deadline,
        terminus_address=drop.terminus_address,
        terminus_pool_id=drop.terminus_pool_id,
        claim_id=drop.claim_id,
        active=drop.active,
    )


@router.put(
    "/claims/{dropper_claim_id}/deactivate",
    response_model=data.DropUpdatedResponse,
)
async def deactivate_drop(
    request: Request,
    dropper_claim_id: UUID,
    db_session: Session = Depends(db.yield_db_session),
) -> data.DropUpdatedResponse:

    """
    Activate a given drop by drop id.
    """
    try:
        actions.ensure_admin_token_holder(
            db_session, dropper_claim_id, request.state.address
        )
    except actions.AuthorizationError as e:
        logger.error(e)
        raise DropperHTTPException(status_code=403)
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="Drop not found")

    try:
        drop = actions.deactivate_drop(
            db_session=db_session,
            dropper_claim_id=dropper_claim_id,
        )
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="Drop not found")
    except Exception as e:
        logger.error(f"Can't activate drop: {e}")
        raise DropperHTTPException(status_code=500, detail="Can't activate drop")

    return data.DropUpdatedResponse(
        dropper_claim_id=drop.id,
        dropper_contract_id=drop.dropper_contract_id,
        title=drop.title,
        description=drop.description,
        claim_block_deadline=drop.claim_block_deadline,
        terminus_address=drop.terminus_address,
        terminus_pool_id=drop.terminus_pool_id,
        claim_id=drop.claim_id,
        active=drop.active,
    )


@router.put("/claims/{dropper_claim_id}", response_model=data.DropUpdatedResponse)
async def update_drop(
    request: Request,
    dropper_claim_id: UUID,
    update_request: data.DropUpdateRequest = Body(...),
    db_session: Session = Depends(db.yield_db_session),
) -> data.DropUpdatedResponse:

    """
    Update a given drop by drop id.
    """
    try:
        actions.ensure_admin_token_holder(
            db_session, dropper_claim_id, request.state.address
        )
    except actions.AuthorizationError as e:
        logger.error(e)
        raise DropperHTTPException(status_code=403)
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="Drop not found")

    try:
        drop = actions.update_drop(
            db_session=db_session,
            dropper_claim_id=dropper_claim_id,
            title=update_request.title,
            description=update_request.description,
            claim_block_deadline=update_request.claim_block_deadline,
            terminus_address=update_request.terminus_address,
            terminus_pool_id=update_request.terminus_pool_id,
            claim_id=update_request.claim_id,
            address=request.state.address,
        )
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="Drop not found")
    except Exception as e:
        logger.error(f"Can't update drop: {e}")
        raise DropperHTTPException(status_code=500, detail="Can't update drop")

    return data.DropUpdatedResponse(
        dropper_claim_id=drop.id,
        dropper_contract_id=drop.dropper_contract_id,
        title=drop.title,
        description=drop.description,
        claim_block_deadline=drop.claim_block_deadline,
        terminus_address=drop.terminus_address,
        terminus_pool_id=drop.terminus_pool_id,
        claim_id=drop.claim_id,
        active=drop.active,
    )


@router.get("/claimants", response_model=data.DropListResponse)
async def get_claimants(
    request: Request,
    dropper_claim_id: UUID,
    limit: int = 10,
    offset: int = 0,
    db_session: Session = Depends(db.yield_db_session),
) -> data.DropListResponse:
    """
    Get list of claimants for a given dropper contract.
    """

    try:
        actions.ensure_admin_token_holder(
            db_session, dropper_claim_id, request.state.address
        )
    except actions.AuthorizationError as e:
        logger.error(e)
        raise DropperHTTPException(status_code=403)
    except Exception as e:
        logger.error(e)
        raise DropperHTTPException(status_code=500)

    try:
        results = actions.get_claimants(
            db_session=db_session,
            dropper_claim_id=dropper_claim_id,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        logger.info(f"Can't add claimants for claim {dropper_claim_id} with error: {e}")
        raise DropperHTTPException(status_code=500, detail=f"Error adding claimants")

    return data.DropListResponse(drops=list(results))


@router.post("/claimants", response_model=data.ClaimantsResponse)
async def add_claimants(
    request: Request,
    add_claimants_request: data.DropAddClaimantsRequest = Body(...),
    db_session: Session = Depends(db.yield_db_session),
) -> data.ClaimantsResponse:
    """
    Add addresses to particular claim
    """

    try:
        actions.ensure_admin_token_holder(
            db_session, add_claimants_request.dropper_claim_id, request.state.address
        )
    except actions.AuthorizationError as e:
        logger.error(e)
        raise DropperHTTPException(status_code=403)
    except Exception as e:
        logger.error(e)
        raise DropperHTTPException(status_code=500)

    try:
        results = actions.add_claimants(
            db_session=db_session,
            dropper_claim_id=add_claimants_request.dropper_claim_id,
            claimants=add_claimants_request.claimants,
            added_by=request.state.address,
        )
    except Exception as e:
        logger.info(
            f"Can't add claimants for claim {add_claimants_request.dropper_claim_id} with error: {e}"
        )
        raise DropperHTTPException(status_code=500, detail=f"Error adding claimants")

    return data.ClaimantsResponse(claimants=results)


@router.delete("/claimants", response_model=data.RemoveClaimantsResponse)
async def delete_claimants(
    request: Request,
    remove_claimants_request: data.DropRemoveClaimantsRequest = Body(...),
    db_session: Session = Depends(db.yield_db_session),
) -> data.RemoveClaimantsResponse:

    """
    Remove addresses to particular claim
    """

    try:
        actions.ensure_admin_token_holder(
            db_session,
            remove_claimants_request.dropper_claim_id,
            request.state.address,
        )
    except actions.AuthorizationError as e:
        logger.error(e)
        raise DropperHTTPException(status_code=403)
    except Exception as e:
        logger.error(e)
        raise DropperHTTPException(status_code=500)

    try:
        results = actions.delete_claimants(
            db_session=db_session,
            dropper_claim_id=remove_claimants_request.dropper_claim_id,
            addresses=remove_claimants_request.addresses,
        )
    except Exception as e:
        logger.info(
            f"Can't remove claimants for claim {remove_claimants_request.dropper_claim_id} with error: {e}"
        )
        raise DropperHTTPException(status_code=500, detail=f"Error removing claimants")

    return data.RemoveClaimantsResponse(addresses=results)
