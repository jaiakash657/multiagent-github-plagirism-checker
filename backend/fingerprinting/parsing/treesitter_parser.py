from tree_sitter_languages import get_language, get_parser

class TreeSitterParser:
    """
    Thin wrapper around tree-sitter.
    Responsible ONLY for:
    - loading parser
    - parsing source code
    """

    _parser_cache = {}

    @staticmethod
    def parse_code(code: str, language: str):
        """
        Parse source code and return tree-sitter AST.

        :param code: source code as string
        :param language: 'python', 'java', 'javascript', 'cpp', etc.
        :return: tree_sitter.Tree
        """

        if not code or not code.strip():
            return None

        parser = TreeSitterParser._get_parser(language)
        if not parser:
            raise ValueError(f"Unsupported language: {language}")

        return parser.parse(bytes(code, "utf8"))

    @staticmethod
    def _get_parser(language: str):
        """
        Lazy-load and cache parsers per language.
        """

        if language in TreeSitterParser._parser_cache:
            return TreeSitterParser._parser_cache[language]

        try:
            # load grammar + parser lazily
            get_language(language)   # ensures grammar exists
            parser = get_parser(language)
        except Exception as e:
            raise RuntimeError(f"Failed to load Tree-sitter parser for {language}") from e

        TreeSitterParser._parser_cache[language] = parser
        return parser
