# First run (real money)

1. Create bot via @BotFather, put token into `.env`.
2. Register at Platega, get MerchantId + Secret, set callback URL to  
   `https://your-domain{PLATEGA_WEBHOOK_PATH}`.
3. Create a **dedicated** TON wallet (not your main funds). Fund with a small amount (e.g. 2–5 TON).
4. Prepare a Fragment account linked to that wallet. Export cookies (Cookie-Editor → Header string).  
   Update cookies via admin command later; never commit them.
5. Set `USE_POLLING=false`, configure HTTPS reverse proxy, set `WEBHOOK_HOST`.
6. Run migrations, start bot + worker.
7. Place a **50 Stars** order to yourself. Watch logs and Platega / Fragment / blockchain explorers.
8. Only after a successful end-to-end test increase limits / markup.

**Never** paste a real mnemonic into chat or logs.
