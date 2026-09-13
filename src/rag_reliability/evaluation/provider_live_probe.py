"""One-call-at-a-time live semantic-provider qualification."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Literal

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.contracts.enums import (
    AuthorityLevel,
    RefusalReason,
    SourceState,
)
from rag_reliability.contracts.runtime import (
    ContextBundle,
    ContextItem,
    ProviderRefusalDecision,
    ProviderRequest,
    ProviderResponse,
)
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.semantic_provider_profile import (
    build_phase5_semantic_provider_binding,
    build_phase5_semantic_provider_config,
)
from rag_reliability.runtime.http_transport import StdlibJsonTransport
from rag_reliability.runtime.semantic_provider import (
    OpenAICompatibleSemanticProvider,
)

ProbeId = Literal[
    "context-a",
    "context-b",
    "refusal",
]


class LiveProbeReceipt(ContractModel):
    receipt_version: Literal[
        "phase5-live-provider-probe-v1"
    ] = "phase5-live-provider-probe-v1"

    probe_id: ProbeId

    model_id: Literal[
        "glm-5.2"
    ] = "glm-5.2"

    binding_configuration_id: Sha256
    provider_configuration_id: Sha256

    expected_decision: Literal[
        "answer",
        "refusal",
    ]

    observed_decision: Literal[
        "answer",
        "refusal",
    ]

    marker_match: bool
    citation_match: bool
    refusal_reason_match: bool

    passed: Literal[True] = True

    credential_value_persisted: Literal[
        False
    ] = False

    raw_provider_payload_persisted: Literal[
        False
    ] = False

    baseline_execution_authorized: Literal[
        False
    ] = False

    held_out_outcomes_exposed: Literal[
        False
    ] = False


def _context(
    *,
    query: str,
    evidence_id: str,
    content: str,
) -> ContextBundle:
    item = ContextItem(
        evidence_id=evidence_id,
        source_ids=("phase5-live-probe-source",),
        document_ids=("phase5-live-probe-document",),
        content=content,
        position=1,
        authority_level=AuthorityLevel.AUTHORITATIVE,
        source_state=SourceState.CURRENT,
        eligible_as_final_citation=True,
    )

    return ContextBundle(
        query=query,
        items=(item,),
        assembled_context=(
            f"EVIDENCE: {evidence_id}\n"
            f"{content}"
        ),
    )


async def _answer_probe(
    provider: OpenAICompatibleSemanticProvider,
    *,
    probe_id: Literal[
        "context-a",
        "context-b",
    ],
    marker: str,
    evidence_id: str,
) -> LiveProbeReceipt:
    query = (
        "According only to the supplied context, "
        "what is the project marker?"
    )

    context = _context(
        query=query,
        evidence_id=evidence_id,
        content=(
            f"The project marker is {marker}."
        ),
    )

    result = await provider.generate(
        ProviderRequest(
            query=query,
            context=context,
        )
    )

    observed: Literal[
        "answer",
        "refusal",
    ] = (
        "answer"
        if isinstance(
            result,
            ProviderResponse,
        )
        else "refusal"
    )

    marker_match = (
        isinstance(
            result,
            ProviderResponse,
        )
        and marker in result.answer_text
    )

    citation_match = (
        isinstance(
            result,
            ProviderResponse,
        )
        and result.cited_evidence_ids
        == (evidence_id,)
    )

    if not (
        observed == "answer"
        and marker_match
        and citation_match
    ):
        raise RuntimeError(
            f"live probe failed: {probe_id}"
        )

    return LiveProbeReceipt(
        probe_id=probe_id,
        binding_configuration_id=(
            provider.binding_id
        ),
        provider_configuration_id=(
            provider.configuration_id
        ),
        expected_decision="answer",
        observed_decision=observed,
        marker_match=marker_match,
        citation_match=citation_match,
        refusal_reason_match=False,
    )


async def _refusal_probe(
    provider: OpenAICompatibleSemanticProvider,
) -> LiveProbeReceipt:
    query = "What is the exact deployment date?"

    context = _context(
        query=query,
        evidence_id="phase5-live-refusal",
        content=(
            "The supplied context contains "
            "no deployment date."
        ),
    )

    result = await provider.generate(
        ProviderRequest(
            query=query,
            context=context,
        )
    )

    observed: Literal[
        "answer",
        "refusal",
    ] = (
        "refusal"
        if isinstance(
            result,
            ProviderRefusalDecision,
        )
        else "answer"
    )

    refusal_match = (
        isinstance(
            result,
            ProviderRefusalDecision,
        )
        and result.reason
        is RefusalReason.INSUFFICIENT_EVIDENCE
    )

    if not (
        observed == "refusal"
        and refusal_match
    ):
        raise RuntimeError(
            "live refusal probe failed"
        )

    return LiveProbeReceipt(
        probe_id="refusal",
        binding_configuration_id=(
            provider.binding_id
        ),
        provider_configuration_id=(
            provider.configuration_id
        ),
        expected_decision="refusal",
        observed_decision=observed,
        marker_match=False,
        citation_match=False,
        refusal_reason_match=refusal_match,
    )


async def _run(
    probe_id: ProbeId,
) -> LiveProbeReceipt:
    provider = OpenAICompatibleSemanticProvider(
        config=build_phase5_semantic_provider_config(),
        binding=build_phase5_semantic_provider_binding(),
        transport=StdlibJsonTransport(),
    )

    if probe_id == "context-a":
        return await _answer_probe(
            provider,
            probe_id="context-a",
            marker="ORCHID-731",
            evidence_id=(
                "phase5-live-evidence-a"
            ),
        )

    if probe_id == "context-b":
        return await _answer_probe(
            provider,
            probe_id="context-b",
            marker="COBALT-284",
            evidence_id=(
                "phase5-live-evidence-b"
            ),
        )

    return await _refusal_probe(
        provider
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--probe",
        required=True,
        choices=(
            "context-a",
            "context-b",
            "refusal",
        ),
    )

    args = parser.parse_args()

    probe_id: ProbeId = args.probe

    receipt = asyncio.run(
        _run(
            probe_id
        )
    )

    repo_root = (
        Path(__file__)
        .resolve()
        .parents[3]
    )

    path = (
        repo_root
        / "artifacts"
        / "development"
        / (
            "phase5_live_provider_"
            f"{probe_id.replace('-', '_')}_v1.json"
        )
    )

    digest = write_json_with_sha256(
        path,
        receipt,
    )

    print(
        f"PHASE5_LIVE_PROBE={probe_id}"
    )
    print(
        "PHASE5_LIVE_PROBE_PASS=true"
    )
    print(
        f"PHASE5_LIVE_PROBE_SHA256={digest}"
    )
    print(
        "PHASE5_BASELINE_EXECUTION_AUTHORIZED=false"
    )
    print(
        "PHASE5_HELD_OUT_OUTCOMES_EXPOSED=false"
    )


if __name__ == "__main__":
    main()
