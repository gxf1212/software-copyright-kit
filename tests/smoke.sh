#!/usr/bin/env bash
# 端到端冒烟测试：在临时目录模拟新用户，验证核心功能可用。
# 用法：bash tests/smoke.sh
# 需要：python（含pypdf）、xelatex、pdftotext。

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${PYTHON:-python}"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/sc-smoke.XXXXXX")"
FAIL=0

ok()   { echo "[PASS] $1"; }
bad()  { echo "[FAIL] $1"; FAIL=$((FAIL+1)); }
run()  { "$@" >"$TMP/out.log" 2>&1; }

echo "Smoke test in $TMP"

# 1. CLI四个命令
cd "$ROOT/software_copyright/src" || exit 1
printf 'Name,Score\n,88\nalice,92\n' > "$TMP/raw.csv"
if run "$PY" -m demo_tool --version; then ok "CLI --version"; else bad "CLI --version"; fi
if run "$PY" -m demo_tool clean "$TMP/raw.csv" "$TMP/clean.csv" && grep -q 'name' "$TMP/clean.csv"; then ok "CLI clean"; else bad "CLI clean"; fi
if run "$PY" -m demo_tool select "$TMP/clean.csv" "$TMP/sel.csv" --columns name && grep -q 'name' "$TMP/sel.csv"; then ok "CLI select"; else bad "CLI select"; fi
if run "$PY" -m demo_tool report "$TMP/sel.csv" --output "$TMP/report.csv" && grep -q 'column' "$TMP/report.csv"; then ok "CLI report"; else bad "CLI report"; fi

# 2. src_prod初始化（在临时副本上，不碰仓库）
cp -a "$ROOT/software_copyright/src" "$TMP/src"
if run "$PY" "$ROOT/softcopy-toolkit/init_code_copy.py" --src "$TMP/src" --dst "$TMP/src_prod_test" && [ -d "$TMP/src_prod_test/demo_tool" ]; then
  ok "init_code_copy"
else
  bad "init_code_copy"
fi

# 3. count_lines守卫：src应被拒绝
if run "$PY" "$ROOT/softcopy-toolkit/count_lines.py" "$TMP/src" --remove-empty; then
  bad "count_lines guard allowed src"
else
  ok "count_lines guard rejects src"
fi

# 4. 两份LaTeX编译
cd "$ROOT/software_copyright" || exit 1
for doc in document source-code; do
  if run xelatex -interaction=nonstopmode -halt-on-error "$doc.tex" && \
     run xelatex -interaction=nonstopmode -halt-on-error "$doc.tex" && \
     [ -f "$doc.pdf" ]; then ok "compile $doc.tex"; else bad "compile $doc.tex"; fi
done

# 5. 抽页（在小PDF上，验证不报错且输出存在）
if run "$PY" "$ROOT/softcopy-toolkit/extract_front_back_pages.py" source-code.pdf "$TMP/extract.pdf" --front-pages 2 --back-pages 2 && [ -f "$TMP/extract.pdf" ]; then
  ok "extract_front_back_pages"
else
  bad "extract_front_back_pages"
fi

# 6. 审计与隐私检查脚本可运行
if run "$PY" "$ROOT/softcopy-toolkit/audit_material.py"; then ok "audit_material runs"; else bad "audit_material runs"; fi
if run "$PY" "$ROOT/softcopy-toolkit/check_privacy.py" "$ROOT"; then ok "check_privacy runs"; else bad "check_privacy runs"; fi

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
else
  echo "$FAIL CHECK(S) FAILED"
fi
exit "$FAIL"
