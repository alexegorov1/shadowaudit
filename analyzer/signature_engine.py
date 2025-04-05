import os
import yaml
import re
from typing import List, Dict, Any, Callable, Optional, Union
from analyzer.base_analyzer import BaseAnalyzer

class SignatureAnalyzer(BaseAnalyzer):
    def __init__(self, rules_path: str = "analyzer/rules/signatures.yaml"):
        super().__init__()
        self.name = "signature_analyzer"
        self.rules_path = rules_path
        self.rules = self._load_rules()
        self.active_rules = self._compile_rules()
        self.set_severity_map({r["id"]: r.get("severity", 1) for r in self.rules if "id" in r})

    def get_name(self) -> str:
        return self.name

    def supported_types(self) -> List[str]:
        types = set()
        for rule in self.rules:
            val = rule.get("artifact_type")
            if isinstance(val, str):
                types.add(val)
            elif isinstance(val, list):
                types.update(val)
        return list(types) or ["*"]

    def analyze(self, artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for artifact in artifacts:
            matched = []
            for rule in self.active_rules:
                try:
                    if rule["match"](artifact):
                        matched.append(rule["id"])
                except Exception as e:
                    self.logger.warning(f"{self.name} rule failed [{rule['id']}]: {e}")
            if matched:
                severity = max(self.get_severity_for_rule(r) for r in matched)
                result = self.enrich_result(artifact, matched, severity)
                results.append(result)
            else:
                results.append(artifact)
        return results

    def _load_rules(self) -> List[Dict[str, Any]]:
        if not os.path.isfile(self.rules_path):
            self.logger.warning(f"{self.name} rules not found: {self.rules_path}")
            return []
        with open(self.rules_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or []

    def _compile_rules(self) -> List[Dict[str, Any]]:
        compiled = []
        for rule in self.rules:
            rule_id = rule.get("id")
            if not rule_id:
                continue
            conditions = self._build_conditions(rule)
            if not conditions:
                continue
            def matcher(artifact: Dict[str, Any], conds=conditions) -> bool:
                return all(c(artifact) for c in conds)
            compiled.append({"id": rule_id, "match": matcher})
        return compiled

    def _build_conditions(self, rule: Dict[str, Any]) -> List[Callable[[Dict[str, Any]], bool]]:
        conditions = []
        field = rule.get("field")
        if not field:
            return conditions

        if "equals" in rule:
            expected = rule["equals"]
            conditions.append(lambda a: a.get(field) == expected)

        if "not_equals" in rule:
            expected = rule["not_equals"]
            conditions.append(lambda a: a.get(field) != expected)

        if "contains" in rule:
            substr = rule["contains"]
            conditions.append(lambda a: substr in str(a.get(field, "")))

        if "startswith" in rule:
            prefix = rule["startswith"]
            conditions.append(lambda a: str(a.get(field, "")).startswith(prefix))

        if "endswith" in rule:
            suffix = rule["endswith"]
            conditions.append(lambda a: str(a.get(field, "")).endswith(suffix))

        if "in" in rule:
            valid = rule["in"]
            conditions.append(lambda a: a.get(field) in valid)

        if "exists" in rule:
            flag = rule["exists"]
            if flag:
                conditions.append(lambda a: field in a)
            else:
                conditions.append(lambda a: field not in a)

        if "gt" in rule:
            threshold = rule["gt"]
            conditions.append(lambda a: isinstance(a.get(field), (int, float)) and a.get(field) > threshold)

        if "lt" in rule:
            threshold = rule["lt"]
            conditions.append(lambda a: isinstance(a.get(field), (int, float)) and a.get(field) < threshold)

        if "regex" in rule:
            pattern = re.compile(rule["regex"])
            conditions.append(lambda a: isinstance(a.get(field), str) and pattern.search(a.get(field)) is not None)

        if "custom_lambda" in rule:
            try:
                func = eval(rule["custom_lambda"])
                if callable(func):
                    conditions.append(lambda a: func(a.get(field)))
            except Exception:
                pass

        return conditions
