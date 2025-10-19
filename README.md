# AutoDrive Market

A bilingual (English & Arabic) Django storefront for showcasing car inventory. The project ships with a SQLite database model for vehicles, multilingual copy, and tooling to generate a static bundle that can be deployed on GitHub Pages.

## Features

- Django models for storing vehicle details in both languages
- Responsive landing page with RTL adjustments and a language toggle
- Reusable bilingual copy shared between views and the static exporter
- Management command to render a GitHub Pages–ready static bundle (HTML + assets)

## Prerequisites

- Python 3.11+
- pip (Python package manager)

## Local development

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Apply database migrations**

   ```bash
   python manage.py migrate
   ```

3. **Load the sample inventory (optional)**

   ```bash
   python manage.py loaddata initial_cars
   ```

4. **Run the development server**

   ```bash
   python manage.py runserver
   ```

   Visit `http://127.0.0.1:8000/` to interact with the bilingual storefront. Use the language buttons in the header to switch between Arabic and English; your selection is remembered via `localStorage`.

## Managing inventory

- Access the Django admin at `http://127.0.0.1:8000/admin/` (create a superuser with `python manage.py createsuperuser`).
- Add or edit `Car` records. Each vehicle stores English and Arabic copy for its name, price, and key features.

## Exporting for GitHub Pages

GitHub Pages only serves static files, so this project includes an exporter that renders the current database state into a static bundle.

```bash
python manage.py export_static_site --output static_site
```

The command will:

- Render `market/index.html` with your live database content.
- Collect all static assets into `static_site/static/`.
- Write the ready-to-host `index.html` to `static_site/index.html`.

To deploy:

1. Commit and push the repository to GitHub.
2. Run the exporter locally or via GitHub Actions.
3. Push the contents of the generated `static_site/` directory to a `gh-pages` branch (or the `docs/` folder on `main`).
4. Enable GitHub Pages in the repository settings, pointing to the published branch/folder.

Your live site will now serve the pre-rendered page that reflects your database at the time of export. Re-run the exporter whenever you update your inventory and redeploy the generated bundle.

## Project structure

```
├── autodrive/                 # Django project settings
├── manage.py                  # Django management entry point
├── market/                    # Storefront app (models, views, templates, static files)
├── requirements.txt           # Python dependencies
└── README.md
```

## Next steps

- Connect to a production-ready database (PostgreSQL, MySQL, etc.).
- Deploy the Django backend to a platform such as Render, Railway, or Fly.io if you need live administration while hosting the static front-end on GitHub Pages.
- Customize the styling in `market/static/market/styles.css` to match your brand.
