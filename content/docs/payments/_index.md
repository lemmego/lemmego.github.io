---
title: Payments
type: docs
prev: docs/seo/
next: docs/appendix/
sidebar:
  open: true
weight: 61
---

## Overview

`lemmego/pay` is subscription billing: one hosted checkout, one signed
webhook, and a verified-revenue reader that is deliberately a separate
authorisation.

```go
&pay.Provider{
    Gateway: stripe.New(stripe.Config{
        SecretKey: config.MustEnv("STRIPE_SECRET_KEY", ""),
    }),
    Store:   func(a app.App) pay.Store { return billing.NewStore(a) },
    Secrets: []string{config.MustEnv("STRIPE_WEBHOOK_SECRET", "")},
}

r.Post("/webhooks/stripe", pay.WebhookHandler())
```

```bash
go get github.com/lemmego/pay
```

## Three mistakes this package exists to prevent

The expensive mistakes in billing are not in the API calls — they are in what
the application believes afterwards.

**1. Entitlement comes from the webhook, never from the redirect.** A browser
returning to a success URL proves only that a browser was sent there: the
person can close the tab, the redirect can be lost, and the URL can be visited
again tomorrow by anyone who remembers it. The webhook is signed, retried
until acknowledged, and is the only thing `Handle` will write from.

**2. A delivery arrives more than once, and out of order.** Stripe retries
until it gets a 2xx and promises no ordering at all. So `Store.Seen`
deduplicates on the event id, and `Store.Apply` has to let an older event lose
against a newer one — **as a condition on the write, not a read followed by a
write.** A read-then-write guard has a window exactly wide enough to lose the
newer event.

**3. A signature is checked over the exact bytes received**, with the timestamp
inside the MAC and a tolerance around it. Without the tolerance a captured
signature is valid forever; without the raw bytes the check passes only by
luck, since decoding and re-encoding the same JSON changes the signature.

{{< callout type="info" >}}
**With no `Gateway`, every paid path refuses with `ErrNoGateway` and the rest
of the application runs.** An application whose home page will not render
without Stripe credentials is one nobody can contribute to.
{{< /callout >}}

`Livemode` is derived from the gateway when unset, which is strictly better
than configuring it: a flag that can disagree with the key in use eventually
does, and the failure is a test-mode event granting a real subscription.

## Money is an integer, always

```go
type Money struct {
    Amount   int64  // in the currency's smallest unit
    Currency string
}
```

Never a float. A `float64` holds `0.1` as
`0.1000000000000000055511151231257827`, and a sum of a few thousand
subscription amounts drifts by enough to show the wrong figure — which for a
badge calling itself *verified* is the whole value gone.

{{< callout type="warning" >}}
**`Factor(currency)` is not a nicety.** Stripe reports a ¥5,000 subscription as
`5000`, not `500000`, so dividing by 100 gives ¥50 — wrong by two orders of
magnitude, in the direction that makes a Japanese founder's revenue look like a
rounding error.
{{< /callout >}}

```go
m.Major()            // whole units, truncated
m.Add(other)         // refuses mixed currency: ErrMixedCurrency
m.Sub(other)         // floors at zero
m.DivRound(n)        // rounds half away from zero
m.Percent(17.5)
```

There is **no exchange rate in this module and there should not be**: a rate is
a time-varying external fact, and a revenue figure that silently depends on one
is not verifiable by the person reading it.

## Status, and the two questions you ask of it

```go
s.Status.Entitling()   // active, trialing — may they use the feature?
s.Status.Earning()     // active, past_due — does this count as revenue?
```

They differ on `past_due` on purpose. Somebody whose card just failed is still
a paying customer for the purposes of a revenue figure, and should be nudged
rather than cut off mid-sentence; entitlement is the stricter question.

## A grace period, not a cliff

```go
const pay.GracePeriod = 48 * time.Hour
```

A missed renewal webhook — a deploy during a delivery, a 500 from your own
handler — should cost two days of grace, not revoke a paying customer's access.

```go
func (u *User) ProActive() bool {
    if !u.IsPro {
        return false
    }
    if u.ProUntil == nil {
        return true
    }
    return time.Now().UTC().Before(u.ProUntil.Add(pay.GracePeriod))
}
```

The inverse mistake is worse: granting Pro forever because no webhook ever
arrived to take it away.

## The webhook

| Outcome | Status | Why |
|---|---|---|
| Verified and applied | 200 | |
| Already seen | 200 | A retry must do nothing, and must not be retried again |
| Event this app ignores | 200 | Acknowledged, not an error |
| Bad signature | **400** | Not 500 — nothing to retry |
| Store failed | **500** | So Stripe retries. Never acknowledge a write that did not happen |
| Test-mode event in live mode | refused | A free subscription otherwise |

Exempt the route from CSRF, and write the reason next to the exemption — the
request is signed, which is a stronger check than a CSRF token, and Stripe
cannot send one.

## `Store` is yours to implement

```go
type Store interface {
    Seen(ctx Context, event *Event) (first bool, err error)
    Apply(ctx Context, event *Event) error
}
```

`Seen` is **a unique index on the event id and nothing cleverer**.

`Apply` is one statement:

```sql
INSERT INTO subscriptions (…, event_at) VALUES (…)
ON CONFLICT (id) DO UPDATE SET …, event_at = excluded.event_at
WHERE excluded.event_at >= subscriptions.event_at
```

The `WHERE` on the `DO UPDATE` is the whole point: it is the guard, applied by
the database, with no window.

## Verified revenue is a separate interface

`RevenueReader` is **not** part of `Gateway`, deliberately: charging a customer
and reading a founder's books are different authorisations with different blast
radii, and an application should be able to do the first without being able to
do the second.

```go
revenue := paystripe.NewRevenue(gateway, clientID, clientSecret)
url, err := revenue.AuthorizeURL(state, redirectURI)   // read_only; state required
account, err := revenue.Exchange(ctx, code)            // stores only the account id
total, err := pay.Total(ctx, revenue, account, time.Now())
```

Connect is asked for `read_only` and **the returned scope is checked**, not
assumed. No access token is stored — only the account id.

### Bands, not figures

```go
band, ok := pay.BandFor(total.Monthly)
```

The ladder is coarse at the bottom and open at the top, because the interesting
distinction for a reader is the order of magnitude — and **a ladder fine enough
to separate $4,900 from $5,100 is a ladder that reveals the figure it was meant
to hide.** Somebody's exact MRR plus a public plan price is their customer
count.

`ok` is false for a currency the dollar ladder does not cover, and for no
revenue at all. **Do not treat that as the bottom band**: "no revenue verified"
and "under $100" are different claims, and only one of them is about money.

{{< callout type="warning" >}}
If you publish a leaderboard, order by band and then by who verified first,
never by amount. Ordering within a band publishes an ordering finer than the
band.
{{< /callout >}}

## Testing without a network

```go
gateway := paytest.New("whsec_test")
payload := gateway.Event("evt_1", "customer.subscription.updated", now, sub, "user_42")
signature := gateway.Sign(payload, now)

err := billing.Handle(ctx, payload, signature)
```

`paytest.Gateway` **verifies with the same code the real driver uses**, so a
test that passes against the fake is a test of the real signature scheme. It
records `Checkouts()` and `Portals()` so you can assert on what would have been
sent.

## Deliberate omissions

No refunds, invoices, metered usage, tax, one-off charges, a cancel flow of our
own, or any local copy of a price. Each is either the gateway's hosted page
doing a better job than we would, or a Stripe endpoint whose presence here
would make the interface Stripe-shaped.

Read the price from the gateway rather than mirroring it in an env var. Two
copies of a price disagree eventually, and the one your checkout uses is not the
one your pricing page shows.
