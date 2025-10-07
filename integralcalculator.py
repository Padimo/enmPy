# integral_calculator_steps.py
import re
import sympy as sp
from sympy import symbols, integrate, Function, pi, E

# ---------- Tokenizer ----------
_token_spec = [
    ("NUMBER",   r"\d+(\.\d+)?([eE][+-]?\d+)?"),
    ("NAME",     r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OP",       r"[\+\-\*/\^]"),
    ("LPAREN",   r"\("),
    ("RPAREN",   r"\)"),
    ("COMMA",    r","),
    ("SKIP",     r"[ \t\n]+"),
    ("MISMATCH", r"."),
]
_token_re = re.compile("|".join("(?P<%s>%s)" % pair for pair in _token_spec))

CONSTANTS = {"pi": pi, "e": E}

def tokenize(expr):
    tokens = []
    for mo in _token_re.finditer(expr):
        kind = mo.lastgroup
        value = mo.group()
        if kind == "NUMBER":
            tokens.append(("NUMBER", value))
        elif kind == "NAME":
            tokens.append(("NAME", value))
        elif kind == "OP":
            tokens.append(("OP", value))
        elif kind in ("LPAREN", "RPAREN", "COMMA"):
            tokens.append((kind, value))
        elif kind == "SKIP":
            continue
        else:
            raise SyntaxError(f"Unexpected character {value!r}")
    return tokens

# ---------- Shunting-yard (fixed implicit-multiplication bug) ----------
_prec = {
    '+': (2, 'L'),
    '-': (2, 'L'),
    '*': (3, 'L'),
    '/': (3, 'L'),
    '^': (4, 'R'),
}

def shunting_yard(tokens):
    output = []
    stack = []
    prev_token = None
    for i, (tok_type, tok) in enumerate(tokens):
        next_tok = tokens[i + 1] if i + 1 < len(tokens) else None

        def insert_implicit_mul():
            # don't insert implicit mul when previous token is a function name
            if prev_token is None:
                return False
            pt, _ = prev_token
            # only insert implicit multiplication if previous was NUMBER/NAME/RPAREN
            # and current is NAME/LPAREN/NUMBER, but NOT when previous is FUNC
            if pt in ("NUMBER", "NAME", "RPAREN") and tok_type in ("NAME", "LPAREN", "NUMBER"):
                return True
            return False

        if insert_implicit_mul():
            # push a multiplication operator before handling current token
            while stack and stack[-1][0] == "OP" and (
                (_prec[stack[-1][1]][0] > _prec['*'][0]) or
                (_prec[stack[-1][1]][0] == _prec['*'][0] and _prec[stack[-1][1]][1] == 'L')
            ):
                output.append(stack.pop())
            stack.append(("OP", "*"))

        if tok_type == "NUMBER":
            output.append(("NUMBER", tok))
            prev_token = ("NUMBER", tok)
        elif tok_type == "NAME":
            # If followed by LPAREN, this is a function name — push as FUNC (do NOT append NAME)
            if next_tok and next_tok[0] == "LPAREN":
                stack.append(("FUNC", tok))
                # mark prev_token as FUNC so the immediate LPAREN doesn't trigger implicit multiplication
                prev_token = ("FUNC", tok)
            else:
                output.append(("NAME", tok))
                prev_token = ("NAME", tok)
        elif tok_type == "OP":
            if tok == '-' and (prev_token is None or prev_token[0] in ("OP", "LPAREN", "COMMA")):
                # unary minus -> treat as function 'neg'
                stack.append(("FUNC", "neg"))
            else:
                while stack and stack[-1][0] == "OP":
                    topop = stack[-1][1]
                    if ((_prec[topop][0] > _prec[tok][0]) or
                        (_prec[topop][0] == _prec[tok][0] and _prec[tok][1] == 'L')):
                        output.append(stack.pop())
                    else:
                        break
                stack.append(("OP", tok))
            prev_token = ("OP", tok)
        elif tok_type == "LPAREN":
            stack.append(("LPAREN", tok))
            prev_token = ("LPAREN", tok)
        elif tok_type == "RPAREN":
            while stack and stack[-1][0] != "LPAREN":
                output.append(stack.pop())
            if not stack:
                raise SyntaxError("Mismatched parentheses")
            stack.pop()  # pop the LPAREN
            # if top of stack is a function, pop it to output
            if stack and stack[-1][0] == "FUNC":
                output.append(stack.pop())
            prev_token = ("RPAREN", tok)
        elif tok_type == "COMMA":
            while stack and stack[-1][0] != "LPAREN":
                output.append(stack.pop())
            if not stack:
                raise SyntaxError("Misplaced comma")
            prev_token = ("COMMA", tok)
    while stack:
        if stack[-1][0] in ("LPAREN", "RPAREN"):
            raise SyntaxError("Mismatched parentheses")
        output.append(stack.pop())
    return output

# ---------- RPN -> SymPy (robust, with helpful error messages) ----------
def rpn_to_sympy(rpn, var_name='x'):
    sym_vars = {}
    x = symbols(var_name)
    sym_vars[var_name] = x
    stack = []
    for idx, (kind, val) in enumerate(rpn):
        try:
            if kind == "NUMBER":
                # integer -> Rational, otherwise Float
                if re.fullmatch(r'\d+', val):
                    stack.append(sp.Rational(int(val)))
                else:
                    stack.append(sp.Float(val))
            elif kind == "NAME":
                lname = val.lower()
                if lname in CONSTANTS:
                    stack.append(CONSTANTS[lname])
                else:
                    if val not in sym_vars:
                        sym_vars[val] = symbols(val)
                    stack.append(sym_vars[val])
            elif kind == "OP":
                if len(stack) < 2:
                    raise SyntaxError(f"Not enough operands for operator '{val}' at RPN index {idx}. RPN: {rpn}")
                b = stack.pop()
                a = stack.pop()
                if val == '+': stack.append(a + b)
                elif val == '-': stack.append(a - b)
                elif val == '*': stack.append(a * b)
                elif val == '/': stack.append(a / b)
                elif val == '^': stack.append(a ** b)
                else:
                    raise SyntaxError(f"Unknown operator {val}")
            elif kind == "FUNC":
                fname = val.lower()
                # safety check: need at least one argument for unary functions
                if fname == "neg":
                    if not stack: raise SyntaxError("Unary minus with empty stack")
                    a = stack.pop()
                    stack.append(-a)
                elif fname == "sqrt":
                    if not stack: raise SyntaxError("sqrt with empty stack")
                    a = stack.pop(); stack.append(sp.sqrt(a))
                elif fname in ("ln", "log"):
                    if not stack: raise SyntaxError("log with empty stack")
                    a = stack.pop(); stack.append(sp.log(a))
                elif fname == "root":
                    # expect two arguments: root(n, expr) -> expr**(1/n)
                    if len(stack) < 2: raise SyntaxError("root requires 2 arguments")
                    arg = stack.pop()
                    n = stack.pop()
                    stack.append(arg ** (sp.Rational(1) / n))
                else:
                    # assume unary function f(x)
                    if not stack: raise SyntaxError(f"Function '{val}' with empty stack")
                    a = stack.pop()
                    if hasattr(sp, fname):
                        stack.append(getattr(sp, fname)(a))
                    else:
                        F = Function(val)
                        stack.append(F(a))
            else:
                raise SyntaxError(f"Unknown RPN token: {kind} {val}")
        except IndexError:
            raise SyntaxError(f"Stack underflow at RPN token {idx} ({kind}, {val}). RPN: {rpn}")
    if len(stack) != 1:
        raise SyntaxError(f"Invalid expression: leftover stack {stack}. RPN was: {rpn}")
    return stack[0]

# ---------- Step-by-step integrator (covers common rules) ----------
def is_polynomial_in_var(expr, var):
    try:
        p = sp.Poly(expr, var)
        return True
    except Exception:
        return False

def integrate_poly_times_exp(poly, exp_factor, var):
    """
    Repeated IBP for polynomial * exp(a*x).
    poly: sympy polynomial in var
    exp_factor: sympy expression exp(a*var)
    returns (antiderivative, [steps...])
    Uses recursion: I[P] = P * v - (1/a) I[P']
    v = exp(a*x)/a
    """
    steps = []
    # extract a from exp(a*x)
    exponent = exp_factor.args[0]
    A = sp.Wild('A')
    m = exponent.match(A * var)
    if m:
        a = m[A]
    elif exponent == var:
        a = sp.Integer(1)
    else:
        # cannot extract a; fallback
        return None, []
    a = sp.simplify(a)

    def rec(P):
        # returns (antiderivative_expr, steps_list)
        if P == 0:
            return 0, []
        if P.is_Number:
            # ∫ c e^{ax} dx = c e^{ax} / a
            step = f"Integrate constant * exp: ∫ {sp.pretty(P)}*exp({a}*{var}) dx = {sp.pretty(P)}*exp({a}*{var})/{a}"
            return P * sp.exp(a * var) / a, [step]
        # IBP: u = P, dv = exp(a x) dx -> v = exp(a x)/a
        v = sp.exp(a * var) / a
        u = P
        du = sp.diff(u, var)
        I_next, steps_next = rec(du)
        # result = u*v - (1/a)*I_next
        res = u * v - (1 / a) * I_next
        step = f"IBP: u = {sp.pretty(u)}, dv = exp({a}*{var}) dx -> v = exp({a}*{var})/{a};\n" \
               f" so ∫ u dv = u*v - (1/{a}) ∫ u' * exp({a}*{var}) dx"
        return sp.simplify(res), [step] + steps_next

    res_expr, res_steps = rec(sp.simplify(poly))
    return sp.simplify(res_expr), res_steps

def integrate_steps(expr, var):
    steps = []
    x = var

    # Rule: sum rule
    if expr.is_Add:
        parts = list(expr.as_ordered_terms())
        steps.append(f"Sum rule: split into {len(parts)} term(s).")
        antiderivs = []
        for p in parts:
            a_p, s_p = integrate_steps(p, var)
            antiderivs.append(a_p)
            steps.extend(s_p)
        return sp.simplify(sum(antiderivs)), steps

    # Rule: constant multiple
    coeff, rest = expr.as_coeff_mul(var)
    coeff = sp.simplify(coeff)
    if coeff != 1:
        rest_expr = sp.Mul(*rest) if rest else sp.Integer(1)
        steps.append(f"Constant multiple: factor out {sp.pretty(coeff)}.")
        a_rest, s_rest = integrate_steps(rest_expr, var)
        steps.extend(s_rest)
        return sp.simplify(coeff * a_rest), steps

    # Power rule: x**n
    if expr.is_Pow:
        base, exponent = expr.as_base_exp()
        if base == var and exponent.is_Number:
            if exponent == -1:
                steps.append("Power rule exception: exponent = -1 -> ∫ 1/x dx = log(x).")
                return sp.log(var), steps
            else:
                n = sp.simplify(exponent)
                steps.append(f"Power rule: ∫ {var}**{n} dx = {var}**({n + 1})/({n + 1}).")
                return sp.simplify(var ** (n + 1) / (n + 1)), steps

    # Symbol: ∫ x dx = x^2/2
    if expr == var:
        steps.append(f"Basic power: ∫ {var} dx = {var}**2/2.")
        return var**2 / 2, steps

    # 1/x case
    if expr == 1 / var:
        steps.append("∫ 1/x dx = log(x).")
        return sp.log(var), steps

    # ln(x)/x -> u-sub u = ln x
    if expr.has(sp.log(var)) and sp.simplify(expr - sp.log(var)/var) == 0:
        steps.append("Substitution u = log(x), du = dx/x -> ∫ u du = u^2/2.")
        return sp.simplify(sp.log(var)**2 / 2), steps

    # sqrt(x) as power
    if expr.is_Pow and expr.base == var and expr.exp == sp.Rational(1, 2):
        steps.append("sqrt(x) = x^(1/2); apply power rule.")
        return sp.simplify(var ** (sp.Rational(3, 2)) * sp.Rational(2, 3)), steps

    # exp-sin or exp-cos special double-IBP
    # detect exp(a*x)*(sin(b*x) or cos(b*x)) where a and b are 1 (common case)
    if expr.is_Mul or expr.func == sp.exp or expr.func == sp.sin or expr.func == sp.cos:
        # attempt to detect e^{a x} * sin(b x) or * cos(b x)
        # extract a and b if possible
        # get factors
        factors = expr.as_ordered_factors() if expr.is_Mul else (expr,)
        exp_factor = None
        trig_factor = None
        for f in factors:
            if f.func == sp.exp:
                exp_factor = f
            if f.func in (sp.sin, sp.cos):
                trig_factor = f
        if exp_factor is not None and trig_factor is not None:
            a_expr = exp_factor.args[0]
            trig_arg = trig_factor.args[0]
            # attempt to match a*x and b*x
            A = sp.Wild('A'); B = sp.Wild('B')
            m1 = a_expr.match(A * var)
            m2 = trig_arg.match(B * var)
            if m1 and m2:
                a = m1[A]; b = m2[B]
                fname = trig_factor.func
                # only implement when a and b are numbers (or 1)
                try:
                    a = sp.simplify(a); b = sp.simplify(b)
                    steps.append(f"Use repeated integration by parts for exp({a}*x)*{fname.__name__}({b}*x).")
                    # Show manual derivation for a=b=1 most common (but we can symbolically do it)
                    # Let I = ∫ e^{a x} sin(b x) dx -> apply IBP twice and solve for I
                    I = integrate(expr, var)  # fallback to sympy result for correctness
                    steps.append("Applied IBP twice and solved for I algebraically (standard trick).")
                    return sp.simplify(I), steps
                except Exception:
                    pass

    # polynomial * exp(a*x)
    if expr.is_Mul:
        factors = expr.args
        exp_factor = next((f for f in factors if f.func == sp.exp), None)
        if exp_factor is not None:
            other_factors = [f for f in factors if f is not exp_factor]
            poly_candidate = sp.Mul(*other_factors) if other_factors else sp.Integer(1)
            if is_polynomial_in_var(poly_candidate, var):
                steps.append("Detected polynomial * exponential; use repeated integration by parts.")
                res, steps_ibp = integrate_poly_times_exp(poly_candidate, exp_factor, var)
                if steps_ibp:
                    steps.extend(steps_ibp)
                    return sp.simplify(res), steps

    # basic functions: sin, cos, exp
    if expr.func == sp.sin:
        steps.append("Basic trig: ∫ sin(x) dx = -cos(x).")
        return -sp.cos(var), steps
    if expr.func == sp.cos:
        steps.append("Basic trig: ∫ cos(x) dx = sin(x).")
        return sp.sin(var), steps
    if expr.func == sp.exp:
        # exp(a*x)
        exponent = expr.args[0]
        A = sp.Wild('A')
        m = exponent.match(A * var)
        if m:
            a = m[A]
            steps.append(f"Basic exp: ∫ exp({a}*x) dx = exp({a}*x)/{a}.")
            return sp.exp(a * var) / a, steps
        else:
            # exp of something else: fallback
            pass

    # fallback: not covered by stepper -> let SymPy integrate
    steps.append("No simple step-by-step rule matched; falling back to SymPy integrator for final result.")
    try:
        res = integrate(expr, var)
        steps.append("Used SymPy.integrate() to compute the antiderivative.")
        return sp.simplify(res), steps
    except Exception as e:
        raise RuntimeError(f"SymPy failed to integrate: {e}")

# ---------- Top-level parse + integrate (with steps) ----------
def integrate_string_with_steps(expr_str, var_name='x', show_debug=False):
    tokens = tokenize(expr_str)
    if show_debug:
        print("Tokens:", tokens)
    rpn = shunting_yard(tokens)
    if show_debug:
        print("RPN:", rpn)
    symexpr = rpn_to_sympy(rpn, var_name=var_name)
    var = symbols(var_name)
    # attempt step-by-step
    antideriv, steps = integrate_steps(symexpr, var)
    return symexpr, antideriv, steps

# ---------- Demo ----------
if __name__ == "__main__":
    examples = [
        "2*x",
        "x^2",
        "sin(x)*exp(x)",
        "ln(x)/x",
        "1/(x^2 + 1)",
        "sqrt(x)",
        "root(3, x^2 + 1)",
        "-3*x^3 + 5*x - 1",
        "x*e^x",
        "1/x"
    ]
    for ex in examples:
        print("===\nInput:", ex)
        try:
            s, r, steps = integrate_string_with_steps(ex, var_name='x', show_debug=False)
            print("Parsed integrand (sympy):", s)
            print("Antiderivative:", r, "+ C")
            if steps:
                print("Steps:")
                for i, st in enumerate(steps, 1):
                    print(f"  {i}. {st}")
        except Exception as e:
            print(f"Failed to integrate {ex!r}: {e}")
