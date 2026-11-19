Full Upload:
Verify version and app install
BACKEND:
- heroku --version
- heroku login
    - if necessary: unset HEROKU_API_KEY
- heroku auth:whoami
- cd backend
- cat > Procfile << 'EOF'
web: gunicorn run:app
release: flask db upgrade
EOF
- echo "python-3.10.11" > runtime.txt
- cat > .slugignore << 'EOF'
*.pyc
__pycache__/
.pytest_cache/
tests/
*.md
.git/
.venv/
venv/
EOF
- heroku create mock-pbm-app
- heroku addons:create heroku-postgresql:essential-0 -a  mock-pbm-app
- heroku addons
- heroku config:get DATABASE_URL -a mock-pbm-app
Set ENV Vars:
    - heroku config:set FLASK_ENV=production -a mock-pbm-app
    - heroku config:set SECRET_KEY=dev-secret-key-change-in-production -a mock-pbm-app
    - heroku config:set FLASK_APP=app -a mock-pbm-app
    - heroku config -a mock-pbm-app
CD into backend 
- Make sure migrations directoryt exists
- flask db init
- flask db migrate -m "Initial migration with models"
- Commit and push
- heroku run python scripts/init_db.py
- heroku run python scripts/seed_data.py
- curl https://mock-pbm-app-bf706fbe79fa.herokuapp.com/health
FRONTEND:
- cat > .env.production << 'EOF'
VITE_API_BASE_URL=https://mock-pbm-app-bf706fbe79fa.herokuapp.com
VITE_APP_NAME=MockPBM
EOF
- need to edit vite.config.ts: target: process.env.VITE_API_BASE_URL || 'http://localhost:5000',
- Build the front end "npm run build"
- cd to frontend
- heroku create pmock-pbm-app-ui
- cat > static.json << 'EOF'
{
  "root": "dist",
  "clean_urls": true,
  "routes": {
    "/**": "index.html"
  },
  "headers": {
    "/**": {
      "Cache-Control": "no-cache, no-store, must-revalidate"
    },
    "/assets/**": {
      "Cache-Control": "public, max-age=31536000, immutable"
    }
  }
}
EOF
- Update packagejson: add: "heroku-postbuild": "npm run build"
- heroku buildpacks:add heroku/nodejs -a pmock-pbm-app-ui
- heroku buildpacks:add https://github.com/heroku/heroku-buildpack-static -a pmock-pbm-app-ui

UPDATES TO THE BACKEND
- heroku login
    - if necessary: unset HEROKU_API_KEY
- git status
- git branch
- git add .
- git commit -m "Comment"
- cd to root
- heroku git:remote -a recipe-ripper -r heroku-backend
-   if login issues verify auth key in .netrc
-       heroku auth:token
-       nano ~/.netrc 
-       if tokens don't match. update the value in .netrc.  can also double chgeck value in _netrc
- git subtree push --prefix backend heroku-backend main

UPDATES TO THE FRONEND
- make edits
- npm install		        # if new packages are added or required
  - npm start		          # for local testing (runs the last build code)
  - npm run start-local   # for testing local changes before doing a run build
  - npm run build		      # for production ready code deployment
- cd to root
- git status
- git branch
- git add .
- git commit -m "Comment"
- heroku git:remote -a reciperipper-ui -r heroku-frontend
- git subtree push --prefix frontend heroku-frontend main


UPDATE SQL MODELS
- update data model as needed
- Generate the migration locally
-- flask db migrate -m "Increase size of recipes.instructions"
- Commit and deploy
-- git add . 
-- git commit -m "comment"
-- git push to remote
-- cd to root
-- git subtree push --prefix backend heroku main
-- heroku run flask db upgrade -a recipe-ripper


EXECUTE SQL ON HEROKU
- heroku pg:psql -a recipe-ripper
- output: 
-- recipe-ripper::DATABASE=> 
-- SELECT current_database();
-- SELECT id, email FROM users;
-- \d users
-- \dt
-- \d
-- \q
--  SELECT column_name, data_type, character_maximum_length
    FROM information_schema.columns
    WHERE table_name = 'users';

WATCH LOGS:
- heroku logs --tail -a reciperipper-ui
- heroku logs --tail -a recipe-ripper
- heroku logs --tail -r heroku-backend
- heroku logs --tail -r heroku-frontend

RENAME APPLICATION
- heroku apps:rename reciperipper-ui -a reciperipper




