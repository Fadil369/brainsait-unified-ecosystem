-- BrainSAIT Healthcare Unification Platform Database Schema
-- Enhanced for NPHIES integration and healthcare identity management

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enhanced healthcare identities table
CREATE TABLE IF NOT EXISTS healthcare_identities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    name VARCHAR(500) NOT NULL,
    name_ar VARCHAR(500),
    role VARCHAR(100) NOT NULL,
    access_level VARCHAR(50) NOT NULL,
    national_id VARCHAR(50),
    nphies_id VARCHAR(100),
    organization VARCHAR(500),
    department VARCHAR(255),
    expires TIMESTAMP NOT NULL,
    full_oid VARCHAR(255) UNIQUE NOT NULL,
    metadata JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create NPHIES claims table
CREATE TABLE IF NOT EXISTS nphies_claims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id VARCHAR(100) UNIQUE NOT NULL,
    patient_nphies_id VARCHAR(100) NOT NULL,
    provider_nphies_id VARCHAR(100) NOT NULL,
    claim_type VARCHAR(100) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'SAR',
    diagnosis_codes JSONB DEFAULT '[]',
    procedure_codes JSONB DEFAULT '[]',
    status VARCHAR(50) DEFAULT 'submitted',
    submission_date TIMESTAMP NOT NULL,
    processing_date TIMESTAMP,
    payment_date TIMESTAMP,
    nphies_reference VARCHAR(255),
    error_codes JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create AI analyses table
CREATE TABLE IF NOT EXISTS ai_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id VARCHAR(100) UNIQUE NOT NULL,
    entity_id VARCHAR(255) NOT NULL,
    analysis_type VARCHAR(100) NOT NULL,
    results JSONB NOT NULL,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create healthcare organizations table
CREATE TABLE IF NOT EXISTS healthcare_organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    name_ar VARCHAR(500),
    type VARCHAR(100) NOT NULL, -- hospital, clinic, pharmacy, lab, etc.
    nphies_id VARCHAR(100),
    license_number VARCHAR(100),
    region VARCHAR(100),
    city VARCHAR(255),
    address TEXT,
    contact_info JSONB DEFAULT '{}',
    specialties JSONB DEFAULT '[]',
    certification_level VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create revenue cycle metrics table
CREATE TABLE IF NOT EXISTS rcm_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES healthcare_organizations(id),
    metric_date DATE NOT NULL,
    total_claims INTEGER DEFAULT 0,
    approved_claims INTEGER DEFAULT 0,
    denied_claims INTEGER DEFAULT 0,
    pending_claims INTEGER DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0,
    collected_amount DECIMAL(15,2) DEFAULT 0,
    avg_collection_days DECIMAL(5,2) DEFAULT 0,
    denial_rate DECIMAL(5,2) DEFAULT 0,
    first_pass_rate DECIMAL(5,2) DEFAULT 0,
    cost_savings DECIMAL(15,2) DEFAULT 0,
    duplicate_detections INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create audit log table for compliance
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id VARCHAR(255),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_healthcare_identities_entity_type ON healthcare_identities(entity_type);
CREATE INDEX IF NOT EXISTS idx_healthcare_identities_role ON healthcare_identities(role);
CREATE INDEX IF NOT EXISTS idx_healthcare_identities_organization ON healthcare_identities(organization);
CREATE INDEX IF NOT EXISTS idx_healthcare_identities_national_id ON healthcare_identities(national_id);
CREATE INDEX IF NOT EXISTS idx_healthcare_identities_nphies_id ON healthcare_identities(nphies_id);
CREATE INDEX IF NOT EXISTS idx_healthcare_identities_full_oid ON healthcare_identities(full_oid);
CREATE INDEX IF NOT EXISTS idx_healthcare_identities_status ON healthcare_identities(status);
CREATE INDEX IF NOT EXISTS idx_healthcare_identities_created_at ON healthcare_identities(created_at);

CREATE INDEX IF NOT EXISTS idx_nphies_claims_claim_id ON nphies_claims(claim_id);
CREATE INDEX IF NOT EXISTS idx_nphies_claims_patient_id ON nphies_claims(patient_nphies_id);
CREATE INDEX IF NOT EXISTS idx_nphies_claims_provider_id ON nphies_claims(provider_nphies_id);
CREATE INDEX IF NOT EXISTS idx_nphies_claims_status ON nphies_claims(status);
CREATE INDEX IF NOT EXISTS idx_nphies_claims_submission_date ON nphies_claims(submission_date);

CREATE INDEX IF NOT EXISTS idx_ai_analyses_entity_id ON ai_analyses(entity_id);
CREATE INDEX IF NOT EXISTS idx_ai_analyses_type ON ai_analyses(analysis_type);
CREATE INDEX IF NOT EXISTS idx_ai_analyses_created_at ON ai_analyses(created_at);

CREATE INDEX IF NOT EXISTS idx_organizations_nphies_id ON healthcare_organizations(nphies_id);
CREATE INDEX IF NOT EXISTS idx_organizations_type ON healthcare_organizations(type);
CREATE INDEX IF NOT EXISTS idx_organizations_region ON healthcare_organizations(region);
CREATE INDEX IF NOT EXISTS idx_organizations_status ON healthcare_organizations(status);

CREATE INDEX IF NOT EXISTS idx_rcm_metrics_org_date ON rcm_metrics(organization_id, metric_date);
CREATE INDEX IF NOT EXISTS idx_rcm_metrics_date ON rcm_metrics(metric_date);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);

-- Create full-text search indexes for Arabic content
CREATE INDEX IF NOT EXISTS idx_healthcare_identities_search 
ON healthcare_identities USING gin(to_tsvector('arabic', coalesce(name, '') || ' ' || coalesce(name_ar, '')));

CREATE INDEX IF NOT EXISTS idx_organizations_search 
ON healthcare_organizations USING gin(to_tsvector('arabic', coalesce(name, '') || ' ' || coalesce(name_ar, '')));

-- Insert sample data for development and testing
INSERT INTO healthcare_organizations (organization_id, name, name_ar, type, nphies_id, region, city, specialties) VALUES
('ORG001', 'King Faisal Specialist Hospital', 'مستشفى الملك فيصل التخصصي', 'hospital', 'NPHIES_KFSH_001', 'Riyadh', 'Riyadh', '["oncology", "cardiology", "neurology"]'),
('ORG002', 'Saudi German Hospital', 'المستشفى السعودي الألماني', 'hospital', 'NPHIES_SGH_001', 'Jeddah', 'Jeddah', '["general_medicine", "surgery", "pediatrics"]'),
('ORG003', 'Dr. Sulaiman Al Habib Medical Group', 'مجموعة د. سليمان الحبيب الطبية', 'hospital_group', 'NPHIES_SAH_001', 'Riyadh', 'Riyadh', '["multi_specialty", "emergency", "maternity"]')
ON CONFLICT (organization_id) DO NOTHING;

-- Sample healthcare identities
INSERT INTO healthcare_identities (entity_type, user_id, name, name_ar, role, access_level, organization, full_oid, nphies_id) VALUES
('provider', 'DR001', 'Dr. Ahmed Al-Rashid', 'د. أحمد الراشد', 'physician', 'high', 'King Faisal Specialist Hospital', '1.3.6.1.4.1.61026.2.1001', 'NPHIES_DR_001'),
('provider', 'NR001', 'Sara Al-Zahra', 'سارة الزهراء', 'nurse', 'medium', 'Saudi German Hospital', '1.3.6.1.4.1.61026.2.1002', 'NPHIES_NR_001'),
('patient', 'PT001', 'Mohammad Al-Faisal', 'محمد الفيصل', 'patient', 'low', NULL, '1.3.6.1.4.1.61026.1.1001', 'NPHIES_PT_001'),
('administrator', 'AD001', 'Fatima Al-Qasimi', 'فاطمة القاسمي', 'administrator', 'critical', 'Dr. Sulaiman Al Habib Medical Group', '1.3.6.1.4.1.61026.2.1003', 'NPHIES_AD_001')
ON CONFLICT (full_oid) DO NOTHING;

-- Sample NPHIES claims
INSERT INTO nphies_claims (claim_id, patient_nphies_id, provider_nphies_id, claim_type, amount, diagnosis_codes, procedure_codes) VALUES
('CLM001', 'NPHIES_PT_001', 'NPHIES_DR_001', 'outpatient', 1500.00, '["Z00.00", "K59.00"]', '["99213", "45378"]'),
('CLM002', 'NPHIES_PT_001', 'NPHIES_DR_001', 'emergency', 3200.00, '["S72.001A"]', '["99285", "27244"]')
ON CONFLICT (claim_id) DO NOTHING;

-- Sample RCM metrics
INSERT INTO rcm_metrics (organization_id, metric_date, total_claims, approved_claims, denied_claims, total_amount, collected_amount, avg_collection_days, denial_rate, first_pass_rate) VALUES
((SELECT id FROM healthcare_organizations WHERE organization_id = 'ORG001'), CURRENT_DATE - INTERVAL '1 day', 150, 142, 8, 450000.00, 425000.00, 18.5, 5.3, 94.7),
((SELECT id FROM healthcare_organizations WHERE organization_id = 'ORG002'), CURRENT_DATE - INTERVAL '1 day', 200, 185, 15, 680000.00, 615000.00, 22.1, 7.5, 92.5),
((SELECT id FROM healthcare_organizations WHERE organization_id = 'ORG003'), CURRENT_DATE - INTERVAL '1 day', 320, 305, 15, 1200000.00, 1150000.00, 15.8, 4.7, 95.3);

-- Legacy OID table for backward compatibility
CREATE TABLE IF NOT EXISTS oids (
    oid VARCHAR(100) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    name VARCHAR(500) NOT NULL,
    role VARCHAR(100) NOT NULL,
    access_level VARCHAR(50) NOT NULL,
    expires TIMESTAMP NOT NULL,
    full_oid VARCHAR(255) UNIQUE NOT NULL,
    parent_oid VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Migration data from legacy to new system
INSERT INTO oids (oid, user_id, name, role, access_level, expires, full_oid, parent_oid) VALUES
('1001', 'admin', 'System Administrator', 'administrator', 'critical', '2025-12-31 23:59:59', '1.3.6.1.4.1.61026.2.1001', '1.3.6.1.4.1.61026.2'),
('1002', 'dev001', 'Developer User', 'administrator', 'high', '2025-06-30 23:59:59', '1.3.6.1.4.1.61026.2.1002', '1.3.6.1.4.1.61026.2')
ON CONFLICT (oid) DO NOTHING;

-- Create triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER healthcare_identities_updated_at
    BEFORE UPDATE ON healthcare_identities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER nphies_claims_updated_at
    BEFORE UPDATE ON nphies_claims
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER healthcare_organizations_updated_at
    BEFORE UPDATE ON healthcare_organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Create audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (action, table_name, record_id, new_values)
        VALUES ('INSERT', TG_TABLE_NAME, NEW.id::text, row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (action, table_name, record_id, old_values, new_values)
        VALUES ('UPDATE', TG_TABLE_NAME, NEW.id::text, row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (action, table_name, record_id, old_values)
        VALUES ('DELETE', TG_TABLE_NAME, OLD.id::text, row_to_json(OLD));
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers to sensitive tables
CREATE TRIGGER healthcare_identities_audit
    AFTER INSERT OR UPDATE OR DELETE ON healthcare_identities
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER nphies_claims_audit
    AFTER INSERT OR UPDATE OR DELETE ON nphies_claims
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- ===== TRAINING PLATFORM SCHEMA =====
-- Medical Coding Training Programs
CREATE TABLE IF NOT EXISTS training_programs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    title_ar VARCHAR(500),
    description TEXT,
    description_ar TEXT,
    program_type VARCHAR(100) NOT NULL, -- foundation, advanced, specialization, corporate
    duration_hours INTEGER NOT NULL,
    certification_type VARCHAR(100), -- CPC, CCS, NPHIES, etc.
    language VARCHAR(20) DEFAULT 'bilingual', -- arabic, english, bilingual
    price_sar DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Training Modules within Programs
CREATE TABLE IF NOT EXISTS training_modules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_id UUID REFERENCES training_programs(id),
    module_code VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    title_ar VARCHAR(500),
    content_type VARCHAR(50), -- video, document, quiz, lab
    duration_minutes INTEGER,
    sequence_order INTEGER NOT NULL,
    content_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Student Enrollments
CREATE TABLE IF NOT EXISTS student_enrollments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES healthcare_identities(id),
    program_id UUID REFERENCES training_programs(id),
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    start_date DATE,
    expected_completion DATE,
    actual_completion DATE,
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'enrolled', -- enrolled, active, completed, withdrawn
    final_score DECIMAL(5,2),
    certificate_number VARCHAR(100),
    certificate_issued_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Training Progress Tracking
CREATE TABLE IF NOT EXISTS training_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    enrollment_id UUID REFERENCES student_enrollments(id),
    module_id UUID REFERENCES training_modules(id),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    time_spent_minutes INTEGER DEFAULT 0,
    quiz_score DECIMAL(5,2),
    attempts INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'not_started', -- not_started, in_progress, completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== BOT (BUILD-OPERATE-TRANSFER) LIFECYCLE SCHEMA =====
-- BOT Projects
CREATE TABLE IF NOT EXISTS bot_projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_code VARCHAR(100) UNIQUE NOT NULL,
    client_organization_id UUID REFERENCES healthcare_organizations(id),
    project_name VARCHAR(500) NOT NULL,
    project_type VARCHAR(100) NOT NULL, -- rcm_operations, training_setup, full_platform
    contract_value_sar DECIMAL(15,2) NOT NULL,
    build_start_date DATE NOT NULL,
    build_end_date DATE NOT NULL,
    operate_start_date DATE NOT NULL,
    operate_end_date DATE NOT NULL,
    transfer_start_date DATE NOT NULL,
    transfer_end_date DATE NOT NULL,
    current_phase VARCHAR(50) DEFAULT 'planning', -- planning, build, operate, transfer, completed
    status VARCHAR(50) DEFAULT 'active',
    sla_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BOT Phase Milestones
CREATE TABLE IF NOT EXISTS bot_milestones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES bot_projects(id),
    phase VARCHAR(50) NOT NULL, -- build, operate, transfer
    milestone_name VARCHAR(500) NOT NULL,
    description TEXT,
    target_date DATE NOT NULL,
    completion_date DATE,
    completion_percentage DECIMAL(5,2) DEFAULT 0,
    deliverables JSONB DEFAULT '[]',
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed, delayed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BOT Knowledge Transfer Records
CREATE TABLE IF NOT EXISTS knowledge_transfers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES bot_projects(id),
    transfer_type VARCHAR(100) NOT NULL, -- documentation, training, process, technology
    title VARCHAR(500) NOT NULL,
    description TEXT,
    recipient_count INTEGER DEFAULT 0,
    completion_status VARCHAR(50) DEFAULT 'pending',
    transfer_date DATE,
    documentation_url TEXT,
    feedback_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== OPERATIONS CENTER SCHEMA =====
-- Real-time Operations Metrics
CREATE TABLE IF NOT EXISTS operations_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_timestamp TIMESTAMP NOT NULL,
    metric_type VARCHAR(100) NOT NULL, -- claims_processing, system_health, staff_productivity
    location VARCHAR(100) NOT NULL, -- riyadh, jeddah, dammam, all
    metric_name VARCHAR(255) NOT NULL,
    metric_value DECIMAL(15,2) NOT NULL,
    unit VARCHAR(50), -- count, percentage, seconds, sar
    threshold_status VARCHAR(50), -- normal, warning, critical
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staff Shifts and Productivity
CREATE TABLE IF NOT EXISTS staff_shifts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    staff_id UUID REFERENCES healthcare_identities(id),
    shift_date DATE NOT NULL,
    shift_type VARCHAR(50) NOT NULL, -- morning, evening, night, weekend
    location VARCHAR(100) NOT NULL,
    check_in_time TIMESTAMP,
    check_out_time TIMESTAMP,
    claims_processed INTEGER DEFAULT 0,
    accuracy_rate DECIMAL(5,2),
    productivity_score DECIMAL(5,2),
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, active, completed, absent
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System Alerts and Incidents
CREATE TABLE IF NOT EXISTS system_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_type VARCHAR(100) NOT NULL, -- performance, security, compliance, business
    severity VARCHAR(50) NOT NULL, -- info, warning, error, critical
    title VARCHAR(500) NOT NULL,
    description TEXT,
    affected_systems JSONB DEFAULT '[]',
    impact_assessment TEXT,
    resolution_steps TEXT,
    alert_timestamp TIMESTAMP NOT NULL,
    acknowledged_by UUID REFERENCES healthcare_identities(id),
    acknowledged_at TIMESTAMP,
    resolved_by UUID REFERENCES healthcare_identities(id),
    resolved_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active', -- active, acknowledged, resolved, false_positive
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== ENHANCED NPHIES INTEGRATION TABLES =====
-- NPHIES Eligibility Checks
CREATE TABLE IF NOT EXISTS nphies_eligibility_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(100) UNIQUE NOT NULL,
    patient_nphies_id VARCHAR(100) NOT NULL,
    insurance_id VARCHAR(100) NOT NULL,
    provider_nphies_id VARCHAR(100) NOT NULL,
    check_type VARCHAR(50) NOT NULL, -- benefits, coverage, preauth
    request_timestamp TIMESTAMP NOT NULL,
    response_timestamp TIMESTAMP,
    is_eligible BOOLEAN,
    coverage_details JSONB DEFAULT '{}',
    limitations JSONB DEFAULT '[]',
    response_code VARCHAR(50),
    response_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NPHIES Pre-Authorization Requests
CREATE TABLE IF NOT EXISTS nphies_preauth_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    preauth_id VARCHAR(100) UNIQUE NOT NULL,
    claim_id UUID REFERENCES nphies_claims(id),
    requested_procedures JSONB NOT NULL,
    requested_amount DECIMAL(15,2) NOT NULL,
    medical_justification TEXT,
    supporting_documents JSONB DEFAULT '[]',
    request_timestamp TIMESTAMP NOT NULL,
    response_timestamp TIMESTAMP,
    approval_status VARCHAR(50), -- approved, partial, denied, pending
    approved_amount DECIMAL(15,2),
    approval_reference VARCHAR(100),
    denial_reasons JSONB DEFAULT '[]',
    valid_until DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for new tables
CREATE INDEX idx_training_programs_type ON training_programs(program_type);
CREATE INDEX idx_training_programs_status ON training_programs(status);
CREATE INDEX idx_student_enrollments_student ON student_enrollments(student_id);
CREATE INDEX idx_student_enrollments_program ON student_enrollments(program_id);
CREATE INDEX idx_student_enrollments_status ON student_enrollments(status);
CREATE INDEX idx_training_progress_enrollment ON training_progress(enrollment_id);
CREATE INDEX idx_bot_projects_client ON bot_projects(client_organization_id);
CREATE INDEX idx_bot_projects_phase ON bot_projects(current_phase);
CREATE INDEX idx_bot_milestones_project ON bot_milestones(project_id);
CREATE INDEX idx_bot_milestones_status ON bot_milestones(status);
CREATE INDEX idx_operations_metrics_timestamp ON operations_metrics(metric_timestamp);
CREATE INDEX idx_operations_metrics_type ON operations_metrics(metric_type);
CREATE INDEX idx_staff_shifts_date ON staff_shifts(shift_date);
CREATE INDEX idx_staff_shifts_staff ON staff_shifts(staff_id);
CREATE INDEX idx_system_alerts_severity ON system_alerts(severity);
CREATE INDEX idx_system_alerts_status ON system_alerts(status);
CREATE INDEX idx_nphies_eligibility_patient ON nphies_eligibility_checks(patient_nphies_id);
CREATE INDEX idx_nphies_preauth_claim ON nphies_preauth_requests(claim_id);

-- Apply update triggers to new tables
CREATE TRIGGER training_programs_updated_at
    BEFORE UPDATE ON training_programs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER student_enrollments_updated_at
    BEFORE UPDATE ON student_enrollments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER bot_projects_updated_at
    BEFORE UPDATE ON bot_projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Insert sample training programs
INSERT INTO training_programs (program_code, title, title_ar, program_type, duration_hours, certification_type, price_sar) VALUES
('MCC-101', 'Medical Coding Foundations', 'أساسيات الترميز الطبي', 'foundation', 300, 'CPC', 4999.00),
('NCC-201', 'NPHIES Compliance Certification', 'شهادة الامتثال لنظام نفيس', 'advanced', 160, 'NPHIES', 2999.00),
('RCM-301', 'Revenue Cycle Management Professional', 'محترف إدارة دورة الإيرادات', 'specialization', 240, 'RCMP', 7999.00),
('HIT-401', 'Healthcare IT Integration Specialist', 'أخصائي تكامل تقنية المعلومات الصحية', 'specialization', 200, 'HITS', 6999.00)
ON CONFLICT (program_code) DO NOTHING;

-- Grant appropriate permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO brainsait_admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO brainsait_admin;

-- Create views for analytics and reporting
CREATE OR REPLACE VIEW rcm_dashboard AS
SELECT 
    o.name as organization_name,
    o.name_ar as organization_name_ar,
    r.metric_date,
    r.total_claims,
    r.approved_claims,
    r.denied_claims,
    r.total_amount,
    r.collected_amount,
    r.avg_collection_days,
    r.denial_rate,
    r.first_pass_rate,
    r.cost_savings,
    ROUND((r.collected_amount / NULLIF(r.total_amount, 0)) * 100, 2) as collection_rate
FROM rcm_metrics r
JOIN healthcare_organizations o ON r.organization_id = o.id
ORDER BY r.metric_date DESC, o.name;

CREATE OR REPLACE VIEW healthcare_identity_summary AS
SELECT 
    entity_type,
    role,
    access_level,
    organization,
    COUNT(*) as total_count,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_count,
    COUNT(CASE WHEN expires < CURRENT_TIMESTAMP THEN 1 END) as expired_count
FROM healthcare_identities
GROUP BY entity_type, role, access_level, organization
ORDER BY entity_type, role;

-- Insert success message
INSERT INTO audit_logs (action, table_name, record_id, new_values) VALUES
('DATABASE_INIT', 'system', 'init', '{"message": "BrainSAIT Healthcare Unification Platform database initialized successfully", "version": "2.0.0", "timestamp": "' || CURRENT_TIMESTAMP || '"}');

COMMIT;
