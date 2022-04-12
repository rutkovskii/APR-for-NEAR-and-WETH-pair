from web3 import Web3
import json
import time
import requests


def get_estimated_blocks_per_day(client, last_n_blocks=10000):
    '''
    Computes blocks/day

    :param client: instance of Web3
    :param last_n_blocks: range size
    :type last_n_blocks: int
    :return: blocks/day
    :rtype: float
    '''
    now = int(time.time())
    current_block = client.eth.get_block_number()
    n_blocks_ago = current_block - last_n_blocks
    n_blocks_ago = max(n_blocks_ago, 500)
    first_block = client.eth.get_block(n_blocks_ago)
    return last_n_blocks / (now - first_block.timestamp) * 60 * 60 * 24


def blocks_per_day(last_n_blocks=10000):
    '''
    Caller function to get and print blocks/day

    :param last_n_blocks: range size
    :type last_n_blocks: int
    :return: blocks/day
    :rtype: float
    '''
    blocks_per_day = get_estimated_blocks_per_day(w3, last_n_blocks)
    print(f"Avg Block Time = {1 / blocks_per_day * 60 * 60 * 24:.2f}s")
    return blocks_per_day


def get_price(coin_id):
    """
    Gets price of a particular coin from Coingecko

    :param coin_id:
    :type coin_id: str
    :return: coin price
    :rtype: float
    """
    coingecko_url = f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd'
    response = requests.get(coingecko_url)
    return response.json()[coin_id]['usd']


def web3_connector(net_url):
    """
    Connecting to a Blockchain net

    :param net_url: url to blockchain
    :type net_url: str
    :return: w3
    :rtype: object
    """
    w3 = Web3(Web3.HTTPProvider(net_url))
    res = w3.isConnected()
    print(f'web3 connected: {res}')
    return w3


def contract_initiator(client,abi_raw, address_raw):
    """
    Instantiate smart contract

    :param abi_raw: abi of smart contract
    :type abi_raw: str
    :param address_raw: address of smart contract
    :type address_raw: str
    :return: contract
    :rtype: object
    """
    abi = json.loads(abi_raw)
    address = client.toChecksumAddress(address_raw)
    contract = client.eth.contract(address=address, abi=abi)
    return contract

def rewards_per_year(coins_per_block,coin_price,reward_percent):
    """
    Computes rewards/year

    :param coins_per_block: coins/block
    :type coins_per_block: int
    :param coin_price: coin price
    :type coin_price: float
    :param reward_percent:
    :type reward_percent: float
    :return: rewards_per_year
    :rtype: float
    """
    rewards_per_year = coins_per_block / 1e18 * coin_price * reward_percent * blocks_per_day() * 365
    print(f'rewards_per_year\t{rewards_per_year:.2f} $')
    return rewards_per_year

def rewards_per_year_vfat(coins_per_block,coin_price,reward_percent):
    """
    Computes rewards/year

    :param coins_per_block: coins/block
    :type coins_per_block: int
    :param coin_price: coin price
    :type coin_price: float
    :param reward_percent:
    :type reward_percent: float
    :return: rewards_per_year_vfat
    :rtype: float
    """
    rewards_per_year_vfat = coins_per_block / 1e18 * coin_price * reward_percent * (60 * 60 * 24 / 1.1) * 365
    print(f'rewards_per_year_vfat\t{rewards_per_year_vfat:.2f} $')
    return rewards_per_year_vfat


def staked_usd(lp_staked,eth_per_lp):
    """
    Computes staked value in the usd

    :param lp_staked: stacked balance in liquid pool
    :type lp_staked: float
    :param eth_per_lp: ethereum in the liquid pool
    :type eth_per_lp: float
    :return: staked_value_in_usd
    :rtype: float
    """
    # each lp token is worth that much ETH + an equivalent amount of NEAR
    staked_value_in_eth = lp_staked * eth_per_lp * 2
    staked_value_in_usd = staked_value_in_eth * ETH_price
    print(f'staked_value_in_usd\t{staked_value_in_usd:.2f} $')
    return staked_value_in_usd

def find_APR(rewards_per_year,staked_value_in_usd):
    """
    Calculates APR based on the current data

    :param rewards_per_year: approximate rewards in usd in a year
    :type rewards_per_year: float
    :param staked_value_in_usd: staked value in the usd
    :type staked_value_in_usd: float
    :return: APR
    :rtype: float
    """
    APR = rewards_per_year / staked_value_in_usd * 100
    return APR


if __name__ == '__main__':
    import auroraswap

    net = 'https://mainnet.aurora.dev'
    w3 = web3_connector(net)

    # Instance of Auroraswap Contract
    contract = contract_initiator(client=w3,abi_raw=auroraswap.auroraswap_abi,address_raw=auroraswap.auroraswap_address)

    BRL_price = get_price(auroraswap.BRL_id)
    BRLPerBlock = contract.functions.BRLPerBlock().call()

    # NEAR-WETH pool info
    pool_id = 1 # corresponds to NEAR-WETH
    pool_info = contract.functions.poolInfo(pool_id).call()
    totalAllocPoint = contract.functions.totalAllocPoint().call()
    reward_percent = pool_info[1] / totalAllocPoint
    print(f"Pool {pool_id} alloc points = {pool_info[1]} = {reward_percent * 100:.2f}% of rewards")

    # rewards per year
    rewards_per_year = rewards_per_year(BRLPerBlock,BRL_price,reward_percent)
    rewards_per_year_vfat = rewards_per_year_vfat(BRLPerBlock, BRL_price, reward_percent)

    lp_contract = contract_initiator(client=w3,abi_raw=auroraswap.NEAR_WETH_abi,address_raw=pool_info[0])
    #print(dir(lp_contract.functions))

    # Balance of BRLMasterchef
    lp_staked = lp_contract.functions.balanceOf(contract.address).call() / 1e18
    print(f'lp_staked\t\t{lp_staked:.4f} Aurora-LP')

    # Programmatically finding a general solution is harder, but right now only NEAR-WETH pool is needed
    # So I can get just ETH/lp and multiply by the price of ETH.
    # The lp token is NEAR/WETH so WETH is the 2nd token on the reserves
    eth_per_lp = lp_contract.functions.getReserves().call()[1] / lp_contract.functions.totalSupply().call()
    ETH_price = get_price(auroraswap.ETH_id)

    staked_usd = staked_usd(lp_staked, eth_per_lp)

    APR = find_APR(rewards_per_year,staked_usd)
    APR_vfat = find_APR(rewards_per_year_vfat,staked_usd)

    print(f'APR\t\t\t{APR:.2f} %')
    print(f'APR_vfat\t\t{APR_vfat:.2f} %')



