"""
PRG Implementation Usage Table — Merged version
Combines user's scheme list/columns with quantitative enhancements.

Columns:
  cryptographically_secure  : bool
  deterministic             : bool
  os_backed                 : bool
  easy_for_non_experts      : bool
  high_throughput           : bool   (>1000 MB/s)
  good_for_embedded         : bool
  good_for_simulation       : bool
  forward_secrecy           : bool   [new col 1]
  side_channel_resistant    : bool   [new col 2]
  approx_speed_mbs          : int    [quantitative]
  security_bits             : int    [quantitative, 0 = not cryptographic]
  standardized              : bool
  use_cases                 : str
  notes                     : str
"""

SCHEMES = {
    "LCG": {
        "cryptographically_secure": False,
        "deterministic":            True,
        "os_backed":                False,
        "easy_for_non_experts":     True,
        "high_throughput":          True,
        "good_for_embedded":        True,
        "good_for_simulation":      True,
        "forward_secrecy":          False,
        "side_channel_resistant":   False,
        "approx_speed_mbs":         8000,
        "security_bits":            0,
        "standardized":             False,
        "use_cases":                "Simple simulations, teaching, old game engines",
        "notes":                    "Linear Congruential Generator; trivially predictable — never use for security",
    },
    "C rand": {
        "cryptographically_secure": False,
        "deterministic":            True,
        "os_backed":                False,
        "easy_for_non_experts":     True,
        "high_throughput":          True,
        "good_for_embedded":        True,
        "good_for_simulation":      True,
        "forward_secrecy":          False,
        "side_channel_resistant":   False,
        "approx_speed_mbs":         5000,
        "security_bits":            0,
        "standardized":             True,
        "use_cases":                "Simple C programs, legacy code, teaching",
        "notes":                    "Implementation-defined; often an LCG. Output is predictable.",
    },
    "AES-CTR DRBG": {
        "cryptographically_secure": True,
        "deterministic":            True,
        "os_backed":                False,
        "easy_for_non_experts":     False,
        "high_throughput":          True,
        "good_for_embedded":        True,
        "good_for_simulation":      False,
        "forward_secrecy":          False,
        "side_channel_resistant":   True,
        "approx_speed_mbs":         3000,
        "security_bits":            128,
        "standardized":             True,
        "use_cases":                "FIPS/NIST-compliant systems, HSMs, government applications",
        "notes":                    "NIST SP 800-90A; requires AES-NI for side-channel safety",
    },
    "HMAC-DRBG": {
        "cryptographically_secure": True,
        "deterministic":            True,
        "os_backed":                False,
        "easy_for_non_experts":     False,
        "high_throughput":          False,  # moderate
        "good_for_embedded":        True,
        "good_for_simulation":      False,
        "forward_secrecy":          True,
        "side_channel_resistant":   False,
        "approx_speed_mbs":         350,
        "security_bits":            256,
        "standardized":             True,
        "use_cases":                "Key generation, certificate signing, FIPS-compliant apps",
        "notes":                    "NIST SP 800-90A; slower but provides forward secrecy via V/K state",
    },
    "Hash-DRBG": {
        "cryptographically_secure": True,
        "deterministic":            True,
        "os_backed":                False,
        "easy_for_non_experts":     False,
        "high_throughput":          False,  # moderate
        "good_for_embedded":        True,
        "good_for_simulation":      False,
        "forward_secrecy":          False,
        "side_channel_resistant":   False,
        "approx_speed_mbs":         500,
        "security_bits":            256,
        "standardized":             True,
        "use_cases":                "NIST-compliant key generation, token generation",
        "notes":                    "NIST SP 800-90A; simpler than HMAC-DRBG but no forward secrecy",
    },
    "/dev/urandom": {
        "cryptographically_secure": True,
        "deterministic":            False,
        "os_backed":                True,
        "easy_for_non_experts":     True,
        "high_throughput":          True,
        "good_for_embedded":        False,
        "good_for_simulation":      False,
        "forward_secrecy":          True,
        "side_channel_resistant":   True,
        "approx_speed_mbs":         1500,
        "security_bits":            256,
        "standardized":             False,
        "use_cases":                "Key generation, seeding other PRGs, general-purpose secure randomness",
        "notes":                    "Linux kernel CSPRNG (ChaCha20-based since kernel 5.17); non-blocking",
    },
    "Python secrets": {
        "cryptographically_secure": True,
        "deterministic":            False,
        "os_backed":                True,
        "easy_for_non_experts":     True,
        "high_throughput":          False,  # moderate
        "good_for_embedded":        False,
        "good_for_simulation":      False,
        "forward_secrecy":          True,
        "side_channel_resistant":   True,
        "approx_speed_mbs":         400,
        "security_bits":            256,
        "standardized":             False,
        "use_cases":                "Passwords, tokens, API keys, OTPs in Python applications",
        "notes":                    "Python 3.6+ stdlib; wraps os.urandom(); easiest secure option for Python devs",
    },
    # ── NEW ROW ──────────────────────────────────────────────────────────────
    "ChaCha20": {
        "cryptographically_secure": True,
        "deterministic":            True,
        "os_backed":                False,
        "easy_for_non_experts":     False,
        "high_throughput":          True,
        "good_for_embedded":        False,
        "good_for_simulation":      False,
        "forward_secrecy":          False,
        "side_channel_resistant":   True,
        "approx_speed_mbs":         4500,
        "security_bits":            256,
        "standardized":             True,
        "use_cases":                "TLS 1.3, WireGuard, disk encryption, high-speed CSPRNG",
        "notes":                    "RFC 8439; ARX design is naturally constant-time. Used in Linux /dev/urandom since kernel 5.17",
    },
}
