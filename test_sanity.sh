#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC} - $2"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC} - $2"
        ((FAILED++))
    fi
}

# Function to check if service is running
check_service() {
    docker-compose ps | grep -q "$1.*Up"
    return $?
}

echo -e "${BLUE}=== Image Description Service Sanity Tests ===${NC}"
echo ""

# Test 1: Check if services are running
echo -e "${YELLOW}1. Checking service status...${NC}"
check_service "redis" && print_result 0 "Redis service is running" || print_result 1 "Redis service is not running"
check_service "web" && print_result 0 "Web service is running" || print_result 1 "Web service is not running"
check_service "worker" && print_result 0 "Worker service is running" || print_result 1 "Worker service is not running"

# Test 2: Test health endpoint
echo -e "${YELLOW}2. Testing health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:${WEB_PORT:-8000}/health 2>/dev/null)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    print_result 0 "Health endpoint is working"
else
    print_result 1 "Health endpoint is not working"
fi

# Test 3: Test API documentation
echo -e "${YELLOW}3. Testing API documentation...${NC}"
DOCS_RESPONSE=$(curl -s http://localhost:${WEB_PORT:-8000}/docs 2>/dev/null)
if echo "$DOCS_RESPONSE" | grep -q "swagger"; then
    print_result 0 "API documentation is accessible"
else
    print_result 1 "API documentation is not accessible"
fi

# Test 4: Test Redis connection
echo -e "${YELLOW}4. Testing Redis connection...${NC}"
REDIS_PING=$(docker exec image-service-redis redis-cli ping 2>/dev/null)
if [ "$REDIS_PING" = "PONG" ]; then
    print_result 0 "Redis connection is working"
else
    print_result 1 "Redis connection is not working"
fi

# Test 5: Test image upload
echo -e "${YELLOW}5. Testing image upload...${NC}"
if [ -f "/mnt/c/Users/Celestite/Downloads/pexels-photo-15210705-939182326.jpeg" ]; then
    UPLOAD_RESPONSE=$(curl -s -X POST "http://localhost:${WEB_PORT:-8000}/api/v1/submit" \
        -H "accept: application/json" \
        -H "Content-Type: multipart/form-data" \
        -F "file=@/mnt/c/Users/Celestite/Downloads/pexels-photo-15210705-939182326.jpeg" 2>/dev/null)
    
    if echo "$UPLOAD_RESPONSE" | grep -q "job_id"; then
        print_result 0 "Image upload is working"
        JOB_ID=$(echo "$UPLOAD_RESPONSE" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)
        echo "   Job ID: $JOB_ID"
        
        # Test 6: Test job status
        echo -e "${YELLOW}6. Testing job status...${NC}"
        sleep 3
        STATUS_RESPONSE=$(curl -s "http://localhost:${WEB_PORT:-8000}/api/v1/status/$JOB_ID" 2>/dev/null)
        if echo "$STATUS_RESPONSE" | grep -q "job_id"; then
            print_result 0 "Job status endpoint is working"
            echo "   Status: $(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)"
        else
            print_result 1 "Job status endpoint is not working"
        fi
        
        # Test 7: Test job result (wait a bit longer)
        echo -e "${YELLOW}7. Testing job result...${NC}"
        sleep 10
        RESULT_RESPONSE=$(curl -s "http://localhost:${WEB_PORT:-8000}/api/v1/result/$JOB_ID" 2>/dev/null)
        if echo "$RESULT_RESPONSE" | grep -q "job_id"; then
            print_result 0 "Job result endpoint is working"
            if echo "$RESULT_RESPONSE" | grep -q "image_description"; then
                print_result 0 "Image processing completed successfully"
                echo "   Description: $(echo "$RESULT_RESPONSE" | grep -o '"image_description":"[^"]*"' | cut -d'"' -f4 | head -c 100)..."
            else
                print_result 1 "Image processing did not complete"
            fi
        else
            print_result 1 "Job result endpoint is not working"
        fi
    else
        print_result 1 "Image upload is not working"
    fi
else
    print_result 1 "Test image not found at /mnt/c/Users/Celestite/Downloads/pexels-photo-15210705-939182326.jpeg"
fi

# Test 8: Test error handling
echo -e "${YELLOW}8. Testing error handling...${NC}"
ERROR_RESPONSE=$(curl -s -w "%{http_code}" "http://localhost:${WEB_PORT:-8000}/api/v1/status/invalid-id" 2>/dev/null | tail -1)
if [ "$ERROR_RESPONSE" = "404" ]; then
    print_result 0 "Error handling is working (404 for invalid job ID)"
else
    print_result 1 "Error handling is not working properly"
fi

# Test 9: Test database
echo -e "${YELLOW}9. Testing database...${NC}"
if [ -f "data/app.db" ]; then
    print_result 0 "Database file exists"
    DB_COUNT=$(sqlite3 data/app.db "SELECT COUNT(*) FROM jobs;" 2>/dev/null)
    if [ "$DB_COUNT" -ge 0 ]; then
        print_result 0 "Database is accessible"
        echo "   Jobs in database: $DB_COUNT"
    else
        print_result 1 "Database is not accessible"
    fi
else
    print_result 1 "Database file does not exist"
fi

# Test 10: Test Celery worker logs
echo -e "${YELLOW}10. Testing Celery worker...${NC}"
WORKER_LOGS=$(docker-compose logs worker 2>/dev/null | grep -c "process_image_task" || echo "0")
if [ "$WORKER_LOGS" -gt 0 ]; then
    print_result 0 "Celery worker is processing tasks"
    echo "   Tasks processed: $WORKER_LOGS"
else
    print_result 1 "Celery worker is not processing tasks"
fi

echo ""
echo -e "${BLUE}=== Test Summary ===${NC}"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "Total: $((PASSED + FAILED))"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Your service is working correctly.${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Check the output above for details.${NC}"
    exit 1
fi 