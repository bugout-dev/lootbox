import { useQuery } from "react-query";
import { getClaim } from "../services/moonstream-engine.service";
import { queryCacheProps } from "./hookCommon";

const useClaimant = ({ dropId, claimantAddress }) => {
  console.log("useClaimant dropId", dropId);
  const claim = useQuery(
    ["claim", dropId, claimantAddress],
    async () => {
      const result = await getClaim(dropId, claimantAddress);
      return result.data;
    },
    {
      ...queryCacheProps,
      cacheTime: 0,
      enabled: !!dropId && !!claimantAddress,
    }
  );

  return { claim };
};

export default useClaimant;
