"""
Cycle module
This module provides a Cycle class for representing and manipulating permutations
written as disjoint cycles. A Cycle object encapsulates a mapping from integer
elements to their images under the permutation and a dimension that indicates the
largest element considered in the permutation.
Usage summary:
- Create a Cycle from a cycle-string: Cycle.Cycle("(1, 4, 3, 2)") returns a Cycle
    representing that permutation.
- Compose permutations with * : (a * b)(x) = a(b(x)). Composition is associative
    but not commutative.
- Invert a permutation with .inverse().
- Call a Cycle on an integer to get its image: cycle(3).
- String/representation methods produce a human-readable disjoint-cycle form.
Public API:
- Cycle.Cycle(string: str) -> Cycle
        Parse a string of one or more parenthesized cycles (e.g. "(6, 4)(2, 3, 1)(5)")
        into a Cycle instance. The parser expects cycles separated by adjacent
        parentheses and integers separated by commas. Singletons (fixed points) are
        handled but internal mapping removes explicit fixed-point entries.
- Cycle.generate_single_cycle(cycle: list[int]) -> Cycle
        Build a Cycle from a single cycle given as a list of integers (e.g. [2,3,1]).
        The returned Cycle maps each element to the next element in the list and
        uses the maximum element as the permutation dimension.
- Cycle.inverse(self) -> Cycle
        Return the inverse permutation by swapping keys and values of the internal
        mapping. The result keeps the same dimension.
- Cycle.__call__(self, value: int) -> int
        Apply the permutation to a single element. If the element is not present in
        the internal mapping it is treated as a fixed point and returned unchanged.
- Cycle.__mul__(self, other: Cycle) -> Cycle
        Return the composition self ∘ other (apply other first, then self). The
        resulting Cycle has dimension equal to the maximum of the two operands'
        dimensions. Elements not explicitly mapped by either operand are treated as
        fixed points.
- Cycle.__repr__/__str__(self) -> str
        Produce a string of the disjoint-cycle decomposition covering elements from
        1 up to the permutation's dimension. Fixed points are omitted from the
        printed cycles; if there are no nontrivial cycles a canonical representation
        is returned (e.g. "(1)").
Implementation notes and invariants:
- The internal mapping is a dict[int, int] that stores only nontrivial images
    (entries where mapping[x] != x). The dimension is stored separately and
    determines the universe of elements considered when printing or composing.
- Parsing via Cycle.Cycle expects well-formed input; whitespace tolerances are
    limited to the basic comma-separated integer tokens within parentheses.
- Composition semantics follow functional composition: (a * b)(x) == a(b(x)).
Examples:
- Cycle.Cycle("(1, 4, 3, 2)")(1) -> 4
- Cycle.Cycle("(1, 4, 3, 2)") * Cycle.Cycle("(1, 2)")  # apply (1 2) then (1 4 3 2)
- Cycle.generate_single_cycle([2, 3, 1]).inverse()
This docstring documents the public behavior of the Cycle class and its
convenience constructors. Refer to method docstrings for more granular details.
"""

from typing import Optional




class Cycle:
    def __init__(self, mapping:Optional[dict[int,int]]=None, dimension:int=0):
        if mapping is None:
            self._map = {}
        else:
            keys = list(mapping.keys())
            for key in keys:
                if mapping[key] == key:
                    mapping.pop(key)
            self._map = dict(mapping)
        self._dim = dimension
        
    @staticmethod
    def Cycle(string:str):
        # string is in the form (6, 4)(2, 3, 1)(5) for example
        bracketed = string[1:-1].split(")(")
        # print("bracketed")
        # print(bracketed)
        
        cycles = []
        for cycle in bracketed:
            tokens = [x.strip() for x in cycle.split(",") if x.strip() != ""]
            if tokens:
                cycles.append([int(x) for x in tokens])
                # if no tokens found, then its an empty cycle so is the identity
        
        # print("cycles")
        # print(cycles)
        if not cycles:
            return Cycle()

        cycles[-1] = Cycle.generate_single_cycle(cycles[-1])
        while len(cycles) > 1:
            # print("cycle")
            # print(cycles[-2], "*", cycles[-1])
            last = cycles.pop()
            second = Cycle.generate_single_cycle(cycles.pop())
            # print(second, "*", last)
            # print(second * last)
            cycles.append(second * last)
        
        return cycles[0]

    @staticmethod
    def generate_single_cycle(cycle:list[int]):
        seq = list(cycle)
        dim = max(seq)
        mapping = {}
        seq.append(seq[0])
        while len(seq) >= 2:
            current = seq.pop(0)
            mapping[current] = seq[0]
        return Cycle(mapping=mapping, dimension=dim)
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def __call__(self, value:int):
        if not isinstance(value, int):
            raise ValueError(f"Can only send integer value, not {value}")
        if value not in self._map.keys():
            return value
        return self._map[value]
        
    def __mul__(self, cycle: "Cycle")-> "Cycle":
        """product of cycles are associative"""
        dim = max(self.get_dimension(), cycle.get_dimension())
        
        to_check = [x for x in range(1, dim+1)]
        
        new_cycle = {}
        
        while to_check:
            current = to_check.pop(0)
            new_cycle[current] = self(cycle(current))

        return Cycle(mapping=new_cycle, dimension=dim)
    
    def _create_representation(self)->list[list[int]]:
        to_check = list(range(1, self.get_dimension()+1))
        
        cycles = []
        
        while to_check:
            looping = True
            cycle = []
            current = to_check[0]
            while looping:
                to_check.remove(current)
                cycle.append(current)
                nxt = self(current)
                if nxt in cycle:
                    looping = False
                    if len(cycle) > 1:
                        cycles.append(cycle)
                else:
                    current = nxt
                    
        return cycles
    
    def _prettify(self, representation:list[list[int]])->str:
        stringified = [[str(x) for x in cycle] for cycle in representation]
        inner_join = [", ".join(cycle) for cycle in stringified]
        result = "(" + (")(".join(inner_join)) + ")"
        if result == "()":
            result = "(1)"
        return result
    
    def __repr__(self):
        cycles = self._create_representation()
        return self._prettify(cycles)
            
    def get_dimension(self):
        return self._dim
    
    def decompose(self) -> str:
        """returns the decomposed form of the cycle as a string"""
        cycles = self._create_representation()
        
        representation = []
        for cycle in cycles:
            representation += [[cycle[0], cycle[i]] for i in range(len(cycle)-1, 0, -1)]
        
        return self._prettify(representation)
    
    def inverse(self):
        new_mapping = {value:key for key, value in self._map.items()}
        return Cycle(mapping=new_mapping, dimension=self.get_dimension())
    
    
a = Cycle.Cycle("(1, 2, 3, 4)")
print(a)
print(a.decompose())

print(a(4))