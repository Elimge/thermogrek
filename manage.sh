#!/usr/bin/env bash
# ==============================================================================
# ThermoGrek - Operational Management CLI
# ==============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${PROJECT_DIR}/backups"

print_header() {
    echo -e "\033[1;34m=== ThermoGrek Platform Manager ===\033[0m"
}

case "$1" in
    start)
        print_header
        echo "Starting all ThermoGrek services in background..."
        docker compose up -d
        echo -e "\033[1;32mStack started successfully.\033[0m"
        echo "Frontend: http://127.0.0.1:5174"
        echo "API Docs: http://127.0.0.1:8001/docs"
        ;;

    stop)
        print_header
        echo "Stopping all ThermoGrek services (preserving database volume)..."
        docker compose stop
        echo -e "\033[1;33mStack paused. Host memory freed.\033[0m"
        ;;

    restart)
        print_header
        echo "Restarting services..."
        docker compose restart
        ;;

    status)
        print_header
        docker compose ps
        echo ""
        echo -e "\033[1;36mMemory & CPU Utilization:\033[0m"
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
        ;;

    test)
        print_header
        echo "Running automated Unit & Integration test suites..."
        docker run --rm -v "${PROJECT_DIR}:/app" -w /app python:3.12-slim bash -c "pip install --quiet pytest pydantic && pytest tests/unit/ -v"
        docker run --rm --network thermogrek_thermogrek-net -v "${PROJECT_DIR}:/app" -w /app python:3.12-slim bash -c "pip install --quiet pytest httpx && pytest tests/integration/ -v"
        echo -e "\033[1;32mAll test suites passed successfully!\033[0m"
        ;;

    backup)
        print_header
        mkdir -p "${BACKUP_DIR}"
        TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")
        BACKUP_FILE="${BACKUP_DIR}/thermogrek_backup_${TIMESTAMP}.sql"
        echo "Generating full PostgreSQL backup to: ${BACKUP_FILE}..."
        docker exec -t thermogrek-db pg_dump -U thermogrek_user -d thermogrek_db > "${BACKUP_FILE}"
        echo -e "\033[1;32mBackup completed successfully.\033[0m File size: $(du -h "${BACKUP_FILE}" | cut -f1)"
        ;;

    logs)
        docker compose logs -f --tail 50
        ;;

    *)
        print_header
        echo "Usage: ./manage.sh {start|stop|restart|status|test|backup|logs}"
        exit 1
        ;;
esac
