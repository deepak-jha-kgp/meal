<p align="center">
  <img src="./docs/social-preview.jpg" alt="Meal — say what you ate, see the pattern, choose one next move." width="100%"/>
</p>

<p align="center">
  <a href="https://lemma.work/import/github/deepak-jha-kgp/meal"><img alt="Run on Lemma" src="https://img.shields.io/badge/Run_on_Lemma-111111?style=for-the-badge"></a>
  <a href="https://github.com/deepak-jha-kgp/meal/fork"><img alt="Fork and make it yours" src="https://img.shields.io/badge/Fork_and_make_it_yours-F4F1EA?style=for-the-badge&amp;logo=github&amp;logoColor=111111"></a>
</p>

<p align="center">A food journal that accepts ordinary meal descriptions and turns them into a useful daily picture.</p>

## Why it exists

Most food trackers ask for the exact ingredient, brand, weight, and serving size before they will save anything. Real meals are remembered as “two rotis and some dal” or “the usual sandwich.”

Meal accepts that ordinary language. It records what it knows, shows where it is unsure, and gives you a calm view of the day rather than pretending every estimate is exact.

## What it does

- Log a meal by describing it in Telegram as you normally would.
- Keep the original words alongside the interpreted foods and portions.
- Show confidence signals when the description leaves room for doubt.
- Update the day's nutrition totals after each meal.
- Offer one useful next move instead of a stream of warnings.

## What a normal use looks like

You message “paneer wrap and coffee” after lunch. Meal records the phrase, makes a reasonable estimate, and marks the uncertain parts. The daily view updates, and you can correct the meal later if the estimate was off.

## How it is built on Lemma

This repository contains the pod itself, not just a screenshot or a prompt. The interface and the parts that do the work are installed together.

- `surfaces/telegram/` — The low-friction place to log a meal.
- `tables/` — Meals, foods, interpreted signals, daily totals, and review triggers.
- `agents/meal-logger-agent/` — The instructions for reading an ordinary meal description without inventing certainty.
- `functions/` — Record a meal and review it through checked writes.
- `schedules/` — Start the review when a meal is added.
- `apps/meal-tracker-app/` — The daily view for totals, confidence, and corrections.

The files in this repo contain the structure and instructions. Your private records, connected accounts, credentials, and deployed URLs are added after import.

## Run it on Lemma

<p>
  <a href="https://lemma.work/import/github/deepak-jha-kgp/meal"><img alt="Run on Lemma" src="https://img.shields.io/badge/Run_on_Lemma-111111?style=for-the-badge"></a>
</p>

The button opens Lemma's import flow for this exact GitHub repository:

`https://lemma.work/import/github/deepak-jha-kgp/meal`

Connect your Telegram bot, describe one real meal, and check the interpretation in the app. No health history, meal data, or bot token is included.

<details>
<summary>Import from the command line</summary>

```bash
git clone https://github.com/deepak-jha-kgp/meal.git
cd meal

lemma pods import . --dry-run
lemma pods import .
```

</details>

## Make it yours

You do not need to keep this pod exactly as it is.

1. [Fork the repository](https://github.com/deepak-jha-kgp/meal/fork).
2. Change the instructions, app, tables, or rules for the way you work.
3. Import your fork with `https://lemma.work/import/github/<your-github-name>/<your-repo>`.
4. When it is useful, [show your version here](https://github.com/deepak-jha-kgp/meal/issues/new?template=show-your-version.yml&title=%5BRemix%5D+) with one screenshot and a short note about what changed.

If this pod saved you from rebuilding the same thing, star the repo so the useful versions are easier to find.

## Repository guide

- [Implementation notes](./docs/implementation-notes.md)
- [Social preview](./docs/social-preview.jpg)
- [Contributing](./CONTRIBUTING.md)
- [Security](./SECURITY.md)

## Share

<p>
  <a href="https://twitter.com/intent/tweet?text=Meal%3A%20A%20food%20journal%20that%20accepts%20ordinary%20meal%20descriptions%20and%20turns%20them%20into%20a%20useful%20daily%20picture.&amp;url=https%3A%2F%2Fgithub.com%2Fdeepak-jha-kgp%2Fmeal"><img alt="Share on X" src="https://img.shields.io/badge/Share_on_X-111111?style=for-the-badge&amp;logo=x"></a>
  <a href="https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fgithub.com%2Fdeepak-jha-kgp%2Fmeal"><img alt="Share on LinkedIn" src="https://img.shields.io/badge/Share_on_LinkedIn-0A66C2?style=for-the-badge&amp;logo=linkedin"></a>
  <a href="https://bsky.app/intent/compose?text=Meal%3A%20A%20food%20journal%20that%20accepts%20ordinary%20meal%20descriptions%20and%20turns%20them%20into%20a%20useful%20daily%20picture.%20https%3A%2F%2Fgithub.com%2Fdeepak-jha-kgp%2Fmeal"><img alt="Share on Bluesky" src="https://img.shields.io/badge/Share_on_Bluesky-1185FE?style=for-the-badge&amp;logo=bluesky&amp;logoColor=white"></a>
</p>
