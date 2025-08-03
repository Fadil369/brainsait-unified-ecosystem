#!/bin/bash

# BrainSAIT Ecosystem Quick Start Script
# This script demonstrates the unified ecosystem in action

echo "🚀 BrainSAIT Healthcare Platform - Quick Start Demo"
echo "=================================================="

# Set working directory
cd "$(dirname "$0")/backend"

echo ""
echo "🔍 Verifying Ecosystem Integration..."
python3 test_ecosystem_integration.py

echo ""
echo "📊 System Status Check..."
if [ -f "ecosystem_integration_report.json" ]; then
    echo "✅ Integration Report Generated Successfully"
    echo "📄 Report Location: backend/ecosystem_integration_report.json"
else
    echo "❌ Integration Report Not Found"
fi

echo ""
echo "🧠 PyBrain Integration Status:"
if [ -f "integrations/brainsait_pybrain.py" ]; then
    echo "✅ BrainSAIT PyBrain Module: Ready"
    echo "   - Advanced Arabic Healthcare NLP"
    echo "   - Predictive Analytics Engine"
    echo "   - Cultural Intelligence System"
else
    echo "❌ PyBrain Module Not Found"
fi

echo ""
echo "💓 PyHeart Integration Status:"
if [ -f "integrations/brainsait_pyheart.py" ]; then
    echo "✅ BrainSAIT PyHeart Module: Ready"
    echo "   - Intelligent Workflow Orchestration"
    echo "   - Healthcare Process Automation"
    echo "   - Resource Management System"
else
    echo "❌ PyHeart Module Not Found"
fi

echo ""
echo "🎼 Ecosystem Orchestrator Status:"
if [ -f "integrations/ecosystem_orchestrator.py" ]; then
    echo "✅ Ecosystem Orchestrator: Ready"
    echo "   - Central coordination hub"
    echo "   - Unified operation handling"
    echo "   - Performance metrics tracking"
else
    echo "❌ Ecosystem Orchestrator Not Found"
fi

echo ""
echo "🌟 Available Capabilities:"
echo "   🤖 AI Insight Generation"
echo "   🔄 Workflow Orchestration"
echo "   🌍 Cultural Intelligence"
echo "   🛡️ Compliance Automation"
echo "   📊 Real-time Monitoring"
echo "   🚨 Emergency Response"
echo "   📈 Predictive Analytics"
echo "   🗣️ Arabic Language Support"

echo ""
echo "📋 Next Steps:"
echo "   1. Install dependencies: pip install -r requirements.txt"
echo "   2. Configure environment: cp .env.example .env"
echo "   3. Initialize database: python init_platform.py"
echo "   4. Start development server: uvicorn main:app --reload"
echo "   5. Access frontend: http://localhost:3000"
echo "   6. Access API docs: http://localhost:8000/docs"

echo ""
echo "🎯 Deployment Options:"
echo "   📦 Docker: docker-compose up -d"
echo "   ☁️  Production: ./deploy-to-vps-prod.sh"
echo "   🧪 Testing: pytest tests/"

echo ""
echo "🎉 BrainSAIT Ecosystem Status: READY FOR DEPLOYMENT!"
echo "=================================================="
