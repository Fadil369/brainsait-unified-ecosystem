"""
Code Analyzer

Provides comprehensive static code analysis for Python applications,
detecting bugs, code smells, complexity issues, and maintainability concerns.
"""

import ast
import logging
import os
import re
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import inspect
from pathlib import Path

logger = logging.getLogger(__name__)

# Define a safe root directory for code analysis
SAFE_CODE_ROOT = "/srv/code_projects"

class CodeAnalyzer:
    """
    Performs static analysis on Python code to identify issues,
    complexity metrics, and improvement opportunities.
    """
    
    def __init__(self):
        self.issue_categories = [
            'syntax_errors',
            'logical_errors',
            'complexity_issues',
            'code_smells',
            'maintainability_issues',
            'style_violations',
            'documentation_issues'
        ]
        
        self.complexity_thresholds = {
            'function_lines': 50,
            'function_complexity': 10,
            'class_methods': 20,
            'file_lines': 500,
            'nested_depth': 4
        }
    
    async def analyze_codebase(self, project_path: str) -> Dict[str, Any]:
        """
        Analyze entire codebase for issues and improvements.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Comprehensive analysis results
        """
        try:
            # Normalize and validate the user-supplied project_path
            abs_project_path = os.path.abspath(os.path.normpath(project_path))
            abs_safe_root = os.path.abspath(os.path.normpath(SAFE_CODE_ROOT))
            if not abs_project_path.startswith(abs_safe_root):
                return {
                    'success': False,
                    'error': 'Invalid project path: access outside allowed directory is not permitted'
                }

            analysis_results = {
                'analysis_date': datetime.now().isoformat(),
                'project_path': abs_project_path,
                'summary': {},
                'files_analyzed': [],
                'issues': [],
                'metrics': {},
                'recommendations': []
            }
            
            # Find Python files to analyze
            python_files = await self._find_python_files(abs_project_path)
            
            if not python_files:
                return {
                    'success': False,
                    'error': 'No Python files found in the specified path'
                }
            
            # Analyze each file
            all_issues = []
            file_metrics = []
            
            for file_path in python_files:
                file_analysis = await self._analyze_file(file_path)
                if file_analysis['success']:
                    analysis_results['files_analyzed'].append({
                        'file': file_path,
                        'issues_count': len(file_analysis.get('issues', [])),
                        'complexity_score': file_analysis.get('metrics', {}).get('complexity_score', 0)
                    })
                    all_issues.extend(file_analysis.get('issues', []))
                    file_metrics.append(file_analysis.get('metrics', {}))
            
            analysis_results['issues'] = all_issues
            analysis_results['summary'] = await self._generate_summary(all_issues, file_metrics)
            analysis_results['metrics'] = await self._calculate_project_metrics(file_metrics)
            analysis_results['recommendations'] = await self._generate_recommendations(all_issues, file_metrics)
            
            return {
                'success': True,
                **analysis_results
            }
            
        except Exception as e:
            logger.error(f"Error analyzing codebase: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def analyze_code_snippet(self, code: str, filename: str = 'snippet.py') -> Dict[str, Any]:
        """
        Analyze a single code snippet.
        
        Args:
            code: Python code string to analyze
            filename: Optional filename for context
            
        Returns:
            Analysis results for the code snippet
        """
        try:
            # Parse the code
            try:
                tree = ast.parse(code, filename=filename)
            except SyntaxError as e:
                return {
                    'success': True,
                    'issues': [{
                        'type': 'syntax_error',
                        'severity': 'error',
                        'line': e.lineno,
                        'message': f'Syntax error: {e.msg}',
                        'file': filename
                    }],
                    'metrics': {},
                    'recommendations': ['Fix syntax error before proceeding with analysis']
                }
            
            # Perform analysis
            issues = await self._analyze_ast(tree, code, filename)
            metrics = await self._calculate_code_metrics(tree, code)
            recommendations = await self._generate_code_recommendations(issues, metrics)
            
            return {
                'success': True,
                'issues': issues,
                'metrics': metrics,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error analyzing code snippet: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _find_python_files(self, project_path: str) -> List[str]:
        """Find all Python files in the project directory."""
        python_files = []
        
        try:
            for root, dirs, files in os.walk(project_path):
                # Skip common directories that shouldn't be analyzed
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv']]
                
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
            
            return python_files
            
        except Exception as e:
            logger.error(f"Error finding Python files: {str(e)}")
            return []
    
    async def _analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Parse the file
            try:
                tree = ast.parse(code, filename=file_path)
            except SyntaxError as e:
                return {
                    'success': True,
                    'issues': [{
                        'type': 'syntax_error',
                        'severity': 'error',
                        'line': e.lineno,
                        'message': f'Syntax error: {e.msg}',
                        'file': file_path
                    }],
                    'metrics': {}
                }
            
            # Perform analysis
            issues = await self._analyze_ast(tree, code, file_path)
            metrics = await self._calculate_code_metrics(tree, code)
            
            return {
                'success': True,
                'issues': issues,
                'metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _analyze_ast(self, tree: ast.AST, code: str, filename: str) -> List[Dict[str, Any]]:
        """Analyze the AST for various issues."""
        issues = []
        lines = code.splitlines()
        
        class IssueVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_function = None
                self.current_class = None
                self.function_complexity = 0
                self.nesting_depth = 0
                
            def visit_FunctionDef(self, node):
                old_function = self.current_function
                old_complexity = self.function_complexity
                
                self.current_function = node.name
                self.function_complexity = 1
                
                # Check function length
                func_lines = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0
                if func_lines > self.analyzer.complexity_thresholds['function_lines']:
                    issues.append({
                        'type': 'complexity_issue',
                        'severity': 'warning',
                        'line': node.lineno,
                        'message': f'Function "{node.name}" is too long ({func_lines} lines)',
                        'file': filename,
                        'suggestion': 'Consider breaking this function into smaller functions'
                    })
                
                # Check for missing docstring
                if not ast.get_docstring(node):
                    issues.append({
                        'type': 'documentation_issue',
                        'severity': 'info',
                        'line': node.lineno,
                        'message': f'Function "{node.name}" missing docstring',
                        'file': filename,
                        'suggestion': 'Add a docstring to document the function purpose and parameters'
                    })
                
                # Check parameter count
                if len(node.args.args) > 7:
                    issues.append({
                        'type': 'complexity_issue',
                        'severity': 'warning',
                        'line': node.lineno,
                        'message': f'Function "{node.name}" has too many parameters ({len(node.args.args)})',
                        'file': filename,
                        'suggestion': 'Consider using a parameter object or reducing parameters'
                    })
                
                self.generic_visit(node)
                
                # Check cyclomatic complexity
                if self.function_complexity > self.analyzer.complexity_thresholds['function_complexity']:
                    issues.append({
                        'type': 'complexity_issue',
                        'severity': 'warning',
                        'line': node.lineno,
                        'message': f'Function "{node.name}" has high complexity ({self.function_complexity})',
                        'file': filename,
                        'suggestion': 'Consider simplifying the function logic'
                    })
                
                self.current_function = old_function
                self.function_complexity = old_complexity
            
            def visit_ClassDef(self, node):
                old_class = self.current_class
                self.current_class = node.name
                
                # Check for missing docstring
                if not ast.get_docstring(node):
                    issues.append({
                        'type': 'documentation_issue',
                        'severity': 'info',
                        'line': node.lineno,
                        'message': f'Class "{node.name}" missing docstring',
                        'file': filename,
                        'suggestion': 'Add a docstring to document the class purpose'
                    })
                
                # Count methods
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > self.analyzer.complexity_thresholds['class_methods']:
                    issues.append({
                        'type': 'complexity_issue',
                        'severity': 'warning',
                        'line': node.lineno,
                        'message': f'Class "{node.name}" has too many methods ({len(methods)})',
                        'file': filename,
                        'suggestion': 'Consider breaking the class into smaller classes'
                    })
                
                self.generic_visit(node)
                self.current_class = old_class
            
            def visit_If(self, node):
                self.function_complexity += 1
                old_depth = self.nesting_depth
                self.nesting_depth += 1
                
                if self.nesting_depth > self.analyzer.complexity_thresholds['nested_depth']:
                    issues.append({
                        'type': 'complexity_issue',
                        'severity': 'warning',
                        'line': node.lineno,
                        'message': f'Deep nesting detected (depth: {self.nesting_depth})',
                        'file': filename,
                        'suggestion': 'Consider extracting nested logic into separate functions'
                    })
                
                self.generic_visit(node)
                self.nesting_depth = old_depth
            
            def visit_For(self, node):
                self.function_complexity += 1
                self.generic_visit(node)
            
            def visit_While(self, node):
                self.function_complexity += 1
                self.generic_visit(node)
            
            def visit_Try(self, node):
                self.function_complexity += 1
                
                # Check for bare except
                for handler in node.handlers:
                    if handler.type is None:
                        issues.append({
                            'type': 'code_smell',
                            'severity': 'warning',
                            'line': handler.lineno,
                            'message': 'Bare except clause detected',
                            'file': filename,
                            'suggestion': 'Specify the exception type to catch'
                        })
                
                self.generic_visit(node)
            
            def visit_Import(self, node):
                # Check for unused imports (simplified check)
                for alias in node.names:
                    name = alias.asname or alias.name
                    if name not in code:
                        issues.append({
                            'type': 'code_smell',
                            'severity': 'info',
                            'line': node.lineno,
                            'message': f'Potentially unused import: {alias.name}',
                            'file': filename,
                            'suggestion': 'Remove unused imports to improve code cleanliness'
                        })
                
                self.generic_visit(node)
        
        # Create visitor with analyzer reference
        visitor = IssueVisitor()
        visitor.analyzer = self
        visitor.visit(tree)
        
        # Check file length
        if len(lines) > self.complexity_thresholds['file_lines']:
            issues.append({
                'type': 'complexity_issue',
                'severity': 'warning',
                'line': 1,
                'message': f'File is too long ({len(lines)} lines)',
                'file': filename,
                'suggestion': 'Consider splitting the file into smaller modules'
            })
        
        return issues
    
    async def _calculate_code_metrics(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Calculate various code metrics."""
        lines = code.splitlines()
        
        metrics = {
            'lines_of_code': len(lines),
            'blank_lines': len([line for line in lines if not line.strip()]),
            'comment_lines': len([line for line in lines if line.strip().startswith('#')]),
            'functions': 0,
            'classes': 0,
            'complexity_score': 0,
            'maintainability_index': 0
        }
        
        class MetricVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                metrics['functions'] += 1
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                metrics['classes'] += 1
                self.generic_visit(node)
            
            def visit_If(self, node):
                metrics['complexity_score'] += 1
                self.generic_visit(node)
            
            def visit_For(self, node):
                metrics['complexity_score'] += 1
                self.generic_visit(node)
            
            def visit_While(self, node):
                metrics['complexity_score'] += 1
                self.generic_visit(node)
        
        visitor = MetricVisitor()
        visitor.visit(tree)
        
        # Calculate maintainability index (simplified)
        effective_lines = metrics['lines_of_code'] - metrics['blank_lines'] - metrics['comment_lines']
        if effective_lines > 0:
            metrics['maintainability_index'] = max(0, min(100, 
                100 - (metrics['complexity_score'] * 2) - (effective_lines / 10)
            ))
        
        return metrics
    
    async def _generate_summary(self, all_issues: List[Dict[str, Any]], file_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of analysis results."""
        summary = {
            'total_issues': len(all_issues),
            'by_severity': {},
            'by_type': {},
            'critical_issues': 0,
            'average_maintainability': 0
        }
        
        # Count by severity
        for issue in all_issues:
            severity = issue.get('severity', 'info')
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
            if severity == 'error':
                summary['critical_issues'] += 1
        
        # Count by type
        for issue in all_issues:
            issue_type = issue.get('type', 'unknown')
            summary['by_type'][issue_type] = summary['by_type'].get(issue_type, 0) + 1
        
        # Calculate average maintainability
        if file_metrics:
            maintainability_scores = [m.get('maintainability_index', 0) for m in file_metrics]
            summary['average_maintainability'] = round(sum(maintainability_scores) / len(maintainability_scores), 2)
        
        return summary
    
    async def _calculate_project_metrics(self, file_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate project-level metrics."""
        if not file_metrics:
            return {}
        
        total_loc = sum(m.get('lines_of_code', 0) for m in file_metrics)
        total_functions = sum(m.get('functions', 0) for m in file_metrics)
        total_classes = sum(m.get('classes', 0) for m in file_metrics)
        
        return {
            'total_lines_of_code': total_loc,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'average_file_size': round(total_loc / len(file_metrics), 2) if file_metrics else 0,
            'functions_per_file': round(total_functions / len(file_metrics), 2) if file_metrics else 0,
            'classes_per_file': round(total_classes / len(file_metrics), 2) if file_metrics else 0
        }
    
    async def _generate_recommendations(self, all_issues: List[Dict[str, Any]], file_metrics: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        # Count issue types
        issue_counts = {}
        for issue in all_issues:
            issue_type = issue.get('type', 'unknown')
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        # Generate recommendations based on common issues
        if issue_counts.get('complexity_issue', 0) > 5:
            recommendations.append('Focus on reducing code complexity by breaking down large functions and classes')
        
        if issue_counts.get('documentation_issue', 0) > 10:
            recommendations.append('Improve code documentation by adding docstrings to functions and classes')
        
        if issue_counts.get('code_smell', 0) > 3:
            recommendations.append('Address code smells to improve code quality and maintainability')
        
        if issue_counts.get('syntax_error', 0) > 0:
            recommendations.append('Fix syntax errors before proceeding with other improvements')
        
        # Recommendations based on metrics
        if file_metrics:
            avg_maintainability = sum(m.get('maintainability_index', 0) for m in file_metrics) / len(file_metrics)
            if avg_maintainability < 50:
                recommendations.append('Overall maintainability is low - consider refactoring critical components')
        
        if not recommendations:
            recommendations.append('Code quality looks good! Consider setting up automated code quality checks')
        
        return recommendations
    
    async def _generate_code_recommendations(self, issues: List[Dict[str, Any]], metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations for a single code snippet."""
        recommendations = []
        
        error_count = len([i for i in issues if i.get('severity') == 'error'])
        warning_count = len([i for i in issues if i.get('severity') == 'warning'])
        
        if error_count > 0:
            recommendations.append(f'Fix {error_count} error(s) first')
        
        if warning_count > 0:
            recommendations.append(f'Address {warning_count} warning(s) to improve code quality')
        
        maintainability = metrics.get('maintainability_index', 0)
        if maintainability < 50:
            recommendations.append('Consider refactoring to improve maintainability')
        elif maintainability > 80:
            recommendations.append('Code maintainability is excellent!')
        
        if not recommendations and not issues:
            recommendations.append('Code looks good! No issues detected.')
        
        return recommendations