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
import random

# ── colour helpers ────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[32m"
CYAN   = "\033[36m"
YELLOW = "\033[33m"
DIM    = "\033[2m"
RED    = "\033[31m"
LINE   = "─" * 62

# ── implementation usage table ────────────────────────────────────────────────
# Columns that are INFERRED (never asked directly):
#   os_backed, side_channel_resistant, security_bits
# Columns that map to user questions:
#   cryptographically_secure  ← Q2
#   easy_for_non_experts      ← Q1 (context)
#   good_for_embedded         ← Q4
#   high_throughput           ← Q5
#   standardized              ← Q6
#   forward_secrecy           ← Q7
#   deterministic             ← Q8
#   good_for_simulation       ← Q1
#   good_for_python           ← Q3

SCHEMES = {
    "LCG": {
        "cryptographically_secure": False,
        "deterministic":            True,
        "os_backed":                False,
        "easy_for_non_experts":     True,
        "high_throughput":          True,
        "good_for_embedded":        True,
        "good_for_simulation":      True,
        "good_for_python":          False,
        "forward_secrecy":          False,
        "side_channel_resistant":   False,
        "standardized":             False,
        "approx_speed_mbs":         8000,
        "security_bits":            0,
        "use_cases":                "Simple simulations, teaching, old game engines",
        "notes":                    "Trivially predictable — never use for security.",
    },
    "C rand": {
        "cryptographically_secure": False,
        "deterministic":            True,
        "os_backed":                False,
        "easy_for_non_experts":     True,
        "high_throughput":          True,
        "good_for_embedded":        True,
        "good_for_simulation":      True,
        "good_for_python":          False,
        "forward_secrecy":          False,
        "side_channel_resistant":   False,
        "standardized":             True,
        "approx_speed_mbs":         5000,
        "security_bits":            0,
        "use_cases":                "Simple C programs, legacy code, teaching",
        "notes":                    "Often an LCG internally. Output is predictable.",
    },
    "AES-CTR DRBG": {
        "cryptographically_secure": True,
        "deterministic":            True,
        "os_backed":                False,
        "easy_for_non_experts":     False,
        "high_throughput":          True,
        "good_for_embedded":        True,
        "good_for_simulation":      False,
        "good_for_python":          False,
        "forward_secrecy":          False,
        "side_channel_resistant":   True,
        "standardized":             True,
        "approx_speed_mbs":         3000,
        "security_bits":            128,
        "use_cases":                "FIPS/NIST-compliant systems, HSMs, government applications",
        "notes":                    "NIST SP 800-90A. Requires AES-NI for side-channel safety.",
    },
    "HMAC-DRBG": {
        "cryptographically_secure": True,
        "deterministic":            True,
        "os_backed":                False,
        "easy_for_non_experts":     False,
        "high_throughput":          False,
        "good_for_embedded":        True,
        "good_for_simulation":      False,
        "good_for_python":          False,
        "forward_secrecy":          True,
        "side_channel_resistant":   False,
        "standardized":             True,
        "approx_speed_mbs":         350,
        "security_bits":            256,
        "use_cases":                "Key generation, certificate signing, FIPS-compliant apps",
        "notes":                    "NIST SP 800-90A. Slower but provides forward secrecy.",
    },
    "Hash-DRBG": {
        "cryptographically_secure": True,
        "deterministic":            True,
        "os_backed":                False,
        "easy_for_non_experts":     False,
        "high_throughput":          False,
        "good_for_embedded":        True,
        "good_for_simulation":      False,
        "good_for_python":          False,
        "forward_secrecy":          False,
        "side_channel_resistant":   False,
        "standardized":             True,
        "approx_speed_mbs":         500,
        "security_bits":            256,
        "use_cases":                "NIST-compliant key/token generation",
        "notes":                    "NIST SP 800-90A. Simpler than HMAC-DRBG but no forward secrecy.",
    },
    "/dev/urandom": {
        "cryptographically_secure": True,
        "deterministic":            False,
        "os_backed":                True,
        "easy_for_non_experts":     True,
        "high_throughput":          True,
        "good_for_embedded":        False,
        "good_for_simulation":      False,
        "good_for_python":          False,
        "forward_secrecy":          True,
        "side_channel_resistant":   True,
        "standardized":             False,
        "approx_speed_mbs":         1500,
        "security_bits":            256,
        "use_cases":                "Key generation, seeding other PRGs, general secure randomness on Linux/macOS",
        "notes":                    "ChaCha20-based since Linux kernel 5.17. Non-blocking and safe.",
    },
    "Python secrets": {
        "cryptographically_secure": True,
        "deterministic":            False,
        "os_backed":                True,
        "easy_for_non_experts":     True,
        "high_throughput":          False,
        "good_for_embedded":        False,
        "good_for_simulation":      False,
        "good_for_python":          True,
        "forward_secrecy":          True,
        "side_channel_resistant":   True,
        "standardized":             False,
        "approx_speed_mbs":         400,
        "security_bits":            256,
        "use_cases":                "Passwords, tokens, API keys, OTPs in Python apps",
        "notes":                    "Python 3.6+ stdlib. Wraps os.urandom(). Easiest secure option for Python.",
    },
    "ChaCha20": {
        "cryptographically_secure": True,
        "deterministic":            True,
        "os_backed":                False,
        "easy_for_non_experts":     False,
        "high_throughput":          True,
        "good_for_embedded":        False,
        "good_for_simulation":      False,
        "good_for_python":          False,
        "forward_secrecy":          False,
        "side_channel_resistant":   True,
        "standardized":             True,
        "approx_speed_mbs":         4500,
        "security_bits":            256,
        "use_cases":                "TLS 1.3, WireGuard, disk encryption, high-speed CSPRNG",
        "notes":                    "RFC 8439. ARX design is naturally constant-time. Used in Linux /dev/urandom.",
    },
}

# ── decision tree ─────────────────────────────────────────────────────────────
# Each node:
#   question : str          plain-English question shown to user
#   hint     : str          one-line clarification shown in dim text
#   choices  : list of dicts  {label, next}
#   leaf     : list[str] | None   scheme names at leaf nodes

def leaf(*schemes):
    return {"question": None, "hint": None, "choices": [], "leaf": list(schemes)}


def build_tree():

    # ── leaves ────────────────────────────────────────────────────────────────

    # Non-crypto
    l_simulation_fast     = leaf("LCG", "C rand")
    l_simulation_embedded = leaf("C rand", "LCG")
    l_simulation_repro    = leaf("C rand", "LCG")
    l_simulation_general  = leaf("C rand", "LCG")

    # Crypto — compliance branch
    l_fips_forward        = leaf("HMAC-DRBG")
    l_fips_fast           = leaf("AES-CTR DRBG", "Hash-DRBG")
    l_fips_general        = leaf("AES-CTR DRBG", "HMAC-DRBG", "Hash-DRBG")

    # Crypto — non-compliance branch
    l_fast_repro          = leaf("ChaCha20", "AES-CTR DRBG")
    l_fast_nonrepro       = leaf("/dev/urandom", "ChaCha20")
    l_slow_forward        = leaf("HMAC-DRBG", "/dev/urandom")
    l_slow_general        = leaf("Hash-DRBG", "HMAC-DRBG")
    l_python              = leaf("Python secrets")
    l_os_general          = leaf("/dev/urandom", "Python secrets")

    # ── Q8: Reproducible sequence? (non-crypto path) ──────────────────────────
    q8_noncrypto = {
        "question": "Do you need to reproduce the exact same sequence of numbers later\n"
                    "  (e.g. for debugging, testing, or procedural generation with a seed)?",
        "hint":     "If yes, you'll need a deterministic generator you can re-seed.",
        "choices": [
            {"label": "Yes — same seed should give same output", "next": l_simulation_repro},
            {"label": "No — different every time is fine",       "next": l_simulation_general},
            {"label": "Not sure",                                "next": l_simulation_general},
        ],
    }

    # ── Q5: Speed (non-crypto path) ───────────────────────────────────────────
    q5_noncrypto = {
        "question": "Does speed matter a lot — like generating millions of\n"
                    "  random values per second?",
        "hint":     "e.g. physics simulation, procedural world generation, particle systems.",
        "choices": [
            {"label": "Yes — need maximum speed",          "next": l_simulation_fast},
            {"label": "No — speed is not a concern",       "next": q8_noncrypto},
            {"label": "Not sure",                          "next": q8_noncrypto},
        ],
    }

    # ── Q4: Embedded? (non-crypto path) ──────────────────────────────────────
    q4_noncrypto = {
        "question": "Does it need to run on a microcontroller or a very\n"
                    "  resource-limited device?",
        "hint":     "e.g. Arduino, ESP32, or any device with very limited RAM/CPU.",
        "choices": [
            {"label": "Yes — very limited hardware",  "next": l_simulation_embedded},
            {"label": "No — standard computer/phone", "next": q5_noncrypto},
            {"label": "Not sure",                     "next": q5_noncrypto},
        ],
    }

    # ── Q8: Reproducible sequence? (crypto fast path) ────────────────────────
    q8_crypto_fast = {
        "question": "Do you need to reproduce the exact same sequence later\n"
                    "  given the same seed?",
        "hint":     "Deterministic generators can replay output; OS-backed ones cannot.",
        "choices": [
            {"label": "Yes — must be reproducible",        "next": l_fast_repro},
            {"label": "No — different every time is fine", "next": l_fast_nonrepro},
            {"label": "Not sure",                          "next": l_fast_repro},
        ],
    }

    # ── Q5: Speed (crypto, non-compliance path) ───────────────────────────────
    q5_crypto = {
        "question": "Does speed matter a lot — like encrypting large files or\n"
                    "  generating a huge number of keys quickly?",
        "hint":     "High-throughput schemes can produce 3,000–4,500 MB/s vs ~350 MB/s for slower ones.",
        "choices": [
            {"label": "Yes — need high throughput",    "next": q8_crypto_fast},
            {"label": "No — speed is not a concern",   "next": l_slow_forward},
            {"label": "Not sure",                      "next": q8_crypto_fast},
        ],
    }

    # ── Q7: Forward secrecy (crypto, non-compliance path) ────────────────────
    q7_crypto = {
        "question": "If an attacker broke into your server tomorrow and stole\n"
                    "  its memory, should they be unable to figure out what\n"
                    "  random values were generated in the past?",
        "hint":     "This is called 'forward secrecy'. Important for long-running servers.",
        "choices": [
            {"label": "Yes — past outputs must stay secret", "next": l_slow_forward},
            {"label": "No — not a concern",                  "next": q5_crypto},
            {"label": "Not sure",                            "next": q5_crypto},
        ],
    }

    # ── Q6: FIPS / compliance (crypto path) ──────────────────────────────────
    q6_fips_forward = {
        "question": "Within the compliance requirement, do you also need\n"
                    "  forward secrecy?",
        "hint":     "Required in some high-security government/finance contexts.",
        "choices": [
            {"label": "Yes",      "next": l_fips_forward},
            {"label": "No",       "next": l_fips_fast},
            {"label": "Not sure", "next": l_fips_general},
        ],
    }

    q6_crypto = {
        "question": "Is this for something that must meet an official standard —\n"
                    "  like a government system, medical device, or financial app\n"
                    "  that requires FIPS 140 or NIST compliance?",
        "hint":     "If unsure, the answer is probably No.",
        "choices": [
            {"label": "Yes — must be FIPS/NIST certified", "next": q6_fips_forward},
            {"label": "No — no compliance requirement",    "next": q7_crypto},
            {"label": "Not sure",                          "next": q7_crypto},
        ],
    }

    # ── Q4: Embedded? (crypto path) ──────────────────────────────────────────
    q4_crypto = {
        "question": "Does it need to run on a microcontroller or a very\n"
                    "  resource-limited device?",
        "hint":     "e.g. a smart card, IoT sensor, or device with <64KB RAM.",
        "choices": [
            {"label": "Yes — very limited hardware",  "next": q6_crypto},
            {"label": "No — standard computer/phone", "next": q6_crypto},
            {"label": "Not sure",                     "next": q6_crypto},
        ],
    }

    # ── Q3: Python? ───────────────────────────────────────────────────────────
    q3 = {
        "question": "Are you writing a Python application?",
        "hint":     "Python has a built-in secure module that handles everything for you.",
        "choices": [
            {"label": "Yes — it's a Python project",     "next": l_python},
            {"label": "No — different language / system","next": q4_crypto},
            {"label": "Not sure",                        "next": q4_crypto},
        ],
    }

    # ── Q2: Security needed? ─────────────────────────────────────────────────
    q2 = {
        "question": "Are you worried about someone being able to guess or predict\n"
                    "  the random values your program generates?",
        "hint":     "If generating passwords, tokens, keys, or anything security-related — answer Yes.",
        "choices": [
            {"label": "Yes — it must be unpredictable to an attacker", "next": q3},
            {"label": "No — predictability is not a concern",          "next": q4_noncrypto},
            {"label": "Not sure — better safe than sorry",             "next": q3},
        ],
    }

    # ── Q1: What are you building? (root) ────────────────────────────────────
    root = {
        "question": "What are you building?",
        "hint":     "Pick the closest match — you can always go back.",
        "choices": [
            {"label": "A game, simulation, or statistical model",         "next": q4_noncrypto},
            {"label": "A general app (web, mobile, desktop)",             "next": q2},
            {"label": "Something security-sensitive (auth, crypto, keys)","next": q3},
            {"label": "Not sure / something else",                        "next": q2},
        ],
    }

    return root


# ── display ───────────────────────────────────────────────────────────────────

def header():
    print(f"\n{BOLD}{LINE}{RESET}")
    print(f"{BOLD}  PRG Scheme Selector — NYU cs6903/4783  Project 2.6{RESET}")
    print(f"{BOLD}{LINE}{RESET}\n")
    print("  Answer a few plain-English questions and I'll recommend")
    print("  the right Pseudo-Random Generator for your situation.\n")
    print(f"{DIM}  Enter the number of your answer. Type 'q' to quit.{RESET}\n")


def wrap(text, width=58, indent=""):
    return textwrap.fill(text, width=width,
                         initial_indent=indent,
                         subsequent_indent=indent)


def tick(v):
    return f"{GREEN}✔{RESET}" if v else f"{RED}✘{RESET}"


def show_result(leaf_schemes):
    print(f"\n{LINE}")
    print(f"{BOLD}{GREEN}  Recommendation{RESET}\n")

    top  = leaf_schemes[0]
    rest = leaf_schemes[1:]
    s    = SCHEMES[top]

    print(f"  {BOLD}★  {top}{RESET}\n")
    sec = f"{s['security_bits']}-bit" if s['cryptographically_secure'] else "None"
    print(f"     Security level           : {sec}")
    print(f"     Cryptographically secure : {tick(s['cryptographically_secure'])}")
    print(f"     OS-backed                : {tick(s['os_backed'])}")
    print(f"     High throughput          : {tick(s['high_throughput'])}  (~{s['approx_speed_mbs']:,} MB/s)")
    print(f"     Forward secrecy          : {tick(s['forward_secrecy'])}")
    print(f"     Side-channel resistant   : {tick(s['side_channel_resistant'])}")
    print(f"     Good for embedded        : {tick(s['good_for_embedded'])}")
    print(f"     Reproducible (seeded)    : {tick(s['deterministic'])}")
    print(f"     FIPS/NIST standardized   : {tick(s['standardized'])}")
    print(f"\n     {wrap(s['use_cases'], indent='     ')}")
    if s.get("notes"):
        print(f"     {DIM}{wrap(s['notes'], indent='     ')}{RESET}")

    if rest:
        print(f"\n  {DIM}Also consider:{RESET}")
        for name in rest[:3]:
            alt = SCHEMES[name]
            tag = "secure" if alt["cryptographically_secure"] else "fast"
            print(f"    • {name}  [{tag}, ~{alt['approx_speed_mbs']:,} MB/s]")

    print(f"\n{LINE}\n")


def ask(node, step, total):
    print(f"{LINE}")
    print(f"{DIM}  Question {step}{RESET}")
    print(f"\n{BOLD}  {node['question']}{RESET}")
    if node.get("hint"):
        print(f"  {DIM}{node['hint']}{RESET}")
    print()

    choices = node["choices"]
    for i, c in enumerate(choices, 1):
        print(f"  {CYAN}{i}{RESET}. {c['label']}")
    print()

    while True:
        raw = input(f"  Your answer [1–{len(choices)}]: ").strip().lower()
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
        node = ask(node, step, 8)
        if node is None:
            print("\n  Goodbye!\n")
            return
        step += 1


# ── table printer ─────────────────────────────────────────────────────────────

def print_table():
    cols = [
        ("Crypto?",       "cryptographically_secure"),
        ("Deterministic?","deterministic"),
        ("OS-backed?",    "os_backed"),
        ("Non-expert?",   "easy_for_non_experts"),
        ("Fast?",         "high_throughput"),
        ("Embedded?",     "good_for_embedded"),
        ("Simulation?",   "good_for_simulation"),
        ("Fwd Secrecy?★", "forward_secrecy"),
        ("SideCh Res?★",  "side_channel_resistant"),
        ("Speed MB/s",    "approx_speed_mbs"),
        ("Sec bits",      "security_bits"),
        ("Standardized?", "standardized"),
    ]
    h = ["Scheme"] + [c[0] for c in cols]
    w = [22] + [max(len(c[0]), 8) for c in cols]

    print("\n" + "  ".join(f"{v:<{w[i]}}" for i, v in enumerate(h)))
    print("  ".join("-" * x for x in w))
    for name, s in SCHEMES.items():
        row = [name]
        for _, key in cols:
            val = s[key]
            row.append("Yes" if val is True else ("No" if val is False else str(val)))
        print("  ".join(f"{v:<{w[i]}}" for i, v in enumerate(row)))
    print(f"\n  ★ = new columns added beyond lecture slides\n")


# ── evaluation ────────────────────────────────────────────────────────────────

# Maps each scheme to the answers it would give for each question node.
# Keyed by node question substring for robustness.
SCHEME_ANSWERS = {
    "LCG": {
        "What are you building":                         0,  # game/simulation
        "worried about someone being able to guess":     1,  # No
        "Python application":                            1,  # No
        "microcontroller":                               1,  # No
        "millions of random values per second":          0,  # Yes
        "official standard":                             1,  # No
        "broke into your server":                        1,  # No
        "reproduce the exact same sequence":             0,  # Yes
        "compliance requirement, do you also":           1,  # No
        "speed matter a lot — like encrypting":          1,  # No
    },
    "C rand": {
        "What are you building":                         0,
        "worried about someone being able to guess":     1,
        "Python application":                            1,
        "microcontroller":                               1,
        "millions of random values per second":          1,  # No (speed not top)
        "official standard":                             1,
        "broke into your server":                        1,
        "reproduce the exact same sequence":             0,  # Yes
        "compliance requirement, do you also":           1,
        "speed matter a lot — like encrypting":          1,
    },
    "AES-CTR DRBG": {
        "What are you building":                         2,  # security-sensitive
        "worried about someone being able to guess":     0,
        "Python application":                            1,
        "microcontroller":                               1,
        "millions of random values per second":          0,  # Yes
        "official standard":                             0,  # Yes FIPS
        "broke into your server":                        1,
        "reproduce the exact same sequence":             0,
        "compliance requirement, do you also":           1,  # No fwd secrecy
        "speed matter a lot — like encrypting":          0,  # Yes
    },
    "HMAC-DRBG": {
        "What are you building":                         2,
        "worried about someone being able to guess":     0,
        "Python application":                            1,
        "microcontroller":                               1,
        "millions of random values per second":          1,
        "official standard":                             0,  # Yes FIPS
        "broke into your server":                        0,  # Yes fwd secrecy
        "reproduce the exact same sequence":             0,
        "compliance requirement, do you also":           0,  # Yes fwd secrecy
        "speed matter a lot — like encrypting":          1,
    },
    "Hash-DRBG": {
        "What are you building":                         2,
        "worried about someone being able to guess":     0,
        "Python application":                            1,
        "microcontroller":                               1,
        "millions of random values per second":          1,
        "official standard":                             0,  # Yes FIPS
        "broke into your server":                        1,
        "reproduce the exact same sequence":             0,
        "compliance requirement, do you also":           1,  # No fwd secrecy
        "speed matter a lot — like encrypting":          1,
    },
    "/dev/urandom": {
        "What are you building":                         1,  # general app
        "worried about someone being able to guess":     0,
        "Python application":                            1,  # No (not Python-specific)
        "microcontroller":                               1,
        "millions of random values per second":          1,
        "official standard":                             1,
        "broke into your server":                        0,  # Yes
        "reproduce the exact same sequence":             1,  # No (non-deterministic)
        "compliance requirement, do you also":           1,
        "speed matter a lot — like encrypting":          1,
    },
    "Python secrets": {
        "What are you building":                         2,
        "worried about someone being able to guess":     0,
        "Python application":                            0,  # Yes
        "microcontroller":                               1,
        "millions of random values per second":          1,
        "official standard":                             1,
        "broke into your server":                        0,
        "reproduce the exact same sequence":             1,
        "compliance requirement, do you also":           1,
        "speed matter a lot — like encrypting":          1,
    },
    "ChaCha20": {
        "What are you building":                         2,
        "worried about someone being able to guess":     0,
        "Python application":                            1,
        "microcontroller":                               1,
        "millions of random values per second":          0,
        "official standard":                             1,
        "broke into your server":                        1,
        "reproduce the exact same sequence":             0,
        "compliance requirement, do you also":           1,
        "speed matter a lot — like encrypting":          0,
    },
}


def simulate_user(scheme_name, tree):
    """Walk the tree answering as the given scheme would."""
    node = tree
    answers = SCHEME_ANSWERS[scheme_name]

    while node.get("leaf") is None:
        q = node["question"]
        choices = node["choices"]

        # Find matching answer key
        matched_key = None
        for key in answers:
            if key.lower() in q.lower():
                matched_key = key
                break

        if matched_key is not None:
            idx = answers[matched_key]
            idx = min(idx, len(choices) - 1)
            node = choices[idx]["next"]
        else:
            # Fallback: last choice ("Not sure")
            node = choices[-1]["next"]

    return node["leaf"]


def run_evaluation(n_trials=1000):
    tree         = build_tree()
    scheme_names = list(SCHEMES.keys())

    correct      = 0
    top1_correct = 0
    per_scheme   = {s: {"trials": 0, "hits": 0, "top1": 0} for s in scheme_names}

    for _ in range(n_trials):
        chosen = random.choice(scheme_names)
        result = simulate_user(chosen, tree)

        per_scheme[chosen]["trials"] += 1
        if chosen in result:
            correct += 1
            per_scheme[chosen]["hits"] += 1
        if result and result[0] == chosen:
            top1_correct += 1
            per_scheme[chosen]["top1"] += 1

    acc  = correct      / n_trials * 100
    top1 = top1_correct / n_trials * 100

    print(f"\n{LINE}")
    print(f"{BOLD}  Evaluation Results  ({n_trials} trials){RESET}\n")
    print(f"  Any-rank accuracy : {GREEN}{acc:.1f}%{RESET}  (scheme in recommendation list)")
    print(f"  Top-1 accuracy    : {GREEN}{top1:.1f}%{RESET}  (scheme is #1 recommendation)")
    print(f"  Random baseline   : {100/len(scheme_names):.1f}%  "
          f"(random pick from {len(scheme_names)} schemes)\n")

    print(f"  Per-scheme breakdown:")
    for name, data in per_scheme.items():
        t   = data["trials"]
        h   = data["hits"]
        pct = h / t * 100 if t else 0
        bar = "█" * int(pct / 5)
        t1  = data["top1"] / t * 100 if t else 0
        print(f"    {name:<22}  any:{pct:5.1f}%  top1:{t1:5.1f}%  {bar}")

    print(f"\n{LINE}\n")


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--eval"  in sys.argv:
        run_evaluation()
    elif "--table" in sys.argv:
        print_table()
    else:
        run_interactive()
