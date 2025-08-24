#!/bin/bash

# SuperMoment Universal Launcher
# Combines all functionalities in one file

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the SuperMoment directory
cd "$SCRIPT_DIR"

echo "📍 Working directory: $(pwd)"
echo ""

# Function to check status
check_status() {
    echo "🔍 Checking service status..."
    echo ""
    
    # Check backend
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Backend: 🟢 ACTIVE on http://localhost:8000"
        BACKEND_STATUS="🟢 ACTIVE"
    else
        echo "❌ Backend: 🔴 INACTIVE"
        BACKEND_STATUS="🔴 INACTIVE"
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 > /dev/null; then
        echo "✅ Frontend: 🟢 ACTIVE on http://localhost:3000"
        FRONTEND_STATUS="🟢 ACTIVE"
    else
        echo "❌ Frontend: 🔴 INACTIVE"
        FRONTEND_STATUS="🔴 INACTIVE"
    fi
    
    echo ""
    echo "📊 Status Summary:"
    echo "=================="
    echo "Backend:  $BACKEND_STATUS"
    echo "Frontend: $FRONTEND_STATUS"
    echo ""
    
    if [[ "$BACKEND_STATUS" == "🟢 ACTIVE" && "$FRONTEND_STATUS" == "🟢 ACTIVE" ]]; then
        echo "🎉 SuperMoment is fully functional!"
        echo ""
        echo "🌐 Available links:"
        echo "   Frontend Admin: http://localhost:3000"
        echo "   Backend API:    http://localhost:8000"
        echo "   API Docs:       http://localhost:8000/docs"
    fi
}

# Function to start services
start_services() {
    echo "🚀 Starting SuperMoment services..."
    echo "=================================="
    echo ""
    
    # Check if already running
    if curl -s http://localhost:8000/health > /dev/null && curl -s http://localhost:3000 > /dev/null; then
        echo "⚠️  SuperMoment is already running!"
        check_status
        return
    fi
    
    # Activate virtual environment
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        echo "🔧 Activating virtual environment..."
        source supermoment-env/bin/activate
    fi
    
    # Check if main.py exists
    if [ ! -f "backend/main.py" ]; then
        echo "❌ Error: You are not in the SuperMoment directory!"
        echo "Go to the SuperMoment directory and try again."
        read -p "Press Enter to exit..."
        exit 1
    fi
    
    # Install frontend dependencies if missing
    if [ ! -d "frontend/node_modules" ]; then
        echo "📦 Installing frontend dependencies..."
        cd frontend
        npm install
        cd ..
    fi
    
    # Start backend
    echo "🔧 Starting backend server..."
    cd backend
    python main.py &
    BACKEND_PID=$!
    cd ..
    
    echo "⏳ Waiting for backend to start..."
    sleep 5
    
    # Check if backend started successfully
    if ! curl -s http://localhost:8000/health > /dev/null; then
        echo "❌ Backend failed to start!"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    echo "✅ Backend is running!"
    
    # Start frontend
    echo "🎨 Starting frontend application..."
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    echo "⏳ Waiting for frontend to start..."
    sleep 8
    
    # Check if frontend started successfully
    if ! curl -s http://localhost:3000 > /dev/null; then
        echo "❌ Frontend failed to start!"
        kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
        exit 1
    fi
    echo "✅ Frontend is running!"
    
    echo ""
    echo "🎉 SuperMoment started successfully!"
    echo "=================================="
    echo "🌐 Frontend Admin: http://localhost:3000"
    echo "🔧 Backend API:    http://localhost:8000"
    echo "📚 API Docs:       http://localhost:8000/docs"
    echo ""
    echo "🛑 Press Ctrl+C to stop all services"
    echo ""
    
    # Cleanup function
    cleanup() {
        echo ""
        echo "🛑 Stopping services..."
        kill $BACKEND_PID 2>/dev/null
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Services stopped."
        exit 0
    }
    
    trap cleanup INT
    wait
}

# Function to start with browser
start_with_browser() {
    echo "🚀 Starting SuperMoment with browser..."
    echo "======================================"
    echo ""
    
    # Start services in background
    start_services &
    SERVICES_PID=$!
    
    # Wait for services to start
    echo "⏳ Waiting for services to start..."
    sleep 15
    
    # Check if services started
    if curl -s http://localhost:8000/health > /dev/null && curl -s http://localhost:3000 > /dev/null; then
        echo "🌐 Opening browser..."
        open http://localhost:3000
        echo "✅ Browser opened!"
    else
        echo "❌ Services did not start in expected time."
        kill $SERVICES_PID 2>/dev/null
        exit 1
    fi
    
    # Wait for user to stop
    echo ""
    echo "🛑 Press Ctrl+C to stop"
    wait $SERVICES_PID
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping SuperMoment services..."
    echo "=================================="
    echo ""
    
    # Find and stop processes
    BACKEND_PIDS=$(lsof -ti:8000 2>/dev/null)
    FRONTEND_PIDS=$(lsof -ti:3000 2>/dev/null)
    
    if [ ! -z "$BACKEND_PIDS" ]; then
        echo "🔧 Stopping backend processes..."
        kill $BACKEND_PIDS
        echo "✅ Backend stopped."
    else
        echo "ℹ️  Backend was not running."
    fi
    
    if [ ! -z "$FRONTEND_PIDS" ]; then
        echo "🎨 Stopping frontend processes..."
        kill $FRONTEND_PIDS
        echo "✅ Frontend stopped."
    else
        echo "ℹ️  Frontend was not running."
    fi
    
    echo ""
    echo "✅ All SuperMoment services stopped."
}

# Function to restart services
restart_services() {
    echo "🔄 Restart SuperMoment services..."
    echo "================================="
    echo ""
    
    stop_services
    sleep 2
    start_services
}

# Main menu
show_menu() {
    clear
    echo "🚀 SuperMoment Universal Launcher"
    echo "================================"
    echo ""
    echo "Select option:"
    echo ""
    echo "1️⃣  🚀 Start services"
    echo "2️⃣  🌐 Start + open browser"
    echo "3️⃣  🔍 Check status"
    echo "4️⃣  🛑 Stop services"
    echo "5️⃣  🔄 Restart services"
            echo "6️⃣  📚 Open API documentation"
        echo "7️⃣  🎨 Open frontend admin"
        echo "8️⃣  🔧 Open backend API"
        echo "9️⃣  🔐 Open login page"
        echo "0️⃣  ❌ Exit"
    echo ""
}

# Main logic
main() {
    while true; do
        show_menu
        read -p "Enter option number (1-9, 0): " choice
        
        case $choice in
            1)
                echo ""
                start_services
                break
                ;;
            2)
                echo ""
                start_with_browser
                break
                ;;
            3)
                echo ""
                check_status
                echo ""
                read -p "Press Enter to return to menu..."
                ;;
            4)
                echo ""
                stop_services
                echo ""
                read -p "Press Enter to return to menu..."
                ;;
            5)
                echo ""
                restart_services
                break
                ;;
            6)
                echo ""
                echo "📚 Opening API documentation..."
                open http://localhost:8000/docs
                echo "✅ API documentation opened in browser."
                echo ""
                read -p "Press Enter to return to menu..."
                ;;
            7)
                echo ""
                echo "🎨 Opening frontend admin panel..."
                open http://localhost:3000
                echo "✅ Frontend admin opened in browser."
                echo ""
                read -p "Press Enter to return to menu..."
                ;;
            8)
                echo ""
                echo "🔧 Opening backend API..."
                open http://localhost:8000
                echo "✅ Backend API opened in browser."
                echo ""
                read -p "Press Enter to return to menu..."
                ;;
            9)
                echo ""
                echo "🔐 Opening login page..."
                open http://localhost:3000/login
                echo "✅ Login page opened in browser."
                echo ""
                read -p "Press Enter to return to menu..."
                ;;
            0)
                echo ""
                echo "👋 Goodbye!"
                exit 0
                ;;
            *)
                echo ""
                echo "❌ Invalid option. Try again."
                sleep 2
                ;;
        esac
    done
}

# Start main menu
main
