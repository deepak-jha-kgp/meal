# Meal implementation notes

# Meal

First-class Lemma app for the sentence: “Remember what I ate.”

Meal accepts food language or a photo caption in Telegram and quick structured
entries in the single-page app. `log_meal` owns the canonical write, daily
nutrition rollup, and an isolated trigger. The trigger wakes a specialist that
materializes a gentle balance review, confidence/attention state, and one useful
next move.

## Intended live surfaces

- App: <https://meal.apps.lemma.work>
- Telegram: `@lemma_meal_bot`

Bot credentials remain deployment secrets.

## Durable resources

- `meals`: private meal journal and materialized review.
- `foods`: shared nutrition reference catalog.
- `daily_nutrition`: private, chart-ready day rollup.
- `meal_signals`: private, sparse nutrition and confidence signals.
- `meal_triggers`: isolated wake-up queue.
- `log_meal`: idempotent intake and daily aggregation.
- `review_meal`: idempotent background review and trigger completion.
- `review-on-meal`: DATASTORE schedule bound only to `meal_triggers`.

## Import and verify

```bash
lemma --server cloud --pod meal-tracker pods import ./meal-tracker --dry-run
lemma --server cloud --pod meal-tracker pods import ./meal-tracker
lemma --server cloud pods doctor meal-tracker
```

Deterministic smoke:

```bash
lemma --server cloud --pod meal-tracker functions run log_meal \
  --file ./meal-tracker/payloads/log_meal.input.json
```

Copy the returned meal and trigger ids into
`payloads/review_meal.input.json` to exercise `review_meal` directly. Replaying
the log payload is safe because it carries a `dedupe_key`.
