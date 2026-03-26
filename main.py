#!/usr/bin/env python3
"""
PRG Scheme Selector — Interactive Decision Tree
NYU cs6903/4783, Project 2.6

Usage:
    python main.py          # interactive mode
    python main.py --eval   # evaluation experiment
    python main.py --table  # print the implementation usage table
"""

import sys
import textwrap

from prg_table import SCHEMES
from decision_tree import build_tree

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[32m"
CYAN   = "\033[36m"
YELLOW = "\033[33m"
DIM    = "\033[2m"
RED    = "\033[31m"
LINE   = "─" * 62


# ── display helpers ───────────────────────────────────────────────────────────

def header():
    print(f"\n{BOLD}{LINE}{RESET}")
    print(f"{BOLD}  PRG Scheme Selector — NYU cs6903/4783  Project 2.6{RESET}")
    print(f"{BOLD}{LINE}{RESET}\n")
    print("  Answer a few questions and I'll recommend the right")
    print("  Pseudo-Random Generator for your situation.\n")
    print(f"{DIM}  Enter the number of your answer. Type 'q' to quit.{RESET}\n")


def tick(v):  return f"{GREEN}✔{RESET}" if v else f"{RED}✘{RESET}"
def yn(v):    return "Yes" if v else "No"


def show_result(leaf_schemes):
    print(f"\n{LINE}")
    print(f"{BOLD}{GREEN}  Recommendation{RESET}\n")

    top  = leaf_schemes[0]
    rest = leaf_schemes[1:]
    s    = SCHEMES[top]

    print(f"  {BOLD}★  {top}{RESET}\n")
    print(f"     Cryptographically secure : {tick(s['cryptographically_secure'])}")
    print(f"     OS-backed                : {tick(s['os_backed'])}")
    print(f"     High throughput          : {tick(s['high_throughput'])}  (~{s['approx_speed_mbs']:,} MB/s)")
    if s['cryptographically_secure']:
        print(f"     Security level           : {s['security_bits']}-bit")
        print(f"     Forward secrecy          : {tick(s['forward_secrecy'])}")
        print(f"     Side-channel resistant   : {tick(s['side_channel_resistant'])}")
    print(f"     Good for embedded        : {tick(s['good_for_embedded'])}")
    print(f"     Good for simulation      : {tick(s['good_for_simulation'])}")
    print(f"     Standardized             : {tick(s['standardized'])}")
    print(f"\n     Use cases : {s['use_cases']}")
    note = s.get("notes", "")
    if note:
        wrapped = textwrap.fill(note, width=56,
                                initial_indent    ="     Note      : ",
                                subsequent_indent ="                  ")
        print(wrapped)

    if rest:
        print(f"\n  {DIM}Also consider:{RESET}")
        for name in rest[:3]:
            alt = SCHEMES[name]
            tag = "secure" if alt["cryptographically_secure"] else "fast"
            print(f"    • {name}  [{tag}, ~{alt['approx_speed_mbs']:,} MB/s]")

    print(f"\n{LINE}\n")


def ask(node, step):
    print(f"{LINE}")
    q = node["question"]
    # word-wrap long questions
    wrapped_q = textwrap.fill(q, width=58,
                               initial_indent    =f"{BOLD}Q{step}: ",
                               subsequent_indent ="      ")
    print(f"{wrapped_q}{RESET}\n")

    choices = node["choices"]
    for i, c in enumerate(choices, 1):
        print(f"  {CYAN}{i}{RESET}. {c['label']}")
    print()

    while True:
        raw = input(f"  Your choice [1–{len(choices)}]: ").strip().lower()
        if raw in ("q", "quit", "exit"):
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(choices):
            return choices[int(raw) - 1]["next"]
        print(f"  {YELLOW}Please enter a number between 1 and {len(choices)}.{RESET}")


def run_interactive():
    header()
    tree = build_tree()
    node = tree
    step = 1

    while node is not None:
        if node.get("leaf") is not None:
            show_result(node["leaf"])
            try:
                again = input("  Run again? [y/N]: ").strip().lower()
            except EOFError:
                return
            if again == "y":
                run_interactive()
            return
        node = ask(node, step)
        if node is None:
            print("\n  Goodbye!\n")
            return
        step += 1


# ── table printer ─────────────────────────────────────────────────────────────

def print_table():
    cols = [
        ("CryptoSecure",     "cryptographically_secure"),
        ("Deterministic",    "deterministic"),
        ("OS-backed",        "os_backed"),
        ("NonExpertFriendly","easy_for_non_experts"),
        ("HighThroughput",   "high_throughput"),
        ("Embedded",         "good_for_embedded"),
        ("Simulation",       "good_for_simulation"),
        ("FwdSecrecy★",      "forward_secrecy"),
        ("SideChRes★",       "side_channel_resistant"),
        ("Speed(MB/s)",      "approx_speed_mbs"),
        ("SecBits",          "security_bits"),
    ]
    header_row = ["Scheme"] + [c[0] for c in cols]
    col_w = [max(len(h), 10) for h in header_row]
    col_w[0] = 20

    sep   = "  ".join("-" * w for w in col_w)
    h_row = "  ".join(f"{h:<{col_w[i]}}" for i, h in enumerate(header_row))
    print(f"\n{BOLD}{h_row}{RESET}")
    print(sep)

    for name, s in SCHEMES.items():
        row = [name]
        for label, key in cols:
            val = s[key]
            if isinstance(val, bool):
                row.append("Yes" if val else "No")
            else:
                row.append(str(val))
        print("  ".join(f"{v:<{col_w[i]}}" for i, v in enumerate(row)))

    print(f"\n  ★ = new columns added beyond lecture slides\n")


# ── evaluation ────────────────────────────────────────────────────────────────

def simulate_user(scheme_name, tree):
    """Walk tree answering as if we are the given scheme."""
    node = tree
    s    = SCHEMES[scheme_name]

    while node.get("leaf") is None:
        feature = node.get("feature")
        choices = node["choices"]

        if feature is None:
            # Python shortcut question — answer based on os_backed as proxy
            answer_val = "yes" if scheme_name == "Python secrets" else "no"
            matched = False
            for c in choices:
                if c["value"] == answer_val:
                    node = c["next"]; matched = True; break
            if not matched:
                node = choices[-1]["next"]
        else:
            scheme_val = s.get(feature)
            matched    = False
            for c in choices:
                if c["value"] == scheme_val:
                    node = c["next"]; matched = True; break
            if not matched:
                node = choices[-1]["next"]   # "not sure" fallback

    return node["leaf"]


def run_evaluation(n_trials=1000):
    import random
    tree         = build_tree()
    scheme_names = list(SCHEMES.keys())

    correct      = 0
    top1_correct = 0
    per_scheme   = {s: {"trials": 0, "hits": 0, "top1": 0} for s in scheme_names}

    for _ in range(n_trials):
        chosen = random.choice(scheme_names)
        leaf   = simulate_user(chosen, tree)

        per_scheme[chosen]["trials"] += 1
        if chosen in leaf:
            correct += 1
            per_scheme[chosen]["hits"] += 1
        if leaf and leaf[0] == chosen:
            top1_correct += 1
            per_scheme[chosen]["top1"] += 1

    acc  = correct      / n_trials * 100
    top1 = top1_correct / n_trials * 100

    print(f"\n{LINE}")
    print(f"{BOLD}  Evaluation Results  ({n_trials} trials){RESET}\n")
    print(f"  Any-rank accuracy : {GREEN}{acc:.1f}%{RESET}  "
          f"(correct scheme appears in recommendation list)")
    print(f"  Top-1 accuracy    : {GREEN}{top1:.1f}%{RESET}  "
          f"(correct scheme is the #1 recommendation)\n")
    print(f"  Baseline (random) : {100/len(scheme_names):.1f}%  "
          f"(random pick from {len(scheme_names)} schemes)\n")

    print(f"  Per-scheme breakdown (any-rank):")
    for name, data in per_scheme.items():
        t   = data["trials"]
        h   = data["hits"]
        pct = h / t * 100 if t else 0
        bar = "█" * int(pct / 5)
        print(f"    {name:<22}  {pct:5.1f}%  {bar}")

    print(f"\n{LINE}\n")
    return acc


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--eval"  in sys.argv:
        run_evaluation()
    elif "--table" in sys.argv:
        print_table()
    else:
        run_interactive()
