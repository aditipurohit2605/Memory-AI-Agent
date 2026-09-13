import ast
from html.parser import HTMLParser
import operator
from urllib.parse import parse_qs, unquote, urlparse

import requests


_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _evaluate_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        if isinstance(node.value, bool):
            raise ValueError("Boolean values are not supported.")
        return node.value

    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_evaluate_node(node.operand))

    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate_node(node.left)
        right = _evaluate_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("Exponent is too large.")
        return _BINARY_OPERATORS[type(node.op)](left, right)

    raise ValueError("Unsupported expression.")


def calculator(expression):
    """Safely calculate a small arithmetic expression without executing code."""
    if not isinstance(expression, str) or not expression.strip() or len(expression) > 200:
        return "Invalid mathematical expression."
    if any(character not in "0123456789+-*/(). %" for character in expression):
        return "Invalid mathematical expression."

    try:
        tree = ast.parse(expression, mode="eval")
        result = _evaluate_node(tree.body)
        if abs(result) > 10**100:
            return "Could not calculate the expression."
        return str(result)
    except (SyntaxError, TypeError, ValueError, ZeroDivisionError, OverflowError):
        return "Could not calculate the expression."


# --------------------------------
# WEB SEARCH
# --------------------------------

class _SearchResultParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self._current = None
        self._capture = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        if tag == "a" and "result__a" in classes:
            self._current = {"title": "", "href": attributes.get("href", ""), "body": ""}
            self._capture = "title"
        elif self._current and "result__snippet" in classes:
            self._capture = "body"

    def handle_data(self, data):
        if self._current and self._capture:
            self._current[self._capture] += data.strip() + " "

    def handle_endtag(self, tag):
        if tag == "a" and self._current and self._capture == "title":
            self._capture = None
        elif self._current and self._capture == "body" and tag in {"a", "div"}:
            self._current["title"] = self._current["title"].strip()
            self._current["body"] = self._current["body"].strip()
            self.results.append(self._current)
            self._current = None
            self._capture = None


def _fallback_web_search(query):
    response = requests.get(
        "https://html.duckduckgo.com/html/",
        params={"q": query},
        headers={"User-Agent": "MemoryAI/1.0"},
        timeout=10,
    )
    response.raise_for_status()
    parser = _SearchResultParser()
    parser.feed(response.text)
    return parser.results[:5]


def _format_search_results(results):
    if not results:
        return "No search results found."

    output = ""
    for result in results:
        url = result.get("href", result.get("url", ""))
        parsed_url = urlparse(url)
        if parsed_url.query:
            target = parse_qs(parsed_url.query).get("uddg", [None])[0]
            if target:
                url = unquote(target)
        output += (
            f"\nTitle: {result.get('title', '')}\n"
            f"URL: {url}\n"
            f"Summary: {result.get('body', '')}\n"
        )
    return output

def web_search(query):
    """
    Search the web using DuckDuckGo.
    """

    try:

        from ddgs import DDGS

        try:
            results = DDGS().text(query, max_results=5)
        except Exception:
            results = _fallback_web_search(query)
        return _format_search_results(results)

    except Exception as e:
        return "Web search failed: " + str(e)


# --------------------------------
# CALCULATOR TOOL DEFINITION
# --------------------------------

calculator_tool = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Calculate a mathematical expression.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to calculate."
                }
            },
            "required": ["expression"]
        }
    }
}


# --------------------------------
# WEB SEARCH TOOL DEFINITION
# --------------------------------

web_search_tool = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the internet for current or factual information.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query."
                }
            },
            "required": ["query"]
        }
    }
}


# --------------------------------
# TOOL EXECUTOR
# --------------------------------

def execute_tool(tool_name, arguments):

    if tool_name == "calculator":

        expression = arguments.get(
            "expression",
            ""
        )

        return calculator(expression)

    if tool_name == "web_search":

        query = arguments.get(
            "query",
            ""
        )

        return web_search(query)

    return "Unknown tool."