# Resilience Notes

This project handles wallet purchases and rewards with a few simple safeguards.

## Duplicate requests
The same `Idempotency-Key` returns the same stored response instead of running the action twice.
If the same key is reused with different data, the request is rejected.

## Concurrent purchases
The wallet row is locked with `select_for_update()` inside `transaction.atomic()`, so two requests cannot spend the same balance at the same time.

## Atomic updates
Balance changes, transaction records, and idempotency records are written in one database transaction.
Either everything succeeds or nothing is saved.

## Rollbacks
If validation fails, Django rolls back the transaction automatically.
That prevents partial updates like a saved balance change without a matching transaction record.

## Price validation
The purchase flow checks the client price against the current server price from the shop item.
If they do not match, the request is rejected.

## Double spending prevention
The wallet balance is checked after the row lock is acquired and before the debit happens.
This stops two overlapping purchases from using the same funds twice.

## Idempotency
Each successful request stores a hash of the payload plus the response for 24 hours.
That makes retries safe and keeps repeated requests consistent.