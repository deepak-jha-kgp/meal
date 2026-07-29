#!/usr/bin/env bash
# seed/seed.sh — load sample foods + a day of meals so the app demos itself.
# Run after `lemma pods import`. Targets the active pod (or pass --pod meal-tracker).
set -uo pipefail
POD="${POD:-meal-tracker}"
LEMA="lemma"

# food creates are idempotent: skip silently if the name already exists (unique)
food () { $LEMA records create foods --pod "$POD" --data "$1" >/dev/null 2>&1 || true; }

echo "==> Seeding foods catalog (shared)..."
food '{"name":"grilled chicken breast","serving_unit":"100 g","calories_per_serving":165,"protein_g":31,"carbs_g":0,"fat_g":3.6,"tags":"protein,poultry,low-carb"}'
food '{"name":"boiled egg","serving_unit":"1 large","calories_per_serving":78,"protein_g":6.3,"carbs_g":0.6,"fat_g":5.3,"tags":"protein,breakfast"}'
food '{"name":"whole wheat toast","serving_unit":"1 slice","calories_per_serving":80,"protein_g":4,"carbs_g":14,"fat_g":1.1,"tags":"carb,bread"}'
food '{"name":"black coffee","serving_unit":"1 cup","calories_per_serving":2,"protein_g":0.3,"carbs_g":0,"fat_g":0,"tags":"drink,low-cal"}'
food '{"name":"banana","serving_unit":"1 medium","calories_per_serving":105,"protein_g":1.3,"carbs_g":27,"fat_g":0.4,"tags":"fruit,carb"}'
food '{"name":"greek yogurt","serving_unit":"170 g","calories_per_serving":100,"protein_g":17,"carbs_g":6,"fat_g":0.7,"tags":"protein,dairy,low-fat"}'
food '{"name":"oats","serving_unit":"40 g dry","calories_per_serving":150,"protein_g":5,"carbs_g":27,"fat_g":3,"tags":"carb,breakfast,whole-grain"}'
food '{"name":"salmon fillet","serving_unit":"100 g","calories_per_serving":208,"protein_g":20,"carbs_g":0,"fat_g":13,"tags":"protein,fish,omega-3"}'
food '{"name":"white rice","serving_unit":"1 cup cooked","calories_per_serving":205,"protein_g":4.3,"carbs_g":45,"fat_g":0.4,"tags":"carb,grain"}'
food '{"name":"mixed green salad","serving_unit":"1 bowl","calories_per_serving":120,"protein_g":3,"carbs_g":10,"fat_g":7,"tags":"veg,low-carb"}'

echo "==> Seeding a day of meals (today, RLS-scoped to you)..."
D="$(date -u +%Y-%m-%d)"
$LEMA records create meals --pod "$POD" --data "{\"name\":\"Oats with banana and black coffee\",\"meal_type\":\"breakfast\",\"logged_at\":\"${D}T08:10:00Z\",\"calories\":257,\"protein_g\":6.6,\"carbs_g\":54,\"fat_g\":3.4,\"source\":\"manual\",\"raw_input\":{\"text\":\"oats, banana, coffee\"}}" >/dev/null
$LEMA records create meals --pod "$POD" --data "{\"name\":\"Grilled chicken salad\",\"meal_type\":\"lunch\",\"logged_at\":\"${D}T12:45:00Z\",\"calories\":420,\"protein_g\":35,\"carbs_g\":12,\"fat_g\":22,\"quantity\":1,\"unit\":\"bowl\",\"source\":\"telegram\",\"raw_input\":{\"text\":\"grilled chicken salad\"}}" >/dev/null
$LEMA records create meals --pod "$POD" --data "{\"name\":\"Greek yogurt\",\"meal_type\":\"snack\",\"logged_at\":\"${D}T16:20:00Z\",\"calories\":100,\"protein_g\":17,\"carbs_g\":6,\"fat_g\":0.7,\"quantity\":1,\"unit\":\"tub\",\"source\":\"telegram\",\"raw_input\":{\"text\":\"greek yogurt\"}}" >/dev/null
$LEMA records create meals --pod "$POD" --data "{\"name\":\"Salmon with white rice\",\"meal_type\":\"dinner\",\"logged_at\":\"${D}T19:30:00Z\",\"calories\":413,\"protein_g\":24.3,\"carbs_g\":45,\"fat_g\":13.4,\"source\":\"manual\",\"raw_input\":{\"text\":\"salmon and rice\"}}" >/dev/null

echo "==> Seeded. Today's totals:"
$LEMA query run "select round(sum(calories)) as kcal, round(sum(protein_g)) as protein_g, round(sum(carbs_g)) as carbs_g, round(sum(fat_g)) as fat_g, count(*) as meals from meals" --pod "$POD"
