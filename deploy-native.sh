#!/bin/bash
#
# 龙泉驿环卫智能体 - 原生部署脚本
# LQY Sanitation Intelligence - Native Deployment Script
#
# 使用方法: ./deploy-native.sh [command]
# 命令: start|stop|restart|status
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
LOGS_DIR="$PROJECT_DIR/logs"
PID_DIR="$PROJECT_DIR/pids"

# 环境变量
export $(cat "$PROJECT_DIR/.env" | grep -v '^#' | xargs)

# 创建必要目录
mkdir -p "$LOGS_DIR" "$PID_DIR"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."

    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi

    # 检查Node
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装"
        exit 1
    fi

    # 检查PostgreSQL
    if ! command -v psql &> /dev/null; then
        log_warn "PostgreSQL 客户端未安装，跳过数据库检查"
    fi

    log_success "依赖检查完成"
}

# 安装后端依赖
install_backend_deps() {
    log_info "安装后端依赖..."
    cd "$BACKEND_DIR"

    # 创建虚拟环境（如果不存在）
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "创建虚拟环境"
    fi

    # 激活虚拟环境
    source venv/bin/activate

    # 升级pip
    pip install --upgrade pip -q

    # 安装依赖
    pip install -r requirements.txt -q

    log_success "后端依赖安装完成"
}

# 安装前端依赖
install_frontend_deps() {
    log_info "安装前端依赖..."
    cd "$FRONTEND_DIR"

    # 安装依赖
    npm install --silent

    log_success "前端依赖安装完成"
}

# 数据库迁移
run_migrations() {
    log_info "执行数据库迁移..."
    cd "$BACKEND_DIR"

    source venv/bin/activate

    # 检查数据库连接
    if command -v psql &> /dev/null; then
        until PGPASSWORD="$POSTGRES_PASSWORD" psql -h localhost -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
            log_warn "等待PostgreSQL就绪..."
            sleep 2
        done
    fi

    # 运行迁移
    alembic upgrade head

    log_success "数据库迁移完成"
}

# 启动后端
start_backend() {
    log_info "启动后端服务..."
    cd "$BACKEND_DIR"

    source venv/bin/activate

    # 检查是否已在运行
    if [ -f "$PID_DIR/backend.pid" ]; then
        PID=$(cat "$PID_DIR/backend.pid")
        if ps -p "$PID" > /dev/null 2>&1; then
            log_warn "后端服务已在运行 (PID: $PID)"
            return
        fi
    fi

    # 启动服务
    nohup uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers 2 \
        --log-level info \
        > "$LOGS_DIR/backend.log" 2>&1 &

    echo $! > "$PID_DIR/backend.pid"
    log_success "后端服务启动完成 (PID: $(cat "$PID_DIR/backend.pid"))"
}

# 启动前端
start_frontend() {
    log_info "启动前端服务..."
    cd "$FRONTEND_DIR"

    # 检查是否已在运行
    if [ -f "$PID_DIR/frontend.pid" ]; then
        PID=$(cat "$PID_DIR/frontend.pid")
        if ps -p "$PID" > /dev/null 2>&1; then
            log_warn "前端服务已在运行 (PID: $PID)"
            return
        fi
    fi

    # 构建生产版本
    log_info "构建前端..."
    npm run build

    # 使用serve提供静态文件
    if ! command -v serve &> /dev/null; then
        npm install -g serve
    fi

    # 启动服务
    nohup serve dist \
        -l 8080 \
        --single \
        > "$LOGS_DIR/frontend.log" 2>&1 &

    echo $! > "$PID_DIR/frontend.pid"
    log_success "前端服务启动完成 (PID: $(cat "$PID_DIR/frontend.pid"))"
}

# 停止服务
stop_services() {
    log_info "停止服务..."

    # 停止后端
    if [ -f "$PID_DIR/backend.pid" ]; then
        PID=$(cat "$PID_DIR/backend.pid")
        if ps -p "$PID" > /dev/null 2>&1; then
            kill "$PID"
            log_success "后端服务已停止"
        fi
        rm -f "$PID_DIR/backend.pid"
    fi

    # 停止前端
    if [ -f "$PID_DIR/frontend.pid" ]; then
        PID=$(cat "$PID_DIR/frontend.pid")
        if ps -p "$PID" > /dev/null 2>&1; then
            kill "$PID"
            log_success "前端服务已停止"
        fi
        rm -f "$PID_DIR/frontend.pid"
    fi
}

# 查看状态
status() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE} 服务状态${NC}"
    echo -e "${BLUE}================================${NC}"

    # 检查后端
    if [ -f "$PID_DIR/backend.pid" ]; then
        PID=$(cat "$PID_DIR/backend.pid")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "后端服务: ${GREEN}运行中${NC} (PID: $PID)"
            echo -e "API地址: http://localhost:8000"
            echo -e "API文档: http://localhost:8000/docs"
        else
            echo -e "后端服务: ${RED}未运行${NC}"
        fi
    else
        echo -e "后端服务: ${RED}未运行${NC}"
    fi

    echo ""

    # 检查前端
    if [ -f "$PID_DIR/frontend.pid" ]; then
        PID=$(cat "$PID_DIR/frontend.pid")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "前端服务: ${GREEN}运行中${NC} (PID: $PID)"
            echo -e "访问地址: http://localhost:8080"
        else
            echo -e "前端服务: ${RED}未运行${NC}"
        fi
    else
        echo -e "前端服务: ${RED}未运行${NC}"
    fi

    echo -e "${BLUE}================================${NC}"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."

    # 检查后端API
    if curl -s http://localhost:8000/health > /dev/null; then
        log_success "后端API正常"
    else
        log_error "后端API异常"
    fi

    # 检查前端
    if curl -s http://localhost:8080 > /dev/null; then
        log_success "前端服务正常"
    else
        log_error "前端服务异常"
    fi
}

# 显示日志
tail_logs() {
    echo -e "${BLUE}后端日志:${NC}"
    tail -n 20 "$LOGS_DIR/backend.log" 2>/dev/null || echo "无日志"

    echo ""
    echo -e "${BLUE}前端日志:${NC}"
    tail -n 20 "$LOGS_DIR/frontend.log" 2>/dev/null || echo "无日志"
}

# 主函数
main() {
    case "$1" in
        install)
            check_dependencies
            install_backend_deps
            install_frontend_deps
            ;;
        migrate)
            run_migrations
            ;;
        start)
            start_backend
            sleep 2
            start_frontend
            sleep 2
            status
            health_check
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            sleep 2
            start_backend
            sleep 2
            start_frontend
            sleep 2
            status
            ;;
        status)
            status
            ;;
        health)
            health_check
            ;;
        logs)
            tail_logs
            ;;
        full-deploy)
            log_info "开始完整部署..."
            check_dependencies
            install_backend_deps
            install_frontend_deps
            run_migrations
            start_backend
            sleep 2
            start_frontend
            sleep 2
            status
            health_check
            log_success "部署完成！"
            ;;
        *)
            echo "龙泉驿环卫智能体 - 部署脚本"
            echo ""
            echo "使用方法: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  install       - 安装依赖"
            echo "  migrate       - 执行数据库迁移"
            echo "  start         - 启动服务"
            echo "  stop          - 停止服务"
            echo "  restart       - 重启服务"
            echo "  status        - 查看状态"
            echo "  health        - 健康检查"
            echo "  logs          - 查看日志"
            echo "  full-deploy   - 完整部署"
            echo ""
            exit 1
            ;;
    esac
}

main "$@"
