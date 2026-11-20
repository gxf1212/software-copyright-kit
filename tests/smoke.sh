#!/usr/bin/env bash
# 端到端冒烟测试：把仓库复制到临时目录，模拟新用户跑完整流程。
# 用法：bash tests/smoke.sh
# 需要：python（含pypdf）、xelatex、pdftotext。

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${PYTHON:-python}"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/sc-smoke.XXXXXX")"
REPO="$TMP/repo"
FAIL=0

ok()   { echo "[PASS] $1"; }
bad()  { echo "[FAIL] $1"; FAIL=$((FAIL+1)); }
run()  { "$@" >"$TMP/out.log" 2>&1; }

echo "Smoke test in $TMP"

# 0. 复制仓库到临时副本，模拟干净克隆（排除.git、src_prod、PDF与编译产物）
mkdir -p "$REPO"
( cd "$ROOT" && tar -cf - --exclude='.git' --exclude='src_prod' \
    --exclude='*.pdf' --exclude='*.aux' --exclude='*.log' \
    --exclude='*.toc' --exclude='*.out' . ) | ( cd "$REPO" && tar -xf - )

# 1. CLI四个命令
cd "$REPO/software_copyright/src" || exit 1
printf 'Name,Score\n,88\nalice,92\n' > "$TMP/raw.csv"
if run "$PY" -m demo_tool --version; then ok "CLI --version"; else bad "CLI --version"; fi
if run "$PY" -m demo_tool clean "$TMP/raw.csv" "$TMP/clean.csv" && grep -q 'name' "$TMP/clean.csv"; then ok "CLI clean"; else bad "CLI clean"; fi
if run "$PY" -m demo_tool select "$TMP/clean.csv" "$TMP/sel.csv" --columns name && grep -q 'name' "$TMP/sel.csv"; then ok "CLI select"; else bad "CLI select"; fi
if run "$PY" -m demo_tool report "$TMP/sel.csv" --output "$TMP/report.csv" && grep -q 'column' "$TMP/report.csv"; then ok "CLI report"; else bad "CLI report"; fi

# 2. src_prod初始化（在副本里，模拟用户首次运行，生成源码文档引用的副本）
if run "$PY" "$REPO/softcopy-toolkit/init_code_copy.py" && [ -f "$REPO/software_copyright/src_prod/demo_tool/io.py" ]; then
  ok "init_code_copy"
else
  bad "init_code_copy"
fi

# 3. count_lines守卫：原始src应被拒绝改写
if run "$PY" "$REPO/softcopy-toolkit/count_lines.py" "$REPO/software_copyright/src" --remove-empty; then
  bad "count_lines guard allowed src"
else
  ok "count_lines guard rejects src"
fi

# 4. 两份LaTeX编译（副本里src_prod已生成）
cd "$REPO/software_copyright" || exit 1
for doc in document source-code; do
  if run xelatex -interaction=nonstopmode -halt-on-error "$doc.tex" && \
     run xelatex -interaction=nonstopmode -halt-on-error "$doc.tex" && \
     [ -f "$doc.pdf" ]; then ok "compile $doc.tex"; else bad "compile $doc.tex"; fi
done

# 5.抽页：封面自动排除，输出恰好4页源码，首页是正文第1页
if run "$PY" "$REPO/softcopy-toolkit/extract_front_back_pages.py" source-code.pdf "$TMP/extract.pdf" --front-pages 2 --back-pages 2 && \
   "$PY" -c 'from pypdf import PdfReader; import sys; r=PdfReader(sys.argv[1]); t=r.pages[0].extract_text() or ""; assert len(r.pages)==4 and "第1页" in t, (len(r.pages), t[:60])' "$TMP/extract.pdf" >"$TMP/out.log" 2>&1; then
  ok "extract excludes cover and keeps 4 source pages"
else
  cat "$TMP/out.log"
  bad "extract excludes cover and keeps 4 source pages"
fi

# 6.审计：干净包应返回0，故意植入问题应返回1
if run "$PY" "$REPO/softcopy-toolkit/audit_material.py" --package "$REPO/software_copyright"; then
  ok "audit passes clean package"
else
  cat "$TMP/out.log"
  bad "audit passes clean package"
fi
cp -r "$REPO/software_copyright" "$TMP/badpkg"
printf 'TODO planted for smoke test\n' >> "$TMP/badpkg/1-introduction.tex"
if ! run "$PY" "$REPO/softcopy-toolkit/audit_material.py" --package "$TMP/badpkg"; then
  ok "audit detects planted issue"
else
  bad "audit detects planted issue"
fi
if run "$PY" "$REPO/softcopy-toolkit/check_privacy.py" "$REPO"; then ok "check_privacy runs (advisory)"; else bad "check_privacy runs (advisory)"; fi

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
else
  echo "$FAIL CHECK(S) FAILED"
fi
exit "$FAIL"
