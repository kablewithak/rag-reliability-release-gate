from rag_reliability.config.identity import RuntimeConfiguration


def base_payload() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "retrieval": {
            "retriever_id": "retriever-contract-v1",
            "top_k": 8,
        },
        "source_policy": {
            "policy_id": "authority-current-v1",
        },
        "reranker": None,
        "context": {
            "builder_id": "bounded-context-v1",
            "budget_unit_id": "characters",
            "max_budget": 12000,
            "max_evidence_items": 6,
        },
        "provider": {
            "adapter_id": "fake-replay-v1",
            "model_id": "replay-model-v1",
            "timeout_ms": 3000,
            "max_retries": 1,
        },
        "citation": {
            "validator_id": "citation-validator-v1",
            "require_citations": True,
        },
        "fallback": {
            "policy_id": "safe-refusal-v1",
            "allow_qualified_answer": True,
        },
    }


def test_semantically_identical_key_order_has_same_identity() -> None:
    first = base_payload()
    second = {
        "fallback": first["fallback"],
        "citation": first["citation"],
        "provider": first["provider"],
        "context": first["context"],
        "reranker": first["reranker"],
        "source_policy": first["source_policy"],
        "retrieval": first["retrieval"],
        "schema_version": first["schema_version"],
    }

    first_config = RuntimeConfiguration.model_validate(first)
    second_config = RuntimeConfiguration.model_validate(second)

    assert first_config.configuration_id == second_config.configuration_id
    assert first_config.canonical_json() == second_config.canonical_json()


def test_material_configuration_change_changes_identity() -> None:
    first_config = RuntimeConfiguration.model_validate(base_payload())

    changed_payload = base_payload()
    changed_payload["retrieval"] = {
        "retriever_id": "retriever-contract-v1",
        "top_k": 9,
    }
    second_config = RuntimeConfiguration.model_validate(changed_payload)

    assert first_config.configuration_id != second_config.configuration_id
    assert first_config.retrieval.configuration_id != second_config.retrieval.configuration_id
    assert first_config.provider.configuration_id == second_config.provider.configuration_id


def test_configuration_identity_is_lowercase_sha256() -> None:
    config = RuntimeConfiguration.model_validate(base_payload())

    assert len(config.configuration_id) == 64
    assert config.configuration_id == config.configuration_id.lower()
    assert all(character in "0123456789abcdef" for character in config.configuration_id)
