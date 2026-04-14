#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  branch_pr_merge.sh [options] --branch <name> [--branch <name> ...]
  branch_pr_merge.sh [options] --branches <name1,name2,...>

Options:
  --repo-dir <path>        Repository directory (default: $REPO_DIR or current dir)
  --base-branch <name>     Base branch for PRs (default: $BASE_BRANCH or main)
  --branch <name>          Target branch to process (repeatable)
  --branches <csv>         Comma-separated branch list
  --merge-method <method>  merge | rebase | squash (default: $MERGE_METHOD or rebase)
  --auto-merge <bool>      true/false (default: $AUTO_MERGE or false)
  --delete-branch <bool>   true/false (default: $DELETE_BRANCH or false)
  --dry-run                Print actions without mutating state
  --verbose                Enable extra logging
  -h, --help               Show this help message

Environment defaults:
  REPO_DIR, BASE_BRANCH, MERGE_METHOD, AUTO_MERGE, DELETE_BRANCH, BRANCHES

Examples:
  branch_pr_merge.sh --branch feature/a --branch feature/b
  branch_pr_merge.sh --branches feature/a,feature/b --merge-method rebase --dry-run
USAGE
}

log() {
  printf '[%s] %s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*"
}

vlog() {
  if [[ "$VERBOSE" == "true" ]]; then
    log "$*"
  fi
}

error() {
  printf 'ERROR: %s\n' "$*" >&2
}

die() {
  error "$*"
  exit 1
}

normalize_bool() {
  local value="${1:-}"
  case "${value,,}" in
    true|1|yes|y|on) echo "true" ;;
    false|0|no|n|off) echo "false" ;;
    *) return 1 ;;
  esac
}

print_cmd() {
  local out=""
  local arg
  for arg in "$@"; do
    printf -v arg_quoted '%q' "$arg"
    out+="${arg_quoted} "
  done
  log "CMD: ${out% }"
}

run_cmd() {
  if [[ "$DRY_RUN" == "true" ]]; then
    print_cmd "$@"
    return 0
  fi
  "$@"
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

DEFAULT_REPO_DIR="$(pwd)"
REPO_DIR="${REPO_DIR:-$DEFAULT_REPO_DIR}"
BASE_BRANCH="${BASE_BRANCH:-main}"
MERGE_METHOD="${MERGE_METHOD:-rebase}"
AUTO_MERGE_RAW="${AUTO_MERGE:-false}"
DELETE_BRANCH_RAW="${DELETE_BRANCH:-false}"
BRANCHES_ENV="${BRANCHES:-}"
DRY_RUN="false"
VERBOSE="false"

if ! AUTO_MERGE="$(normalize_bool "$AUTO_MERGE_RAW" 2>/dev/null)"; then
  die "Invalid AUTO_MERGE value: '$AUTO_MERGE_RAW'"
fi
if ! DELETE_BRANCH="$(normalize_bool "$DELETE_BRANCH_RAW" 2>/dev/null)"; then
  die "Invalid DELETE_BRANCH value: '$DELETE_BRANCH_RAW'"
fi

BRANCHES=()
if [[ -n "${BRANCHES_ENV:-}" ]]; then
  IFS=',' read -r -a __env_branches <<<"$BRANCHES_ENV"
  for b in "${__env_branches[@]}"; do
    b="${b//[[:space:]]/}"
    [[ -n "$b" ]] && BRANCHES+=("$b")
  done
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-dir)
      [[ $# -ge 2 ]] || die "Missing value for --repo-dir"
      REPO_DIR="$2"
      shift 2
      ;;
    --base-branch)
      [[ $# -ge 2 ]] || die "Missing value for --base-branch"
      BASE_BRANCH="$2"
      shift 2
      ;;
    --branch)
      [[ $# -ge 2 ]] || die "Missing value for --branch"
      BRANCHES+=("$2")
      shift 2
      ;;
    --branches)
      [[ $# -ge 2 ]] || die "Missing value for --branches"
      IFS=',' read -r -a parsed <<<"$2"
      for b in "${parsed[@]}"; do
        b="${b//[[:space:]]/}"
        [[ -n "$b" ]] && BRANCHES+=("$b")
      done
      shift 2
      ;;
    --merge-method)
      [[ $# -ge 2 ]] || die "Missing value for --merge-method"
      MERGE_METHOD="$2"
      shift 2
      ;;
    --auto-merge)
      [[ $# -ge 2 ]] || die "Missing value for --auto-merge"
      AUTO_MERGE="$(normalize_bool "$2")" || die "Invalid --auto-merge value: '$2'"
      shift 2
      ;;
    --delete-branch)
      [[ $# -ge 2 ]] || die "Missing value for --delete-branch"
      DELETE_BRANCH="$(normalize_bool "$2")" || die "Invalid --delete-branch value: '$2'"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    --verbose)
      VERBOSE="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "Unknown argument: $1"
      ;;
  esac
done

case "$MERGE_METHOD" in
  merge|rebase|squash) ;;
  *) die "Invalid --merge-method '$MERGE_METHOD' (allowed: merge,rebase,squash)" ;;
esac

if [[ ${#BRANCHES[@]} -eq 0 ]]; then
  die "At least one branch is required via --branch/--branches or BRANCHES env var"
fi

if ! command_exists git; then
  die "Required command not found: git"
fi
if ! command_exists gh; then
  die "Required command not found: gh"
fi

[[ -d "$REPO_DIR" ]] || die "Repository directory does not exist: $REPO_DIR"
cd "$REPO_DIR"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "Not a git repository: $REPO_DIR"

if [[ -n "$(git status --porcelain)" ]]; then
  die "Working tree is not clean. Commit or stash changes before running this script."
fi

vlog "Checking GitHub authentication"
gh auth status >/dev/null 2>&1 || die "gh authentication is not active; run 'gh auth login' or configure GH_TOKEN"

vlog "Checking repository access"
REPO_FULL_NAME="$(gh repo view --json nameWithOwner -q '.nameWithOwner' 2>/dev/null)" || \
  die "Unable to access repository via gh CLI"
OWNER="${REPO_FULL_NAME%%/*}"

log "Using repository: $REPO_FULL_NAME"
log "Configuration: repo_dir=$REPO_DIR base_branch=$BASE_BRANCH merge_method=$MERGE_METHOD auto_merge=$AUTO_MERGE delete_branch=$DELETE_BRANCH dry_run=$DRY_RUN"

run_cmd git fetch --all --prune

if ! git show-ref --verify --quiet "refs/remotes/origin/$BASE_BRANCH"; then
  die "Base branch origin/$BASE_BRANCH was not found"
fi

for br in "${BRANCHES[@]}"; do
  if ! git ls-remote --exit-code --heads origin "$br" >/dev/null 2>&1; then
    die "Target branch does not exist on origin: $br"
  fi
done

SUMMARY_FILE="$(mktemp "${TMPDIR:-/tmp}/branch-pr-merge-summary.XXXXXX.tsv")"
trap 'rm -f "$SUMMARY_FILE"' EXIT INT TERM

TOTAL=${#BRANCHES[@]}
SUCCESS=0
FAILED=0

record_result() {
  local branch="$1"
  local status="$2"
  local pr_number="$3"
  local message="$4"
  printf '%s\t%s\t%s\t%s\n' "$branch" "$status" "$pr_number" "$message" >>"$SUMMARY_FILE"
}

for BR in "${BRANCHES[@]}"; do
  log "=== BEGIN branch: $BR ==="

  PR_NUMBER=""

  if ! run_cmd git switch "$BR"; then
    error "Failed checkout for branch: $BR"
    record_result "$BR" "failed" "" "checkout_failed"
    FAILED=$((FAILED + 1))
    log "=== END branch: $BR (failed) ==="
    continue
  fi

  if ! run_cmd git pull --ff-only origin "$BR"; then
    error "Failed fast-forward pull for branch: $BR"
    record_result "$BR" "failed" "" "pull_ff_only_failed"
    FAILED=$((FAILED + 1))
    log "=== END branch: $BR (failed) ==="
    continue
  fi

  if ! run_cmd git push -u origin "$BR"; then
    error "Failed push/upstream setup for branch: $BR"
    record_result "$BR" "failed" "" "push_failed"
    FAILED=$((FAILED + 1))
    log "=== END branch: $BR (failed) ==="
    continue
  fi

  PR_NUMBER="$(gh pr list --state open --base "$BASE_BRANCH" --head "$OWNER:$BR" --json number -q '.[0].number' 2>/dev/null || true)"

  if [[ -z "$PR_NUMBER" ]]; then
    if [[ "$DRY_RUN" == "true" ]]; then
      log "Dry-run: would create PR for $BR -> $BASE_BRANCH"
      PR_NUMBER="dry-run"
    else
      PR_CREATE_OUTPUT=""
      if ! PR_CREATE_OUTPUT="$(gh pr create --base "$BASE_BRANCH" --head "$BR" --title "Merge $BR into $BASE_BRANCH" --body "Automated PR for $BR" 2>&1)"; then
        error "Failed creating PR for branch: $BR"
        [[ -n "$PR_CREATE_OUTPUT" ]] && error "gh pr create output: $PR_CREATE_OUTPUT"
        record_result "$BR" "failed" "" "pr_create_failed"
        FAILED=$((FAILED + 1))
        log "=== END branch: $BR (failed) ==="
        continue
      fi

      PR_NUMBER="$(gh pr list --state open --base "$BASE_BRANCH" --head "$OWNER:$BR" --json number -q '.[0].number' 2>/dev/null || true)"
      if [[ -z "$PR_NUMBER" ]]; then
        error "PR creation appeared successful, but no open PR found for $BR"
        record_result "$BR" "failed" "" "pr_lookup_after_create_failed"
        FAILED=$((FAILED + 1))
        log "=== END branch: $BR (failed) ==="
        continue
      fi
      log "PR created: #$PR_NUMBER"
    fi
  else
    log "PR exists: #$PR_NUMBER"
  fi

  if [[ "$DRY_RUN" == "true" ]]; then
    log "Dry-run: would evaluate and merge PR for $BR"
    record_result "$BR" "dry_run" "$PR_NUMBER" "simulated"
    SUCCESS=$((SUCCESS + 1))
    log "=== END branch: $BR (dry-run) ==="
    continue
  fi

  PR_STATE="$(gh pr view "$PR_NUMBER" --json state -q '.state' 2>/dev/null || true)"
  PR_DRAFT="$(gh pr view "$PR_NUMBER" --json isDraft -q '.isDraft' 2>/dev/null || true)"
  MERGE_STATE="$(gh pr view "$PR_NUMBER" --json mergeStateStatus -q '.mergeStateStatus' 2>/dev/null || true)"

  if [[ "$PR_STATE" != "OPEN" ]]; then
    error "PR #$PR_NUMBER is not OPEN (state=$PR_STATE)"
    record_result "$BR" "failed" "$PR_NUMBER" "pr_not_open"
    FAILED=$((FAILED + 1))
    log "=== END branch: $BR (failed) ==="
    continue
  fi

  if [[ "$PR_DRAFT" == "true" ]]; then
    error "PR #$PR_NUMBER is a draft and cannot be merged"
    record_result "$BR" "failed" "$PR_NUMBER" "pr_is_draft"
    FAILED=$((FAILED + 1))
    log "=== END branch: $BR (failed) ==="
    continue
  fi

  if [[ "$AUTO_MERGE" == "false" ]]; then
    case "$MERGE_STATE" in
      CLEAN|HAS_HOOKS|UNSTABLE) ;;
      *)
        error "PR #$PR_NUMBER not mergeable now (mergeStateStatus=$MERGE_STATE)"
        record_result "$BR" "failed" "$PR_NUMBER" "merge_state_$MERGE_STATE"
        FAILED=$((FAILED + 1))
        log "=== END branch: $BR (failed) ==="
        continue
        ;;
    esac
  else
    case "$MERGE_STATE" in
      DIRTY|UNKNOWN)
        error "PR #$PR_NUMBER not suitable for auto-merge (mergeStateStatus=$MERGE_STATE)"
        record_result "$BR" "failed" "$PR_NUMBER" "merge_state_$MERGE_STATE"
        FAILED=$((FAILED + 1))
        log "=== END branch: $BR (failed) ==="
        continue
        ;;
      *) ;;
    esac
  fi

  MERGE_ARGS=("--$MERGE_METHOD")
  if [[ "$DELETE_BRANCH" == "true" ]]; then
    MERGE_ARGS+=("--delete-branch")
  fi
  if [[ "$AUTO_MERGE" == "true" ]]; then
    MERGE_ARGS+=("--auto")
  fi

  if gh pr merge "$PR_NUMBER" "${MERGE_ARGS[@]}"; then
    log "Merged PR #$PR_NUMBER with method=$MERGE_METHOD auto=$AUTO_MERGE delete_branch=$DELETE_BRANCH"
    record_result "$BR" "merged" "$PR_NUMBER" "ok"
    SUCCESS=$((SUCCESS + 1))
    log "=== END branch: $BR (merged) ==="
  else
    error "Failed to merge PR #$PR_NUMBER for branch $BR"
    record_result "$BR" "failed" "$PR_NUMBER" "merge_command_failed"
    FAILED=$((FAILED + 1))
    log "=== END branch: $BR (failed) ==="
  fi
done

log "Done processing branches"

python3 - "$SUMMARY_FILE" "$TOTAL" "$SUCCESS" "$FAILED" <<'PY'
import json
import sys

if len(sys.argv) != 5:
    raise SystemExit(
        "Expected 4 arguments after script name (summary_file, total, success, failed), "
        f"got {len(sys.argv) - 1}"
    )

summary_file, total, success, failed = sys.argv[1:5]
results = []
with open(summary_file, 'r', encoding='utf-8') as fh:
    for line in fh:
        line = line.rstrip('\n')
        if not line:
            continue
        branch, status, pr, message = line.split('\t', 3)
        results.append(
            {
                'branch': branch,
                'status': status,
                'pr_number': pr or None,
                'message': message,
            }
        )

payload = {
    'total': int(total),
    'success': int(success),
    'failed': int(failed),
    'results': results,
}
print(json.dumps(payload, ensure_ascii=False))
PY

if [[ "$FAILED" -gt 0 ]]; then
  exit 1
fi
