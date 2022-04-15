import React, { useContext } from "react";
import Web3Context from "../providers/Web3Provider/context";
import BN from "bn.js";
import { getDropList, getDropMessage } from "../services/dropper.service";
import queryCacheProps from "./hookCommon";
import { useMutation, useQuery, UseQueryResult } from "react-query";
import { getState } from "../contracts/dropper.contract";
import DataContext from "../providers/DataProvider/context";
import { ReactWeb3ProviderInterface } from "../../../types/Moonstream";

const useDropper = ({
  dropperAddress,
  targetChain,
  ctx,
}: {
  dropperAddress: string;
  targetChain: any;
  ctx: ReactWeb3ProviderInterface;
}) => {
  const dropperWeb3State = useQuery(
    ["dropperContractState", dropperAddress, targetChain.chainId],
    () => getState(dropperAddress, ctx)(),
    {
      onSuccess: () => {},
      enabled:
        ctx.web3?.utils.isAddress(ctx.account) && ctx.chainId === ctx.chainId,
    }
  );

  const dropList = useQuery(
    ["dropList", dropperAddress, targetChain.chainId],
    () => getDropList(dropperAddress, 1)().then((data) => data.data.drops),
    {
      onSuccess: () => {},
    }
  );

  // const [usersDropList, setUsersDropList] = React.useState<Array<any>>([]);

  let usersDropList: any = {};
  usersDropList['data'] = React.useMemo((): any => {
    const retval: Array<any> = [];
    if (dropList?.data && ctx.account) {
      const _usersDropList: any = [];
      dropList.data.forEach((entry: any, id: Number) => {
        if (entry.content.includes(ctx.account)) {
          const claimIdtag = entry.tags.find((tag: string) =>
            tag.startsWith("claim_id:")
          );
          id = claimIdtag.split(":")[1];
          retval.push({ id, entry });
        }
      });
    }
    return retval;
  }, [dropList.data, ctx.account]);

  usersDropList.isLoading = dropList.isLoading;
  usersDropList.error = dropList.error;
  usersDropList.status = dropList.status;


  return { dropperWeb3State, usersDropList };
};

export default useDropper;
