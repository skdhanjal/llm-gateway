
from gateway.routes_cfg import Truncation
from gateway.token_math import get_encoding

OMISSION_MARK = "\n[… {n} tokens omitted …]\n"

class BudgetExceeded(Exception):
    def __init__(self, have: int, budget: int):
        self.have = have
        self.budget = budget

def enforce_budget(text: str, budget: int, strategy: Truncation,
                   model: str) -> tuple[str, int]:
    """Return (possibly-truncated text, tokens_dropped).
    Token-wise, never character-wise; always leaves an explicit marker."""
    enc = get_encoding(model)
    ids = enc.encode(text)
    if len(ids) <= budget:
        return text, 0
    
    if strategy == Truncation.REJECT:
        raise BudgetExceeded(len(ids), budget)

    dropped = len(ids) - budget
    mark = OMISSION_MARK.format(n=dropped)
    mark_cost = len(enc.encode(mark))
    keep = budget - mark_cost                    # the marker pays rent too

    if strategy == Truncation.TAIL_DROP:
        kept = enc.decode(ids[:keep]) + mark
    elif strategy == Truncation.HEAD_DROP:
        kept = mark + enc.decode(ids[-keep:])
    else:  # MIDDLE_DROP — split the keep budget across both ends
        head, tail = keep // 2, keep - keep // 2
        kept = enc.decode(ids[:head]) + mark + enc.decode(ids[-tail:])
    return kept, dropped