#!/bin/bash
# Master script to manage all Docker services for Augment Adam

set -e

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Define service types
SERVICES=(
    "mcp-context-engine"
    "api"
    "ollama"
)

# Define the base directory for service compose files
DOCKER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_DIR="${DOCKER_DIR}/services"

# Function to display usage information
usage() {
    echo -e "${BLUE}Augment Adam Service Management Script${NC}"
    echo ""
    echo "Usage: $0 [service] [command]"
    echo ""
    echo "Services:"
    echo "  all                - Manage all services"
    for service in "${SERVICES[@]}"; do
        echo "  $service"
    done
    echo ""
    echo "Commands:"
    echo "  start              - Start the specified service(s)"
    echo "  stop               - Stop the specified service(s)"
    echo "  restart            - Restart the specified service(s)"
    echo "  status             - Check the status of the specified service(s)"
    echo "  logs [service]     - View logs for the specified service(s)"
    echo "  build              - Build the specified service(s)"
    echo "  clean              - Remove containers and volumes for the specified service(s)"
    echo "  create-volumes     - Create required Docker volumes"
    echo "  help               - Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0 all start       - Start all services"
    echo "  $0 mcp-context-engine logs - View logs for the MCP Context Engine service"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
        exit 1
    fi
}

# Function to check if Docker Compose is installed
check_docker_compose() {
    if ! docker compose version > /dev/null 2>&1; then
        echo -e "${RED}Error: Docker Compose is not installed. Please install Docker Compose and try again.${NC}"
        exit 1
    fi
}

# Function to get the compose file path for a service
get_compose_file() {
    local service=$1
    local compose_file="${SERVICE_DIR}/${service}/docker-compose.yml"
    
    if [ ! -f "$compose_file" ]; then
        echo -e "${RED}Error: Compose file for service '${service}' not found at ${compose_file}${NC}"
        exit 1
    fi
    
    echo "$compose_file"
}

# Function to start a service
start_service() {
    local service=$1
    local compose_file=$(get_compose_file "$service")
    
    echo -e "${GREEN}Starting ${service} service...${NC}"
    docker compose -f "$compose_file" up -d
    echo -e "${GREEN}${service} service started successfully.${NC}"
}

# Function to stop a service
stop_service() {
    local service=$1
    local compose_file=$(get_compose_file "$service")
    
    echo -e "${YELLOW}Stopping ${service} service...${NC}"
    docker compose -f "$compose_file" down
    echo -e "${GREEN}${service} service stopped successfully.${NC}"
}

# Function to restart a service
restart_service() {
    local service=$1
    local compose_file=$(get_compose_file "$service")
    
    echo -e "${YELLOW}Restarting ${service} service...${NC}"
    docker compose -f "$compose_file" restart
    echo -e "${GREEN}${service} service restarted successfully.${NC}"
}

# Function to check service status
check_status() {
    local service=$1
    local compose_file=$(get_compose_file "$service")
    
    echo -e "${GREEN}Checking ${service} service status...${NC}"
    docker compose -f "$compose_file" ps
}

# Function to view logs
view_logs() {
    local service=$1
    local container=$2
    local compose_file=$(get_compose_file "$service")
    
    if [ -z "$container" ]; then
        echo -e "${GREEN}Viewing logs for all ${service} services...${NC}"
        docker compose -f "$compose_file" logs --tail=100 -f
    else
        echo -e "${GREEN}Viewing logs for ${container} in ${service}...${NC}"
        docker compose -f "$compose_file" logs --tail=100 -f "$container"
    fi
}

# Function to build services
build_service() {
    local service=$1
    local compose_file=$(get_compose_file "$service")
    
    echo -e "${GREEN}Building ${service} service...${NC}"
    docker compose -f "$compose_file" build
    echo -e "${GREEN}${service} service built successfully.${NC}"
}

# Function to clean up
clean_service() {
    local service=$1
    local compose_file=$(get_compose_file "$service")
    
    echo -e "${YELLOW}Removing all ${service} containers and volumes...${NC}"
    docker compose -f "$compose_file" down -v
    echo -e "${GREEN}${service} cleanup completed successfully.${NC}"
}

# Function to create required Docker volumes
create_volumes() {
    echo -e "${GREEN}Creating required Docker volumes...${NC}"
    
    # Create volumes with specific names
    docker volume create augment-adam-ollama-models || echo "Volume already exists"
    docker volume create augment-adam-model-cache || echo "Volume already exists"
    docker volume create augment-adam-huggingface-cache || echo "Volume already exists"
    docker volume create augment-adam-pip-cache || echo "Volume already exists"
    docker volume create augment-adam-apt-cache || echo "Volume already exists"
    docker volume create augment-adam-torch-cache || echo "Volume already exists"
    docker volume create augment-adam-chroma-data || echo "Volume already exists"
    docker volume create augment-adam-neo4j-data || echo "Volume already exists"
    docker volume create augment-adam-redis-data || echo "Volume already exists"
    docker volume create augment-adam-redis-vector-data || echo "Volume already exists"
    
    echo -e "${GREEN}Docker volumes created successfully.${NC}"
    docker volume ls | grep augment-adam
}

# Function to execute a command for all services
execute_all() {
    local command=$1
    local extra_arg=$2
    
    for service in "${SERVICES[@]}"; do
        case "$command" in
            start)
                start_service "$service"
                ;;
            stop)
                stop_service "$service"
                ;;
            restart)
                restart_service "$service"
                ;;
            status)
                check_status "$service"
                ;;
            logs)
                view_logs "$service" "$extra_arg"
                ;;
            build)
                build_service "$service"
                ;;
            clean)
                clean_service "$service"
                ;;
            *)
                echo -e "${RED}Unknown command: $command${NC}"
                usage
                exit 1
                ;;
        esac
    done
}

# Main script logic
check_docker
check_docker_compose

# Process command line arguments
if [ $# -lt 1 ]; then
    usage
    exit 1
fi

SERVICE=$1
COMMAND=$2
EXTRA_ARG=$3

case "$SERVICE" in
    all)
        case "$COMMAND" in
            start|stop|restart|status|logs|build|clean)
                execute_all "$COMMAND" "$EXTRA_ARG"
                ;;
            create-volumes)
                create_volumes
                ;;
            help|--help|-h)
                usage
                ;;
            *)
                echo -e "${RED}Unknown command: $COMMAND${NC}"
                usage
                exit 1
                ;;
        esac
        ;;
    create-volumes)
        create_volumes
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        # Check if the service is valid
        VALID_SERVICE=false
        for service in "${SERVICES[@]}"; do
            if [ "$SERVICE" = "$service" ]; then
                VALID_SERVICE=true
                break
            fi
        done
        
        if [ "$VALID_SERVICE" = false ]; then
            echo -e "${RED}Unknown service: $SERVICE${NC}"
            usage
            exit 1
        fi
        
        case "$COMMAND" in
            start)
                start_service "$SERVICE"
                ;;
            stop)
                stop_service "$SERVICE"
                ;;
            restart)
                restart_service "$SERVICE"
                ;;
            status)
                check_status "$SERVICE"
                ;;
            logs)
                view_logs "$SERVICE" "$EXTRA_ARG"
                ;;
            build)
                build_service "$SERVICE"
                ;;
            clean)
                clean_service "$SERVICE"
                ;;
            *)
                echo -e "${RED}Unknown command: $COMMAND${NC}"
                usage
                exit 1
                ;;
        esac
        ;;
esac

exit 0
