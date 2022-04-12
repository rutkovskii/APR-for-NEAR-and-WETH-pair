from flask import Flask
import auroraswap
import functions as f


app = Flask(__name__)

@app.route('/')
def welcome():
    return 'Type /aurora/auroraswap/near-weth next to the local host to get APR for NEAR-WETH pool'

@app.route('/aurora/auroraswap/near-weth')
def serve_apr():
    net = 'https://mainnet.aurora.dev'
    w3 = f.web3_connector(net)

    # Instance of Auroraswap Contract
    contract = f.contract_initiator(client=w3, abi_raw=auroraswap.auroraswap_abi,
                                  address_raw=auroraswap.auroraswap_address)

    BRL_price = f.get_price(auroraswap.BRL_id)
    BRLPerBlock = contract.functions.BRLPerBlock().call()

    # NEAR-WETH pool info
    pool_id = 1  # corresponds to NEAR-WETH
    pool_info = contract.functions.poolInfo(pool_id).call()
    totalAllocPoint = contract.functions.totalAllocPoint().call()
    reward_percent = pool_info[1] / totalAllocPoint
    print(f"Pool {pool_id} alloc points = {pool_info[1]} = {reward_percent * 100:.2f}% of rewards")

    # rewards per year
    rewards_per_year = f.rewards_per_year(w3,BRLPerBlock, BRL_price, reward_percent)
    rewards_per_year_vfat = f.rewards_per_year_vfat(BRLPerBlock, BRL_price, reward_percent)

    lp_contract = f.contract_initiator(client=w3,abi_raw=auroraswap.NEAR_WETH_abi, address_raw=pool_info[0])
    # print(dir(lp_contract.functions))

    # Balance of BRLMasterchef
    lp_staked = lp_contract.functions.balanceOf(contract.address).call() / 1e18
    print(f'lp_staked\t\t{lp_staked:.4f} Aurora-LP')

    # Programmatically finding a general solution is harder, but right now only NEAR-WETH pool is needed
    # So I can get just ETH/lp and multiply by the price of ETH.
    # The lp token is NEAR/WETH so WETH is the 2nd token on the reserves
    eth_per_lp = lp_contract.functions.getReserves().call()[1] / lp_contract.functions.totalSupply().call()
    ETH_price = f.get_price(auroraswap.ETH_id)

    staked_usd = f.staked_usd(lp_staked, eth_per_lp,ETH_price)

    APR = f.find_APR(rewards_per_year, staked_usd)
    APR_vfat = f.find_APR(rewards_per_year_vfat, staked_usd)

    print(f'APR\t\t\t{APR:.2f} %')
    print(f'APR_vfat\t\t{APR_vfat:.2f} %')

    return {'APR':APR,'APR_vfat':APR_vfat}

if __name__ == '__main__':
    app.run(port='8080', debug=False)
