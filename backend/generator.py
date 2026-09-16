import random

FUNDAMENTALS = [
    'assets', 'cash', 'liabilities', 'sales', 'income',
    'debt', 'ebit', 'ebitda', 'eps', 'revenue', 'returns', 'close'
]
OPERATORS = ['+', '-', '*', '/']

def generate_expression():
    """
    Generates fully valid Python code as multi-line strings for Python Alphas.
    """
    num_ops = random.randint(1, 5)
    # Pick random fields for this alpha
    fields = random.sample(FUNDAMENTALS, k=num_ops + 1)
    
    # Build a random math expression on the numpy arrays
    expr_parts = []
    for i, field in enumerate(fields):
        if i == 0:
            expr_parts.append(f"data.{field}[-1]")
        else:
            op = random.choice(OPERATORS)
            expr_parts.append(f" {op} data.{field}[-1]")
            
    math_expr = "".join(expr_parts)
    fields_list = ', '.join([f'"{f}"' for f in set(fields)])
    
    code = f"""from brain.alphas import alpha
import numpy as np
import numpy.typing as npt

@alpha(data=[{fields_list}], store=[])
def generated_alpha(data, store) -> npt.NDArray[np.float32]:
    # We use numpy arrays directly. data.field[-1] gets the most recent cross-section.
    signal = {math_expr}
    
    # Handle NaNs and infs safely
    signal = np.nan_to_num(signal, nan=0.0, posinf=0.0, neginf=0.0)
    
    # Cross-sectional neutralization
    signal = signal - np.mean(signal)
    
    return (-signal).astype(np.float32)
"""
    return code

if __name__ == '__main__':
    print(generate_expression())
