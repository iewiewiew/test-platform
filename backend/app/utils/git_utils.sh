#!/bin/bash

# 配置
# 示例配置（请根据实际情况修改）:
# GIT_CONFIG_DEFAULT_REPO_HTTP_URL="https://username:password@git.example.com/owner/repo.git"
# GIT_CONFIG_DEFAULT_REPO_SSH_URL="ssh://git@git.example.com:22/owner/repo.git"
# GIT_REPO_PATH="/path/to/local/repo"

TIME=$(date +%Y%m%d%H%M%S)
BRANCH="master"

# 日志函数（检测是否为终端，非终端不输出颜色）
if [ -t 1 ]; then
    log_info() { echo -e "\033[0;34m[INFO]\033[0m ${1}"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m ${1}"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m ${1}"; }
else
    log_info() { echo "[INFO] ${1}"; }
    log_success() { echo "[SUCCESS] ${1}"; }
    log_error() { echo "[ERROR] ${1}"; }
fi

# 检查 Git
check_git() { command -v git &> /dev/null || { log_error "Git 未安装"; exit 1; }; }

# 获取仓库路径
get_repo_path() {
    local protocol="${1}"
    local repo_name="${GIT_CONFIG_DEFAULT_REPO_HTTP_URL##*/}"
    repo_name="${repo_name%.git}"
    [ "${protocol}" = "tmp" ] && echo "${GIT_REPO_PATH}/${repo_name}-tmp" || echo "${GIT_REPO_PATH}/${repo_name}-${protocol}"
}

# 确保仓库存在（不存在则克隆）
ensure_repo() {
    local repo_path="${1}"
    local repo_url="${2}"
    [ -d "${repo_path}/.git" ] && rm -rf "${repo_path}"
    git clone "${repo_url}" "${repo_path}" 2>/dev/null || { log_error "克隆失败: ${repo_path}"; return 1; }
}

# 切换到 master 分支
switch_to_master() {
    local repo_path="${1}"
    cd "${repo_path}" || return 1
    git checkout "${BRANCH}" 2>/dev/null || git checkout -b "${BRANCH}" 2>/dev/null || true
}

# 在临时仓库中创建并推送内容
create_in_tmp_repo() {
    local tmp_repo_path="${1}"
    local action="${2}"  # file, lfs_file, branch, tag
    local name="${3}"
    
    ensure_repo "${tmp_repo_path}" "${GIT_CONFIG_DEFAULT_REPO_HTTP_URL}" || return 1
    switch_to_master "${tmp_repo_path}" || return 1
    
    case "${action}" in
        file)
            echo "# Test pull file ${TIME}" > "${name}"
            git add "${name}" 2>/dev/null
            git commit -m "Add ${name}" 2>/dev/null || true
            git push origin "${BRANCH}" 2>/dev/null || return 1
            ;;
        lfs_file)
            command -v git-lfs &> /dev/null || return 1
            git lfs install 2>/dev/null || true
            git lfs track "${name}" 2>/dev/null || true
            echo "LFS pull test ${TIME}" > "${name}"
            git add .gitattributes "${name}" 2>/dev/null
            git commit -m "Add ${name}" 2>/dev/null || true
            git push origin "${BRANCH}" 2>/dev/null || return 1
            ;;
        branch)
            git checkout -b "${name}" 2>/dev/null || true
            git push -u origin "${name}" 2>/dev/null || return 1
            ;;
        tag)
            git tag -a "${name}" -m "Tag pull test" 2>/dev/null || true
            git push origin "${name}" 2>/dev/null || return 1
            ;;
    esac
}

# 执行所有 Git 操作
execute_all() {
    check_git
    
    local http_repo_path=$(get_repo_path "http")
    local ssh_repo_path=$(get_repo_path "ssh")
    local tmp_repo_path=$(get_repo_path "tmp")

    log_success "开始执行 Git 操作..."
    
    # 1. 克隆仓库（HTTP 和 SSH）
    log_info "【1/11】克隆仓库..."
    ensure_repo "${http_repo_path}" "${GIT_CONFIG_DEFAULT_REPO_HTTP_URL}"
    ensure_repo "${ssh_repo_path}" "${GIT_CONFIG_DEFAULT_REPO_SSH_URL}"
    [ ! -d "${http_repo_path}/.git" ] && { log_error "HTTP 仓库不存在"; exit 1; }
    
    switch_to_master "${http_repo_path}"
    
    # 2. 推送本地文件
    log_info "【2/11】推送文件..."
    local push_file="test-push-${TIME}.txt"
    echo "# Test file ${TIME}" > "${push_file}"
    git add "${push_file}" 2>/dev/null
    git commit -m "Add test-push file" 2>/dev/null || true
    git push origin "${BRANCH}" 2>/dev/null || log_error "推送文件失败"
    
    # 3. 拉取远程文件
    log_info "【3/11】拉取文件..."
    local pull_file="test-pull-${TIME}.txt"
    create_in_tmp_repo "${tmp_repo_path}" "file" "${pull_file}" && {
        cd "${http_repo_path}" || exit 1
        switch_to_master "${http_repo_path}"
        git pull origin "${BRANCH}" 2>/dev/null || log_error "拉取文件失败"
    }
    
    # 4. 推送 LFS 文件
    log_info "【4/11】推送 LFS 文件..."
    if command -v git-lfs &> /dev/null; then
        cd "${http_repo_path}" || exit 1
        switch_to_master "${http_repo_path}"
        git lfs install 2>/dev/null || true
        local lfs_file="test-lfs-push-${TIME}.txt"
        echo "LFS test ${TIME}" > "${lfs_file}"
        git lfs track "test-lfs-push-*.txt" 2>/dev/null || true
        git add .gitattributes "${lfs_file}" 2>/dev/null
        git commit -m "Add test-lfs-push file" 2>/dev/null || true
        git push origin "${BRANCH}" 2>/dev/null || log_error "推送 LFS 失败"
    fi
    
    # 5. 拉取远程 LFS 文件
    log_info "【5/11】拉取 LFS 文件..."
    if command -v git-lfs &> /dev/null; then
        local lfs_pull_file="test-lfs-pull-${TIME}.txt"
        create_in_tmp_repo "${tmp_repo_path}" "lfs_file" "${lfs_pull_file}" && {
            cd "${http_repo_path}" || exit 1
            switch_to_master "${http_repo_path}"
            git lfs pull origin 2>/dev/null || log_error "拉取 LFS 失败"
        }
    fi
    
    # 6. 推送本地分支
    log_info "【6/11】推送分支..."
    cd "${http_repo_path}" || exit 1
    switch_to_master "${http_repo_path}"
    local new_branch="branch-push-${TIME}"
    git checkout -b "${new_branch}" 2>/dev/null || true
    git push -u origin "${new_branch}" 2>/dev/null || log_error "推送分支失败"
    git checkout "${BRANCH}" 2>/dev/null || true
    
    # 7. 拉取远程分支
    log_info "【7/11】拉取分支..."
    local pull_branch="branch-pull-${TIME}"
    create_in_tmp_repo "${tmp_repo_path}" "branch" "${pull_branch}" && {
        cd "${http_repo_path}" || exit 1
        switch_to_master "${http_repo_path}"
        git pull origin "${BRANCH}" 2>/dev/null || true  # 先更新 master
        git fetch origin 2>/dev/null || log_error "获取远程分支失败"
        if git show-ref --verify --quiet "refs/remotes/origin/${pull_branch}" 2>/dev/null; then
            git checkout -b "${pull_branch}" "origin/${pull_branch}" 2>/dev/null || log_error "拉取分支失败"
            git checkout "${BRANCH}" 2>/dev/null || true
        else
            log_error "远程分支 ${pull_branch} 不存在"
        fi
    }
    
    # 8. 删除远程分支
    log_info "【8/11】删除远程分支..."
    cd "${http_repo_path}" || exit 1
    git push origin --delete "${new_branch}" 2>/dev/null || log_error "删除远程分支失败"
    
    # 9. 推送本地标签
    log_info "【9/11】推送标签..."
    cd "${http_repo_path}" || exit 1
    local tag_name="tag_push_${TIME}"
    git tag -a "${tag_name}" -m "Test tag" 2>/dev/null || true
    git push origin "${tag_name}" 2>/dev/null || log_error "推送标签失败"
    
    # 10. 拉取远程标签
    log_info "【10/11】拉取标签..."
    local pull_tag="tag-pull-${TIME}"
    create_in_tmp_repo "${tmp_repo_path}" "tag" "${pull_tag}" && {
        cd "${http_repo_path}" || exit 1
        git fetch origin --tags 2>/dev/null || log_error "拉取标签失败"
    }
    
    # 11. 删除远程标签
    log_info "【11/11】删除远程标签..."
    cd "${http_repo_path}" || exit 1
    git push origin --delete "${tag_name}" 2>/dev/null || log_error "删除远程标签失败"
    
    log_success "所有 Git 操作执行完成！"
    
    # 清理
    log_info "清理仓库... ${http_repo_path} ${ssh_repo_path} ${tmp_repo_path}"
    rm -rf "${http_repo_path}" "${ssh_repo_path}" "${tmp_repo_path}" 2>/dev/null
}

# 主入口
[ "${BASH_SOURCE[0]}" = "${0}" ] && execute_all

# sh backend/app/utils/git_utils.sh > .tmp/tmp/git_utils.log