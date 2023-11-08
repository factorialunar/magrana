import json
import unidecode

class AnagramGroup:
    def __init__(self, prefix: str, is_prefix=True) -> None:
        self._prefixes: list[(str, bool)] = []
        if prefix:
            self._prefixes.append((prefix, is_prefix))
        self._anagrams: dict[str, list[str]] = {}
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return len(self._prefixes) > 0

    def prefixes(self) -> list[(str, bool)]:
        return self._prefixes

    def data(self) -> dict[str, list[str]]:
        return self._anagrams

    def update_size(self) -> None:
        self._size = len(json.dumps(self._anagrams))

    def add_anagram(self, key: str, words: list[str]) -> None:
        self.add_anagram_fast(key, words)
        self.update_size()

    def add_anagram_fast(self, key: str, words: list[str]) -> None:
        self._anagrams[key] = words

    def merge(self, other) -> None:
        self._prefixes += other.prefixes()
        self._anagrams.update(other.data())
        self.update_size()

words_hashed: dict[str, list[str]] = {}
prefixes = set()
char_map: dict[str, str] = {}

def sanitize_char(c):
    c_sanitized = c.lower().replace("\u00b7", "").replace("-", "")
    if c_sanitized == "":
        return ""
    return unidecode.unidecode(c_sanitized)

with open('dump.json') as f:
    words: dict[str, str] = json.load(f)
    
    for hash, word in words:
        try:
            words_hashed[hash].append(word)
            for c in word.lower():
                char_map[c] = sanitize_char(c)
        except KeyError:
            words_hashed[hash] = [word]
        
        prefixes.add(hash[0])

files: list[tuple[str, dict[str, list[str]]]] = {}

MAX_SIZE = 512 * 1024

def get_entries_by_prefix(entries: dict[str, list[str]], prefix: str) -> AnagramGroup:
    prefix_len = len(prefix)

    anagram_group = AnagramGroup(prefix)
    for word_hash, words in entries.items():
        if word_hash[:prefix_len] == prefix:
            anagram_group.add_anagram_fast(word_hash, words)
    anagram_group.update_size()

    return anagram_group

def generate_tree(prefix: str, level: int, root_entries: dict[str, list[str]]) -> list[AnagramGroup]:
    indent = " " * level

    prefix_len = len(prefix)
    if prefix_len < level:
        anagram = root_entries[prefix]
        print(f"{indent}{level}. Exact match: {prefix} = {anagram}")
        entries = AnagramGroup(prefix, is_prefix=False)
        entries.add_anagram(prefix, anagram)
        return [entries]

    entries = get_entries_by_prefix(root_entries, prefix)

    size = len(entries)

    if size < MAX_SIZE:
        return [entries]

    new_prefix_len = prefix_len + 1
    subprefixes = sorted(set([word_hash[:new_prefix_len] for word_hash in entries.data().keys() if word_hash[:prefix_len] == prefix]))
    print(f'{indent}{level}. Subdividing prefix {prefix} of {int(size / 1024)} KB into {subprefixes}')
    subtree: list[AnagramGroup] = []
    for subprefix in subprefixes:
        subtree += generate_tree(subprefix, new_prefix_len, entries.data())
    return subtree

# Break the big prefixes into smaller subsets
prefix_entries: list[AnagramGroup] = []
for prefix in sorted(prefixes):
    prefix_entries += generate_tree(prefix, 1, words_hashed)

def consolidate(entries: list[AnagramGroup]) -> list[AnagramGroup]:
    consolidated: list[AnagramGroup] = []
    current_entry = AnagramGroup(None)
    for next_entry in entries:
        if len(current_entry) + len(next_entry) < MAX_SIZE:
            # Consolidate
            current_entry.merge(next_entry)
        else:
            if current_entry:
                print(f"Consolidated {[prefix[0] for prefix in current_entry.prefixes()]} = {int(len(current_entry) / 1024)} KB")
                consolidated.append(current_entry)
            current_entry = next_entry

    if current_entry:
        print(f"Consolidated {[prefix[0] for prefix in current_entry.prefixes()]} = {int(len(current_entry) / 1024)} KB")
        consolidated.append(current_entry)

    return consolidated

index: dict[str, str] = {}
for entry in consolidate(prefix_entries):
    keys = entry.prefixes()
    file_name = (keys[0][0] if len(keys) == 1 else f"{keys[0][0]}-{keys[-1][0]}") + ".json"
    print(f"{file_name}: {int(len(entry) / 1024)} KB")

    with open(f"data/{file_name}", "w") as f:
        json.dump(entry.data(), f)

    for key, is_prefix in keys:
        index_entry = {"file": file_name}
        if not is_prefix:
            index_entry["is_prefix"] = is_prefix
        index[key] = index_entry

with open("index.js", "w") as f:
    index_text = json.dumps(index, indent=2)
    f.write("const AnagramIndex = " + index_text + ";\n")

    f.write("const CharMap = " + json.dumps(char_map, indent=2) + ";\n")
