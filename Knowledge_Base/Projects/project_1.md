HUFF — Huffman Coding Compression Tool
Project Overview
HUFF is a C++ command‑line Huffman encoder/decoder. It builds a Huffman tree from byte frequencies, encodes payloads into compact bitstreams, appends a fixed‑size tree metadata footer, and can decode files by reconstructing the tree from that metadata.
- Type: Personal project (academic‑style, but self‑driven)
- Role: Sole developer (design, implementation, testing, documentation)
- Purpose & Audience:
- Intended for students, engineers, and hobbyists learning about compression.
- Demonstrates Huffman coding in a working CLI tool.

Repository Layout
- Huffman.h / Huffman.cpp → Core algorithm (tree, encoding, decoding)
- Main.cpp → CLI entry point, argument parsing
- HUFF.sln / HUFF.vcxproj → Visual Studio project files
- /Debug, /Release → Build output folders

Build & Run Metadata
- Build Instructions:
- Open HUFF.sln in Visual Studio
- Build target: Debug or Release (x64)
- Compiler: MSVC (vc142)
- No special flags required
- Platform:
- Tested on Windows 10/11 with MSVC
- Default shell: Windows CMD or PowerShell
- CLI Usage Examples:
- Encode (build‑and‑encode):
HUFF -me -i:input.bin -o:out.huf
- Decode:
HUFF -md -i:out.huf -o:decoded.bin
- Export tree:
HUFF -mt -i:input.bin -o:tree.htree
- Encode with external tree:
HUFF -met -i:input.bin -t:tree.htree -o:out.huf

- Parameters:
- -i:<path> → input file
- -o:<path> → output file
- -t:<path> → tree metadata file
- Help flags: -h, -?, -help

Data Structures & Constants
struct node {
    unsigned char symbol;
    int weight;
    node *leftChild, *rightChild;
};

// Class fields
node* nodeArray[256];
int freqArray[256];
string pathArray[256];
unsigned char charArray[510];
node* root;
int fileSize, bytesOut;
string currentPath, longestPath;

// Constants
ALPHABET_SIZE = 256
FOOTER_SIZE_BYTES = 510
MAX_PAIRS = 255
BIT_ORDER = MSB-first (bits 7..0)
PADDING_POLICY = "copy prefix bits from longest code to fill last byte"

Binary Format
- Encoded File Layout:
[payload bytes: encoded bitstream] + [footer 510 bytes]
- Footer Layout:
- 255 pairs × 2 bytes each = 510 bytes
- Each pair: (childIndexA : 1 byte, childIndexB : 1 byte)
- childIndex ∈ [0..255], indexes into nodeArray
- Pairs stored in order created during tree construction
- Unused pairs = 0x00
- Bit Packing:
- Codes: left = 0, right = 1
- Bits appended MSB‑first (first bit → bit7)
- Final byte padded using prefix bits from longestPath

Algorithmic Summary
- Count frequencies of all 256 symbols.
- Build initial leaf nodes for nonzero frequencies.
- Iteratively combine two minimal‑weight nodes into a parent.
- Store child index pair in footer array.
- Traverse final tree to assign bit codes.
- Encode input bytes → bit codes → packed bytes.
- Pad final byte with prefix bits from longestPath.
- Append footer (510 bytes).
- Decode: read footer, rebuild tree, traverse bits to output symbols.

Edge Cases, Failure Modes & Constraints
- Requires footer of exactly 510 bytes to decode.
- Missing/corrupted footer → decode may crash or produce incorrect output.
- Empty input: fileSize=0; may produce footer of zeros; decoder behavior unspecified.
- Single‑symbol input: degenerate tree; padding behavior critical.
- Memory: nodes allocated with new but not deleted → memory leak risk if reused.
- Naive O(256²) minima scan (fine for 256 symbols).
- Uses while(!eof()) in some reads → brittle.

Known Bugs & Design Choices
- Fixed‑size 510‑byte footer wastes space but simplifies format.
- Padding protocol (copying prefix from longest code) is nonstandard — must be documented for interoperability.
- No explicit deallocation of nodes.
- Tie‑breaking in minima selection depends on scan order (deterministic but important for reproducibility).
- Error policy: file open failure → exit(EXIT_FAILURE) (no return codes or exceptions).

Outcome & Impact
- Result: Successfully compresses files with skewed byte distributions, reducing file size compared to raw storage.
- Efficiency / Usability: Improves storage efficiency for text and binary files with non‑uniform symbol distributions.
- Deployment: Implemented as a standalone executable (Visual Studio solution). Could be shared via GitHub for demonstration or portfolio purposes.

Challenges & Learning
- Challenges:
- Designing a fixed‑size metadata footer.
- Managing bit‑level operations (MSB‑first packing).
- Handling memory management for dynamically allocated nodes.
- Solutions:
- Chose fixed 510‑byte footer for simplicity.
- Implemented careful bit‑manipulation routines.
- Accepted potential memory leaks as trade‑off for short‑lived CLI tool.
- Learnings:
- Hands‑on experience with tree data structures and priority‑based merging.
- Importance of metadata design in compression.
- Trade‑offs between efficiency, portability, and simplicity.
- Strengthened C++ skills in low‑level memory handling and CLI design.
