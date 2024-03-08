from __future__ import annotations
from collections import defaultdict
import random
import string

DIGITS = '1234567890'

class Stack:
    def __init__(self) -> None:
        self.items = []

    def push(self, value = None):
        value = value or "Value"
        self.items.append(value)

    def pop(self):
        return self.items.pop()
    
    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0

class Lexer:
    @classmethod
    def lex(cls, expression: str) -> list[Term | Expression] | Term | Expression:
        tokens = []
        tt = ''
        skip = 0

        for i, character in enumerate(expression):
            if skip:
                skip -= 1
                continue

            if character == ' ':
                continue

            if character == '(':
                skip, tok = Lexer.sublex(expression=expression[i+1:])
                tokens.append(tok)
                continue
    
            if (character in Operation.OPERATORS or 
                (tt != '' and tt[-1] in DIGITS and character not in DIGITS)):
                if tt:
                    tokens.append(Term(tt, int(tt)))
                    if character not in Operation.OPERATORS:
                        tokens.append(Operation('*'))

                if character in Operation.OPERATORS:
                    tokens.append(Operation(character))
                else:
                    tokens.append(Term(character, var_expo={character: 1}))

                tt = ''
                continue
            
            if character in DIGITS:
                tt += character
            else:
                if expression[i-1] not in Operation.OPERATORS:
                    tokens.append(Operation('*'))
                tokens.append(Term(character, var_expo={character: 1}))

        if tt:
            tokens.append(Term(tt, int(tt)))

        return tokens


    @classmethod
    def sublex(cls, expression: str, until: str = None) -> tuple[int, list[Term | Expression] | Term | Expression]:
        """
        Lexes a smaller sub-portion of out expression

        :param expression: The expression to lex
        :param until: The character at which we stop lexing
        :returns: The number of characters to skip, and the tokens
        """
        until = until or ')'

        tokens = []
        skip = 0
        ret_skip = 0
        tt = ''

        for i, character in enumerate(expression):
            ret_skip += 1
            if skip:
                skip -= 1
                continue

            if character == ' ':
                continue

            if character == until:
                if tt:
                    tokens.append(Term(tt, int(tt)))
                return ret_skip, tokens

            if character == '(':
                skip, tok = Lexer.sublex(expression=expression[i+1:])
                tokens.append(tok)
                continue
    
            if (character in Operation.OPERATORS or 
                (tt != '' and tt[-1] in DIGITS and character not in DIGITS)):
                if tt:
                    tokens.append(Term(tt, int(tt)))
                    tokens.append(Operation('*'))

                if character in Operation.OPERATORS:
                    tokens.append(Operation(character))
                else:
                    tokens.append(Term(character, var_expo={character: 1}))

                tt = ''
                continue
            
            if character in DIGITS+'.':
                tt += character
            else:
                tokens.append(Term(character, var_expo={character: 1}))

class Operation:
    OPERATORS = '+-*/^'

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol

        self.parent: Expression = None
        self.belonging = None

    def __repr__(self) -> str:
        return self.symbol
    
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, str):
            return self.symbol == __value
        
        if not isinstance(__value, Operation):
            return False
        
        return self.symbol == __value.symbol
    
    def transposed(self):
        if self.symbol == '+': new = '-'
        if self.symbol == '-': new = '+'
        if self.symbol == '*': new = '/'
        if self.symbol == '/': new = '*'
        return Operation(new)

class Term:
    def __init__(self, character: str, coefficient: float = 1, var_expo: dict[str, int] = None) -> None:
        self.character = character
        self.coefficient = coefficient
        self.var_expo = var_expo or {}

        self.parent = None
        self.belonging = None

    def __repr__(self) -> str:
        if not self.var_expo:
            return str(self.coefficient)
        if len(self.var_expo) == 1:
            key = list(self.var_expo.keys())[0]
            front = [str(self.coefficient), ''][self.coefficient == 1]

            if self.var_expo[key] == 1:
                return f"{front}{key}"
            else:
                return f"{front}{key}^{self.var_expo[key]}"
        else:
            construction = ''
            if self.coefficient != 1:
                construction = str(self.coefficient)
            for k, v in self.var_expo.items():
                if v == 1:
                    construction += f'({k})'
                else:
                    construction += f"({k}^{v})"
            return construction

    @property
    def has_variable(self) -> bool:
        return bool(self.var_expo)
    
    def __add__(self, other):
        if isinstance(other, (int, float)):
            return Expression.from_terms([self, Operation('+'), Expression(str(other))])
        return Expression.from_terms([self, Operation('+'), other])

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            new = self
            new.coefficient *= other
            return new
        
        new_coeff = other.coefficient * self.coefficient
        new_var_expo = defaultdict(lambda: 0)
        new_var_expo.update(self.var_expo)
        for k, v in other.var_expo.items():
            new_var_expo[k] += v

        return Term('XXX', new_coeff, new_var_expo)
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Term):
            return False

        return all([
            self.character == value.character,
            self.coefficient == value.coefficient,
            self.var_expo == value.var_expo,
            self.parent == value.parent,
            self.belonging == value.belonging
        ])
    
    def transpose(self):
        if not isinstance(self.parent.parent, Equation):
            return ValueError("Cannot transpose right now.")

        new = []

        self_idx = self.parent.terms.index(self)            
        for i, term in enumerate(self.parent.terms):
            if not (i == self_idx or i == self_idx - 1):
                new.append(term)

        if self.parent.identity == 0:
            self.parent.parent.rhs.terms.append(self.parent.terms[self_idx-1].transposed())
            self.parent.parent.rhs.terms.append(self)
        else:
            self.parent.parent.lhs.terms.append(self.parent.terms[self_idx-1].transposed())
            self.parent.parent.lhs.terms.append(self)
        self.parent.terms = new        

class Expression:
    def __init__(self, expression: str) -> None:
        self.terms = Lexer.lex(expression)
        self.id = "".join(random.choices(string.ascii_letters, k=5))
        self.parent = None

        self.identity = None

    def __eq__(self, __value: object) -> bool:
        return self.id == __value.id

    @classmethod
    def from_terms(cls, terms: list[Term | Expression]) -> Expression:
        obj = cls('')
        obj.terms = terms
        return obj
    
    def __getitem__(self, idx: int):
        if not isinstance(idx, int):
            return ValueError(f"Expecting idx to be of type int, got {idx=} of {type(idx)}")
        
        return self.terms[idx]
    
    def __len__(self):
        return len(self.terms)
    
    def adopt(self):
        for term in self.terms:
            if isinstance(term, Expression):
                term.adopt()
                term.parent = self
            else:
                term.parent = self

        return self
    
    def flatten(self):
        new_expr = []
        for i, term in enumerate(self.terms):
            if isinstance(term, Expression):
                term.flatten()
            
            if isinstance(term, Term) and term.has_variable:
                construction = term
                if i >= 2:
                    has_cofficient = self.terms[i-1] == '*'
                    if has_cofficient:
                        coeff = self.terms[i-2]
                        if not coeff.belonging:
                            coeff.belonging = term
                            self.terms[i-1].belonging = term
                            construction.coefficient = coeff
                        else:
                            coeff.belonging.var_expo.update(term.var_expo)
                            coeff.belonging.coefficient *= term.coefficient
                            term.belonging = coeff
                            self.terms[i-1].belonging = coeff

                if i+2 <= len(self.terms)-1:
                    has_expo = self.terms[i+1] == '^'
                    if has_expo:
                        expo = self.terms[i+2]
                        expo.belonging = term
                        self.terms[i+1].belonging = term
                        construction.var_expo[term.character] = expo
                
                new_expr.append(construction)
            else:
                new_expr.append(term)

        filtered = [term for term in new_expr if not term.belonging]
        self.terms = filtered
        self.multiply_out()
    
    def multiply_out(self):
        new = []
        for i, term in enumerate(self.terms):
            if isinstance(term, Operation) and term == '*':
                left = self.terms[i-1]
                right = self.terms[i+1]

                left.belonging = right.belonging = term
                new.append(left * right)
            else:
                new.append(term)
        
        filtered = [term for term in new if not term.belonging]
        self.terms = filtered

    def __repr__(self) -> str:
        text = ''
        for term in self.terms:
            text += str(term)
            text += ' '
        return text.strip()

class Equation:
    def __init__(self, lhs: Expression, rhs: Expression) -> None:
        self.lhs = lhs
        self.rhs = rhs

    @classmethod
    def parse(cls, equation: str) -> Equation:
        lhs_expr, rhs_expr = equation.split('=')
        lhs_expr = lhs_expr.strip()
        rhs_expr = rhs_expr.strip()

        lhs = Expression(expression=lhs_expr)
        rhs = Expression(expression=rhs_expr)

        equ = cls(lhs=lhs, rhs=rhs)

        return equ
    
    def __repr__(self) -> str:
        return f'{self.lhs} = {self.rhs}'
    
    def adopt(self, *, side: int = 2) -> Equation:
        """
        Goes to every expression/term in the side and assigns its parent

        :param side: The side on which to perform the adoption. 2 means both, 1 means RHS, and 0 means LHS
        :returns: The new equation
        """
        if side in (0, 2):
            self.lhs.adopt()
        if side in (1, 2):
            self.rhs.adopt()
        self.lhs.parent = self.rhs.parent = self
        self.lhs.identity = 0
        self.rhs.identity = 1
        return self
    
    def flatten(self, *, side: int = 2) -> Equation:
        """
        Assigns variables coefficients and exponents
        """
        if side in (0, 2):
            self.lhs.flatten()
        if side in (1, 2):
            self.rhs.flatten()
        return self

equation = '3xy^2 + 3yx^z + 9912yxz + 2 = 82'
equ = Equation.parse(equation=equation).adopt().flatten()
t = equ.lhs[-1]
t.transpose()
print(equ)

