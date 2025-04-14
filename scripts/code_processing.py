import ast
import re
import radon.complexity as radon_cc
from radon.metrics import h_visit

class CodeFeatureExtractor:
    
    def __init__(self, name, node_type, file_path, code_snippet):
        self.name = name            # Function or class name
        self.node_type = node_type  # "function" or "class"
        self.file_path = file_path
        self.code_snippet = code_snippet

        # ========== Repository Metadata ========== 
        self.repo_name = None
        self.repo_stars = None
        self.repo_forks = None
        self.repo_watchers = None
        self.repo_language = None
        self.repo_created_at = None
        self.repo_last_updated = None
        self.repo_topics = None  # Optional list or string

        # ========== Size & Structure Features ==========
        self.loc = None       # Lines of Code
        self.num_args = None  # Number of arguments (only for functions)
        self.num_returns = None
        self.num_variables = None
        self.num_function_calls = None
        self.has_decorators = None
        self.uses_globals = None
        self.is_recursive = None

        # ========== Estimated attributes from radon ==========
        self.estimated_branches = None
        self.estimated_difficulty = None
        self.estimated_bugs = None

        # ========== Documentation & Comments ==========
        self.has_docstring = None
        self.docstring_length = None
        self.num_comments = None

        # ========== Naming Quality ==========
        self.name_length = len(name)
        self.is_name_well_formed = None
        self.bad_variable_names_count = None

        # ========== Return-Specific ==========
        self.max_return_length = None

        # ========== Target Label ==========
        self.quality = None


    def set_features(self, node):

        # Size & Structure
        self.extract_loc(node)
        self.extract_num_args(node)
        self.extract_num_returns(node)
        self.extract_num_variables(node)
        self.extract_num_function_calls(node)
        self.extract_has_decorators(node)
        self.extract_uses_globals(node)
        self.extract_is_recursive(node)

        # Estimated via radon
        self.extract_complexity()
        self.extract_radon_metrics()

        # Documentation & Comments
        self.extract_docstring_info(node)
        self.extract_num_comments()

        # Naming Quality
        self.extract_name_quality()
        self.extract_bad_variable_names_count(node)

        # Return-Specific
        self.extract_max_return_length(node)

    def print_features(self):
        print("\n Code Feature Summary")
        print("=" * 40)
        print(f"Name: {self.name}")
        print(f"Type: {self.node_type}")
        print(f"File: {self.file_path}")
        print("\n Size & Structure")
        print(f"  LOC: {self.loc}")
        print(f"  Arguments: {self.num_args}")
        print(f"  Returns: {self.num_returns}")
        print(f"  Variables: {self.num_variables}")
        print(f"  Function Calls: {self.num_function_calls}")
        print(f"  Has Decorators: {self.has_decorators}")
        print(f"  Uses Globals: {self.uses_globals}")
        print(f"  Is Recursive: {self.is_recursive}")

        print("\n Estimated (Radon)")
        print(f"  Branching Complexity: {self.estimated_complexity}")
        print(f"  Difficulty: {self.estimated_difficulty}")
        print(f"  Estimated Bugs: {self.estimated_bugs}")

        print("\n Documentation & Comments")
        print(f"  Has Docstring: {self.has_docstring}")
        print(f"  Docstring Length: {self.docstring_length}")
        print(f"  # Comments: {self.num_comments}")

        print("\n Naming Quality")
        print(f"  Name Length: {self.name_length}")
        print(f"  Name Well-Formed: {self.is_name_well_formed}")
        print(f"  Bad Variable Names Count: {self.bad_variable_names_count}")

        print("\n Return")
        print(f"  Max Return Length: {self.max_return_length}")

        print("\n Repository Metadata")
        print(f"  Repo Name: {self.repo_name}")
        print(f"  Stars: {self.repo_stars}")
        print(f"  Forks: {self.repo_forks}")
        print(f"  Watchers: {self.repo_watchers}")
        print(f"  Language: {self.repo_language}")
        print(f"  Created At: {self.repo_created_at}")
        print(f"  Last Updated: {self.repo_last_updated}")
        print(f"  Topics: {self.repo_topics}")
        print("=" * 40)


    def extract_loc(self, node):
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            self.loc = node.end_lineno - node.lineno + 1
        else:
            self.loc = len(self.code_snippet.strip().splitlines())

    def extract_num_args(self, node):
        if isinstance(node, ast.FunctionDef):
            self.num_args = len(node.args.args)
        else:
            self.num_args = None

    def extract_num_returns(self, node):
        self.num_returns = sum(isinstance(n, ast.Return) for n in ast.walk(node))

    def extract_num_variables(self, node):
        self.num_variables = sum(isinstance(n, ast.Assign) for n in ast.walk(node))

    def extract_num_function_calls(self, node):
        self.num_function_calls = sum(isinstance(n, ast.Call) for n in ast.walk(node))

    def extract_complexity(self):
        try:
            blocks = list(radon_cc.cc_visit(self.code_snippet))
            self.estimated_complexity = blocks[0].complexity if blocks else 0
        except Exception:
            self.estimated_complexity = -1  # use -1 as an error flag if parsing fails

    def extract_radon_metrics(self):
        try:
            result = h_visit(self.code_snippet)
            self.estimated_difficulty = result.total.difficulty
            self.estimated_bugs = result.total.bugs
        except Exception:
            self.estimated_difficulty = -1
            self.estimated_bugs = -1

    def extract_has_decorators(self, node):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
            self.has_decorators = len(node.decorator_list) > 0
        else:
            self.has_decorators = False

    def extract_uses_globals(self, node):
        self.uses_globals = any(isinstance(n, ast.Global) for n in ast.walk(node))

    def extract_is_recursive(self, node):
        self.is_recursive = False
        if isinstance(node, ast.FunctionDef):
            for n in ast.walk(node):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                    if n.func.id == node.name:
                        self.is_recursive = True
                        break
    
    def extract_docstring_info(self, node):
        docstring = ast.get_docstring(node)
        if docstring:
            self.has_docstring = True
            self.docstring_length = len(docstring.strip().splitlines())
        else:
            self.has_docstring = False
            self.docstring_length = 0

    def extract_num_comments(self):
        self.num_comments = sum(1 for line in self.code_snippet.splitlines() if line.strip().startswith("#"))

    def extract_name_quality(self):
        if self.node_type == "function":
            # snake_case
            pattern = r'^[a-z_][a-z0-9_]*$'
        elif self.node_type == "class":
            # CamelCase
            pattern = r'^[A-Z][a-zA-Z0-9]*$'
        else:
            self.is_name_well_formed = False
            return

        self.is_name_well_formed = bool(re.fullmatch(pattern, self.name))

    def extract_bad_variable_names_count(self, node):
        bad_names = {"x", "y", "z", "tmp", "var", "foo", "bar"}
        count = 0

        for subnode in ast.walk(node):
            if isinstance(subnode, ast.Name) and isinstance(subnode.ctx, ast.Store):
                name = subnode.id
                if len(name) <= 2 or name.lower() in bad_names:
                    count += 1

        self.bad_variable_names_count = count
    
    def extract_max_return_length(self, node):
        self.max_return_length = 0
        for subnode in ast.walk(node):
            if isinstance(subnode, ast.Return) and subnode.value is not None:
                try:
                    return_code = ast.unparse(subnode.value)  # Python 3.9+
                    length = len(return_code)
                    self.max_return_length = max(self.max_return_length, length)
                except Exception:
                    continue
