import string
import copy

EXPRESSION_ID = 0


class LambdaExpression:
    def __init__(self, expression: str, id: str = "0", scope = {}):
        self.id = id
        self.scope = scope
        self.construct(expression, scope)
    
    def print_tree(self, offset = ""):
        self.child.print_tree(offset + ("| " if self.id != "0" else ""))
    
    def get_expression(self, indices = {}):
        return self.child.get_expression(indices)
    
    def construct(self, expression: str, scope):
        expression = LambdaExpression.remove_redundant_parentheses(expression.replace(' ', '').replace('L', 'λ'))
        if len(expression) == 1:
            self.child = VariableExpression(expression, self.id, scope)
        elif expression[0] == 'λ':
            self.child = DefinitionExpression(expression, self.id, scope)
        else:
            self.child = ApplicationExpression(expression, self.id, scope)
    
    def can_reduce(self):
        return False
    
    def find_reductions(self):
        return self.child.find_reductions()
    
    def apply_reduction(self, reduction_id):
        if reduction_id != self.id:
            self.child.apply_reduction(reduction_id)
            return
        if not isinstance(self.child, ApplicationExpression):
            raise(Exception("Can only reduce ApplicationExpressions"))
        if not self.child.can_reduce():
            raise(Exception("Attempted to reduce a non directly reducible ApplicationExpression"))
        self.child.left.child.initiate_replacement(self.child.right.child)
        self.child = self.child.left.child.lambda_expression.child
    
    def replace_with(self, symbol, scope, value_to_copy):
        if not isinstance(self.child, VariableExpression):
            self.child.replace_with(symbol, scope, value_to_copy)
            return
        if self.child.symbol != symbol:
            return
        if self.child.bounded_by != scope:
            return
        self.child = copy.deepcopy(value_to_copy)
    
    # STATIC METHODS
    
    def remove_redundant_parentheses(expression: str):
        if expression[0] != '(':
            return expression
        depth = 1
        for char in expression[1:-1]:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
                if depth == 0:
                    return expression
        if expression[-1] != ')':
            raise(ValueError(f'Mismatched outside parentheses in expression : "{expression}"'))
        return expression[1:-1]


class DefinitionExpression(LambdaExpression):
    def __init__(self, expression: str, id: str, scope):
        super().__init__(expression, id, scope)
    
    def print_tree(self, offset):
        print(offset + f"λ{self.variable}.    ({self.id})")
        self.lambda_expression.print_tree(offset)
    
    def get_expression(self, indices):
        if self.variable not in indices:
            indices[self.variable] = [self.id]
        elif self.id not in indices[self.variable]:
            indices[self.variable].append(self.id)
        return f"λ{self.variable}{indices[self.variable].index(self.id)}.{self.lambda_expression.get_expression(indices)}"

    def construct(self, expression: str, scope):
        if expression[0] != 'λ' or not VariableExpression.is_variable_character(expression[1]) or expression[2] != '.' or len(expression) <= 3:
            raise(ValueError(f'DefinitionExpression expected expression of the following format : "λx.<rest of expression>" (L can be used for λ), but got : "{expression}"'))
        self.variable = expression[1]
        scope[self.variable] = self.id
        self.lambda_expression = LambdaExpression(expression[3:], self.id + ".0", scope)
    
    def can_reduce_with(self, character: str):
        return self.variable == character
    
    def can_reduce(self):
        return super().can_reduce()
    
    def find_reductions(self):
        return self.lambda_expression.find_reductions()
    
    def apply_reduction(self, reduction_id):
        self.lambda_expression.apply_reduction(reduction_id)

    def initiate_replacement(self, value_to_copy):
        self.lambda_expression.replace_with(self.variable, self.id, value_to_copy)
    
    def replace_with(self, symbol, scope, value_to_copy):
        self.lambda_expression.replace_with(symbol, scope, value_to_copy)


class ApplicationExpression(LambdaExpression):
    def __init__(self, expression: str, id: str, scope):
        super().__init__(expression, id, scope)
    
    def print_tree(self, offset):
        print(offset + f"app    ({self.id})")
        self.left.print_tree(offset)
        print(offset + "to")
        self.right.print_tree(offset)

    def get_expression(self, indices):
        function_str = self.left.get_expression(indices)
        if isinstance(self.left.child, DefinitionExpression):
            function_str = f"({function_str})"

        value_str = self.right.get_expression(indices)
        if isinstance(self.right.child, (DefinitionExpression, ApplicationExpression)):
            value_str = f"({value_str})"

        return function_str + " " + value_str
    
    def construct(self, expression: str, scope):
        value = ApplicationExpression.get_last_element(expression)
        func = expression[:-len(value)]

        self.left = LambdaExpression(func, self.id + ".0", scope)
        self.right = LambdaExpression(value, self.id + ".1", scope)
    
    def can_reduce(self):
        return isinstance(self.left.child, DefinitionExpression)
    
    def find_reductions(self):
        result = self.left.find_reductions() + self.right.find_reductions()
        if self.can_reduce():
            result.append(self.id)
        return result

    def apply_reduction(self, reduction_id):
        self.left.apply_reduction(reduction_id)
        self.right.apply_reduction(reduction_id)
    
    def replace_with(self, symbol, scope, value_to_copy):
        self.left.replace_with(symbol, scope, value_to_copy)
        self.right.replace_with(symbol, scope, value_to_copy)
    
    # STATIC METHODS

    def get_last_element(expression: str):
        last_element = expression[-1]
        if last_element == ")":
            depth = 1
            while depth > 0:
                last_element = expression[-len(last_element) - 1] + last_element
                if last_element[0] == '(':
                    depth -= 1
                elif last_element[0] == ')':
                    depth += 1
        else:
            while expression[-len(last_element) - 1] != ")":
                last_element = expression[-len(last_element) - 1] + last_element
                if (len(last_element) == len(expression)):
                    return expression[-1]
        return last_element


class VariableExpression(LambdaExpression):
    def __init__(self, expression: str, id: str, scope):
        super().__init__(expression, id, scope)
    
    def print_tree(self, offset):
        print(offset + self.symbol + "    bb " + self.bounded_by)
    
    def get_expression(self, indices):
        return self.symbol + (str(indices[self.symbol].index(self.bounded_by)) if self.symbol in indices else "")
    
    def construct(self, expression: str, scope):
        if len(expression) != 1:
            raise(ValueError(f'VariableExpression cannot be constructed with multi-character expression : "{expression}", please use single character.'))
        self.symbol = expression
        self.bounded_by = scope[self.symbol]
    
    def can_reduce(self):
        return super().can_reduce()
    
    def find_reductions(self):
        return []
    
    def apply_reduction(self, reduction_id):
        return
    
    # STATIC METHODS

    def is_variable_character(character: str):
        return character in string.ascii_letters