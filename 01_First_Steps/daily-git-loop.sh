#!/usr/bin/env bash
# daily-git-loop.sh — Your daily fork-based GitHub workflow, one phase at a time.
#
# Usage:
#   ./daily-git-loop.sh --phase sync        # fetch + fast-forward main (always re-runnable)
#   ./daily-git-loop.sh --phase branch       # create/switch feature branch, scaffold scratch file
#   ./daily-git-loop.sh --phase review       # git add -A && diff (re-runnable; just re-stages and rediffs)
#   ./daily-git-loop.sh --phase commit       # interactive commit via $EDITOR
#   ./daily-git-loop.sh --phase push-pr      # push branch + open draft PR
#
# Resume is automatic: each phase records its completion in .git/.daily-loop-state.
# To start over, delete that file or pass --reset.

set -euo pipefail

STATE_FILE=".git/.daily-loop-state"
UPSTREAM_REPO="AI-Maker-Space/The-Hive-FDE-Challenge"

usage() {
  cat <<EOF
Usage: $(basename "$0") --phase <sync|branch|review|commit|push-pr> [--reset]

Phases:
  sync       Fetch upstream and fast-forward main (safe to re-run)
  branch     Create or switch feature branch; scaffold scratch file for editing
  review     Stage all changes and show the diff (re-runnable)
  commit     Interactive commit message via \$EDITOR (re-runnable if nothing staged)
  push-pr    Push branch to origin and open a draft PR

Options:
  --reset    Clear state and start the loop from scratch
EOF
  exit 1
}

need() { command -v "$1" >&2 && return 0 || { echo "ERROR: '$1' not found" >&2; exit 1; }; }
require_phase() {
  if [[ "$PHASE" != "$1" ]]; then
    echo "ERROR: phase '$1' must complete before running '$PHASE'"
    echo "       Current state: $(current_state)"
    exit 1
  fi
}
current_state() { sed -n 's/^phase=//p' "$STATE_FILE" 2>/dev/null || echo "none"; }
save_state() { echo "phase=$1" > "$STATE_FILE"; }

need git; need gh

# ── Parse args ───────────────────────────────────────────────────────────────
PHASE=""
RESET=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --phase) PHASE="${2:-}"; shift 2 ;;
    --reset)  RESET=true;   shift  ;;
    *)        usage           ;;
  esac
done

[[ -z "$PHASE" ]] && usage

if [[ "$RESET" == true ]]; then
  rm -f "$STATE_FILE"
  echo "State cleared."
fi

USER=$(gh api user --jq .login)

# ── PHASE: sync ────────────────────────────────────────────────────────────────
sync_phase() {
  echo "=== sync ==="

  origin_url=$(git remote get-url origin 2>/dev/null || true)
  if [[ -z "$origin_url" ]]; then
    echo "ERROR: no 'origin' remote configured."
    exit 1
  fi

  # Detect fork vs. instructor setup by checking if origin IS the course repo.
  case "${origin_url,,}" in
    *"${UPSTREAM_REPO,,}"*)
      SYNC_REMOTE="origin"
      echo "Instructor setup detected (origin is the course repo); syncing from origin."
      ;;
    *)
      if ! git remote | grep -q '^upstream$'; then
        git remote add upstream "https://github.com/${UPSTREAM_REPO}.git"
        echo "Added 'upstream' remote → ${UPSTREAM_REPO}"
      fi
      SYNC_REMOTE="upstream"
      ;;
  esac

  git fetch "$SYNC_REMOTE"

  local_head=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origino/||')
  upstream_main="${SYNC_REMOTE}/main"

  echo ""
  echo "Recent commits on ${upstream_main}:"
  git log --oneline -5 "$upstream_main"
  echo ""

  local_tracking=$(git rev-parse --abbrev-ref HEAD)
  if [[ "$local_tracking" != "main" ]]; then
    echo "You are on '$local_tracking'. Switch to main first:"
    echo "  git switch main && $(basename "$0") --phase sync"
    exit 1
  fi

  ahead=$(git rev-list --count "${upstream_main}..HEAD" 2>/dev/null || echo 0)
  behind=$(git rev-list --count "HEAD..${upstream_main}" 2>/dev/null || echo 0)

  if [[ "$behind" -gt 0 ]]; then
    echo "Your main is $behind commit(s) behind ${upstream_main}."
    read -p "Fast-forward? [y/N] " confirm
    if [[ "${confirm,,}" == y ]]; then
      git merge --ff-only "$upstream_main"
      if [[ "$SYNC_REMOTE" != "origin" ]]; then
        git push origin main
      fi
      echo "✅ Fast-forwarded and pushed."
    else
      echo "Skipped. Your local main is stale — resolve this before continuing."
      exit 1
    fi
  elif [[ "$ahead" -gt 0 ]]; then
    echo "Your main is $ahead commit(s) ahead of ${upstream_main} (unusual for a sync)."
  else
    echo "Already up to date with ${upstream_main}."
  fi

  save_state sync
  echo ""
  echo "✅ Sync complete. Next: $(basename "$0") --phase branch"
}

# ── PHASE: branch ───────────────────────────────────────────────────────────────
branch_phase() {
  echo "=== branch ==="

  # Require sync (or be on main with no prior state — first run is fine)
  if [[ -f "$STATE_FILE" ]]; then
    require_phase sync
    current=$(current_state)
    if [[ "$current" == branch || "$current" == review || "$current" == commit ]]; then
      echo "Already on a branch. To start fresh: $(basename "$0") --reset && $(basename "$0") --phase sync"
      exit 1
    fi
  fi

  BRANCH="feat/${USER}-daily-demo"

  if git branch --list "$BRANCH" | grep -q .; then
    echo "Branch '$BRANCH' already exists."
    read -p "Switch to it? [Y/n] " confirm
    if [[ "${confirm,,}" != n ]]; then
      git switch "$BRANCH"
    fi
  else
    git switch -c "$BRANCH"
  fi

  current_branch=$(git branch --show-current)
  echo ""
  echo "On branch: $current_branch"

  # Scaffold a scratch file for the student to edit.
  participants_dir="participants"
  mkdir -p "$participants_dir"
  scratch_file="${participants_dir}/${USER}.md"

  if [[ ! -f "$scratch_file" ]]; then
    cat > "$scratch_file" <<EOF
# ${USER}

Replace this text with your notes, findings, or whatever you're working on today.

When you run --phase review, only this file will be staged.
EOF
    echo "Created scratch file: $scratch_file  ← edit this during the workshop"
  else
    echo "Scratch file already exists: $scratch_file"
  fi

  save_state branch
  echo ""
  echo "✅ Branch ready. Edit your files, then: $(basename "$0") --phase review"
}

# ── PHASE: review ───────────────────────────────────────────────────────────────
review_phase() {
  echo "=== review ==="

  if [[ -f "$STATE_FILE" ]]; then
    require_phase branch
  fi

  current_branch=$(git branch --show-current)
  if [[ -z "$current_branch" ]]; then
    echo "ERROR: not on a branch. Run --phase branch first."
    exit 1
  fi

  staged=$(git diff --staged --name-only 2>/dev/null || true)
  if [[ -n "$staged" ]]; then
    echo "Re-showing already-staged diff (--phase review is idempotent):"
    git --no-pager diff --staged
  else
    git add -A
    echo ""
    echo "=== STAGED DIFF (what will be committed) ==="
    git --no-pager diff --staged
    echo ""
    read -p "Looks good? [y/N] " confirm
    if [[ "${confirm,,}" != y ]]; then
      echo "Unstaging. Edit your files and re-run --phase review."
      git reset HEAD
      exit 0
    fi
  fi

  save_state review
  echo ""
  echo "✅ Review complete. Next: $(basename "$0") --phase commit"
}

# ── PHASE: commit ───────────────────────────────────────────────────────────────
commit_phase() {
  echo "=== commit ==="

  if [[ -f "$STATE_FILE" ]]; then
    require_phase review
  fi

  current_branch=$(git branch --show-current)
  if [[ -z "$current_branch" ]]; then
    echo "ERROR: not on a branch. Run --phase branch first."
    exit 1
  fi

  staged=$(git diff --staged --name-only)
  if [[ -z "$staged" ]]; then
    echo "Nothing staged. Run --phase review first."
    exit 1
  fi

  # Build a sensible default commit message from the branch name.
  # feat/jane-daily-demo → "docs: daily demo"
  default_msg=$(echo "$current_branch" | sed 's/^[a-z]*\/[a-z]*-//' | tr '-' ' ')
  if [[ -z "$default_msg" ]]; then
    default_msg="update"
  fi

  COMMIT_MSG_FILE="${TMPDIR:-/tmp}/commit_msg_$$.txt"
  cat > "$COMMIT_MSG_FILE" <<EOF
docs: ${default_msg}

What changed and why.
EOF

  echo ""
  echo "Write your commit message in the editor below."
  echo "First line is the summary (keep it under 72 chars). Blank line separates from body."
  echo ""

  "${EDITOR:-vi}" "$COMMIT_MSG_FILE"
  sed -i '/^#/d' "$COMMIT_MSG_FILE"
  msg=$(cat "$COMMIT_MSG_FILE")
  rm -f "$COMMIT_MSG_FILE"

  if [[ -z "$(echo "$msg" | tr -d ' \n')" ]]; then
    echo "Empty message — commit aborted."
    exit 1
  fi

  git commit -F - <<<"$msg"
  save_state commit
  echo ""
  echo "✅ Committed. Next: $(basename "$0") --phase push-pr"
}

# ── PHASE: push-pr ───────────────────────────────────────────────────────────────
push_pr_phase() {
  echo "=== push-pr ==="

  if [[ -f "$STATE_FILE" ]]; then
    require_phase commit
  fi

  current_branch=$(git branch --show-current)
  if [[ -z "$current_branch" ]]; then
    echo "ERROR: not on a branch."
    exit 1
  fi

  origin_slug=$(git remote get-url origin | sed -E 's|.*github\.com[:/]([^/]+)/(.+?)(|\.git)$|\1/\2|I')
  upstream_slug="${UPSTREAM_REPO}"

  # Push the branch if not already pushed.
  if ! git ls-remote --exit-code --heads origin "$current_branch" &>/dev/null; then
    echo "Pushing '$current_branch' to origin..."
    git push -u origin "$current_branch"
  else
    echo "Branch already on origin. Pushing any new commits..."
    git push origin "$current_branch"
  fi

  # Check for existing PR.
  pr_url=$(gh pr list --repo "$origin_slug" --head "$current_branch" --json url --jq '.[0].url // empty' 2>/dev/null || true)

  if [[ -n "$pr_url" ]]; then
    echo "PR already open: $pr_url"
  else
    # Derive title from the last commit message.
    title=$(git log -1 --format='%s')
    pr_url=$(gh pr create \
      --repo "$origin_slug" \
      --base main \
      --head "$current_branch" \
      --draft \
      --title "$title" \
      --body "Daily-driver workflow demo — safe to close." \
      --json url --jq '.url')
    echo "✅ Draft PR opened: $pr_url"
  fi

  gh pr view "$current_branch" --repo "$origin_slug" --json url,state,isDraft

  save_state push-pr
  echo ""
  echo "✅ Done! PR is open. When you're ready for real work:"
  echo "   gh pr merge --squash --delete-branch $pr_url"
  echo ""
  echo "To start a new loop: $(basename "$0") --reset && $(basename "$0") --phase sync"
}

# ── Dispatch ───────────────────────────────────────────────────────────────
case "$PHASE" in
  sync)     sync_phase    ;;
  branch)   branch_phase  ;;
  review)   review_phase  ;;
  commit)   commit_phase  ;;
  push-pr)  push_pr_phase ;;
  *)        usage         ;;
esac