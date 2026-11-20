#!/bin/bash

# LaTeX编译脚本 - 生成软件著作权申请材料PDF
# 适用于Ubuntu系统，使用XeLaTeX编译器
# 
# 使用方法：
#   chmod +x compile.sh
#   ./compile.sh

set -e  # 遇到错误立即退出

# 颜色输出定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    print_info "检查LaTeX编译环境..."
    
    if ! command -v xelatex &> /dev/null; then
        print_error "XeLaTeX未安装！请运行以下命令安装："
        echo "sudo apt update"
        echo "sudo apt install texlive-full"
        echo "或者安装精简版："
        echo "sudo apt install texlive-latex-base texlive-xetex texlive-lang-chinese texlive-fonts-recommended texlive-latex-extra texlive-science"
        exit 1
    fi
    
    if ! command -v bibtex &> /dev/null; then
        print_error "BibTeX未安装！请安装texlive-latex-extra包"
        exit 1
    fi
    
    print_success "LaTeX环境检查通过"
}

# 检查特定LaTeX包
check_latex_packages() {
    print_info "检查必需的LaTeX包..."
    
    # 创建临时测试文件来检查包
    local tmp_dir
    tmp_dir="$(mktemp -d)"
    local test_file="${tmp_dir}/package_test.tex"
    cat > "$test_file" << 'EOF'
\documentclass{article}
\usepackage{newtxtext,newtxmath}
\usepackage{chemmacros}
\usepackage{tcolorbox}
\usepackage{fontspec}
\usepackage{xeCJK}
\begin{document}
Package test
\end{document}
EOF
    
    # 尝试编译测试文件
    if xelatex -interaction=batchmode "$test_file" > /dev/null 2>&1; then
        print_success "所需LaTeX包检查通过"
    else
        print_warning "某些LaTeX包可能缺失，建议安装完整版："
        echo "sudo apt install texlive-full"
        echo "或安装特定包："
        echo "sudo apt install texlive-fonts-extra texlive-science texlive-latex-extra"
        print_info "继续编译，如遇到包缺失错误请手动安装"
    fi
    
    # 清理测试文件
    rm -rf "$tmp_dir" 2>/dev/null
}

# 清理临时文件
cleanup() {
    local target_dir="${1:-.}"
    print_info "清理临时文件..."
    (cd "$target_dir" && rm -f *.aux *.log *.toc *.out *.fdb_latexmk *.fls *.synctex.gz *.bbl *.blg *.idx *.ind *.ilg *.lof *.lot *.nav *.snm *.vrb *.xdv *.figlist *.makefile *.fls_latexmk *.run.xml *-blx.bib package_test.*)
    print_success "临时文件清理完成"
}

# 编译单个LaTeX文件
compile_single() {
    local tex_path="$1"
    local tex_dir
    tex_dir="$(dirname "$tex_path")"
    local tex_name
    tex_name="$(basename "$tex_path")"
    local base_name="${tex_name%.tex}"

    # 每次编译独立日志目录，避免并行编译多个软著时互相覆盖
    local log_dir
    log_dir="$(mktemp -d "${TMPDIR:-/tmp}/softcopy-${base_name}.XXXXXX")"

    print_info "编译 $tex_path..."

    # 第一次编译 - 生成辅助文件
    print_info "第一次XeLaTeX编译..."
    (cd "$tex_dir" && xelatex -synctex=1 -interaction=nonstopmode "$tex_name" > "$log_dir/xelatex_pass1.log" 2>&1)
    local pass1_status=$?

    # 如果有.bib文件，运行BibTeX
    if [ -f "${tex_dir}/${base_name}.bib" ]; then
        print_info "运行BibTeX处理参考文献..."
        (cd "$tex_dir" && bibtex "${base_name}" > "$log_dir/bibtex.log" 2>&1) || {
            print_warning "BibTeX处理失败，但继续编译"
        }
    fi

    # 第二次编译 - 处理交叉引用
    print_info "第二次XeLaTeX编译..."
    (cd "$tex_dir" && xelatex -synctex=1 -interaction=nonstopmode "$tex_name" > "$log_dir/xelatex_pass2.log" 2>&1)
    local pass2_status=$?

    # 第三次编译 - 确保所有引用正确
    print_info "第三次XeLaTeX编译..."
    (cd "$tex_dir" && xelatex -synctex=1 -interaction=nonstopmode "$tex_name" > "$log_dir/xelatex_pass3.log" 2>&1)
    local pass3_status=$?

    # 检查PDF是否生成
    if [ -f "${tex_dir}/${base_name}.pdf" ]; then
        local pdf_size=$(ls -lh "${tex_dir}/${base_name}.pdf" | awk '{print $5}')
        local pdf_pages=$(pdfinfo "${tex_dir}/${base_name}.pdf" 2>/dev/null | grep "Pages:" | awk '{print $2}')
        print_success "成功生成 ${base_name}.pdf (${pdf_pages} 页, ${pdf_size})"

        # 显示警告（如果有）
        if [ $pass1_status -ne 0 ] || [ $pass2_status -ne 0 ] || [ $pass3_status -ne 0 ]; then
            print_warning "编译过程中有警告，但PDF已成功生成"
            print_info "查看日志: ${log_dir}/xelatex_pass*.log"
        else
            # 三次编译均无警告：本次日志不再有排查价值，清理以免 /tmp 堆积。
            # 路径前缀守卫：变量异常/为空时绝不执行 rm -rf
            if [[ -n "$log_dir" && "$log_dir" == "${TMPDIR:-/tmp}/softcopy-"* ]]; then
                rm -rf -- "$log_dir" 2>/dev/null
            fi
        fi
        return 0
    else
        print_error "编译失败，未生成PDF文件"
        print_info "查看日志: ${log_dir}/xelatex_pass*.log"
        return 1
    fi
}

# 解析TeX路径（支持从脚本目录或当前目录运行）
resolve_tex_path() {
    local input_path="$1"
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    if [ -f "$input_path" ]; then
        echo "$input_path"
        return 0
    fi

    if [ -f "${script_dir}/../${input_path}" ]; then
        echo "${script_dir}/../${input_path}"
        return 0
    fi

    echo "$input_path"
    return 0
}

# 主编译函数
main() {
    local tex_file="${1:-document.tex}"
    local tex_path
    tex_path="$(resolve_tex_path "$tex_file")"
    local base_name
    base_name="$(basename "$tex_path" .tex)"
    local tex_dir
    tex_dir="$(dirname "$tex_path")"

    print_info "开始编译软件著作权申请材料..."

    # 检查文件是否存在
    if [ ! -f "$tex_path" ]; then
        print_error "未找到${tex_file}文件！"
        exit 1
    fi

    # 检查依赖
    check_dependencies

    # 检查LaTeX包
    check_latex_packages

    # 检查中文字体支持
    print_info "检查中文字体支持..."
    if ! fc-list | grep -qi "noto.*cjk"; then
        print_warning "建议安装中文字体包以获得更好的显示效果："
        echo "sudo apt-get install fonts-noto-cjk"
        print_info "如果字体错误持续，请尝试安装："
        echo "sudo apt-get install fonts-liberation"
    fi

    # 清理旧的临时文件
    cleanup "$tex_dir"

    # 编译指定文档
    compile_single "$tex_path"

    # 最终清理
    cleanup "$tex_dir"

    # 检查输出文件
    if [ -f "${tex_dir}/${base_name}.pdf" ]; then
        print_success "编译完成！生成文件：${base_name}.pdf"
        print_info "PDF文件大小：$(du -h ${tex_dir}/${base_name}.pdf | cut -f1)"
        print_info "PDF页数：$(pdfinfo ${tex_dir}/${base_name}.pdf 2>/dev/null | grep 'Pages:' | awk '{print $2}')"

        if [[ "${CHECK_PDF_LINES:-}" == "true" ]]; then
            local script_dir
            script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
            local material_kind="document"
            if [[ "$base_name" == "source-code" ]]; then
                material_kind="source"
            fi
            print_info "检查PDF每页行数（${material_kind}，普通交存范围）..."
            python3 "${script_dir}/check_pdf_lines.py" \
                "${tex_dir}/${base_name}.pdf" --kind "$material_kind" --scope deposit
        fi

        # 可选：打开PDF文件（使用 --open 参数时才询问）
        if [[ "${OPEN_PDF:-}" == "true" ]] && command -v evince &> /dev/null; then
            print_info "是否要打开PDF文件？(y/n)"
            read -r response < /dev/tty
            if [[ "$response" =~ ^[Yy]$ ]]; then
                evince ${tex_dir}/${base_name}.pdf &
            fi
        fi
    else
        print_error "编译失败，未生成PDF文件"
        exit 1
    fi
}

# 显示帮助信息
show_help() {
    echo "LaTeX编译脚本 - 软件著作权申请材料"
    echo ""
    echo "用法："
    echo "  ./compile.sh                    - 编译document.tex（默认）"
    echo "  ./compile.sh <file.tex>         - 编译指定的.tex文件"
    echo "  ./compile.sh --open             - 编译后可选择打开PDF"
    echo "  ./compile.sh --check-lines FILE - 编译后检查PDF每页行数"
    echo "  ./compile.sh clean              - 清理临时文件"
    echo "  ./compile.sh help               - 显示此帮助信息"
    echo ""
    echo "示例："
    echo "  ./compile.sh source-code.tex    - 编译源代码文档"
    echo "  ./compile.sh document.tex       - 编译使用说明文档"
    echo "  ./compile.sh --check-lines source-code.tex"
    echo ""
    echo "环境变量："
    echo "  OPEN_PDF=true                   - 编译后询问是否打开PDF"
    echo ""
    echo "环境要求："
    echo "  - Ubuntu系统"
    echo "  - 已安装XeLaTeX (texlive-xetex)"
    echo "  - 已安装中文字体支持 (texlive-lang-chinese)"
    echo ""
    echo "安装命令："
    echo "  sudo apt update"
    echo "  sudo apt install texlive-full"
    echo ""
    echo "或精简安装："
    echo "  sudo apt install texlive-latex-base texlive-xetex texlive-lang-chinese texlive-fonts-recommended"
}

# 解析命令行参数
case "${1:-}" in
    clean)
        cleanup "$(dirname "$(resolve_tex_path "document.tex")")"
        exit 0
        ;;
    --open)
        export OPEN_PDF=true
        main
        ;;
    --check-lines)
        export CHECK_PDF_LINES=true
        main "${2:-document.tex}"
        ;;
    help|--help|-h)
        show_help
        exit 0
        ;;
    "")
        main
        ;;
    *.tex)
        main "$1"
        ;;
    *)
        print_error "未知参数: $1"
        echo "使用 './compile.sh help' 查看帮助信息"
        exit 1
        ;;
esac
