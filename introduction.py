from dataclasses import dataclass

@dataclass
class A:
    x: int

@dataclass
class B:
    y: str

a = B("hej")

match a:
    case A:
        print("hi")
    case B:
        print("bye")
