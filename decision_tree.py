"""
Decision tree for PRG scheme selection — rebuilt on merged table.

Branch logic:
1. Need cryptographic security?
   ├─ No  → Need simulation-quality stats?
   │          ├─ Yes → Need embedded support? → [LCG] or [C rand]
   │          └─ No  → [C rand, LCG]
   └─ Yes → Is this a Python project? (easy/os-backed path)
              ├─ Yes → [Python secrets]
              └─ No  → Need OS-backed (non-deterministic) randomness?
                         ├─ Yes → [/dev/urandom]
                         └─ No  → Need forward secrecy?
                                    ├─ Yes → [HMAC-DRBG]
                                    └─ No  → Need high throughput?
                                               ├─ Yes → Need side-channel resistance?
                                               │          ├─ Yes → [ChaCha20]
                                               │          └─ No  → [AES-CTR DRBG]
                                               └─ No  → [Hash-DRBG, HMAC-DRBG]
"""

from prg_table import SCHEMES


def rank(candidates):
    """Sort by: cryptographic first, then speed descending."""
    return sorted(candidates,
                  key=lambda s: (-int(SCHEMES[s]["cryptographically_secure"]),
                                 -SCHEMES[s]["approx_speed_mbs"]))


def leaf(*schemes):
    return {"question": None, "feature": None, "choices": [], "leaf": list(schemes)}


def build_tree():

    # ── Non-crypto leaves ─────────────────────────────────────────────────────
    non_crypto_embedded = leaf("LCG", "C rand")
    non_crypto_general  = leaf("C rand", "LCG")

    non_crypto_embedded_node = {
        "question": "Do you need it to run on embedded or very constrained hardware?",
        "feature":  "good_for_embedded",
        "choices": [
            {"label": "Yes — limited RAM/CPU",       "value": True,      "next": non_crypto_embedded},
            {"label": "No — standard hardware",      "value": False,     "next": non_crypto_general},
            {"label": "Not sure",                    "value": "unknown", "next": non_crypto_general},
        ],
    }

    non_crypto_node = {
        "question": "Do you need good statistical quality for simulations or games?",
        "feature":  "good_for_simulation",
        "choices": [
            {"label": "Yes — simulation / game / Monte Carlo",  "value": True,      "next": non_crypto_embedded_node},
            {"label": "No — any output is fine",                "value": False,     "next": non_crypto_general},
            {"label": "Not sure",                               "value": "unknown", "next": non_crypto_general},
        ],
    }

    # ── Crypto leaves ─────────────────────────────────────────────────────────
    leaf_python      = leaf("Python secrets")
    leaf_os          = leaf("/dev/urandom", "Python secrets")
    leaf_forward_sec = leaf("HMAC-DRBG")
    leaf_chacha      = leaf("ChaCha20", "AES-CTR DRBG")
    leaf_aes_ctr     = leaf("AES-CTR DRBG", "ChaCha20")
    leaf_slow_crypto = leaf("Hash-DRBG", "HMAC-DRBG")

    # Side-channel branch
    side_channel_node = {
        "question": "Do you need resistance to timing / side-channel attacks "
                    "(e.g. in a shared cloud environment or smartcard)?",
        "feature":  "side_channel_resistant",
        "choices": [
            {"label": "Yes — side-channel safety required",  "value": True,      "next": leaf_chacha},
            {"label": "No — not a concern",                  "value": False,     "next": leaf_aes_ctr},
            {"label": "Not sure",                            "value": "unknown", "next": leaf_chacha},
        ],
    }

    # Throughput branch
    throughput_node = {
        "question": "Do you need high throughput (encrypting large streams, "
                    "generating many keys quickly)?",
        "feature":  "high_throughput",
        "choices": [
            {"label": "Yes — need high speed",       "value": True,      "next": side_channel_node},
            {"label": "No — throughput not critical","value": False,     "next": leaf_slow_crypto},
            {"label": "Not sure",                    "value": "unknown", "next": side_channel_node},
        ],
    }

    # Forward secrecy branch
    forward_sec_node = {
        "question": "Do you need forward secrecy? "
                    "(past output stays safe even if the current state is later compromised)",
        "feature":  "forward_secrecy",
        "choices": [
            {"label": "Yes — forward secrecy required",  "value": True,      "next": leaf_forward_sec},
            {"label": "No — not needed",                 "value": False,     "next": throughput_node},
            {"label": "Not sure",                        "value": "unknown", "next": throughput_node},
        ],
    }

    # OS-backed branch
    os_backed_node = {
        "question": "Do you want OS-backed randomness (non-deterministic, "
                    "seeded by the kernel from hardware entropy)?",
        "feature":  "os_backed",
        "choices": [
            {"label": "Yes — let the OS handle it",      "value": True,      "next": leaf_os},
            {"label": "No — I'll manage the seed myself","value": False,     "next": forward_sec_node},
            {"label": "Not sure",                        "value": "unknown", "next": leaf_os},
        ],
    }

    # Python shortcut branch
    python_node = {
        "question": "Are you writing a Python application?",
        "feature":  None,
        "choices": [
            {"label": "Yes — Python project",        "value": "yes",     "next": leaf_python},
            {"label": "No — other language / system","value": "no",      "next": os_backed_node},
            {"label": "Not sure",                    "value": "unknown", "next": os_backed_node},
        ],
    }

    # Root
    root = {
        "question": "Do you need cryptographically secure randomness? "
                    "(i.e. output must be unpredictable to an adversary — "
                    "required for passwords, keys, tokens, or any security use)",
        "feature":  "cryptographically_secure",
        "choices": [
            {"label": "Yes — security is required",           "value": True,      "next": python_node},
            {"label": "No — simulation / stats / games only", "value": False,     "next": non_crypto_node},
            {"label": "Not sure",                             "value": "unknown", "next": python_node},
        ],
    }

    return root
