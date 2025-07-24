import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from pathlib import Path
from string import Template

DATA_PATH = Path('menus.json')


def load_foods():
    with open(DATA_PATH) as f:
        return json.load(f)


def get_food(name, foods):
    for item in foods:
        if item['name'] == name:
            return item
    return None


def recommended_calories(gender: str, age: str) -> int:
    base = 2500 if gender == 'male' else 2000
    if age.isdigit():
        age_val = int(age)
        if age_val < 30:
            base += 100
        elif age_val > 50:
            base -= 100
    return base


def recommended_macros(calories: int):
    return {
        'protein': calories * 0.25 / 4,
        'carbs': calories * 0.5 / 4,
        'fat': calories * 0.25 / 9,
    }


def total_macros(names, foods):
    totals = {'protein': 0, 'carbs': 0, 'fat': 0}
    for name in names:
        food = get_food(name, foods)
        if not food:
            continue
        for k in totals:
            totals[k] += food.get(k, 0)
    return totals


def recommend(last_meals, allergies, gender, age, foods):
    calories = recommended_calories(gender, age)
    rec = recommended_macros(calories)
    consumed = total_macros(last_meals, foods)
    best = None
    best_score = float('inf')
    for item in foods:
        if set(allergies) & set(item.get('allergens', [])):
            continue
        combined = {k: consumed[k] + item.get(k, 0) for k in consumed}
        score = sum((combined[k] - rec[k]) ** 2 for k in combined)
        if score < best_score:
            best_score = score
            best = item
    return best, rec, consumed


class Handler(BaseHTTPRequestHandler):
    def _render_index(self):
        foods = load_foods()
        options = '\n'.join(f'<option value="{f["name"]}">' for f in foods)
        tpl = Template("""<!DOCTYPE html>
<html lang=\"en\" class=\"h-full\">
<head>
<meta charset=\"utf-8\">
<script src=\"https://cdn.tailwindcss.com\"></script>
<title>Menu Recommendation</title>
</head>
<body class=\"min-h-screen flex flex-col items-center p-4 bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100\">
<div class=\"w-full max-w-xl\">
<button id=\"toggle\" class=\"mb-4 px-2 py-1 border rounded\">Toggle Dark Mode</button>
<form method=\"POST\" action=\"/recommend\" class=\"space-y-4\">
  <div>
    <label class=\"block\">Gender
      <select name=\"gender\" class=\"border p-1 w-full\">
        <option value=\"male\">Male</option>
        <option value=\"female\">Female</option>
      </select>
    </label>
  </div>
  <div>
    <label class=\"block\">Age
      <input type=\"number\" name=\"age\" class=\"border p-1 w-full\" required>
    </label>
  </div>
  <div>
    <label class=\"block\">Allergies (comma separated)
      <input type=\"text\" name=\"allergies\" class=\"border p-1 w-full\">
    </label>
  </div>
  <div>
    <label class=\"block\">Meal 1
      <input list=\"foods\" name=\"meal1\" class=\"border p-1 w-full\" required>
    </label>
  </div>
  <div>
    <label class=\"block\">Meal 2
      <input list=\"foods\" name=\"meal2\" class=\"border p-1 w-full\" required>
    </label>
  </div>
  <div>
    <label class=\"block\">Meal 3
      <input list=\"foods\" name=\"meal3\" class=\"border p-1 w-full\" required>
    </label>
  </div>
  <datalist id=\"foods\">$options</datalist>
  <button type=\"submit\" class=\"px-4 py-2 bg-blue-500 text-white rounded\">Recommend</button>
</form>
</div>
<script>
const btn=document.getElementById('toggle');
btn.addEventListener('click',()=>{
  document.documentElement.classList.toggle('dark');
  localStorage.setItem('theme',document.documentElement.classList.contains('dark')?'dark':'light');
});
if(localStorage.getItem('theme')==='dark'||(window.matchMedia('(prefers-color-scheme: dark)').matches&&!localStorage.getItem('theme'))){
  document.documentElement.classList.add('dark');
}
</script>
</body>
</html>""")
        html = tpl.substitute(options=options)
        self._send_html(html)

    def _render_result(self, menu, rec, consumed):
        if menu:
            reason = f"Adds protein {menu['protein']}g, carbs {menu['carbs']}g, fat {menu['fat']}g"
            tpl = Template("""<!DOCTYPE html>
<html lang=\"en\" class=\"h-full\">
<head>
<meta charset=\"utf-8\">
<script src=\"https://cdn.tailwindcss.com\"></script>
<title>Recommendation</title>
</head>
<body class=\"min-h-screen flex flex-col items-center p-4 bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100\">
<div class=\"w-full max-w-xl space-y-4\">
<button onclick=\"history.back()\" class=\"px-2 py-1 border rounded\">Back</button>
<h1 class=\"text-xl font-bold\">Recommended Menu: $name</h1>
<p>Calories: $cal kcal</p>
<p>Protein: $protein g, Carbs: $carbs g, Fat: $fat g</p>
<h2 class=\"font-semibold\">Reason</h2>
<p>$reason</p>
</div>
<script>
if(localStorage.getItem('theme')==='dark'||(window.matchMedia('(prefers-color-scheme: dark)').matches&&!localStorage.getItem('theme'))){
  document.documentElement.classList.add('dark');
}
</script>
</body>
</html>""")
            html = tpl.substitute(name=menu['name'], cal=menu['calories'], protein=menu['protein'], carbs=menu['carbs'], fat=menu['fat'], reason=reason)
        else:
            html = "<p>No recommendation available</p>"
        self._send_html(html)

    def _send_html(self, html: str):
        encoded = html.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        self._render_index()

    def do_POST(self):
        if self.path != '/recommend':
            self.send_error(404)
            return
        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length).decode('utf-8')
        params = parse_qs(data)
        gender = params.get('gender', ['female'])[0]
        age = params.get('age', ['0'])[0]
        allergies = params.get('allergies', [''])[0].split(',') if params.get('allergies') else []
        last_meals = [params.get('meal1', [''])[0], params.get('meal2', [''])[0], params.get('meal3', [''])[0]]
        foods = load_foods()
        menu, rec, consumed = recommend(last_meals, [a.strip() for a in allergies if a.strip()], gender, age, foods)
        self._render_result(menu, rec, consumed)


def run(server_class=HTTPServer, handler_class=Handler, port=8000):
    with server_class(('', port), handler_class) as httpd:
        print(f'Serving on http://localhost:{port}')
        httpd.serve_forever()


if __name__ == '__main__':
    run()
