#!/bin/bash
#
# 环境检查脚本
# Environment Check Script
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "================================"
echo "龙泉驿环卫智能体 - 环境检查"
echo "================================"
echo ""

# 检查系统命令
echo -e "${BLUE}检查系统依赖...${NC}"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    check_pass "Python: $PYTHON_VERSION"
else
    check_fail "Python3 未安装"
fi

if command -v pip3 &> /dev/null; then
    check_pass "pip3: 已安装"
else
    check_warn "pip3 未安装"
fi

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    check_pass "Node.js: $NODE_VERSION"
else
    check_fail "Node.js 未安装"
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    check_pass "npm: $NPM_VERSION"
else
    check_fail "npm 未安装"
fi

echo ""
echo -e "${BLUE}检查数据库...${NC}"

if command -v psql &> /dev/null; then
    PG_VERSION=$(psql --version | head -n1)
    check_pass "PostgreSQL: $PG_VERSION"
else
    check_warn "PostgreSQL客户端未安装"
fi

if command -v redis-cli &> /dev/null; then
    REDIS_VERSION=$(redis-cli --version)
    check_pass "Redis: $REDIS_VERSION"
else
    check_warn "Redis客户端未安装"
fi

echo ""
echo -e "${BLUE}检查Docker...${NC}"

if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    check_pass "Docker: $DOCKER_VERSION"
else
    check_warn "Docker 未安装（可选）"
fi

if command -v docker-compose &> /dev/null; then
    DC_VERSION=$(docker-compose --version)
    check_pass "Docker Compose: $DC_VERSION"
else
    check_warn "Docker Compose 未安装（可选）"
fi

echo ""
echo -e "${BLUE}检查项目文件...${NC}"

if [ -f ".env" ]; then
    check_pass ".env 文件存在"
else
    check_fail ".env 文件缺失"
fi

if [ -f "docker-compose.yml" ]; then
    check_pass "docker-compose.yml 存在"
else
    check_warn "docker-compose.yml 缺失"
fi

if [ -f "deploy-native.sh" ]; then
    check_pass "deploy-native.sh 存在"
else
    check_fail "deploy-native.sh 缺失"
fi

if [ -d "backend" ]; then
    check_pass "backend 目录存在"
else
    check_fail "backend 目录缺失"
fi

if [ -d "frontend" ]; then
    check_pass "frontend 目录存在"
else
    check_fail "frontend 目录缺失"
fi

echo ""
echo -e "${BLUE}检查环境变量...${NC}"

if [ -f ".env" ]; then
    # 检查关键变量
    if grep -q "KIMI_API_KEY" .env; then
        check_pass "KIMI_API_KEY 已配置"
    else
        check_warn "KIMI_API_KEY 未配置"
    fi

    if grep -q "DATABASE_URL" .env; then
        check_pass "DATABASE_URL 已配置"
    else
        check_warn "DATABASE_URL 未配置"
    fi

    if grep -q "SECRET_KEY" .env; then
        check_pass "SECRET_KEY 已配置"
    else
        check_warn "SECRET_KEY 未配置"
    fi
fi

echo ""
echo -e "${BLUE}检查端口占用...${NC}"

if command -v lsof &> /dev/null; then
    if lsof -i :8000 &> /dev/null; then
        check_warn "端口 8000 已被占用"
    else
        check_pass "端口 8000 可用"
    fi

    if lsof -i :8080 &> /dev/null; then
        check_warn "端口 8080 已被占用"
    else
        check_pass "端口 8080 可用"
    fi
else
    check_warn "无法检查端口（lsof未安装）"
fi

echo ""
echo "================================"
echo -e "${GREEN}环境检查完成！${NC}"
echo "================================"
echo ""
echo "如果发现缺少的依赖，请安装:"
echo "  - Ubuntu/Debian: sudo apt install python3 python3-pip nodejs npm"
echo "  - CentOS/RHEL:   sudo yum install python3 python3-pip nodejs npm"
echo ""
