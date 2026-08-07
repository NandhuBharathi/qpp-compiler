"""Q++ AST nodes."""

from dataclasses import dataclass, field


class Node:
    pass


class Statement(Node):
    pass


class Expression(Node):
    pass


@dataclass
class Program(Node):
    statements: list[Statement] = field(default_factory=list)


@dataclass
class Identifier(Expression):
    name: str


@dataclass
class Integer(Expression):
    value: int


@dataclass
class Float(Expression):
    value: float


@dataclass
class String(Expression):
    value: str


@dataclass
class Boolean(Expression):
    value: bool


@dataclass
class Binary(Expression):
    left: Expression
    operator: str
    right: Expression


@dataclass
class Unary(Expression):
    operator: str
    operand: Expression


@dataclass
class Assign(Statement):
    name: str
    value: Expression


@dataclass
class Print(Statement):
    value: Expression


@dataclass
class Return(Statement):
    value: Expression | None = None


@dataclass
class If(Statement):
    condition: Expression
    body: list[Statement]
    else_body: list[Statement] = field(default_factory=list)


@dataclass
class While(Statement):
    condition: Expression
    body: list[Statement]


@dataclass
class Function(Statement):
    name: str
    parameters: list[str]
    body: list[Statement]


@dataclass
class Class(Statement):
    name: str
    body: list[Statement]


@dataclass
class Import(Statement):
    module: str


@dataclass
class Call(Expression):
    name: str
    arguments: list[Expression]


@dataclass
class BinaryOp:
    left: object
    operator: str
    right: object
