# APR for NEAR-WETH pool on auroraswap
 By Aleksei Rutkovskii for https://www.multifarm.fi/

### About
Entire process can be automated and calculated fully programmatically, but here I went for simplicity

Also, my results are more accurate than the ones provided by vfat because in his calculations the underlying assumption
was that one block is created in 1.1 second, but in reality `blocks_per_day` prints the accurate time to create a block.

### Files

* main.py — to run on in the terminal by typing `python3 main.py`
* flaskMain.py — to run a flask server on local network by typing `python3 flaskMain.py`
* functions.py — contains all functions used in flaskMain.py
* auroraswap.py — constains all coin ids, abis, adresses
* scratch/scratch.py — first functioning version
 

Links: 
1. [Address of NEAR-WETH pool](https://explorer.mainnet.aurora.dev/address/0x35CC71888DBb9FfB777337324a4A60fdBAA19DDE/read-contract)
2. [LP_ABI](https://bscscan.com/address/0xa9ae4e4b41145e09fcd6a1c171e8297de228ef9d#code)
3. [vfat.tools](https://vfat.tools/aurora/auroraswap/)
4. [vfat Github](https://github.com/vfat-tools/vfat-tools/blob/master/src/static/js/aurora_auroraswap.js)