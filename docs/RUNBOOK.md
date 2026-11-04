# Runbook

## Expired Fragment cookies / SessionExpired

1. Log into fragment.com in a browser with the dedicated account.
2. Export cookies (Header string).
3. Use admin command to update cookies (message is deleted after processing).
4. Confirm `healthcheck` becomes ok; worker will resume paid orders.

## Low TON balance

1. Alert fires when balance is insufficient for next quote.
2. Maintenance mode activates for **new** orders; already paid orders stay in queue.
3. Top up the wallet, then disable maintenance.

## Order in `manual_review`

1. Open admin → find order by id / username.
2. Inspect events + Platega status + on-chain tx if any.
3. Actions: Confirm delivery / Retry fulfillment / Refund to internal balance.

## Platega callback missing

Worker/background job re-checks `awaiting_payment` orders every minute via `GET /transaction/{id}`.

## Double-spend / crash after broadcast

Worker **never** re-sends a transaction if `fragment_ref_id` or `ton_tx_hash` is already set.  
It verifies on-chain / Fragment state first. Ambiguous outcome → `manual_review` + admin alert.
