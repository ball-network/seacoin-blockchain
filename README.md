# seacoin-blockchain

SeaCoin Website: https://seacoin.vip

Full Node Port: 30000

## How to staking

1. Query the staking balance:

   ```
   $ sea staking info
   ...
   Staking balance:  0
   Staking address:  xsea1lnvsnstgtpg20c6pufryq6hv08jchj0vpvymq2zzm65lze3f87aq040ux3
   ...
   ```

2. Send coins to the staking:

   ```
   $ sea staking send -a 1
   ```

   Wait for the transaction get confirmed, query staking balance again:

   ```
   $ sea staking info
   ...
   Staking balance:  1
   Staking address:  xsea1lnvsnstgtpg20c6pufryq6hv08jchj0vpvymq2zzm65lze3f87aq040ux3
   ...
   ```

3. Withdraw coins from the staking address:

   ```
   $ sea staking withdraw -a 1
   ```

   Do a transaction to transfer the coins from the staking address to now wallet receive address.