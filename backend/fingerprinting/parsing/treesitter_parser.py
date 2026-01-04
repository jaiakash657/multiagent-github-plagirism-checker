from tree_sitter import Parser, Language
import tree_sitter_python as tspython
import tree_sitter_java as tsjava
import tree_sitter_javascript as tsjs
# pip install tree-sitter-typescript
import tree_sitter_typescript as tsts 

# Map keys to the actual grammar functions
# Note: typescript and tsx are different grammars within the same package
LANGUAGE_FUNCTIONS = {
    "python": tspython.language,
    "java": tsjava.language,
    "javascript": tsjs.language,
    "typescript": tsts.language_typescript,
    "tsx": tsts.language_tsx,
}

_PARSER_CACHE = {}

class TreeSitterParser:
    @staticmethod
    def _get_parser(lang: str):
        if lang in _PARSER_CACHE:
            return _PARSER_CACHE[lang]

        if lang not in LANGUAGE_FUNCTIONS:
            return None

        # Wrap the capsule in a Language object
        # This fixes the "Incompatible Language version" and "PyCapsule" errors
        lang_func = LANGUAGE_FUNCTIONS[lang]
        language_object = Language(lang_func())
        
        parser = Parser(language_object)
        _PARSER_CACHE[lang] = parser
        return parser

    @staticmethod
    def parse_code(code: str, lang: str):
        parser = TreeSitterParser._get_parser(lang)
        if not parser or not code:
            return None
        return parser.parse(code.encode("utf8"))