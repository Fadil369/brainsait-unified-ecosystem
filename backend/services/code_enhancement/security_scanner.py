"""
Security Scanner

Performs security vulnerability scanning and assessment for Python code,
identifying potential security risks and providing remediation guidance.
"""

import ast
import re
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import hashlib
import secrets

logger = logging.getLogger(__name__)

class SecurityScanner:
    """
    Scans Python code for security vulnerabilities and provides
    recommendations for improving code security.
    """
    
    def __init__(self):
        self.vulnerability_patterns = {
            'sql_injection': [
                r'execute\s*\(\s*["\'].*%.*["\']',
                r'cursor\.execute\s*\(\s*f["\']',
                r'\.format\s*\(\s*.*\)\s*\)',
            ],
            'command_injection': [
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(',
                r'eval\s*\(',
                r'exec\s*\(',
            ],
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
            ],
            'path_traversal': [
                r'open\s*\(\s*.*\+.*\)',
                r'file\s*=.*\+',
                r'\.\./',
            ],
            'insecure_random': [
                r'random\.randint\s*\(',
                r'random\.choice\s*\(',
                r'random\.random\s*\(',
            ],
            'xxe_vulnerability': [
                r'xml\.etree\.ElementTree\.parse',
                r'lxml\.etree\.parse',
                r'xml\.dom\.minidom\.parse',
            ]
        }
        
        self.security_best_practices = [
            'input_validation',
            'output_encoding',
            'authentication',
            'authorization',
            'error_handling',
            'logging',
            'crypto_usage'
        ]
    
    async def scan_security_vulnerabilities(self, code: str, filename: str = 'code.py') -> Dict[str, Any]:
        """
        Perform comprehensive security vulnerability scan.
        
        Args:
            code: Python code string to scan
            filename: Optional filename for context
            
        Returns:
            Security scan results with vulnerabilities and recommendations
        """
        try:
            scan_results = {
                'scan_date': datetime.now().isoformat(),
                'filename': filename,
                'vulnerabilities': [],
                'security_score': 100,
                'risk_level': 'low',
                'recommendations': [],
                'compliance_issues': []
            }
            
            # Parse the code
            try:
                tree = ast.parse(code, filename=filename)
            except SyntaxError as e:
                return {
                    'success': False,
                    'error': f'Syntax error in code: {e.msg}'
                }
            
            # Pattern-based vulnerability detection
            pattern_vulnerabilities = await self._scan_vulnerability_patterns(code, filename)
            
            # AST-based security analysis
            ast_vulnerabilities = await self._analyze_ast_security(tree, code, filename)
            
            # Combine vulnerabilities
            all_vulnerabilities = pattern_vulnerabilities + ast_vulnerabilities
            scan_results['vulnerabilities'] = all_vulnerabilities
            
            # Calculate security score
            security_score = await self._calculate_security_score(all_vulnerabilities)
            scan_results['security_score'] = security_score
            
            # Determine risk level
            scan_results['risk_level'] = await self._determine_risk_level(all_vulnerabilities, security_score)
            
            # Generate recommendations
            recommendations = await self._generate_security_recommendations(all_vulnerabilities)
            scan_results['recommendations'] = recommendations
            
            # Check compliance issues
            compliance_issues = await self._check_compliance_issues(tree, code)
            scan_results['compliance_issues'] = compliance_issues
            
            return {
                'success': True,
                **scan_results
            }
            
        except Exception as e:
            logger.error(f"Error scanning security vulnerabilities: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def check_dependency_vulnerabilities(self, requirements_content: str) -> Dict[str, Any]:
        """
        Check for known vulnerabilities in project dependencies.
        
        Args:
            requirements_content: Content of requirements.txt file
            
        Returns:
            Dependency vulnerability analysis
        """
        try:
            dependency_analysis = {
                'scan_date': datetime.now().isoformat(),
                'total_dependencies': 0,
                'vulnerable_dependencies': [],
                'outdated_dependencies': [],
                'recommendations': []
            }
            
            # Parse requirements
            dependencies = await self._parse_requirements(requirements_content)
            dependency_analysis['total_dependencies'] = len(dependencies)
            
            # Check for known vulnerable packages (simplified)
            vulnerable_packages = await self._check_vulnerable_packages(dependencies)
            dependency_analysis['vulnerable_dependencies'] = vulnerable_packages
            
            # Check for outdated packages (simplified)
            outdated_packages = await self._check_outdated_packages(dependencies)
            dependency_analysis['outdated_dependencies'] = outdated_packages
            
            # Generate recommendations
            recommendations = await self._generate_dependency_recommendations(
                vulnerable_packages, outdated_packages
            )
            dependency_analysis['recommendations'] = recommendations
            
            return {
                'success': True,
                **dependency_analysis
            }
            
        except Exception as e:
            logger.error(f"Error checking dependency vulnerabilities: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _scan_vulnerability_patterns(self, code: str, filename: str) -> List[Dict[str, Any]]:
        """Scan code for vulnerability patterns using regex."""
        vulnerabilities = []
        lines = code.splitlines()
        
        for vuln_type, patterns in self.vulnerability_patterns.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        severity = await self._get_vulnerability_severity(vuln_type)
                        vulnerabilities.append({
                            'type': vuln_type,
                            'severity': severity,
                            'line': line_num,
                            'code_snippet': line.strip(),
                            'message': await self._get_vulnerability_message(vuln_type),
                            'file': filename,
                            'cwe_id': await self._get_cwe_id(vuln_type),
                            'remediation': await self._get_remediation_advice(vuln_type)
                        })
        
        return vulnerabilities
    
    async def _analyze_ast_security(self, tree: ast.AST, code: str, filename: str) -> List[Dict[str, Any]]:
        """Analyze AST for security vulnerabilities."""
        vulnerabilities = []
        
        class SecurityVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                # Check for dangerous function calls
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    
                    # Check for eval/exec usage
                    if func_name in ['eval', 'exec']:
                        vulnerabilities.append({
                            'type': 'code_injection',
                            'severity': 'high',
                            'line': node.lineno,
                            'message': f'Dangerous function "{func_name}" detected',
                            'file': filename,
                            'cwe_id': 'CWE-94',
                            'remediation': 'Avoid using eval() and exec(). Use safer alternatives like ast.literal_eval() for simple expressions.'
                        })
                    
                    # Check for os.system usage
                    elif func_name == 'system':
                        vulnerabilities.append({
                            'type': 'command_injection',
                            'severity': 'high',
                            'line': node.lineno,
                            'message': 'os.system() usage detected',
                            'file': filename,
                            'cwe_id': 'CWE-78',
                            'remediation': 'Use subprocess.run() with shell=False instead of os.system()'
                        })
                
                # Check for subprocess calls
                elif (isinstance(node.func, ast.Attribute) and
                      isinstance(node.func.value, ast.Name) and
                      node.func.value.id == 'subprocess'):
                    
                    # Check for shell=True usage
                    for keyword in node.keywords:
                        if (keyword.arg == 'shell' and
                            isinstance(keyword.value, ast.Constant) and
                            keyword.value.value is True):
                            vulnerabilities.append({
                                'type': 'command_injection',
                                'severity': 'medium',
                                'line': node.lineno,
                                'message': 'subprocess call with shell=True detected',
                                'file': filename,
                                'cwe_id': 'CWE-78',
                                'remediation': 'Avoid shell=True when possible. Validate and sanitize user input.'
                            })
                
                self.generic_visit(node)
            
            def visit_Str(self, node):
                # Check for hardcoded secrets (simple patterns)
                secret_indicators = ['password', 'secret', 'key', 'token', 'api']
                if any(indicator in node.s.lower() for indicator in secret_indicators):
                    if len(node.s) > 8 and not node.s.isalpha():  # Likely a real secret
                        vulnerabilities.append({
                            'type': 'hardcoded_secret',
                            'severity': 'medium',
                            'line': node.lineno,
                            'message': 'Potential hardcoded secret detected',
                            'file': filename,
                            'cwe_id': 'CWE-798',
                            'remediation': 'Move secrets to environment variables or secure configuration files'
                        })
                
                self.generic_visit(node)
            
            def visit_Import(self, node):
                # Check for insecure imports
                for alias in node.names:
                    if alias.name in ['pickle', 'cPickle']:
                        vulnerabilities.append({
                            'type': 'insecure_deserialization',
                            'severity': 'medium',
                            'line': node.lineno,
                            'message': f'Insecure module "{alias.name}" imported',
                            'file': filename,
                            'cwe_id': 'CWE-502',
                            'remediation': 'Be cautious with pickle. Only unpickle data from trusted sources.'
                        })
                
                self.generic_visit(node)
            
            def visit_Assign(self, node):
                # Check for weak random number generation
                if (isinstance(node.value, ast.Call) and
                    isinstance(node.value.func, ast.Attribute) and
                    isinstance(node.value.func.value, ast.Name) and
                    node.value.func.value.id == 'random'):
                    
                    vulnerabilities.append({
                        'type': 'weak_random',
                        'severity': 'low',
                        'line': node.lineno,
                        'message': 'Weak random number generation detected',
                        'file': filename,
                        'cwe_id': 'CWE-338',
                        'remediation': 'Use secrets module for cryptographically secure random numbers'
                    })
                
                self.generic_visit(node)
        
        visitor = SecurityVisitor()
        visitor.visit(tree)
        
        return vulnerabilities
    
    async def _get_vulnerability_severity(self, vuln_type: str) -> str:
        """Get severity level for vulnerability type."""
        severity_map = {
            'sql_injection': 'high',
            'command_injection': 'high',
            'code_injection': 'high',
            'hardcoded_secrets': 'medium',
            'hardcoded_secret': 'medium',
            'path_traversal': 'medium',
            'insecure_random': 'low',
            'weak_random': 'low',
            'xxe_vulnerability': 'medium',
            'insecure_deserialization': 'medium'
        }
        return severity_map.get(vuln_type, 'medium')
    
    async def _get_vulnerability_message(self, vuln_type: str) -> str:
        """Get descriptive message for vulnerability type."""
        messages = {
            'sql_injection': 'Potential SQL injection vulnerability detected',
            'command_injection': 'Command injection vulnerability detected',
            'hardcoded_secrets': 'Hardcoded secret or credential detected',
            'path_traversal': 'Path traversal vulnerability detected',
            'insecure_random': 'Insecure random number generation',
            'xxe_vulnerability': 'XML External Entity (XXE) vulnerability'
        }
        return messages.get(vuln_type, f'{vuln_type.replace("_", " ").title()} vulnerability detected')
    
    async def _get_cwe_id(self, vuln_type: str) -> str:
        """Get CWE (Common Weakness Enumeration) ID for vulnerability type."""
        cwe_map = {
            'sql_injection': 'CWE-89',
            'command_injection': 'CWE-78',
            'code_injection': 'CWE-94',
            'hardcoded_secrets': 'CWE-798',
            'hardcoded_secret': 'CWE-798',
            'path_traversal': 'CWE-22',
            'insecure_random': 'CWE-338',
            'weak_random': 'CWE-338',
            'xxe_vulnerability': 'CWE-611',
            'insecure_deserialization': 'CWE-502'
        }
        return cwe_map.get(vuln_type, 'CWE-Unknown')
    
    async def _get_remediation_advice(self, vuln_type: str) -> str:
        """Get remediation advice for vulnerability type."""
        advice = {
            'sql_injection': 'Use parameterized queries or prepared statements instead of string concatenation',
            'command_injection': 'Validate and sanitize all user input. Use subprocess with shell=False',
            'hardcoded_secrets': 'Store secrets in environment variables or secure configuration files',
            'path_traversal': 'Validate file paths and use os.path.abspath() to prevent directory traversal',
            'insecure_random': 'Use secrets module for cryptographically secure random numbers',
            'xxe_vulnerability': 'Disable XML external entity processing in XML parsers'
        }
        return advice.get(vuln_type, 'Review code for security best practices')
    
    async def _calculate_security_score(self, vulnerabilities: List[Dict[str, Any]]) -> int:
        """Calculate overall security score based on vulnerabilities."""
        base_score = 100
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'low')
            if severity == 'high':
                base_score -= 20
            elif severity == 'medium':
                base_score -= 10
            else:  # low
                base_score -= 5
        
        return max(0, base_score)
    
    async def _determine_risk_level(self, vulnerabilities: List[Dict[str, Any]], security_score: int) -> str:
        """Determine overall risk level."""
        high_severity_count = len([v for v in vulnerabilities if v.get('severity') == 'high'])
        
        if high_severity_count > 0 or security_score < 60:
            return 'high'
        elif security_score < 80:
            return 'medium'
        else:
            return 'low'
    
    async def _generate_security_recommendations(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate security recommendations based on vulnerabilities."""
        recommendations = []
        
        # Group vulnerabilities by type
        vuln_counts = {}
        for vuln in vulnerabilities:
            vuln_type = vuln.get('type', 'unknown')
            vuln_counts[vuln_type] = vuln_counts.get(vuln_type, 0) + 1
        
        # Generate specific recommendations
        if vuln_counts.get('sql_injection', 0) > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'injection_prevention',
                'title': 'Implement SQL Injection Protection',
                'description': f'Found {vuln_counts["sql_injection"]} potential SQL injection vulnerabilities',
                'actions': [
                    'Replace string concatenation with parameterized queries',
                    'Use ORM frameworks with built-in protection',
                    'Implement input validation and sanitization',
                    'Apply principle of least privilege for database access'
                ]
            })
        
        if vuln_counts.get('command_injection', 0) > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'injection_prevention',
                'title': 'Prevent Command Injection',
                'description': f'Found {vuln_counts["command_injection"]} command injection vulnerabilities',
                'actions': [
                    'Use subprocess.run() with shell=False',
                    'Validate and whitelist allowed commands',
                    'Escape or sanitize user input',
                    'Run processes with minimal privileges'
                ]
            })
        
        if vuln_counts.get('hardcoded_secret', 0) > 0 or vuln_counts.get('hardcoded_secrets', 0) > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'secret_management',
                'title': 'Implement Secure Secret Management',
                'description': 'Hardcoded secrets detected in code',
                'actions': [
                    'Move secrets to environment variables',
                    'Use secure configuration management',
                    'Implement secret rotation policies',
                    'Add secrets to .gitignore'
                ]
            })
        
        if vuln_counts.get('weak_random', 0) > 0 or vuln_counts.get('insecure_random', 0) > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'cryptography',
                'title': 'Use Cryptographically Secure Random Numbers',
                'description': 'Weak random number generation detected',
                'actions': [
                    'Replace random module with secrets module',
                    'Use os.urandom() for cryptographic purposes',
                    'Review all random number usage'
                ]
            })
        
        # General recommendations
        recommendations.append({
            'priority': 'medium',
            'category': 'general_security',
            'title': 'Implement Security Best Practices',
            'description': 'General security improvements',
            'actions': [
                'Implement comprehensive input validation',
                'Add security headers to HTTP responses',
                'Enable security logging and monitoring',
                'Regular security code reviews',
                'Keep dependencies updated'
            ]
        })
        
        return recommendations
    
    async def _check_compliance_issues(self, tree: ast.AST, code: str) -> List[Dict[str, Any]]:
        """Check for compliance-related issues (HIPAA, GDPR, etc.)."""
        compliance_issues = []
        
        # Check for potential PII handling without proper protection
        pii_patterns = ['ssn', 'social_security', 'credit_card', 'email', 'phone', 'address']
        
        for pattern in pii_patterns:
            if pattern in code.lower():
                compliance_issues.append({
                    'type': 'pii_handling',
                    'regulation': 'GDPR/HIPAA',
                    'description': f'Potential PII data handling detected: {pattern}',
                    'requirement': 'Ensure proper encryption and access controls for PII data'
                })
        
        # Check for logging sensitive information
        class ComplianceVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if (isinstance(node.func, ast.Attribute) and
                    node.func.attr in ['info', 'debug', 'warning', 'error'] and
                    isinstance(node.func.value, ast.Name) and
                    'log' in node.func.value.id.lower()):
                    
                    compliance_issues.append({
                        'type': 'logging_compliance',
                        'regulation': 'HIPAA/GDPR',
                        'line': node.lineno,
                        'description': 'Logging detected - ensure no sensitive data is logged',
                        'requirement': 'Implement secure logging practices'
                    })
                
                self.generic_visit(node)
        
        visitor = ComplianceVisitor()
        visitor.visit(tree)
        
        return compliance_issues[:5]  # Limit to first 5 issues
    
    async def _parse_requirements(self, requirements_content: str) -> List[Dict[str, str]]:
        """Parse requirements.txt content."""
        dependencies = []
        
        for line in requirements_content.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                # Simple parsing (doesn't handle all pip syntax)
                if '==' in line:
                    name, version = line.split('==', 1)
                    dependencies.append({'name': name.strip(), 'version': version.strip()})
                elif '>=' in line:
                    name, version = line.split('>=', 1)
                    dependencies.append({'name': name.strip(), 'version': version.strip(), 'operator': '>='})
                else:
                    dependencies.append({'name': line, 'version': 'unknown'})
        
        return dependencies
    
    async def _check_vulnerable_packages(self, dependencies: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Check for known vulnerable packages (simplified)."""
        # This is a simplified implementation
        # In production, you'd use a real vulnerability database
        known_vulnerable = {
            'django': ['1.11.0', '2.0.0', '2.1.0'],
            'flask': ['0.12.0', '1.0.0'],
            'requests': ['2.19.0', '2.20.0'],
            'urllib3': ['1.24.0', '1.25.0']
        }
        
        vulnerable = []
        for dep in dependencies:
            name = dep['name'].lower()
            version = dep.get('version', 'unknown')
            
            if name in known_vulnerable and version in known_vulnerable[name]:
                vulnerable.append({
                    'package': name,
                    'version': version,
                    'vulnerability': f'Known vulnerability in {name} {version}',
                    'severity': 'high',
                    'recommendation': f'Update {name} to latest version'
                })
        
        return vulnerable
    
    async def _check_outdated_packages(self, dependencies: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Check for outdated packages (simplified)."""
        # This is a simplified implementation
        # In production, you'd check against PyPI or other package repositories
        outdated = []
        
        # Simulate some outdated packages
        for dep in dependencies[:3]:  # Just check first 3 for demo
            if dep.get('version', 'unknown') != 'unknown':
                outdated.append({
                    'package': dep['name'],
                    'current_version': dep['version'],
                    'latest_version': f"{dep['version']}.1",  # Simulated
                    'recommendation': f'Update {dep["name"]} to latest version'
                })
        
        return outdated
    
    async def _generate_dependency_recommendations(
        self, 
        vulnerable_packages: List[Dict[str, Any]], 
        outdated_packages: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations for dependency management."""
        recommendations = []
        
        if vulnerable_packages:
            recommendations.append(f'Immediately update {len(vulnerable_packages)} vulnerable packages')
        
        if outdated_packages:
            recommendations.append(f'Consider updating {len(outdated_packages)} outdated packages')
        
        recommendations.extend([
            'Implement automated dependency scanning in CI/CD pipeline',
            'Set up security alerts for new vulnerabilities',
            'Regular dependency updates and security reviews',
            'Use dependency pinning for reproducible builds'
        ])
        
        return recommendations