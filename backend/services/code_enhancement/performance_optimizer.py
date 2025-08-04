"""
Performance Optimizer

Analyzes Python code for performance bottlenecks and provides optimization
recommendations for improved execution speed and resource usage.
"""

import ast
import logging
import time
import gc
import psutil
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import inspect
import sys
from functools import wraps

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """
    Analyzes code performance and provides optimization recommendations
    for better execution speed and resource efficiency.
    """
    
    def __init__(self):
        self.performance_patterns = {
            'inefficient_loops': r'for.*in.*range\(len\(',
            'string_concatenation': r'\+\s*["\']',
            'unnecessary_comprehensions': r'\[.*for.*in.*\]',
            'repeated_calculations': r'def.*\(\):.*return.*\(',
            'memory_leaks': r'global\s+\w+|^(?!.*del\s)',
        }
        
        self.optimization_rules = [
            'use_list_comprehensions',
            'avoid_global_variables',
            'use_generators_for_large_data',
            'optimize_database_queries',
            'cache_expensive_operations',
            'use_built_in_functions',
            'minimize_object_creation'
        ]
    
    async def analyze_performance(self, code: str, filename: str = 'code.py') -> Dict[str, Any]:
        """
        Analyze code for performance issues and optimization opportunities.
        
        Args:
            code: Python code string to analyze
            filename: Optional filename for context
            
        Returns:
            Performance analysis results with recommendations
        """
        try:
            analysis_results = {
                'analysis_date': datetime.now().isoformat(),
                'filename': filename,
                'performance_issues': [],
                'optimization_opportunities': [],
                'resource_usage': {},
                'recommendations': [],
                'estimated_improvements': {}
            }
            
            # Parse the code
            try:
                tree = ast.parse(code, filename=filename)
            except SyntaxError as e:
                return {
                    'success': False,
                    'error': f'Syntax error in code: {e.msg}'
                }
            
            # Analyze AST for performance patterns
            performance_issues = await self._analyze_ast_performance(tree, code, filename)
            analysis_results['performance_issues'] = performance_issues
            
            # Identify optimization opportunities
            optimization_opportunities = await self._identify_optimizations(tree, code)
            analysis_results['optimization_opportunities'] = optimization_opportunities
            
            # Analyze resource usage patterns
            resource_analysis = await self._analyze_resource_usage(tree, code)
            analysis_results['resource_usage'] = resource_analysis
            
            # Generate recommendations
            recommendations = await self._generate_performance_recommendations(
                performance_issues, optimization_opportunities, resource_analysis
            )
            analysis_results['recommendations'] = recommendations
            
            # Estimate potential improvements
            improvements = await self._estimate_improvements(performance_issues, optimization_opportunities)
            analysis_results['estimated_improvements'] = improvements
            
            return {
                'success': True,
                **analysis_results
            }
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def profile_code_execution(self, code: str, iterations: int = 100) -> Dict[str, Any]:
        """
        Profile code execution to measure actual performance metrics.
        
        Args:
            code: Python code string to profile
            iterations: Number of iterations to run for profiling
            
        Returns:
            Profiling results with timing and resource usage data
        """
        try:
            profiling_results = {
                'profiling_date': datetime.now().isoformat(),
                'iterations': iterations,
                'timing_results': {},
                'memory_usage': {},
                'cpu_usage': {},
                'bottlenecks': []
            }
            
            # Prepare code for execution
            compiled_code = compile(code, 'profiled_code.py', 'exec')
            
            # Memory usage before execution
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Time execution
            execution_times = []
            for i in range(iterations):
                start_time = time.perf_counter()
                
                # Execute code
                namespace = {}
                exec(compiled_code, namespace)
                
                end_time = time.perf_counter()
                execution_times.append(end_time - start_time)
                
                # Cleanup
                del namespace
                if i % 10 == 0:  # Garbage collect every 10 iterations
                    gc.collect()
            
            # Memory usage after execution
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            
            # Calculate timing statistics
            avg_time = sum(execution_times) / len(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            
            profiling_results['timing_results'] = {
                'average_execution_time_ms': round(avg_time * 1000, 4),
                'min_execution_time_ms': round(min_time * 1000, 4),
                'max_execution_time_ms': round(max_time * 1000, 4),
                'total_execution_time_ms': round(sum(execution_times) * 1000, 4),
                'execution_consistency': round((1 - (max_time - min_time) / avg_time) * 100, 2)
            }
            
            profiling_results['memory_usage'] = {
                'memory_before_mb': round(memory_before, 2),
                'memory_after_mb': round(memory_after, 2),
                'memory_increase_mb': round(memory_after - memory_before, 2),
                'memory_per_iteration_kb': round((memory_after - memory_before) * 1024 / iterations, 2)
            }
            
            # Identify potential bottlenecks
            if avg_time > 0.1:  # More than 100ms average
                profiling_results['bottlenecks'].append({
                    'type': 'slow_execution',
                    'description': f'Average execution time ({avg_time*1000:.2f}ms) is relatively slow',
                    'suggestion': 'Consider optimizing algorithmic complexity'
                })
            
            if memory_after - memory_before > 10:  # More than 10MB increase
                profiling_results['bottlenecks'].append({
                    'type': 'memory_usage',
                    'description': f'High memory usage increase ({memory_after - memory_before:.2f}MB)',
                    'suggestion': 'Review memory allocation and consider using generators or streaming'
                })
            
            return {
                'success': True,
                **profiling_results
            }
            
        except Exception as e:
            logger.error(f"Error profiling code execution: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _analyze_ast_performance(self, tree: ast.AST, code: str, filename: str) -> List[Dict[str, Any]]:
        """Analyze AST for performance issues."""
        issues = []
        
        class PerformanceVisitor(ast.NodeVisitor):
            def visit_For(self, node):
                # Check for inefficient range(len()) patterns
                if (isinstance(node.iter, ast.Call) and 
                    isinstance(node.iter.func, ast.Name) and 
                    node.iter.func.id == 'range' and
                    len(node.iter.args) == 1 and
                    isinstance(node.iter.args[0], ast.Call) and
                    isinstance(node.iter.args[0].func, ast.Name) and
                    node.iter.args[0].func.id == 'len'):
                    
                    issues.append({
                        'type': 'inefficient_loop',
                        'severity': 'warning',
                        'line': node.lineno,
                        'message': 'Inefficient range(len()) pattern detected',
                        'file': filename,
                        'suggestion': 'Use enumerate() or iterate directly over the sequence',
                        'optimization_potential': 'medium'
                    })
                
                # Check for nested loops
                nested_loops = [n for n in ast.walk(node) if isinstance(n, (ast.For, ast.While)) and n != node]
                if len(nested_loops) > 1:
                    issues.append({
                        'type': 'nested_loops',
                        'severity': 'warning',
                        'line': node.lineno,
                        'message': f'Deeply nested loops detected (depth: {len(nested_loops) + 1})',
                        'file': filename,
                        'suggestion': 'Consider algorithmic optimization or vectorization',
                        'optimization_potential': 'high'
                    })
                
                self.generic_visit(node)
            
            def visit_ListComp(self, node):
                # Check for complex list comprehensions
                if len(node.generators) > 2:
                    issues.append({
                        'type': 'complex_comprehension',
                        'severity': 'info',
                        'line': node.lineno,
                        'message': 'Complex list comprehension with multiple generators',
                        'file': filename,
                        'suggestion': 'Consider breaking into separate loops for readability',
                        'optimization_potential': 'low'
                    })
                
                self.generic_visit(node)
            
            def visit_Call(self, node):
                # Check for inefficient string operations
                if (isinstance(node.func, ast.Attribute) and 
                    isinstance(node.func.value, ast.Str) and
                    node.func.attr in ['join', 'replace', 'split']):
                    
                    # Check if used in a loop context
                    # This is a simplified check
                    issues.append({
                        'type': 'string_operation',
                        'severity': 'info',
                        'line': node.lineno,
                        'message': 'String operation detected - consider efficiency in loops',
                        'file': filename,
                        'suggestion': 'Use efficient string methods and avoid repeated concatenation',
                        'optimization_potential': 'medium'
                    })
                
                # Check for repeated function calls
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in ['len', 'max', 'min', 'sum'] and self._in_loop_context(node):
                        issues.append({
                            'type': 'repeated_calculation',
                            'severity': 'warning',
                            'line': node.lineno,
                            'message': f'Function "{func_name}" called repeatedly in loop',
                            'file': filename,
                            'suggestion': 'Cache the result outside the loop',
                            'optimization_potential': 'medium'
                        })
                
                self.generic_visit(node)
            
            def visit_Global(self, node):
                issues.append({
                    'type': 'global_variable',
                    'severity': 'warning',
                    'line': node.lineno,
                    'message': 'Global variable usage detected',
                    'file': filename,
                    'suggestion': 'Minimize global variable usage for better performance',
                    'optimization_potential': 'low'
                })
                
                self.generic_visit(node)
            
            def visit_Import(self, node):
                # Check for imports inside functions
                parent_node = getattr(node, 'parent', None)
                if isinstance(parent_node, ast.FunctionDef):
                    issues.append({
                        'type': 'import_in_function',
                        'severity': 'warning',
                        'line': node.lineno,
                        'message': 'Import statement inside function',
                        'file': filename,
                        'suggestion': 'Move imports to module level for better performance',
                        'optimization_potential': 'low'
                    })
                
                self.generic_visit(node)
            
            def _in_loop_context(self, node):
                """Check if node is inside a loop (simplified)."""
                # This is a simplified implementation
                # In a full implementation, you'd traverse up the AST
                return False
        
        visitor = PerformanceVisitor()
        visitor.visit(tree)
        
        return issues
    
    async def _identify_optimizations(self, tree: ast.AST, code: str) -> List[Dict[str, Any]]:
        """Identify optimization opportunities."""
        opportunities = []
        
        class OptimizationVisitor(ast.NodeVisitor):
            def visit_For(self, node):
                # Suggest list comprehensions where appropriate
                if self._can_use_comprehension(node):
                    opportunities.append({
                        'type': 'list_comprehension',
                        'line': node.lineno,
                        'description': 'Loop can be replaced with list comprehension',
                        'benefit': 'Faster execution and more Pythonic code',
                        'implementation_effort': 'low'
                    })
                
                self.generic_visit(node)
            
            def visit_FunctionDef(self, node):
                # Check for functions that can benefit from caching
                if self._can_benefit_from_caching(node):
                    opportunities.append({
                        'type': 'function_caching',
                        'line': node.lineno,
                        'description': f'Function "{node.name}" can benefit from caching',
                        'benefit': 'Avoid repeated expensive calculations',
                        'implementation_effort': 'low'
                    })
                
                # Check for generator opportunities
                if self._can_use_generator(node):
                    opportunities.append({
                        'type': 'generator_function',
                        'line': node.lineno,
                        'description': f'Function "{node.name}" can be converted to generator',
                        'benefit': 'Reduced memory usage for large datasets',
                        'implementation_effort': 'medium'
                    })
                
                self.generic_visit(node)
            
            def _can_use_comprehension(self, node):
                """Check if a for loop can be replaced with comprehension."""
                # Simplified check for basic append patterns
                if len(node.body) == 1 and isinstance(node.body[0], ast.Expr):
                    call = node.body[0].value
                    if (isinstance(call, ast.Call) and 
                        isinstance(call.func, ast.Attribute) and
                        call.func.attr == 'append'):
                        return True
                return False
            
            def _can_benefit_from_caching(self, node):
                """Check if function can benefit from caching."""
                # Look for expensive operations like loops, recursive calls
                for child in ast.walk(node):
                    if isinstance(child, (ast.For, ast.While)):
                        return True
                    if (isinstance(child, ast.Call) and 
                        isinstance(child.func, ast.Name) and
                        child.func.id == node.name):  # Recursive call
                        return True
                return False
            
            def _can_use_generator(self, node):
                """Check if function can be converted to generator."""
                # Look for functions that build and return lists
                for child in ast.walk(node):
                    if (isinstance(child, ast.Return) and
                        isinstance(child.value, ast.List)):
                        return True
                return False
        
        visitor = OptimizationVisitor()
        visitor.visit(tree)
        
        return opportunities
    
    async def _analyze_resource_usage(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Analyze potential resource usage patterns."""
        resource_analysis = {
            'memory_concerns': [],
            'cpu_intensive_operations': [],
            'io_operations': [],
            'estimated_complexity': 'O(1)'
        }
        
        class ResourceVisitor(ast.NodeVisitor):
            def __init__(self):
                self.loop_depth = 0
                self.max_loop_depth = 0
                
            def visit_For(self, node):
                self.loop_depth += 1
                self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
                
                # Check for memory-intensive operations
                for child in ast.walk(node):
                    if isinstance(child, ast.List) and len(getattr(child, 'elts', [])) > 1000:
                        resource_analysis['memory_concerns'].append({
                            'type': 'large_list_creation',
                            'line': node.lineno,
                            'description': 'Large list created in loop'
                        })
                
                self.generic_visit(node)
                self.loop_depth -= 1
            
            def visit_While(self, node):
                self.loop_depth += 1
                self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
                self.generic_visit(node)
                self.loop_depth -= 1
            
            def visit_Call(self, node):
                # Check for I/O operations
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['open', 'print', 'input']:
                        resource_analysis['io_operations'].append({
                            'type': 'file_io',
                            'line': node.lineno,
                            'function': node.func.id
                        })
                
                # Check for CPU-intensive operations
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['sort', 'sorted', 'max', 'min', 'sum']:
                        resource_analysis['cpu_intensive_operations'].append({
                            'type': 'computation',
                            'line': node.lineno,
                            'operation': node.func.id
                        })
                
                self.generic_visit(node)
        
        visitor = ResourceVisitor()
        visitor.visit(tree)
        
        # Estimate algorithmic complexity based on loop depth
        if visitor.max_loop_depth == 0:
            resource_analysis['estimated_complexity'] = 'O(1)'
        elif visitor.max_loop_depth == 1:
            resource_analysis['estimated_complexity'] = 'O(n)'
        elif visitor.max_loop_depth == 2:
            resource_analysis['estimated_complexity'] = 'O(n²)'
        else:
            resource_analysis['estimated_complexity'] = f'O(n^{visitor.max_loop_depth})'
        
        return resource_analysis
    
    async def _generate_performance_recommendations(
        self, 
        performance_issues: List[Dict[str, Any]], 
        optimization_opportunities: List[Dict[str, Any]],
        resource_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate performance optimization recommendations."""
        recommendations = []
        
        # Recommendations based on issues
        issue_counts = {}
        for issue in performance_issues:
            issue_type = issue.get('type', 'unknown')
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        if issue_counts.get('inefficient_loop', 0) > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'loop_optimization',
                'title': 'Optimize Loop Patterns',
                'description': f'Found {issue_counts["inefficient_loop"]} inefficient loop patterns',
                'actions': [
                    'Replace range(len()) with enumerate() or direct iteration',
                    'Use list comprehensions where appropriate',
                    'Consider vectorized operations for numerical computations'
                ],
                'estimated_improvement': '20-40% faster execution'
            })
        
        if issue_counts.get('nested_loops', 0) > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'algorithmic_optimization',
                'title': 'Reduce Algorithmic Complexity',
                'description': f'Found {issue_counts["nested_loops"]} nested loop patterns',
                'actions': [
                    'Review algorithm design for lower complexity alternatives',
                    'Consider using hash tables or sets for O(1) lookups',
                    'Implement early termination conditions'
                ],
                'estimated_improvement': '50-90% faster for large datasets'
            })
        
        # Recommendations based on opportunities
        if optimization_opportunities:
            list_comp_ops = [op for op in optimization_opportunities if op['type'] == 'list_comprehension']
            if list_comp_ops:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'pythonic_optimization',
                    'title': 'Use List Comprehensions',
                    'description': f'Found {len(list_comp_ops)} opportunities for list comprehensions',
                    'actions': [
                        'Replace simple loops with list comprehensions',
                        'Use generator expressions for memory efficiency'
                    ],
                    'estimated_improvement': '10-30% faster execution'
                })
        
        # Recommendations based on resource analysis
        if resource_analysis.get('memory_concerns'):
            recommendations.append({
                'priority': 'medium',
                'category': 'memory_optimization',
                'title': 'Optimize Memory Usage',
                'description': 'Memory usage concerns detected',
                'actions': [
                    'Use generators instead of lists for large datasets',
                    'Implement streaming processing for large files',
                    'Clear unused variables explicitly'
                ],
                'estimated_improvement': '30-70% less memory usage'
            })
        
        if not recommendations:
            recommendations.append({
                'priority': 'low',
                'category': 'maintenance',
                'title': 'Code Performance Looks Good',
                'description': 'No significant performance issues detected',
                'actions': [
                    'Continue monitoring performance with profiling',
                    'Consider adding performance tests'
                ],
                'estimated_improvement': 'Maintain current performance'
            })
        
        return recommendations
    
    async def _estimate_improvements(
        self, 
        performance_issues: List[Dict[str, Any]], 
        optimization_opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Estimate potential performance improvements."""
        improvements = {
            'execution_speed': {
                'low_estimate': 0,
                'high_estimate': 0,
                'confidence': 'medium'
            },
            'memory_usage': {
                'reduction_percentage': 0,
                'confidence': 'medium'
            },
            'maintainability': {
                'improvement_score': 0,
                'confidence': 'high'
            }
        }
        
        # Calculate speed improvements
        speed_improvement = 0
        for issue in performance_issues:
            potential = issue.get('optimization_potential', 'low')
            if potential == 'high':
                speed_improvement += 30
            elif potential == 'medium':
                speed_improvement += 15
            else:
                speed_improvement += 5
        
        improvements['execution_speed']['low_estimate'] = min(speed_improvement * 0.5, 80)
        improvements['execution_speed']['high_estimate'] = min(speed_improvement, 90)
        
        # Calculate memory improvements
        memory_issues = [i for i in performance_issues if 'memory' in i.get('type', '').lower()]
        if memory_issues:
            improvements['memory_usage']['reduction_percentage'] = min(len(memory_issues) * 15, 60)
        
        # Calculate maintainability improvements
        total_optimizations = len(performance_issues) + len(optimization_opportunities)
        improvements['maintainability']['improvement_score'] = min(total_optimizations * 5, 40)
        
        return improvements