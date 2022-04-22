import React, { useContext } from "react";
import { Flex, Button, Image, Center, Spinner } from "@chakra-ui/react";
import { DEFAULT_METATAGS } from "../src/core/constants";
import Web3Context from "../src/core/providers/Web3Provider/context";
// import { getLayout } from "../src/layouts/AppLayout";
import useDropper from "../src/core/hooks/useDropper";
import { targetChain } from "../src/core/providers/Web3Provider";
const assets: any = {
  onboarding:
    "https://s3.amazonaws.com/static.simiotics.com/unicorn_bazaar/unim-onboarding.png",
};
import DropList from "../src/components/DropList";

const Homepage = () => {
  const web3Provider = useContext(Web3Context);



  if(web3Provider.account == '') return <Spinner />

  console.log("web3Provider.account", web3Provider.account)
  console.log(web3Provider)

  const dropper = useDropper({dropperAddress: process.env.NEXT_PUBLIC_DROPPER_ADDRESS ?? "",
   targetChain: targetChain,
    blockchain: process.env.NEXT_PUBLIC_BLOCKCHAIN ?? "",
     dropperContractID: process.env.NEXT_PUBLIC_DROPPER_CONTRACT_ID ?? "",
      dropperClaimId: process.env.NEXT_PUBLIC_DROPPER_CLAIM_ID ?? "",
       ctx: web3Provider});


  if(dropper.dropperWeb3State.isLoading || dropper.usersDropList.isLoading) return <Spinner />


  return (
    <Flex w="100%" minH="100vh" bgColor={"blue.1200"} direction={"column"}>
      {web3Provider.account && <DropList drops={dropper.usersDropList.data}  />}
      {!web3Provider.account &&
        web3Provider.buttonText !== web3Provider.WALLET_STATES.CONNECTED && (
          <Center>
            <Button
              mt={20}
              colorScheme={
                web3Provider.buttonText === web3Provider.WALLET_STATES.CONNECTED
                  ? "orange"
                  : "orange"
              }
              onClick={web3Provider.onConnectWalletClick}
            >
              {web3Provider.buttonText}
              {"  "}
              <Image
                pl={2}
                h="24px"
                src="https://raw.githubusercontent.com/MetaMask/brand-resources/master/SVG/metamask-fox.svg"
              />
            </Button>
          </Center>
        )}
    </Flex>
  );
};

interface Preconnect {
  rel: string;
  href: string;
  as?: string;
}

// Homepage.getLayout = getLayout;

export async function getStaticProps() {
  const assetPreload: Array<Preconnect> = assets
    ? Object.keys(assets).map((key) => {
        return {
          rel: "preload",
          href: assets[key],
          as: "image",
        };
      })
    : [];
  const preconnects: Array<Preconnect> = [
    { rel: "preconnect", href: "https://s3.amazonaws.com" },
  ];

  const preloads = assetPreload.concat(preconnects);

  return {
    props: { metaTags: DEFAULT_METATAGS, preloads },
  };
}

export default Homepage;
