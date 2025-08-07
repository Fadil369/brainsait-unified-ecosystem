"""
Debug Automation

Provides automated debugging utilities and error analysis for Python applications,
helping identify and resolve common programming issues.
"""

import ast
import logging
import traceback
import sys
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import inspect

logger = logging.getLogger(__name__)

class DebugAutomation:
    """
    Automates debugging processes and provides intelligent error analysis
    and resolution suggestions for Python code.
    """
    
    def __init__(self):
        self.common_errors = {
            'NameError': 'Variable or function name not defined',
            'TypeError': 'Incorrect type used in operation',
            'AttributeError': 'Object attribute does not exist',
            'IndexError': 'List index out of range',
            'KeyError': 'Dictionary key does not exist',
            'ValueError': 'Inappropriate value for operation',
            'IndentationError': 'Incorrect code indentation',
            'SyntaxError': 'Invalid Python syntax',
            'ImportError': 'Module import failed',
            'FileNotFoundError': 'File or directory not found'
        }
        
        self.debugging_patterns = [
            'missing_imports',
            'undefined_variables',
            'type_mismatches',
            'logical_errors',
            'exception_handling_issues'
        ]
    
    async def analyze_error(self, error_traceback: str, code: str = None) -> Dict[str, Any]:
        """
        Analyze an error traceback and provide debugging suggestions.
        
        Args:
            error_traceback: Full error traceback string
            code: Optional source code for additional analysis
            
        Returns:
            Error analysis with debugging suggestions
        """
        try:
            analysis_results = {
                'analysis_date': datetime.now().isoformat(),
                'error_info': {},
                'root_cause': {},
                'debugging_steps': [],
                'code_suggestions': [],
                'prevention_tips': []
            }
            
            # Parse error information
            error_info = await self._parse_error_traceback(error_traceback)
            analysis_results['error_info'] = error_info
            
            # Identify root cause
            root_cause = await self._identify_root_cause(error_info, code)
            analysis_results['root_cause'] = root_cause
            
            # Generate debugging steps
            debugging_steps = await self._generate_debugging_steps(error_info, root_cause)
            analysis_results['debugging_steps'] = debugging_steps
            
            # Provide code suggestions
            if code:
                code_suggestions = await self._generate_code_suggestions(error_info, code)
                analysis_results['code_suggestions'] = code_suggestions
            
            # Prevention tips
            prevention_tips = await self._generate_prevention_tips(error_info)
            analysis_results['prevention_tips'] = prevention_tips
            
            return {
                'success': True,
                **analysis_results
            }
            
        except Exception as e:
            logger.error(f"Error analyzing error traceback: {str(e)}")
            return {'success': False, 'error': 'An internal error occurred during error analysis.'}
    
    async def detect_potential_bugs(self, code: str, filename: str = 'code.py') -> Dict[str, Any]:
        """
        Analyze code for potential bugs and issues.
        
        Args:
            code: Python code string to analyze
            filename: Optional filename for context
            
        Returns:
            Bug detection results with suggestions
        """
        try:
            bug_analysis = {
                'analysis_date': datetime.now().isoformat(),
                'filename': filename,
                'potential_bugs': [],
                'code_smells': [],
                'logic_issues': [],
                'recommendations': []
            }
            
            # Parse the code
            try:
                tree = ast.parse(code, filename=filename)
            except SyntaxError as e:
                return {
                    'success': True,
                    'syntax_error': {
                        'line': e.lineno,
                        'message': e.msg,
                        'suggestion': 'Fix syntax error before proceeding with bug analysis'
                    }
                }
            
            # Detect potential bugs
            potential_bugs = await self._detect_bugs_in_ast(tree, code, filename)
            bug_analysis['potential_bugs'] = potential_bugs
            
            # Detect code smells
            code_smells = await self._detect_code_smells(tree, code, filename)
            bug_analysis['code_smells'] = code_smells
            
            # Detect logic issues
            logic_issues = await self._detect_logic_issues(tree, code, filename)
            bug_analysis['logic_issues'] = logic_issues
            
            # Generate recommendations
            recommendations = await self._generate_bug_fix_recommendations(
                potential_bugs, code_smells, logic_issues
            )
            bug_analysis['recommendations'] = recommendations
            
            return {
                'success': True,
                **bug_analysis
            }
            
        except Exception as e:
            logger.error(f"Error detecting potential bugs: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def suggest_debugging_strategy(self, problem_description: str) -> Dict[str, Any]:
        """
        Suggest debugging strategy based on problem description.
        
        Args:
            problem_description: Description of the issue or problem
            
        Returns:
            Debugging strategy suggestions
        """
        try:
            strategy = {
                'analysis_date': datetime.now().isoformat(),
                'problem_category': '',
                'debugging_approach': [],
                'tools_to_use': [],
                'common_solutions': [],
                'next_steps': []
            }
            
            # Categorize the problem
            problem_category = await self._categorize_problem(problem_description)
            strategy['problem_category'] = problem_category
            
            # Suggest debugging approach
            debugging_approach = await self._suggest_debugging_approach(problem_category)
            strategy['debugging_approach'] = debugging_approach
            
            # Recommend tools
            tools = await self._recommend_debugging_tools(problem_category)
            strategy['tools_to_use'] = tools
            
            # Provide common solutions
            common_solutions = await self._provide_common_solutions(problem_category)
            strategy['common_solutions'] = common_solutions
            
            # Next steps
            next_steps = await self._suggest_next_steps(problem_category)
            strategy['next_steps'] = next_steps
            
            return {
                'success': True,
                **strategy
            }
            
        except Exception as e:
            logger.error(f"Error suggesting debugging strategy: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _parse_error_traceback(self, error_traceback: str) -> Dict[str, Any]:
        """Parse error traceback to extract useful information."""
        error_info = {
            'error_type': 'Unknown',
            'error_message': '',
            'file_name': '',
            'line_number': 0,
            'function_name': '',
            'code_context': ''
        }
        
        lines = error_traceback.strip().split('\n')
        
        # Find the error type and message (usually the last line)
        if lines:
            last_line = lines[-1]
            if ':' in last_line:
                error_type, error_message = last_line.split(':', 1)
                error_info['error_type'] = error_type.strip()
                error_info['error_message'] = error_message.strip()
        
        # Parse traceback lines
        for i, line in enumerate(lines):
            if line.strip().startswith('File "'):
                # Extract file name and line number
                match = re.search(r'File "([^"]+)", line (\d+)', line)
                if match:
                    error_info['file_name'] = match.group(1)
                    error_info['line_number'] = int(match.group(2))
                
                # Extract function name
                func_match = re.search(r'in (\w+)', line)
                if func_match:
                    error_info['function_name'] = func_match.group(1)
                
                # Get code context (next line)
                if i + 1 < len(lines):
                    error_info['code_context'] = lines[i + 1].strip()
                
                break
        
        return error_info
    
    async def _identify_root_cause(self, error_info: Dict[str, Any], code: str = None) -> Dict[str, Any]:
        """Identify the root cause of the error."""
        error_type = error_info.get('error_type', '')
        error_message = error_info.get('error_message', '')
        
        root_cause = {
            'category': 'unknown',
            'description': '',
            'likely_causes': [],
            'confidence': 'medium'
        }
        
        # Analyze based on error type
        if error_type == 'NameError':
            root_cause.update({
                'category': 'undefined_variable',
                'description': 'Variable or function name is not defined',
                'likely_causes': [
                    'Typo in variable name',
                    'Variable used before assignment',
                    'Missing import statement',
                    'Variable scope issue'
                ],
                'confidence': 'high'
            })
        
        elif error_type == 'TypeError':
            root_cause.update({
                'category': 'type_mismatch',
                'description': 'Incorrect data type used in operation',
                'likely_causes': [
                    'Wrong data type passed to function',
                    'Attempting unsupported operation on type',
                    'Missing type conversion',
                    'None value where object expected'
                ],
                'confidence': 'high'
            })
        
        elif error_type == 'AttributeError':
            root_cause.update({
                'category': 'missing_attribute',
                'description': 'Object does not have the expected attribute',
                'likely_causes': [
                    'Typo in attribute name',
                    'Wrong object type',
                    'None value where object expected',
                    'Missing method or property'
                ],
                'confidence': 'high'
            })
        
        elif error_type == 'IndexError':
            root_cause.update({
                'category': 'index_out_of_bounds',
                'description': 'List or sequence index is out of range',
                'likely_causes': [
                    'Empty list or sequence',
                    'Index calculation error',
                    'Loop boundary issue',
                    'Off-by-one error'
                ],
                'confidence': 'high'
            })
        
        elif error_type == 'KeyError':
            root_cause.update({
                'category': 'missing_key',
                'description': 'Dictionary key does not exist',
                'likely_causes': [
                    'Typo in key name',
                    'Key not initialized',
                    'Case sensitivity issue',
                    'Dynamic key generation error'
                ],
                'confidence': 'high'
            })
        
        elif error_type == 'ImportError' or error_type == 'ModuleNotFoundError':
            root_cause.update({
                'category': 'import_issue',
                'description': 'Module or package cannot be imported',
                'likely_causes': [
                    'Module not installed',
                    'Incorrect module name',
                    'Python path issue',
                    'Virtual environment not activated'
                ],
                'confidence': 'high'
            })
        
        return root_cause
    
    async def _generate_debugging_steps(self, error_info: Dict[str, Any], root_cause: Dict[str, Any]) -> List[str]:
        """Generate step-by-step debugging instructions."""
        steps = []
        error_type = error_info.get('error_type', '')
        category = root_cause.get('category', '')
        
        # General first steps
        steps.append("1. Read the error message carefully and identify the exact line where error occurred")
        steps.append(f"2. Look at line {error_info.get('line_number', 'N/A')} in file {error_info.get('file_name', 'N/A')}")
        
        # Specific steps based on error category
        if category == 'undefined_variable':
            steps.extend([
                "3. Check if the variable name is spelled correctly",
                "4. Verify the variable is defined before use",
                "5. Check if the variable is in the correct scope",
                "6. Look for missing import statements"
            ])
        
        elif category == 'type_mismatch':
            steps.extend([
                "3. Check the data types of variables involved",
                "4. Print variable types using type() function",
                "5. Add type conversion if needed",
                "6. Check for None values"
            ])
        
        elif category == 'missing_attribute':
            steps.extend([
                "3. Check if the object has the expected attribute",
                "4. Use dir() to list available attributes",
                "5. Verify object initialization",
                "6. Check for None values"
            ])
        
        elif category == 'index_out_of_bounds':
            steps.extend([
                "3. Check the length of the list/sequence",
                "4. Print index values before accessing",
                "5. Add bounds checking",
                "6. Review loop conditions"
            ])
        
        elif category == 'missing_key':
            steps.extend([
                "3. Check if the key exists using 'in' operator",
                "4. Use .get() method with default value",
                "5. Print dictionary keys",
                "6. Check for case sensitivity"
            ])
        
        elif category == 'import_issue':
            steps.extend([
                "3. Check if module is installed (pip list)",
                "4. Verify module name spelling",
                "5. Check Python path and virtual environment",
                "6. Install missing packages"
            ])
        
        # General debugging steps
        steps.extend([
            f"{len(steps) + 1}. Add print statements to trace execution",
            f"{len(steps) + 2}. Use debugger (pdb) for step-by-step execution",
            f"{len(steps) + 3}. Test with simpler inputs",
            f"{len(steps) + 4}. Review recent changes to the code"
        ])
        
        return steps
    
    async def _generate_code_suggestions(self, error_info: Dict[str, Any], code: str) -> List[Dict[str, str]]:
        """Generate specific code suggestions to fix the error."""
        suggestions = []
        error_type = error_info.get('error_type', '')
        line_number = error_info.get('line_number', 0)
        
        if error_type == 'NameError':
            suggestions.append({
                'type': 'variable_check',
                'description': 'Add variable existence check',
                'code': """# Check if variable exists before use
if 'variable_name' in locals() or 'variable_name' in globals():
    # use variable_name
else:
    # handle undefined variable"""
            })
        
        elif error_type == 'TypeError':
            suggestions.append({
                'type': 'type_check',
                'description': 'Add type checking and conversion',
                'code': """# Check and convert types
if isinstance(value, str):
    value = int(value)  # or appropriate conversion
elif value is None:
    value = default_value"""
            })
        
        elif error_type == 'AttributeError':
            suggestions.append({
                'type': 'attribute_check',
                'description': 'Check attribute existence',
                'code': """# Check if attribute exists
if hasattr(obj, 'attribute_name'):
    result = obj.attribute_name
else:
    # handle missing attribute"""
            })
        
        elif error_type == 'IndexError':
            suggestions.append({
                'type': 'bounds_check',
                'description': 'Add bounds checking',
                'code': """# Check list bounds
if 0 <= index < len(my_list):
    value = my_list[index]
else:
    # handle out of bounds"""
            })
        
        elif error_type == 'KeyError':
            suggestions.append({
                'type': 'key_check',
                'description': 'Use safe dictionary access',
                'code': """# Safe dictionary access
value = my_dict.get('key', default_value)
# or
if 'key' in my_dict:
    value = my_dict['key']"""
            })
        
        return suggestions
    
    async def _generate_prevention_tips(self, error_info: Dict[str, Any]) -> List[str]:
        """Generate tips to prevent similar errors in the future."""
        tips = []
        error_type = error_info.get('error_type', '')
        
        general_tips = [
            "Use descriptive variable names to avoid typos",
            "Add type hints to function parameters and return values",
            "Write unit tests to catch errors early",
            "Use linting tools (pylint, flake8) to catch issues",
            "Add logging and error handling to your code"
        ]
        
        specific_tips = {
            'NameError': [
                "Initialize variables before use",
                "Use IDE with syntax highlighting and autocomplete",
                "Organize imports at the top of the file"
            ],
            'TypeError': [
                "Use type hints and type checking",
                "Validate input parameters",
                "Handle None values explicitly"
            ],
            'AttributeError': [
                "Use hasattr() to check attribute existence",
                "Initialize objects properly",
                "Use isinstance() to check object types"
            ],
            'IndexError': [
                "Always check list length before accessing",
                "Use enumerate() for index-safe iteration",
                "Consider using try-except for index access"
            ],
            'KeyError': [
                "Use dict.get() method with defaults",
                "Validate dictionary keys before access",
                "Use collections.defaultdict for automatic defaults"
            ]
        }
        
        tips.extend(specific_tips.get(error_type, []))
        tips.extend(general_tips)
        
        return tips[:8]  # Limit to 8 tips
    
    async def _detect_bugs_in_ast(self, tree: ast.AST, code: str, filename: str) -> List[Dict[str, Any]]:
        """Detect potential bugs by analyzing the AST."""
        bugs = []
        
        class BugDetector(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Check for functions that don't return anything but should
                if self._should_return_value(node) and not self._has_return_statement(node):
                    bugs.append({
                        'type': 'missing_return',
                        'severity': 'warning',
                        'line': node.lineno,
                        'message': f'Function "{node.name}" may be missing return statement',
                        'file': filename,
                        'suggestion': 'Add return statement or ensure function side effects are intended'
                    })
                
                self.generic_visit(node)
            
            def visit_Compare(self, node):
                # Check for potential equality vs assignment confusion
                if (len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq) and
                    isinstance(node.left, ast.Name)):
                    bugs.append({
                        'type': 'potential_assignment_confusion',
                        'severity': 'info',
                        'line': node.lineno,
                        'message': 'Equality comparison - ensure this is not intended assignment',
                        'file': filename,
                        'suggestion': 'Use = for assignment, == for comparison'
                    })
                
                self.generic_visit(node)
            
            def visit_List(self, node):
                # Check for empty list initialization that might cause issues
                if len(node.elts) == 0:
                    bugs.append({
                        'type': 'empty_list',
                        'severity': 'info',
                        'line': node.lineno,
                        'message': 'Empty list created - ensure this is intentional',
                        'file': filename,
                        'suggestion': 'Consider if empty list is appropriate here'
                    })
                
                self.generic_visit(node)
            
            def _should_return_value(self, node):
                """Check if function should return a value based on its name."""
                return_indicators = ['get', 'find', 'calculate', 'compute', 'create', 'build']
                return any(indicator in node.name.lower() for indicator in return_indicators)
            
            def _has_return_statement(self, node):
                """Check if function has a return statement."""
                for child in ast.walk(node):
                    if isinstance(child, ast.Return):
                        return True
                return False
        
        detector = BugDetector()
        detector.visit(tree)
        
        return bugs
    
    async def _detect_code_smells(self, tree: ast.AST, code: str, filename: str) -> List[Dict[str, Any]]:
        """Detect code smells that might indicate problems."""
        smells = []
        
        class SmellDetector(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Check for very long functions
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    func_length = node.end_lineno - node.lineno
                    if func_length > 50:
                        smells.append({
                            'type': 'long_function',
                            'severity': 'warning',
                            'line': node.lineno,
                            'message': f'Function "{node.name}" is very long ({func_length} lines)',
                            'file': filename,
                            'suggestion': 'Consider breaking into smaller functions'
                        })
                
                self.generic_visit(node)
            
            def visit_If(self, node):
                # Check for deeply nested if statements
                nested_depth = self._count_nested_depth(node)
                if nested_depth > 3:
                    smells.append({
                        'type': 'deep_nesting',
                        'severity': 'warning',
                        'line': node.lineno,
                        'message': f'Deep nesting detected (depth: {nested_depth})',
                        'file': filename,
                        'suggestion': 'Consider extracting nested logic or using early returns'
                    })
                
                self.generic_visit(node)
            
            def _count_nested_depth(self, node, depth=0):
                """Count the nesting depth of if statements."""
                max_depth = depth
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, ast.If):
                        child_depth = self._count_nested_depth(child, depth + 1)
                        max_depth = max(max_depth, child_depth)
                return max_depth
        
        detector = SmellDetector()
        detector.visit(tree)
        
        return smells
    
    async def _detect_logic_issues(self, tree: ast.AST, code: str, filename: str) -> List[Dict[str, Any]]:
        """Detect potential logic issues."""
        issues = []
        
        class LogicDetector(ast.NodeVisitor):
            def visit_Compare(self, node):
                # Check for always true/false conditions
                if (isinstance(node.left, ast.Constant) and 
                    len(node.comparators) == 1 and
                    isinstance(node.comparators[0], ast.Constant)):
                    
                    issues.append({
                        'type': 'constant_comparison',
                        'severity': 'warning',
                        'line': node.lineno,
                        'message': 'Comparison between constants detected',
                        'file': filename,
                        'suggestion': 'Review if this comparison is intended'
                    })
                
                self.generic_visit(node)
            
            def visit_While(self, node):
                # Check for potential infinite loops
                if (isinstance(node.test, ast.Constant) and node.test.value is True):
                    issues.append({
                        'type': 'potential_infinite_loop',
                        'severity': 'warning',
                        'line': node.lineno,
                        'message': 'Potential infinite loop (while True)',
                        'file': filename,
                        'suggestion': 'Ensure loop has proper exit condition'
                    })
                
                self.generic_visit(node)
        
        detector = LogicDetector()
        detector.visit(tree)
        
        return issues
    
    async def _generate_bug_fix_recommendations(
        self, 
        potential_bugs: List[Dict[str, Any]], 
        code_smells: List[Dict[str, Any]], 
        logic_issues: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations for fixing detected issues."""
        recommendations = []
        
        total_issues = len(potential_bugs) + len(code_smells) + len(logic_issues)
        
        if potential_bugs:
            recommendations.append(f"Address {len(potential_bugs)} potential bugs identified")
        
        if code_smells:
            recommendations.append(f"Refactor {len(code_smells)} code smells for better maintainability")
        
        if logic_issues:
            recommendations.append(f"Review {len(logic_issues)} potential logic issues")
        
        if total_issues == 0:
            recommendations.append("No obvious issues detected - code looks good!")
        
        recommendations.extend([
            "Add comprehensive unit tests",
            "Use static analysis tools regularly",
            "Implement code review process",
            "Add error handling and logging"
        ])
        
        return recommendations[:6]  # Limit to 6 recommendations
    
    async def _categorize_problem(self, description: str) -> str:
        """Categorize the problem based on description."""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['crash', 'error', 'exception', 'traceback']):
            return 'runtime_error'
        elif any(word in description_lower for word in ['slow', 'performance', 'timeout']):
            return 'performance_issue'
        elif any(word in description_lower for word in ['wrong', 'incorrect', 'unexpected']):
            return 'logic_error'
        elif any(word in description_lower for word in ['import', 'module', 'package']):
            return 'import_issue'
        else:
            return 'general_debugging'
    
    async def _suggest_debugging_approach(self, category: str) -> List[str]:
        """Suggest debugging approach based on problem category."""
        approaches = {
            'runtime_error': [
                "Read the full error traceback carefully",
                "Identify the exact line where error occurs",
                "Check variable values at the error point",
                "Add try-except blocks for error handling"
            ],
            'performance_issue': [
                "Profile the code to identify bottlenecks",
                "Check for inefficient algorithms or data structures",
                "Look for unnecessary repeated operations",
                "Monitor memory usage patterns"
            ],
            'logic_error': [
                "Add print statements to trace execution flow",
                "Verify input and output values",
                "Check conditional statements and loops",
                "Test with different input scenarios"
            ],
            'import_issue': [
                "Verify module installation",
                "Check Python path and virtual environment",
                "Ensure correct module names and spelling",
                "Check for circular imports"
            ],
            'general_debugging': [
                "Start with simple test cases",
                "Use systematic elimination approach",
                "Add logging to track program flow",
                "Break down complex problems into smaller parts"
            ]
        }
        
        return approaches.get(category, approaches['general_debugging'])
    
    async def _recommend_debugging_tools(self, category: str) -> List[str]:
        """Recommend debugging tools based on problem category."""
        tools = {
            'runtime_error': ['Python debugger (pdb)', 'IDE debugger', 'Traceback analysis'],
            'performance_issue': ['cProfile', 'memory_profiler', 'timeit', 'line_profiler'],
            'logic_error': ['Print statements', 'Logging', 'Unit tests', 'Assert statements'],
            'import_issue': ['pip list', 'sys.path inspection', 'Virtual environment tools'],
            'general_debugging': ['Print statements', 'Logging', 'Python debugger (pdb)', 'Unit tests']
        }
        
        return tools.get(category, tools['general_debugging'])
    
    async def _provide_common_solutions(self, category: str) -> List[str]:
        """Provide common solutions based on problem category."""
        solutions = {
            'runtime_error': [
                "Add proper error handling with try-except",
                "Validate input parameters",
                "Initialize variables before use",
                "Check for None values"
            ],
            'performance_issue': [
                "Use efficient data structures (sets, dicts)",
                "Avoid repeated calculations",
                "Use generators for large datasets",
                "Optimize database queries"
            ],
            'logic_error': [
                "Review conditional logic",
                "Check loop boundaries",
                "Verify calculation formulas",
                "Test edge cases"
            ],
            'import_issue': [
                "Install missing packages with pip",
                "Check virtual environment activation",
                "Verify Python path settings",
                "Fix circular import dependencies"
            ],
            'general_debugging': [
                "Write unit tests",
                "Use version control to track changes",
                "Document code behavior",
                "Follow coding best practices"
            ]
        }
        
        return solutions.get(category, solutions['general_debugging'])
    
    async def _suggest_next_steps(self, category: str) -> List[str]:
        """Suggest next steps for debugging."""
        next_steps = [
            "Implement the suggested debugging approach",
            "Test the proposed solutions systematically",
            "Document the issue and resolution for future reference",
            "Consider adding preventive measures (tests, error handling)",
            "Review similar code patterns for potential issues"
        ]
        
        return next_steps