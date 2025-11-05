# Radix Project — Intel 80x86 Assembly

**Tags:** radix, assembly, 80x86, base-conversion, low-level
**Last Updated:** 2025-10-10

Short summary
- A compact Intel 80x86 assembly program that reads integer values and source/target radices from the console, performs base conversions and basic arithmetic operations, and prints results in radices from 2 (binary) up to 62. All runtime helpers (console I/O, parsing, conversion) are implemented by hand — no Irvine32 or other convenience libraries are used.

Why this project matters
- Demonstrates low‑level programming skills: manual string I/O, integer parsing, arbitrary‑base conversion, digit mapping (0–9, A–Z, a–z), and careful register/stack discipline on 32‑bit x86.
- Useful for learning computer arithmetic, number systems, and constrained programming (no runtime libraries).

Assumptions & environment
- Target ISA: Intel 80386 / 32‑bit x86 (flat memory model). The code is portable to assemblers that support standard x86 syntax (MASM, NASM, or similar) with minimal adapter glue.
- Input/Output: console text I/O implemented with OS calls (or BIOS/CRT routines depending on toolchain). This project deliberately avoids Irvine32 helper functions; all routines are handwritten.
- Numbers: integer arithmetic and conversions (signed integers). Fractional numbers are out of scope unless explicitly added.

Core features
- Read source radix (2..62) and target radix (2..62) from user input.
- Read integer values (decimal or in source radix) and perform:
	- Base conversion (source → target)
	- Basic operations (add, subtract, multiply, divide) on integers — optional depending on assignment scope.
- Print converted results using digit mapping: 0–9, A–Z (10–35), a–z (36–61) to reach radix 62.
- Looping prompt: after output, prompt user whether to repeat or exit.

High‑level algorithm (base conversion)
1. Parse input string to integer value using the source radix:
	 - Initialize accumulator = 0
	 - For each character c in input string:
		 * digit = char_to_value(c)  // map '0'..'9','A'..'Z','a'..'z' to 0..61
		 * accumulator = accumulator * source_radix + digit
2. Convert accumulator to target radix string:
	 - If accumulator == 0 then output "0"
	 - While accumulator != 0:
		 * digit = accumulator % target_radix
		 * push digit onto digit stack
		 * accumulator = accumulator / target_radix
	 - Pop digits from stack and map to characters with value_to_char(digit)
3. Print result string to console.

Notes on integer handling and overflow
- Implementations must consider signed input and overflow behavior. Typical class/homework implementations assume inputs that fit within a 32‑bit signed integer. If larger ranges are needed, implement big‑integer support (bignum) or limit input with explicit checks.

I/O and helper routines (recommended)
- read_line(buffer, maxlen): read characters until newline; handle backspace and simple editing.
- parse_int(buffer, radix): parse signed integer from buffer using given radix; return error on invalid digit.
- write_string(ptr): write null‑terminated string to console.
- write_int_in_radix(value, radix): convert integer and output using algorithm above.

Testing & example cases
- Basic coverage:
	- Input: src=10, tgt=2, value=13 → Output: 1101
	- Input: src=16, tgt=10, value=FF → Output: 255
	- Input: src=2, tgt=36, value=101011 → Output: "..." (validate mapping)
	- Input: src=10, tgt=62, value=61 → Output: 'z'
- Edge cases:
	- Input value 0 → Output 0.
	- Negative values: ensure '-' is printed and absolute value converted.
	- Invalid digit for source radix → error message and re‑prompt.
	- Radix bounds: reject radices <2 or >62.
	- Overflow detection: report or limit input if accumulator exceeds 32‑bit signed range.

Suggested test harness
- Provide a small test script (shell or Python) that runs the assembled binary with redirected input and compares stdout to expected outputs for the above cases.

Recommended artifacts to include
- Source assembly file(s) (e.g., Radix.asm or main.asm).
- Build instructions (assembler, linker commands; e.g., MASM, NASM + LD, or TASM).
- Sample input/output transcripts (plain text) for test cases.
- A small README describing design decisions (char mapping, overflow policy, assembler chosen).

Potential improvements / extensions
- Add fractional base conversion (fixed‑point or rational conversions).
- Implement arbitrary‑precision integers to support very large numbers.
- Add locale‑aware digit grouping or formatted output.
- Provide a small C harness to exercise the assembly routines and run unit tests.

RAG-friendly metadata (JSON)
```json
{
	"id": "project-radix-80x86",
	"title": "Radix Project — Intel 80x86 Assembly",
	"tags": ["assembly","radix","80x86","base-conversion"],
	"short_summary": "Assembly program that converts integers between radices 2..62, with manual I/O and conversion routines (no Irvine32).",
	"last_updated": "2025-10-10",
	"suggested_artifacts": ["Radix.asm","README.md","testcases.txt"]
}
```