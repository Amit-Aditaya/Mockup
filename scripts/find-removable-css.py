import re
import sys

css_file = '/Users/hello/Projects/NextJS/Mockup/public/clone/assets/css/main.css'

with open(css_file, 'r') as f:
    lines = f.readlines()

total_lines = len(lines)

# Patterns for CSS we want to potentially remove
remove_patterns = [
    r'\.about-section-3',
    r'\.about-wrapper-4',
    r'\.news-box-items',
    r'\.news-details',
    r'\.news-sidebar',
    r'\.case-study',
    r'\.pricing-box',
    r'\.error-content',
    r'\.hero-[2-5]',
    r'\.hero-section-[2-5]',
    r'\.service-section-[2-9]',
    r'\.footer-section-[2-9]',
    r'\.footer-widgets-wrapper-22',
    r'header-[2-9]',
    r'\.homemenu',
    r'has-homemenu',
    r'\.marquee-',
    r'\.marquee-section',
    r'\.marquee-wrapper',
    r'\.portfolio-',
    r'\.project-box',
    r'\.project-section',
    r'\.project-details',
    r'\.project-wrapper',
]

# Find all lines that match any of these patterns
matches = set()
for i, line in enumerate(lines, 1):
    for pat in remove_patterns:
        if re.search(pat, line):
            matches.add(i)
            break

# Now, for each matched line that starts a CSS rule (top-level selector),
# we need to find the complete rule block including its closing brace,
# and any @media queries that contain only removable selectors.

# Build a list of all top-level selector start lines and what's on them
selector_lines = []
for i, line in enumerate(lines, 1):
    stripped = line.rstrip()
    # A top-level selector starts with a non-whitespace char that's not } and not a comment
    if stripped and not stripped.startswith('}') and not stripped.startswith('/*') and not stripped.startswith('*') and not stripped.startswith('//'):
        if not line[0].isspace() and '{' in stripped:
            selector_lines.append(i)

# For each selector line, find the matching closing brace
def find_block_end(start_line_idx):
    """Given 0-based line index of a line containing '{', find the matching '}'"""
    depth = 0
    for i in range(start_line_idx, total_lines):
        line = lines[i]
        depth += line.count('{') - line.count('}')
        if depth <= 0:
            return i + 1  # 1-based
    return total_lines

# Now find complete removable blocks
removable_ranges = []

# Also handle @media blocks that wrap removable selectors
i = 0
while i < total_lines:
    line = lines[i]
    line_num = i + 1
    stripped = line.rstrip()
    
    # Check if this is a @media query
    if stripped.startswith('@media'):
        block_end = find_block_end(i)
        # Check if ALL selectors inside this media query are removable
        all_removable = True
        has_selectors = False
        for j in range(i + 1, block_end - 1):
            inner_line = lines[j].strip()
            if inner_line and not inner_line.startswith('}') and '{' in inner_line:
                has_selectors = True
                if (j + 1) not in matches:
                    all_removable = False
                    break
        if all_removable and has_selectors:
            removable_ranges.append((line_num, block_end))
            i = block_end
            continue
    
    # Check if this line matches a removable pattern
    if line_num in matches:
        # Find the end of this CSS block
        block_end = find_block_end(i)
        removable_ranges.append((line_num, block_end))
        i = block_end
        continue
    
    i += 1

# Merge overlapping/adjacent ranges
removable_ranges.sort()
merged = []
for start, end in removable_ranges:
    if merged and start <= merged[-1][1] + 2:
        merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    else:
        merged.append((start, end))

# Print results
print(f"Total CSS file lines: {total_lines}")
print(f"Found {len(merged)} removable blocks:\n")

total_removable = 0
for start, end in merged:
    count = end - start + 1
    total_removable += count
    first_line = lines[start - 1].strip()[:100]
    last_selector = ""
    for j in range(end - 1, start - 2, -1):
        l = lines[j].strip()
        if l and not l.startswith('}') and '{' in l:
            last_selector = l[:100]
            break
    print(f"Block: Lines {start}-{end} ({count} lines)")
    print(f"  First: {first_line}")
    if last_selector and last_selector != first_line:
        print(f"  Last rule: {last_selector}")
    print()

print(f"\nTotal removable lines: {total_removable} out of {total_lines} ({100*total_removable/total_lines:.1f}%)")
