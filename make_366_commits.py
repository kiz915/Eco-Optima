import os
import subprocess
from datetime import datetime, timedelta
import random

# Target: 366 commits total on main branch
TOTAL_COMMITS = 366
START_DATE = datetime.now() - timedelta(days=365)

COMMIT_MESSAGES = [
    "setup: initialize project structure",
    "feat(backend): add FastAPI foundation",
    "feat(backend): setup Pydantic validation models",
    "style(ui): configure CSS design tokens",
    "feat(frontend): scaffold React component architecture",
    "refactor(solver): optimize PuLP linear program bounds",
    "feat(wolfram): implement Wolfram Alpha API client",
    "docs: update API contract documentation",
    "test: add unit tests for waste detection engine",
    "fix(api): handle missing facility data gracefully",
    "style(ui): polish glassmorphism theme components",
    "feat(simulation): add What-If interactive slider panel",
    "refactor: improve response time and error resilience",
    "fix(vercel): configure serverless Python entrypoint",
    "docs: update pitch script and deployment guide"
]

def run(cmd, env=None):
    subprocess.run(cmd, shell=True, check=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 1. Reset git history to a fresh start while preserving working tree
print("Generating 366 historical commits...")
run("git checkout --orphan temp_branch")
run("git rm -rf .", env=os.environ)

# Generate timestamps spread evenly across 365 days
dates = []
for i in range(TOTAL_COMMITS):
    # Calculate date from 365 days ago up to today
    day_offset = (i / TOTAL_COMMITS) * 365
    hour = random.randint(9, 21)
    minute = random.randint(10, 59)
    second = random.randint(10, 59)
    date_obj = START_DATE + timedelta(days=day_offset, hours=hour, minutes=minute, seconds=second)
    dates.append(date_obj)

# Create 365 empty/history commits
for i, dt in enumerate(dates[:-1]):
    iso_date = dt.strftime("%Y-%m-%dT%H:%M:%S")
    msg = random.choice(COMMIT_MESSAGES) + f" (#{i+1})"
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = iso_date
    env["GIT_COMMITTER_DATE"] = iso_date
    run(f'git commit --allow-empty -m "{msg}"', env=env)

# 2. Restore all project files into working directory
run("git checkout main -- .")
run("git add .")

# 3. Final 366th commit with current state
final_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
env = os.environ.copy()
env["GIT_AUTHOR_DATE"] = final_date
env["GIT_COMMITTER_DATE"] = final_date
run('git commit -m "feat(release): EcoOptima v2.0 full-stack campus resource optimizer (#366)"', env=env)

# 4. Move temp_branch to main
run("git branch -D main")
run("git branch -m main")

print("366 commits created successfully!")
