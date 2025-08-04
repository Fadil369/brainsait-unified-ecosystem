"""
Quality Metrics

Calculates comprehensive code quality metrics and provides scoring
for maintainability, complexity, and overall code health.
"""

import ast
import re
import logging
import math
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class QualityMetrics:
    """
    Calculates comprehensive code quality metrics including maintainability,
    complexity, documentation coverage, and overall code health scores.
    """
    
    def __init__(self):
        self.metrics_categories = [
            'complexity_metrics',
            'maintainability_metrics',
            'documentation_metrics',
            'style_metrics',
            'structure_metrics'
        ]
        
        self.quality_thresholds = {
            'cyclomatic_complexity': {'good': 5, 'acceptable': 10, 'poor': 20},
            'maintainability_index': {'good': 80, 'acceptable': 60, 'poor': 40},
            'documentation_coverage': {'good': 80, 'acceptable': 60, 'poor': 40},
            'duplication_ratio': {'good': 5, 'acceptable': 10, 'poor': 20},
            'test_coverage': {'good': 80, 'acceptable': 60, 'poor': 40}
        }
    
    async def calculate_quality_metrics(self, code: str, filename: str = 'code.py') -> Dict[str, Any]:
        """
        Calculate comprehensive quality metrics for the given code.
        
        Args:
            code: Python code string to analyze
            filename: Optional filename for context
            
        Returns:
            Comprehensive quality metrics and scores
        """
        try:
            metrics_results = {
                'analysis_date': datetime.now().isoformat(),
                'filename': filename,
                'complexity_metrics': {},
                'maintainability_metrics': {},
                'documentation_metrics': {},
                'style_metrics': {},
                'structure_metrics': {},
                'overall_quality_score': 0,
                'quality_grade': 'F',
                'recommendations': []
            }
            
            # Parse the code
            try:
                tree = ast.parse(code, filename=filename)
            except SyntaxError as e:
                return {
                    'success': False,
                    'error': f'Syntax error in code: {e.msg}'
                }
            
            # Calculate different categories of metrics
            complexity_metrics = await self._calculate_complexity_metrics(tree, code)
            metrics_results['complexity_metrics'] = complexity_metrics
            
            maintainability_metrics = await self._calculate_maintainability_metrics(tree, code)
            metrics_results['maintainability_metrics'] = maintainability_metrics
            
            documentation_metrics = await self._calculate_documentation_metrics(tree, code)
            metrics_results['documentation_metrics'] = documentation_metrics
            
            style_metrics = await self._calculate_style_metrics(tree, code)
            metrics_results['style_metrics'] = style_metrics
            
            structure_metrics = await self._calculate_structure_metrics(tree, code)
            metrics_results['structure_metrics'] = structure_metrics
            
            # Calculate overall quality score
            overall_score = await self._calculate_overall_quality_score(
                complexity_metrics, maintainability_metrics, documentation_metrics,
                style_metrics, structure_metrics
            )
            metrics_results['overall_quality_score'] = overall_score
            
            # Assign quality grade
            metrics_results['quality_grade'] = await self._assign_quality_grade(overall_score)
            
            # Generate recommendations
            recommendations = await self._generate_quality_recommendations(
                complexity_metrics, maintainability_metrics, documentation_metrics,
                style_metrics, structure_metrics, overall_score
            )
            metrics_results['recommendations'] = recommendations
            
            return {
                'success': True,
                **metrics_results
            }
            
        except Exception as e:
            logger.error(f"Error calculating quality metrics: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def compare_quality_metrics(self, code_versions: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Compare quality metrics across multiple versions of code.
        
        Args:
            code_versions: List of dicts with 'version' and 'code' keys
            
        Returns:
            Comparative quality analysis
        """
        try:
            comparison_results = {
                'analysis_date': datetime.now().isoformat(),
                'versions_analyzed': len(code_versions),
                'version_metrics': [],
                'trends': {},
                'improvements': [],
                'regressions': []
            }
            
            # Calculate metrics for each version
            for version_info in code_versions:
                version = version_info.get('version', 'unknown')
                code = version_info.get('code', '')
                
                metrics = await self.calculate_quality_metrics(code, f'version_{version}')
                if metrics.get('success'):
                    comparison_results['version_metrics'].append({
                        'version': version,
                        'metrics': metrics
                    })
            
            # Analyze trends
            if len(comparison_results['version_metrics']) >= 2:
                trends = await self._analyze_quality_trends(comparison_results['version_metrics'])
                comparison_results['trends'] = trends
                
                # Identify improvements and regressions
                improvements, regressions = await self._identify_quality_changes(
                    comparison_results['version_metrics']
                )
                comparison_results['improvements'] = improvements
                comparison_results['regressions'] = regressions
            
            return {
                'success': True,
                **comparison_results
            }
            
        except Exception as e:
            logger.error(f"Error comparing quality metrics: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _calculate_complexity_metrics(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Calculate code complexity metrics."""
        complexity_metrics = {
            'cyclomatic_complexity': 0,
            'cognitive_complexity': 0,
            'nesting_depth': 0,
            'function_complexity': {},
            'class_complexity': {}
        }
        
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_function = None
                self.current_class = None
                self.complexity = 1  # Base complexity
                self.nesting_level = 0
                self.max_nesting = 0
                self.function_complexities = {}
                self.class_complexities = {}
                
            def visit_FunctionDef(self, node):
                old_function = self.current_function
                old_complexity = self.complexity
                
                self.current_function = node.name
                self.complexity = 1  # Reset for function
                
                self.generic_visit(node)
                
                # Store function complexity
                self.function_complexities[node.name] = self.complexity
                
                self.current_function = old_function
                self.complexity = old_complexity
            
            def visit_ClassDef(self, node):
                old_class = self.current_class
                self.current_class = node.name
                
                class_start_complexity = len(self.function_complexities)
                self.generic_visit(node)
                class_end_complexity = len(self.function_complexities)
                
                # Store class complexity as sum of its methods
                methods_complexity = sum(
                    complexity for name, complexity in self.function_complexities.items()
                    if name not in list(self.function_complexities.keys())[:class_start_complexity]
                )
                self.class_complexities[node.name] = methods_complexity
                
                self.current_class = old_class
            
            def visit_If(self, node):
                self.complexity += 1
                self.nesting_level += 1
                self.max_nesting = max(self.max_nesting, self.nesting_level)
                self.generic_visit(node)
                self.nesting_level -= 1
            
            def visit_For(self, node):
                self.complexity += 1
                self.nesting_level += 1
                self.max_nesting = max(self.max_nesting, self.nesting_level)
                self.generic_visit(node)
                self.nesting_level -= 1
            
            def visit_While(self, node):
                self.complexity += 1
                self.nesting_level += 1
                self.max_nesting = max(self.max_nesting, self.nesting_level)
                self.generic_visit(node)
                self.nesting_level -= 1
            
            def visit_Try(self, node):
                self.complexity += 1
                self.generic_visit(node)
            
            def visit_ExceptHandler(self, node):
                self.complexity += 1
                self.generic_visit(node)
            
            def visit_With(self, node):
                self.complexity += 1
                self.generic_visit(node)
            
            def visit_BoolOp(self, node):
                # Add complexity for boolean operations
                self.complexity += len(node.values) - 1
                self.generic_visit(node)
        
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        
        complexity_metrics['cyclomatic_complexity'] = visitor.complexity
        complexity_metrics['nesting_depth'] = visitor.max_nesting
        complexity_metrics['function_complexity'] = visitor.function_complexities
        complexity_metrics['class_complexity'] = visitor.class_complexities
        
        # Calculate cognitive complexity (simplified)
        complexity_metrics['cognitive_complexity'] = await self._calculate_cognitive_complexity(tree)
        
        return complexity_metrics
    
    async def _calculate_maintainability_metrics(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Calculate maintainability metrics."""
        lines = code.splitlines()
        
        maintainability_metrics = {
            'maintainability_index': 0,
            'lines_of_code': len(lines),
            'effective_lines_of_code': 0,
            'comment_ratio': 0,
            'duplication_ratio': 0,
            'function_length_avg': 0,
            'parameter_count_avg': 0
        }
        
        # Calculate effective lines of code (non-blank, non-comment)
        effective_lines = 0
        comment_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                effective_lines += 1
            elif stripped.startswith('#'):
                comment_lines += 1
        
        maintainability_metrics['effective_lines_of_code'] = effective_lines
        maintainability_metrics['comment_ratio'] = (comment_lines / len(lines) * 100) if lines else 0
        
        # Calculate function metrics
        function_lengths = []
        parameter_counts = []
        
        class MaintainabilityVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Function length
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    func_length = node.end_lineno - node.lineno + 1
                    function_lengths.append(func_length)
                
                # Parameter count
                param_count = len(node.args.args) + len(node.args.kwonlyargs)
                if node.args.vararg:
                    param_count += 1
                if node.args.kwarg:
                    param_count += 1
                parameter_counts.append(param_count)
                
                self.generic_visit(node)
        
        visitor = MaintainabilityVisitor()
        visitor.visit(tree)
        
        if function_lengths:
            maintainability_metrics['function_length_avg'] = sum(function_lengths) / len(function_lengths)
        
        if parameter_counts:
            maintainability_metrics['parameter_count_avg'] = sum(parameter_counts) / len(parameter_counts)
        
        # Calculate duplication ratio (simplified)
        maintainability_metrics['duplication_ratio'] = await self._calculate_duplication_ratio(code)
        
        # Calculate maintainability index
        maintainability_metrics['maintainability_index'] = await self._calculate_maintainability_index(
            maintainability_metrics, tree
        )
        
        return maintainability_metrics
    
    async def _calculate_documentation_metrics(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Calculate documentation coverage metrics."""
        documentation_metrics = {
            'docstring_coverage': 0,
            'functions_with_docstrings': 0,
            'classes_with_docstrings': 0,
            'total_functions': 0,
            'total_classes': 0,
            'comment_density': 0,
            'documentation_quality_score': 0
        }
        
        class DocumentationVisitor(ast.NodeVisitor):
            def __init__(self):
                self.functions_with_docs = 0
                self.classes_with_docs = 0
                self.total_functions = 0
                self.total_classes = 0
                
            def visit_FunctionDef(self, node):
                self.total_functions += 1
                if ast.get_docstring(node):
                    self.functions_with_docs += 1
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                self.total_classes += 1
                if ast.get_docstring(node):
                    self.classes_with_docs += 1
                self.generic_visit(node)
        
        visitor = DocumentationVisitor()
        visitor.visit(tree)
        
        documentation_metrics['functions_with_docstrings'] = visitor.functions_with_docs
        documentation_metrics['classes_with_docstrings'] = visitor.classes_with_docs
        documentation_metrics['total_functions'] = visitor.total_functions
        documentation_metrics['total_classes'] = visitor.total_classes
        
        # Calculate coverage percentages
        total_documentable = visitor.total_functions + visitor.total_classes
        documented = visitor.functions_with_docs + visitor.classes_with_docs
        
        if total_documentable > 0:
            documentation_metrics['docstring_coverage'] = (documented / total_documentable) * 100
        
        # Calculate comment density
        lines = code.splitlines()
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        
        if code_lines > 0:
            documentation_metrics['comment_density'] = (comment_lines / code_lines) * 100
        
        # Calculate documentation quality score
        documentation_metrics['documentation_quality_score'] = (
            documentation_metrics['docstring_coverage'] * 0.7 +
            min(documentation_metrics['comment_density'], 30) * 0.3  # Cap comment density at 30%
        )
        
        return documentation_metrics
    
    async def _calculate_style_metrics(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Calculate code style metrics."""
        style_metrics = {
            'naming_consistency': 0,
            'line_length_violations': 0,
            'whitespace_consistency': 0,
            'import_organization': 0,
            'style_score': 0
        }
        
        lines = code.splitlines()
        
        # Check line length violations (>80 characters)
        long_lines = [i for i, line in enumerate(lines, 1) if len(line) > 80]
        style_metrics['line_length_violations'] = len(long_lines)
        
        # Check naming consistency (simplified)
        naming_score = await self._calculate_naming_consistency(tree)
        style_metrics['naming_consistency'] = naming_score
        
        # Check whitespace consistency (simplified)
        whitespace_score = await self._calculate_whitespace_consistency(lines)
        style_metrics['whitespace_consistency'] = whitespace_score
        
        # Check import organization
        import_score = await self._calculate_import_organization(tree)
        style_metrics['import_organization'] = import_score
        
        # Calculate overall style score
        max_line_violations = len(lines) * 0.1  # Allow 10% violations
        line_score = max(0, 100 - (len(long_lines) / max_line_violations * 100)) if max_line_violations > 0 else 100
        
        style_metrics['style_score'] = (
            naming_score * 0.3 +
            line_score * 0.2 +
            whitespace_score * 0.2 +
            import_score * 0.3
        )
        
        return style_metrics
    
    async def _calculate_structure_metrics(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Calculate code structure metrics."""
        structure_metrics = {
            'cohesion_score': 0,
            'coupling_score': 0,
            'inheritance_depth': 0,
            'class_size_avg': 0,
            'module_organization': 0,
            'structure_score': 0
        }
        
        class StructureVisitor(ast.NodeVisitor):
            def __init__(self):
                self.classes = []
                self.imports = []
                self.current_class = None
                self.class_methods = defaultdict(list)
                
            def visit_ClassDef(self, node):
                self.classes.append(node.name)
                old_class = self.current_class
                self.current_class = node.name
                
                # Count methods in class
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                self.class_methods[node.name] = methods
                
                self.generic_visit(node)
                self.current_class = old_class
            
            def visit_Import(self, node):
                for alias in node.names:
                    self.imports.append(alias.name)
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                if node.module:
                    self.imports.append(node.module)
                self.generic_visit(node)
        
        visitor = StructureVisitor()
        visitor.visit(tree)
        
        # Calculate average class size
        if visitor.class_methods:
            class_sizes = [len(methods) for methods in visitor.class_methods.values()]
            structure_metrics['class_size_avg'] = sum(class_sizes) / len(class_sizes)
        
        # Calculate cohesion (simplified - based on method count consistency)
        if visitor.class_methods:
            class_sizes = [len(methods) for methods in visitor.class_methods.values()]
            if class_sizes:
                avg_size = sum(class_sizes) / len(class_sizes)
                variance = sum((size - avg_size) ** 2 for size in class_sizes) / len(class_sizes)
                structure_metrics['cohesion_score'] = max(0, 100 - variance * 5)
        else:
            structure_metrics['cohesion_score'] = 100
        
        # Calculate coupling (simplified - based on import count)
        coupling_penalty = min(len(visitor.imports) * 2, 50)  # Max 50% penalty
        structure_metrics['coupling_score'] = max(0, 100 - coupling_penalty)
        
        # Module organization (simplified)
        structure_metrics['module_organization'] = 85  # Default good score
        
        # Calculate overall structure score
        structure_metrics['structure_score'] = (
            structure_metrics['cohesion_score'] * 0.4 +
            structure_metrics['coupling_score'] * 0.3 +
            structure_metrics['module_organization'] * 0.3
        )
        
        return structure_metrics
    
    async def _calculate_cognitive_complexity(self, tree: ast.AST) -> int:
        """Calculate cognitive complexity (simplified version)."""
        cognitive_complexity = 0
        
        class CognitiveVisitor(ast.NodeVisitor):
            def __init__(self):
                self.nesting_level = 0
                self.complexity = 0
                
            def visit_If(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1
            
            def visit_For(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1
            
            def visit_While(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1
        
        visitor = CognitiveVisitor()
        visitor.visit(tree)
        
        return visitor.complexity
    
    async def _calculate_duplication_ratio(self, code: str) -> float:
        """Calculate code duplication ratio (simplified)."""
        lines = [line.strip() for line in code.splitlines() if line.strip()]
        
        if len(lines) < 2:
            return 0.0
        
        # Count duplicate lines (simplified approach)
        line_counts = Counter(lines)
        duplicate_lines = sum(count - 1 for count in line_counts.values() if count > 1)
        
        return (duplicate_lines / len(lines)) * 100 if lines else 0.0
    
    async def _calculate_maintainability_index(self, metrics: Dict[str, Any], tree: ast.AST) -> float:
        """Calculate maintainability index using simplified formula."""
        loc = metrics.get('effective_lines_of_code', 1)
        complexity = 1  # Simplified - would need cyclomatic complexity
        
        # Simplified maintainability index calculation
        # MI = 171 - 5.2 * ln(aveV) - 0.23 * aveG - 16.2 * ln(aveLOC)
        # Where aveV = average Halstead volume, aveG = average cyclomatic complexity, aveLOC = average LOC
        
        # Simplified version using available metrics
        if loc > 0:
            mi = 171 - 5.2 * math.log(loc) - 0.23 * complexity - 16.2 * math.log(loc)
            return max(0, min(100, mi))  # Normalize to 0-100 scale
        
        return 50  # Default middle score
    
    async def _calculate_naming_consistency(self, tree: ast.AST) -> float:
        """Calculate naming consistency score."""
        naming_score = 85  # Default good score
        
        class NamingVisitor(ast.NodeVisitor):
            def __init__(self):
                self.function_names = []
                self.class_names = []
                self.variable_names = []
                
            def visit_FunctionDef(self, node):
                self.function_names.append(node.name)
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                self.class_names.append(node.name)
                self.generic_visit(node)
            
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Store):
                    self.variable_names.append(node.id)
                self.generic_visit(node)
        
        visitor = NamingVisitor()
        visitor.visit(tree)
        
        # Check naming conventions (simplified)
        violations = 0
        
        # Functions should use snake_case
        for name in visitor.function_names:
            if not re.match(r'^[a-z_][a-z0-9_]*$', name):
                violations += 1
        
        # Classes should use PascalCase
        for name in visitor.class_names:
            if not re.match(r'^[A-Z][a-zA-Z0-9]*$', name):
                violations += 1
        
        total_names = len(visitor.function_names) + len(visitor.class_names)
        if total_names > 0:
            violation_rate = violations / total_names
            naming_score = max(0, 100 - violation_rate * 100)
        
        return naming_score
    
    async def _calculate_whitespace_consistency(self, lines: List[str]) -> float:
        """Calculate whitespace consistency score."""
        if not lines:
            return 100
        
        # Check for consistent indentation
        indentation_counts = defaultdict(int)
        
        for line in lines:
            if line.strip():  # Skip empty lines
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces > 0:
                    indentation_counts[leading_spaces] += 1
        
        if not indentation_counts:
            return 100
        
        # Check if indentation follows 4-space pattern
        four_space_pattern = all(indent % 4 == 0 for indent in indentation_counts.keys())
        
        return 90 if four_space_pattern else 60
    
    async def _calculate_import_organization(self, tree: ast.AST) -> float:
        """Calculate import organization score."""
        class ImportVisitor(ast.NodeVisitor):
            def __init__(self):
                self.imports = []
                self.non_import_found = False
                
            def visit_Import(self, node):
                if not self.non_import_found:
                    self.imports.append(('import', node.lineno))
                else:
                    return 50  # Imports not at top
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                if not self.non_import_found:
                    self.imports.append(('from', node.lineno))
                else:
                    return 50  # Imports not at top
                self.generic_visit(node)
            
            def visit(self, node):
                if not isinstance(node, (ast.Import, ast.ImportFrom, ast.Module)):
                    self.non_import_found = True
                super().visit(node)
        
        visitor = ImportVisitor()
        visitor.visit(tree)
        
        # Simplified scoring - imports at top get good score
        return 90 if visitor.imports else 100
    
    async def _calculate_overall_quality_score(
        self, 
        complexity_metrics: Dict[str, Any],
        maintainability_metrics: Dict[str, Any],
        documentation_metrics: Dict[str, Any],
        style_metrics: Dict[str, Any],
        structure_metrics: Dict[str, Any]
    ) -> float:
        """Calculate overall quality score."""
        
        # Normalize complexity score (lower is better)
        complexity_score = max(0, 100 - complexity_metrics.get('cyclomatic_complexity', 0) * 5)
        
        # Use maintainability index
        maintainability_score = maintainability_metrics.get('maintainability_index', 50)
        
        # Use documentation quality score
        documentation_score = documentation_metrics.get('documentation_quality_score', 0)
        
        # Use style score
        style_score = style_metrics.get('style_score', 0)
        
        # Use structure score
        structure_score = structure_metrics.get('structure_score', 0)
        
        # Weighted average
        overall_score = (
            complexity_score * 0.25 +
            maintainability_score * 0.25 +
            documentation_score * 0.20 +
            style_score * 0.15 +
            structure_score * 0.15
        )
        
        return round(overall_score, 2)
    
    async def _assign_quality_grade(self, score: float) -> str:
        """Assign quality grade based on score."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    async def _generate_quality_recommendations(
        self,
        complexity_metrics: Dict[str, Any],
        maintainability_metrics: Dict[str, Any],
        documentation_metrics: Dict[str, Any],
        style_metrics: Dict[str, Any],
        structure_metrics: Dict[str, Any],
        overall_score: float
    ) -> List[str]:
        """Generate quality improvement recommendations."""
        recommendations = []
        
        # Complexity recommendations
        if complexity_metrics.get('cyclomatic_complexity', 0) > 10:
            recommendations.append("Reduce cyclomatic complexity by breaking down complex functions")
        
        if complexity_metrics.get('nesting_depth', 0) > 4:
            recommendations.append("Reduce nesting depth to improve readability")
        
        # Maintainability recommendations
        if maintainability_metrics.get('maintainability_index', 0) < 60:
            recommendations.append("Improve maintainability by reducing complexity and improving documentation")
        
        if maintainability_metrics.get('function_length_avg', 0) > 30:
            recommendations.append("Break down long functions into smaller, focused functions")
        
        # Documentation recommendations
        if documentation_metrics.get('docstring_coverage', 0) < 60:
            recommendations.append("Add docstrings to functions and classes to improve documentation coverage")
        
        if documentation_metrics.get('comment_density', 0) < 10:
            recommendations.append("Add more comments to explain complex logic")
        
        # Style recommendations
        if style_metrics.get('line_length_violations', 0) > 0:
            recommendations.append("Fix line length violations (keep lines under 80 characters)")
        
        if style_metrics.get('naming_consistency', 0) < 80:
            recommendations.append("Improve naming consistency (use snake_case for functions, PascalCase for classes)")
        
        # Structure recommendations
        if structure_metrics.get('coupling_score', 0) < 70:
            recommendations.append("Reduce coupling by minimizing dependencies between modules")
        
        if structure_metrics.get('cohesion_score', 0) < 70:
            recommendations.append("Improve cohesion by grouping related functionality together")
        
        # Overall recommendations
        if overall_score < 70:
            recommendations.append("Focus on overall code quality improvement through refactoring")
        
        if not recommendations:
            recommendations.append("Code quality is good! Continue following best practices")
        
        return recommendations[:8]  # Limit to 8 recommendations
    
    async def _analyze_quality_trends(self, version_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze quality trends across versions."""
        trends = {
            'quality_score_trend': 'stable',
            'complexity_trend': 'stable',
            'documentation_trend': 'stable',
            'overall_direction': 'stable'
        }
        
        if len(version_metrics) < 2:
            return trends
        
        # Extract scores
        quality_scores = []
        complexity_scores = []
        doc_scores = []
        
        for vm in version_metrics:
            metrics = vm.get('metrics', {})
            quality_scores.append(metrics.get('overall_quality_score', 0))
            complexity_scores.append(metrics.get('complexity_metrics', {}).get('cyclomatic_complexity', 0))
            doc_scores.append(metrics.get('documentation_metrics', {}).get('docstring_coverage', 0))
        
        # Analyze trends
        if len(quality_scores) >= 2:
            quality_change = quality_scores[-1] - quality_scores[0]
            if quality_change > 5:
                trends['quality_score_trend'] = 'improving'
            elif quality_change < -5:
                trends['quality_score_trend'] = 'declining'
        
        if len(complexity_scores) >= 2:
            complexity_change = complexity_scores[-1] - complexity_scores[0]
            if complexity_change > 2:
                trends['complexity_trend'] = 'increasing'
            elif complexity_change < -2:
                trends['complexity_trend'] = 'decreasing'
        
        if len(doc_scores) >= 2:
            doc_change = doc_scores[-1] - doc_scores[0]
            if doc_change > 10:
                trends['documentation_trend'] = 'improving'
            elif doc_change < -10:
                trends['documentation_trend'] = 'declining'
        
        # Overall direction
        positive_trends = sum(1 for trend in [trends['quality_score_trend'], trends['documentation_trend']] if trend == 'improving')
        negative_trends = sum(1 for trend in [trends['quality_score_trend'], trends['documentation_trend']] if trend == 'declining')
        negative_trends += 1 if trends['complexity_trend'] == 'increasing' else 0
        positive_trends += 1 if trends['complexity_trend'] == 'decreasing' else 0
        
        if positive_trends > negative_trends:
            trends['overall_direction'] = 'improving'
        elif negative_trends > positive_trends:
            trends['overall_direction'] = 'declining'
        
        return trends
    
    async def _identify_quality_changes(self, version_metrics: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """Identify quality improvements and regressions."""
        improvements = []
        regressions = []
        
        if len(version_metrics) < 2:
            return improvements, regressions
        
        latest = version_metrics[-1]['metrics']
        previous = version_metrics[-2]['metrics']
        
        # Compare scores
        quality_change = latest.get('overall_quality_score', 0) - previous.get('overall_quality_score', 0)
        if quality_change > 5:
            improvements.append(f"Overall quality score improved by {quality_change:.1f} points")
        elif quality_change < -5:
            regressions.append(f"Overall quality score declined by {abs(quality_change):.1f} points")
        
        # Compare complexity
        latest_complexity = latest.get('complexity_metrics', {}).get('cyclomatic_complexity', 0)
        previous_complexity = previous.get('complexity_metrics', {}).get('cyclomatic_complexity', 0)
        complexity_change = latest_complexity - previous_complexity
        
        if complexity_change < -2:
            improvements.append(f"Cyclomatic complexity reduced by {abs(complexity_change)}")
        elif complexity_change > 2:
            regressions.append(f"Cyclomatic complexity increased by {complexity_change}")
        
        # Compare documentation
        latest_doc = latest.get('documentation_metrics', {}).get('docstring_coverage', 0)
        previous_doc = previous.get('documentation_metrics', {}).get('docstring_coverage', 0)
        doc_change = latest_doc - previous_doc
        
        if doc_change > 10:
            improvements.append(f"Documentation coverage improved by {doc_change:.1f}%")
        elif doc_change < -10:
            regressions.append(f"Documentation coverage declined by {abs(doc_change):.1f}%")
        
        return improvements, regressions